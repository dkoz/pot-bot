import nextcord
from nextcord.ext import commands
import config

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=config.bot_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='ping', help='Returns the latency of the bot.')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

if __name__ == '__main__':
    bot.run(config.bot_token)