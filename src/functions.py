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

async def set_server_nickname(member_id: int):
    try:
        tog_id = int(os.getenv("TOGETHERNET_SERVER_GUILD_ID"))
        user = await client.fetch_user(member_id)
        discord_username = user.name

        ssis_bot_api_url = "https://ssis-bot-ssis-bot-v2.apps.okd.ssis.nu/api/togethernet/lookup-student"
        ssis_bot_token = os.getenv("SSIS_BOT_TOKEN", "secret-token")
        headers = {"Authorization": f"Bearer {ssis_bot_token}", "Content-Type": "application/json", "accept": "application/json"}
        payload = {"discordUsername": discord_username}
        async with aiohttp.ClientSession() as session:
            async with session.post(ssis_bot_api_url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Lookup request failed with status {resp.status}")
                data = await resp.json()

        first_name = data.get('name').split()[0]
        user_class = data.get('class') or 'CLASS NOT FOUND'
        target_name = f"{first_name} ({user_class})"

        tog_guild = client.get_guild(tog_id) or await client.fetch_guild(tog_id)
        tog_member = await tog_guild.fetch_member(member_id)

        await tog_member.edit(nick=target_name)
        logger.info("Updated %s's nickname to: %s", tog_member.name, target_name)
    except Exception:
        logger.exception("Nickname sync failed for user ID %s", member_id)