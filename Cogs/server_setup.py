#!/bin/python3
import asyncio
import re

import database
import discord
from discord import app_commands
from discord.ext import commands


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
    kuro_usagi = self.bot.get_user(104373103802466304)
    owner_invite_embed = discord.Embed(title=f"Hi {guild.owner.name},",
                                       description=f"I have been invited to your server **{guild.name}**"
                                                   "\nI am a fun bot made for Femdom Communities to help Dommes to play with their subs and also punish them."
                                                   "\n\n**My prefix is `/`**\n> **`/setup`** use this command to set me up in the server"
                                                   "\n> **`/help`** use this command to know me more.",
                                       color=0xF2A2C0)
    owner_invite_embed.set_thumbnail(url=self.bot.user.display_avatar.url)
    owner_invite_embed.set_footer(text=f'created by {kuro_usagi}')
    await guild.owner.send(embed=owner_invite_embed)

  @commands.Cog.listener()
  async def on_guild_remove(self, guild):
    database.remove_guild(guild.id)

  @app_commands.command()
  @app_commands.guild_only()
  @app_commands.checks.has_permissions(administrator=True)
  async def setup(self, it: discord.Interaction):
    """
    [ADMIN ONLY] Set up the bot in the server to use it.
    """
    check = lambda m: it.user.id == m.author.id and m.channel.id == it.channel.id

    embeds = dict(
      setup_embed_domme=discord.Embed(
        title='Setting Me Up.. (1/6)',
        description=f"Mention Domme role/s in the server, \nI will consider members with those roles as Domme.\n> "
                    "*I will wait 1 minute for you to mention the Domme role/s.*",
        color=0xBF99A0
      ),

      setup_embed_slave=discord.Embed(
        title='Setting Me Up.. (2/6)',
        description=f"Mention Sub role/s in the server,\nI will consider members with those roles as Subs.\n> "
                    "*I will wait 1 minute for you to mention the Sub role/s.*",
        color=0x591B32
      ),
      setup_embed_switch=discord.Embed(
        title='Setting Me Up.. (4/6)',
        description=f"Mention the switch roles, I will consider members with those roles as both Subs and Domme."
                    f"\n> *I will wait 1 minute for you to mention the Role/s*",
        color=0x591B32
      ),
      setup_embed_reactionroles_channel=discord.Embed(
        title='Setting Me Up.. (5/6)',
        description=f"Mention a channel to put the role choosing message in (something like #get-roles).\n> "
                    "*I will wait 1 minute for you to mention a channel,*\n> *or type anything so I will make a new get roles channel.*",
        color=0xF2A2C0
      ),
      setup_embed_prison=discord.Embed(
        title='Setting Me Up.. (6/6)',
        description=f"Mention a channel to lock Subs for punishments.\n> "
                    "*I will wait 1 minute for you to mention a channel,*\n> *or type anything so I will make a new prison channel.*",
        color=0xF2A2C0
      ),
      setup_embed_fail=discord.Embed(
        title='Failed',
        description=f"**I was not able to find a valid role (or channel) mentioned in this message**\n"
                    f"you can always retry the setup again **`/setup`**",
        color=0xFF2030
      ),
      setup_embed_timeout=discord.Embed(
        title='Times Up',
        description=f"I can't wait for long, I have limited bandwidth\nits ok you can always try it again type **`/setup`**",
        color=0xFF2030
      )
    )

    for embed in embeds.values():
      embed.set_thumbnail(url=self.bot.user.display_avatar.url)

    m = None
    ctx = await self.bot.get_context(it)

    setup_roles = {}
    prison_channel = None

    for i, stage in enumerate(['domme', 'slave', 'switch', 'reactionroles_channel', 'prison']):
      em = embeds[f'setup_embed_{stage}']

      if not m:
        m = await ctx.send(embed=em)
      else:
        await m.edit(embed=em)

      try:
        resp: discord.Message = await self.bot.wait_for('message', timeout=90, check=check)
      except asyncio.TimeoutError:
        return await m.edit(embed=setup_embed_timeout)

      if stage == 'reactionroles_channel':
        channel = resp.channel_mentions

        if not channel or not isinstance(channel[0], discord.TextChannel):
          rr_channel = await ctx.guild.create_text_channel(
            'get-roles',
            overwrites={
              ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=False
              ),
              ctx.guild.me: discord.PermissionOverwrite(
                send_messages=True
              )
            })
          database.insert_config(stage, it.guild.id, str(rr_channel.id))
        else:
          database.insert_config(stage, it.guild.id, str(channel[0].id))
          rr_channel = channel[0]

        DOMME_REACTION, SUB_REACTION, SWITCH_REACTION = '<:Domme:1167057873990336512>', '<:Sub:1155850020541710489>', '🔀'

        em = discord.Embed(
          title='Which side are you?',
          description=f"""
          If you are a Domme choose {DOMME_REACTION}: \n
          If you are a Sub choose: {SUB_REACTION} \n
          If you are a Switch choose: {SWITCH_REACTION} \n
          """.strip(),
          color=discord.Color.orange()
        )

        em.set_footer(text=f"{self.bot.user.name} | Donate here - https://ko-fi.com/kyrian",
                      icon_url=self.bot.user.display_avatar.url)

        rrm = await rr_channel.send(embed=em)

        for r in (DOMME_REACTION, SUB_REACTION, SWITCH_REACTION):
          await rrm.add_reaction(r)

        #  TODO REACTION ROLES
        database.insert_config("reactionroles_message", it.guild.id, str(rrm.id))
        database.insert_config("reactionroles_reactions", it.guild.id,
                               f"{DOMME_REACTION},{SUB_REACTION},{SWITCH_REACTION}")



      elif stage == 'prison':
        channel = resp.channel_mentions

        if not channel or not isinstance(channel[0], discord.TextChannel):
          prison_channel = await ctx.guild.create_text_channel('prison')
          database.insert_config(stage, it.guild.id, str(prison_channel.id))
        else:
          database.insert_config(stage, it.guild.id, str(channel[0].id))
          prison_channel = channel[0]

      else:
        roles = resp.role_mentions

        if not roles:
          await m.send(embed=embeds['setup_embed_fail'])
          return

        database.insert_config(stage, it.guild.id, ",".join(map(str, resp.raw_role_mentions)))
        setup_roles[stage] = roles

      await resp.delete()

    # completed summary
    em = discord.Embed(
      title='Completed',
      color=0x08FF08,
      description=f"""
      Dommes in the server are the members with the following roles:
      > {" ".join(r.mention for r in setup_roles['domme'])}
      Subs in the server are the members with the following roles:
      > {" ".join(r.mention for r in setup_roles['slave'])}
      Switches in the server are members with the following roles:
      > {" ".join(r.mention for r in setup_roles['switch'])}
      The channel where members can choose their roles:
      > {rr_channel.mention}
      The channel where Dommes can torture and punish subs:
      > {prison_channel.mention}
      
      **Use the command `/help` to know more about me.**
      """.strip()
    )
    em.set_thumbnail(url=self.bot.user.display_avatar.url)
    await m.edit(embed=em)

    prisoner = await ctx.guild.create_role(name='Prisoner', color=0x591B32)
    database.insert_config('prisoner', ctx.guild.id, prisoner.id)

    await prisoner.edit(
      permissions=discord.Permissions(
        view_channel=False,
        send_messages=False
      )
    )

    await prison_channel.set_permissions(prisoner, view_channel=True, send_messages=True)
    await prison_channel.set_permissions(ctx.guild.default_role, view_channel=True, send_messages=False)

    for r in setup_roles['domme']:
      await prison_channel.set_permissions(r, view_channel=True, send_messages=True)

  @commands.hybrid_command()
  @commands.guild_only()
  async def stats(self, ctx):
    """
    this command will show my stats/configs in the server
    """
    prison = database.get_config('prison', ctx.guild.id)
    domme = database.get_config('domme', ctx.guild.id)
    slave = database.get_config('slave', ctx.guild.id)
    NSFW = database.get_config('NSFW', ctx.guild.id)
    chat = database.get_config('chat', ctx.guild.id)

    t_mem = 0

    for guild in self.bot.guilds:
      t_mem = t_mem + (guild.member_count or 0)

    if NSFW == [0]:
      NSFW = f"> {ctx.guild.default_role}"
    if chat == [0]:
      chat = f"> {ctx.guild.default_role}"

    if domme != [0]:
      stat_embed = discord.Embed(title='Status',
                                 description=f"**I am controling {t_mem} members.**\n\n"
                                             f"Domme roles:\n{self.list_roles(domme)}\n"
                                             f"Sub roles:\n{self.list_roles(slave)}\n"
                                             f"NSFW command access is given to:\n{self.list_roles(NSFW)}\n"
                                             f"Members who have permission to talk to me:\n{self.list_roles(chat)}\n\n"
                                             f"**Dommes can torture subs in <#{prison[0]}>**\n"
                                             f"\n> type **`/help`** to know more about me",
                                 color=0xF2A2C0)
    else:
      stat_embed = discord.Embed(title='Status',
                                 description=f"**I am active in {len(self.bot.guilds)} servers.**\n"
                                             f"\n> type **`/setup`** to set me up in the server"
                                             f"\n> type **`/help`** to know more about me",
                                 color=0xF2A2C0)
    stat_embed.set_thumbnail(url=self.bot.user.display_avatar.url)
    await ctx.send(embed=stat_embed)

  @commands.hybrid_command()
  @commands.has_permissions(administrator=True)
  @commands.guild_only()
  async def setnsfw(self, ctx, *, roles=None):
    """use this command to make sure that only members with mentioned role/s can access NSFW commands."""
    if roles is None or '@everyone' in roles:
      database.clear_config('NSFW', ctx.guild.id)
      sucess_embed = discord.Embed(description=f"NSFW command access is given to {ctx.guild.default_role}",
                                   color=0xF2A2C0)
      await ctx.reply(embed=sucess_embed)
      return
    roles = "".join([role[3:-1] for role in re.findall(r'<@&\d*>', roles)])
    if roles == "":
      fail_embed = discord.Embed(
        description=f"{ctx.author.mention} you didn't mention any roles or you mentioned invalid roles.",
        color=0xF2A2C0)
      await ctx.reply(embed=fail_embed)
    else:
      database.insert_config('NSFW', ctx.guild.id, roles)
      sucess_embed = discord.Embed(
        description=f"NSFW command access is only for members with the following roles:\n{self.list_roles(database.get_config('NSFW', ctx.guild.id))}",
        color=0xF2A2C0)
      await ctx.reply(embed=sucess_embed)

  @commands.hybrid_command()
  @commands.has_permissions(administrator=True)
  @commands.guild_only()
  async def setchat(self, ctx, *, roles=None):
    """I will chat with member only with the mentioned roles and have fun. ||maybe some erp||"""
    if roles is None or '@everyone' in roles:
      database.clear_config('chat', ctx.guild.id)
      sucess_embed = discord.Embed(description=f"{ctx.guild.default_role} can chat with me.",
                                   color=0xF2A2C0)
      await ctx.reply(embed=sucess_embed)
      return
    roles = ",".join([role[3:-1] for role in re.findall(r'<@&\d*>', roles)])
    if roles == "":
      fail_embed = discord.Embed(
        description=f"{ctx.author.mention} you didn't mention any roles or you mentioned invalid roles.",
        color=0xF2A2C0)
      await ctx.reply(embed=fail_embed)
    else:
      database.insert_config('chat', ctx.guild.id, roles)
      sucess_embed = discord.Embed(
        description=f"Only Members with the following roles can chat with me:\n{self.list_roles(database.get_config('chat', ctx.guild.id))}",
        color=0xF2A2C0)
      await ctx.reply(embed=sucess_embed)

  @commands.hybrid_command()
  @commands.has_permissions(administrator=True)
  @commands.guild_only()
  async def blacklist(self, ctx, member: discord.Member = None):
    """This will blacklist a mentioned member, and prevent them to lock any subs.
    If no arg, then willlist of blacklisted members."""
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
      box = await ctx.send(embed=embed)
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
        embed = discord.Embed(title='Added into Blacklist',
                              description=f"{member.mention} is Blacklisted, now the member can't lock anyone in the server anymore.",
                              color=0xFF2030)
      else:
        embed = discord.Embed(title='Removed from Blacklist',
                              description=f"{member.mention} is no longer Blacklisted, and can lock the subs <#{database.get_config('prison', ctx.guild.id)[0]}>",
                              color=0x08FF08)
      embed.set_thumbnail(url=member.display_avatar.url)
      await ctx.send(embed=embed)

  @blacklist.error
  async def on_blacklist_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(
        description=f"Usage:\n**`/blacklist @mention`** to **add** or **remove** member from blacklis/"
                    f"\n**`/blacklist`** to see the list of blacklisted members.",
        color=0xFF2030)
      await ctx.send(embed=embed)

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    """
    For reaction roles
    """

    if not database.is_config(payload.guild_id):
      return

    if payload.message_id != int(database.get_config('reactionroles_message', payload.guild_id)[0]):
      return

    if payload.user_id == self.bot.user.id:
      return

    DOMME_REACTION, SUB_REACTION, SWITCH_REACTION = database.get_config('reactionroles_reactions',
                                                                                       payload.guild_id)

    reaction_role = {
      DOMME_REACTION: database.get_config('domme', payload.guild_id)[0],
      SUB_REACTION: database.get_config('slave', payload.guild_id)[0],
      SWITCH_REACTION: database.get_config('switch', payload.guild_id)[0]
    }

    guild = self.bot.get_guild(payload.guild_id)
    mem = (payload.member or guild.get_member(payload.user_id))

    # print('ADD REACTION')
    # print(f'{payload.emoji} {payload.user_id} {payload.member} {mem} {mem.roles}')
    # print(reaction_role.get(str(payload.emoji)))
    # print('---------------')

    if role := reaction_role.get(str(payload.emoji)):
      role_id = int(role.split(',')[0])
      role = guild.get_role(role_id)

      has_role = lambda rid: rid in [r.id for r in mem.roles]

      to_remove = []

      if has_role(int(reaction_role[DOMME_REACTION])) and role_id != int(reaction_role[DOMME_REACTION]):
        to_remove.append(int(reaction_role[DOMME_REACTION]))
      if has_role(int(reaction_role[SUB_REACTION])) and role_id != int(reaction_role[SUB_REACTION]):
        to_remove.append(int(reaction_role[SUB_REACTION]))
      if has_role(int(reaction_role[SWITCH_REACTION])) and role_id != int(reaction_role[SWITCH_REACTION]):
        to_remove.append(int(reaction_role[SWITCH_REACTION]))

      await mem.remove_roles(*[discord.Object(id=r) for r in to_remove])

      if not has_role(role_id):
        await mem.add_roles(role)

  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
    """
    For reaction roles
    """

    if not database.is_config(payload.guild_id):
      return

    if payload.message_id != int(database.get_config('reactionroles_message', payload.guild_id)[0]):
      return

    if payload.user_id == self.bot.user.id:
      return

    DOMME_REACTION, SUB_REACTION, SWITCH_REACTION = \
      database.get_config('reactionroles_reactions', payload.guild_id)

    reaction_role = {
      DOMME_REACTION: database.get_config('domme', payload.guild_id)[0],
      SUB_REACTION: database.get_config('slave', payload.guild_id)[0],
      SWITCH_REACTION: database.get_config('switch', payload.guild_id)[0]
    }

    guild = self.bot.get_guild(payload.guild_id)
    mem = (payload.member or guild.get_member(payload.user_id))

    # print('REMOVE REACTION')
    # print(f'{payload.emoji} {payload.user_id} {payload.member} {mem} {mem.roles}')
    # print(reaction_role.get(str(payload.emoji)))
    # print('---------------')

    if role := reaction_role.get(str(payload.emoji)):
      role_id = int(role.split(',')[0])
      role = guild.get_role(role_id)
      await mem.remove_roles(role)


async def setup(bot):
  await bot.add_cog(ServerConfig(bot))
