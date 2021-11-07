#!/bin/python3
"""
commands    |   description
----------------------------
lock        |   member will locker role can lock members with slave role
unlock      |   admins and the member who locked the slave can unlock the locked slave from prison
escape      |   if the prisoner has gem then they can use it to escape the prison without lines and get 6h of lockproof


events              |   description
----------------------------
on_message          |   when prisoner sends message bot checks it and gives new line if its correct
on_prisoner_remove  |   unlocks all the prisoner
on_prison_delete    |   deletes the prisoner role and unlocks all the prisoners

Note: a slave can't be locked multiple times without 30 minutes of cooldown in between
"""
import discord
import database
import textwrap
import asyncio
import unicodedata
import re
from random import choice, randint, getrandbits, random
from discord.ext import commands, tasks
from discord_components import *
from PIL import Image, ImageDraw, ImageFont
from string import ascii_letters


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
            if set(database.get_config('locker', member.guild.id)) & set([role.id for role in author.roles]):
                if author.id == member.id:
                    return 2
                if set(database.get_config('locker', member.guild.id)) & set([role.id for role in member.roles]):
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
                if set(database.get_config('locker', member.guild.id)) & set([role.id for role in member.roles]):
                    return 102
                else:
                    return 111
            else:
                return 0
        else:
            return -1
    else:
        return -1 * ban_data[1]


def make_image(sentence, memberid):
    """
    Saves lines png in ./Image with filename coresponding to member's ID
    returns randomly capitalized string.

    Note string includes newline as character
    """
    new_string = ''
    for character in sentence:
        if bool(getrandbits(1)):
            new_string += character.upper()
        else:
            new_string += character.lower()

    img = Image.open('./Image/blank_discord_bg.png')
    font = ImageFont.truetype('./Fonts/LadylikeBB.ttf', 53)
    draw = ImageDraw.Draw(img)
    avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
    max_char_count = int(img.size[0] * .95 / avg_char_width)  # 618
    new_string = textwrap.fill(text=new_string, width=max_char_count)

    draw.text(xy=(img.size[0] / 2, img.size[1] / 2), text=new_string, font=font, fill='#ffffff', anchor='mm')
    img.save(f'./Image/{memberid}.png')
    return new_string


