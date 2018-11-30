from argparse import ArgumentParser

from discord.channel import Channel
from discord.client import Client

from .persist import Persistence

parser = ArgumentParser()

def process_command(client:Client, pers:Persistence, command:str):
    pass