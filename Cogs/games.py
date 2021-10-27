#!/bin/python3
import discord
import database
import asyncio
import random
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            if message.author.id != 302050872383242240:  # user ID of Disboard bot
                return
            else:
                for embed in message.embeds:
                    try:
                        if "https://disboard.org/images/bot-command-image-bump.png" == embed.to_dict()['image']['url']:
                            user_id = int(embed.to_dict()['description'][2:20].replace('>', ''))
                            database.add_money(user_id, message.guild.id, 30, 0)
                            embed = discord.Embed(description=f"<@{user_id}> received 30 <a:pinkcoin:900000697288892416> for Bumping the server.", color=0xF2A2C0)
                            await message.channel.send(embed=embed)
                            return
                    except Exception:
                        return

        if random.random() < 0.1:
            database.add_money(message.author.id, message.guild.id, 1, 0)

        try:
            data = database.get_config_raw('counting', message.guild.id).split('_')  # [number, channel, member, message, count_length]
        except AttributeError:
            return
        if message.channel.id != int(data[1]):
            return

        try:
            count = int(message.content)
        except ValueError:
            if message.content.lower() == 's.ruin':  # string is passed
                return
            else:
                # await message.delete()
                return

        number = int(data[0])
        if number < 0:
            if (-1 * number) == count:
                embed = discord.Embed(description=f"{message.author.mention} you guessed the correct number and you earned 30 <a:pinkcoin:900000697288892416>", color=0xF2A2C0)
                await message.reply(embed=embed)
                database.add_money(message.author.id, message.guild.id, 30, 0)
                data[0] = str(-1 * number + 1)
                data[2] = str(message.author.id)
                data[3] = str(message.id)
                data[4] = '1'
                database.insert_config('counting', message.guild.id, '_'.join(data))
                await message.add_reaction(emoji='pinkcoin:900000697288892416')
            else:
                if count > number * -1:
                    hint = f"Next number is {len(str(number * -1))} digit number and less than {count}"
                else:
                    hint = f"Next number is {len(str(number * -1))} digit number and greater than {count}"
                embed = discord.Embed(title='Hint', description=hint, color=0xF2A2C0)
                await message.channel.send(embed=embed)

        else:
            if message.author.id == int(data[2]):
                await message.delete()
                m = await message.channel.send(f"{message.author.mention} you can't continues wait for someone else.")
                await asyncio.sleep(5)
                await m.delete()
            elif count == number:
                database.add_money(message.author.id, message.guild.id, 1, 0)
                data[0] = str(number + 1)
                data[2] = str(message.author.id)
                data[3] = str(message.id)
                data[4] = str(int(data[4]) + 1)
                database.insert_config('counting', message.guild.id, '_'.join(data))
                await message.add_reaction(emoji='pinkcoin:900000697288892416')
            else:
                await message.delete()

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setcount(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        data = f"70_{channel.id}_0_0_0"
        database.insert_config('counting', ctx.guild.id, data)
        await channel.send('I will start with my fav number.')
        m = await channel.send('69')
        await m.add_reaction(emoji='pinkcoin:900000697288892416')
        embed = discord.Embed(title='Counting',
                              description=f"{channel.mention} is the counting channel.\n**How to earn more pinkcoins <a:pinkcoin:900000697288892416>**"
                              f"\n> Counting earns pinkcoins <a:pinkcoin:900000697288892416>\n> Dommes can ruin by **`s.ruin`** the game and earn pinkcoins <a:pinkcoin:900000697288892416>"
                              f"\n> Guessing the correct number after ruing also gives pinkcoins <a:pinkcoin:900000697288892416>", color=0xF2A2C0)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1 * 60 * 60, commands.BucketType.user)
    async def ruin(self, ctx):
        try:
            data = database.get_config_raw('counting', ctx.guild.id).split('_')  # [number, channel, member, message, count_length]
        except AttributeError:
            embed = discord.Embed(description=f"Counting channel is not configured yet, ask Admins to run **`s.setcount #countChannel`**", color=0xF2A2C0)
            await ctx.reply(embed=embed)
            return
        if ctx.channel.id != int(data[1]):
            await ctx.reply(f"You should use this command in <#{data[1]}>")
        elif set(database.get_config('domme', ctx.guild.id)) & set([role.id for role in ctx.author.roles]):
            database.add_money(ctx.author.id, ctx.guild.id, int(data[4]), 0)
            data_ = f"{-1 * random.randint(70, 1000)}_{ctx.channel.id}_0_0_0"
            database.insert_config('counting', ctx.guild.id, data_)
            embed = discord.Embed(description=f"{ctx.author.mention} ruined the counting and earned {data[4]} <a:pinkcoin:900000697288892416>"
                                  f"\n\n\n> **Now guess the next number to earn more**", color=0xF2A2C0)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            roles = '>'
            for r in database.get_config('domme', ctx.guild.id):
                roles = f"{roles} <@&{r}>\n>"
            embed = discord.Embed(description=f"you don't have any of the following roles to ruin the game.\n{roles[:-2]}", color=0xF2A2C0)
            await ctx.send(embed=embed)

    @commands.command(aliases=['praise', 'simp', 'footkiss', 'feetkiss'])
    @commands.guild_only()
    async def worship(self, ctx, member: discord.Member):
        if set(database.get_config('domme', ctx.guild.id)) & set([role.id for role in member.roles]):
            if ctx.channel.is_nsfw():
                money = database.get_money(ctx.author.id, ctx.guild.id)[2]
                if money >= 100:
                    database.remove_money(ctx.author.id, ctx.guild.id, 100, 0)
                    database.add_money(ctx.author.id, ctx.guild.id, 0, 1)
                    database.add_money(member.id, ctx.guild.id, 0, 1)
                    database.simp(ctx.author.id, ctx.guild.id, member.id)
                    simp_embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} Simps for {member.nick or member.name}",
                                               description=f"",
                                               color=0xF2A2C0)
                    with open('Text_files/simp_image.txt', 'r') as f:
                        lines = f.read().splitlines()
                        link = random.choice(lines)
                    simp_embed.set_image(url=link)
                    await ctx.send(embed=simp_embed)
                else:
                    embed = discord.Embed(description=f"{ctx.author.mention} you need at least 100 <a:pinkcoin:900000697288892416> to simp for {member.mention}", color=0xF2A2C0)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f'{ctx.author.mention} This is not a NSFW Channel try again in NSFW channel.', color=0xF2A2C0)
                await ctx.reply(embed=embed)
        else:
            roles = '>'
            for r in database.get_config('domme', ctx.guild.id):
                roles = f"{roles} <@&{r}>\n>"
            embed = discord.Embed(description=f"You can only simp/worship members with following roles.\n{roles[:-2]}", color=0xF2A2C0)
            await ctx.send(embed=embed)

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                 GAMMBLE                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @commands.command(aliases=['cf'])
    @commands.guild_only()
    # @commands.cooldown(50, 30 * 60, commands.BucketType.user)s.status
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
            if random.random() > 0.5:

                if choice in ['head', 'heads', 'h']:
                    database.add_money(ctx.author.id, ctx.guild.id, 2 * bet, 0)
                    embed = discord.Embed(title='its heads!!', description=f"{ctx.author.mention} won {bet}", color=0x08FF08)
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed(title='its heads!!', description=f"{ctx.author.mention} lost {bet}", color=0xFF2030)
                    await ctx.reply(embed=embed)

            else:
                if choice in ['tail', 'tails', 't']:
                    database.add_money(ctx.author.id, ctx.guild.id, 2 * bet, 0)
                    embed = discord.Embed(title='its tails!!', description=f"{ctx.author.mention} won {bet}", color=0x08FF08)
                else:
                    embed = discord.Embed(title='its tails!!', description=f"{ctx.author.mention} lost {bet}", color=0xFF2030)
                    await ctx.reply(embed=embed)

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                  ERRORS                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @ruin.error
    async def on_ruin_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Ruin Cooldown is 1h",
                                  description="{} you need to wait {:,.1f} minutes to ruin the game again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
        await ctx.send(embed=embed)

    @worship.error
    async def on_worship_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.worship @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

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


def setup(bot):
    bot.add_cog(Games(bot))
