import asyncio
import json
import os
import platform
from datetime import datetime

import discord
import requests
from colorama import Fore
from discord.ext import commands, tasks

with open("config.json", "r", encoding="UTF-8") as configfile:
    config = json.load(configfile)
    token = config["Token"]
    greet = config.get("greetmembers", True)



def clear_console():
    try:
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
    except Exception as e:
        print(f"Error: {e}")



loaded = 0
allcogs = 0

class Bot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):

        super().__init__(command_prefix=commands.when_mentioned_or("$$"), intents=intents)
    

    async def setup_hook(self):
        global loaded, allcogs
        clear_console()
        for filepath in os.listdir('cogs'):
            for filename in os.listdir(f'cogs/{filepath}'):
                if filename.endswith('.py'):
                    filename = filename.replace('.py', '')
                    allcogs += 1
                    try:
                        time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                        await bot.load_extension(f'cogs.{filepath}.{filename}')
                        print(f'[{time}] [{Fore.LIGHTCYAN_EX}BOT{Fore.RESET}] [\u2705] Loaded cogs.{filepath}.{filename}')
                        loaded += 1
                    except Exception as error:
                        print(f'[{time}] [{Fore.RED}BOT{Fore.RESET}] [\u274C] Failed to load cogs.{filepath}.{filename}: {error}')

                        
        await self.tree.sync()  
        

intents = discord.Intents.all()
intents.presences = True
intents.members = True
bot = Bot(intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd)

    time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    print(f'[{time}] [{Fore.LIGHTCYAN_EX}BOT{Fore.RESET}] Loaded [{loaded}/{allcogs}] cogs')
    
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="anditv.it"),)
    print(f'\n[{time}] [{Fore.LIGHTCYAN_EX}BOT{Fore.RESET}] has connected as {bot.user} via discord.py {discord.__version__}')

    bg_task.start()

@bot.event
async def on_member_join(member):
    if greet:
        await member.create_dm()
        await member.dm_channel.send(f'Welcome **{member.name}** to **{member.guild.name}**!')
    

# loop for changing rpc
@tasks.loop(seconds=5)
async def bg_task():
    try:
        await bot.wait_until_ready()
        while not bot.is_closed():
            member_count = 0
            for guild in bot.guilds:
                member_count += guild.member_count
            status_list = [
                (discord.Status.dnd, discord.Activity(type=discord.ActivityType.watching, name="github.com/anditv21")),
                (discord.Status.dnd, discord.Activity(type=discord.ActivityType.watching, name="anditv.it")),
                (discord.Status.dnd, discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} users")),
                (discord.Status.dnd, discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"))
            ]
            for status, activity in status_list:
                await bot.change_presence(status=status, activity=activity)
                await asyncio.sleep(5)
    except Exception as e:
        print(e)



"""
@bot.event
async def on_message(message):
    print(str(message.content))
"""

bot.run(token=token, log_level=40)