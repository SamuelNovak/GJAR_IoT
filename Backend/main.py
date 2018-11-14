#!/usr/bin/python3

import os, time
import yaml
from flask import Flask, request, abort, send_from_directory, g

from lib import api_manager
from webhook import webhook
from updater import update_hook


app = Flask(__name__)

with open("/GJAR_IoT/Backend/config.yml") as f:
    conf = yaml.load(f.read())

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = conf["database"]["user"]
app.config['MYSQL_DATABASE_PASSWORD'] = conf["database"]["password"]
app.config['MYSQL_DATABASE_DB'] = conf["database"]["db"]
app.config['MYSQL_DATABASE_HOST'] = conf["database"]["host"]

os.chdir(conf["base-dir"])

webhook("Loading Flask application. Should be running as a daemon. Yayy!")

@app.route("/v<version>/<req>", methods=["POST"])
def api_call(version, req):
    if request.is_json:
        return api_manager.call(version, req.lower(), request.get_json())
    else:
        return abort(400)

@app.route("/githook/" + conf["git"]["token"], methods=["POST"])
def hook():
    if request.is_json:
        return update_hook(request.headers, request.get_json(), conf["git"])
    else:
        return abort(400)

if __name__ == '__main__':
    app.run()
