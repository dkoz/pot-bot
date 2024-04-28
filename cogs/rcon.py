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

    @group.command(name="setmarks", description="Set a mark for a player.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(player="The player to set the marks for.", marks="Number of marks to give a player.", server="The server to set the mark on.")
    async def setmarks(self, interaction: discord.Interaction, player: str, marks: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"setmarks {player} {marks}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @group.command(name="setmarksall", description="Set marks for all players on the server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(marks="Number of marks to give to everyone.", server="The server to set the mark on.")
    async def setmarksall(self, interaction: discord.Interaction, marks: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"setmarksall {marks}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @group.command(name="addmarks", description="Add marks to a player.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(player="The player to add the marks to.", marks="Number of marks to give a player.", server="The server to set the mark on.")
    async def addmarks(self, interaction: discord.Interaction, player: str, marks: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"addmarks {player} {marks}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @group.command(name="removemarks", description="Remove marks from a player.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(player="The player to remove marks from.", marks="Number of marks to remove from a player.", server="Select a server to remove the marks from.")
    async def removemarks(self, interaction: discord.Interaction, player: str, marks: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"removemarks {player} {marks}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @group.command(name="restart", description="Restart the server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(seconds="Restarts the server after the specified number of seconds.", server="The server to restart.")
    async def restart(self, interaction: discord.Interaction, seconds: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"restart {seconds}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @group.command(name="whisper", description="Send a private message to a player.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(player="The player to send the message to.", message="The message to send.", server="The server to send the message from.")
    async def whisper(self, interaction: discord.Interaction, player: str, message: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"whisper {player} {message}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RconCog(bot))