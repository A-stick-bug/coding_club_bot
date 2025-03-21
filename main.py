import discord

import os
from dotenv import load_dotenv
from typing import List

import keep_alive

# imports from other files
from translate import translate_text
from user_data import get_user_data
from dmoj import connect_account
from levels import handle_message_sent
from banner import make_banner
from leaderboard import make_leaderboard
from points_plotter import fetch_problem_history, fetch_point_history, plot_points
from problem_types_plotter import plot_problem_types, plot_problem_types_weighted

load_dotenv("environment/.env")  # load all the variables from the env file
token = os.getenv("TOKEN")

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
        cmd = message.content.split(" ", 1)
        if message.reference:  # translate replied message
            original_message = await message.channel.fetch_message(message.reference.message_id)
            translated_text = translate_text(original_message.content, "en")
            await message.reply(translated_text)

        elif len(cmd) > 1:
            translated_text = translate_text(message.content[11:], "en")
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
            "An error has occurred while reacting. Make sure that the bot has permission to react external emojis (from other servers); if it does, then please alert an Executive.",
            ephemeral=True
        )
        raise


@bot.slash_command(name="fetch_points", description="Fetch your CCC points from DMOJ")
async def ccc_points(ctx, user: discord.Option(discord.User, "Get the points of another user", required=False,
                                               default=None)):
    try:
        user_id = (user.id if user else ctx.author.id)
        user_data = get_user_data(user_id)
        if user_data is None:
            if user:
                await ctx.respond(
                    f"{user.name} has not connected to a DMOJ account yet. This can be done using `/connect_account [DMOJ username]`")
            else:
                await ctx.respond(
                    "You have not connected to a DMOJ account yet. You can do so using `/connect_account [DMOJ username]`")
            return

        await ctx.defer()  # Generating the image can take a while

        if not user:
            user = bot.get_user(ctx.author.id)

        filename = make_banner(user)
        with open(filename, "rb") as file_pointer:
            await ctx.followup.send(file=discord.File(file_pointer))

    except:
        await ctx.respond("An error has occurred while fetching CCC points. Please alert an Executive.")
        raise


@bot.slash_command(name="leaderboard", description="Get the server-wide leaderboard")
async def leaderboard(ctx):
    try:
        await ctx.defer()  # Generating the image can take a while

        filename = make_leaderboard(bot)
        with open(filename, "rb") as file_pointer:
            await ctx.followup.send(file=discord.File(file_pointer))

    except:
        await ctx.respond(
            "An error has occurred while fetching the leaderboard. Please alert an Executive.")
        raise


@bot.slash_command(name="connect_account", description="Connect your Discord account to your DMOJ account")
async def connect_dmoj_account(ctx, username: discord.Option(str, "Your DMOJ username")):
    try:
        connect_account(ctx.author.id, username)
        await ctx.respond(f"Successfully connected your Discord account to **{username}**.")

    except:
        await ctx.respond(
            "An error has occurred while connecting your account. Please make sure that you correctly input your DMOJ username; if you did, then please alert an Executive.")
        raise


@bot.slash_command(name="plot_points", description="Plot your DMOJ points progression")
async def plot_dmoj_points(ctx, user: discord.Option(discord.User, "Plot points of another user",
                                                     required=False, default=None)):
    try:
        await ctx.defer()
        user_id = user.id if user else ctx.author.id
        user_data = get_user_data(user_id)
        if user_data is None:
            if user:
                await ctx.respond(
                    f"{user.name} has not connected to a DMOJ account yet. This can be done using `/connect_account [DMOJ username]`")
            else:
                await ctx.respond(
                    "You have not connected to a DMOJ account yet. You can do so using `/connect_account [DMOJ username]`")
            return

        history = fetch_point_history(user_data.dmoj_username)
        plot_points(history, user_data.dmoj_username, "Points", "Points Progression")
        await ctx.respond(file=discord.File('point_graph.png'))

    except:
        await ctx.respond("An error has occurred while plotting points. Please alert an Executive.")
        raise


@bot.slash_command(name="plot_problems", description="Plot your DMOJ problems progression")
async def plot_dmoj_problems(ctx, user: discord.Option(discord.User, "Plot problems of another user",
                                                       required=False, default=None)):
    try:
        await ctx.defer()
        user_id = user.id if user else ctx.author.id
        user_data = get_user_data(user_id)
        if user_data is None:
            if user:
                await ctx.respond(
                    f"{user.name} has not connected to a DMOJ account yet. This can be done using `/connect_account [DMOJ username]`")
            else:
                await ctx.respond(
                    "You have not connected to a DMOJ account yet. You can do so using `/connect_account [DMOJ username]`")
            return

        history = fetch_problem_history(user_data.dmoj_username)
        plot_points(history, user_data.dmoj_username, "Problems Solved", "Problems Progression")
        await ctx.respond(file=discord.File('point_graph.png'))

    except:
        await ctx.respond("An error has occurred while plotting problems. Please alert an Executive.")
        raise


@bot.slash_command(name="plot_problem_types", description="Plot your DMOJ solved problem's types")
async def plot_problem_types_cmd(ctx, users: discord.Option(str,
                                                            "Plot problem types of other users (DMOJ usernames, separate with comma)",
                                                            required=False, default=None)):
    try:
        await ctx.defer()
        if not users:  # plot your own problem types
            user_id = ctx.author.id
            user_data = get_user_data(user_id)
            if user_data is None:
                await ctx.respond(
                    "You have not connected to a DMOJ account yet. You can do so using `/connect_account [DMOJ username]`")
                return
            plot_problem_types([user_data.dmoj_username])

        else:  # plot and compare other people's problem types
            dmoj_usernames = users.split(",")
            dmoj_usernames = list(map(lambda x: x.strip(), dmoj_usernames))  # strip whitespace from all usernames
            plot_problem_types(dmoj_usernames)
        await ctx.respond(file=discord.File('problem_types_graph.png'))

    except Exception as e:
        await ctx.respond(f"An error has occurred while plotting types. Please alert an Executive. "
                          f"Error message: {e}")
        raise


@bot.slash_command(name="plot_problem_types_weighted",
                   description="Plot your DMOJ points by problem type. Weighted using the leaderboard system.")
async def plot_problem_types_cmd(ctx, users: discord.Option(str,
                                                            "Plot problem types of other users (DMOJ usernames, separate with comma)",
                                                            required=False, default=None)):
    try:
        await ctx.defer()
        if not users:  # plot your own problem types
            user_id = ctx.author.id
            user_data = get_user_data(user_id)
            if user_data is None:
                await ctx.respond(
                    "You have not connected to a DMOJ account yet. You can do so using `/connect_account [DMOJ username]`")
                return
            plot_problem_types_weighted([user_data.dmoj_username])

        else:  # plot and compare other people's problem types
            dmoj_usernames = users.split(",")
            dmoj_usernames = list(map(lambda x: x.strip(), dmoj_usernames))  # strip whitespace from all usernames
            plot_problem_types_weighted(dmoj_usernames)
        await ctx.respond(file=discord.File('problem_types_graph_weighted.png'))

    except Exception as e:
        await ctx.respond(f"An error has occurred while plotting types. Please alert an Executive. "
                          f"Error message: {e}")
        raise


keep_alive.keep_alive()
bot.run(token)
