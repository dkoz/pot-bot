import json
import discord
from discord.ext import commands
from discord import app_commands
from gamercon_async import GameRCON
import asyncio
import logging

class RconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_config = self.load_config()

    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    async def rcon_command(self, server_name, command):
        server = self.server_config["RCON_SERVERS"].get(server_name)
        if not server:
            logging.error(f"Server not found: {server_name}")
            return "Server not found."
        async with GameRCON(server["RCON_HOST"], server["RCON_PORT"], server["RCON_PASS"]) as pc:
            try:
                return await asyncio.wait_for(pc.send(command), timeout=10.0)
            except asyncio.TimeoutError:
                logging.error(f"Command timed out: {server_name} {command}")
                return "Command timed out."
            except Exception as e:
                logging.error(f"Error sending command: {e}")
                return f"Error sending command: {e}"

    async def server_autocomplete(self, interaction: discord.Interaction, current: str):
        server_names = [name for name in self.server_config["RCON_SERVERS"] if current.lower() in name.lower()]
        choices = [app_commands.Choice(name=name, value=name) for name in server_names]
        
        return choices
    
    group = app_commands.Group(name="rcon", description="Remote console command sender", default_permissions=discord.Permissions(administrator=True))

    @group.command(name="command", description="Send a remote RCON command to a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(command="The command to send", server="The server to send the command to.")
    async def command(self, interaction: discord.Interaction, command: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await self.rcon_command(server, command)
        
        embed = discord.Embed(title=server, color=discord.Color.green())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RconCog(bot))