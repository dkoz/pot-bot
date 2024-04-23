import discord
from discord.ext import commands
from discord import app_commands
from utils.database import Database

class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database("players.db")

    @app_commands.command(name="link", description="Link your Discord ID to your Alderon ID")
    async def link(self, interaction: discord.Interaction, alderon_id: str):
        discord_id = interaction.user.id
        discord_name = interaction.user.name

        try:
            self.db.link_discord_to_alderon(discord_id, discord_name, alderon_id)
            await interaction.response.send_message("Your Discord ID is now linked with your Alderon ID.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")

    @app_commands.command(name="me", description="Get your player profile information")
    async def me(self, interaction: discord.Interaction):
        discord_id = interaction.user.id
        alderon_id = self.db.get_player_by_discord_id(discord_id)

        if alderon_id:
            player_profile = self.db.get_player(alderon_id)
            if player_profile and len(player_profile) >= 6:
                _, name, alderon_id, kills, deaths, dinosaur, location = player_profile

                k_d_ratio = kills / deaths if deaths > 0 else float("inf")

                response = (
                    f"Name: {name}\n"
                    f"Alderon ID: {alderon_id}\n"
                    f"Dinosaur: {dinosaur}\n"
                    f"Location: {location}\n"
                    f"Kills: {kills}\n"
                    f"Deaths: {deaths}\n"
                )
                await interaction.response.send_message(response)
            else:
                await interaction.response.send_message("Player profile not found or incomplete.")
        else:
            await interaction.response.send_message("Your Discord ID isn't linked to any Alderon ID.")

    @app_commands.command(name="search", description="Search for a player's profile")
    async def search(self, interaction: discord.Interaction, player_name: str):
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT name FROM players WHERE name LIKE ?", (f"%{player_name}%",))
        results = cursor.fetchall()

        if results:
            suggestions = ", ".join(row[0] for row in results)
            await interaction.response.send_message(f"Matches: {suggestions}")
        else:
            await interaction.response.send_message("No matching players found.")

    @search.autocomplete("player_name")
    async def search_autocomplete(self, interaction: discord.Interaction, current: str):
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT name FROM players WHERE name LIKE ?", (f"%{current}%",))
        results = cursor.fetchall()

        if results:
            return [app_commands.Choice(name=row[0], value=row[0]) for row in results]
        else:
            return []

async def setup(bot):
    await bot.add_cog(PlayerCog(bot))
