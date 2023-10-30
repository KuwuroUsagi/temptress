#!/bin/python3

import database
import discord
from discord.ext import commands
from discord.ext import menus
# from pyurbandict import UrbanDict

class Menu(menus.MenuPages):
  async def send_initial_message(self, ctx, channel):
    page = await self._source.get_page(0)
    kwargs = await self._get_kwargs_from_page(page)
    return await ctx.send(**kwargs)

class MySource(menus.ListPageSource):
  def __init__(self, data, definition):
    self.definition = definition
    super().__init__(data, per_page=3)

  async def format_page(self, menu, entries):
    offset = menu.current_page * self.per_page

    em = discord.Embed(title=f'Urban - {self.definition}', color=discord.Color.purple())
    em.set_footer(text=f'Page {menu.current_page + 1}/{self.get_max_pages()}')

    for i, v in enumerate(entries, start=offset):
      print(v)
      em.add_field(name=f'{v.definition[:250]}...' if len(v.definition) > 250 else v.definition,
                   value=f'{v.example}\n\n> **{v.thumbs_up} 👍** －O－ **{v.thumbs_down} 👎**', inline=False)

    return em


class Misc(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command()
  @commands.guild_only()
  async def define(self, ctx, *, word):
    """this command will show the definition of the word from urban dictionary."""
    if ctx.author.bot:
      return

    if (bd := database.is_botban(ctx.author.id)):
      embed = discord.Embed(
        description=f"{ctx.author.mention} you are banned from using {self.bot.user.mention} till {ban_data[1]}",
        color=0xF2A2C0)
      return await ctx.send(embed=embed)

    # results = UrbanDict(word).search()
    results = None

    if not results:
      em = discord.Embed(
        description=f'😢 I can\'t find the definition of the word **`{word}`**',
        color=0xFF2030
      )
      await ctx.send(embed=em)

    pages = Menu(source=MySource(results, word), clear_reactions_after=True)
    await pages.start(ctx)
    return

  @define.error
  async def on_define_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
      embed = discord.Embed(description=f"Usage:\n> **`/define <word>`** ",
                            color=0xFF2030)
      return await ctx.send(embed=embed)

    raise error


async def setup(bot):
  await bot.add_cog(Misc(bot))
