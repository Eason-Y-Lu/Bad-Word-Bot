import discord
import re
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)


@bot.command()
async def online(ctx):
    await ctx.send(f"The bot is currently {str(bot.latency*1000)}ms latency and online.")


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    if message.author.bot or isinstance(message.channel, discord.DMChannel):
        return

    with open('profanity.txt', 'r') as file:
        profanity_words = [word.strip() for word in file]

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
            break

    # Process commands after checking for profanity words
    await bot.process_commands(message)


bot.run('#redacted')
