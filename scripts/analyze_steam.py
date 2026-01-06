import pandas as pd
import requests
import time
from tqdm import tqdm
from datetime import datetime

STEAM_SEARCH_API = "https://store.steampowered.com/api/storesearch"
STEAM_APP_API = "https://store.steampowered.com/api/appdetails"

INPUT_CSV = "data/raw/steam_charts.csv"
OUTPUT_CSV = "data/processed/steam_snapshot_analysis.csv"

REQUEST_DELAY = 0.8
HEADERS = {"User-Agent": "steam-playtime-analysis/1.0"}

CURRENT_YEAR = datetime.now().year

# ==========================
# LOAD DATA
# ==========================
df = pd.read_csv(INPUT_CSV)

required = {"name", "cur_players", "peak_players", "hours_played", "release_date"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

# ==========================
# HELPERS
# ==========================
def find_app_id(game_name):
    """
    Finds the Steam app ID for a given game name using the Steam Store search API.

    :param game_name: The name of the game to search for
    :return: The Steam app ID of the game, or None if not found
    """
    try:
        r = requests.get(
            STEAM_SEARCH_API,
            params={"term": game_name, "l": "english", "cc": "US"},
            headers=HEADERS,
            timeout=10
        )
        items = r.json().get("items", [])
        if items:
            return items[0]["id"]
    except Exception:
        pass
    return None

def fetch_metadata(app_id):
    """
    Fetches metadata for a Steam app given its ID.

    The metadata includes the primary genre, age rating, whether the game is free-to-play and its price in EUR.

    :param app_id: The Steam app ID to fetch metadata for
    :return: A dictionary containing the metadata
    """
    try:
        r = requests.get(
            STEAM_APP_API,
            params={"appids": app_id},
            headers=HEADERS,
            timeout=10
        )
        payload = r.json().get(str(app_id))
        if not payload or not payload.get("success"):
            return None

        data = payload["data"]

        genres = [g["description"] for g in data.get("genres", [])]
        age = int(data.get("required_age", 0))

        is_free = data.get("is_free", False)

        price_eur = 0.0
        if not is_free:
            price_info = data.get("price_overview")
            if price_info:
                price_eur = price_info.get("final", 0) / 100.0

        return {
            "primary_genre": genres[0] if genres else "Unknown",
            "age_rating": age,
            "is_free": is_free,
            "price_eur": price_eur
        }
    except Exception:
        pass
    return None

def age_bucket(age):
    """
    Maps an age rating into a standardized bucket.

    Agebuckets are: "All ages", "7+", "12+", "16+", and "18+".

    :param age: The age rating to map
    :return: A standardized age bucket
    """
    if age == 0:
        return "All ages"
    if age <= 7:
        return "7+"
    if age <= 12:
        return "12+"
    if age <= 16:
        return "16+"
    return "18+"

# ==========================
# PROCESS
# ==========================
rows = []
# Process the games and fetch metadata
for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing games"):
    game_name = row["name"]

    # Find the Steam app ID for the game
    app_id = find_app_id(game_name)
    if not app_id:
        continue

    # Fetch metadata for the app
    meta = fetch_metadata(app_id)
    if not meta:
        continue

    # Calculate time since release
    release_year = int(row["release_date"][:4])
    age_years = max(1, CURRENT_YEAR - release_year)

    # Calculate playtime per player
    hours_per_player = row["hours_played"] / max(row["peak_players"], 1)
    # Calculate playtime per player per year
    hours_per_player_per_year = hours_per_player / age_years

    # Store the results
    rows.append({
        "game_name": game_name,
        "primary_genre": meta["primary_genre"],  # Primary genre of the game
        "age_group": age_bucket(meta["age_rating"]),  # Age rating bucket
        "release_year": release_year,  # Year of release
        "age_years": age_years,  # Time since release
        "cur_players": row["cur_players"],  # Current player count
        "peak_players": row["peak_players"],  # Peak player count
        "hours_played": row["hours_played"],  # Total playtime
        "hours_per_player": round(hours_per_player, 1),  # Playtime per player
        "hours_per_player_per_year": round(hours_per_player_per_year, 2),  # Playtime per player per year
        "monetization": "Free-to-play" if meta["is_free"] else "Paid",  # Monetization model
        "price_eur": meta["price_eur"]  # Price in EUR
    })

    # Delay to avoid overloading the Steam API
    time.sleep(REQUEST_DELAY)

# Create the output DataFrame
out = pd.DataFrame(rows)

# Sort the DataFrame by playtime per player per year
out = out.sort_values(
    "hours_per_player_per_year",
    ascending=False
)

# Export the DataFrame to a CSV file (LibreOffice-friendly)
out.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8"
)

print("✔ LibreOffice-friendly analysis completed")
print(f"✔ Output written to: {OUTPUT_CSV}")
