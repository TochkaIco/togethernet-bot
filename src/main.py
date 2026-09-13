import os
import discord
import aiohttp
from dotenv import load_dotenv
from src.logger import setup_logging

load_dotenv()

logger = setup_logging()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

token = os.environ.get("BOT_TOKEN")
if not token:
    logger.critical("BOT_TOKEN is not set in environment variables.")
    raise SystemExit(1)

client.run(token, log_handler=None)