import os
import discord
import re

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    bad_words = ['profanity', 'badword', 'curse']

    for word in bad_words:
        pattern = re.compile(r"\b" + word + r"\b", re.IGNORECASE)
        if pattern.search(message.content):
            new_content = pattern.sub(word[0] + '*' * (len(word) - 2) + word[-1], message.content)
            await message.channel.send(f"{message.author.mention} said: {new_content}")
            await message.delete()
            return

    if not message.content.strip():
        await message.delete()
        await message.channel.send("Your message was deleted because it contained no text.")
        return

client.run(os.environ['TOKEN'])
