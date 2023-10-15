import discord

import os
from dotenv import load_dotenv
import keep_alive

# imports from other files
from translate import translate_text
from user_data import get_user_data
from dmoj import fetch_points, fetch_ccc, connect_account
from levels import handle_message_sent
from bot_graphics.banner import make_banner
from bot_graphics.leaderboard import make_leaderboard

load_dotenv("environment/.env")  # load all the variables from the env file
token = os.getenv("SOMETOKEN")

bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    print('Servers:')
    for guild in bot.guilds:
        print(f"- {guild.name}")


@bot.event
async def on_application_command_completion(ctx):
    handle_message_sent(ctx)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    handle_message_sent(message, is_slash_command=False)
    
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
                                             "ID of the message to react to"),
                reaction: discord.Option(str,
                                         "Name of the reaction"),
                channel: discord.Option(str,
                                        "ID of the channel to react in",
                                        required=False)):
    if not message.isdigit():
        await ctx.respond(
            "Invalid message ID.",
            ephemeral=True
        )
        return
    elif channel and not channel.isdigit():
        await ctx.respond(
            "Invalid channel ID.",
            ephemeral=True
        )
        return
    
    try:
        reaction = reaction.strip(":")
        if not channel:
            channel = ctx.channel
        else:
            channel = bot.get_channel(int(channel))
            if not channel:
                await ctx.respond(
                    "Invalid channel ID.",
                    ephemeral=True
                )
                return
        
        message = await channel.fetch_message(message)
        reaction = discord.utils.get(bot.emojis, name=reaction)
        await message.add_reaction(reaction)
        await ctx.respond("Successfully reacted to message", ephemeral=True)
    
    except discord.errors.NotFound as e:
        print(e)
        await ctx.respond(
            "Invalid message ID.",
            ephemeral=True
        )
    except discord.errors.InvalidArgument as e:
        print(e)
        await ctx.respond(
            "Invalid reaction name.",
            ephemeral=True
        )
    except:
        await ctx.respond(
            "An error has occurred while reacting. Make sure that the bot has permission to react external emojis (from other servers); if it does, then please alert an Executive or Contributor.",
            ephemeral=True
        )
        raise


@bot.slash_command(name="fetch_points", description="Fetch your CCC points from DMOJ")
async def ccc_points(ctx, user: discord.Option(discord.User, "Get the points of another user", required=False, default=None)):
    try:
        user_id = (user.id if user else ctx.author.id)
        user_data = get_user_data(user_id)
        if user_data is None:
            if user:
                await ctx.respond(f"{user.name} has not connected to a DMOJ account yet. This can be done using `/connect_account [DMOJ username]`")
            else:
                await ctx.respond("You have not connected to a DMOJ account yet. You can do so using `/connect_account [DMOJ username]`")
            return
        
        await ctx.defer() #Generating the image can take a while
        
        if not user:
            user = bot.get_user(ctx.author.id)
        
        filename = make_banner(user)
        with open(filename, "rb") as file_pointer:
            await ctx.followup.send(file=discord.File(file_pointer))
    
    except:
        await ctx.respond("An error has occurred while fetching CCC points. Please alert an Executive or Contributor.")
        raise


@bot.slash_command(name="leaderboard", description="Get the server-wide leaderboard")
async def leaderboard(ctx):
    try:
        await ctx.defer() #Generating the image can take a while
        
        filename = make_leaderboard(bot)
        with open(filename, "rb") as file_pointer:
            await ctx.followup.send(file=discord.File(file_pointer))
    
    except:
        await ctx.respond("An error has occurred while fetching the leaderboard. Please alert an Executive or Contributor.")
        raise



@bot.slash_command(name="connect_account", description="Connect your Discord account to your DMOJ account")
async def connect_dmoj_account(ctx, username: discord.Option(str, "Your DMOJ username")):
    try:
        connect_account(ctx.author.id, username)
        await ctx.respond(f"Successfully connected your Discord account to **{username}**.")
    
    except:
        await ctx.respond("An error has occurred while connecting your account. Please make sure that you correctly input your DMOJ username; if you did, then please alert an Executive or Contributor.")
        raise


keep_alive.keep_alive()
bot.run(token)

