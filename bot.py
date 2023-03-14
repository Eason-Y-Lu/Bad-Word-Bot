import discord
import re
import os

from discord import Intents
from discord.ext import commands

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)


client = commands.Bot(command_prefix='~', intents=intents)
my_secret = os.environ['DISCORD_BOT_TOKEN']


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author.bot or isinstance(message.channel, discord.DMChannel):
        return

    profanity_words = ['badword1', 'badword2', 'badword3']

    pattern = re.compile(r'\b(?:%s)\b' % '|'.join(profanity_words), re.IGNORECASE)
    if pattern.search(message.content):
        filtered_message = pattern.sub(lambda match: match.group(1) + '*' * (len(match.group(0)) - 2) + match.group(-1), message.content)
        filtered_message = filtered_message.replace(f"<@{message.author.id}>", '{user said}')
        await message.delete()
        await message.channel.send(f"{message.author}: {filtered_message}")

        dm_channel = await message.author.create_dm()
        await dm_channel.send(f"Hi {message.author.name}, please refrain from using profanity in this server. Thank you!")


@client.command()
async def online(ctx):
    await ctx.send(f"The bot is online and ready to filter profanity!")


client.run(my_secret)
