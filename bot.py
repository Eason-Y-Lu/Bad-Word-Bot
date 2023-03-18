import discord
import re
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)

# Define the check function for admin role
def is_admin(ctx):
    return discord.utils.get(ctx.author.roles, name='admin') is not None


@bot.command()
async def ping(ctx):
    await ctx.send(f"The bot is currently {str(bot.latency*1000)}ms latency and online.")


@bot.command()
async def profanity(ctx):
    with open('profanity.txt', 'r') as file:
        profanity_words = [word.strip() for word in file]
    if profanity_words:
        if sum(len(word) for word in profanity_words) <= 1900:
            await ctx.send("Current profanity list:\n" + "\n".join(profanity_words))
        else:
            with open('profanity_list.txt', 'w') as f:
                f.write("\n".join(profanity_words))
            with open('profanity_list.txt', 'rb') as f:
                await ctx.send("Current profanity list is too long to display. Here's a text file with the full list:",
                               file=discord.File(f, 'profanity_list.txt'))
    else:
        await ctx.send("The profanity list is currently empty.")


@bot.command()
@commands.has_role('Office of Strategic Services')
async def add(ctx, word):
    with open('profanity.txt', 'a') as file:
        file.write(word + "\n")
    await ctx.send(f"Added \"{word}\" to the profanity list.")


@bot.command()
@commands.has_role('Office of Strategic Services')
async def remove(ctx, word):
    with open('profanity.txt', 'r') as file:
        profanity_words = [w.strip() for w in file]
    if word in profanity_words:
        profanity_words.remove(word)
        with open('profanity.txt', 'w') as file:
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
