import os
import discord
import re
from discord.ext import commands

my_secret = os.environ['DISCORD_BOT_TOKEN']
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)


@bot.event
async def on_ready():
  print('Logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
  if message.author.bot or isinstance(message.channel, discord.DMChannel):
    return

  profanity_words = ['badword1', 'badword2', 'badword3']

  for word in profanity_words:
    # Use regular expressions to match the profanity word regardless of its position in the message
    regex_pattern = r"\b\w*" + re.escape(word) + r"\w*\b"
    regex_match = re.search(regex_pattern, message.content, re.IGNORECASE)

    if regex_match:
      filtered_word = word[0] + '*' * (len(word) - 2) + word[-1]
      filtered_message = re.sub(regex_pattern,
                                filtered_word,
                                message.content,
                                flags=re.IGNORECASE)
      filtered_message = filtered_message.replace(f"<@{message.author.id}>",
                                                  '{user said}')
      await message.delete()
      await message.channel.send(f"{message.author}: {filtered_message}")

      dm_channel = await message.author.create_dm()
      await dm_channel.send(
        f"Hi {message.author.name}, please refrain from using profanity in this server. Thank you!"
      )
      break


bot.run(my_secret)
