#!/bin/python3
import database
import discord
import asyncio
import re
from youtube_dl import YoutubeDL
from random import choice
from discord.ext import commands
from discord_components import *


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(bot)
        self.is_playing = False
        self.music_queue = {}
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    def yt_search(self, url):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % url, download=False)['entries'][0]
                v_id = info['id']
                title = info['title']
                thumbnail = info['thumbnails'][-1]['url']
                url = f"https://www.youtube.com/watch?v={v_id}"
                audio_url = info['formats'][0]['url']
            except IndexError:
                return
        return [v_id, title, thumbnail, url, audio_url]

    # @commands.Cog.listener()
    # async def on_voice_state_update(self, member, before, after):
    #     voice_client = before.channel.guild.voice_client
    #     if member.id == self.bot.user.id:
    #         if after.channel is None:
    #             voice_client.stop()

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, *, url):
        voice_client = ctx.guild.voice_client
        if ctx.author.voice is None:
            await ctx.reply("<:staff:897777248839540757> Connect to a Voice Channel, and Try Again")
        else:
            data = self.yt_search(url)
            if data is None:
                embed = discord.Embed(description=f"Please make sure that it is a **valid YouTube URL or Search Term** \n> **Note** : YouTube playlist URLs are not supported.", color=0xF2A2C0)
                await ctx.send(embed=embed)
            else:

                voice_channel = ctx.author.voice.channel
                try:
                    voice_client = await voice_channel.connect()
                except asyncio.TimeoutError:
                    await ctx.reply('I am sorry, can you try again, I just forgot what you said, bitflips are real.')
                except discord.errors.ClientException:
                    pass
                try:
                    voice_client.play(discord.FFmpegPCMAudio(data[-1], **self.FFMPEG_OPTIONS))
                except discord.errors.ClientException:
                    await voice_client.move_to(voice_channel)

    @commands.command()
    async def pp(self, ctx):
        await ctx.guild.voice_client.disconnect()


def setup(bot):
    bot.add_cog(Music(bot))
