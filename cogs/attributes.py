import json
import discord
from discord.ext import commands
from discord import app_commands
from utils.rcon_protocol import rcon_command
from utils.attributes import attributes_list

class AttributesCog(commands.Cog):
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
    
    async def attribute_autocomplete(self, interaction: discord.Interaction, current: str):
        filtered_attributes = [attr for attr in attributes_list if current.lower() in attr.lower()]
        limited_choices = filtered_attributes[:25]
        choices = [app_commands.Choice(name=attr, value=attr) for attr in limited_choices]
        
        return choices
    
    group = app_commands.Group(name="attributes", description="Control users attributes.", default_permissions=discord.Permissions(administrator=True))

    @group.command(name="set", description="Set a user's attribute.")
    @app_commands.autocomplete(server=server_autocomplete, attribute=attribute_autocomplete)
    @app_commands.describe(user="The user to set the attribute for.", attribute="The attribute to set.", value="The value to set the attribute to.")
    async def set(self, interaction: discord.Interaction, user: str, attribute: str, value: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"setattr {user} {attribute} {value}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)
        
    @group.command(name="get", description="Get a user's attribute.")
    @app_commands.autocomplete(server=server_autocomplete, attribute=attribute_autocomplete)
    @app_commands.describe(user="The user to get the attribute for.", attribute="The attribute to get.")
    async def get(self, interaction: discord.Interaction, user: str, attribute: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"getattr {user} {attribute}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @group.command(name="getall", description="Get all attributes for a user.")
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(user="The user to get all attributes for.")
    async def getall(self, interaction: discord.Interaction, user: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"getallattr {user}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)

    @group.command(name="setall", description="Set an attribute for all users.")
    @app_commands.autocomplete(server=server_autocomplete, attribute=attribute_autocomplete)
    @app_commands.describe(attribute="The attribute to set.", value="The value to set the attribute to.")
    async def setall(self, interaction: discord.Interaction, attribute: str, value: str, server: str):
        await interaction.response.defer(ephemeral=True)

        response = await rcon_command(self.server_config, server, f"setattrall {attribute} {value}")
        
        embed = discord.Embed(title=server, color=discord.Color.blurple())
        embed.description = f"**Response:** {response}"
        await interaction.followup.send(embed=embed)



async def setup(bot):
    await bot.add_cog(AttributesCog(bot))