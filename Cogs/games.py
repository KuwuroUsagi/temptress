#!/bin/python3
import discord
import database
import asyncio
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
                embed = discord.Embed(description=f"{message.author.mention} you guessed the correct number and you earned 20 <a:pinkcoin:900000697288892416>", color=0xF2A2C0)
                await message.reply(embed=embed)
                database.add_money(message.author.id, 20, 0)
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


def setup(bot):
    bot.add_cog(Games(bot))
