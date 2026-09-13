import os
import discord
from dotenv import load_dotenv
from src.functions import set_server_nickname, send_it_logs_message
from src.bot import client, logger

load_dotenv()

verification_messages = {}

@client.event
async def on_member_join(member):
    target_guild_id = int(os.getenv("TOGETHERNET_SERVER_GUILD_ID"))
    if target_guild_id is None or member.guild.id != int(target_guild_id):
        return

    try:
        msg = await member.send(
            f"Vällkommen {member.mention}! Reagera med ✅ för att verifiera dig och få sin togethernet-roll."
        )
        await msg.add_reaction("✅")
        verification_messages[member.id] = msg.id
    except discord.Forbidden:
        logger.warning("Could not send DM to %s (DMs closed).", member.name)
        await send_it_logs_message(f"Could not send DM to {member.name} (DMs closed) on member join.")


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if str(reaction.emoji) not in ["✅", "\u2705"]:
        return

    expected_msg_id = verification_messages.get(user.id)
    if expected_msg_id and reaction.message.id == expected_msg_id:
        tog_id = os.getenv("TOGETHERNET_SERVER_GUILD_ID")
        tog_role_id = os.getenv("TOGETHERNET_ROLE_ID")
        minion_role_id = os.getenv("MINION_ROLE_ID")

        if tog_id and tog_role_id:
            try:
                guild = client.get_guild(int(tog_id)) or await client.fetch_guild(int(tog_id))

                tog_role = guild.get_role(int(tog_role_id))
                if not tog_role:
                    tog_role = await guild.fetch_role(int(tog_role_id))

                minion_role = guild.get_role(int(minion_role_id))
                if not minion_role:
                    minion_role = await guild.fetch_role(int(minion_role_id))

                tog_member = guild.get_member(user.id) or await guild.fetch_member(user.id)

                if minion_role and tog_member:
                    await tog_member.add_roles(minion_role)
                    logger.info("Assigned role '%s' to %s", minion_role.name, tog_member.name)
                    await send_it_logs_message(f"Assigned role {minion_role.name} to {tog_member.name}")

                nickname_fetch_resp = await set_server_nickname(user.id)
                verification_messages.pop(user.id, None)

                if tog_role and tog_member and nickname_fetch_resp != 'external-user':
                    await tog_member.add_roles(tog_role)
                    logger.info("Assigned role '%s' to %s", tog_role.name, tog_member.name)
                    await send_it_logs_message(f"Assigned role {tog_role.name} to {tog_member.name}")
                elif nickname_fetch_resp == 'external-user':
                    ssis_server_invite_url = "https://discord.ssis.nu"
                    await tog_member.send(f"Du är inte med i [SSIS-huvudservern]({ssis_server_invite_url}) än och kan därför inte få Togethernet-rollen. Gå med i [SSIS-servern]({ssis_server_invite_url}) först, och gå sedan ur och in i denna server igen för att få din roll!")
            except discord.Forbidden:
                logger.error(
                    "Forbidden (403): Missing permissions or role hierarchy issue while assigning role to %s",
                    user.name,
                )
            except Exception:
                logger.exception("Error assigning role to user %s", user.name)
                await send_it_logs_message(f"Error assigning role to user {user.name}")

@client.event
async def on_ready():
    logger.info("Logged in as %s", client.user)
    await send_it_logs_message(f"Bot restarted. Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("toogeternet"):
        await message.channel.send("toogeternet!")