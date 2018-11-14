from flask import abort
from os import system
from webhook import webhook

def update_hook(headers:dict, payload:dict, config:dict):
    try:
        event = headers["X-GitHub-Event"]
    except:
        return abort(400)
    try:
        upstream = config["upstream"]
        branch = config["branch"]
    except:
        return abort(500)

    if event == "push":
        run_update(payload, upstream, branch)
    return ("OK", 200)

def run_update(payload:dict, upstream:str, branch:str):
    webhook("Updater: push event registered.")
    m = system("git fetch {} {}".format(upstream, branch)) + "\n"
    m += system("git pull {} {}".format(upstream, branch))
    webhook(m)
    print(m)