#!/bin/python3
import database
import discord
import asyncio
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
        if isinstance(roles, list):
            role = '>'
            for r in roles:
                role = f"{role} <@&{r}>\n>"
            return role[:-2]
        else:
            return roles

    async def react(self, y_n):
        if y_n == 'yes' or y_n == 'y':
            await self.ctx.message.add_reaction(emoji='YES:897762486042910762')
        elif y_n == 'no' or y_n == 'n':
            await self.ctx.message.add_reaction(emoji='NO:897890789202493460')

    async def chastity(self, access, temp=False):
        channels = await self.ctx.guild.fetch_channels()
        for channel in channels:
            if channel.is_nsfw():
                if access:
                    await channel.set_permissions(self.member, overwrite=None)
                    database.update_slaveDB(self.member.id, 'chastity', True, self.ctx.guild.id)
                else:
                    await channel.set_permissions(self.member, view_channel=False)
                    database.update_slaveDB(self.member.id, 'chastity', False, self.ctx.guild.id)
        if temp:
            await asyncio.sleep(1 * 60 * 60)
            for channel in channels:
                if channel.is_nsfw():
                    await channel.set_permissions(self.member, overwrite=None)
                    database.update_slaveDB(self.member.id, 'chastity', True, self.ctx.guild.id)

    async def muff(self, access):
        channels = await self.ctx.guild.fetch_channels()
        for channel in channels:
            if isinstance(channel, discord.channel.VoiceChannel):
                if access:
                    await channel.set_permissions(self.member, overwrite=None)
                    database.update_slaveDB(self.member.id, 'muff', False, self.ctx.guild.id)
                else:
                    await channel.set_permissions(self.member, connect=False)
                    database.update_slaveDB(self.member.id, 'muff', True, self.ctx.guild.id)

    async def blind(self):
        channels = await self.ctx.guild.fetch_channels()
        for channel in channels:
            await channel.set_permissions(self.member, view_channel=False, send_messages=False)
        await self.member.send(f"you are blindfolded in the server **{self.ctx.guild.name}** for 5 minutes.")
        await asyncio.sleep(5 * 60)
        for channel in channels:
            await channel.set_permissions(self.member, overwrite=None)


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

    @commands.command()
    @commands.guild_only()
    async def chastity(self, ctx, member: discord.Member):
        if ctx.author.bot:
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`t.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return
        
        if member.bot:
            if member.id == self.bot.user.id:
                embed = discord.Embed(title='Nah',
                                      description=f"You can't deny my cum permission, I will cum all day long and you can't stop me.<:devilpanda:897834095474778153>",
                                      color=0xF2A2C0)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Nah',
                                      description=f"You can't keep Bots in chastity.",
                                      color=0xF2A2C0)
                await ctx.send(embed=embed)
        else:
            if member.guild_permissions.administrator:
                embed = discord.Embed(description=f"{member.mention} have administrator permission, I am sorry.", color=0xF2A2C0)
                await ctx.reply(embed=embed)
                return
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to be in chastity!, {ctx.author.mention} you can't "
                                      f"do anything without Domme's permission.",
                                      color=0xF2A2C0)
            elif member_is == 2 or member_is == 202:
                embed = discord.Embed(title='Nah',
                                      description=f"I am sorry {ctx.author.mention}, but I can't do such a thing. It's unbearable to see "
                                                  f"a Domme in chastity.",
                                      color=0xF2A2C0)

            elif member_is == 201:
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:
                embed = discord.Embed(title='So what should I do?', color=0xF2A2C0)
                m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.green, label='Chastity Unlock', emoji='🔓', disabled=database.get_slave_from_DB(member.id, ctx.guild.id)[0][6]),
                                                              Button(style=ButtonStyle.red, label='Chastity Lock', emoji='🔒', disabled=not database.get_slave_from_DB(member.id, ctx.guild.id)[0][6])]])
                try:
                    def check(res):
                        return ctx.author == res.user and res.channel == ctx.channel

                    response = await self.bot.wait_for('button_click', timeout=30, check=check)
                    await response.respond(type=6)
                    if response.component.label == 'Chastity Lock':
                        embed = discord.Embed(description=f"{member.mention} can't access NSFW Channels in this server.", color=0xFF2030)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Chastity Unlock', emoji='🔓', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Chastity Lock', emoji='🔒', disabled=True)]])
                        await action.chastity(False)

                    elif response.component.label == 'Chastity Unlock':
                        embed = discord.Embed(description=f"{member.mention} can access NSFW Channels in this server.", color=0x08FF08)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Chastity Unlock', emoji='🔓', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Chastity Lock', emoji='🔒', disabled=True)]])
                        await action.chastity(True)

                except asyncio.TimeoutError:
                    embed = discord.Embed(description='Time\'s up, you got only 30 secs to make a choice.', color=0xF2A2C0)
                    await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Chastity Unlock', emoji='🔓', disabled=True),
                                                           Button(style=ButtonStyle.red, label='Chastity Lock', emoji='🔒', disabled=True)]])
                return

            elif member_is > 300:
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can chastity lock when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
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
    async def muffs(self, ctx, member: discord.Member):
        if ctx.author.bot:
            return
        
        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`t.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return
        
        if member.bot:
            embed = discord.Embed(title='Nah',
                                  description=f"{member.mention} is bot don't be dumb like Shaman.",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
        else:
            if member.guild_permissions.administrator:
                embed = discord.Embed(description=f"{member.mention} have administrator permission, I am sorry.", color=0xF2A2C0)
                await ctx.reply(embed=embed)
                return
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to cover ears!, {ctx.author.mention} you can't "
                                      f"do anything without Domme's permission.",
                                      color=0xF2A2C0)
            elif member_is == 2 or member_is == 202:
                embed = discord.Embed(title='Nah',
                                      description=f"I am sorry {ctx.author.mention}, but I can't do such a thing. It's unbearable to see "
                                                  f"a Domme suffering.",
                                      color=0xF2A2C0)

            elif member_is == 201:
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:
                embed = discord.Embed(title='So what should I do?', color=0xF2A2C0)
                m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.green, label='Remove Ear Muffs', disabled=database.get_slave_from_DB(member.id, ctx.guild.id)[0][7]),
                                                              Button(style=ButtonStyle.red, label='Give Ear Muffs', disabled=not database.get_slave_from_DB(member.id, ctx.guild.id)[0][7])]])
                try:
                    def check(res):
                        return ctx.author == res.user and res.channel == ctx.channel

                    response = await self.bot.wait_for('button_click', timeout=30, check=check)
                    await response.respond(type=6)
                    if response.component.label == 'Give Ear Muffs':
                        embed = discord.Embed(description=f"{member.mention} can't connect to any Voice Channels in this server.", color=0xFF2030)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Remove Ear Muffs', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Give Ear Muffs', disabled=True)]])
                        await action.muff(False)
                        database.update_slaveDB(member.id, 'muff', False, ctx.guild.id)

                    elif response.component.label == 'Remove Ear Muffs':
                        embed = discord.Embed(description=f"{member.mention} can connect to Voice Channels in this server.", color=0x08FF08)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Remove Ear Muffs', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Give Ear Muffs', disabled=True)]])
                        await action.muff(True)
                        database.update_slaveDB(member.id, 'muff', True, ctx.guild.id)
                except asyncio.TimeoutError:
                    embed = discord.Embed(description='Time\'s up, you got only 30 secs to make a choice.', color=0xF2A2C0)
                    await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Remove Ear Muffs', disabled=True),
                                                           Button(style=ButtonStyle.red, label='Give Ear Muffs', disabled=True)]])
                return

            elif member_is > 300:
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can Ear Muff someone when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\n I need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:
                embed = discord.Embed(title=f'You shall not try such thing!',
                                      description=f'{ctx.author.mention}, you are a slave, you are not as powerful as a domme and you '
                                                  f'will never be! How could you even consider trying something s'
                                                  f'o foolish!! {member.mention} I think someone needs to learn a lesson!!!, brainless slave',
                                      color=0xFF2030)

            elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
                embed = discord.Embed(description=f"{member.mention} should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
                                      color=0xF2A2C0)

            elif member_is == 0:  # when the author doesn't have domme or slave role.
                embed = discord.Embed(description=f"{ctx.author.mention}, you should have any of the following roles \n{self.list_roles(database.get_config('domme', member.guild.id))}\n{self.list_roles(database.get_config('slave', member.guild.id))}",
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
    @commands.cooldown(3, 4 * 60 * 60, commands.BucketType.user)
    async def blind(self, ctx, member: discord.Member):
        if ctx.author.bot:
            return

        if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
            embed = discord.Embed(title='I am not ready yet.',
                                  description=f"Ask the Admins to run the command **`t.setup`** and try again",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            return

        if member.bot:
            if member.id == self.bot.user.id:
                embed = discord.Embed(title='Nah',
                                      description=f"You can't blindfold me, my eyes are powerful I see everything.",
                                      color=0xF2A2C0)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Nah',
                                      description=f"You can't blindfold Bots.",
                                      color=0xF2A2C0)
                await ctx.send(embed=embed)
        else:
            if member.guild_permissions.administrator:
                embed = discord.Embed(description=f"{member.mention} have administrator permission, I am sorry.", color=0xF2A2C0)
                await ctx.reply(embed=embed)
                return
            action = Action(self.bot, ctx, member)
            member_is = who_is(ctx.author, member)
            if member_is == 1:
                embed = discord.Embed(title='Pathetic...',
                                      description=f"Pathetic!!, This simpleton slave is trying to blindfold!, {ctx.author.mention} you can't "
                                      f"do anything without Domme's permission.",
                                      color=0xF2A2C0)
            elif member_is == 2 or member_is == 202:
                embed = discord.Embed(title='Nah',
                                      description=f"I am sorry {ctx.author.mention}, but I can't do such a thing. It's unbearable to see "
                                                  f"a Domme blindfolded.",
                                      color=0xF2A2C0)

            elif member_is == 201:
                embed = discord.Embed(title='Nah',
                                      description=f"{ctx.author.mention}, you can't do such a thing. {member.mention} is a free slave!"
                                                  f" the sub must be owned by you.",
                                      color=0xF2A2C0)

            elif member_is == 200:
                embed = discord.Embed(title='Are you sure that you wanna do this?', description=f"{member.mention} will not be able to see any channels in this server for 5 mins.", color=0xF2A2C0)
                m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.green, label='No'),
                                                              Button(style=ButtonStyle.red, label='Yes do it')]])
                try:
                    def check(res):
                        return ctx.author == res.user and res.channel == ctx.channel

                    response = await self.bot.wait_for('button_click', timeout=30, check=check)
                    await response.respond(type=6)
                    if response.component.label == 'Yes do it':
                        embed = discord.Embed(description=f"{member.mention} can't see any of the Channels in this server for next 5 mins.", color=0xFF2030)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='No', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Yes do it', disabled=True)]])
                        await action.blind()

                    elif response.component.label == 'No':
                        embed = discord.Embed(description=f"Mission Aborted. lucky {member.mention}", color=0x08FF08)
                        await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='No', disabled=True),
                                                               Button(style=ButtonStyle.red, label='Yes do it', disabled=True)]])

                except asyncio.TimeoutError:
                    embed = discord.Embed(description='Time\'s up, you got only 30 secs', color=0xF2A2C0)
                    await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='No', disabled=True),
                                                           Button(style=ButtonStyle.red, label='Yes do it', disabled=True)]])
                return

            elif member_is > 300:
                embed = discord.Embed(title='Nah',
                                      description=f"{member.mention} is owned by <@{member_is}> it's her property.",
                                      color=0xFF2030)

            elif member_is == 101:
                embed = discord.Embed(title='Pathetic...',
                                      description=f"You foolish slave. You think you can blindfold someone when you are a slave, {ctx.author.mention}! "
                                                  f"how Pathetic!!!\nI need to tell this joke to Deity, she will love it.",
                                      color=0xF2A2C0)

            elif member_is == 102:
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

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                 ERRORS                                     #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @chastity.error
    async def on_chastity_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`t.chastity @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @muffs.error
    async def on_muff_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n**`t.muffs @mention`**",
                                  color=0xFF2030)
            await ctx.send(embed=embed)

    @blind.error
    async def on_blind_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(description=f"Usage:\n> **`t.blind @mention`** ",
                                  color=0xFF2030)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Blindfold Cooldown is 4h",
                                  description="{} you need to wait {:,.1f} minutes to blindfold a slave again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Femdom(bot))
