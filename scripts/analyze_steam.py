import pandas as pd
import requests
import time
from tqdm import tqdm

# ======================================================
# CONFIG
# ======================================================
STEAM_STORE_API = "https://store.steampowered.com/api/appdetails"

INPUT_CSV = "data/raw/steam_charts.csv"
OUTPUT_CSV = "data/processed/steam_analysis_by_game.csv"

HOURS_PER_DAY = 2          # explicit assumption
DAYS_PER_MONTH = 30        # explicit assumption
REQUEST_DELAY = 0.8        # seconds (API friendly)

HEADERS = {
    "User-Agent": "steam-playtime-analysis/1.0"
}

# ======================================================
# LOAD INPUT DATA
# ======================================================
df = pd.read_csv(INPUT_CSV)

required_cols = {"app_id", "game_name", "year", "month", "avg_players"}
missing = required_cols - set(df.columns)

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["year"] = df["year"].astype(int)
df["avg_players"] = df["avg_players"].fillna(0)

# ======================================================
# STEAM METADATA
# ======================================================
def fetch_steam_metadata(app_id):
    """
    Fetch genre and age rating from Steam Store API.
    Returns dict or None if unavailable.
    """
    try:
        r = requests.get(
            STEAM_STORE_API,
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
            "genres": ", ".join(genres) if genres else "Unknown",
            "age_rating": age
        }
    except Exception:
        return None

# ======================================================
# FETCH METADATA (CACHED IN-MEMORY)
# ======================================================
metadata = {}

unique_apps = df["app_id"].unique()

for app_id in tqdm(unique_apps, desc="Fetching Steam metadata"):
    meta = fetch_steam_metadata(app_id)
    if meta:
        metadata[app_id] = meta
    time.sleep(REQUEST_DELAY)

meta_df = (
    pd.DataFrame.from_dict(metadata, orient="index")
    .reset_index()
    .rename(columns={"index": "app_id"})
)

# ======================================================
# MERGE DATA
# ======================================================
df = df.merge(meta_df, on="app_id", how="left")

df["genres"].fillna("Unknown", inplace=True)
df["age_rating"].fillna(0, inplace=True)

# ======================================================
# AGE BUCKETS
# ======================================================
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

df["age_group"] = df["age_rating"].apply(age_bucket)

# ======================================================
# PLAYTIME ESTIMATION (PROXY MODEL)
# ======================================================
df["estimated_hours"] = (
    df["avg_players"]
    * DAYS_PER_MONTH
    * HOURS_PER_DAY
)

# ======================================================
# ANNUAL AGGREGATION (PER GAME)
# ======================================================
annual = (
    df.groupby(
        ["year", "app_id", "game_name", "genres", "age_group"],
        as_index=False
    )
    .agg(
        avg_players=("avg_players", "mean"),
        total_hours=("estimated_hours", "sum")
    )
)

annual["hours_per_player"] = (
    annual["total_hours"] / annual["avg_players"]
).round(1)

# ======================================================
# EXPORT
# ======================================================
annual.to_csv(OUTPUT_CSV, index=False)

print("✔ Analysis completed")
print(f"✔ Output written to: {OUTPUT_CSV}")
