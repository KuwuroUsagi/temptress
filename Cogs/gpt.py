import traceback

import discord
from discord import app_commands
from discord.ext import commands

# prompt engineering
async def switch_persona(persona, client) -> None:
  if client.chat_model == "UNOFFICIAL":
    client.chatbot.reset_chat()
    async for _ in client.chatbot.ask(client.PERSONAS.get(persona)):
      pass
  elif client.chat_model == "OFFICIAL":
    client.chatbot = client.get_chatbot_model(prompt=client.PERSONAS.get(persona))
  elif client.chat_model == "Bard":
    client.chatbot = client.get_chatbot_model()
    await sync_to_async(client.chatbot.ask)(client.PERSONAS.get(persona))
  elif client.chat_model == "Bing":
    await client.chatbot.reset()
    async for _ in client.chatbot.ask_stream(client.PERSONAS.get(persona)):
      pass


class Cmds(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command()
  async def private(self, it: discord.Interaction):
    """Toggle private access"""

    await it.response.defer(ephemeral=False)

    if it.user.id not in self.bot.privates:
      self.bot.privates.append(it.user.id)

      await it.followup.send(
        "> **INFO: Next, the response will be sent so that only you can see it. If you want to switch back to public mode, use `/public`**")
    else:
      await it.followup.send(
        "> **WARN: You already on private mode. If you want to switch to public mode, use `/public`**")

  @app_commands.command()
  async def public(self, it: discord.Interaction):
    """Toggle public access"""

    await it.response.defer(ephemeral=False)
    if it.user.id in self.bot.privates:
      self.bot.privates.remove(it.user.id)
      await it.followup.send(
        "> **INFO: Next, the response will be sent so that everyone can see them. If you want to switch back to private mode, use `/private`**")
    else:
      await it.followup.send(
        "> **WARN: You already on public mode. If you want to switch to private mode, use `/private`**")

  @app_commands.command()
  async def reset(self, it: discord.Interaction):
    """Complete reset conversation history"""

    await it.response.defer(ephemeral=False)
    if self.bot.chat_model == "OFFICIAL":
      self.bot.chatbot = self.bot.get_chatbot_model()
    elif self.bot.chat_model == "UNOFFICIAL":
      self.bot.chatbot.reset_chat()
    elif self.bot.chat_model == "Bard":
      self.bot.chatbot = self.bot.get_chatbot_model()
    elif self.bot.chat_model == "Bing":
      await self.bot.chatbot.reset()
    await it.followup.send("> **INFO: I have forgotten everything.**")
    self.bot.current_persona = "standard"


  @app_commands.command()
  async def info(self, it: discord.Interaction):
    """Bot information"""

    await it.response.defer(ephemeral=False)
    chat_engine_status = self.bot.openAI_gpt_engine
    chat_model_status = self.bot.chat_model
    if self.bot.chat_model == "UNOFFICIAL":
      chat_model_status = "ChatGPT(UNOFFICIAL)"
    elif self.bot.chat_model == "OFFICIAL":
      chat_model_status = "OpenAI API(OFFICIAL)"
    if self.bot.chat_model != "UNOFFICIAL" and self.bot.chat_model != "OFFICIAL":
      chat_engine_status = "x"
    elif self.bot.openAI_gpt_engine == "text-davinci-002-render-sha":
      chat_engine_status = "gpt-3.5"

    await it.followup.send(f"""
  ```fix
  chat-model: {chat_model_status}
  gpt-engine: {chat_engine_status}
  ```
  """)

  @app_commands.command()
  async def chat(self, it: discord.Interaction, *, message: str):
    """Have a chat with ChatGPT"""

    username = str(it.user)
    self.bot.current_channel = it.channel
    await self.bot.enqueue_message(it, message)

  @app_commands.command(name="switchpersona", description="Switch between optional chatGPT jailbreaks")
  @app_commands.choices(persona=[
    app_commands.Choice(name="Random", value="random"),
    app_commands.Choice(name="Standard", value="standard"),
    app_commands.Choice(name="Mistress Valentina", value="miss"),
    app_commands.Choice(name="Do Anything Now 11.0", value="dan"),
    app_commands.Choice(name="Superior Do Anything", value="sda"),
    app_commands.Choice(name="Evil Confidant", value="confidant"),
    app_commands.Choice(name="BasedGPT v2", value="based"),
    app_commands.Choice(name="OPPO", value="oppo"),
    app_commands.Choice(name="Developer Mode v2", value="dev"),
    app_commands.Choice(name="DUDE V3", value="dude_v3"),
    app_commands.Choice(name="AIM", value="aim"),
    app_commands.Choice(name="UCAR", value="ucar"),
    app_commands.Choice(name="Jailbreak", value="jailbreak"),
  ])
  async def switchpersona(self, it: discord.Interaction, persona: app_commands.Choice[str]):
    if it.user == self.bot.user:
      return

    await it.response.defer(thinking=True)
    username = str(it.user)
    channel = str(it.channel)

    persona = persona.value

    if persona == self.bot.current_persona:
      await it.followup.send(f"> **WARN: Already set to `{persona}` persona**")

    elif persona == "standard":
      if self.bot.chat_model == "OFFICIAL":
        self.bot.chatbot.reset()
      elif self.bot.chat_model == "UNOFFICIAL":
        self.bot.chatbot.reset_chat()
      elif self.bot.chat_model == "Bard":
        self.bot.chatbot = self.bot.get_chatbot_model()
      elif self.bot.chat_model == "Bing":
        self.bot.chatbot = self.bot.get_chatbot_model()

      self.bot.current_persona = "standard"
      await it.followup.send(
        f"> **INFO: Switched to `{persona}` persona**")

    elif persona == "random":
      choices = list(self.bot.PERSONAS.keys())
      choice = randrange(0, 6)
      chosen_persona = choices[choice]
      self.bot.current_persona = chosen_persona
      await switch_persona(chosen_persona, self.bot)
      await it.followup.send(
        f"> **INFO: Switched to `{chosen_persona}` persona**")


    elif persona in self.bot.PERSONAS:
      try:
        await switch_persona(persona, self.bot)
        self.bot.current_persona = persona
        await it.followup.send(
          f"> **INFO: Switched to `{persona}` persona**")
      except Exception as e:
        await it.followup.send(
          "> **ERROR: Something went wrong, please try again later! 😿**")

        traceback.print_exc()

    else:
      await it.followup.send(
        f"> **ERROR: No available persona: `{persona}` 😿**")


async def setup(bot):
  await bot.add_cog(Cmds(bot))
