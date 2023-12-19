#!/bin/python3
import asyncio

import database
import discord
from discord import ButtonStyle
from discord.ext import commands
from Cogs.femdom import YesNoView

from Utils.relationship import who_is

class BlindButton(discord.ui.Button):
  def __init__(self, key, action, member, ctx, **kw):
    super().__init__(**kw)
    self.key = key
    self.action = action
    self.member = member
    self.ctx = ctx

  async def callback(self, it: discord.Interaction):

    do_blind = False
    if self.key == 'give':
      embed = discord.Embed(
        description=f"{self.member.mention} can't see any of the Channels in this server for next 5 mins.",
        color=0xFF2030)

      do_blind = True

      database.update_slaveDB(self.member.id, 'muff', False, self.ctx.guild.id)
    elif self.key == 'cancel':
      embed = discord.Embed(description=f"Mission Aborted. lucky {self.member.mention}", color=0x08FF08)
      await self.action.chastity(True)

      database.update_slaveDB(self.member.id, 'muff', True, self.ctx.guild.id)

    # await it.channel.send('🫡')

    await it.response.edit_message(embed=embed, view=None)

    async def blind():
      await self.action.blind()

    if do_blind:
      await asyncio.create_task(blind())


class BlindView(discord.ui.View):
  def __init__(self, action, member, ctx):
    self.member = member
    self.ctx = ctx
    super().__init__(timeout=90)

    self.add_item(
      BlindButton(style=ButtonStyle.green, label='Yes do it', emoji='😵‍💫', key='give', ctx=ctx,
                  member=member,
                  action=action),
    )

    self.add_item(
      BlindButton(style=ButtonStyle.red, label='No', emoji='✖️', key='cancel', ctx=ctx,
                  member=member, action=action),
    )

  async def interaction_check(self, it: discord.Interaction):
    return self.ctx.author.id == it.user.id


class ChastityButton(discord.ui.Button):
  def __init__(self, key, action, member, ctx, **kw):
    super().__init__(**kw)
    self.key = key
    self.action = action
    self.member = member
    self.ctx = ctx

  async def callback(self, it: discord.Interaction):

    if self.key == 'lock':
      embed = discord.Embed(description=f"{self.member.mention} can't access NSFW Channels in this server.",
                            color=0xFF2030)
      await self.action.chastity(access=False)
      database.update_slaveDB(self.member.id, 'chastity', True, self.ctx.guild.id)
    elif self.key == 'unlock':
      embed = discord.Embed(description=f"{self.member.mention} can access NSFW Channels in this server.",
                            color=0x08FF08)
      await self.action.chastity(access=True)

      database.update_slaveDB(self.member.id, 'chastity', False, self.ctx.guild.id)

    # await it.channel.send('🫡')

    await it.response.edit_message(embed=embed, view=None)


class ChastityView(discord.ui.View):
  def __init__(self, action, member, ctx):
    self.member = member
    self.ctx = ctx
    super().__init__(timeout=90)

    dbrsp = database.get_slave_from_DB(member.id, ctx.guild.id)
    print(f'getSlave({member}, {ctx.guild}): chastity={dbrsp[0][6]}')

    dsbl = dbrsp[0][6]

    self.add_item(
      ChastityButton(style=ButtonStyle.red, label='Chastity Lock', emoji='🔒', key='lock', disabled=dsbl, ctx=ctx,
                     member=member,
                     action=action),
    )

    self.add_item(
      ChastityButton(style=ButtonStyle.green, label='Chastity Unlock', emoji='🔓', key='unlock', disabled=not dsbl,
                     ctx=ctx,
                     member=member, action=action),
    )

  async def interaction_check(self, it: discord.Interaction):
    return self.ctx.author.id == it.user.id


class MuffsButton(discord.ui.Button):
  def __init__(self, key, action, member, ctx, **kw):
    super().__init__(**kw)
    self.key = key
    self.action = action
    self.member = member
    self.ctx = ctx

  async def callback(self, it: discord.Interaction):

    if self.key == 'rem':
      embed = discord.Embed(description=f"{self.member.mention} can't connect to any Voice Channels in this server.",
                            color=0xFF2030)
      await self.action.muff(False)
      database.update_slaveDB(self.member.id, 'muff', False, self.ctx.guild.id)
    elif self.key == 'give':
      embed = discord.Embed(description=f"{self.member.mention} can connect to Voice Channels in this server.",
                            color=0x08FF08)
      await self.action.muff(True)

      database.update_slaveDB(self.member.id, 'muff', True, self.ctx.guild.id)

    # await it.channel.send('🫡')

    await it.response.edit_message(embed=embed, view=None)


