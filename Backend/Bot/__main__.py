import os
import sys
import yaml

import discord


def load_config() -> dict:
    path = os.path.normpath(
        os.path.join(
            sys.argv[0], "..", "config.yml"
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

config = load_config()
try:
    token = config["token"]
except:
    print("No token.")
    exit(1)

client = discord.Client()

@client.event
async def on_ready():
    print("Connected to server as {}.".format(client.user))
    print("\n".join([str((i.id,i.name)) for i in client.get_all_channels()]))
    await client.send_message(client.get_channel("514610632092418079"), "Hello! {} to save the day. I am the messenger of the... server!".format(client.user.name))

try:
    client.run(token)
except discord.errors.LoginFailure:
    print("Login failure.")
    exit(2)