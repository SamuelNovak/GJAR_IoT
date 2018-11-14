from flask import abort
from subprocess import Popen, PIPE
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
    m = Popen(["git", "fetch", upstream, branch], stdout=PIPE).communicate()[0].decode() + "\n"
    m += Popen(["git", "pull", upstream, branch], stdout=PIPE).communicate()[0].decode()
    webhook(m)
    print(m)