class MuffsView(discord.ui.View):
  def __init__(self, action, member, ctx):
    self.member = member
    self.ctx = ctx
    super().__init__(timeout=90)

    dsbl = database.get_slave_from_DB(member.id, ctx.guild.id)[0][7]

    self.add_item(
      MuffsButton(style=ButtonStyle.green, label='Give Ear Muffs', key='give', disabled=dsbl, ctx=ctx, member=member,
                  action=action),
    )

    self.add_item(
      MuffsButton(style=ButtonStyle.red, label='Remove Ear Muffs', key='rem', disabled=not dsbl, ctx=ctx, member=member,
                  action=action),
    )

  async def interaction_check(self, it: discord.Interaction):
    return self.ctx.author.id == it.user.id


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
      await self.ctx.message.add_reaction('👌')
    elif y_n == 'no' or y_n == 'n':
      await self.ctx.message.add_reaction('🙅‍♀️')

  async def chastity(self, access, temp=False):
    channels = await self.ctx.guild.fetch_channels()
    for channel in channels:
      if channel.is_nsfw():
        if access:
          await channel.set_permissions(self.member, overwrite=None)
          # database.update_slaveDB(self.member.id, 'chastity', True, self.ctx.guild.id)
        else:
          await channel.set_permissions(self.member, view_channel=False)
          # database.update_slaveDB(self.member.id, 'chastity', False, self.ctx.guild.id)
    if temp:
      await asyncio.sleep(1 * 60 * 60)
      for channel in channels:
        if channel.is_nsfw():
          await channel.set_permissions(self.member, overwrite=None)
          # database.update_slaveDB(self.member.id, 'chastity', True, self.ctx.guild.id)

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
    self.bot.blinded_users[self.ctx.guild.id] = self.bot.blinded_users.get(self.ctx.guild.id, []) + [self.member.id]

    channels = await self.ctx.guild.fetch_channels()
    for channel in channels:
      await channel.set_permissions(self.member, view_channel=False, send_messages=False)
    await self.member.send(f"you are blindfolded in the server **{self.ctx.guild.name}** for 5 minutes.")
    await asyncio.sleep(5 * 60)
    for channel in channels:
      await channel.set_permissions(self.member, overwrite=None)


