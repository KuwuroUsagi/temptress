#!/bin/python3
import database
import discord
import asyncio
import requests
import re
import unicodedata
import emoji as emo
from random import choice
from discord.ext import commands
from discord_components import *


def who_is(author, member):
    """
    returns int depends on relationship between author and member.

    2       author and member is the same person + has locker role

    202     both author and member have locker role

    200     member is owned by author

    201     member is unowned by author

    >300    discord id of member's owner

    222     member does not have locker or slave role and author has locker role

    1       author and member is the same person + has slave role

    101     both author and member have slave role

    102     author has slave role and member has locker role

    111     member does not have locker or slave role and author has slave role

    0       author does not have both slave and locker role

    -1      member is bot banned

    <-1     unixtime till author is banned
    """
    ban_data = database.is_botban(author.id)
    if ban_data is None:
        if database.is_botban(member.id) is None:
            if set(database.get_config('domme', member.guild.id)) & set([role.id for role in author.roles]):
                if author.id == member.id:
                    return 2
                if set(database.get_config('domme', member.guild.id)) & set([role.id for role in member.roles]):
                    return 202
                elif set(database.get_config('slave', member.guild.id)) & set([role.id for role in member.roles]):
                    ownerid = database.get_owner(member.id, member.guild.id)
                    if ownerid == author.id:
                        return 200
                    elif ownerid == 0:
                        return 201
                    elif ownerid > 300:
                        return ownerid
                else:
                    return 222
            elif set(database.get_config('slave', member.guild.id)) & set([role.id for role in author.roles]):
                if author.id == member.id:
                    return 1
                if set(database.get_config('slave', member.guild.id)) & set([role.id for role in member.roles]):
                    return 101
                if set(database.get_config('domme', member.guild.id)) & set([role.id for role in member.roles]):
                    return 102
                else:
                    return 111
            else:
                return 0
        else:
            return -1
    else:
        return -1 * ban_data[1]


