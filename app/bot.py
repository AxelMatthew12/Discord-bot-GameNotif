import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from commands.genre import genre

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot {bot.user}Siap ! ")
    
bot.tree.command(name="genre", description="Lihaat daftar genre dan pilih game.")(genre)

# Jalankan bot
bot.run(TOKEN)
