import nextcord
from nextcord.ext import commands
import json
import os
import a2s
import config

class QueryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_config()

    def load_config(self):
        config_path = os.path.join('data', 'config.json')
        with open(config_path) as config_file:
            config = json.load(config_file)
            self.servers = config["RCON_SERVERS"]

    async def autocomplete_server(self, interaction: nextcord.Interaction, current: str):
        choices = [server for server in self.servers if current.lower() in server.lower()]
        await interaction.response.send_autocomplete(choices)

    @nextcord.slash_command(name="query", description="Query a game server's status")
    async def query(self, interaction: nextcord.Interaction, server_name: str = nextcord.SlashOption(description="Select a server", autocomplete=True)):
        server_info = self.servers.get(server_name)
        if server_info:
            try:
                address = (server_info["RCON_HOST"], server_info["QUERY_PORT"])
                info = a2s.info(address)
                embed = nextcord.Embed(title=server_name + " Status", color=nextcord.Color.blue())
                embed.add_field(name="Server Name", value=info.server_name, inline=False)
                embed.add_field(name="Map", value=info.map_name, inline=True)
                embed.add_field(name="Players", value=f"{info.player_count}/{info.max_players}", inline=True)
                embed.add_field(name="Game", value=info.game, inline=True)
                embed.add_field(name="Address", value=f"{server_info['RCON_HOST']}:{server_info['QUERY_PORT']}", inline=False)
                embed.set_thumbnail(url="https://i.imgur.com/830cdKn.png")
                embed.set_footer(text=config.footer + " | " + config.version, icon_url=self.bot.user.avatar.url)
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                await interaction.response.send_message(f"Error querying server: {e}")
        else:
            await interaction.response.send_message("Server not found.")

    @query.on_autocomplete("server_name")
    async def on_autocomplete_rcon(self, interaction: nextcord.Interaction, current: str):
        await self.autocomplete_server(interaction, current)

def setup(bot):
    bot.add_cog(QueryCog(bot))
