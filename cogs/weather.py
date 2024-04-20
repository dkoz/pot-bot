import json
import discord
from discord.ext import commands, tasks
from discord import app_commands
from gamercon_async import GameRCON
import asyncio
import random
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
        if not self.weather_channel:
            logging.error("Failed to load the Weather Channel.")
        if not self.forecast_channel:
            logging.error("Failed to load the Weather Forecast Channel.")
        if not self.pattern_channel:
            logging.error("Failed to load the Weather Pattern Channel.")

        # Automatically start the weather update task if a season and server are already set
        if self.current_season and self.current_server:
            self.weather_task = self.weather_update.start(self.current_server)

    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    def load_season(self):
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            return data.get('current_season', None), data.get('current_server', None)
        except FileNotFoundError:
            return None, None

    def save_season(self, season, server):
        with open(self.data_path, 'w') as f:
            json.dump({'current_season': season, 'current_server': server}, f)

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

    async def season_autocomplete(self, interaction: discord.Interaction, current: str):
        seasons = ["Wet", "Dry", "Temperate", "Cold"]
        filtered_seasons = [season for season in seasons if current.lower() in season.lower()]
        choices = [app_commands.Choice(name=season, value=season) for season in filtered_seasons]
        return choices

    group = app_commands.Group(name="weather", description="Manage game server weather settings")

    @group.command(name="setseason", description="Set the weather pattern for a server.")
    @app_commands.autocomplete(server=server_autocomplete, season=season_autocomplete)
    @app_commands.describe(season="The season to set which determines the weather pattern", server="The server to apply the weather pattern to.")
    async def set_season(self, interaction: discord.Interaction, season: str, server: str):
        seasons = {
            "Wet": ["rain", "storm"],
            "Dry": ["clearsky"],
            "Temperate": ["cloudy", "clearsky", "rain"],
            "Cold": ["overcast", "fog", "storm"]
        }
        if season.capitalize() not in seasons:
            await interaction.response.send_message(f"Invalid season. Choose from {', '.join(seasons.keys())}.")
            return

        self.current_season = season.capitalize()
        self.current_server = server
        self.save_season(self.current_season, self.current_server)  # Save the current season and server to file

        await self.rcon_command(server, f"announce Season set to {self.current_season} on {server}")
        if self.weather_task and self.weather_task.is_running():
            self.weather_task.cancel()
        self.weather_task = self.weather_update.start(server)
        await interaction.response.send_message(f"Weather pattern set to {self.current_season} on {server}.")

        if self.pattern_channel:
            await self.pattern_channel.edit(name=f"Season: {self.current_season}")

    @tasks.loop(minutes=5)
    async def weather_update(self, server):
        if self.current_season is None or server not in self.server_config["RCON_SERVERS"]:
            return

        weather_patterns = {
            "Wet": ["rain", "storm"],
            "Dry": ["clearsky"],
            "Temperate": ["cloudy", "clearsky", "rain"],
            "Cold": ["overcast", "fog", "storm"]
        }
        weather = random.choice(weather_patterns[self.current_season])

        message_details = {
            "rain": f"Rain with {random.randint(70, 90)}% humidity and {random.randint(10, 20)} mph winds.",
            "storm": f"Storm with {random.randint(80, 100)}% humidity and {random.randint(20, 40)} mph winds.",
            "clearsky": "Clear skies with minimal cloud cover.",
            "cloudy": "Cloudy with scattered clouds.",
            "overcast": "Overcast skies, dense with clouds.",
            "fog": "Foggy conditions reducing visibility significantly."
        }
        message = message_details.get(weather, "Weather update.")
        embed = discord.Embed(title=f"Weather Update on {server}", description=message, color=discord.Color.blue())
        try:
            if self.weather_channel:
                await self.weather_channel.send(embed=embed)
            if self.forecast_channel:
                await self.forecast_channel.edit(name=f"Forecast: {weather.capitalize()}")
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.retry_after
                await asyncio.sleep(retry_after)
                await self.weather_update(server)
            else:
                raise

async def setup(bot):
    await bot.add_cog(WeatherControlCog(bot))
