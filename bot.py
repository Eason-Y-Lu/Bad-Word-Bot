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


@bot.command()
async def online(ctx):
  await ctx.send(f"The bot is online and ready to filter profanity!")


@bot.event
async def on_message(message):
  if message.author.bot or isinstance(message.channel, discord.DMChannel):
    return

  profanity_words = ['badword1', 'badword2', 'badword3']

  for word in profanity_words:
    if word in message.content.lower():
      filtered_word = word[0] + '*' * (len(word) - 2) + word[-1]
      filtered_message = re.sub(r'\b{}\b'.format(word),
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
