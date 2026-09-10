import os
import discord
from dotenv import load_dotenv
from logger import setup_logging

load_dotenv()

logger = setup_logging()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

verification_messages = {}


async def set_server_nickname(member_id: int):
    try:
        ssis_id = int(os.getenv("SSIS_SERVER_GUILD_ID"))
        tog_id = int(os.getenv("TOGETHERNET_SERVER_GUILD_ID"))

        ssis_guild = client.get_guild(ssis_id) or await client.fetch_guild(ssis_id)
        ssis_member = await ssis_guild.fetch_member(member_id)
        target_name = ssis_member.nick or ssis_member.display_name
        if target_name:
            words = target_name.split()
            first_name = words[0]
            user_class = words[-1]
            target_name = first_name + ' ' + user_class

        tog_guild = client.get_guild(tog_id) or await client.fetch_guild(tog_id)
        tog_member = await tog_guild.fetch_member(member_id)

        await tog_member.edit(nick=target_name)
        logger.info("Updated %s's nickname to: %s", tog_member.name, target_name)
    except Exception:
        logger.exception("Nickname sync failed for user ID %s", member_id)


@client.event
async def on_member_join(member):
    try:
        msg = await member.send(
            f"Welcome {member.mention}! React with ✅ to verify and get your role."
        )
        await msg.add_reaction("✅")
        verification_messages[member.id] = msg.id
    except discord.Forbidden:
        logger.warning("Could not send DM to %s (DMs closed).", member.name)


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if str(reaction.emoji) not in ["✅", "\u2705"]:
        return

    expected_msg_id = verification_messages.get(user.id)
    if expected_msg_id and reaction.message.id == expected_msg_id:
        tog_id = os.getenv("TOGETHERNET_SERVER_GUILD_ID")
        role_id = os.getenv("TOGETHERNET_ROLE_ID")

        if tog_id and role_id:
            try:
                guild = client.get_guild(int(tog_id)) or await client.fetch_guild(int(tog_id))

                role = guild.get_role(int(role_id))
                if not role:
                    role = await guild.fetch_role(int(role_id))

                tog_member = guild.get_member(user.id) or await guild.fetch_member(user.id)

                if role and tog_member:
                    await tog_member.add_roles(role)
                    logger.info("Assigned role '%s' to %s", role.name, tog_member.name)
            except discord.Forbidden:
                logger.error(
                    "Forbidden (403): Missing permissions or role hierarchy issue while assigning role to %s",
                    user.name,
                )
            except Exception:
                logger.exception("Error assigning role to user %s", user.name)

        await set_server_nickname(user.id)
        verification_messages.pop(user.id, None)


@client.event
async def on_ready():
    logger.info("Logged in as %s", client.user)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$toogeternet"):
        await message.channel.send("toogeternet!")


token = os.environ.get("BOT_TOKEN")
if not token:
    logger.critical("BOT_TOKEN is not set in environment variables.")
    raise SystemExit(1)

client.run(token, log_handler=None)