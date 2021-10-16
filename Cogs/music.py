#!/bin/python3
import database
import discord
import asyncio
import re
from youtube_dl import YoutubeDL
from random import choice
from discord.ext import commands, tasks
from discord_components import *


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(bot)
        self.is_playing = False
        self.music_queue = {}
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.empty_voice_channel_cleanup.start()

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
        return {'id': v_id, 'title': title, 'thumbnail': thumbnail, 'url': url, 'audio_url': audio_url}

    def add_music_to_queue(self, ctx, data):
        try:
            temp = self.music_queue[f'{ctx.guild.id}']
            temp.append(data)
            self.music_queue[f'{ctx.guild.id}'] = temp
        except KeyError:
            self.music_queue[f'{ctx.guild.id}'] = [data]

    def play_next(self, ctx, voice_client, loop=False, shuffle=False):
        temp = self.music_queue[f'{ctx.guild.id}']
        data = temp.pop(0)
        self.music_queue[f'{ctx.guild.id}'] = temp
        voice_client.play(discord.FFmpegPCMAudio(data['audio_url'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx, voice_client, loop=loop, shuffle=shuffle))

    async def play_music(self, ctx, voice_client, loop=False, shuffle=False):
        temp = self.music_queue[f'{ctx.guild.id}']
        data = temp.pop(0)
        self.music_queue[f'{ctx.guild.id}'] = temp
        try:
            voice_client.play(discord.FFmpegPCMAudio(data['audio_url'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx, voice_client, loop=loop, shuffle=shuffle))
        except discord.errors.ClientException:
            await voice_client.move_to(voice_channel)

    @tasks.loop(seconds=60)
    async def empty_voice_channel_cleanup(self):
        guilds = self.bot.guilds
        for guild in guilds:
            voice_client = guild.voice_client
            if voice_client is not None and len(voice_client.channel.members) == 1:
                if voice_client.is_playing():
                    voice_client.stop()
                await voice_client.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            if after.channel is None:
                try:
                    del self.music_queue[f'{member.guild.id}']
                except KeyError:
                    pass

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, *, url=None):

        if ctx.author.voice is None:
            await ctx.reply("<:staff:897777248839540757> Connect to a Voice Channel, and Try Again")
        else:
            voice_client = ctx.guild.voice_client
            if voice_client is not None:
                if voice_client.is_playing() and voice_client.channel != ctx.author.voice.channel:
                    await ctx.send(f'<:staff:897777248839540757>I am alredy playing music in {voice_client.channel.mention}')
                    return
                elif voice_client.channel != ctx.author.voice.channel:
                    await voice_client.move_to(ctx.author.voice.channel)

            if url is None:
                voice_channel = ctx.author.voice.channel
                try:
                    voice_client = await voice_channel.connect()
                except asyncio.TimeoutError:
                    await ctx.reply('I am sorry, can you try again, I just forgot what you said, bitflips are real.')
                except discord.errors.ClientException:  # You are already connected to a voice channel.
                    pass
                if not voice_client.is_playing():
                    try:
                        data = self.music_queue[f"{ctx.guild.id}"][0]
                    except (IndexError, KeyError):
                        await ctx.reply(f"No more tracks in the Queue.")
                        await ctx.message.add_reaction(emoji='NO:897890789202493460')
                        return
                    await self.play_music(ctx, voice_client)
                    embed = discord.Embed(title=f"Now Playing...", description=f"**{data['title']}**\n> {data['url']}", color=0xF2A2C0)
                    embed.set_thumbnail(url=data['thumbnail'])
                    await ctx.send(embed=embed)
                    await asyncio.sleep(5)
                    if not voice_client.is_playing():
                        await ctx.reply("Try again, I got some internal issue")
                        await voice_client.disconnect()
                    return

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
                except discord.errors.ClientException:  # You are already connected to a voice channel.
                    pass
                self.add_music_to_queue(ctx, data)
                if not voice_client.is_playing():
                    await self.play_music(ctx, voice_client)
                    embed = discord.Embed(title=f"Now Playing...", description=f"**{data['title']}**\n> {data['url']}", color=0xF2A2C0)
                    embed.set_thumbnail(url=data['thumbnail'])
                    await ctx.send(embed=embed)
                    await asyncio.sleep(5)
                    if not voice_client.is_playing():
                        await ctx.reply("Try again, I got some internal issue")
                        await voice_client.disconnect()
                else:
                    embed = discord.Embed(title=f"Added to Queue", description=f"**{data['title']}**\n> {data['url']}", color=0xF2A2C0)
                    embed.set_thumbnail(url=data['thumbnail'])
                    await ctx.send(embed=embed)

    @commands.command()
    async def leave(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is not None:
            if ctx.author.voice is not None:
                if voice_client.channel != ctx.author.voice.channel:
                    await ctx.reply(f'<:staff:897777248839540757> We are not in the same Voice Channel.')
                    return
            else:
                await ctx.reply("<:staff:897777248839540757> Connect to a Voice Channel, and Try Again")
                return

            await ctx.guild.voice_client.disconnect()
            await ctx.message.add_reaction(emoji='YES:897762486042910762')

    @commands.command()
    async def next(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is not None:
            if ctx.author.voice is not None:
                if voice_client.channel != ctx.author.voice.channel:
                    await ctx.reply(f'<:staff:897777248839540757> We are not in the same Voice Channel.')
                    return
            else:
                await ctx.reply("<:staff:897777248839540757> Connect to a Voice Channel, and Try Again")
                return

            if voice_client.is_playing():
                voice_client.stop()
                try:
                    data = self.music_queue[f"{ctx.guild.id}"][0]
                except IndexError:
                    await ctx.reply(f"No more tracks in the Queue.")
                    await ctx.message.add_reaction(emoji='NO:897890789202493460')
                    return
                embed = discord.Embed(title=f"Now Playing...", description=f"**{data['title']}**\n> {data['url']}", color=0xF2A2C0)
                embed.set_thumbnail(url=data['thumbnail'])
                await ctx.send(embed=embed)
                self.play_next(ctx, voice_client)
                await asyncio.sleep(5)
                if not voice_client.is_playing():
                    await ctx.reply("Try again, I got some internal issue")

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is not None:
            if ctx.author.voice is not None:
                if voice_client.channel != ctx.author.voice.channel:
                    await ctx.reply(f'<:staff:897777248839540757> We are not in the same Voice Channel.')
                    return
            else:
                await ctx.reply("<:staff:897777248839540757> Connect to a Voice Channel, and Try Again")
                return

            if voice_client.is_playing():
                voice_client.stop()
                await ctx.message.add_reaction(emoji='YES:897762486042910762')

    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is not None:
            if ctx.author.voice is not None:
                if voice_client.channel != ctx.author.voice.channel:
                    await ctx.reply(f'<:staff:897777248839540757> We are not in the same Voice Channel.')
                    return
            else:
                await ctx.reply("<:staff:897777248839540757> Connect to a Voice Channel, and Try Again")
                return

            if voice_client.is_playing():
                voice_client.pause()
                await ctx.message.add_reaction(emoji='YES:897762486042910762')

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client is not None:
            if ctx.author.voice is not None:
                if voice_client.channel != ctx.author.voice.channel:
                    await ctx.reply(f'<:staff:897777248839540757> We are not in the same Voice Channel.')
                    return
            else:
                await ctx.reply("<:staff:897777248839540757> Connect to a Voice Channel, and Try Again")
                return

            if not voice_client.is_playing():
                voice_client.resume()

    @commands.command()
    async def q(self, ctx):
        print(self.music_queue)


def setup(bot):
    bot.add_cog(Music(bot))
