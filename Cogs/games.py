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
            return

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
                await message.delete()
                return

        number = int(data[0])
        if number < 0:
            if (-1 * number) == count:
                embed = discord.Embed(description=f"{message.author.mention} you guessed the correct number and you earned 30 <a:pinkcoin:900000697288892416>", color=0xF2A2C0)
                await message.reply(embed=embed)
                database.add_money(message.author.id, 30, 0)
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
                database.add_money(message.author.id, 1, 0)
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
            database.add_money(ctx.author.id, int(data[4]), 0)
            data_ = f"{-1 * random.randint(70, 10000)}_{ctx.channel.id}_0_0_0"
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

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                  ERRORS                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandInvokeError):
            if isinstance(error.original, discord.errors.Forbidden):
                embed = discord.Embed(title='I don\'t feel so Good.', description=f"I am restrained help, Please make sure that I have **Administration Permissions** and **Elevate my Role**, then try again.", color=0xFF2030)
                await ctx.author.send(embed=embed)
                await ctx.send(embed=embed)

        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(description=f"{ctx.author.mention} you should be using this command in server.", color=0xF2A2C0)
            await ctx.send(embed=embed)

        if isinstance(error, commands.errors.MissingPermissions):
            embed = discord.Embed(title='I see a Fake administrator', description=f"{ctx.author.mention} you don't have **Administration Permissions** in the server.", color=0xF2A2C0)
            await ctx.send(embed=embed)

    @ruin.error
    async def on_ruin_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Ruin Cooldown is 1h",
                                  description="{} you need to wait {:,.1f} minutes to ruin the game again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
