#!/bin/python3
"""
by using API from personalityforge bot can talk like it does, for documentation visit https://www.personalityforge.com/chatbot-api-docs.php
"""
import configparser
from random import choice

import database
import discord
import requests
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')


class Chat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.botID = 106996  # NSFW Annabelle Lee = 106996, Laurel Sweet = 71367 Lil Neko = 148149 SFW Cyber Ty = 63906, prob = 23958,
    self.key = config.get('personalityforge', 'api_key')

    self.base_chat_url = f"https://www.personalityforge.com/api/chat/index.php"

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot or not message.content.startswith('..'):
      return

    ban_data = database.is_botban(message.author.id)
    if ban_data is None:
      if set(database.get_config('chat', message.guild.id)) & set(
          [str(role.id) for role in message.author.roles]) or database.get_config('chat', message.guild.id) == [0]:
        ctx = await self.bot.get_context(message)

        async with ctx.typing():
          if not message.channel.nsfw:
            await ctx.reply(f'This channel is not NSFW, I only chat in NSFW channels to be safe.')
            return

          has_role = lambda rid: str(rid) in [str(role.id) for role in message.author.roles]
          domme = database.get_config('domme', message.author.guild.id)[0]
          switch = database.get_config('switch', message.author.guild.id)[0]
          if has_role(domme) or has_role(switch):
            gender = 'f'
          else:
            gender = 'm'

          message = message.content[2:]

          params = {
            'apiKey': self.key,
            'message': message,
            'chatBotID': self.botID,
            'externalID': str(ctx.author.id),
            'gender': gender
            # 'hash': msg_hash,
            # 'message': raw_msg
          }

          resp = requests.get(self.base_chat_url, params=params).json()
          print(resp)
          message_data = resp['message']['message'].replace('<br>', '\n')
          emotion = resp['message']['emotion']
          if emotion == 'happy-9':
            # await ctx.message.add_reaction(emoji='simp:858985009905664040')
            message_data = message_data + ' 😁'
          if 'cowboy!' in message_data:
            NSFW_reply = ['*ignoring*', 'Go watch porn pervert.', 'I am not a Pervert like you',
                          'I am not a pathetic slut like you.', ]
            message_data = choice(NSFW_reply)
          await ctx.reply(message_data)
          # else:
          # kuro_usagi = self.bot.get_user(104373103802466304)
          # await kuro_usagi.send(f"`{data}`")
          # await ctx.reply(f' Hi {ctx.author.mention} I will be right with you!')
      else:
        roles = '>'
        for r in database.get_config('chat', message.guild.id):
          roles = f"{roles} <@&{r}>\n>"
        embed = discord.Embed(description=f"you don't have any of the following roles to talk to me.\n{roles[:-2]}",
                              color=0xF2A2C0)
        await message.channel.send(embed=embed)
        return
    else:
      embed = discord.Embed(title='Bot Ban',
                            description=f"{message.author.mention} you are banned from using {self.bot.user.mention} till {ban_data[1]}",
                            color=0xF2A2C0)
      await message.reply(embed=embed)


async def setup(bot):
  await bot.add_cog(Chat(bot))
