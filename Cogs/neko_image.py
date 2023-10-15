#!/bin/python3
import discord
import nekos
from discord.ext import commands


class Neko(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command()
  @commands.guild_only()
  async def hug(self, ctx, member: discord.Member):
    """hug someone"""
    if ctx.author.bot:
      return
    image_url = nekos.img('hug')
    embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} hugs {member.nick or member.name}",
                          color=0xF2A2C0)
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)
    if member.id == self.bot.user.id:
      image_url = nekos.img('hug')
      embed = discord.Embed(title=f"Temptress hugs {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
      embed.set_image(url=image_url)
      await ctx.reply(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def tickle(self, ctx, member: discord.Member):
    """tickle someone"""
    if ctx.author.bot:
      return
    image_url = nekos.img('tickle')
    embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} tickles {member.nick or member.name}",
                          color=0xF2A2C0)
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)
    if member.id == self.bot.user.id:
      image_url = nekos.img('tickle')
      embed = discord.Embed(title=f"Temptress tickles {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
      embed.set_image(url=image_url)
      await ctx.reply(embed=embed)

  # xxx: POKE is not available in nekos anymore
  # @commands.hybrid_command()
  # @commands.guild_only()
  # async def poke(self, ctx, member: discord.Member):
  #   """poke someone"""
  #   if ctx.author.bot:
  #     return
  #   image_url = nekos.img('poke')
  #   embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} pokes {member.nick or member.name}",
  #                         color=0xF2A2C0)
  #   embed.set_image(url=image_url)
  #   await ctx.send(embed=embed)
  #   if member.id == self.bot.user.id:
  #     image_url = nekos.img('poke')
  #     embed = discord.Embed(title=f"Temptress pokes {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
  #     embed.set_image(url=image_url)
  #     await ctx.reply(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def slap(self, ctx, member: discord.Member):
    """slap someone"""
    if ctx.author.bot:
      return
    image_url = nekos.img('slap')
    embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} slaps {member.nick or member.name}",
                          color=0xF2A2C0)
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)
    if member.id == self.bot.user.id:
      image_url = nekos.img('slap')
      embed = discord.Embed(title=f"Temptress slaps {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
      embed.set_image(url=image_url)
      await ctx.reply(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def pat(self, ctx, member: discord.Member):
    """pat someone"""
    if ctx.author.bot:
      return
    image_url = nekos.img('pat')
    embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} pats {member.nick or member.name}",
                          color=0xF2A2C0)
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)
    if member.id == self.bot.user.id:
      image_url = nekos.img('pat')
      embed = discord.Embed(title=f"Temptress pats {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
      embed.set_image(url=image_url)
      await ctx.reply(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def kiss(self, ctx, member: discord.Member):
    """kiss someone"""
    if ctx.author.bot:
      return
    image_url = nekos.img('kiss')
    embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} kisses {member.nick or member.name}",
                          color=0xF2A2C0)
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)
    if member.id == self.bot.user.id:
      image_url = nekos.img('kiss')
      embed = discord.Embed(title=f"Temptress kisses {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
      embed.set_image(url=image_url)
      await ctx.reply(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def spank(self, ctx, member: discord.Member):
    """spank someone"""
    if ctx.author.bot:
      return
    image_url = nekos.img('spank')
    embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} spanks {member.nick or member.name}",
                          color=0xF2A2C0)
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)
    if member.id == self.bot.user.id:
      image_url = nekos.img('spank')
      embed = discord.Embed(title=f"Temptress spanks {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
      embed.set_image(url=image_url)
      await ctx.reply(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def cuddle(self, ctx, member: discord.Member):
    """cuddle someone"""
    if ctx.author.bot:
      return
    image_url = nekos.img('cuddle')
    embed = discord.Embed(title=f"{ctx.author.nick or ctx.author.name} cuddles {member.nick or member.name}",
                          color=0xF2A2C0)
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)
    if member.id == self.bot.user.id:
      image_url = nekos.img('cuddle')
      embed = discord.Embed(title=f"Temptress cuddles {ctx.author.nick or ctx.author.name} back.", color=0xF2A2C0)
      embed.set_image(url=image_url)
      await ctx.reply(embed=embed)


async def setup(bot):
  await bot.add_cog(Neko(bot))
