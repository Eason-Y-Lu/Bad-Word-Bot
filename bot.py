import discord
import os
import re
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz

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
            with open(f'profanity_list_{guild_id}.txt', 'w') as f:
                f.write("\n".join(profanity_words))
            with open(f'profanity_list_{guild_id}.txt', 'rb') as f:
                await ctx.send("Current profanity list is too long to display. Here's a text file with the full list:",
                               file=discord.File(f, f'profanity_list_{guild_id}.txt'))
    else:
        await ctx.send("The profanity list is currently empty. Use the `add` command to add a word.")


@bot.command()
@commands.has_role('Office of Strategic Services')
async def add(ctx, word):
    guild_id = ctx.guild.id
    with open(f'profanity_{guild_id}.txt', 'a') as file:
        file.write(word + "\n")
    await ctx.send(f"Added \"{word}\" to the profanity list.")


@bot.command()
@commands.has_role('Office of Strategic Services')
async def remove(ctx, word):
    guild_id = ctx.guild.id
    with open(f'profanity_{guild_id}.txt', 'r') as file:
        profanity_words = [w.strip() for w in file]
    if word in profanity_words:
        profanity_words.remove(word)
        with open(f'profanity_{guild_id}.txt', 'w') as file:
            file.write("\n".join(profanity_words))
        await ctx.send(f"Removed the following word from the profanity list: \"{word}\"")
    else:
        await ctx.send(f"\"{word}\" was not found in the profanity list.")


@bot.command()
async def role(ctx):
    user_roles = [role.name for role in ctx.author.roles]
    user_roles = [role[1:] if role.startswith("@") else role for role in user_roles]
    await ctx.send(f"You have the following roles: {', '.join(user_roles)}")


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    # Ignore messages sent by bots or in DM channels
    if message.author.bot or isinstance(message.channel, discord.DMChannel):
        return

    # Ignore messages that are bot commands
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # Get the name of the profanity list file based on the server name
    profanity_file = f"{message.guild.name}_profanity.txt"

    # Check if the profanity list file exists
    if os.path.isfile(profanity_file):
        with open(profanity_file, 'r') as file:
            profanity_words = [word.strip() for word in file]
    else:
        profanity_words = []

    # Check for misspellings and fuzzy matches of profanity words
    spell = SpellChecker()
    misspelled_words = spell.unknown(profanity_words)
    fuzzy_matches = []

    for word in message.content.split():
        for profanity_word in profanity_words:
            # Check for exact matches
            if word.lower() == profanity_word.lower():
                filtered_word = profanity_word[0] + '*' * (len(profanity_word) - 2) + profanity_word[-1]
                message.content = message.content.replace(profanity_word, filtered_word)
                break
            # Check for misspellings
            if word.lower() in misspelled_words and spell.correction(word).lower() == profanity_word.lower():
                filtered_word = profanity_word[0] + '*' * (len(profanity_word) - 2) + profanity_word[-1]
                message.content = message.content.replace(word, filtered_word)
                break
            # Check for fuzzy matches
            if fuzz.ratio(word.lower(), profanity_word.lower()) > 80:
                fuzzy_matches.append(profanity_word)

    # Replace fuzzy matches with filtered words
    for fuzzy_match in fuzzy_matches:
        filtered_word = fuzzy_match[0] + '*' * (len(fuzzy_match) - 2) + fuzzy_match[-1]
        message.content = re.sub(fuzzy_match, filtered_word, message.content, flags=re.IGNORECASE)

    # Replace author's username with "{user said}"
    message.content = message.content.replace(f"<@{message.author.id}>", '{user said}')

    # Send the filtered message
    await message.delete()
    await message.channel.send(f"{message.author}: {message.content}")

    # Process commands after checking for profanity words
    await bot.process_commands(message)


bot.run('#redacted')
