#!/bin/python3
import discord
from discord_components import *
import database
import asyncio
import random
import sqlite3
from discord.ext import commands


con = sqlite3.connect(':memory:')
cur = con.cursor()


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(bot)

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                 GAMMBLE                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @commands.command(aliases=['cf'])
    @commands.guild_only()
    @commands.cooldown(3, 1 * 60, commands.BucketType.user)
    async def coinflip(self, ctx, choice: str, bet: int):
        if ctx.author.bot:
            return
        ban_data =  database.is_botban(ctx.author.id)
        if ban_data is None:
            if bet < 10:
                await ctx.reply(f"<:staff:897777248839540757> You need to bet at least 10 <a:pinkcoin:920347688791310366>")
            elif choice.lower() not in ['head', 'tail', 'h', 't', 'heads', 'tails']:
                await ctx.reply(f"<:staff:897777248839540757> usage: **`t.coinflip <head|tail> <bet>`**")
            else:
                coins = database.get_money(ctx.author.id, ctx.guild.id)[2]
                if bet > coins:
                    await ctx.reply(f"<:staff:897777248839540757> really?, you are broke you only have {coins} <a:pinkcoin:920347688791310366>")
                    return
                database.remove_money(ctx.author.id, ctx.guild.id, bet, 0)
                await asyncio.sleep(2)
                if bool(random.getrandbits(1)):

                    if choice.lower() in ['head', 'heads', 'h']:
                        database.add_money(ctx.author.id, ctx.guild.id, 2 * bet, 0)
                        embed = discord.Embed(title='its heads!!', description=f"{ctx.author.mention} won {bet}", color=0x08FF08)
                        await ctx.reply(embed=embed)
                    else:
                        embed = discord.Embed(title='its heads!!', description=f"{ctx.author.mention} lost {bet}", color=0xFF2030)
                        await ctx.reply(embed=embed)

                else:
                    if choice.lower() in ['tail', 'tails', 't']:
                        database.add_money(ctx.author.id, ctx.guild.id, 2 * bet, 0)
                        embed = discord.Embed(title='its tails!!', description=f"{ctx.author.mention} won {bet}", color=0x08FF08)
                        await ctx.reply(embed=embed)
                    else:
                        embed = discord.Embed(title='its tails!!', description=f"{ctx.author.mention} lost {bet}", color=0xFF2030)
                        await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title='Bot ban',
                                  description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{ban_data[1]}:F>",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)                        
            
    @commands.command(aliases=['rps'])
    @commands.guild_only()
    # @commands.cooldown(5, 1 * 60 * 60, commands.BucketType.user)
    async def rockpaper(self, ctx, member: discord.Member, bet: int):
        if ctx.author.bot:
            return
        ban_data = database.is_botban(ctx.author.id)
        if ban_data is not None:
            embed = discord.Embed(title='Bot ban',
                                  description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{ban_data[1]}:F>",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return
        elif database.is_botban(member.id) is not None:
            embed = discord.Embed(title='Bot ban',
                                  description=f"{member.mention} is banned from using {self.bot.user.mention}.",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        author_coin = database.get_money(ctx.author.id, ctx.guild.id)[2]
        member_coin = database.get_money(member.id, ctx.guild.id)[2]
        
        if bet < 10:
            embed = discord.Embed(description=f"<:staff:897777248839540757> You need to bet at least 10 <a:pinkcoin:920347688791310366>",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
        elif bet > author_coin:
            embed = discord.Embed(description=f"{ctx.author.mention} really?, <:staff:897777248839540757> You only have {author_coin} <a:pinkcoin:920347688791310366>",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
        elif bet > member_coin:
            embed = discord.Embed(description=f"<:staff:897777248839540757>, {member.mention} only have {member_coin} <a:pinkcoin:920347688791310366>",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
        else:
            m = await ctx.send(f"{ctx.author.nick or ctx.author.name} is thinking...\n{member.nick or member.name} is thinking...",
                               components=[[Button(style=ButtonStyle.blue, label="Rock", emoji='🗿'),
                                            Button(style=ButtonStyle.blue, label='Paper', emoji='🧻'),
                                            Button(style=ButtonStyle.blue, label='Scissors', emoji='✂️',)]])
            try:
                def check(res):
                    return res.user == ctx.author or res.user == member and res.message.id == m.id
                response = await self.bot.wait_for('button_click', timeout=30, check=check)
                await response.respond(type=6)
                if response.user == ctx.author:
                    author_choice = response.component.label
                    await m.edit(f"{ctx.author.nick or ctx.author.name} made a choice.\n{member.nick or member.name} is thinking...")
                    try:
                        def check(res):
                            return res.user == member and res.message.id == m.id
                        response = await self.bot.wait_for('button_click', timeout=30, check=check)
                        await response.respond(type=6)
                        member_choice = response.component.label
                    except asyncio.TimeoutError:
                        await m.edit(f"I guess {member.nick or member.name} is not interested to play with {ctx.author.nick or ctx.author.name}",
                                     components=[])
                else:
                    member_choice = response.component.label
                    await m.edit(f"{ctx.author.nick or ctx.author.name} is thinking...\n{member.nick or member.name} made a choice.")
                    try:
                        def check(res):
                            return res.user == ctx.author and res.message.id == m.id
                        response = await self.bot.wait_for('button_click', timeout=30, check=check)
                        await response.respond(type=6)
                        author_choice = response.component.label
                    except asyncio.TimeoutError:
                        await m.edit(f"I guess {ctx.author.nick or ctx.author.name} is not interested to play with {member.nick or member.name}",
                                     components=[])
                
                if author_choice == member_choice:
                    await m.edit(f"{ctx.author.nick or ctx.author.name} and {member.nick or member.name} both chose {author_choice} :{author_choice.lower().replace('paper', 'roll_of_paper')}: tie!!",
                                 components=[])
                elif author_choice == "Rock":
                    if member_choice == "Paper":
                        await m.edit(f"{member.nick or member.name} won! {bet} <a:pinkcoin:920347688791310366>, {member_choice}, covers {author_choice}",
                                     components=[])
                        database.add_money(member.id, ctx.guild.id, bet, 0)
                        database.remove_money(ctx.author.id, ctx.guild.id, bet, 0)                
                    else:
                        await m.edit(f"{ctx.author.nick or ctx.author.name} won! {bet} <a:pinkcoin:920347688791310366>, {author_choice}, smashes {member_choice}",
                                     components=[])
                        database.add_money(ctx.author.id, ctx.guild.id, bet, 0)
                        database.remove_money(member.id, ctx.guild.id, bet, 0)
                elif author_choice == "Paper":
                    if member_choice == "Scissors":
                        await m.edit(f"{member.nick or member.name} won! {bet} <a:pinkcoin:920347688791310366>, {member_choice}, cuts {author_choice}",
                                     components=[])
                        database.add_money(member.id, ctx.guild.id, bet, 0)
                        database.remove_money(ctx.author.id, ctx.guild.id, bet, 0)
                    else:
                        await m.edit(f"{ctx.author.nick or ctx.author.name} won! {bet} <a:pinkcoin:920347688791310366>, {author_choice}, covers {member_choice}",
                                     components=[])
                        database.add_money(ctx.author.id, ctx.guild.id, bet, 0)
                        database.remove_money(member.id, ctx.guild.id, bet, 0)
                elif author_choice == "Scissors":
                    if member_choice == "Rock":
                        await m.edit(f"{member.nick or member.name} won! {bet} <a:pinkcoin:920347688791310366>, {member_choice}, smashes {author_choice}",
                                     components=[])
                        database.add_money(member.id, ctx.guild.id, bet, 0)
                        database.remove_money(ctx.author.id, ctx.guild.id, bet, 0)
                    else:
                        await m.edit(f"{ctx.author.nick or ctx.author.name} won! {bet} <a:pinkcoin:920347688791310366>, {author_choice}, cuts {member_choice}",
                                     components=[])
                        database.add_money(ctx.author.id, ctx.guild.id, bet, 0)
                        database.remove_money(member.id, ctx.guild.id, bet, 0)                              
            except asyncio.TimeoutError:
                await m.edit(f"I guess {ctx.author.nick or ctx.author.name} and {member.nick or member.name} don't wanna play!!",
                             components=[])

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                  ERRORS                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @coinflip.error
    async def on_coinflip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`t.coinflip <head|tail> <bet amount>`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Coinflip Cooldown is 30 minutes",
                                  description="{} you need to wait {:,.1f} minutes to flip coin again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @rockpaper.error
    async def on_rps_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`t.rps @mention <bet amount>`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="rps Cooldown is 4 hours",
                                  description="{} you need to wait {:,.1f} minutes to flip coin again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Gambling(bot))
