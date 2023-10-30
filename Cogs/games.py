#!/bin/python3
import asyncio
import random

import database
import discord
from discord.ext import commands


class Games(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def ban_check(self, author, member):
    ban_data = database.is_botban(author.id)
    if ban_data is not None:
      embed = discord.Embed(title='Bot ban',
                            description=f"{author.mention} you are banned from using {self.bot.user.mention} till <t:{ban_data[1]}:F>",
                            color=0xF2A2C0)
      return embed
    elif database.is_botban(member.id) is not None:
      embed = discord.Embed(title='Bot ban',
                            description=f"{member.mention} is banned from using {self.bot.user.mention}.",
                            color=0xF2A2C0)
      return embed

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot:
      if message.author.id != 302050872383242240:  # user ID of Disboard bot
        return
      else:
        for embed in message.embeds:
          try:
            if "https://disboard.org/images/bot-command-image-bump.png" == embed.to_dict()['image']['url']:
              user_id = int(embed.to_dict()['description'][2:20].replace('>', ''))
              if database.is_botban(user_id) is not None:
                return
              coins_to_add = 100 + random.randint(0, 50)
              database.add_money(user_id, message.guild.id, coins_to_add, 0)
              embed = discord.Embed(
                description=f"<@{user_id}> received {coins_to_add} <a:pinkcoin:1167061163515858954> for Bumping the server.",
                color=0xF2A2C0)
              await message.channel.send(embed=embed)
              return
          except Exception:
            return

    if random.random() < 0.1 and database.is_botban(message.author.id) is None:
      coins_to_add = 3
      database.add_money(message.author.id, message.guild.id, coins_to_add, 0)

    try:
      data = database.get_config_raw('counting', message.guild.id).split(
        '_')  # [number, channel, member, message, count_length]
    except AttributeError:
      return
    if message.channel.id != int(data[1]):
      return

    try:
      count = int(message.content)
    except ValueError:
      if message.content.lower() == '/ruin':  # string is passed
        return
      else:
        # await message.delete()
        return

    number = int(data[0])
    if number < 0:
      if (-1 * number) == count:
        embed = discord.Embed(
          description=f"{message.author.mention} you guessed the correct number and you earned 30 <a:pinkcoin:1167061163515858954>",
          color=0xF2A2C0)
        await message.reply(embed=embed)
        if database.is_botban(message.author.id) is None:
          database.add_money(message.author.id, message.guild.id, 30, 0)
        data[0] = str(-1 * number + 1)
        data[2] = str(message.author.id)
        data[3] = str(message.id)
        data[4] = '1'
        database.insert_config('counting', message.guild.id, '_'.join(data))
        await message.add_reaction('<a:pinkcoin:1167061163515858954>')
      else:
        if count > number * -1:
          hint = f"Next number is {len(str(number * -1))} digit number and less than {count}"
        else:
          hint = f"Next number is {len(str(number * -1))} digit number and greater than {count}"
        embed = discord.Embed(title='Hint', description=hint, color=0xF2A2C0)
        await message.channel.send(embed=embed)

    else:
      if message.author.id == int(data[2]):
        await message.delete()
        m = await message.channel.send(f"{message.author.mention} you can't continues wait for someone else.")
        await asyncio.sleep(5)
        await m.delete()
      elif count == number:
        if database.is_botban(message.author.id) is None:
          database.add_money(message.author.id, message.guild.id, 1, 0)
        data[0] = str(number + 1)
        data[2] = str(message.author.id)
        data[3] = str(message.id)
        data[4] = str(int(data[4]) + 1)
        database.insert_config('counting', message.guild.id, '_'.join(data))
        await message.add_reaction('<a:pinkcoin:1167061163515858954>')
      else:
        await message.delete()

  @commands.hybrid_command()
  @commands.has_permissions(administrator=True)
  @commands.guild_only()
  async def setcount(self, ctx, channel: discord.TextChannel = None):
    """this command will set the  mentioned channel as counting channel."""
    channel = channel or ctx.channel
    data = f"70_{channel.id}_0_0_0"
    database.insert_config('counting', ctx.guild.id, data)
    await channel.send('I will start with my fav number.')
    m = await channel.send('69')
    await m.add_reaction('<a:pinkcoin:1167061163515858954>')
    embed = discord.Embed(title='Counting',
                          description=f"{channel.mention} is the counting channel.\n**How to earn more pinkcoins <a:pinkcoin:1167061163515858954>**"
                                      f"\n> Counting earns pinkcoins <a:pinkcoin:1167061163515858954>\n> Dommes can ruin by **`/ruin`** the game and earn pinkcoins <a:pinkcoin:1167061163515858954>"
                                      f"\n> Guessing the correct number after ruing also gives pinkcoins <a:pinkcoin:1167061163515858954>",
                          color=0xF2A2C0)
    embed.set_thumbnail(url=self.bot.user.display_avatar.url)
    await ctx.send(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  @commands.cooldown(1, 1 * 60 * 60, commands.BucketType.user)
  async def ruin(self, ctx):
    """Counting earns pinkcoins, Dommes can ruin the game by running this. they will earn pinkcoins."""
    if ctx.author.bot:
      return
    ban_data = database.is_botban(ctx.author.id)
    if ban_data is None:
      try:
        data = database.get_config_raw('counting', ctx.guild.id).split(
          '_')  # [number, channel, member, message, count_length]
      except AttributeError:
        embed = discord.Embed(
          description=f"Counting channel is not configured yet, ask Admins to run **`/setcount #countChannel`**",
          color=0xF2A2C0)
        await ctx.reply(embed=embed)
        return

      has_role = lambda rid: str(rid) in [str(role.id) for role in ctx.author.roles]
      domme = database.get_config('domme', ctx.author.guild.id)[0]
      sub = database.get_config('slave', ctx.author.guild.id)[0]
      switch = database.get_config('switch', ctx.author.guild.id)[0]

      if ctx.channel.id != int(data[1]):
        await ctx.reply(f"You should use this command in <#{data[1]}>")
      elif has_role(domme) or has_role(switch):
        database.add_money(ctx.author.id, ctx.guild.id, int(data[4]), 0)
        data_ = f"{-1 * random.randint(70, 1000)}_{ctx.channel.id}_0_0_0"
        database.insert_config('counting', ctx.guild.id, data_)
        embed = discord.Embed(
          description=f"{ctx.author.mention} ruined the counting and earned {data[4]} <a:pinkcoin:1167061163515858954>"
                      f"\n\n\n> **Now guess the next number to earn more**", color=0xF2A2C0)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
      else:
        roles = '>'
        for r in [*database.get_config('domme', ctx.guild.id), *database.get_config('switch', ctx.guild.id)]:
          roles = f"{roles} <@&{r}>\n>"
        embed = discord.Embed(description=f"you don't have any of the following roles to ruin the game.\n{roles[:-2]}",
                              color=0xF2A2C0)
        await ctx.send(embed=embed)
    else:
      embed = discord.Embed(title='Bot ban',
                            description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till <t:{ban_data[1]}:F>",
                            color=0xF2A2C0)
      await ctx.send(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def give(self, ctx, member: discord.Member, amount: int):
    """transfer coins to other members, you can only transfer coins you have."""
    if ctx.author.bot:
      return

    elif member.bot:  # when mentioned member is bot
      embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                            color=0xF2A2C0)
      await ctx.send(embed=embed)
      return

    ban_embed = self.ban_check(ctx.author, member)
    if ban_embed is not None:
      await ctx.send(embed=ban_embed)
      return

    coin = database.get_money(ctx.author.id, ctx.guild.id)[2]
    if coin < amount:
      await ctx.reply(
        f"🧏‍♀️ really, you are broke, you only have {coin}<a:pinkcoin:1167061163515858954>")
    elif amount < 10:
      await ctx.reply(
        f"🧏‍♀️ Grrr....,  10<a:pinkcoin:1167061163515858954> is minimum amount to transfer")
    else:
      database.add_money(member.id, ctx.guild.id, amount, 0)
      database.remove_money(ctx.author.id, ctx.guild.id, amount, 0)
      embed = discord.Embed(
        description=f"{ctx.author.mention} gave {amount} <a:pinkcoin:1167061163515858954> to {member.mention}",
        color=0xF2A2C0)
      await ctx.send(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def simp(self, ctx: commands.Context, member: discord.Member):
    """simp someone, this is identical to the worship command"""
    await ctx.invoke(self.worship, member=member)

  @commands.hybrid_command(aliases=['praise', 'footkiss', 'feetkiss'])
  @commands.guild_only()
  async def worship(self, ctx, member: discord.Member):
    """worship someone, this is identical to the simp command"""
    if ctx.author.bot:
      return

    elif member.bot:  # when mentioned member is bot
      embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                            color=0xF2A2C0)
      await ctx.send(embed=embed)
      return

    ban_embed = self.ban_check(ctx.author, member)
    if ban_embed is not None:
      await ctx.send(embed=ban_embed)
      return

    if (set(database.get_config('domme', ctx.guild.id)) & set([str(role.id) for role in member.roles])) or (set(database.get_config('switch', ctx.guild.id)) & set([str(role.id) for role in member.roles])):
      if ctx.channel.is_nsfw():
        money = database.get_money(ctx.author.id, ctx.guild.id)[2]
        if money >= 100:
          database.remove_money(ctx.author.id, ctx.guild.id, 100, 0)
          if not set(database.get_config('domme', ctx.guild.id)) & set([str(role.id) for role in ctx.author.roles]):
            database.add_money(ctx.author.id, ctx.guild.id, 0, 1)
            database.add_money(member.id, ctx.guild.id, 0, 5)
          database.simp(ctx.author.id, ctx.guild.id, member.id)
          simp_embed = discord.Embed(
            title=f"{ctx.author.nick or ctx.author.name} Simps for {member.nick or member.name}",
            description=f"",
            color=0xF2A2C0)
          with open('Text_files/simp_image.txt', 'r') as f:
            lines = f.read().splitlines()
            link = random.choice(lines)
          simp_embed.set_image(url=link)
          await ctx.send(embed=simp_embed)
        else:
          embed = discord.Embed(
            description=f"{ctx.author.mention} you need at least 100 <a:pinkcoin:1167061163515858954> to simp for {member.mention}",
            color=0xF2A2C0)
          await ctx.send(embed=embed)
      else:
        embed = discord.Embed(description=f'{ctx.author.mention} This is not a NSFW Channel try again in NSFW channel.',
                              color=0xF2A2C0)
        await ctx.reply(embed=embed)
    else:
      roles = '>'
      for r in database.get_config('domme', ctx.guild.id):
        roles = f"{roles} <@&{r}>\n>"
      embed = discord.Embed(description=f"You can only simp/worship members with following roles.\n{roles[:-2]}",
                            color=0xF2A2C0)
      await ctx.send(embed=embed)

  @commands.hybrid_command()
  @commands.guild_only()
  async def bal(self, ctx, member: discord.Member = None):
    """this command will show your coins and gems"""
    if ctx.author.bot:
      return

    member = member or ctx.author
    ban_embed = self.ban_check(ctx.author, member)
    if ban_embed is not None:
      await ctx.send(embed=ban_embed)
      return

    elif member.bot:  # when mentioned member is bot
      embed = discord.Embed(description=f"{member.mention} is a bot not a Person!",
                            color=0xF2A2C0)
      await ctx.send(embed=embed)

    else:
      money = database.get_money(member.id, member.guild.id)
      embed = discord.Embed(title="Cash",
                            description=f"\n> <a:pinkcoin:1167061163515858954> {money[2]}\n> 💎 {money[3]}",
                            color=0xF2A2C0)
      embed.set_thumbnail(url=member.display_avatar.url)
      await ctx.send(embed=embed)

  ##############################################################################
  #                                                                            #
  #                                                                            #
  #                                  ERRORS                                    #
  #                                                                            #
  #                                                                            #
  ##############################################################################

  @ruin.error
  async def on_ruin_error(self, ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown):
      embed = discord.Embed(title="Ruin Cooldown is 1h",
                            description="{} you need to wait {:,.1f} minutes to ruin the game again.".format(
                              ctx.author.mention, (error.retry_after // 60) + 1),
                            color=0xFF2030)
    await ctx.send(embed=embed)

  @worship.error
  async def on_worship_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(description=f"Usage:\n**`/worship @mention`**",
                            color=0xFF2030)
      await ctx.send(embed=embed)

  @give.error
  async def on_give_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(
        error, commands.MemberNotFound):
      embed = discord.Embed(description=f"Usage:\n**`/give @mention <amount>`**",
                            color=0xFF2030)
      await ctx.send(embed=embed)


async def setup(bot):
  await bot.add_cog(Games(bot))
