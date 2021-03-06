import importlib, importlib.util
import os
from flask import jsonify, abort


apis = {}

def call(version, request, data):
    """Find and load the appropriate API and call the requested method."""
    if version not in apis:
        name = "APIv{}".format(version)
        path = "lib/{}.py".format(name)
        print("Loading", path)
        if os.path.isfile(path):
            module = importlib.import_module("lib." + name, "lib")
            apis[version] = module.api()
        else:
            abort(404)
    return apis[version].call(request, data)
