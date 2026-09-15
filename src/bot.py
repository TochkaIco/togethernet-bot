import os
import discord
from discord import app_commands

from src.role_assigment_message import RoleView
from src.log_instance import logger

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.reactions = True

class BotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(RoleView())

        guild = discord.Object(id=int(os.getenv("TOGETHERNET_SERVER_GUILD_ID")))
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info("Command tree synced successfully.")

client = BotClient(intents=intents)