class Action:
    def __init__(self, bot, ctx, member):
        self.bot = bot
        self.ctx = ctx
        self.author = ctx.author
        self.member = member

    def list_roles(self, roles):
        """
        returns string-metion-roles for embed
        """
        if isinstance(roles, list):
            role = '>'
            for r in roles:
                role = f"{role} <@&{r}>\n>"
            return role[:-2]
        else:
            return roles

    async def react(self, y_n):
        """
        reacts check/cross to the message
        """
        if y_n == 'yes' or y_n == 'y':
            await self.ctx.message.add_reaction(emoji='YES:897762486042910762')
        elif y_n == 'no' or y_n == 'n':
            await self.ctx.message.add_reaction(emoji='NO:897890789202493460')

    async def own(self):
        """
        will asks slave for consent and will add to ownership DB
        """
        def check(res):
            return self.member == res.user and res.channel == self.ctx.channel

        if len(database.get_slaves(self.author.id, self.ctx.guild.id)) >= 10:  # checks if the domme owns 10 or more slaves
            embed = discord.Embed(title='Nah',
                                  description=f"{self.author.mention} don't be like Succs and collect subs like pokemon",
                                  color=0xF2A2C0)
            await self.ctx.send(embed=embed)
        else:
            try:
                embed = discord.Embed(title='A new beginning!',
                                    description=f"{self.author.mention} wants a new toy! {self.member.mention} you are lucky one!!\n"
                                                f"Do you consent to do anything to make the domme happy and do everything she commands you to?",
                                    color=0xF2A2C0)

                m = await self.ctx.channel.send(embed=embed, components=[[Button(style=ButtonStyle.blue, label="Yes, I will be your toy"),
                                                                          Button(style=ButtonStyle.red, label="No, I am dumb")]])
                response = await self.bot.wait_for('button_click', timeout=60, check=check)
                await m.delete()
                
                if response.component.label == "Yes, I will be your toy":
                    database.own_a_slave(self.author.id, self.member.id, self.author.guild.id)
                    yes_embed = discord.Embed(title=f'Congratulations!',
                                              description=f'{self.author.mention} has tied a leash on {self.member.mention} and now she has a new pet!',
                                              color=0xF2A2C0)
                    await self.ctx.channel.send(embed=yes_embed)
                else:
                    no_embed = discord.Embed(title=f'What a catastrophe!',
                                             description=f'{self.member.mention} refused to be owned by {self.author.mention} How dare you!! Someone '
                                                        f'better hide!!!',
                                             color=0xFF2030)
                    await self.ctx.channel.send(embed=no_embed)
            except asyncio.TimeoutError:
                await m.delete()
                timeout_embed = discord.Embed(title=f'Time\'s Up!',
                                              description=f"You were too slow to consent the ownership request by {self.author.mention}.\nNow beg for another chance, "
                                                        f"{self.member.mention}! And better pray that she will request again.",
                                              color=0xF2A2C0)
                await self.ctx.channel.send(embed=timeout_embed)

    async def disown(self):
        """
        removes slave from ownership from DB
        """
        database.disown_a_slave(self.member.id, self.member.guild.id)
        disown_embed = discord.Embed(title=f'End of the Journey',
                                     description=f'The {self.author.mention} has decided to set you free, {self.member.mention}; '
                                                 f'therefore, your shared journey has come to an end. Hope you both had fun, but it is now time to part ways',
                                     color=0xF2A2C0)
        await self.ctx.channel.send(embed=disown_embed)
        await self.react('y')

    async def gag(self, type, message, temp=False):
        """
        gags the slave and updates slave slave DB
        if kwarg 'temp' is True, then gag in only for 10 mins
        """
        database.update_slaveDB(self.member.id, 'gag', type, self.member.guild.id)
        if type == 'kitty':
            kitty_gag_embed = discord.Embed(title="Behave like a good kitty",
                                            description=f"Lets hear you meow! {self.author.mention} convert {self.member.mention} into a kitty{' for next 10 minutes.' if temp else '.'}",
                                            color=0xF2A2C0)

            await message.edit(embed=kitty_gag_embed, components=[[Button(style=ButtonStyle.blue, label='Kitty Gag', emoji='🐱', disabled=True),
                                                                   Button(style=ButtonStyle.blue, label='Puppy Gag', emoji='🐶', disabled=True),
                                                                   Button(style=ButtonStyle.red, label='Ungag', disabled=True)]])

        elif type == 'puppy':
            puppy_gag_embed = discord.Embed(title="Behave like a good puppy",
                                            description=f"Lets hear you bark! {self.author.mention} convert {self.member.mention} into a puppy{' for next 10 minutes.' if temp else '.'}",
                                            color=0xF2A2C0)
            await message.edit(embed=puppy_gag_embed, components=[[Button(style=ButtonStyle.blue, label='Kitty Gag', emoji='🐱', disabled=True),
                                                                   Button(style=ButtonStyle.blue, label='Puppy Gag', emoji='🐶', disabled=True),
                                                                   Button(style=ButtonStyle.red, label='Ungag', disabled=True)]])
        await self.react('y')
        if temp:
            await asyncio.sleep(10 * 60)
            database.update_slaveDB(self.member.id, 'gag', 'off', self.member.guild.id)

    async def ungag(self, message):
        """
        ungags the slave and updates slave DB
        """
        database.update_slaveDB(self.member.id, 'gag', 'off', self.member.guild.id)
        puppy_kitty_ungag_embed = discord.Embed(title=f'Fun is over…',
                                                description=f'{self.author.mention}, converts {self.member.mention} back to a slave.',
                                                color=0xF2A2C0)

        await message.edit(embed=puppy_kitty_ungag_embed, components=[[Button(style=ButtonStyle.blue, label='Kitty Gag', emoji='🐱', disabled=True),
                                                                       Button(style=ButtonStyle.blue, label='Puppy Gag', emoji='🐶', disabled=True),
                                                                       Button(style=ButtonStyle.red, label='Ungag', disabled=True)]])
        await self.react('y')

    async def add_badword(self, badword_list):
        """
        adds badword to the DB
        """
        old_badword_list = [word[0] for word in database.get_badwords(self.member.id, self.member.guild.id)]

        if len(old_badword_list) >= 50:  # ignores the badwords if the member meets the limit '50'
            embed = discord.Embed(description=f"{self.member.mention}'s badwords reached it's limit. Better lock this slut.",
                                  color=0xF2A2C0)
            await self.ctx.send(embed=embed)
            await self.react('n')
        else:
            for badword in badword_list:
                if badword.lower() in ['', ' ']:
                    pass
                elif f"{badword.lower()[1:] if badword.lower().startswith(' ') else badword.lower()}" in old_badword_list:
                    pass
                else:
                    database.insert_badword(self.member.id, self.author.id, f"{badword.lower()[1:] if badword.lower().startswith(' ') else badword.lower()}", self.member.guild.id)
            badword_added_embed = discord.Embed(title="More punishments!",
                                                description=f"{self.author.mention} added a new badword to {self.member.mention}, \"{','.join(badword_list)}\"",
                                                colour=0xF2A2C0)
            await self.ctx.channel.send(embed=badword_added_embed)
            await self.react('y')

    async def remove_badword(self, badword_list):
        """
        removes badword from the DB
        """
        for badword in badword_list:
            database.remove_badword(self.member.id, f"{badword.lower()[1:] if badword.lower().startswith(' ') else badword.lower()}", self.member.guild.id)
        badword_remove_embed = discord.Embed(title="Lucky slave!",
                                             description=f"{self.author.mention} had sympathy for you and removed your bad words \"{','.join(badword_list)}\", {self.member.mention}. Better be grateful! ",
                                             colour=0xF2A2C0)
        await self.ctx.channel.send(embed=badword_remove_embed)
        await self.react('y')

    async def clear_badword(self):
        """
        removes all badwords from the slave
        """
        database.clear_badword(self.member.id, self.member.guild.id)
        badword_clear_embed = discord.Embed(title="Lucky slave!",
                                            description=f"{self.author.mention} had sympathy for you and removed all your badwords, {self.member.mention}. Better be grateful! ",
                                            colour=0xF2A2C0)
        await self.ctx.channel.send(embed=badword_clear_embed)
        await self.react('y')

    async def nickname(self, name):
        """
        changes the nickname of the slave
        """
        me = self.ctx.guild.get_member(self.bot.user.id) 
        if self.ctx.guild.owner_id != self.member.id:  # checking if member is owner
            if me.guild_permissions.administrator:  # checking if bot has admin permission
                if me.top_role > self.member.top_role:  # checking if bot has higher role that member
                    if len(name) > 30:
                        await self.message.reply(f"name is too long, *30 characters only*")
                        await self.react('n')
                        return
                    await self.member.edit(nick=name)
                    if name != '':
                        name_embed = discord.Embed(title=f'New Name!',
                                                description=f'{self.author.mention} gave a new name to {self.member.mention}',
                                                color=0xF2A2C0)
                    else:
                        name_embed = discord.Embed(description=f"name of {self.member.mention} is removed",
                                                color=0x08FF08)
                    await self.ctx.channel.send(embed=name_embed)
                    await self.react('y')
                else:
                    no_power_embed = discord.Embed(description=f'{self.member.mention} have higher role than me <:crypanda:897832575698075688>',
                                                   color=0xFF2030)
                    await self.ctx.send(embed=no_power_embed)
            else:
                no_power_embed = discord.Embed(description=f'I don\'t have administrator permission in the server <:crypanda:897832575698075688>',
                                               color=0xFF2030)
                await self.ctx.send(embed=no_power_embed)
        else:
            no_power_embed = discord.Embed(description=f'{self.member.mention} in the server owner I don\'t have permission to change nickname <:crypanda:897832575698075688>',
                                           color=0xFF2030)
            await self.ctx.send(embed=no_power_embed)

    async def rank(self, num):
        """
        ranks the slave and update Ownership DB
        """
        slave_list = database.get_slaves(self.author.id, self.author.guild.id)
        if 0 <= num <= len(slave_list):
            if num == 0:
                database.set_slave_rank(self.member.id, 1000, self.member.guild.id)
                embed = discord.Embed(description=f"Rank of {self.member.mention} is removed",
                                      colour=0xF2A2C0)
                await self.ctx.channel.send(embed=embed)
                await self.react('y')
            else:
                database.set_slave_rank(self.member.id, num, self.member.guild.id)
                embed = discord.Embed(description=f"{self.member.mention} is on rank **{num}** of {self.author.mention}\'s favorite Subs",
                                      colour=0xF2A2C0)
                await self.ctx.channel.send(embed=embed)
                await self.react('y')
        else:
            embed = discord.Embed(description=f"you only own {len(slave_list)} Subs, Please choice a number between `0-{len(slave_list)}` \n**0** to remove the rank from the mentioned slave.",
                                  color=0xF2A2C0)
            await self.ctx.message.reply(embed=embed)

    async def emoji_access(self, _type, message, temp=False):
        """
        updates SlaveDB and toggle emoji_access,
        if kwarg temp is True then emoji is denied for 1h
        """
        database.update_slaveDB(self.member.id, 'emoji', _type, self.member.guild.id)
        if _type:
            embed = discord.Embed(title="Emojis on",
                                  description=f" {self.member.mention}, you lucky prick! you got your emojis back.",
                                  colour=0xF2A2C0)
        elif not _type:
            embed = discord.Embed(title="Emojis off",
                                  description=f" {self.author.mention} took away {self.member.mention}'s emojis{' for next 1 hour.' if temp else '.'}",
                                  color=0xF2A2C0)
        await message.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Allow Emoji', disabled=True),
                                                     Button(style=ButtonStyle.red, label='Deny Emoji', disabled=True)]])
        await self.react('y')
        if temp:
            await asyncio.sleep(1 * 60 * 60)
            database.update_slaveDB(self.member.id, 'emoji', True, self.member.guild.id)

    async def tie_in_channel(self, channel):
        """
        updates SlaveDB and ties slave in a channel
        """
        database.update_slaveDB(self.member.id, 'tiechannel', channel, self.member.guild.id)
        if channel > 0:
            embed = discord.Embed(title="Time for Bondage!",
                                  description=f" {self.author.mention} tied {self.member.mention} in <#{channel}>, she tied you so strong that you can't move a bit.",
                                  colour=0xF2A2C0)
        elif channel == 0:
            embed = discord.Embed(title="Fun is over…",
                                  description=f"{self.author.mention}, untied her slave now {self.member.mention} is free, (i hope your body has marks of bondage)",
                                  colour=0xF2A2C0)
        await self.ctx.channel.send(embed=embed)
        await self.react('y')

    async def status(self):
        """
        makes status embed
        """
        member = self.member or self.author
        
        ban_data = database.is_botban(member.id)
        if ban_data is not None:  # if the member is banned from using bot
            embed = discord.Embed(title='Bot Ban',
                                  description=f"{member.mention} is banned from using {self.bot.user.mention} till <t:{ban_data[1]}:F>",
                                  color=0xF2A2C0)
            embed.set_thumbnail(url=member.avatar_url)
            await self.ctx.send(embed=embed)
            return
        
        if set(database.get_config('slave', member.guild.id)) & set([role.id for role in member.roles]):  # slave status
            name = member.nick or member.name
            owner = database.get_owner(member.id, member.guild.id)
            if owner == 0:
                owner = f"Owned by no one, a poor lonely soul"
            else:
                if member.id == 855057142297264139:  # Alex wood ID
                    owner = f"Owned by <@{owner}>"
                else:
                    owner = f"Owned by <@{owner}>"
            data = database.get_slave_from_DB(member.id, member.guild.id)[0]
            gag = data[2]
            if gag == 'kitty':
                gag = '<a:kitty:897769441796964372> Kitty'
            elif gag == 'puppy':
                gag = '<:puppy:897769322242510850> Puppy'
            else:
                gag = 'None'

            restriction = f"> **Speech Restriction** : {gag}"

            restriction = f"{restriction}\n> **NSFW Access** : {'<a:YES:897762486042910762>' if data[6] else '<a:NO:897890789202493460>'}\n> **Emoji Access** : {'<a:YES:897762486042910762>' if data[4] else '<a:NO:897890789202493460>'}\n> **Voice Channel Access** : {'<a:YES:897762486042910762>' if data[7] else '<a:NO:897890789202493460>'}\n> **Channel tied too** : {'<a:NO:897890789202493460>' if data[3] == 0 else f'<a:YES:897762486042910762> <#{data[3]}>'}"
            badwords = [word[0] for word in database.get_badwords(member.id, member.guild.id)]
            badword_count = len(badwords)
            if badword_count > 0:
                badwords = ', '.join(badwords)
                restriction = restriction + f"\n> **Badwords ({badword_count})** : {badwords}"

            lines_count = data[5]

            embed = discord.Embed(title=name,
                                  description=f"{owner}",
                                  color=0xF2A2C0)

            money = database.get_money(member.id, member.guild.id)

            embed.add_field(name='Cash', value=f"\n> <a:pinkcoin:900000697288892416> {money[2]}\n> <a:gems:899985611946078208> {money[3]}", inline=False)
            embed.add_field(name='Restrictions', value=restriction, inline=False)

            simp_list = database.get_simp(member.id, member.guild.id)
            if simp_list is not None:
                total_simp = simp_list[1]
                simp_list = simp_list[0]
                simp_list = sorted(simp_list, key=lambda simp_list: simp_list[1], reverse=True)[:5]
                simps = ''
                for s in simp_list:
                    simps = f"{simps}\n> <@{s[0]}> {int((s[1]/total_simp)*100)}% ({s[1]})"
                embed.add_field(name='I Simp for', value=simps, inline=False)

            if lines_count > 0:
                embed.add_field(name="Lines I wrote", value=f"> {lines_count} lines written <#{database.get_config('prison', member.guild.id)[0]}>", inline=False)
            embed.set_thumbnail(url=member.avatar_url)

        elif set(database.get_config('domme', member.guild.id)) & set([role.id for role in member.roles]):   # domme status
            def get_status_emojis(member, guild):
                data = database.get_slave_from_DB(member, guild)[0]
                return f"{'' if data[6] else '<:chastity:897763218670354442>'}  {'' if data[7] else '<a:muffs:897764112388468747>'}  {'<:ballgag:897915835555921921>' if data[2] in ['kitty', 'puppy'] else ''}  {'' if data[4] else '<:noemoji:897921450118356992>'}"
            name = member.nick or member.name
            slaves_list = database.get_slaves(member.id, member.guild.id)
            if not slaves_list:
                owned_slaves = "> Until now, no one has proven themselves worthy of being owned by me"
            else:
                owned_slaves = "\n"
                for slave in slaves_list:
                    owned_slaves += f"> {'' if slave[1] == 1000 else f'{slave[1]}°'} <@{str(slave[0])}>  {get_status_emojis(int(slave[0]), member.guild.id)}\n"

            money = database.get_money(member.id, member.guild.id)

            embed = discord.Embed(title=name, color=0xF2A2C0)
            embed.add_field(name='Cash', value=f"\n> <a:pinkcoin:900000697288892416> {money[2]}\n> <a:gems:899985611946078208> {money[3]} ", inline=False)
            embed.add_field(name='My Subs', value=owned_slaves, inline=False)

            simp_list = database.get_simp(member.id, member.guild.id)
            if simp_list is not None:
                total_simp = simp_list[1]
                simp_list = simp_list[0]
                simp_list = sorted(simp_list, key=lambda simp_list: simp_list[1], reverse=True)[:5]
                simps = ''
                for s in simp_list:
                    simps = f"{simps}\n> <@{s[0]}> {int((s[1]/total_simp)*100)}% ({s[1]})"
                embed.add_field(name='I Simp for', value=simps, inline=False)

            embed.set_thumbnail(url=member.avatar_url)

        else:
            if database.get_config('domme', member.guild.id) == [0]:
                embed = discord.Embed(title='I am not ready yet', description='ask Admins to run the command **`s.setup`**', color=0xF2A2C0)
            else:
                embed = discord.Embed(title='I don\'t know you.',
                                      description=f"You need any of the following roles:\n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                                      color=0xF2A2C0)

        await self.ctx.channel.send(embed=embed)

    async def leaderboard(self, type='line'):
        """
        makes embed for leaderboard.
        kwarg type takes two types 'line' and 'cash'
        """
        page_number = 1
        size = 10

        def check(reaction, user):
            return user == self.author

        if type == 'line':
            data = database.get_lines_leaderboard(self.ctx.guild.id)

            def page(lb_list, page, size):
                value = ''
                try:
                    for x in range(((page - 1) * size), ((page - 1) * size) + size):
                        value = value + f"> <@{lb_list[x][0]}> ({lb_list[x][1]})\n"
                    embed = discord.Embed(title="Leaderboard • Subs • Lines Count", description=value, color=0xF2A2C0)
                except IndexError:
                    embed = discord.Embed(title="Leaderboard • Subs • Lines Count", description=value, color=0xF2A2C0)

                embed.set_footer(text=f"On page {page}/{int(len(lb_list) / size) + (len(lb_list) % size > 0) + 1}")
                embed.set_thumbnail(url=self.ctx.guild.icon_url)
                return embed

            embed = page(data, 1, size)
            box = await self.ctx.channel.send(embed=embed)
            await box.add_reaction('⏪')
            await box.add_reaction('⏩')
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                    await box.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    break
                if str(reaction) == '⏪':
                    if page_number == 1:
                        pass
                    else:
                        embed = page(data, page_number - 1, size)
                        page_number -= 1
                if str(reaction) == '⏩':
                    if page_number == int(len(data) / size) + (len(data) % size > 0) + 1:
                        pass
                    else:
                        embed = page(data, page_number + 1, size)
                        page_number += 1
                await box.edit(embed=embed)

        elif type == 'cash':
            data = database.get_money_leaderboard(self.ctx.guild.id)

            def page(lb_list, page, size):
                value = ''
                try:
                    for x in range(((page - 1) * size), ((page - 1) * size) + size):
                        value = value + f"> <@{lb_list[x][0]}> {int(lb_list[x][2]/10)} <a:gems:899985611946078208>   {lb_list[x][1]} <a:pinkcoin:900000697288892416>\n"
                    embed = discord.Embed(title="Leaderboard • Cash", description=value, color=0xF2A2C0)
                except IndexError:
                    embed = discord.Embed(title="Leaderboard • Cash", description=value, color=0xF2A2C0)

                embed.set_footer(text=f"On page {page}/{int(len(lb_list) / size) + (len(lb_list) % size > 0) + 1}")
                embed.set_thumbnail(url=self.ctx.guild.icon_url)
                return embed

            embed = page(data, 1, size)
            box = await self.ctx.channel.send(embed=embed)
            await box.add_reaction('⏪')
            await box.add_reaction('⏩')
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                    await box.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    break
                if str(reaction) == '⏪':
                    if page_number == 1:
                        pass
                    else:
                        embed = page(data, page_number - 1, size)
                        page_number -= 1
                if str(reaction) == '⏩':
                    if page_number == int(len(data) / size) + (len(data) % size > 0) + 1:
                        pass
                    else:
                        embed = page(data, page_number + 1, size)
                        page_number += 1
                await box.edit(embed=embed)


class Punishment:
    def __init__(self, ctx):
        self.author = ctx.author
        self.id = ctx.message.author.id
        self.message = ctx.message
        self.channel = ctx.channel
        self.avatar_url = ctx.author.avatar_url
        self.mention = ctx.author.mention
        slaveDB = database.get_slave_from_DB(self.id, ctx.guild.id)
        self.badwords = [word[0] for word in database.get_badwords(self.id, ctx.guild.id)]

        self.name = ctx.author.nick or ctx.author.name

        self.is_gag = slaveDB[0][2]
        self.tiechannelid = slaveDB[0][3]
        self.is_emoji = slaveDB[0][4]

    async def send_webhook(self, avatar_url, message, name, channel):
        """
        this function makes webhook and send messages
        """
        hooks = await channel.webhooks()
        if not hooks or 'seductress' not in [hook.name for hook in hooks]:
            new_hook = await channel.create_webhook(name="seductress")
            data = {'content': message,
                    'username': str(name),
                    'avatar_url': str(avatar_url)}
            requests.post(new_hook.url, data=data)
            return
        for hook in hooks:
            if hook.name == 'seductress':
                data = {'content': message,
                        'username': str(name),
                        'avatar_url': str(avatar_url)}
                requests.post(hook.url, data=data)
                return

    async def gag(self):
        """
        this function deletes the message if the member is gagged and calls send_webhook() to replace the message..
        """
        if self.is_gag == 'off':
            return
        message = ''
        await self.message.delete()
        if self.is_gag == 'kitty':
            kitty_text = [' meow', ' mew', ' mrow', ' mrrroww', ' prrr', ' purr', 'maiu']
            for _ in range(int(len(self.message.content) / 7) + 1):
                message = message + choice(kitty_text)
            await self.send_webhook(self.avatar_url, message, '🐱' + self.name, self.channel)
        elif self.is_gag == 'puppy':
            puppy_text = ['ah uh ah uh', 'ar rooff ', ' arf', ' bow-wow', ' ruff', ' ruh-roh', ' woof', 'hu hu hu hu',
                          'raow', 'rrowff', 'auf']
            for _ in range(int(len(self.message.content) / 7) + 1):
                message = message + choice(puppy_text)
            await self.send_webhook(self.avatar_url, message, '🐶' + self.name, self.channel)

    async def is_badword(self):        
        """
        deletes the message if they use badwords
        """
        string = re.sub('[^A-Za-z0-9]+', '', unicodedata.normalize('NFD', self.message.content).encode('ascii', 'ignore').decode('utf-8')).lower()
        if any([bad_word in string for bad_word in self.badwords]):
            await self.message.delete()
            life = database.get_slave_from_DB(self.author.id, self.author.guild.id)[0][8]
            if life == 1:
                database.update_slaveDB(self.author.id, 'life', 10, self.author.guild.id)
                database.update_slaveDB(self.author.id, 'gag', 'kitty', self.author.guild.id)
                embed = discord.Embed(title='Gag the brats',
                                      description=f"{self.author.mention} your are a bad kitty, you are gagged till your owner ungags you.",
                                      color=0xF2A2C0)
                await self.channel.send(embed=embed)
                owner = self.author.guild.get_member(database.get_owner(self.author.id, self.author.guild.id))
                await owner.send(f"{self.author.mention} is gagged in the server **{self.author.guild.name}** because of our policy **Gag the brats** ")
            else:
                database.update_slaveDB(self.author.id, 'life', life-1, self.author.guild.id)
                embed = discord.Embed(title="Nope",
                                    description=f"{self.mention} can't say that word little one! Better watch that mouth!, you lost 1 life."
                                    f"\n\n\n**life**\n> {'<:minecraftheart:906338512184438854>'*(life - 1)}{'<:blackheart:906338619407601695>'*(11 - life)}",
                                    colour=0xF2A2C0)
                await self.channel.send(embed=embed, delete_after=5)

    async def is_tiechannel(self):
        """
        deletes th emessage if tied
        """
        if self.tiechannelid == 0 or self.channel.id == self.tiechannelid:
            return
        await self.message.delete()
        await self.author.send(
            f"you are tied to <#{self.tiechannelid}> you can't send messages in <#{self.channel.id}>")
        message = f"I am tied in <#{self.tiechannelid}>"
        await self.send_webhook(self.avatar_url, message, self.name, self.channel)

    async def emoji_delete(self):
        """
        deletes emoji if they don't have permission to use it
        """
        if self.is_emoji:
            return

        def text_has_emoji(text):
            for character in str(text):
                if character in emo.UNICODE_EMOJI['en'].keys() or character in emo.UNICODE_EMOJI['es'].keys() or character in emo.UNICODE_EMOJI['pt'].keys() or character in emo.UNICODE_EMOJI['it'].keys():
                    return True
            return False

        custom_emojis = re.findall(r'<:\w*:\d*>', self.message.content)
        custom_animated_emojis = re.findall(r'<a:\w*:\d*>', self.message.content)
        if not custom_emojis and not custom_animated_emojis and not text_has_emoji(str(self.message.content)):
            return
        else:
            await self.message.delete()
            m = await self.channel.send(f"{self.mention} you don't have permission to use emojis")
            await asyncio.sleep(5)
            await m.delete()


class Femdom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(bot)

    def list_roles(self, roles):
        if isinstance(roles, list):
            role = '>'
            for r in roles:
                role = f"{role} <@&{r}>\n>"
            return role[:-2]
        else:
            return roles

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if message.author.bot:
            return

        if set(database.get_config('slave', ctx.guild.id)) & set([role.id for role in message.author.roles]):
            if database.is_botban(message.author.id) is None:
                punishment = Punishment(ctx)
                await punishment.is_badword()
                await punishment.is_tiechannel()
                await punishment.gag()
                await punishment.emoji_delete()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        when a new member gets slave role then they are added to slaveDB
        """
        slave_role_id = database.get_config('slave', before.guild.id)
        if not (set(slave_role_id) & set([role.id for role in before.roles])) and set(slave_role_id) & set([role.id for role in after.roles]):
            database.get_slave_from_DB(after.id, before.guild.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        when a member leaves the server deletes them from DB, it the member is domme then all her slaves are free.
        """
        database.remove_member(member.id, member.guild.id)

    @commands.command(aliases=['leash', 'claim'])
    @commands.guild_only()
    async def own(self, ctx, member: discord.Member):
        if ctx.author.bot:  # if the author is a bot.
            return

        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return
    
        if member.id == self.bot.user.id:  # Seductress ID, owning Seductress
            embed = discord.Embed(description=f"I know it is tempting to having a cute baby girl like me as your sub<:giggle:897777342791942225>"
                                              f" I know it is tempting to spank and choke me at the same time but I am"
                                              f" {self.bot.user.name}, this bitch is not for sales, I am sorry<:cya:897777567086563369>",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        elif member.bot:  # owning a random bot
            embed = discord.Embed(description=f"{member.mention} is too strong for you to own!", color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 2:  # Domme self owning.
                embed = discord.Embed(title=f'Nah',
                                      description=f'{ctx.author.mention}, are you the last one alive on earth, why are you trying to own yourself.'
                                                  f'It makes no sense.',
                                      color=0xF2A2C0)

            elif member_is == 1:  # slave self owning
                embed = discord.Embed(title=f'Pathetic!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not worthy of owning anyone or '
                                                  f'anything in your whole life! You are not even worthy to own your own life!',
                                      color=0xF2A2C0)

            elif member_is == 202:  # domme owning a domme.
                embed = discord.Embed(title='Nah',
                                      description=f'Only slaves can be '
                                                  f'owned by dommes and since {member.mention} is a domme you can’t own her.',
                                      color=0xF2A2C0)

            elif member_is == 200:  # owning a already owned pet
                embed = discord.Embed(title='Hmmmm',
                                      description=f"{ctx.author.mention} You already own him, {member.mention} is already your pet",
                                      color=0xF2A2C0)

            elif member_is > 300:  # trying to own other dommes property
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention}, is owned by another Domme, <@{member_is}>.",
                                      color=0xFF2030)

            elif member_is == 101:  # slave trying to own other slave
                embed = discord.Embed(title='Pathetic…',
                                      description=f"<:giggle:897777342791942225>You foolish {ctx.author.mention} ahahahahha. You think you can own a sub when you are a slave?!, "
                                                  f"Ahahahaha don't dumb like Shaman.",
                                      color=0xFF2030)

            elif member_is == 102:  # slave trying to own other slave.
                embed = discord.Embed(title='You shall no do such thing.',
                                      description=f'{ctx.author.mention} , you are a slave, you are not worthy of owning anyone or '
                                                  f'anything in your whole life! Especially not a Domme, how could you even '
                                                  f'consider trying something so foolish!! {member.mention} I think someone needs '
                                                  f'to learn a lesson!!!',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            elif member_is == 201:  # when domme owning a free slave
                await action.own()
                return
            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command(aliases=['release'])
    @commands.guild_only()
    async def disown(self, ctx, member: discord.Member):
        if ctx.author.bot:  # when author is a bot.
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        if member.id == self.bot.user.id:  # Seductress ID, owning Seductress
            embed = discord.Embed(description=f"<:crypanda:897832575698075688> why are you trying to disown me, am I not a good girl.",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        elif member.bot:  # when mentioning a random bot.
            embed = discord.Embed(description=f"{member.mention} is a bot not your slut to disown!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave self disowning
                embed = discord.Embed(title='Pathetic...',
                                      description=f"This simpleton slave is trying to disown himself! {ctx.author.mention} only a "
                                                  f"Domme can decide whether you deserve to be disowned, how pathetic!!",
                                      color=0xFF2030)

            elif member_is == 2:  # Domme self disowning
                embed = discord.Embed(title='Nah',
                                      description=f'{ctx.author.mention}, I am so confused WHAT ARE YOU DOING.',
                                      color=0xF2A2C0)

            elif member_is == 202:  # Domme disowning Domme
                embed = discord.Embed(title='Nah',
                                      description=f"Are you out of your mind, {member.mention} is a domme, So you can\' disown her",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme disowning Free slave
                embed = discord.Embed(title='Nah',
                                      description=f"Don\'t worry, {ctx.author.mention}, you did not own {member.mention} in the first place",
                                      color=0xF2A2C0)

            elif member_is == 200:  # Domme disowning Owned slave
                await action.disown()
                return

            elif member_is > 300:  # Domme disowning other dommes owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"You can't disown {member.mention}, is "
                                                  f"owned by another Domme, <@{member_is}>. ||but you can block {member.mention} <:giggle:897777342791942225>||",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave disowning Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You dumbass slave. You think you can disown when you are a slave, {ctx.author.mention}!"
                                                  f"how Pathetic, Ahahahaha I need to tell this joke to Shaman, he will love it. he is also a pathetic bitch.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave disowning Domme
                embed = discord.Embed(title='Nah',
                                      description=f"You shall not try such thing!, {ctx.author.mention} you are a slave,"
                                                  f" you are not as powerful as a domme and you will never be! How could you even consider trying something so foolish!!"
                                                  f" {member.mention} I think someone needs to learn a lesson!!!, brainless slave",
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)
            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def gag(self, ctx, member: discord.Member):
        if ctx.author.bot:  # when author is a bot.
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        if member.id == self.bot.user.id:  # seductress ID, trying to kitty gag seductress.
            embed = discord.Embed(description=f"Pff.. are you dumb like Shaman, Ahahaha!!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        elif member.bot:  # when mentioning a random bot
            embed = discord.Embed(description=f"{member.mention} is a bot not your slut!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave self gag
                embed = discord.Embed(title='Pathetic...',
                                      description=f"This Pathetic slave is trying to gag himself! {ctx.author.mention} only a "
                                                  f"Domme can gag you.",
                                      color=0xF2A2C0)

            elif member_is == 2 or member_is == 202:  # Domme gag on self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"I am sorry {ctx.author.mention}, but I can't do such a thing. It's unbearable to see "
                                                  f"a Domme being gagged.",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme gag in Free slave
                if database.get_money(ctx.author.id, ctx.guild.id)[3] <= 0:
                    embed = discord.Embed(title='Nah',
                                          description=f"{ctx.author.mention}, you don't have magic gem, you need magic gem <a:gems:899985611946078208> "
                                          f"to gag/ungag because {member.mention} is a free slave!",
                                          color=0xF2A2C0)
                else:
                    embed = discord.Embed(title="What should I do?", color=0xF2A2C0)
                    gag = database.get_slave_from_DB(member.id, ctx.guild.id)[0][2]
                    m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.blue, label='Kitty Gag', emoji='🐱', disabled=(gag == 'kitty')),
                                                                  Button(style=ButtonStyle.blue, label='Puppy Gag', emoji='🐶', disabled=(gag == 'puppy')),
                                                                  Button(style=ButtonStyle.red, label='Ungag', disabled=(gag == 'off'))]])
                    try:
                        def check(res):
                            return ctx.author == res.user and res.channel == ctx.channel

                        response = await self.bot.wait_for('button_click', timeout=30, check=check)
                        await response.respond(type=6)
                        if response.component.label == 'Kitty Gag':
                            await action.gag('kitty', m, temp=True)
                        elif response.component.label == 'Puppy Gag':
                            await action.gag('puppy', m, temp=True)
                        else:
                            await action.ungag(m)
                        database.remove_money(ctx.author.id, ctx.guild.id, 0, 10)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(description=f"{ctx.author.mention} you got only 30 secs to make a choice, I can't wait for long.", color=0xF2A2C0)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.blue, label='Kitty Gag', emoji='🐱', disabled=True),
                                                               Button(style=ButtonStyle.blue, label='Puppy Gag', emoji='🐶', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Ungag', disabled=True)]])
                    return

            elif member_is == 200:  # Domme kitty gag on Owned slave
                embed = discord.Embed(title="What should I do?", color=0xF2A2C0)
                gag = database.get_slave_from_DB(member.id, ctx.guild.id)[0][2]
                m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.blue, label='Kitty Gag', emoji='🐱', disabled=(gag == 'kitty')),
                                                              Button(style=ButtonStyle.blue, label='Puppy Gag', emoji='🐶', disabled=(gag == 'puppy')),
                                                              Button(style=ButtonStyle.red, label='Ungag', disabled=(gag == 'off'))]])
                try:
                    def check(res):
                        return ctx.author == res.user and res.channel == ctx.channel

                    response = await self.bot.wait_for('button_click', timeout=30, check=check)
                    await response.respond(type=6)
                    if response.component.label == 'Kitty Gag':
                        await action.gag('kitty', m)
                    elif response.component.label == 'Puppy Gag':
                        await action.gag('puppy', m)
                    else:
                        await action.ungag(m)
                except asyncio.TimeoutError:
                    embed = discord.Embed(description=f"{ctx.author.mention} you got only 30 secs to make a choice, I can't wait for long.", color=0xF2A2C0)
                    await m.edit(embed=embed, components=[[Button(style=ButtonStyle.blue, label='Kitty Gag', emoji='🐱', disabled=True),
                                                           Button(style=ButtonStyle.blue, label='Puppy Gag', emoji='🐶', disabled=True),
                                                           Button(style=ButtonStyle.red, label='Ungag', disabled=True)]])
                return

            elif member_is > 300:  # Domme gag on other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"I am sorry {member.mention} is owned by <@{member_is}>, it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave kitty gag on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can gag when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\n I need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave kitty gag on Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member doesn't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command(aliases=['word', 'addbadword', 'words', 'badwords', 'addbadwords'])
    @commands.guild_only()
    async def badword(self, ctx, member: discord.Member, *, words):
        if ctx.author.bot:  # when author is a bot
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        elif member.bot:  # when mentioned user is a bot
            embed = discord.Embed(description=f"{member.mention} is a bot not a Pathetic Slut!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave self adding badword
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to be add badword himself! {ctx.author.mention} only a "
                                                  f"Domme can do it.",
                                      color=0xF2A2C0)

            elif member_is == 2 or member_is == 202:  # Domme adding badword on self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"I am sorry {ctx.author.mention}, but I can't do such a thing because you are a beautiful domme.",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme addword on Free slave
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:  # Domme adding badword on Owned slave
                words = words.split(',')
                await action.add_badword(words)
                return

            elif member_is > 300:  # Domme adding badword for other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"I am sorry {member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave adding badword on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can add badword when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave adding badword for Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command(aliases=['removeword'])
    @commands.guild_only()
    async def removebadword(self, ctx, member: discord.Member, *, words):
        if ctx.author.bot:  # when author is a bot
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        elif member.bot:  # when mentioned member is bot
            embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave self removing badword
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to be remove badword himself! {ctx.author.mention} only a "
                                                  f"Domme can do it.",
                                      color=0xF2A2C0)

            elif member_is == 2 or member_is == 202:  # Domme removing badword self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"I am so confused.",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme ungaging on Free slave
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:  # Domme removing badword on Owned slave
                words = words.split(',')
                await action.remove_badword(words)
                return

            elif member_is > 300:  # Domme removing badword on other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave removing badword on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can remove badword when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave removing badword on Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command(aliases=['removeallbadwords', 'clearwords', 'removeallwords'])
    @commands.guild_only()
    async def clearbadword(self, ctx, member: discord.Member):
        if ctx.author.bot:  # when author is a bot
            return

        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        elif member.bot:  # when mentioned member is a bot
            embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave self clearing all badwords
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to be remove badword himself! {ctx.author.mention} only a "
                                                  f"Domme can do it.",
                                      color=0xF2A2C0)

            elif member_is == 2 or member_is == 202:  # Domme clearing badwords self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"I am so confused.",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme clearing badword on Free slave
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:  # Domme clearing badwords on Owned slave
                await action.clear_badword()
                return

            elif member_is > 300:  # Domme clearing badwords on other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave clearing badwords on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can remove badword when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave clearing badword of Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command(aliases=['name', 'nick', 'clearname', 'clearnick', 'removename', 'removenick'])
    @commands.guild_only()
    async def nickname(self, ctx, member: discord.Member, *, name=''):
        if ctx.author.bot:  # when author is a bot
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        elif member.bot:  # when mentioned member is bot
            embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave self nickname
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to change name himself! {ctx.author.mention} only a "
                                                  f"Domme can do it.",
                                      color=0xF2A2C0)

            elif member_is == 202:  # Domme nickname self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.member.mention}, is a beautiful name.",
                                      color=0xF2A2C0)

            elif member_is in [200, 201, 2]:  # Domme nickname on Owned slave
                await action.nickname(name)
                return

            elif member_is > 300:  # Domme nickname on other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave nickname on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can change name when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave nickname on Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def status(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        action = Action(self.bot, ctx, member)
        if ctx.author.bot:
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return
        
        elif member.bot:
            if member.id == self.bot.user.id:
                embed = discord.Embed(title='So you want to know my status?',
                                      description=f"I am Seductress. A woman who seduces someone like you, A harsh dominant one who entices men into sexual activities and suffering.",
                                      color=0xF2A2C0)
            else:
                embed = discord.Embed(description=f"{member.mention} is my friend to make men incel.",
                                      color=0xF2A2C0)
            embed.set_thumbnail(url=member.avatar_url)
        else:
            await action.status()
            return
        await ctx.channel.send(embed=embed)

    @commands.command(aliases=['emoji'])
    @commands.guild_only()
    async def emojii(self, ctx, member: discord.Member):
        if ctx.author.bot:  # when author is a bot
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        elif member.bot:  # when mention a ramdom bot
            embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave try to emoji allow self
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, slut!!",
                                      color=0xF2A2C0)

            elif member_is == 2 or member_is == 202:  # Domme emoji allow self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"It's unbearable to see "
                                                  f"a Domme being punished. so you have emoji access always",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme ungaging on Free slave
                if database.get_money(ctx.author.id, ctx.guild.id)[3] <= 0:
                    embed = discord.Embed(title='Nah',
                                          description=f"{ctx.author.mention}, you don't have magic gem, you need magic gem <a:gems:899985611946078208> "
                                          f"to ban/allow emotes because {member.mention} is a free slave!",
                                          color=0xF2A2C0)
                else:
                    _type = database.get_slave_from_DB(member.id, ctx.guild.id)[0][4]
                    embed = discord.Embed(title="Emoji Access", color=0xF2A2C0)
                    m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.green, label='Allow Emoji', disabled=_type),
                                                                  Button(style=ButtonStyle.red, label='Deny Emoji', disabled=not _type)]])
                    try:
                        def check(res):
                            return ctx.author == res.user and res.channel == ctx.channel

                        response = await self.bot.wait_for('button_click', timeout=30, check=check)
                        await response.respond(type=6)
                        if response.component.label == 'Allow Emoji':
                            await action.emoji_access(True, m)
                        else:
                            await action.emoji_access(False, m, temp=True)
                        database.remove_money(ctx.author.id, ctx.guild.id, 0, 10)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(title='Time\'s Up', description='you got only 30 secs to make a choice.', color=0xF2A2C0)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Allow Emoji', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Deny Emoji', disabled=True)]])
                    return

            elif member_is == 200:  # Domme emoji allow on Owned slave
                _type = database.get_slave_from_DB(member.id, ctx.guild.id)[0][4]
                embed = discord.Embed(title="Emoji Access", color=0xF2A2C0)
                m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.green, label='Allow Emoji', disabled=_type),
                                                              Button(style=ButtonStyle.red, label='Deny Emoji', disabled=not _type)]])
                try:
                    def check(res):
                        return ctx.author == res.user and res.channel == ctx.channel

                    response = await self.bot.wait_for('button_click', timeout=30, check=check)
                    await response.respond(type=6)
                    if response.component.label == 'Allow Emoji':
                        await action.emoji_access(True, m)
                    else:
                        await action.emoji_access(False, m)
                except asyncio.TimeoutError:
                    embed = discord.Embed(title='Time\'s Up', description='you got only 30 secs to make a choice.', color=0xF2A2C0)
                    await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Allow Emoji', disabled=True),
                                                           Button(style=ButtonStyle.red, label='Deny Emoji', disabled=True)]])
                return

            elif member_is > 300:  # Domme emoji allow on other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave emoji allow on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can control emojis when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave emoji allow on Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def tie(self, ctx, member: discord.Member, channel: discord.TextChannel = None):
        if ctx.author.bot:  # when author is a bot
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        elif member.bot:  # when mention a ramdom bot
            embed = discord.Embed(description=f"{member.mention} is a bot not a slut!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave try to tie self
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to tie himself to a channel! {ctx.author.mention} only a "
                                                  f"Domme can do it!!",
                                      color=0xF2A2C0)

            elif member_is == 2 or member_is == 202:  # Domme tie self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"It's unbearable to see "
                                                  f"a Domme being punished and tied up.",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme ungaging on Free slave
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:  # Domme tie on Owned slave
                channel = channel or ctx.channel
                await action.tie_in_channel(channel.id)
                return

            elif member_is > 300:  # Domme tie on other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave tie on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can tie a slave to a channel when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave tie on Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def untie(self, ctx, member: discord.Member):
        if ctx.author.bot:  # when author is a bot
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        elif member.bot:  # when mention a ramdom bot
            embed = discord.Embed(description=f"{member.mention} is a bot not a slut!",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        else:
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:  # slave try to untie self
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to untie himself from a channel! {ctx.author.mention} only a "
                                                  f"Domme can do it!!",
                                      color=0xF2A2C0)

            elif member_is == 2 or member_is == 202:  # Domme untie self or Domme on Domme
                embed = discord.Embed(title='Nah',
                                      description=f"I am so confused.",
                                      color=0xF2A2C0)

            elif member_is == 201:  # Domme ungaging on Free slave
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:  # Domme untie on Owned slave
                await action.tie_in_channel(0)
                return

            elif member_is > 300:  # Domme untie on other domme's owned slave
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:  # Slave untie on Slave
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can untie a slave from a channel when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:  # slave untie on Domme
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

            await action.react('n')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def rank(self, ctx, member: discord.Member, num: int = 0):
        action = Action(self.bot, ctx, member)
        if ctx.author.bot:  # when author is a bot
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return
        
        elif member.bot:  # when mentioned member is a bot.
            embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                                  color=0xF2A2C0)
        else:
            member_is = who_is(ctx.author, member)
            if member_is in [202, 201] or member_is > 300:  # when domme tries to ranks other slaves
                embed = discord.Embed(description=f"{ctx.author.mention} you can only rank your own slaves.", color=0xF2A2C0)

            elif member_is in [1, 2]:  # self rank
                embed = discord.Embed(description=f"{ctx.author.mention} you can't rank yourself.", color=0xF2A2C0)

            elif member_is == 200:  # ranking ownerd sub.
                await action.rank(num)
                return

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(
                    description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(
                    description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                    color=0xF2A2C0)

            elif member_is == -1:  # when member is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                      color=0xF2A2C0)
            elif member_is < -1:  # when author is bot banned
                embed = discord.Embed(title='Bot ban',
                                      description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{member_is * -1}:F>",
                                      color=0xF2A2C0)

        await action.react('n')
        await ctx.channel.send(embed=embed)

    @commands.command(aliases=['lb'])
    @commands.guild_only()
    async def leaderboard(self, ctx, lb_type='cash'):
        if ctx.author.bot:  # when author is a bot.
            return

        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        if lb_type.lower() not in ['cash', 'line']:
            embed = discord.Embed(tite="wrong options", description="I got only few options\n> **`s.lb cash`**\n> **`s.lb line`**", color=0xFF2030)
            await ctx.channel.send(embed=embed)
            return

        action = Action(self.bot, ctx, ctx.author)
        await action.leaderboard(type=lb_type)

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                 ERRORS                                     #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @own.error
    async def on_own_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.own @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @disown.error
    async def on_disown_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.disown @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @gag.error
    async def on_gag_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.gag @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @badword.error
    async def on_badword_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.badword @mention <bad words>`**"
                                              f"\n> aliases = `word`, `addbadword`, `words`, `badwords`, `addbadwords`",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @removebadword.error
    async def on_removebadword_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.removebadword @mention <bad words>`**"
                                              f"\n> aliases = `removeword`",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @clearbadword.error
    async def on_clearbadword_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.clearbadword @mention`**"
                                              f"\n> aliases = `removeallbadwords`, `clearwords`, `removeallwords`",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @nickname.error
    async def on_nickname_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.nickname @mention <name>`**"
                                              f"\n> aliases = `name`, `nick`",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @status.error
    async def on_status_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.status @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @emojii.error
    async def on_allowemoji_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.emoji @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @tie.error
    async def on_tie_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.tie @mention`**"
                                              f"\nor\n**`s.tie @mention #channel`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @untie.error
    async def on_untie_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.untie @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @rank.error
    async def on_rank_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`s.rank @mention X`** X is the rank of slave",
                                  color=0xFF2030)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Femdom(bot))
