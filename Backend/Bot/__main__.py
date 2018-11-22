import sys

import discord

from .persist import load_config, Persistence
from .util import get_general_channel


config = load_config()
try:
    token = config["token"]
except KeyError:
    print("No token.")
    exit(1)

try:
    pers = Persistence(config["pers-file"])
except KeyError:
    print("No persistence file in config.")
    exit(1)

client = discord.Client(command_prefix="!")

@client.event
async def on_ready():
    print("Connected to server as {}.".format(client.user))
    try:
        greet = config["greeting"]
        if "{}" in greet:
            greet = greet.format(client.user.name)
    except KeyError:
        greet = "{} connected.".format(client.user.name)
    except:
        print("Malformed greeting string.")
        return
    await client.send_message(get_general_channel(client), greet)

@client.event
async def on_message(message):
    print(message.author, message.content)

# Testing REPL
from threading import Thread
def repl():
    while True:
        i = input("$ ")
        if i == "exit":
            break
        else:
            try:
                print(eval(i))
            except:
                print(sys.exc_info())
    client.close()

# Main run
try:
    # Thread(target=repl).start()
    client.run(token)
except discord.errors.LoginFailure:
    print("Login failure.")
    exit(2)