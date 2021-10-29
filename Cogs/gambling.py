#!/bin/python3
import discord
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

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                 GAMMBLE                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @commands.command(aliases=['cf'])
    @commands.guild_only()
    # @commands.cooldown(50, 30 * 60, commands.BucketType.user)
    async def coinflip(self, ctx, choice: str, bet: int):
        if bet < 10:
            await ctx.reply(f"<:staff:897777248839540757> You need to bet at least 10 <a:pinkcoin:900000697288892416>")
        elif choice.lower() not in ['head', 'tail', 'h', 't', 'heads', 'tails']:
            await ctx.reply(f"<:staff:897777248839540757> usage: **`s.coinflip <head|tail> <bet>`**")
        else:
            coins = database.get_money(ctx.author.id, ctx.guild.id)[2]
            if bet > coins:
                await ctx.reply(f"<:staff:897777248839540757> really?, you are broke you only have {coins} <a:pinkcoin:900000697288892416>")
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

    @commands.command(aliases=['roulette'])
    @commands.guild_only()
    @commands.cooldown(4, 30 * 60, commands.BucketType.user)
    async def roulete(self, ctx, bet: int, space: str):
        if ctx.author.bot:
            return

        def is_win(out_come, bet, space):
            red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
            st = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
            nd = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
            rd = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
            try:
                if space.lower() == 'red' and out_come in red:
                    return bet * 2
                elif space.lower() == 'black' and out_come in black:
                    return bet * 3
                elif space.lower() == '1st' and out_come in st:
                    return bet * 3
                elif space.lower() == '2nd' and out_come in nd:
                    return bet * 3
                elif space.lower() == '3rd' and out_come in rd:
                    return bet * 3
                elif space.lower() == 'odd' and out_come % 2 != 0:
                    return bet * 2
                elif space.lower() == 'even' and out_come % 2 == 0:
                    return bet * 2
                elif space.lower() == '1-12' and 1 <= out_come <= 12:
                    return bet * 3
                elif space.lower() == '13-24' and 13 <= out_come <= 24:
                    return bet * 3
                elif space.lower() == '25-36' and 25 <= out_come <= 36:
                    return bet * 3
                elif space.lower() == '1-18' and 1 <= out_come <= 18:
                    return bet * 2
                elif space.lower() == '19-36' and 19 <= out_come <= 36:
                    return bet * 2
                elif int(space) == out_come:
                    return bet * 36
                else:
                    return 0
            except ValueError:
                return 0

        input_list = ['red', 'black',
                      'odd', 'even',
                      '1-12', '13-24', '25-36',
                      '1st', '2nd', '3rd',
                      '1-18', '19-36',
                      '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                      '13', '14', '15', '16', '17', '18', '0', '19', '20', '21',
                      '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',
                      '32', '33', '34', '35', '36']
        coin = database.get_money(ctx.author.id, ctx.guild.id)[2]
        if bet < 10:
            embed = discord.Embed(description=f"{ctx.author.mention} minimum bet amount should be 10 <a:pinkcoin:900000697288892416>",
                                  color=0xFF2039)
        elif bet > coin:
            embed = discord.Embed(description=f"{ctx.author.mention} you only have {coin} <a:pinkcoin:900000697288892416>",
                                  color=0xFF2030)
        elif space.lower() not in input_list:
            embed = discord.Embed(
                description=f"{ctx.author.mention} you entered wrong bet space.\nUsage:\n**`h&roulete <bet amount> "
                            f"<space>`**\n> [x36] Single Number\n> [x 3] Dozens (1-12, 13-24, 25-36)\n> [x 3] Columns "
                            f"(1st, 2nd, 3rd)\n> [x 2] Halves (1-18, 19-36)\n> [x 2] Odd/Even\n> [x 2] Colours (red, "
                            f"black)",
                color=0xFF2030)
        else:
            database.remove_money(ctx.author.id, ctx.guild.id, bet, 0)
            out_come = random.randint(0, 36)
            roulete_color = ''
            if out_come in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
                roulete_color = 'RED'
            elif out_come in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]:
                roulete_color = 'BLACK'
            else:
                pass
            cur.execute("""SELECT name FROM sqlite_master WHERE type='table'""")  # , [str(ctx.author.name.replace(' ', '_'))])
            if (ctx.author.name.replace(' ', '_'),) in cur.fetchall():
                with con:
                    cur.execute(f"INSERT INTO {ctx.author.name.replace(' ', '_')} VALUES (?, ?)", [bet, space])
                    embed = discord.Embed(description=f"{ctx.author.mention} placed a bet of {bet} <a:pinkcoin:900000697288892416> on {space}", color=0x9479ED)
                    embed.set_footer(text='anytime now just wait!!')
                    await ctx.send(embed=embed)
                return
            else:
                with con:
                    cur.execute(f"CREATE TABLE IF NOT EXISTS {ctx.author.name.replace(' ', '_')} (bet integer, space text)")
                    cur.execute(f"INSERT INTO {ctx.author.name.replace(' ', '_')} VALUES (?, ?)", [bet, space])
                    embed = discord.Embed(description=f"{ctx.author.mention} placed a bet of {bet} <a:pinkcoin:900000697288892416> on {space}", color=0x9479ED)
                    embed.set_footer(text='30 seconds remaining!!')
                    await ctx.send(embed=embed)
            await asyncio.sleep(30)
            cur.execute(f"SELECT * FROM {ctx.author.name.replace(' ', '_')}")
            bets = cur.fetchall()
            win_amount = 0
            for bet_ in bets:
                win_amount = is_win(out_come, bet_[0], bet_[1]) + win_amount
            if win_amount != 0:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} you won the bet **{win_amount}** <a:pinkcoin:900000697288892416>\n> ball landed on **{out_come} {roulete_color}**",
                    color=0x08FF08)
                database.add_money(ctx.author.id, ctx.guild.id, win_amount, 0)
            else:
                embed = discord.Embed(description=f"{ctx.author.mention} you lost the bet\n> ball landed on **{out_come} {roulete_color}**",
                                      color=0xFF2030)
        await ctx.send(embed=embed)
        try:
            with con:
                cur.execute(f"DROP TABLE {ctx.author.name.replace(' ', '_')}")
        except sqlite3.OperationalError:
            pass

    @commands.command(aliases=['sr'])
    @commands.guild_only()
    @commands.cooldown(5, 1 * 60 * 60, commands.BucketType.user)
    async def subrace(self, ctx, domme: discord.Member, bet: int):
        pass

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
            embed = discord.Embed(description=f"Usage:\n**`s.coinflip <head|tail> <bet>`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Coinflip Cooldown is 30 minutes",
                                  description="{} you need to wait {:,.1f} minutes to flip coin again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @subrace.error
    async def on_subrace_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.subrace @domme <bet amount>`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Subrace Cooldown is 4 hours",
                                  description="{} you need to wait {:,.1f} minutes to flip coin again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @roulete.error
    async def on_roulete_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Cooldown",
                                  description="{} you need to wait {:,.1f} minutes to play roulete again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description=f"Usage:\n**`h&roulete <bet amount> <space>`**",
                                  color=0xFF2030)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Gambling(bot))
