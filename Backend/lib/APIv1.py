import time
from random import randint
from hashlib import sha256
from flask import jsonify, g, abort

from .validator import *
from .helper import *

import db1 as db

class api():
    """API version 1"""
    def __init__(self,):
        self.schemes = {}
        self.schemes["connect"] = Scheme([Item("id", int)], [Item("token", str)])

        self.schemes["data"] = Scheme([Item("token", str)])
        d = Scheme([], [Item("temperature", float), Item("humidity", float), Item("brightness", int)])
        self.schemes["data"].add(Item("data", dict, d))

        self.schemes["error"] = Scheme([Item("id", int), Item("level", str)], [Item("token", str), Item("error", str)])
        self.schemes["alive"] = Scheme([Item("token", str)])

        self.schemes["view"] = Scheme([Item("room", int)])
        self.schemes["view"].add(Item("time", dict, Scheme(None, [
            Item("time", str),
            Item("time-from", str),
            Item("time-to", str)
        ])), False)
        self.schemes["view"].add(Item("data", list, str))
        self.allowed_view_req_data = ("temperature", "humidity", "brightness")

        self.schemes["auth"] = Scheme([Item("user", str), Item("password", str)])
        self.schemes["command"] = Scheme([Item("token", str), Item("command", str)])

        self.last_id = 0
        self.candidates = []

    def call(self, req:str, data:dict):
        """Perform an API call. Use this for all calls, it will direct them to the right methods."""
        if req in self.schemes and hasattr(self, "api_" + req):
            if is_valid(self.schemes[req], data):
                return getattr(self, "api_" + req)(data)
            else:
                return jsonify(API_fatal("Invalid request."))
        else:
            return jsonify(API_fatal("Unknown request."))

    def api_connect(self, data):
        """API call for nodes to connect to the system."""
        if "token" in data:
            s = db.select("devices", "*", "dev_id={} and token='{}'".format(data["id"], data["token"]))
            print(s)
            if len(s) == 1:
                db.insert_raw("logs", "'{}', {}, '{}';".format(db.format_time(), data["id"], "Successfully reconnected."))
                return jsonify(API_response())
            else:
                return jsonify(API_error("Invalid token."))
        else:
            if data["id"] == 0:
                if self.last_id == 0:
                    self.last_id = self.get_last()
                self.last_id += 1
                c = (self.last_id, self.create_token())
                self.candidates.append(c)
                return jsonify(API_response(id=c[0], token=c[1]))
            else:
                return jsonify(API_error("Unable to identify. Initiate a new connection."))

    def api_data(self, data):
        """API call for nodes to input data."""
        d = db.select("devices", "*", "token='{}'".format(data["token"]))
        if len(d) == 1:
            d = d[0]
        else:
            return jsonify(API_error("No such token."))

        dev_id = d[0]
        room_number = d[2]
        t = db.format_time()
        data_m = data["data"]
        d = ""
        if "temperature" in data_m:
            d += str(data_m["temperature"]) + ", "
        else:
            d += "null, "
        if "humidity" in data_m:
            d += str(data_m["humidity"]) + ", "
        else:
            d += "null, "
        if "brightness" in data_m:
            d += str(data_m["brightness"])
        else:
            d += "null"
        db.insert_raw("data", "{}, {}, '{}', {}".format(dev_id, room_number, t, d))
        return jsonify(API_response())

    def api_error(self, data):
        """API call for nodes to log errors."""
        dev_id = data["id"]
        level = data["level"]
        try:
            error = data["error"]
        except:
            error = "<No message.>"
        print("DEVICE has encountered an error. Printing data:")
        print(data)
        db.insert_raw("logs", "'{}', {}, 'ERROR: Node {}:[{}]:{}'".format(db.format_time(), dev_id, dev_id, level, error))
        return jsonify(API_response(msg="I hear ya."))

    def api_alive(self, data):
        """API call for node heartbeat and commands."""
        rows = db.query("select commands.dev_id, command from commands join devices on commands.dev_id = devices.dev_id where devices.token = '{}';".format(data["token"]))
        if rows:
            dev_id = rows[0][0]
            cmds = [r[1] for r in rows]
            db.insert_raw("logs", "'{}', {}, 'Sending commands: {}'".format(db.format_time(), dev_id, "\n".join(cmds)))
            return jsonify(API_response(command=cmds))
        else:
            return jsonify(API_response())

    def api_command(self, data):
        """API call for administration."""
        token = data["token"]
        command = data["command"]
        db.insert_raw("logs", "'{}', null, 'Command invoked by [{}]: {}'".format(db.format_time(), token, command))
        if len(db.select("users", "*", "token='{}'".format(token))) == 1:
            cmd = command.split(" ")
            if not cmd:
                return jsonify(API_fatal("No command supplied."))
            if cmd[0] == "candidates":
                return jsonify(API_response(candidates=self.candidates))
            elif cmd[0] == "approve":
                if len(cmd) == 3 and cmd[1].isdigit() and cmd[2].isdigit():
                    for i in range(len(self.candidates)):
                        if self.candidates[i][0] == int(cmd[1]):
                            if db.select("devices", "*", "dev_id={}".format(cmd[1])):
                                db.query("update devices set token='{}' where dev_id={};".format(self.candidates[i][1], cmd[1]))
                            else:
                                db.insert_raw("devices", "{}, '{}', {}, null".format(self.candidates[i][0], self.candidates[i][1], cmd[2]))
                            return jsonify(API_response())
                    return jsonify(API_error("No such candidate dev_id."))
                else:
                    return jsonify(API_fatal("Invalid query."))
            #elif cmd[0] == "room":
            #    if len(cmd) == 3 and cmd[1].isdigit():
            #        db.insert_raw("rooms", "{}, '{}', null".format(cmd[1], cmd[2]))
            return jsonify(API_error("Unknown command."))
        else:
            return jsonify(API_error("Unable to authenticate."))

    def api_view(self, data):
        """API call for client (user) to view the data."""
        room = data["room"]
        try:
            requested_data = data["data"]
            assert not [i for i in requested_data if not i in self.allowed_view_req_data] # Check if there aren't any unallowed items
            requested_data.insert(0, "time")
        except KeyError:
            requested_data = ("time",) + self.allowed_view_req_data
        except AssertionError:
            return abort(400)

        try:
            field_time = data["time"]
            try:
                exact = field_time["time"]
                return self._view_format(room, requested_data, db.select("data", ",".join(requested_data), "time = '{}' and room_number={}".format(exact, room)))
            except KeyError:
                try:
                    fro = field_time["time-from"]
                    to = field_time["time-to"]
                    return self._view_format(room, requested_data, db.select("data", ",".join(requested_data), "time between cast('{}' as DATETIME) and cast('{}' as DATETIME) and room_number={}".format(fro, to, room)))
                except KeyError:
                    return abort(400)
        except KeyError:
            d = db.select("data", "time", "room_number = {}".format(room))
            if d:
                field_time = max(d, key=lambda x: x[0])[0]
            else:
                return self._view_format(room, ("time",), d)
            return self._view_format(room, requested_data, db.select("data", ",".join(requested_data), "time = '{}' and room_number={}".format(field_time, room)))

    def _view_format(self, room, requested, data):
        """Format data for api_view."""
        if not data:
            return jsonify(API_response(room=room, data=[], msg="No data."))
        return jsonify(API_response(room=room, data=[ {requested[col]: str(line[col]) for col in range(len(requested))} for line in data]))
                

    def get_last(self):
        """Get last device id."""
        d = db.select("devices", "dev_id")
        if d:
            return max(d, key=lambda x: x[0])[0]
        else:
            return 0

    def create_token(self):
        """Generate an identification token"""
        return sha256((db.format_time() + str(randint(0,100)) + repr(self)).encode()).hexdigest()