class Femdom2(commands.Cog):
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

  @commands.hybrid_command()
  @commands.guild_only()
  async def chastity(self, ctx, member: discord.Member):
    """Blocks NSFW sub channels. Note: Dommes must own sub for chastity lock."""
    if ctx.author.bot:
      return

    if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
      embed = discord.Embed(title='I am not ready yet.',
                            description=f"Ask the Admins to run the command **`/setup`** and try again",
                            color=0xF2A2C0)
      await ctx.send(embed=embed)
      return

    if member.bot:
      if member.id == self.bot.user.id:
        embed = discord.Embed(title='Nah',
                              description=f"You can't deny my cum permission, I will cum all day long and you can't stop me.<a:bully:968288741733064814>",
                              color=0xF2A2C0)
        await ctx.send(embed=embed)
      else:
        embed = discord.Embed(title='Nah',
                              description=f"You can't keep Bots in chastity.",
                              color=0xF2A2C0)
        await ctx.send(embed=embed)
    else:
      if member.guild_permissions.administrator:
        embed = discord.Embed(description=f"{member.mention} have administrator permission, I am sorry.",
                              color=0xF2A2C0)
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
        await ctx.send(embed=embed, view=ChastityView(action, member, ctx))
        return

      elif member_is > 300:
        embed = discord.Embed(title='Nah',
                              description=f"{member.mention} is owned by somebody else it's their property.",
                              color=0xFF2030)

      elif member_is == 101:
        embed = discord.Embed(title='Pathetic...',
                              description=f"You foolish slave. You think you can chastity lock when you are a slave, {ctx.author.mention}! "
                                          f"how Pathetic!!!\nI need to tell this joke to Deity, they will love it.",
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

  @commands.hybrid_command()
  @commands.guild_only()
  async def muffs(self, ctx, member: discord.Member):
    """Blocks sub voice channels. Note: Dommes must own sub for voice block."""
    if ctx.author.bot:
      return

    if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
      embed = discord.Embed(title='I am not ready yet.',
                            description=f"Ask the Admins to run the command **`/setup`** and try again",
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
        embed = discord.Embed(description=f"{member.mention} have administrator permission, I am sorry.",
                              color=0xF2A2C0)
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
        print('BRUH!')
        embed = discord.Embed(title='So what should I do?', color=0xF2A2C0)
        await ctx.send(embed=embed, view=MuffsView(action, member, ctx))
        return

      elif member_is > 300:
        embed = discord.Embed(title='Nah',
                              description=f"{member.mention} is owned by somebody else it's their property.",
                              color=0xFF2030)

      elif member_is == 101:
        embed = discord.Embed(title='Pathetic...',
                              description=f"You foolish slave. You think you can Ear Muff someone when you are a slave, {ctx.author.mention}! "
                                          f"how Pathetic!!!\n I need to tell this joke to Deity, they will love it.",
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

  @commands.hybrid_command()
  @commands.guild_only()
  @commands.cooldown(3, 4 * 60 * 60, commands.BucketType.user)
  async def blind(self, ctx, member: discord.Member):
    """This command blocks all sub channels for 5 minutes. Note: Dommes must own a sub before using this."""
    if ctx.author.bot:
      return

    if not database.is_config(ctx.guild.id):  # if bot is not configred in the server
      embed = discord.Embed(title='I am not ready yet.',
                            description=f"Ask the Admins to run the command **`/setup`** and try again",
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
        embed = discord.Embed(description=f"{member.mention} have administrator permission, I am sorry.",
                              color=0xF2A2C0)
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
        embed = discord.Embed(title='Are you sure that you wanna do this?',
                              description=f"{member.mention} will not be able to see any channels in this server for 5 mins.",
                              color=0xF2A2C0)

        if member.id in self.bot.blinded_users.get(ctx.guild.id, []):
          em = discord.Embed(title='They are already blindfolded!',
                             description=f"{member.mention} is already blindfolded, do you want to undo the blind?",
                             color=discord.Color.brand_red())

          async def unblind(mem):
            channels = await mem.guild.fetch_channels()
            for channel in channels:
              await channel.set_permissions(mem, overwrite=None)

          return await ctx.send(embed=em, view=YesNoView(member, action=unblind, msg=dict(
            title='Blindfold removed!',
            description=f'{member.mention} can now see!'
          )))

        await ctx.send(embed=embed, view=BlindView(action, member, ctx))
        return

      elif member_is > 300:
        embed = discord.Embed(title='Nah',
                              description=f"{member.mention} is owned by somebody else it's their property.",
                              color=0xFF2030)

      elif member_is == 101:
        embed = discord.Embed(title='Pathetic...',
                              description=f"You foolish slave. You think you can blindfold someone when you are a slave, {ctx.author.mention}! "
                                          f"how Pathetic!!!\nI need to tell this joke to Deity, they will love it.",
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
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(description=f"Usage:\n**`/chastity @mention`**",
                            color=0xFF2030)
      await ctx.send(embed=embed)

    raise error

  @muffs.error
  async def on_muff_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(description=f"Usage:\n**`/muffs @mention`**",
                            color=0xFF2030)
      await ctx.send(embed=embed)

    raise error

  @blind.error
  async def on_blind_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(description=f"Usage:\n> **`/blind @mention`** ",
                            color=0xFF2030)
      await ctx.send(embed=embed)


    elif isinstance(error, commands.errors.CommandOnCooldown):
      embed = discord.Embed(title="Blindfold Cooldown is 4h",
                            description="{} you need to wait {:,.1f} minutes to blindfold a slave again.".format(
                              ctx.author.mention, (error.retry_after // 60) + 1),
                            color=0xFF2030)
      await ctx.send(embed=embed)

    raise error

async def setup(bot):
  await bot.add_cog(Femdom2(bot))