class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.escape_cleanup.start()
        DiscordComponents(bot)

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

    @tasks.loop(seconds=60 * 5)
    async def escape_cleanup(self):
        """
        clears escape and botban DB
        """
        database.clear_escape()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        gives back all the roles of member when prisoner role is removed from member or when role gets deleted.
        """
        prisoner = before.guild.get_role(database.get_config('prisoner', before.guild.id)[0])
        if prisoner is not None:
            if set([prisoner.id]) & set([role.id for role in before.roles]) and not (set([prisoner.id]) & set([role.id for role in after.roles])):
                roles = database.release_prison(after.id, after.guild.id)
                if roles != [0]:
                    for role in roles:
                        r = after.guild.get_role(role)
                        await after.add_roles(r)
                    await after.send(f"You are now released from <#{database.get_config('prison', before.guild.id)[0]}> of {after.guild.name}")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """
        when new channel is created, bot added prisoner role to the channel.
        if prisoner role is not found bot creates it and add it to all channel.
        """
        prisoner = channel.guild.get_role(database.get_config('prisoner', channel.guild.id)[0])
        if prisoner is None:
            prisoner = await channel.guild.create_role(name='Prisoner', color=0x591B32)
            database.insert_config('prisoner', channel.guild.id, prisoner.id)
            channels = await channel.guild.fetch_channels()
            for ch in channels:
                await ch.set_permissions(prisoner, view_channel=False, send_messages=False)
            prison = channel.guild.get_channel(database.get_config('prison', channel.guild.id)[0])
            if prison is not None:
                await prison.set_permissions(prisoner, view_channel=True, send_messages=True, read_message_history=True)
        await channel.set_permissions(prisoner, view_channel=False, send_messages=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        if author have prisoner role checks if its correct line and updates prison DB
        there is 10% of lossing 2 coins on every wrong lines
        """
        if message.author.bot:
            return

        if set(database.get_config('prisoner', message.guild.id)) & set([role.id for role in message.author.roles]):
            data = database.get_prisoner(message.author.id, message.guild.id)
            if message.content == data[4]:
                await message.add_reaction(emoji='YES:897762486042910762')
                await message.add_reaction(emoji='pinkcoin:900000697288892416')
                sentence = make_image(message.content, message.author.id).replace('\n', ' ')
                sentence = sentence.replace('  ', ' ')
                database.update_lock(message.author.id, sentence, message.guild.id)
                if data[3] == 1:
                    prisoner = message.guild.get_role(database.get_config('prisoner', message.guild.id)[0])
                    await message.author.remove_roles(prisoner)
                    await message.reply(f"{message.author.mention} you are now released from {message.channel.mention} for being a good boy and writing the lines.")
                    database.insert_escape(message.author.id, message.guild.id, 0.2, 'cooldown')
                    return
                if message.author.id == 855057142297264139:
                    await message.author.send(sentence)
                prison = message.guild.get_channel(database.get_config('prison', message.guild.id)[0])
                await prison.send(f"{message.author.mention} you have to write :point_down: {int(data[3] - 1)} times to be free or you have to wait 2h or use **`s.escape`** to be free from prison. ||(it is case sensitive)||")
                await prison.send(file=discord.File(f'./Image/{message.author.id}.png'))
            else:
                await message.add_reaction(emoji='NO:897890789202493460')
                if random() < 0.1:
                    database.remove_money(message.author.id, message.guild.id, 2, 0)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """
        deletes prisoner role of prison channel is deleted to release all prisoner from prison
        """
        if channel.id == database.get_config('prison', channel.guild.id)[0]:
            prisoner = channel.guild.get_role(database.get_config('prisoner', channel.guild.id)[0])
            await prisoner.delete()

    @commands.command()
    @commands.guild_only()
    # @commands.cooldown(2, 3 * 60 * 60, commands.BucketType.user)
    async def lock(self, ctx, member: discord.Member):
        """
        the might lock command which brings chaos to servers
        """
        if ctx.author.bot:  # returns if the author is a bot
            return

        if member.bot:  # if the mentioned member is a bot
            member_bot_embed = discord.Embed(title='Nah.', description=f"Bots are too powerful you can't lock them.", color=0xF2A2C0)
            await ctx.reply(embed=member_bot_embed)
            return

        if not database.is_config(ctx.guild.id):  # if the server is not configured
            need_setup_embed = discord.Embed(title='I am not ready yet.',
                                                 description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                                 color=0xF2A2C0)
            await ctx.reply(embed=need_setup_embed)
            return

        if ctx.author.id in database.get_blacklist(ctx.guild.id):  # if the author is a blacklisted member
            await ctx.reply('you are blacklisted by the Admins ¯\\_(ツ)_/¯')
            return

        if set(database.get_config('prisoner', ctx.guild.id)) & set([role.id for role in member.roles]):  # if the mentioned member already having prisoner role.
            embed = discord.Embed(title='Already suffering',
                                  description=f"{member.mention} is already suffering in <#{database.get_config('prison', ctx.guild.id)[0]}>",
                                  color=0xF2A2C0)
            await ctx.reply(embed=embed)
            return

        is_escaped = database.is_escaped(member.id, ctx.guild.id)
        if is_escaped is not None:  # if the member is under gem cooldown or 30 mins cooldown.
            if is_escaped[3] == 'gem':
                embed = discord.Embed(title='Magic Gem is Real',
                                      description=f"{member.mention} used the power of Magic Gem<a:gems:899985611946078208> "
                                      f"to be free, Magic Gem's Power will deteriorate <t:{is_escaped + (5 * 60)}:R>.\n> *patience is a virtue*",
                                      color=0xF47FFF)
            elif is_escaped[3] == 'cooldown':
                embed = discord.Embed(title='Cooldown',
                                      description=f'{ctx.author.mention} you can lock {member.mention} <t:{is_escaped[2]}:R>',
                                      color=0xF47FFF)
            await ctx.reply(embed=embed)
            return

        member_is = who_is(ctx.author, member)  # checking relationship between author and member

        if member_is in [2, 202]:
            lock_domme_embed = discord.Embed(title='Nah',
                                             description=f"Only Subs can be locked in punished in <#{database.get_config('prison', ctx.guild.id)[0]}>",
                                             color=0xF2A2C0)
            await ctx.reply(embed=lock_domme_embed)

        elif member_is in [1, 101, 102]:
            lock_slave_embed = discord.Embed(title='Pathetic…',
                                             description=f"{ctx.author.mention} you are not worthy to use this command.",
                                             color=0xF2A2C0)
            await ctx.reply(embed=lock_slave_embed)

        elif member_is in [201, 200] or member_is > 300:
            def check(res):
                return ctx.author == res.user and res.channel == ctx.channel

            if not database.get_money(ctx.author.id, ctx.guild.id)[3] > 0:  # checking if author has gems
                no_gem_embed = discord.Embed(title='No Gems',
                                             description=f"{ctx.author.mention} you don't have gems to lock {member.mention}",
                                             color=0xF2A2C0)
                await ctx.reply(embed=no_gem_embed)
                return

            prison = ctx.guild.get_channel(database.get_config('prison', ctx.guild.id)[0])
            prisoner = ctx.guild.get_role(database.get_config('prisoner', ctx.guild.id)[0])
            
            if prisoner is None:  # if prisoner role is deleted makes a new prisoner role and configures it
                prisoner = await ctx.guild.create_role(name='Prisoner', color=0x591B32)
                database.insert_config('prisoner', ctx.guild.id, prisoner.id)
                channels = await ctx.guild.fetch_channels()
                for channel in channels:
                    await channel.set_permissions(prisoner, view_channel=False, send_messages=False)
                await prison.set_permissions(prisoner, view_channel=True, send_messages=True, read_message_history=True)

            embed = discord.Embed(title='What should this slave do while he is in prison?', color=0x9479ED)
            timeout_embed = discord.Embed(title='Time is over the slave escaped from prison', color=0x9479ED)

            m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.green, label="Praise", emoji='🛐'),
                                                            Button(style=ButtonStyle.red, label='Degrade', emoji='🙇‍♂️'),
                                                            Button(style=ButtonStyle.blue, label='Custom Lines', emoji='✍️',)]])
            try:
                response = await self.bot.wait_for('button_click', timeout=30, check=check)
                if response.component.label == 'Praise':
                    await response.respond(type=6)
                    with open('Text_files/praise.txt', 'r') as praise:
                        lines = praise.read().splitlines()
                        sentence = choice(lines)

                elif response.component.label == 'Degrade':
                    await response.respond(type=6)
                    with open('Text_files/degrade.txt', 'r') as degrade:
                        lines = degrade.read().splitlines()
                        sentence = choice(lines)

                elif response.component.label == 'Custom Lines':
                    await response.respond(type=6)

                    def check_m(res):
                        return ctx.author == res.author and res.channel == ctx.channel

                    embed = discord.Embed(title='Type the Custom line.',
                                            description='not more that 120 characters', color=0x9479ED)
                    await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label="Praise", emoji='🛐', disabled=True),
                                                            Button(style=ButtonStyle.red, label='Degrade', emoji='🙇‍♂️', disabled=True),
                                                            Button(style=ButtonStyle.blue, label='Custom Lines', emoji='✍️', disabled=True)]])
                    try:
                        response = await self.bot.wait_for('message', timeout=120, check=check_m)
                        sentence = response.content
                        if len(sentence) > 125:
                            embed = discord.Embed(title='Not more than 120 characters',
                                                    description=f'{ctx.author.mention} failed to lock {member.mention}', color=0xFF2030)
                            await m.edit(embed=embed)
                            return
                        await response.delete()

                    except asyncio.TimeoutError:
                        await m.edit(embed=timeout_embed)
                        return

                embed = discord.Embed(title='Which level of torture do you prefer?', color=0x9479ED)
                await m.edit(embed=embed, components=[[Button(style=ButtonStyle.green, label='Easy'),
                                                        Button(style=ButtonStyle.blue, label='Medium'),
                                                        Button(style=ButtonStyle.red, label='Hard')]])

                try:
                    response = await self.bot.wait_for('button_click', timeout=30, check=check)
                    if response.component.label == 'Easy':
                        num = randint(2, 3)
                    elif response.component.label == 'Medium':
                        num = randint(3, 5)
                    elif response.component.label == 'Hard':
                        num = randint(7, 10)
                    await response.respond(type=6)
                    await m.delete()
                except asyncio.TimeoutError:
                    await m.edit(embed=timeout_embed)
                    return
            except asyncio.TimeoutError:
                await m.edit(embed=timeout_embed)
                return
            roles = "".join([str(role.id) for role in member.roles][1:])
            try:
                roles = roles.replace(str(ctx.guild.premium_subscriber_role.id), '')
            except AttributeError:
                pass
            i_have_power = ctx.guild.get_member(self.bot.user.id).top_role > member.top_role and ctx.guild.owner.id != member.id
            if i_have_power:  # starts to locking the member
                embed = discord.Embed(description=f"I am locking {member.mention} <a:loading:903864796418564188>",
                                      color=0xFF2030)
                m = await ctx.send(embed=embed)
                for role in member.roles:
                    if role != ctx.guild.default_role and role != ctx.guild.premium_subscriber_role:
                        await member.remove_roles(role)

                database.remove_money(ctx.author.id, ctx.guild.id, 0, 10)

                await member.add_roles(prisoner)
                domme_name = re.sub('[^A-Za-z0-9]+', ' ', unicodedata.normalize('NFD', ctx.author.nick or ctx.author.name).encode('ascii', 'ignore').decode('utf-8')).lower()
                sub_name = re.sub('[^A-Za-z0-9]+', ' ', unicodedata.normalize('NFD', member.nick or member.name).encode('ascii', 'ignore').decode('utf-8')).lower()
                sentence = sentence.replace('#domme', domme_name)
                sentence = sentence.replace('#slave', sub_name)
                sentence = make_image(sentence, member.id).replace('\n', ' ')
                sentence = sentence.replace('  ', ' ')
                embed = discord.Embed(description=f"{ctx.author.mention} received 20<a:pinkcoin:900000697288892416> by locking {member.mention} in {prison.mention}",
                                      color=0x9479ED)
                await m.edit(embed=embed)
                await prison.send(f"{member.mention} you have to write :point_down: {num} times to be free or you have to wait 2h or use **`s.escape`** to be free from prison. ||(it is case sensitive)||")
                await prison.send(file=discord.File(f'./Image/{member.id}.png'))
                database.lock(member.id, ctx.guild.id, ctx.author.id, num, sentence, roles)
                database.add_money(ctx.author.id, ctx.guild.id, 20, 0)
                
                if member.id in [855057142297264139]:
                    await member.send(sentence)
                await asyncio.sleep(60 * 60 * 2)                
                if prisoner.id in [role.id for role in member.roles]:
                    await member.remove_roles(prisoner)
                    database.insert_escape(ctx.author.id, ctx.guild.id, 0.5, 'cooldown')

            else:  # I have no power
                no_power_embed = discord.Embed(title='I don\'t have power',
                                                description=f'{member.mention} might be server owner or having higher role than me <:crypanda:897832575698075688>',
                                                color=0xFF2030)
                await ctx.send(embed=no_power_embed)

        elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
            embed = discord.Embed(description=f"{member.mention} should have any of the following roles \n"
                                  f"{self.list_roles(database.get_config('locker', member.guild.id))}\n"
                                  f"{self.list_roles(database.get_config('slave', member.guild.id))}",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        elif member_is == 0:  # when the author doesn't have domme or slave role.
            embed = discord.Embed(description=f"{ctx.author.mention}, you should have any of the following roles \n"
                                  f"{self.list_roles(database.get_config('locker', member.guild.id))}\n"
                                  f"{self.list_roles(database.get_config('slave', member.guild.id))}",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)
            
        elif member_is == -1:  # when member is bot banned
            embed = discord.Embed(description=f"{member.mention} is banned from using {self.bot.user.mention}",
                                  color=0xF2A2c0)
            await ctx.send(embed=embed)
        
        elif member_is < -1:  # when author is bot banned
            embed = discord.Embed(description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{-1 * member_is}:F>",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def unlock(self, ctx, member: discord.Member):
        """
        unlock command unlocks prisoner and sets them free
        """
        if ctx.author.bot:  # returns if the author is a bot
            return

        if not set(database.get_config('prisoner', ctx.guild.id)) & set([role.id for role in member.roles]) or member.bot:  # if member does not have prisoner role
            embed = discord.Embed(title='Already Free', description=f"{member.mention} is already in woods enjoying the sun.", color=0xF2A2C0)
            await ctx.reply(embed=embed)
            return

        member_is = who_is(ctx.author, member)
        prisoner = ctx.guild.get_role(database.get_config('prisoner', ctx.guild.id)[0])
        
        if member_is < -1: #  if author is bot banned
            embed = discord.Embed(description=f"{ctx.author.mention} you are banned from {self.bot.user.nick or self.bot.user.name} till <t:{-1 * member_is}:F>",
                                  color=0xF2A2C0)
            await ctx.reply(embed=embed)

        elif member_is in [2, 202]:  # when locker is self unlocking or unlocking a locker.
            embed = discord.Embed(description=f"{member.mention} is free in Woods enjoying the sun, nobody can lock the Domme.", color=0xF2A2C0)
            await ctx.reply(embed=embed)

        elif member_is in [222] or ctx.author.guild_permissions.administrator: #  locker/admin unlocking a slave
            domme = database.get_prisoner(member.id, ctx.guild.id)[2]
            if ctx.author.id == int(domme) or ctx.author.guild_permissions.administrator:
                await member.remove_roles(prisoner)
                embed = discord.Embed(description=f'{member.mention} is free now, released by {ctx.author.mention}', color=0xF2A2C0)
                await ctx.reply(embed=embed)
            else: 
                embed = discord.Embed(title='Nah', description=f"Only <@{domme}> or the Admins can set {member.mention} free.", color=0xF2A2C0)
                await ctx.reply(embed=embed)

        else:
            unlock_slave_embed = discord.Embed(title='Pathetic…',
                                               description=f"you are not worthy to use this command.",
                                               color=0xF2A2C0)
            await ctx.reply(embed=unlock_slave_embed)

    @commands.command()
    @commands.guild_only()
    async def escape(self, ctx):
        """
        this command will enable prisoner to escape from prison and grand 6h of protection.
        """
        if ctx.author.bot:
            return

        if not set(database.get_config('prisoner', ctx.guild.id)) & set([role.id for role in ctx.author.roles]):  # if author does not have prisoner role
            embed = discord.Embed(title='Already Free', description=f"{ctx.author.mention} is already in woods enjoying the sun.", color=0xF2A2C0)
            await ctx.reply(embed=embed)
            return

        if database.get_money(ctx.author.id, ctx.guild.id)[3] != 0 or ctx.author.id == 855057142297264139:  # if prisoner have gems
            if ctx.author.id != 855057142297264139:
                database.remove_money(ctx.author.id, ctx.guild.id, 0, 10)
            prisoner = ctx.guild.get_role(database.get_config('prisoner', ctx.guild.id)[0])
            await ctx.author.remove_roles(prisoner)
            embed = discord.Embed(description=f"{ctx.author.mention} was lucky to have a magic gem <a:gems:899985611946078208> and escaped from {ctx.channel.mention}", color=0xF2A2C0)
            await ctx.send(embed=embed)
            database.insert_escape(ctx.author.id, ctx.guild.id, 6, 'gem')
        else:  # if prisoner does not have a gem
            embed = discord.Embed(description=f"{ctx.author.mention} you don't have magic gem <a:gems:899985611946078208> to be free.", color=0xF2A2C0)
            await ctx.reply(embed=embed)

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                  ERRORS                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @lock.error
    async def on_lock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(title='How to use Prison?', description=f"Usage:\n> **`s.lock @mention`** "
                                  f"\nAfter it just enjoy the slave punishment!",
                                  color=0xFF2030)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Prison Cooldown is 3h",
                                  description="{} you need to wait {:,.1f} minutes to lock a slave again.".format(ctx.author.mention, (error.retry_after // 60) + 1),
                                  color=0xFF2030)
        await ctx.send(embed=embed)

    @unlock.error
    async def on_unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(title='How to save a slave from Prison?', description=f"Usage:\n> **`s.unlock @mention`** ",
                                  color=0xFF2030)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Lock(bot))
