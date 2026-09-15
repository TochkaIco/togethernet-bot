import discord
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from src.role_assigment_message import RoleView
from src.bot import client
from src.log_instance import logger
from src.functions import send_it_logs_message

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