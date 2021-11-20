#!/bin/python3

import discord
import os
import asyncio
import database
import help_embed as hell
from configparser import ConfigParser
from discord.ext import commands
from discord_components import *


# Setting up Prefix and removing default help command.
bot = commands.Bot(command_prefix=['.'], case_insensitive=True, intents=discord.Intents.all())
bot.remove_command('help')

# Getting discord bot token from environment variable
TOKEN = os.environ['TEST_BOT']


# Loading Cogs and changing presence when the bot is online
@bot.event
async def on_ready():
    DiscordComponents(bot)
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f"Cogs.{filename[:-3]}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with your mind."))
    print("Seductress is ready and online...")


@bot.command(aliases=['h', '?'])
async def help(ctx):
    def check(res):
        return ctx.author == res.user and res.channel == ctx.channel
    m = await ctx.send(embed=hell.main, components=[[Button(style=ButtonStyle.blue, label="Main", disabled=True),
                                                     Button(style=ButtonStyle.blue, label='Lock'),
                                                     Button(style=ButtonStyle.blue, label='Domme only'),
                                                     Button(style=ButtonStyle.red, label='NSFW'),
                                                     Button(style=ButtonStyle.green, label='Admin')]])
    while True:
        try:
            response = await bot.wait_for('button_click', timeout=60, check=check)
            if response.component.label == 'Main':
                await m.edit(embed=hell.main, components=[[Button(style=ButtonStyle.blue, label="Main", disabled=True),
                                                           Button(style=ButtonStyle.blue, label='Lock'),
                                                           Button(style=ButtonStyle.blue, label='Domme only'),
                                                           Button(style=ButtonStyle.red, label='NSFW'),
                                                           Button(style=ButtonStyle.green, label='Admin')]])
                await response.respond(type=6)

            elif response.component.label == 'Lock':
                await m.edit(embed=hell.lock, components=[[Button(style=ButtonStyle.blue, label="Main"),
                                                           Button(style=ButtonStyle.blue, label='Lock', disabled=True),
                                                           Button(style=ButtonStyle.blue, label='Domme only'),
                                                           Button(style=ButtonStyle.red, label='NSFW'),
                                                           Button(style=ButtonStyle.green, label='Admin')]])
                await response.respond(type=6)

            elif response.component.label == 'Domme only':
                await m.edit(embed=hell.domme, components=[[Button(style=ButtonStyle.blue, label="Main"),
                                                            Button(style=ButtonStyle.blue, label='Lock'),
                                                            Button(style=ButtonStyle.blue, label='Domme only', disabled=True),
                                                            Button(style=ButtonStyle.red, label='NSFW'),
                                                            Button(style=ButtonStyle.green, label='Admin')]])
                await response.respond(type=6)

            elif response.component.label == 'NSFW':
                await m.edit(embed=hell.nsfw, components=[[Button(style=ButtonStyle.blue, label="Main"),
                                                           Button(style=ButtonStyle.blue, label='Lock'),
                                                           Button(style=ButtonStyle.blue, label='Domme only'),
                                                           Button(style=ButtonStyle.red, label='NSFW', disabled=True),
                                                           Button(style=ButtonStyle.green, label='Admin')]])
                await response.respond(type=6)

            elif response.component.label == 'Admin':
                await m.edit(embed=hell.admin, components=[[Button(style=ButtonStyle.blue, label="Main"),
                                                            Button(style=ButtonStyle.blue, label='Lock'),
                                                            Button(style=ButtonStyle.blue, label='Domme only'),
                                                            Button(style=ButtonStyle.red, label='NSFW'),
                                                            Button(style=ButtonStyle.green, label='Admin', disabled=True)]])
                await response.respond(type=6)

        except asyncio.TimeoutError:
            break


# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CommandInvokeError):
#         if isinstance(error.original, discord.errors.Forbidden):
#             embed = discord.Embed(title='I don\'t feel so Good.', description=f"I am restrained help, Please make sure that I have **Administration Permissions** and **Elevate my Role**, then try again.", color=0xFF2030)
#             await ctx.author.send(embed=embed)
#             await ctx.send(embed=embed)

#     if isinstance(error, commands.NoPrivateMessage):
#         embed = discord.Embed(description=f"{ctx.author.mention} you should be using this command in server.", color=0xF2A2C0)
#         await ctx.send(embed=embed)

#     if isinstance(error, commands.errors.MissingPermissions):
#         embed = discord.Embed(title='I see a Fake administrator', description=f"{ctx.author.mention} you don't have **Administration Permissions** in the server.", color=0xF2A2C0)
#         await ctx.send(embed=embed)

#     if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
#         m = await ctx.reply("<:staff:897777248839540757> You need to pass all required Argument properly.")
#         await asyncio.sleep(5)
#         await m.delete()


if __name__ == '__main__':
    bot.run(TOKEN)
