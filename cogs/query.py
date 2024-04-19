import discord
from discord.ext import commands
from discord import app_commands
import json
import a2s
import logging

class QueryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_config = self.load_config()

    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    async def server_autocomplete(self, interaction: discord.Interaction, current: str):
        server_names = [name for name in self.server_config["RCON_SERVERS"] if current.lower() in name.lower()]
        choices = [app_commands.Choice(name=name, value=name) for name in server_names]
        return choices

    group = app_commands.Group(name="query", description="Query game server status", default_permissions=discord.Permissions(administrator=True))

    @group.command(name="status", description="Query a game server's status.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to query.")
    async def status(self, interaction: discord.Interaction, server: str):
        server_info = self.server_config["RCON_SERVERS"].get(server)
        if server_info:
            try:
                address = (server_info["RCON_HOST"], server_info["QUERY_PORT"])
                info = a2s.info(address)
                embed = discord.Embed(title=f"{server} Status", color=discord.Color.blue())
                embed.add_field(name="Server Name", value=info.server_name, inline=False)
                embed.add_field(name="Map", value=info.map_name, inline=True)
                embed.add_field(name="Players", value=f"{info.player_count}/{info.max_players}", inline=True)
                embed.add_field(name="Game", value=info.game, inline=True)
                embed.add_field(name="Address", value=f"{server_info['RCON_HOST']}:{server_info['QUERY_PORT']}", inline=False)
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                logging.error(f"Error querying server: {e}")
                await interaction.response.send_message(f"Error querying server: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("Server not found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QueryCog(bot))
