import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
from dotenv import load_dotenv
from discord.ui import Select, View

# Muat token dari .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Token tidak ditemukan. Pastikan file .env sudah diatur dengan benar.")

API_URL = "https://steamspy.com/api.php"

# Inisialisasi bot dengan intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Fungsi untuk mendapatkan daftar genre
def get_available_genres():
    return [
        "Action", "Adventure", "Casual", "Indie",
        "Massively Multiplayer", "Racing", "RPG",
        "Simulation", "Sports", "Strategy"
    ]

# Fungsi untuk mendapatkan game berdasarkan genre
def get_games_by_genre(genre):
    params = {"request": "genre", "genre": genre}
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                sorted_games = sorted(
                    data.items(), key=lambda x: x[1].get("price", float("inf"))
                )
                games = []
                for _, game in sorted_games[:10]:
                    name = game.get("name", "Tidak Tersedia")
                    price = game.get("price", "Tidak Tersedia")
                    developer = game.get("developer", "Tidak Tersedia")
                    games.append(f"| {name:<30} | {price:<10} | {developer:<20} |")
                return games
            else:
                return ["Tidak ada game yang ditemukan untuk genre ini."]
        else:
            return [f"Kesalahan saat menghubungi API: {response.status_code}"]
    except requests.exceptions.Timeout:
        return ["Permintaan API melebihi batas waktu."]
    except Exception as e:
        return [f"Terjadi kesalahan: {e}"]

# Event ketika bot siap
@bot.event
async def on_ready():
    try:
        # Sinkronisasi global
        await bot.tree.sync()
        print("Perintah global telah disinkronkan.")

        # Sinkronisasi spesifik untuk server tempat pengujian
        for guild in bot.guilds:
            await bot.tree.sync(guild=discord.Object(id=guild.id))
            print(f"Perintah disinkronkan untuk server: {guild.name} (ID: {guild.id})")

        print(f"Bot telah login sebagai {bot.user}")
    except Exception as e:
        print(f"Kesalahan saat sinkronisasi commands: {e}")

# Slash command untuk daftar genre
@bot.tree.command(name="genre", description="Lihat daftar genre dan pilih game.")
async def genre(interaction: discord.Interaction):
    print("Perintah genre diterima.")
    genres = get_available_genres()
    print(f"Daftar genre: {genres}")

    class GenreSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label=genre, value=genre)
                for genre in genres
            ]
            super().__init__(
                placeholder="Pilih genre...",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, select_interaction: discord.Interaction):
            selected_genre = self.values[0]
            print(f"Genre terpilih: {selected_genre}")
            await select_interaction.response.defer()
            games = get_games_by_genre(selected_genre)
            print(f"Daftar game: {games}")
            if games:
                header = f"| {'Nama Game':<30} | {'Harga':<10} | {'Developer':<20} |"
                separator = f"+{'-'*32}+{'-'*12}+{'-'*22}+" 
                table = "\n".join([separator, header, separator] + games + [separator])
                await select_interaction.followup.send(f"```\n{table}\n```")
            else:
                await select_interaction.followup.send(
                    f"Tidak ada game yang ditemukan untuk genre: {selected_genre}"
                )

    view = View()
    view.add_item(GenreSelect())  # Lengkapi penambahan item select ke dalam view
    await interaction.response.send_message("Pilih genre game:", view=view)

# Jalankan bot
bot.run(TOKEN)
