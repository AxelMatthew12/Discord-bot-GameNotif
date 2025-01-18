import discord
from discord import app_commands
from discord.ui import Select, View
import logging
from utils.steamspy import fetch_genres_from_api, get_games_by_genre

async def genre(interaction: discord.Interaction):
    logging.info("Perintah genre diterima.")
    try:
        genres = fetch_genres_from_api()

        # Pastikan genre tidak kosong
        if not genres:
            logging.error("Daftar genre kosong.")
            await interaction.response.send_message("Gagal mengambil daftar genre.")
            return

        class GenreSelect(Select):
            def __init__(self):
                # Jika genre kosong, beri pesan fallback
                options = [discord.SelectOption(label=genre, value=genre) for genre in genres]
                super().__init__(placeholder="Pilih genre...", min_values=1, max_values=1, options=options)

            async def callback(self, select_interaction: discord.Interaction):
                selected_genre = self.values[0]
                await select_interaction.response.defer()
                try:
                    logging.info(f"Mengambil game untuk genre: {selected_genre}")
                    games = get_games_by_genre(selected_genre)
                    if games:
                        header = f"| {'Nama Game':<30} | {'Harga':<10} | {'Developer':<20} | {'Tahun Rilis':<10} |"
                        separator = f"+{'-'*32}+{'-'*12}+{'-'*22}+{'-'*12}+" 
                        table = "\n".join([separator, header, separator] + games + [separator])
                        await select_interaction.followup.send(f"```\n{table}\n```")
                    else:
                        await select_interaction.followup.send(f"Tidak ada game ditemukan untuk genre: {selected_genre}")
                except Exception as e:
                    logging.error(f"Kesalahan saat mengambil game untuk genre {selected_genre}: {e}")
                    await select_interaction.followup.send(f"Kesalahan saat mengambil data game: {e}")

        view = View()
        view.add_item(GenreSelect())
        await interaction.response.send_message("Pilih genre game:", view=view)
    except Exception as e:
        logging.error(f"Kesalahan saat mengambil daftar genre: {e}")
        await interaction.response.send_message(f"Gagal mengambil daftar genre: {e}")
