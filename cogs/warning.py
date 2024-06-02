from discord.ext import commands
from discord import app_commands
import discord
from utils.database import Database

class WarningCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database("players.db")

    group = app_commands.Group(name="warning", description="Control warnings on users.", default_permissions=discord.Permissions(administrator=True))

    @group.command(name="add", description="Add warning points to a user")
    @app_commands.describe(user="The user to warn", points="Number of points to add")
    async def add_warning(self, interaction: discord.Interaction, user: discord.Member, points: int):
        self.db.add_or_update_warning(user.id, user.display_name, points)
        await interaction.response.send_message(f"Added {points} warning points to {user.display_name}.")

    @group.command(name="remove", description="Remove warning points from a user")
    @app_commands.describe(user="The user from whom to remove warning points", points="Number of points to remove")
    async def remove_warning(self, interaction: discord.Interaction, user: discord.Member, points: int):
        current_points = self.db.get_warnings(user.id)
        new_points = max(0, current_points - points)
        self.db.add_or_update_warning(user.id, user.display_name, new_points - current_points)
        await interaction.response.send_message(f"Removed {points} warning points from {user.display_name}. Now has {new_points} points.")

    @group.command(name="check", description="Check the warning points of a user")
    @app_commands.describe(user="The user whose warning points to check")
    async def check_warnings(self, interaction: discord.Interaction, user: discord.Member):
        warning_points = self.db.get_warnings(user.id)
        await interaction.response.send_message(f"{user.display_name} has {warning_points} warning points.")

async def setup(bot):
    await bot.add_cog(WarningCog(bot))
