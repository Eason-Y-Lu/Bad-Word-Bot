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

    if not message.content.strip():
        return

    has_bad_word = False
    for word in message.content.split():
        if word.lower() in bad_words:
            pattern = re.compile(r"\b" + word + r"\b", re.IGNORECASE)
            message.content = pattern.sub(word[0] + '*' * (len(word) - 2) + word[-1],
                                          message.content)
            has_bad_word = True

    if has_bad_word:
        await message.channel.send(f"{message.author.mention} said: {message.content}")
        await message.delete()
    else:
        return


my_secret = os.environ['TOKEN']
client.run(my_secret)
