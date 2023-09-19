import discord

import os
from dotenv import load_dotenv
import keep_alive

# imports from other files
from translate import translate_text
from dmoj import fetch_points, fetch_ccc, connect_account
from db_utils import fetch_id

load_dotenv("environment/.env")  # load all the variables from the env file
token = str(os.getenv("TOKEN"))

bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!\n")
    print('Servers:')
    for guild in bot.guilds:
        print(f"- {guild.name}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(",translate"):
        cmd = message.content.split()
        if message.reference:  # translate replied message
            original_message = await message.channel.fetch_message(message.reference.message_id)
            translated_text = translate_text(original_message.content, "en")
            await message.reply(translated_text)

        elif len(cmd) > 1:
            translated_text = translate_text(cmd[1], "en")
            await message.reply(translated_text)


@bot.slash_command(name="hello", description="A test command to make sure bot is working")
async def hello(ctx):
    await ctx.respond("Hey!")


@bot.slash_command(name="react", description="React to a message")
async def react(ctx, message: discord.Option(str,
                                             "ID of the MESSAGE to react to"),
                reaction: discord.Option(str,
                                         "Name of the reaction (omit colons)"),
                channel: discord.Option(str,
                                        "ID of the CHANNEL to react to",
                                        required=False)):
    try:
        reaction = reaction.strip(":")
        if not channel:
            channel = bot.get_channel(ctx.channel.id)
        else:
            channel = bot.get_channel(channel)

        message = await channel.fetch_message(message)
        reaction = discord.utils.get(bot.emojis, name=reaction)
        await message.add_reaction(reaction)
        await ctx.respond("Successfully reacted to message", ephemeral=True)

    except:
        await ctx.respond(
            "Invalid channel ID, message ID, or reaction name. Also make sure that the bot has permission to react external emojis (from other servers)",
            ephemeral=True)


@bot.slash_command(name="fetch_points", description="Fetch your CCC points from DMOJ")
async def ccc_points(ctx, username: discord.Option(str,
                                                   "Get the points of a specific user (this is your own DMOJ account by default)",
                                                   required=False)):
    try:
        # return data on a specific DMOJ account
        if username:
            points = fetch_points(username)
            await ctx.respond(f"**{username}** has **{points}** CCC points.")

        # get your own data
        else:
            user = fetch_id(ctx.author.id)
            if not user:  # user did not connect to a DMOJ account
                await ctx.respond("You have not connected to a DMOJ account yet. You can do so using `/connect_account [DMOJ username]`")
            else:
                points = fetch_points(user)
                await ctx.respond(f"You have **{points}** CCC points.")

    except Exception as e:
        print(e)
        await ctx.respond(
            "An error has occurred while fetching CCC points. Please make you input a valid DMOJ account",
            ephemeral=True)


@bot.slash_command(name="connect_account", description="Connect your discord account to your DMOJ account")
async def connect_dmoj_account(ctx, username: discord.Option(str, "Your DMOJ username")):
    try:
        connect_account(ctx.author.id, username)
        await ctx.respond(f"Successfully connected your discord account to **{username}**")

    except Exception as e:
        print(e)
        await ctx.respond("An error has occurred while connecting your account. Please make sure you correctly input "
                          "your DMOJ account")


keep_alive.keep_alive()
bot.run(token)
