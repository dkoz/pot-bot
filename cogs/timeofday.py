import json
from discord.ext import commands, tasks
from utils.rcon_protocol import rcon_command
import asyncio
import logging

class TimeOfDayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.gametime_channel = None
        self.bot.loop.create_task(self.init_channel())

    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    async def init_channel(self):
        await self.bot.wait_until_ready()
        self.gametime_channel = self.bot.get_channel(self.config["GAMETIME_CHANNEL"])
        if self.gametime_channel:
            self.update_gametime.start()

    @tasks.loop(minutes=15)
    async def update_gametime(self):
        await asyncio.sleep(5)
        server_info = await rcon_command(self.config, "Dev Server", "ServerInfo")
        time_of_day = self.extract_time(server_info)
        if time_of_day and self.gametime_channel:
            new_name = f"║🕦︱𝙲𝚞𝚛𝚛𝚎𝚗𝚝-𝚃𝚒𝚖𝚎︱{time_of_day}"
            await self.gametime_channel.edit(name=new_name)

    def extract_time(self, server_info):
        try:
            parts = server_info.split('/')
            for part in parts:
                if "TimeOfDay" in part:
                    return part.split(':')[1].strip()
        except Exception as e:
            logging.error(f"Error parsing server info: {e}")
            return None

async def setup(bot):
    await bot.add_cog(TimeOfDayCog(bot))
