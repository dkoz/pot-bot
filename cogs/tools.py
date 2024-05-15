import json
import discord
from discord.ext import commands
from discord import app_commands
from utils.rcon_protocol import rcon_command

class ToolsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_config = self.load_config()
        
    def load_config(self):
        with open("config.json", "r") as f:
            return json.load(f)
        
    async def server_autocomplete(self, interaction: discord.Interaction, current: str):
        server_names = [name for name in self.server_config["RCON_SERVERS"] if current.lower() in name.lower()]
        choices = [app_commands.Choice(name=name, value=name) for name in server_names]
        
        return choices
    
    list = app_commands.Group(name="list", description="List of information on the server.", default_permissions=discord.Permissions(administrator=True))
    
    @list.command(name="players", description="List players on a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to list players from.")
    async def listplayers(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, "listplayers")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @list.command(name="roles", description="List roles on a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to list roles from.")
    async def listroles(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, "listroles")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @list.command(name="waystones", description="List waystones on a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to list waystones from.")
    async def listwaystones(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, "listwaystones")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @list.command(name="waters", description="List waters on a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to list waters from.")
    async def listwaters(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, "listwaters")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @list.command(name="poi", description="List points of interest on a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to list points of interest from.")
    async def listpoi(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, "listpoi")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    quests = app_commands.Group(name="quests", description="Command group for quests.", default_permissions=discord.Permissions(administrator=True))

    @quests.command(name="list", description="List quests on a server.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to list quests from.")
    async def questlist(self, interaction: discord.Interaction, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, "listquests")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
  
    @quests.command(name="give", description="Give a quest to a player.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(server="The server to give the quest on.")
    async def givequest(self, interaction: discord.Interaction, player: str, quest: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"givequest {player} {quest}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ToolsCog(bot))