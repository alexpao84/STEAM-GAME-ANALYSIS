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

        return {
            "primary_genre": genres[0] if genres else "Unknown",
            "age_rating": age
        }
    except Exception:
        pass
    return None


def age_bucket(age):
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

for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing games"):
    game_name = row["name"]

    app_id = find_app_id(game_name)
    if not app_id:
        continue

    meta = fetch_metadata(app_id)
    if not meta:
        continue

    release_year = int(row["release_date"][:4])
    age_years = max(1, CURRENT_YEAR - release_year)

    hours_per_player = row["hours_played"] / max(row["peak_players"], 1)
    hours_per_player_per_year = hours_per_player / age_years

    rows.append({
        "game_name": game_name,
        "primary_genre": meta["primary_genre"],
        "age_group": age_bucket(meta["age_rating"]),
        "release_year": release_year,
        "age_years": age_years,
        "cur_players": row["cur_players"],
        "peak_players": row["peak_players"],
        "hours_played": row["hours_played"],
        "hours_per_player": round(hours_per_player, 1),
        "hours_per_player_per_year": round(hours_per_player_per_year, 2)
    })

    time.sleep(REQUEST_DELAY)

out = pd.DataFrame(rows)

# ==========================
# SORT & EXPORT (LIBRE SAFE)
# ==========================
out = out.sort_values(
    "hours_per_player_per_year",
    ascending=False
)

out.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8"
)

print("✔ LibreOffice-friendly analysis completed")
print(f"✔ Output written to: {OUTPUT_CSV}")
