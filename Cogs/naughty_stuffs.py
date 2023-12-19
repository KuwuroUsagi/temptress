#!/bin/python3
import random
from random import randint, choice

import database
import discord
from discord.ext import commands
from pornhub_api import PornhubApi

api = PornhubApi()


async def getporn(ctx, tag=None):
  if ctx.channel.is_nsfw():
    if tag is None:
      tag = ["femdom", "pet play", "pegging"]
    else:
      tag = tag.split(' ')
    # await ctx.send(f'{ctx.message.author.mention} ||check your DMs|| :shushing_face: Shhh...')

    page = random.randint(1, 100)
    data = list(api.search.search_videos(page=page, tags=tag))
    vid = random.choice(data)

    video_url = vid.url
    video_title = vid.title
    video_thumbnail = vid.default_thumb

    stars = ", ".join(star.pornstar_name for star in vid.pornstars)
    cats = ", ".join(cat.category for cat in vid.categories)
    tags = ", ".join(tag.tag_name for tag in vid.tags)

    porn_embed = discord.Embed(title=f'{video_title} :peach: ', description=f'{stars} \n\n {cats} \n\n {tags}',
                               color=0xF2A2C0, url=video_url)
    porn_embed.set_thumbnail(url=video_thumbnail)
    await ctx.reply(embed=porn_embed)
  else:
    embed = discord.Embed(title='You Pervert this is not a NSFW Channel.', color=0xF2A2C0)
    await ctx.reply(embed=embed)


async def getporn_image(ctx, file):
  if ctx.channel.is_nsfw():
    with open(file, 'r') as f:
      lines = f.read().splitlines()
      porn_image_link = choice(lines)
    embed = discord.Embed(title='You asked for it', color=0xF2A2C0)
    embed.set_image(url=porn_image_link)
    await ctx.reply(embed=embed)
  else:
    embed = discord.Embed(title='You Pervert this is not a NSFW Channel.', color=0xF2A2C0)
    await ctx.reply(embed=embed)


class Porn(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command(aliases=['pornv'])
  @commands.guild_only()
  async def pornvideo(self, ctx):
    """this command will send you a femdom porn suggestion.😏🤤"""
    if set(database.get_config('NSFW', ctx.guild.id)) & set(
        [str(role.id) for role in ctx.author.roles]) or database.get_config('NSFW', ctx.guild.id) == [0]:
      print('Getting the video')
      await getporn(ctx)
    else:
      print('Not allowed')
      roles = '>'
      for r in database.get_config('NSFW', ctx.guild.id):
        roles = f"{roles} <@&{r}>\n>"
      embed = discord.Embed(
        description=f"{ctx.author.mention} you are not eligible for NSFW content. \nGet any of the following role and try again.\n{roles[:-2]}",
        color=0xF2A2C0)
      await ctx.send(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def porn(self, ctx):
    """this command will show you irl femdom Pics in server."""
    if set(database.get_config('NSFW', ctx.guild.id)) & set(
        [str(role.id) for role in ctx.author.roles]) or database.get_config('NSFW', ctx.guild.id) == [0]:
      await getporn_image(ctx, 'Text_files/porn_image_list.txt')
    else:
      roles = '>'
      for r in database.get_config('NSFW', ctx.guild.id):
        roles = f"{roles} <@&{r}>\n>"
      embed = discord.Embed(
        description=f"{ctx.author.mention} you are not eligible for NSFW content. \nGet any of the following role and try again.\n{roles[:-2]}",
        color=0xF2A2C0)
      await ctx.send(embed=embed)

  @commands.hybrid_command(aliases=['ph'])
  @commands.guild_only()
  async def pornhub(self, ctx, *, tag=None):
    """this command will show you a porn suggestion in a category.😏🤤"""
    if set(database.get_config('NSFW', ctx.guild.id)) & set(
        [str(role.id) for role in ctx.author.roles]) or database.get_config('NSFW', ctx.guild.id) == [0]:
      await getporn(ctx, tag=tag)
      # embed = discord.Embed(
      #   description=f"this command is disabled due to some unknown reason, which I don't know about GRRRR",
      #   color=0xFF2030)
      # await ctx.send(embed=embed)
    else:
      roles = '>'
      for r in database.get_config('NSFW', ctx.guild.id):
        roles = f"{roles} <@&{r}>\n>"
      embed = discord.Embed(
        description=f"{ctx.author.mention} you are not eligible for NSFW content. \nGet any of the following role and try again.\n{roles[:-2]}",
        color=0xF2A2C0)
      await ctx.send(embed=embed)


async def setup(bot):
  await bot.add_cog(Porn(bot))
