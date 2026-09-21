import discord
import os
import asyncio
import re
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from src.role_assigment_message import RoleView
from src.bot import client
from src.log_instance import logger
from src.functions import send_it_logs_message, set_server_nickname

load_dotenv()

TARGET_GUILD_ID = int(os.getenv("TOGETHERNET_SERVER_GUILD_ID"))
STYRELSE_ROLE_ID = int(os.getenv("STYRELSE_ROLE_ID"))

@client.tree.command(
    name="deploy-role-selector",
    description="Sends the role selection message into the channel.",
    guild=discord.Object(id=TARGET_GUILD_ID),
)
@app_commands.checks.has_role(STYRELSE_ROLE_ID)
async def deploy_role_selector(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Togethernet roller",
        description="Genom att klicka en av knapparna ner kan du gå in i ett eller flera av våra utskott!",
        color=discord.Color.orange(),
    )
    await interaction.channel.send(embed=embed, view=RoleView())
    await interaction.response.send_message(
        "Rolväljaren har skickats!", ephemeral=True
    )
    logger.info(
        f"{interaction.user.name} triggered deploy_role_selector in {interaction.channel.name}"
    )
    await send_it_logs_message(
        f"{interaction.user.name} triggered deploy_role_selector in {interaction.channel.mention}"
    )

@deploy_role_selector.error
async def deploy_role_selector_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(
            "Du saknar behörighet (Styrelse-rollen) för att använda detta kommando.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            f"Ett fel uppstod: {error}", ephemeral=True
        )

@client.tree.command(
    name="force-sync-names",
    description="Sync all members' nicknames with SSIS server.",
    guild=discord.Object(id=TARGET_GUILD_ID),
)
@app_commands.checks.has_role(STYRELSE_ROLE_ID)
async def force_sync_names(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    guild = client.get_guild(TARGET_GUILD_ID) or await client.fetch_guild(TARGET_GUILD_ID)
    if not guild:
        await interaction.followup.send("Failed to locate the guild.", ephemeral=True)
        return
    processed = 0
    failed = 0
    batch = 0
    logger.info("Started execution of force_sync_names")
    await send_it_logs_message("# Started execution of ``force_sync_names``")

    async for member in guild.fetch_members(limit=None):
        if member.bot:
            continue
        if member.nick and re.search(r".+ \(TE\d{2}[A-Za-z]\)$", member.nick):
            continue
        try:
            await set_server_nickname(member.id)
            processed += 1
        except Exception:
            failed += 1
            logger.exception("Error syncing nickname for member %s", member.id)
        batch += 1
        if batch >= 100:
            await asyncio.sleep(16 * 60)
            batch = 0
    logger.info(f"Sync complete. Processed {processed} members, {failed} failures.")
    await send_it_logs_message(f"# Sync complete. Processed {processed} members, {failed} failures.")
    await interaction.followup.send(
        f"Sync complete. Processed {processed} members, {failed} failures.",
        ephemeral=True,
    )

@client.tree.command(
    name="numbers-of-formatted-nicknames",
    description="Show the number of properly formatted nicknames.",
    guild=discord.Object(id=TARGET_GUILD_ID),
)
@app_commands.checks.has_role(STYRELSE_ROLE_ID)
async def numbers_of_formatted_nicknames(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    guild = client.get_guild(TARGET_GUILD_ID) or await client.fetch_guild(TARGET_GUILD_ID)
    if not guild:
        await interaction.followup.send("Failed to locate the guild.", ephemeral=True)
        return

    formatted_num = 0

    for member in guild.fetch_members(limit=None):
        if member.bot:
            continue
        if member.nick and re.search(r".+ \(TE\d{2}[A-Za-z]\)$", member.nick):
            formatted_num += 1
    await interaction.followup.send(
        f"Number of properly formatted nicknames: {formatted_num}",
        ephemeral=True,
    )