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
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx):
        # item = 'AMONG US Theme Song (Moondai EDM Remix)'
        # with YoutubeDL(self.YDL_OPTIONS) as ydl:
        #     info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()
        # print(info['formats'][0]['url'])
        voice_client.play(discord.FFmpegPCMAudio('https://r1---sn-3jja-jv3l.googlevideo.com/videoplayback?expire=1634241299&ei=szZoYYWfH9-ag8UP-qC5gAU&ip=103.161.55.149&id=o-AOsq4n3zO3z6q02LLQAkWXh4zZUYUkgwY4M66FzYqOQp&itag=249&source=youtube&requiressl=yes&mh=Hs&mm=31%2C29&mn=sn-3jja-jv3l%2Csn-h5576nlk&ms=au%2Crdu&mv=m&mvi=1&pl=24&initcwndbps=838750&vprv=1&mime=audio%2Fwebm&ns=7LGQJKB7ZH6ndidvN43zV5wG&gir=yes&clen=791553&dur=129.161&lmt=1605975840988242&mt=1634219358&fvip=5&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=5431432&n=j7Y7sun66KQJPr&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRQIhAJHtWe-k5es-J1Asc11Younex34jJOmgEpGV1J_4QLOGAiAjrmQ2AO4FTpxKd14eW8PgZ9CSyVrK7Kee0zDW6-B7dw%3D%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIhALSumdHzrqY6E2PSc8eKH3G8BTxdKu7fA3b3n_yEHwFQAiAsFuE_tm5DBFcAb3iSOa1p3TNINFamhxCeIWhIQBkqGw%3D%3D', **self.FFMPEG_OPTIONS))


def setup(bot):
    bot.add_cog(Music(bot))
