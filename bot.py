#bot.py
#This code is coded by Eason Lu with the Help of ChatGPT.
import discord
import os
import re
from discord.ext import commands
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)
spell = SpellChecker()

@bot.command()
async def ping(ctx):
    await ctx.send(f"The bot is currently {str(bot.latency*1000)}ms latency and online.")


@bot.command()
async def profanity(ctx):
    guild_id = ctx.guild.id
    profanity_file = f'profanity_{guild_id}.txt'

    if not os.path.isfile(profanity_file):
        await ctx.send("There are currently no profanity words in the list. Use the `add` command to add a word.")
        return

    with open(profanity_file, 'r') as file:
        profanity_words = [word.strip() for word in file]
        
    if profanity_words:
        if sum(len(word) for word in profanity_words) <= 1900:
            await ctx.send("Current profanity list:\n" + "\n".join(profanity_words))
        else:
            with open(f'profanity_list_{guild_id}.txt', 'w') as f:
                f.write("\n".join(profanity_words))
            with open(f'profanity_list_{guild_id}.txt', 'rb') as f:
                await ctx.send("Current profanity list is too long to display. Here's a text file with the full list:",
                               file=discord.File(f, f'profanity_list_{guild_id}.txt'))
    else:
        await ctx.send("The profanity list is currently empty. Use the `add` command to add a word.")

@bot.command()
async def add(ctx, *args):
    if len(args) < 1:
        await ctx.send("Error: not enough arguments. Usage: `~add [word1] [word2] ... [wordN]`")
        return

    server_id = str(ctx.guild.id)
    filename = f"profanity_{server_id}.txt"

    words = []
    for arg in args:
        if arg.startswith("[") and arg.endswith("]"):
            words.append(arg[1:-1])
        else:
            await ctx.send(f"Error: invalid argument `{arg}`. Arguments must be enclosed in square brackets, e.g. `[word]`")
            return

    with open(filename, 'a') as file:
        for word in words:
            file.write(word.lower() + "\n")
    
    await ctx.send(f"{', '.join(words)} added successfully!")


@bot.command()
async def remove(ctx, *args):
    if len(args) < 1:
        await ctx.send("Error: not enough arguments. Usage: `~remove [word1] [word2] ... [wordN]` or `~remove all`")
        return

    server_id = str(ctx.guild.id)
    filename = f"profanity_{server_id}.txt"

    words = []
    for arg in args:
        if arg == "all":
            words = ["all"]
            break
        elif arg.startswith("[") and arg.endswith("]"):
            words.append(arg[1:-1])
        else:
            await ctx.send(f"Error: invalid argument `{arg}`. Arguments must be enclosed in square brackets, e.g. `[word]`")
            return

    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        removed = []
        if "all" in words:
            removed = [line.strip() for line in lines]
        else:
            for line in lines:
                word = line.strip()
                if word.lower() not in words:
                    file.write(line)
                else:
                    removed.append(word)

        if len(removed) > 0:
            await ctx.send(f"{', '.join(removed)} removed successfully!")
        else:
            await ctx.send("Error: no words removed. Make sure the words you specified are in the list.")

@bot.command()
async def role(ctx):
    user_roles = [role.name for role in ctx.author.roles]
    user_roles = [role[1:] if role.startswith("@") else role for role in user_roles]
    await ctx.send(f"You have the following roles: {', '.join(user_roles)}")

@bot.command()
@commands.has_role('Chat Mod')
async def debug(ctx):
    guild_id = ctx.guild.id
    profanity_file = f'profanity_{ctx.guild.id}.txt'

    if os.path.isfile(profanity_file):
        with open(profanity_file, 'r') as file:
            profanity_words = [word.strip() for line in file for word in line.split('\n') if word.strip()]
    else:
        profanity_words = []

    await ctx.send(f"Profanity words: {profanity_words}")


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author.bot or isinstance(message.channel, discord.DMChannel):
        return
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    guild_id = message.guild.id
    profanity_file = f'profanity_{guild_id}.txt'

    if os.path.isfile(profanity_file):
        with open(profanity_file, 'r') as file:
            profanity_words = [word.strip() for line in file for word in line.split('\n') if word.strip()]
    else:
        profanity_words = []

    for word in profanity_words:
        # Check for exact match
        regex_pattern = r"\b\w*" + re.escape(word) + r"\w*\b"
        regex_match = re.search(regex_pattern, message.content, re.IGNORECASE)

        # Check for fuzzy match
        if not regex_match:
            fuzzy_match = process.extractOne(word, message.content.split(), scorer=fuzz.token_sort_ratio)
            if fuzzy_match and fuzzy_match[1] >= 80:
                regex_match = True

        # Check for misspelled match
        if not regex_match:
            misspelled_match = spell.correction(word)
            if misspelled_match != word and misspelled_match in message.content:
                regex_match = True

        if regex_match:
            filtered_word = word[0] + '*' * (len(word) - 2) + word[-1]
            filtered_message = re.sub(regex_pattern, filtered_word, message.content, flags=re.IGNORECASE)
            filtered_message = filtered_message.replace(f"<@{message.author.id}>", '{user said}')
            await message.delete()
            await message.channel.send(f"{message.author}: {filtered_message}")
            break

bot.run('#removed')
