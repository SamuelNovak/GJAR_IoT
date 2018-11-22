from discord.channel import Channel
from discord.client import Client

from .persist import Persistence

def get_general_channel(client:Client) -> Channel:
    for chan in client.get_all_channels():
        if chan.name == "general":
            return chan