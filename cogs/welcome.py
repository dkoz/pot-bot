import json
import discord
from discord.ext import commands
import logging

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.welcome_channel_id = self.config["WELCOME_CHANNEL"]
        self.welcome_role_id = self.config["WELCOME_ROLE"]
        self.departure_channel_id = self.config["DEPARTURE_CHANNEL"]

    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = self.bot.get_channel(self.welcome_channel_id)
        if welcome_channel:
            member_count = len(welcome_channel.guild.members)
            roles_channel = f"<#{1174119680827465728}>"
            rules_channel = f"<#{1221663413952970812}>"
            link_channel = f"<#{1160404673228972195}>"
            
            embed = discord.Embed(
                title=f"Welcome {member.display_name}!",
                description=f"Welcome! **{member.name}** We are happy to see you join Jurassic Lands! You are member **{member_count}** of the community!\n\nIn order to start posting and see all of our channels you must visit: {rules_channel} and react to the post to be elevated to a hatchling. Once you have completed that you must go to: {link_channel} and follow the steps. This will link your account and allow you to use all features available, such as nesting. And you will now be a juvenile. Check out our {roles_channel} to get roles to notify you of server activities.\n\nThank you, we cant wait to see you in the game!",
                color=discord.Color.blurple()
            )
            embed.set_thumbnail(url=member.avatar.url)
            
            await welcome_channel.send(content=f"{member.mention}", embed=embed)

        role = member.guild.get_role(self.welcome_role_id)
        if role:
            try:
                await member.add_roles(role)
                logging.info(f"Assigned {role.name} to {member.display_name}.")
            except discord.errors.Forbidden:
                logging.error("I do not have permission to assign roles.")
            except Exception as e:
                logging.error(f"Failed to assign role: {e}")
                
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        departure_channel = self.bot.get_channel(self.departure_channel_id)
        if departure_channel:
            try:
                embed = discord.Embed(
                    title=f"Goodbye {member.display_name}!",
                    description=f"**{member.name}** has left the server.",
                    color=discord.Color.blurple()
                )
                embed.set_thumbnail(url=member.avatar.url)
                
                await departure_channel.send(embed=embed)
            except Exception as e:
                logging.error(f"Failed to send departure message: {e}")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
