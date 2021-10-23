#!/bin/python3
import discord
import database
import textwrap
import asyncio
from random import choice, randint, getrandbits
from discord.ext import commands
from discord_components import *
from PIL import Image, ImageDraw, ImageFont
from string import ascii_letters


def who_is(author, member):
    if database.get_config('locker', member.guild.id) == [0]:
        return -1
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


def make_image(sentence):
    new_string = ''
    for character in sentence:
        if bool(getrandbits(1)):
            new_string += character.upper()
        else:
            new_string += character.lower()

    img = Image.open('./Image/blank_discord_bg.png')
    font = ImageFont.truetype('./Fonts/arial.ttf', 30)
    draw = ImageDraw.Draw(img)
    avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
    max_char_count = int(img.size[0] * .95 / avg_char_width)  # 618
    new_string = textwrap.fill(text=new_string, width=max_char_count)

    draw.text(xy=(img.size[0] / 2, img.size[1] / 2), text=new_string, font=font, fill='#ffffff', anchor='mm')
    img.save('./Image/new.png')
    return new_string


class Lock(commands.Cog):
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
    async def on_member_update(self, before, after):
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
        prisoner = database.get_config('prisoner', channel.guild.id)
        if prisoner == [0] or channel.guild.get_role(int(prisoner[0])) is None:
            prisoner = await channel.guild.create_role(name='Prisoner', color=0x591B32)
            database.insert_config('prisoner', channel.guild.id, prisoner.id)
            channels = await channel.guild.fetch_channels()
            for channel in channels:
                await channel.set_permissions(prisoner, view_channel=False, send_messages=False)
            prison = channel.guild.get_channel(database.get_config('prison', message.guild.id)[0])
            if prison is not None:
                await prison.set_permissions(prisoner, view_channel=True, send_messages=True, read_message_history=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if set(database.get_config('prisoner', message.guild.id)) & set([role.id for role in message.author.roles]):
            data = database.get_prisoner(message.author.id, message.guild.id)
            if message.content == data[4]:
                await message.add_reaction(emoji='YES:897762486042910762')
                await message.add_reaction(emoji='pinkcoin:900000697288892416')
                sentence = make_image(message.content).replace('\n', ' ')
                sentence = sentence.replace('  ', ' ')
                database.update_lock(message.author.id, sentence, message.guild.id)
                if data[3] == 1:
                    prisoner = message.guild.get_role(database.get_config('prisoner', message.guild.id)[0])
                    await message.author.remove_roles(prisoner)
                    database.add_money(message.author.id, message.guild.id, 70, 0)
                    await message.reply(f"{message.author.mention} received 70 <a:pinkcoin:900000697288892416> for being a good boy and writing the lines.")
                    return
                if message.author.id == 855057142297264139:
                    await message.author.send(sentence)
                prison = message.guild.get_channel(database.get_config('prison', message.guild.id)[0])
                await prison.send(f"{message.author.mention} you have to write :point_down: {int(data[3] - 1)} times to be free or you have to wait 2h or use **`s.escape`** to be free from prison. ||(it is case sensitive)||")
                await prison.send(file=discord.File('./Image/new.png'))
            else:
                await message.add_reaction(emoji='NO:897890789202493460')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if channel.id == database.get_config('prison', channel.guild.id)[0]:
            prisoner = channel.guild.get_role(database.get_config('prisoner', channel.guild.id)[0])
            await prisoner.delete()

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(3, 2 * 60 * 60, commands.BucketType.user)
    async def lock(self, ctx, member: discord.Member):
        if ctx.author.bot:
            return

        if member.bot:
            member_bot_embed = discord.Embed(title='Nah.', description=f"Bots are too powerful you can't lock them.", color=0xF2A2C0)
            await ctx.reply(embed=member_bot_embed)
            return

        if ctx.author.id in database.get_blacklist(ctx.guild.id):
            await ctx.reply('you are blacklisted by the Admins ¯\\_(ツ)_/¯')
            return

        if set(database.get_config('prisoner', ctx.guild.id)) & set([role.id for role in member.roles]):
            embed = discord.Embed(title='Already suffering',
                                  description=f"{member.mention} is already suffering in <#{database.get_config('prison', ctx.guild.id)[0]}>",
                                  color=0xF2A2C0)
            await ctx.reply(embed=embed)
            return

        member_is = who_is(ctx.author, member)

        if member_is in [2, 202]:
            lock_domme_embed = discord.Embed(title='Nah',
                                             description=f"Only Subs can be locked in punished in <#{database.get_config('prison', ctx.guild.id)[0]}>",
                                             color=0xF2A2C0)
            await ctx.reply(embed=lock_domme_embed)

        elif member_is in [1, 101, 102]:
            lock_slave_embed = discord.Embed(title='Pathetic…',
                                             description=f"you are not worthy to use this command, how can you even to do such things you stupid bitch.",
                                             color=0xF2A2C0)
            await ctx.reply(embed=lock_slave_embed)

        elif member_is in [201, 200, -1] or member_is > 300:
            def check(res):
                return ctx.author == res.user and res.channel == ctx.channel

            # checking if prison channel exist
            prison = ctx.guild.get_channel(database.get_config('prison', ctx.guild.id)[0])

            if prison is None or member_is == -1:
                need_setup_embed = discord.Embed(title='I am not ready yet.',
                                                 description=f"Ask the Admins to run the command **`s.setup`** and try again",
                                                 color=0xF2A2C0)
                await ctx.reply(embed=need_setup_embed)
            else:
                # checking if prisoner role exist if not creates it.
                prisoner = database.get_config('prisoner', ctx.guild.id)
                if prisoner == [0] or ctx.guild.get_role(int(prisoner[0])) is None:
                    prisoner = await ctx.guild.create_role(name='Prisoner', color=0x591B32)
                    database.insert_config('prisoner', ctx.guild.id, prisoner.id)
                    channels = await ctx.guild.fetch_channels()
                    for channel in channels:
                        await channel.set_permissions(prisoner, view_channel=False, send_messages=False)
                    await prison.set_permissions(prisoner, view_channel=True, send_messages=True, read_message_history=True)
                else:
                    prisoner = ctx.guild.get_role(prisoner[0])

                embed = discord.Embed(title='What should this slave do while he is in prison?', color=0x9479ED)
                timeout_embed = discord.Embed(title='Time is over the slave escaped from prison', color=0x9479ED)
                m = await ctx.reply(embed=embed, components=[[Button(style=ButtonStyle.green, label="Praise", emoji='🛐'),
                                                              Button(style=ButtonStyle.red, label='Degrade', emoji='🙇‍♂️')]])
                try:
                    response = await self.bot.wait_for('button_click', timeout=30, check=check)
                    if response.component.label == 'Praise':
                        with open('Text_files/praise.txt', 'r') as praise:
                            lines = praise.read().splitlines()
                            sentence = choice(lines)
                    elif response.component.label == 'Degrade':
                        with open('Text_files/degrade.txt', 'r') as degrade:
                            lines = degrade.read().splitlines()
                            sentence = choice(lines)
                    await response.respond(type=6)
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
                roles = roles.replace(str(ctx.guild.premium_subscriber_role.id), '')
                i_have_power = ctx.guild.get_member(self.bot.user.id).top_role > member.top_role and ctx.guild.owner.id != member.id
                if i_have_power:
                    for role in member.roles:
                        if role != ctx.guild.default_role and role != ctx.guild.premium_subscriber_role:
                            await member.remove_roles(role)

                    await member.add_roles(prisoner)
                    sentence = sentence.replace('#domme', ctx.author.nick or ctx.author.name)
                    sentence = sentence.replace('#slave', member.nick or member.name)
                    sentence = make_image(sentence).replace('\n', ' ')
                    sentence = sentence.replace('  ', ' ')
                    embed = discord.Embed(description=f"{member.mention} is locked in prison by {ctx.author.mention}.", color=0x9479ED)
                    await ctx.channel.send(embed=embed)
                    await prison.send(f"{member.mention} you have to write :point_down: {num} times to be free or you have to wait 2h or use **`s.escape`** to be free from prison. ||(it is case sensitive)||")
                    await prison.send(file=discord.File('./Image/new.png'))

                    database.lock(member.id, ctx.guild.id, ctx.author.id, num, sentence, roles)
                    database.add_money(ctx.author.id, ctx.guild.id, 20, 0)
                    points_embed = discord.Embed(description=f"{ctx.author.mention} received 20<a:pinkcoin:900000697288892416> by locking {member.mention} in {prison.mention}", color=0xF2A2C0)
                    await ctx.send(embed=points_embed)
                    if member.id == 855057142297264139:
                        await member.send(sentence)
                    await asyncio.sleep(60 * 60 * 2)
                    # roles = database.release_prison(member.id, ctx.guild.id)
                    if prisoner.id in [role.id for role in member.roles]:
                        #     for role in roles:
                        #         r = ctx.guild.get_role(role)
                        #         await member.add_roles(r)
                        await member.remove_roles(prisoner)
                        await member.send(f"You are now released from {prison.mention} of {ctx.guild.name}")

                else:  # I have no power
                    no_power_embed = discord.Embed(title='I don\'t have power',
                                                   description=f'{member.mention} might be server owner or having higher role than me <:crypanda:897832575698075688>',
                                                   color=0xFF2030)
                    await ctx.send(embed=no_power_embed)

        elif member_is == 222 or member_is == 111:  # when mentioned member does't have slave or domme role
            embed = discord.Embed(description=f"{member.mention} should have any of the folloing roles \n"
                                  f"{self.list_roles(database.get_config('locker', member.guild.id))}\n"
                                  f"{self.list_roles(database.get_config('slave', member.guild.id))}",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

        elif member_is == 0:  # when the author doesn't have domme or slave role.
            embed = discord.Embed(description=f"{ctx.author.mention}, you should have any of the folloing roles \n"
                                  f"{self.list_roles(database.get_config('locker', member.guild.id))}\n"
                                  f"{self.list_roles(database.get_config('slave', member.guild.id))}",
                                  color=0xF2A2C0)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def unlock(self, ctx, member: discord.Member):
        if ctx.author.bot:
            return

        if not set(database.get_config('prisoner', ctx.guild.id)) & set([role.id for role in member.roles]) or member.bot:
            embed = discord.Embed(title='Already Free', description=f"{member.mention} is already in woods enjoying the sun.", color=0xF2A2C0)
            await ctx.reply(embed=embed)
            return

        member_is = who_is(ctx.author, member)
        prisoner = ctx.guild.get_role(database.get_config('prisoner', ctx.guild.id)[0])

        if member_is in [2, 202]:
            embed = discord.Embed(description=f"{member.mention} is free in Woods enjoying the sun, nobody can lock the Domme.", color=0xF2A2C0)
            await ctx.reply(embed=embed)

        elif member_is in [201, 200, 222] or member_is > 300 or ctx.author.guild_permissions.administrator:
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
                                               description=f"you are not worthy to use this command, how can you even to do such things you stupid bitch.",
                                               color=0xF2A2C0)
            await ctx.reply(embed=unlock_slave_embed)

    @commands.command()
    @commands.guild_only()
    async def escape(self, ctx):
        if ctx.author.bot:
            return

        if not set(database.get_config('prisoner', ctx.guild.id)) & set([role.id for role in member.roles]) or member.bot:
            embed = discord.Embed(title='Already Free', description=f"{member.mention} is already in woods enjoying the sun.", color=0xF2A2C0)
            await ctx.reply(embed=embed)
            return

        if database.get_money(ctx.author.id, ctx.guild.id)[3] != 0:
            database.remove_money(ctx.author.id, ctx.guild.id, 0, 10)
            prisoner = ctx.guild.get_role(database.get_config('prisoner', ctx.guild.id)[0])
            await ctx.author.remove_roles(prisoner)
            embed = discord.Embed(description=f"{ctx.author.mention} was lucky to have a magic gem <a:gems:899985611946078208> and escaped from {ctx.channel.mention}", color=0xF2A2C0)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"{ctx.author.mention} you don't have magic gem <a:gems:899985611946078208> to be free.", color=0xF2A2C0)

    ##############################################################################
    #                                                                            #
    #                                                                            #
    #                                  ERRORS                                    #
    #                                                                            #
    #                                                                            #
    ##############################################################################

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(description=f"{ctx.author.mention} you should be using this command in server.", color=0xFF2030)
            await ctx.send(embed=embed)

        if isinstance(error, commands.errors.CommandInvokeError):
            if isinstance(error.original, discord.errors.Forbidden):
                embed = discord.Embed(title='I don\'t feel so Good.', description=f"I am restrained help, Please make sure that I have **Administration Permissions** and **Elevate my Role**, then try again.", color=0xFF2030)
                await ctx.author.send(embed=embed)
                await ctx.send(embed=embed)

    @lock.error
    async def on_lock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(title='How to use Prison?', description=f"Usage:\n> **`s.lock @mention`** "
                                  f"\nAfter it just enjoy the slave punishment!",
                                  color=0xFF2030)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title="Prison Cooldown is 2h",
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
