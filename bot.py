import discord
import os
import re
from discord.ext import commands
from fuzzywuzzy import fuzz, process

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)

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
            with open(f'profanity_{guild_id}.txt', 'w') as f:
                f.write("\n".join(profanity_words))
            with open(f'profanity_{guild_id}.txt', 'rb') as f:
                await ctx.send("Current profanity list is too long to display. Here's a text file with the full list:",
                               file=discord.File(f, f'profanity_{guild_id}.txt'))
    else:
        await ctx.send("The profanity list is currently empty. Use the `add` command to add a word.")


@bot.command()
@commands.has_role('Mod (Praeses)')
async def add(ctx, *, words):
    guild_id = ctx.guild.id
    pattern = r'\[([^\[\]]+)\]'  # regular expression to match words in square brackets
    matches = re.findall(pattern, words)
    if not matches:
        await ctx.send("Please provide at least one word enclosed in square brackets.")
        return
    added_words = []
    try:
        with open(f'profanity_{guild_id}.txt', 'a') as file:
            for match in matches:
                file.write(match + "\n")
                added_words.append(match)
    except Exception as e:
        await ctx.send(f"An error occurred while updating the profanity list: {e}")
        return
    if len(added_words) > 0:
        added_word_str = "\n".join(f"- {w}" for w in added_words)
        await ctx.send(f"Added {len(added_words)} words to the profanity list:\n{added_word_str}")
    else:
        await ctx.send("No words were added to the profanity list.")

@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide at least one word enclosed in square brackets.")
    else:
        await ctx.send(f"An error occurred while executing the command: {error}")

@bot.command()
@commands.has_role('Mod (Praeses)')
async def remove(ctx, *, words):
    guild_id = ctx.guild.id
    pattern = r'\[([^\[\]]+)\]'  # regular expression to match words in square brackets
    matches = re.findall(pattern, words)
    if not matches and words != "all":
        await ctx.send("Please provide at least one word enclosed in square brackets, or enter 'all' to remove all words from the profanity list.")
        return
    removed_words = []
    try:
        with open(f'profanity_{guild_id}.txt', 'r') as file:
            profanity_words = [w.strip() for w in file]
        if words == "all":
            removed_words = profanity_words
            profanity_words = []
        else:
            for match in matches:
                if match in profanity_words:
                    profanity_words.remove(match)
                    removed_words.append(match)
        with open(f'profanity_{guild_id}.txt', 'w') as file:
            file.write("\n".join(profanity_words))
    except Exception as e:
        await ctx.send(f"An error occurred while updating the profanity list: {e}")
        return
    if len(removed_words) > 0:
        removed_word_str = "\n".join(f"- {w}" for w in removed_words)
        await ctx.send(f"Removed {len(removed_words)} words from the profanity list:\n{removed_word_str}")
    elif words == "all":
        await ctx.send("Removed all words from the profanity list.")
    else:
        await ctx.send("No words were removed from the profanity list.")

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide at least one word enclosed in square brackets, or enter 'all' to remove all words from the profanity list.")
    else:
        await ctx.send(f"An error occurred while executing the command: {error}")

@bot.command()
async def role(ctx):
    user_roles = [role.name for role in ctx.author.roles]
    user_roles = [role[1:] if role.startswith("@") else role for role in user_roles]
    await ctx.send(f"You have the following roles: {', '.join(user_roles)}")

@bot.command()
@commands.has_role('Mod (Praeses)')
async def debug(ctx):
    guild_id = ctx.guild.id
    profanity_file = f'profanity_{ctx.guild.id}.txt'

    try:
        with open(profanity_file, 'r') as file:
            profanity_words = [word.strip() for line in file for word in line.split('\n') if word.strip()]
    except FileNotFoundError:
        await ctx.send(f"Could not find profanity list file \"{profanity_file}\"")
        return
    except Exception as e:
        await ctx.send(f"An error occurred while reading profanity list file: {e}")
        return

    output = f"Profanity words ({len(profanity_words)}):\n"
    for i, word in enumerate(profanity_words):
        output += f"{i+1}. {word}\n"
        if i % 20 == 19:  # send every 20 lines to avoid message size limits
            await ctx.send(output)
            output = ""
    if output:
        await ctx.send(output)

@debug.error
async def debug_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command.")

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
        ratio = fuzz.token_set_ratio(word, message.content)
        if ratio >= 90:
            regex_pattern = r"\b\w*" + re.escape(word) + r"\w*\b"
            regex_match = re.search(regex_pattern, message.content, re.IGNORECASE)
            if regex_match:
                filtered_word = word[0] + '*' * (len(word) - 2) + word[-1]
                filtered_message = re.sub(regex_pattern, filtered_word, message.content, flags=re.IGNORECASE)
                filtered_message = filtered_message.replace(f"<@{message.author.id}>", '{user said}')
                await message.delete()
                await message.channel.send(f"{message.author}: {filtered_message}")
                break
    await bot.process_commands(message)
bot.run('#removed')
