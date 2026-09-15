import discord
import os
from dotenv import load_dotenv

from src.log_instance import logger
from src.functions import send_it_logs_message

load_dotenv()

ROLE_MAP = {
    "design": int(os.getenv("DESIGN_ROLE_ID") or 0),
    "kommunikation": int(os.getenv("KOMMUNIKATION_ROLE_ID") or 0),
    "planering": int(os.getenv("PLANERING_ROLE_ID") or 0),
    "karaoke": int(os.getenv("KARAOKE_ROLE_ID") or 0),
    "film_party": int(os.getenv("FILM_PARTY_ROLE_ID") or 0),
    "patches": int(os.getenv("PATCHES_ROLE_ID") or 0),
    "ljud_ljus_kablar": int(os.getenv("LJUD_LJUS_KABLAR_ROLE_ID") or 0),
    "pant": int(os.getenv("PANT_ROLE_ID") or 0),
}


class RoleButton(discord.ui.Button):
    def __init__(self, label: str, custom_id: str, row: int):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=custom_id,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        role_id = ROLE_MAP.get(self.custom_id)
        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message(
                "Kunde inte hitta rollen. Kontakta en administratör.", ephemeral=True
            )
            return

        member = interaction.user

        if role in member.roles:
            await member.remove_roles(role, reason="Self-assigned role removal")
            await interaction.response.send_message(
                f"Tog bort **{role.name}** rollen.", ephemeral=True
            )
            logger.info(f"Removed the {role.name} role from {member.name}.")
            await send_it_logs_message(f"Removed the **{role.name}** role from {member.name}.")
        else:
            await member.add_roles(role, reason="Self-assigned role addition")
            await interaction.response.send_message(
                f"Läggde till **{role.name}** rollen!", ephemeral=True
            )
            logger.info(f"Added the {role.name} role to {member.name}!")
            await send_it_logs_message(f"Added the **{role.name}** role to {member.name}!")


class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        roles_config = [
            ("🖌️️Designutskottet", "design"),
            ("📣Kommunikationsutskottet", "kommunikation"),
            ("¿?Planeringsgruppen", "planering"),
            ("🎤Karaokegruppen", "karaoke"),
            ("🎥Filmkvällskommiten", "film_party"),
            ("Märkesgruppen", "patches"),
            ("🔊Ljud Ljus & Kablar", "ljud_ljus_kablar"),
            ("♻️Pantgruppen", "pant"),
        ]

        # 4 buttons per row
        for index, (label, custom_id) in enumerate(roles_config):
            row = index // 4
            self.add_item(RoleButton(label=label, custom_id=custom_id, row=row))