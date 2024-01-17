import json
import os
import nextcord
from nextcord.ext import commands
from gamercon_async import GameRCON

class RconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_config()

    def load_config(self):
        config_path = os.path.join('data', 'config.json')
        with open(config_path) as config_file:
            config = json.load(config_file)
            self.servers = config["RCON_SERVERS"]

    async def rcon_command(self, server_name, command):
        server = self.servers.get(server_name)
        if not server:
            return f"Server '{server_name}' not found."

        try:
            async with GameRCON(server["RCON_HOST"], server["RCON_PORT"], server["RCON_PASS"]) as pc:
                return await pc.send(command)
        except Exception as error:
            return f"Error sending command: {error}"

    async def autocomplete_server(self, interaction: nextcord.Interaction, current: str):
        choices = [server for server in self.servers if current.lower() in server.lower()]
        await interaction.response.send_autocomplete(choices)

    @nextcord.slash_command(description="Main Path of Titans server command.", default_member_permissions=nextcord.Permissions(administrator=True))
    async def rcon(self, interaction: nextcord.Interaction):
        pass

    @rcon.subcommand(description="Send a remote rcon command to Path of Titans server.")
    async def command(self, interaction: nextcord.Interaction, command: str, server: str = nextcord.SlashOption(description="Select a server", autocomplete=True)):
        response = await self.rcon_command(server, command)
        await interaction.response.send_message(f'Response: {response}')

    @command.on_autocomplete("server")
    async def on_autocomplete_rcon(self, interaction: nextcord.Interaction, current: str):
        await self.autocomplete_server(interaction, current)

def setup(bot):
    bot.add_cog(RconCog(bot))
