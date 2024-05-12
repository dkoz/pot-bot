import discord
from discord.ext import commands
import settings
import os
import logging

logging.basicConfig(level=logging.INFO, filename='bot.log', format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=settings.bot_prefix, intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.group()
async def app(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid app command passed...')

async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            extension = f"cogs.{filename[:-3]}"
            await bot.load_extension(extension)
    await bot.tree.sync()

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    ascii_art = r"""
█ ▄▄  ██     ▄▄▄▄▀ ▄  █     ████▄ ▄████    
█   █ █ █ ▀▀▀ █   █   █     █   █ █▀   ▀   
█▀▀▀  █▄▄█    █   ██▀▀█     █   █ █▀▀      
█     █  █   █    █   █     ▀████ █        
 █       █  ▀        █             █       
  ▀     █           ▀               ▀      
       ▀                                   
   ▄▄▄▄▀ ▄█    ▄▄▄▄▀ ██      ▄      ▄▄▄▄▄  
▀▀▀ █    ██ ▀▀▀ █    █ █      █    █     ▀▄
    █    ██     █    █▄▄█ ██   █ ▄  ▀▀▀▀▄  
   █     ▐█    █     █  █ █ █  █  ▀▄▄▄▄▀   
  ▀       ▐   ▀         █ █  █ █           
                       █  █   ██           
                      ▀                    
    """
    print(ascii_art)
    print(f'Bot is ready! Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Path of Titans"))


if __name__ == '__main__':
    bot.run(settings.bot_token)
