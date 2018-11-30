import sys

import discord

from .persist import load_config, Persistence
from .util import get_general_channel
from .command import process_command


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



client = discord.Client()
try:
    prefix = config["command-prefix"]
except KeyError:
    prefix = "!"

try:
    pers["root"] = config["root"]
except:
    pass

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
        greet = "{} connected.".format(client.user.name)
    await client.send_message(get_general_channel(client), greet)

@client.event
async def on_message(message):
    if message.author != client.user:
        print(message.author, message.author.id, message.content)
        if message.content.startswith(prefix):
            process_command(client, pers, message.content)



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
    del pers
except discord.errors.LoginFailure:
    print("Login failure.")
    del pers
    exit(2)