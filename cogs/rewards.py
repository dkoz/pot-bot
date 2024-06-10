import json
import discord
import asyncio
from discord.ext import commands, tasks
from utils.rcon_protocol import rcon_command

class RewardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_config = self.load_config()
        self.ready = False
        self.give_marks.start()

    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    @tasks.loop(minutes=60)
    async def give_marks(self):
        if not self.ready:
            self.ready = True
            return

        marks_amount = self.server_config["MARKS_AMOUNT"]
        marks_delay = self.server_config["MARKS_DELAY"]

        for server_name in self.server_config["RCON_SERVERS"]:
            try:
                response = await rcon_command(self.server_config, server_name, "listplayers")
                player_lines = response.split('\n')[1:]

                for line in player_lines:
                    if line.strip():
                        player_name = line.split(' ')[0]
                        await rcon_command(self.server_config, server_name, f"addmarks {player_name} {marks_amount}")
                        await rcon_command(self.server_config, server_name, f"whisper {player_name} You have been awarded {marks_amount} marks for being active!")
                        print(f"Gave {marks_amount} marks to {player_name} on {server_name}")
                        await asyncio.sleep(marks_delay)
            except Exception as e:
                print(f"Error processing server {server_name}: {e}")

    @give_marks.before_loop
    async def before_give_marks(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RewardsCog(bot))
