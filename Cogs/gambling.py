#!/bin/python3
import asyncio
import random
import sqlite3

import database
import discord
from discord import ButtonStyle
from discord.ext import commands

con = sqlite3.connect(':memory:')
cur = con.cursor()


class RpsView(discord.ui.View):
  def __init__(self, member, ctx, bet):
    self.member = member
    self.ctx = ctx
    self.bet = bet

    self.author_choice = None
    self.member_choice = None

    super().__init__(timeout=90)

  async def update_game(self, it: discord.Interaction):
    mem_state = 'is thinking...' if not self.member_choice else 'made a choice.'
    author_state = 'is thinking...' if not self.author_choice else 'made a choice.'

    aut = f'**{self.ctx.author.display_name}**'
    mem = f'**{self.member.display_name}**'

    await it.message.edit(embed=discord.Embed(title='Rock Paper Scissors 🪨🧻✂️', description=f"{aut if self.author_choice else self.ctx.author.display_name} {author_state}\n{mem if self.member_choice else self.member.display_name} {mem_state}", color=discord.Color.pink()), view=self)

    if not (self.member_choice and self.author_choice):
      return await it.response.defer()

    em_map = {'rock': '🗿', 'paper': '🧻', 'scissors': '✂️'}
    mod_map = {'rock': 1, 'paper': 2, 'scissors': 3}

    if self.member_choice == self.author_choice:
      m = f"💥 {aut} and {mem} both chose {self.author_choice}. **It's a TIE** {em_map[self.author_choice] * 3} 💥"

    elif (mod_map[self.member_choice] + 1) % 3 == mod_map[self.author_choice] % 3:
      m = f"{aut} won! **{self.bet}** <a:pinkcoin:1167061163515858954>\n{self.author_choice}, *smashes* {self.member_choice} 🍃🍃 {em_map[self.author_choice]} >>> {em_map[self.member_choice]}"
      database.add_money(self.ctx.author.id, self.ctx.guild.id, self.bet, 0)
      database.remove_money(self.member.id, self.ctx.guild.id, self.bet, 0)
    else:
      m = f"{mem} won! **{self.bet}** <a:pinkcoin:1167061163515858954>\n{self.member_choice}, *smashes* {self.author_choice} 🍃🍃 {em_map[self.member_choice]} >>> {em_map[self.author_choice]}"
      database.add_money(self.member.id, self.ctx.guild.id, self.bet, 0)
      database.remove_money(self.ctx.author.id, self.ctx.guild.id, self.bet, 0)

    await it.message.edit(embed=discord.Embed(title='Rock Paper Scissors 🪨🧻✂️', description=m, color=discord.Color.gold()), view=None)

  @discord.ui.button(style=ButtonStyle.blurple, label="Rock", emoji='🗿')
  async def rock(self, it: discord.Interaction, btn: discord.ui.Button):
    if it.user.id == self.ctx.author.id:
      self.author_choice = 'rock'
    else:
      self.member_choice = 'rock'
    await self.update_game(it)

  @discord.ui.button(style=ButtonStyle.blurple, label='Paper', emoji='🧻')
  async def paper(self, it: discord.Interaction, btn: discord.ui.Button):
    if it.user.id == self.ctx.author.id:
      self.author_choice = 'paper'
    else:
      self.member_choice = 'paper'
    await self.update_game(it)

  @discord.ui.button(style=ButtonStyle.blurple, label='Scissors', emoji='✂️', )
  async def scissors(self, it: discord.Interaction, btn: discord.ui.Button):
    if it.user.id == self.ctx.author.id:
      self.author_choice = 'scissors'
    else:
      self.member_choice = 'scissors'
    await self.update_game(it)

  async def interaction_check(self, interaction: discord.Interaction):
    if interaction.user.id != self.member.id and interaction.user.id != self.ctx.author.id:
      return False

    if interaction.user.id == self.member.id and self.member_choice or interaction.user.id == self.ctx.author.id and self.author_choice:
      await interaction.response.send_message('You already made a choice.', ephemeral=True)
      return False

    return True


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

  @commands.hybrid_command(aliases=['cf'])
  @commands.guild_only()
  @commands.cooldown(3, 1 * 60, commands.BucketType.user)
  async def coinflip(self, ctx, choice: str, bet: int):
    """gamble and earn coins by flipping coins"""
    if ctx.author.bot:
      return
    ban_data = database.is_botban(ctx.author.id)
    if ban_data is None:
      if bet < 10:
        await ctx.reply(f"🧏‍♀️ You need to bet at least 10 <a:pinkcoin:1167061163515858954>")
      elif choice.lower() not in ['head', 'tail', 'h', 't', 'heads', 'tails']:
        await ctx.reply(f"🧏‍♀️ usage: **`/coinflip <head|tail> <bet>`**")
      else:
        coins = database.get_money(ctx.author.id, ctx.guild.id)[2]
        if bet > coins:
          await ctx.reply(
            f"🧏‍♀️ really?, you are broke you only have {coins} <a:pinkcoin:1167061163515858954>")
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

  @commands.hybrid_command(aliases=['rockpaper'])
  @commands.guild_only()
  # @commands.cooldown(5, 1 * 60 * 60, commands.BucketType.user)
  async def rps(self, ctx, member: discord.Member, bet: int):
    """play rock paper scissors and steal coins from them."""
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
      embed = discord.Embed(
        description=f"🧏‍♀️ You need to bet at least 10 <a:pinkcoin:1167061163515858954>",
        color=0xF2A2C0)
      await ctx.send(embed=embed)
    elif bet > author_coin:
      embed = discord.Embed(
        description=f"{ctx.author.mention} really?, 🧏‍♀️ You only have {author_coin} <a:pinkcoin:1167061163515858954>",
        color=0xF2A2C0)
      await ctx.send(embed=embed)
    elif bet > member_coin:
      embed = discord.Embed(
        description=f"🧏‍♀️, {member.mention} only have {member_coin} <a:pinkcoin:1167061163515858954>",
        color=0xF2A2C0)
      await ctx.send(embed=embed)
    else:
      await ctx.send(
        embed=discord.Embed(title='RPS 🪨🧻✂️',
                            description=f"{ctx.author.display_name} is thinking...\n{member.display_name} is thinking...",
                            color=discord.Color.blurple()),
        view=RpsView(member, ctx, bet))

  ##############################################################################
  #                                                                            #
  #                                                                            #
  #                                  ERRORS                                    #
  #                                                                            #
  #                                                                            #
  ##############################################################################

  @coinflip.error
  async def on_coinflip_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(description=f"Usage:\n**`/coinflip <head|tail> <bet amount>`**",
                            color=0xFF2030)
      await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.CommandOnCooldown):
      embed = discord.Embed(title="Coinflip Cooldown is 30 minutes",
                            description="{} you need to wait {:,.1f} minutes to flip coin again.".format(
                              ctx.author.mention, (error.retry_after // 60) + 1),
                            color=0xFF2030)
      await ctx.send(embed=embed)

  @rps.error
  async def on_rps_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(description=f"Usage:\n**`/rps @mention <bet amount>`**",
                            color=0xFF2030)
      await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.CommandOnCooldown):
      embed = discord.Embed(title="rps Cooldown is 4 hours",
                            description="{} you need to wait {:,.1f} minutes to flip coin again.".format(
                              ctx.author.mention, (error.retry_after // 60) + 1),
                            color=0xFF2030)
      await ctx.send(embed=embed)


async def setup(bot):
  await bot.add_cog(Gambling(bot))
