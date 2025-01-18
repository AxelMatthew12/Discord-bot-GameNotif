import requests
import logging

API_URL = "https://steamspy.com/api.php"

def fetch_genres_from_api():
    fallback_genres = [
        "Action", "Strategy", "RPG", "Indie", "Adventure",
        "Sports", "Simulation", "Early Access", "Ex Early Access",
        "MMO", "Free"
    ]
    try:
        params = {"request": "genres"}
        response = requests.get(API_URL, params=params, timeout=10)
        logging.info(f"API Status Code: {response.status_code}")  # Log status code
        response.raise_for_status()  # This will raise an error for 4xx/5xx responses
        data = response.json()
        
        if isinstance(data, dict):
            logging.info(f"Daftar genre berhasil diambil dari API: {list(data.keys())}")
            return list(data.keys())
        else:
            logging.warning("API tidak mengembalikan format genre yang valid. Menggunakan fallback.")
            return fallback_genres
    except Exception as e:
        logging.error(f"Kesalahan saat mengambil genre dari API: {e}. Menggunakan fallback.")
        return fallback_genres


def get_games_by_genre(genre, year_threshold=2019):
    params = {"request": "genre", "genre": genre}
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            logging.warning(f"Tidak ada game ditemukan untuk genre '{genre}'.")
            return ["Tidak ada game yang ditemukan untuk genre ini."]
        
        filtered_games = []
        for app_id, game in data.items():
            name = game.get("name", "Tidak Tersedia")
            price = game.get("price", "Tidak Tersedia")
            developer = game.get("developer", "Tidak Tersedia")
            release_year = game.get("release_year")

            if release_year is not None and release_year >= year_threshold:
                filtered_games.append({
                    "name": name,
                    "price": price,
                    "developer": developer,
                    "release_year": release_year,
                })

        sorted_games = sorted(filtered_games, key=lambda g: g.get("price", float("inf")))
        return [
            f"| {game['name']:<30} | {game['price']:<10} | {game['developer']:<20} | {game['release_year']:<10} |"
            for game in sorted_games[:10]
        ] or ["Tidak ada game yang sesuai dengan kriteria."]
    except requests.exceptions.RequestException as e:
        logging.error(f"Kesalahan koneksi ke API: {e}")
        return [f"Kesalahan saat menghubungi API: {e}"]
    except Exception as e:
        logging.error(f"Kesalahan tak terduga: {e}")
        return [f"Terjadi kesalahan: {e}"]

# Fungsi untuk menangani interaksi Discord, dengan penambahan `defer` untuk menghindari error 404
async def genre(interaction):
    await interaction.response.defer()  # Mengakui interaksi segera

    try:
        genres = fetch_genres_from_api()
        if isinstance(genres, list) and genres:
            await interaction.followup.send(f"Daftar genre: {', '.join(genres)}")
        else:
            await interaction.followup.send("Gagal mengambil daftar genre.")
    except Exception as e:
        await interaction.followup.send(f"Gagal mengambil daftar genre: {e}")
