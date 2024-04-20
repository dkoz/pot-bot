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
                embed.add_field(name=info.server_name, value=info.game, inline=False)
                embed.add_field(name="Map", value=info.map_name, inline=True)
                embed.add_field(name="Players", value=f"{info.player_count}/{info.max_players}", inline=True)
                embed.add_field(name="Version", value=info.version, inline=True)
                embed.add_field(name="Connect", value=f"```{server_info['RCON_HOST']}:{server_info['SERVER_PORT']}```", inline=False)
                await interaction.response.send_message(embed=embed)
                
                players = a2s.players(address)
                embed_players = discord.Embed(title=f"{server} Players", color=discord.Color.blue())
                
                player_display = ""
                for index, player in enumerate(players):
                    if index % 30 == 0 and index != 0:
                        embed_players.add_field(name="Players", value=player_display, inline=True)
                        player_display = ""
                    player_display += f"{player.name} ({player.score})\n"
                
                if player_display:
                    embed_players.add_field(name="Players", value=player_display, inline=True)
                
                await interaction.followup.send(embed=embed_players)
            except Exception as e:
                logging.error(f"Error querying server: {e}")
                await interaction.followup.send(f"Error querying server: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("Server not found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QueryCog(bot))
