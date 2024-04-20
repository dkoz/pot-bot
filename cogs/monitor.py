import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import a2s
import logging

class MonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_file = os.path.join("data", "monitor.json")
        self.server_config = self.load_config()
        self.message_data = self.load_json()
        self.update_task.start()

    def cog_unload(self):
        self.update_task.cancel()

    def load_config(self):
        with open("config.json", "r") as f:
            return json.load(f)

    def load_json(self):
        if not os.path.exists(self.json_file):
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
            with open(self.json_file, "w") as f:
                json.dump({}, f)
        with open(self.json_file, "r") as f:
            return json.load(f)

    def save_json(self):
        with open(self.json_file, "w") as f:
            json.dump(self.message_data, f)

    async def server_autocomplete(self, interaction: discord.Interaction, current: str):
        server_names = [name for name in self.server_config["RCON_SERVERS"] if current.lower() in name.lower()]
        choices = [
            app_commands.Choice(name=name, value=name)
            for name in server_names
        ]
        return choices

    async def post_or_update_embed(self, channel, server_name, server_info):
        try:
            address = (server_info["RCON_HOST"], server_info["QUERY_PORT"])
            info = a2s.info(address)
            players = a2s.players(address)

            embed = discord.Embed(
                title=f"{server_name} Status",
                color=discord.Color.blurple(),
            )
            embed.add_field(name="Server Name", value=info.server_name, inline=False)
            embed.add_field(name="Game", value=info.game, inline=False)
            embed.add_field(name="Map", value=info.map_name, inline=True)
            embed.add_field(name="Players", value=f"{info.player_count}/{info.max_players}", inline=True)
            embed.add_field(name="Version", value=info.version, inline=True)
            embed.add_field(name="Connect", value=f"{server_info['RCON_HOST']}:{server_info['SERVER_PORT']}", inline=False)

            embed_players = discord.Embed(
                title=f"{server_name} Players",
                color=discord.Color.blurple(),
            )

            player_display = ""
            for index, player in enumerate(players):
                if index % 30 == 0 and index != 0:
                    embed_players.add_field(name="Players", value=player_display, inline=True)
                    player_display = ""
                player_display += f"{player.name} ({player.score})\n"

            if player_display:
                embed_players.add_field(name="Players", value=player_display, inline=True)

            message_data = self.message_data.get(server_name, {})
            message_id = message_data.get("message_id")
            players_message_id = message_data.get("players_message_id")

            if message_id:
                try:
                    message = await channel.fetch_message(message_id)
                    await message.edit(embed=embed)
                    if not players_message_id:
                        player_message = await channel.send(embed=embed_players)
                        message_data["players_message_id"] = player_message.id
                        self.save_json()
                    else:
                        player_message = await channel.fetch_message(players_message_id)
                        await player_message.edit(embed=embed_players)
                except discord.NotFound:
                    message = await channel.send(embed=embed)
                    player_message = await channel.send(embed=embed_players)
                    message_data["message_id"] = message.id
                    message_data["players_message_id"] = player_message.id
                    self.save_json()
            else:
                message = await channel.send(embed=embed)
                player_message = await channel.send(embed=embed_players)
                message_data["message_id"] = message.id
                message_data["players_message_id"] = player_message.id
                self.save_json()

        except Exception as e:
            logging.error(f"Error querying server '{server_name}': {e}")


    @tasks.loop(seconds=15)
    async def update_task(self):
        for server_name, server_info in self.server_config["RCON_SERVERS"].items():
            channel_id = self.message_data.get(server_name, {}).get("channel_id")

            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel is not None:
                    await self.post_or_update_embed(channel, server_name, server_info)

    @app_commands.command(name="monitor", description="Posts server status and player list embeds to a selected channel.",)
    @app_commands.autocomplete(server=server_autocomplete)
    @app_commands.describe(channel="Channel to post the embeds", server="Select a game server to post.")
    async def post_embeds(self, interaction: discord.Interaction, channel: discord.TextChannel, server: str):
        server_info = self.server_config["RCON_SERVERS"].get(server)

        if server_info:
            server_name = server
            
            await self.post_or_update_embed(channel, server_name, server_info)

            if server_name not in self.message_data:
                self.message_data[server_name] = {}

            self.message_data[server_name]["channel_id"] = channel.id
            self.save_json()

            await interaction.response.send_message(f"Embeds posted to {channel.mention} for {server_name}.")
        else:
            await interaction.response.send_message("Server not found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MonitorCog(bot))
