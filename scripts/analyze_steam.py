import pandas as pd
import requests
import time
from tqdm import tqdm

STEAM_SEARCH_API = "https://store.steampowered.com/api/storesearch"
STEAM_APP_API = "https://store.steampowered.com/api/appdetails"

INPUT_CSV = "data/raw/steam_charts.csv"
OUTPUT_CSV = "data/processed/steam_snapshot_analysis.csv"

REQUEST_DELAY = 0.8
HEADERS = {"User-Agent": "steam-playtime-analysis/1.0"}

# ==========================
# LOAD DATA
# ==========================
df = pd.read_csv(INPUT_CSV)

required = {"name", "cur_players", "peak_players", "hours_played", "release_date"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

# ==========================
# FETCH APP ID FROM NAME
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
        return None

# ==========================
# FETCH METADATA
# ==========================
def fetch_metadata(app_id):
    try:
        r = requests.get(
            STEAM_APP_API,
            params={"appids": app_id},
            headers=HEADERS,
            timeout=10
        )
        data = r.json().get(str(app_id))
        if not data or not data["success"]:
            return None

        d = data["data"]
        genres = [g["description"] for g in d.get("genres", [])]
        age = int(d.get("required_age", 0))

        return {
            "app_id": app_id,
            "genres": ", ".join(genres) if genres else "Unknown",
            "age_rating": age
        }
    except Exception:
        return None

# ==========================
# PROCESS GAMES
# ==========================
rows = []

for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing games"):
    name = row["name"]

    app_id = find_app_id(name)
    if not app_id:
        continue

    meta = fetch_metadata(app_id)
    if not meta:
        continue

    avg_hours_per_player = row["hours_played"] / max(row["peak_players"], 1)

    rows.append({
        "game_name": name,
        "app_id": app_id,
        "release_year": row["release_date"][:4],
        "genres": meta["genres"],
        "age_rating": meta["age_rating"],
        "cur_players": row["cur_players"],
        "peak_players": row["peak_players"],
        "hours_played": row["hours_played"],
        "hours_per_player": round(avg_hours_per_player, 1)
    })

    time.sleep(REQUEST_DELAY)

out = pd.DataFrame(rows)

# ==========================
# AGE BUCKET
# ==========================
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

out["age_group"] = out["age_rating"].apply(age_bucket)

out.to_csv(OUTPUT_CSV, index=False)

print("✔ Snapshot analysis completed")
print(f"✔ Output: {OUTPUT_CSV}")
