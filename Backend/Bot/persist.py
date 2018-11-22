import os
import sys
import yaml

def load_config() -> dict:
    path = os.path.normpath(
        os.path.join(
            os.path.dirname(sys.argv[0]),
            "..",
            "config.yml"
        )
    )
    try:
        with open(path, "r") as f:
            try:
                conf = yaml.safe_load(f.read())
                try:
                    return conf["bot"]
                except:
                    print("No bot configuration in the config file.")
                    exit(1)
            except:
                print("Invalid config file.")
                exit(1)
    except:
        print("No config file found.")
        exit(1)

class Persistence():
    _path = "None"
    _data = {}
    def __init__(self, path):
        self._path = path
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    data = yaml.safe_load(f.read())
                except:
                    print("Persistence error: Unable to read data.")
                    data = {}
                    i = 0
                    while os.path.exists(path + str(i)):
                        i += 1
                    self._path = path + str(i)
                    print("Redirecting persistence to <{}>.".format(self._path))
            self._data = data

    def __getattr__(self, name:str):
        try:
            return self._data[name]
        except KeyError:
            self._data[name] = None
            return None
    
    def __setattr__(self, name:str, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            print("__setattr__(self, {}, {})".format(repr(name), repr(value)))
            self._data[name] = value
