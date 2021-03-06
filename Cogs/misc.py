#!/bin/python3
import discord
import asyncio
import database
import requests
import os
from discord.ext import commands
from discord_components import *


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(bot)        

    @commands.command()
    @commands.guild_only()
    async def define(self, ctx, *, word):
        if ctx.author.bot:
            return
        ban_data = database.is_botban(ctx.author.id)
        if ban_data is None:
            url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
            querystring = {"term": word}
            headers = {'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
                    'x-rapidapi-key': os.environ["RAPID_API"]}
            response = requests.request("GET", url, headers=headers, params=querystring).json()['list']
            if len(response) == 0:
                embed = discord.Embed(description=f'<:cry:968287446217400320>  I can\'t find the definition of the word **`{word}`**',
                                      color=0xFF2030)
                await ctx.send(embed=embed)
            else:
                def make_embed(page):
                    embed=discord.Embed(description=f"{response[page]['definition']}\n\nExample:\n> {response[page]['example']}\n\nVotes:\n> <a:upvote:968292752813068298> {response[page]['thumbs_up']}              <a:downvote:968293083982729247> {response[page]['thumbs_down']}",
                                        color=0xF2A2C0)
                    embed.set_footer(text=f"{page + 1}/{len(response)}", icon_url=self.bot.user.avatar_url)
                    embed.set_author(name=word.upper(), url=response[page]['permalink'])
                    return embed
                
                page_no = 0
                m = await ctx.send(embed=make_embed(page_no), components=[[Button(style=ButtonStyle.blue, label="Previous results", disabled=page_no==0),
                                                                        Button(style=ButtonStyle.blue, label='Next results', disabled=page_no==len(response)-1)]])

                while True:
                    def check(res):
                        return ctx.author == res.user and res.channel == ctx.channel and res.message.id == m.id
                    try:
                        click = await self.bot.wait_for('button_click', timeout=90, check=check)
                        await click.respond(type=6)
                        if click.component.label == 'Next results':
                            page_no += 1
                            await m.edit(embed=make_embed(page_no), components=[[Button(style=ButtonStyle.blue, label="Previous results", disabled=page_no==0),
                                                                                Button(style=ButtonStyle.blue, label='Next results', disabled=page_no==len(response)-1)]])
                        elif click.component.label == 'Previous results':
                            page_no -= 1
                            await m.edit(embed=make_embed(page_no), components=[[Button(style=ButtonStyle.blue, label="Previous results", disabled=page_no==0),
                                                                                Button(style=ButtonStyle.blue, label='Next results', disabled=page_no==len(response)-1)]])
                    except asyncio.TimeoutError:
                        await m.edit(embed=make_embed(page_no), components=[])
        else:
            embed=discord.Embed(description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till {ban_data[1]}",
                                color=0xF2A2C0)
            await ctx.send(embed=embed)


    ##############################################################################
    
    #                                                                            #
    #                                                                            #
    #                                  ERRORS                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################
    
    @define.error
    async def on_define_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            embed = discord.Embed(description=f"Usage:\n> **`t.define <word>`** ",
                                  color=0xFF2030)
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Misc(bot))
