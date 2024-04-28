import json
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils.rcon_protocol import rcon_command
from utils.weather_forecast import get_weather_update, weather_emojis
import asyncio
import os
import logging

class WeatherControlCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_config = self.load_config()
        self.data_path = os.path.join('data', 'season.json')
        self.current_season, self.current_server = self.load_season()
        self.weather_channel = None
        self.forecast_channel = None
        self.pattern_channel = None
        self.weather_task = None
        self.bot.loop.create_task(self.init_channels())

    async def init_channels(self):
        await self.bot.wait_until_ready()
        self.weather_channel = self.bot.get_channel(self.server_config["WEATHER_CHANNEL"])
        self.forecast_channel = self.bot.get_channel(self.server_config["WEATHER_REPORT"])
        self.pattern_channel = self.bot.get_channel(self.server_config["WEATHER_PATTERN"])
        if self.current_season and self.current_server:
            if self.weather_task is None:
                self.weather_task = self.weather_update
            if not self.weather_task.is_running():
                self.weather_task.start(self.current_server)
            await self.update_channels(self.current_season)

    async def update_channels(self, season):
        weather_message, selected_weather = get_weather_update(season)

        if self.pattern_channel:
            new_pattern_name = f"Season: {season.capitalize()}"
            if self.pattern_channel.name != new_pattern_name:
                await self.pattern_channel.edit(name=new_pattern_name)

    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    def load_season(self):
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            return data.get('current_season', None), data.get('current_server', None)
        except FileNotFoundError:
            logging.error("Season data file not found.")
            return None, None

    def save_season(self, season, server):
        with open(self.data_path, 'w') as f:
            json.dump({'current_season': season, 'current_server': server}, f)

    async def server_autocomplete(self, interaction: discord.Interaction, current: str):
        server_names = [name for name in self.server_config["RCON_SERVERS"] if current.lower() in name.lower()]
        choices = [app_commands.Choice(name=name, value=name) for name in server_names]
        return choices

    async def season_autocomplete(self, interaction: discord.Interaction, current: str):
        seasons = ["Wet", "Dry", "Temperate", "Cold"]
        filtered_seasons = [season for season in seasons if current.lower() in season.lower()]
        choices = [app_commands.Choice(name=season, value=season) for season in filtered_seasons]
        return choices
    
    async def weather_autocomplete(self, interaction: discord.Interaction, current: str):
        weathers = ["ClearSky", "Rain", "Fog", "Overcast", "Storm", "Snow"]
        filtered_weathers = [weather for weather in weathers if current.lower() in weather.lower()]
        choices = [app_commands.Choice(name=weather, value=weather) for weather in filtered_weathers]
        return choices

    group = app_commands.Group(name="weather", description="Set the weather pattern for a server", default_permissions=discord.Permissions(administrator=True))

    @group.command(name="setweather", description="Force switch the weather through RCON.")
    @app_commands.autocomplete(server=server_autocomplete, weather=weather_autocomplete)
    @app_commands.describe(weather="The weather pattern to set", server="The server to apply the weather pattern to.")
    async def set_weather(self, interaction: discord.Interaction, weather: str, server: str):
        await interaction.response.defer(ephemeral=True)
        await rcon_command(self.server_config, server, f"weather {weather}")
        await interaction.followup.send(f"Weather set to {weather} on {server}.")

    @group.command(name="setseason", description="Set the weather pattern for a server.")
    @app_commands.autocomplete(server=server_autocomplete, season=season_autocomplete)
    @app_commands.describe(season="The season to set which determines the weather pattern", server="The server to apply the weather pattern to.")
    async def set_season(self, interaction: discord.Interaction, season: str, server: str):
        if season.capitalize() not in ["Wet", "Dry", "Temperate", "Cold"]:
            await interaction.response.send_message(f"Invalid season. Choose from Wet, Dry, Temperate, Cold.")
            return

        self.current_season = season.capitalize()
        self.current_server = server
        self.save_season(self.current_season, self.current_server)

        await rcon_command(self.server_config, server, f"announce Season set to {self.current_season} on {server}")

        if self.weather_task and self.weather_task.is_running():
            self.weather_task.cancel()
            await asyncio.sleep(1)

        self.weather_task.start(server)
        await self.update_channels(self.current_season)
        await interaction.response.send_message(f"Weather pattern set to {self.current_season} on {server}.")

    @tasks.loop(minutes=5)
    async def weather_update(self, server):
        if self.current_season is None or server not in self.server_config["RCON_SERVERS"]:
            logging.info("No valid season or server config found; aborting task.")
            return

        weather_message, selected_weather = get_weather_update(self.current_season)

        if self.weather_channel:
            embed = discord.Embed(title=f"Weather on Panjura", description=weather_message, color=discord.Color.blue())
            emoji_url = weather_emojis.get(selected_weather, "")
            if emoji_url:
                embed.set_thumbnail(url=emoji_url)
            await self.weather_channel.send(embed=embed)

        await asyncio.sleep(13)

        new_name = f"Forecast: {selected_weather.capitalize()}"
        if self.forecast_channel and self.forecast_channel.name != new_name:
            try:
                await self.forecast_channel.edit(name=new_name)
                logging.info("Forecast channel name updated successfully.")
            except discord.HTTPException as e:
                logging.error(f"Failed to edit channel name due to rate limiting or other HTTP issue: {e}")

        command = f"weather {selected_weather}"
        await rcon_command(self.server_config, server, command)

async def setup(bot):
    await bot.add_cog(WeatherControlCog(bot))
