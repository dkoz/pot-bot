import discord
from discord.ext import commands
from discord import app_commands
from utils.database import Database

class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database("players.db")

    @app_commands.command(name="link", description="Link your Discord ID to your Alderon ID")
    @app_commands.describe(alderon_id="Your Alderon ID")
    async def link(self, interaction: discord.Interaction, alderon_id: str):
        discord_id = interaction.user.id
        discord_name = interaction.user.name

        try:
            self.db.link_discord_to_alderon(discord_id, discord_name, alderon_id)
            await interaction.response.send_message("Your Discord ID is now linked with your Alderon ID.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")

    @app_commands.command(name="unlink", description="Unlink your Discord ID from your Alderon ID")
    async def unlink(self, interaction: discord.Interaction):
        discord_id = interaction.user.id

        try:
            self.db.unlink_discord(discord_id)
            await interaction.response.send_message("Your Discord ID is now unlinked.")
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
                avatar_url = interaction.user.avatar.url
                
                embed = discord.Embed(
                    title=f"{name} ({alderon_id})",
                    color=discord.Color.blurple()
                )
                embed.add_field(name="Kills", value=kills, inline=True)
                embed.add_field(name="Deaths", value=deaths, inline=True)
                embed.add_field(name="Dinosaur", value=dinosaur, inline=True)
                embed.add_field(name="Location", value=location, inline=True)
                embed.set_thumbnail(url=avatar_url)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Player profile not found or incomplete.")
        else:
            await interaction.response.send_message("Your Discord ID isn't linked to any Alderon ID.")

    @app_commands.command(name="leaderboard", description="Get the top players leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        limit = 10
        top_players = self.db.get_top_kills(limit)

        if top_players:
            embed = discord.Embed(
                title="Top Players Leaderboard",
                color=discord.Color.blurple(),
            )
            for index, player in enumerate(top_players, start=1):
                _, name, alderon_id, kills, deaths, dinosaur, location = player
                embed.add_field(
                    name=f"{index}. {name} ({alderon_id})",
                    value=f"Kills: {kills} / Deaths: {deaths}",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No players found in the leaderboard.")

    @app_commands.command(name="search", description="Search for a player's profile")
    @app_commands.describe(player_name="The name of the player to search for.")
    @app_commands.default_permissions(administrator=True)
    async def search(self, interaction: discord.Interaction, player_name: str):
        player_profile = self.db.get_player_by_name(player_name)

        if player_profile:
            _, name, alderon_id, kills, deaths, dinosaur, location = player_profile
            embed = discord.Embed(
                title=f"{name} ({alderon_id})",
                color=discord.Color.blurple()
            )
            embed.add_field(name="Kills", value=kills, inline=True)
            embed.add_field(name="Deaths", value=deaths, inline=True)
            embed.add_field(name="Dinosaur", value=dinosaur, inline=True)
            embed.add_field(name="Location", value=location, inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Player profile not found or incomplete.")

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
