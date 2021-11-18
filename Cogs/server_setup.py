#!/bin/python3
from discord.ext import commands
import discord
import database
import asyncio
import re


class ServerConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def list_roles(self, roles):
        if isinstance(roles, list):
            role = '>'
            for r in roles:
                role = f"{role} <@&{r}>\n>"
            return role[:-2]
        else:
            return roles

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        alex_wood = self.bot.get_user(855057142297264139)
        owner_invite_embed = discord.Embed(title=f"Hi {guild.owner.name},",
                                           description=f"I have been invited to your server **{guild.name}**"
                                           "\nI am a fun bot made for Femdom Communities to help Dommes to play with their subs and also punish them."
                                           "\n\n**My prefix is `s.`**\n> **`s.setup`** use this command to set me up in the server"
                                           "\n> **`s.help`** use this command to know me more.",
                                           color=0xF2A2C0)
        owner_invite_embed.set_thumbnail(url=self.bot.user.avatar_url)
        owner_invite_embed.set_footer(text=f'created by {alex_wood}', icon_url=alex_wood.avatar_url)
        await guild.owner.send(embed=owner_invite_embed)
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        database.remove_guild(guild.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setup(self, ctx):
        def check(res):
            return ctx.author == res.author and res.channel == ctx.channel

        setup_embed_domme = discord.Embed(title='Setting Me Up.. (1/4)',
                                          description=f"Mention Domme role/s in the server, \nI will consider members with those roles as Domme.\n> "
                                          "*I will wait 1 minute for you to mention the Domme role/s.*",
                                          color=0xBF99A0)
        setup_embed_domme.set_thumbnail(url=self.bot.user.avatar_url)

        setup_embed_slave = discord.Embed(title='Setting Me Up.. (2/4)',
                                          description=f"Mention Sub role/s in the server,\nI will consider members with those roles as Subs.\n> "
                                          "*I will wait 1 minute for you to mention the Sub role/s.*",
                                          color=0x591B32)
        setup_embed_slave.set_thumbnail(url=self.bot.user.avatar_url)

        setup_embed_prison = discord.Embed(title='Setting Me Up.. (4/4)',
                                           description=f"Mention a channel to lock Subs for punishments.\n> "
                                           "*I will wait 1 minute for you to mention a channel,*\n> *or type anything so I will make a new prison channel.*",
                                           color=0xF2A2C0)
        setup_embed_prison.set_thumbnail(url=self.bot.user.avatar_url)

        setup_embed_locker = discord.Embed(title='Setting Me Up.. (3/4)',
                                           description=f"Mention the lock roles, so only Members with that role can lock Subs in prison."
                                           f"\n> *I will wait 1 minute for you to mention the Role/s*",
                                           color=0x591B32)

        setup_embed_fail = discord.Embed(title='Failed',
                                         description=f"**I was not able to find a valid role mentioned in this message**\n"
                                         f"you can always retry the setup again **`s.setup`**",
                                         color=0xFF2030)

        setup_embed_fail.set_thumbnail(url=self.bot.user.avatar_url)

        setup_embed_timeout = discord.Embed(title='Times Up',
                                            description=f"I can't wait for long, I have limited bandwidth\nits ok you can always try it again type **`s.setup`**",
                                            color=0xFF2030)

        setup_embed_timeout.set_thumbnail(url=self.bot.user.avatar_url)

        m = await ctx.send(embed=setup_embed_domme)

        try:
            response = await self.bot.wait_for('message', timeout=90, check=check)
            domme_roles = "".join([role[3:-1] for role in re.findall(r'<@&\d*>', response.content)])
            if domme_roles == '':
                await response.reply(embed=setup_embed_fail)
                return
            database.insert_config('domme', ctx.guild.id, domme_roles)
            await response.delete()
            await m.edit(embed=setup_embed_slave)

            try:
                response = await self.bot.wait_for('message', timeout=90, check=check)
                slave_roles = [role[3:-1] for role in re.findall(r'<@&\d*>', response.content)]
                for x in slave_roles:
                    if x in domme_roles:
                        slave_roles.pop(x)
                slave_roles = "".join(slave_roles)

                if slave_roles == '':
                    await response.reply(embed=setup_embed_fail)
                    return
                database.insert_config('slave', ctx.guild.id, slave_roles)
                await response.delete()
                await m.edit(embed=setup_embed_locker)

                try:
                    response = await self.bot.wait_for('message', timeout=90, check=check)
                    locker_roles = [role[3:-1] for role in re.findall(r'<@&\d*>', response.content)]
                    for x in locker_roles:
                        if x in slave_roles:
                            locker_roles.pop(x)
                    locker_roles = ''.join(locker_roles)

                    if locker_roles == '':
                        await response.reply(embed=setup_embed_fail)
                        return
                    database.insert_config('locker', ctx.guild.id, locker_roles)
                    await response.delete()
                    await m.edit(embed=setup_embed_prison)

                    try:
                        response = await self.bot.wait_for('message', timeout=90, check=check)
                        try:
                            prison = [role[2:-1] for role in re.findall(r'<#\d*>', response.content)][0]
                            database.insert_config('prison', ctx.guild.id, prison)
                            await response.delete()

                            d_roles = ''
                            s_roles = ''
                            l_roles = ''
                            for r in range(int(len(domme_roles) / 18)):
                                d_roles = f"{d_roles}\n> <@&{domme_roles[r * 18:(r * 18) + 18]}>"

                            for r in range(int(len(slave_roles) / 18)):
                                s_roles = f"{s_roles}\n> <@&{slave_roles[r * 18:(r * 18) + 18]}>"

                            for r in range(int(len(locker_roles) / 18)):
                                l_roles = f"{l_roles}\n> <@&{locker_roles[r * 18:(r * 18) + 18]}>"

                            setup_embed_summary = discord.Embed(title='Completed',
                                                                description=f"Dommes in the server are the members with the following roles{d_roles}"
                                                                f"\nSubs in the server are the members with the following roles{s_roles}"
                                                                f"\nMembers with following roles can lock sub in <#{prison}> {l_roles}"
                                                                f"\nThe channel where Dommes can torture and punish subs.\n> <#{prison}>"
                                                                f"\n\n**Use the command `s.help` to know more about me.**",
                                                                color=0x08FF08)
                            setup_embed_summary.set_thumbnail(url=self.bot.user.avatar_url)
                            await m.edit(embed=setup_embed_summary)
                        except IndexError:
                            prison = database.get_config('prison', ctx.guild.id)
                            if prison == [0] or ctx.guild.get_channel(int(prison[0])) is None:
                                prison = await ctx.guild.create_text_channel('Prison')
                                database.insert_config('prison', ctx.guild.id, prison.id)
                                prison = prison.id
                            else:
                                prison = int(prison[0])
                            d_roles = ''
                            s_roles = ''
                            for r in range(int(len(domme_roles) / 18)):
                                d_roles = f"{d_roles}\n> <@&{domme_roles[r * 18:(r * 18) + 18]}>"

                            for r in range(int(len(slave_roles) / 18)):
                                s_roles = f"{s_roles}\n> <@&{slave_roles[r * 18:(r * 18) + 18]}>"

                            for r in range(int(len(locker_roles) / 18)):
                                l_roles = f"{l_roles}\n> <@&{locker_roles[r * 18:(r * 18) + 18]}>"

                            setup_embed_summary = discord.Embed(title='Completed',
                                                                description=f"Dommes in the server are the members with the following roles{d_roles}"
                                                                f"\nSubs in the server are the members with the following roles{s_roles}"
                                                                f"\nMembers with following roles can lock sub in <#{prison}> {l_roles}"
                                                                f"\nThe channel where Dommes can torture and punish subs.\n> <#{prison}>"
                                                                f"\n\n**Use the command `s.help` to know more about me.**",
                                                                color=0x08FF08)
                            setup_embed_summary.set_thumbnail(url=self.bot.user.avatar_url)
                            await m.edit(embed=setup_embed_summary)

                    except asyncio.TimeoutError:
                        await m.edit(embed=setup_embed_timeout)

                except asyncio.TimeoutError:
                    await m.edit(embed=setup_embed_timeout)

            except asyncio.TimeoutError:
                await m.edit(embed=setup_embed_timeout)

        except asyncio.TimeoutError:
            await m.edit(embed=setup_embed_timeout)

        prisoner = database.get_config('prisoner', ctx.guild.id)
        if prisoner == [0] or ctx.guild.get_role(int(prisoner[0])) is None:
            prisoner = await ctx.guild.create_role(name='Prisoner', color=0x591B32)
            database.insert_config('prisoner', ctx.guild.id, prisoner.id)
        else:
            prisoner = ctx.guild.get_role(prisoner[0])
        prison = ctx.guild.get_channel(int(prison))
        channels = await ctx.guild.fetch_channels()
        for channel in channels:
            await channel.set_permissions(prisoner, view_channel=False, send_messages=False)
        await prison.set_permissions(prisoner, view_channel=True, send_messages=True)
        await prison.set_permissions(ctx.guild.default_role, view_channel=True, send_messages=False)

        for r in range(int(len(domme_roles) / 18)):
            d_role = int((domme_roles[r * 18:(r * 18) + 18]))
            await prison.set_permissions(ctx.guild.get_role(d_role), view_channel=True, send_messages=True)

    @commands.command(aliases=['stats'])
    @commands.guild_only()
    async def stat(self, ctx):
        prison = database.get_config('prison', ctx.guild.id)
        domme = database.get_config('domme', ctx.guild.id)
        slave = database.get_config('slave', ctx.guild.id)
        NSFW = database.get_config('NSFW', ctx.guild.id)
        chat = database.get_config('chat', ctx.guild.id)
        locker = database.get_config('locker', ctx.guild.id)
        t_mem = 0
        
        for guild in self.bot.guilds:
            t_mem = t_mem + guild.member_count

        if NSFW == [0]:
            NSFW = f"> {ctx.guild.default_role}"
        if chat == [0]:
            chat = f"> {ctx.guild.default_role}"

        if domme != [0]:
            stat_embed = discord.Embed(title='Status',
                                       description=f"**I am controling {t_mem} members.**\n\n"
                                       f"Domme roles:\n{self.list_roles(domme)}\n"
                                       f"Sub roles:\n{self.list_roles(slave)}\n"
                                       f"Dommes who are strong to lock subs in <#{prison[0]}>:\n{self.list_roles(locker)}\n"
                                       f"NSFW command access is given to:\n{self.list_roles(NSFW)}\n"
                                       f"Members who have permission to talk to me:\n{self.list_roles(chat)}\n\n"
                                       f"**Dommes can torture subs in <#{prison[0]}>**\n"
                                       f"\n> type **`s.help`** to know more about me",
                                       color=0xF2A2C0)
        else:
            stat_embed = discord.Embed(title='Status',
                                       description=f"**I am active in {len(self.bot.guilds)} servers.**\n"
                                       f"\n> type **`s.setup`** to set me up in the server"
                                       f"\n> type **`s.help`** to know more about me",
                                       color=0xF2A2C0)
        stat_embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=stat_embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setNSFW(self, ctx, *, roles=None):
        if roles is None or '@everyone' in roles:
            database.clear_config('NSFW', ctx.guild.id)
            sucess_embed = discord.Embed(description=f"NSFW command access is given to {ctx.guild.default_role}",
                                         color=0xF2A2C0)
            await ctx.reply(embed=sucess_embed)
            return
        roles = "".join([role[3:-1] for role in re.findall(r'<@&\d*>', roles)])
        if roles == "":
            fail_embed = discord.Embed(description=f"{ctx.author.mention} you didn't mention any roles or you mentioned invalid roles.", color=0xF2A2C0)
            await ctx.reply(embed=fail_embed)
        else:
            database.insert_config('NSFW', ctx.guild.id, roles)
            sucess_embed = discord.Embed(description=f"NSFW command access is only for members with the following roles:\n{self.list_roles(database.get_config('NSFW', ctx.guild.id))}",
                                         color=0xF2A2C0)
            await ctx.reply(embed=sucess_embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setchat(self, ctx, *, roles=None):
        if roles is None or '@everyone' in roles:
            database.clear_config('chat', ctx.guild.id)
            sucess_embed = discord.Embed(description=f"{ctx.guild.default_role} can chat with me.",
                                         color=0xF2A2C0)
            await ctx.reply(embed=sucess_embed)
            return
        roles = "".join([role[3:-1] for role in re.findall(r'<@&\d*>', roles)])
        if roles == "":
            fail_embed = discord.Embed(description=f"{ctx.author.mention} you didn't mention any roles or you mentioned invalid roles.", color=0xF2A2C0)
            await ctx.reply(embed=fail_embed)
        else:
            database.insert_config('chat', ctx.guild.id, roles)
            sucess_embed = discord.Embed(description=f"Only Members with the following roles can chat with me:\n{self.list_roles(database.get_config('chat', ctx.guild.id))}",
                                         color=0xF2A2C0)
            await ctx.reply(embed=sucess_embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def blacklist(self, ctx, member: discord.Member = None):
        if member is None:
            page_number = 1
            size = 10
            data = database.get_blacklist(ctx.guild.id)

            def page(lb_list, page, size):
                value = ''
                try:
                    for x in range(((page - 1) * size), ((page - 1) * size) + size):
                        value = value + f"> <@{lb_list[x]}>\n"
                    embed = discord.Embed(title="Blacklisted Members", description=value, color=0xF2A2C0)
                except IndexError:
                    embed = discord.Embed(title="Blacklisted Members", description=value, color=0xF2A2C0)

                embed.set_footer(text=f"On page {page}/{int(len(lb_list) / size) + (len(lb_list) % size > 0) + 1}")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                return embed

            def check(reaction, user):
                return user == ctx.author

            embed = page(data, 1, size)
            box = await ctx.channel.send(embed=embed)
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
        else:
            if database.insert_remove_blacklist(member.id, ctx.guild.id):
                embed = discord.Embed(title='Added into Blacklist', description=f"{member.mention} is Blacklisted, now the member can't lock anyone in the server anymore.", color=0xFF2030)
            else:
                embed = discord.Embed(title='Removed from Blacklist', description=f"{member.mention} is no longer Blacklisted, and can lock the subs <#{database.get_config('prison', ctx.guild.id)[0]}>", color=0x08FF08)
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)

    # @blacklist.error
    # async def on_blacklist_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
    #         embed = discord.Embed(description=f"Usage:\n**`s.blacklist @mention`** to **add** or **remove** member from blacklist."
    #                                           f"\n**`s.blacklist`** to see the list of blacklisted members.",
    #                               color=0xFF2030)
    #         await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ServerConfig(bot))
