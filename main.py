import nextcord
from nextcord.ext import commands
import config
import os

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=config.bot_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    activity = nextcord.Activity(type=nextcord.ActivityType.watching, name=config.bot_status)
    await bot.change_presence(activity=activity)

@bot.command(name='ping', help='Returns the latency of the bot.')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

if __name__ == '__main__':
    # Simplified cog loading
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
    bot.run(config.bot_token)
