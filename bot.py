import discord
import re
import os

from discord import Intents

intents = Intents.default()
intents.members = True

client = discord.Client(intents=intents)
my_secret = os.environ['DISCORD_BOT_TOKEN']


@client.event
async def on_message(message):
  if message.author.bot or isinstance(message.channel, discord.DMChannel):
    return

  profanity_words = ['badword1', 'badword2', 'badword3']

  pattern = re.compile(r'\b(?:%s)\b' % '|'.join(profanity_words),
                       re.IGNORECASE)
  if pattern.search(message.content):
    filtered_message = pattern.sub(
      lambda match: match.group(1) + '*' *
      (len(match.group(0)) - 2) + match.group(-1), message.content)
    filtered_message = filtered_message.replace(f"<@{message.author.id}>",
                                                f"{message.author}:")
    await message.delete()
    await message.channel.send(filtered_message)


client.run(my_secret)
