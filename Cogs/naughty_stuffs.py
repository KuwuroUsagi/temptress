#!/bin/python3
from discord.ext import commands
from pornhub_api import PornhubApi
from random import randint, choice
import discord
import database

api = PornhubApi()


async def getporn(ctx):
    await ctx.send(f'{ctx.message.author.mention} ||check your DMs|| :shushing_face: Shhh...')
    while True:
        try:
            page_no = randint(1, 100)
            porn_no = randint(1, 30)
            data = api.search.search(page=page_no, tags=["femdom", "pet play", "pegging"])
            video = data.videos[porn_no]
            video_url = video.url
            video_title = video.title
            video_thumbnail = video.default_thumb
            break
        except Exception:
            pass

    star_list = []
    cat_list = []
    tag_list = []
    for star in video.pornstars:
        star_list.append(star.pornstar_name)
    stars = ", ".join(star_list)

    for c in video.categories:
        cat_list.append(c.category)
    cats = ", ".join(cat_list)

    for t in video.tags:
        tag_list.append(t.tag_name)
    tags = ", ".join(tag_list)

    porn_embed = discord.Embed(title=f'{video_title} :peach: ', description=f'{stars} \n\n {cats} \n\n {tags}',
                               color=0xF2A2C0, url=video_url)
    porn_embed.set_thumbnail(url=video_thumbnail)
    await ctx.message.author.send(embed=porn_embed)


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

    @commands.command(aliases=['pornv'])
    @commands.guild_only()
    async def pornvideo(self, ctx):
        if set(database.get_config('NSFW', ctx.guild.id)) & set([role.id for role in ctx.author.roles]) or database.get_config('NSFW', ctx.guild.id) == [0]:
            await getporn(ctx)
        else:
            roles = '>'
            for r in database.get_config('NSFW', ctx.guild.id):
                roles = f"{roles} <@&{r}>\n>"
            embed = discord.Embed(description=f"{ctx.author.mention} you are not eligible for NSFW content. \nGet any of the folloing role and try again.\n{roles}", color=0xF2A2C0)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def porn(self, ctx):
        if set(database.get_config('NSFW', ctx.guild.id)) & set([role.id for role in ctx.author.roles]) or database.get_config('NSFW', ctx.guild.id) == [0]:
            await getporn_image(ctx, 'Text_files/porn_image_list.txt')
        else:
            roles = '>'
            for r in database.get_config('NSFW', ctx.guild.id):
                roles = f"{roles} <@&{r}>\n>"
            embed = discord.Embed(description=f"{ctx.author.mention} you are not eligible for NSFW content. \nGet any of the folloing role and try again.\n{roles}", color=0xF2A2C0)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(description=f"{ctx.author.mention} you should be using this command in server.", color=0xF2A2C0)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Porn(bot))
