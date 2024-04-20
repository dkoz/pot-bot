import json
import discord
from discord.ext import commands
from discord import app_commands
from utils.rcon_protocol import rcon_command

class RconCog(commands.Cog):
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
    
    group = app_commands.Group(name="rcon", description="Remote console command sender", default_permissions=discord.Permissions(administrator=True))

    @group.command(name="command", description="Send a remote RCON command to a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(command="The command to send", server="The server to send the command to.")
    async def command(self, interaction: discord.Interaction, command: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, command)
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @group.command(name="listplayers", description="List players on a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to list players from.")
    async def listplayers(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, "listplayers")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @group.command(name="announce", description="Send an announcement to a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(message="The message to send", server="The server to send the message to.")
    async def announce(self, interaction: discord.Interaction, message: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"announce {message}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @group.command(name="kick", description="Kick a player from a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(player="The player to kick", reason="The reason for kicking the player.", server="The server to kick the player from.")
    async def kick(self, interaction: discord.Interaction, player: str, reason: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"kick {player} {reason}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @group.command(name="ban", description="Ban a player from a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(player="The player to ban", duration="The duration of the ban", reason="The reason for banning the player.", userreason="The reason shown to the user.", server="The server to ban the player from.")
    async def ban(self, interaction: discord.Interaction, player: str, duration: str, reason: str, userreason: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f'ban {player} {duration} "{reason}" "{userreason}"')
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RconCog(bot))