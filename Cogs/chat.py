#!/bin/python3
"""
by using API from personalityforge bot can talk like it does, for documentation visit https://www.personalityforge.com/chatbot-api-docs.php
"""
import discord
import requests
import database
from os import environ
from random import choice
from discord.ext import commands


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botID = 159644  # NSFW Annabelle Lee = 106996, Laurel Sweet = 71367 Lil Neko = 148149 SFW Cyber Ty = 63906, prob = 23958
        self.key = environ['FORGE']
        self.base_chat_url = "https://www.personalityforge.com/api/chat/?apiKey={self.key}&chatBotID={self.botID}&message="  # "{message}&externalID=<externalID>&firstName=<firstName>&lastName=<lastName>&gender=<gender>"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.content.startswith('..'):
            return
        ban_data = database.is_botban(message.author.id)
        if ban_data is None:
            if set(database.get_config('chat', message.guild.id)) & set([role.id for role in message.author.roles]) or database.get_config('chat', message.guild.id) == [0]:
                ctx = await self.bot.get_context(message)
                async with ctx.typing():
                    if not message.channel.nsfw:
                        await ctx.reply(f'This channel is not NSFW, I only chat in NSFW channels to be safe.')
                        return

                    if set(database.get_config('domme', message.guild.id)) & set([role.id for role in message.author.roles]):
                        gender = 'f'
                    else:
                        gender = 'm'
                    message = message.content[2:]
                    url = f"{self.base_chat_url}{message}&externalID={ctx.author.id}&gender={gender}"
                    data = requests.get(url).json()
                    if data['success'] == 1:
                        message = data['message']['message'].replace('<br>', '\n')
                        emotion = data['message']['emotion']
                        if emotion == 'happy-9':
                            # await ctx.message.add_reaction(emoji='simp:858985009905664040')
                            message = message + ' <:giggle:897777342791942225>'
                        if 'cowboy!' in message:
                            NSFW_reply = ['*ignoring*', 'Go watch porn pervert.', 'I am not a Pervert like you', 'I am not a pathetic slut like you.', ]
                            message = choice(NSFW_reply)
                        await ctx.reply(message)
                    else:
                        kuro_usagi = self.bot.get_user(104373103802466304)
                        await kuro_usagi.send(f"`{data}`")
                        await ctx.reply(f' I can\'t talk righ now {ctx.author.mention} I have personal stuff to do.')
            else:
                roles = '>'
                for r in database.get_config('chat', message.guild.id):
                    roles = f"{roles} <@&{r}>\n>"
                embed = discord.Embed(description=f"you don't have any of the following roles to talk to me.\n{roles[:-2]}", color=0xF2A2C0)
                await message.channel.send(embed=embed)
                return
        else:
            embed = discord.Embed(title='Bot Ban',
                                  description=f"{message.author.mention} you are banned from using {self.bot.user.mention} till {ban_data[1]}",
                                  color=0xF2A2C0)
            await message.reply(embed=embed)


def setup(bot):
    bot.add_cog(Chat(bot))
