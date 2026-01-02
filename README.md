# Steam Playtime Analysis

Open analysis of average playtime per game, genre, age rating and year (Steam ecosystem)

## Overview

This repository provides an open, reproducible data pipeline to analyze Steam games usage over time, focusing on:

- Yearly trends
- Single game level
- Genre-based aggregation
- Age rating buckets
- Estimated average hours played per player

Steam does not expose official per-user playtime distributions or demographic data.
This project bridges that gap by combining Steam Charts historical player counts with Steam Store metadata, producing consistent and comparable indicators.

**All playtime values are estimates, designed for comparative and trend analysis, not exact telemetry.**

## What this project answers

How many hours per year are spent on a given game?

How does player engagement evolve as games age?

Which genres retain players longer?

Are age-restricted games associated with higher/lower engagement?

How does engagement differ across game categories?

## Data sources

### 1. Steam Charts

Used for historical player data:

- Monthly average concurrent players
- Aggregated by year

Source: https://steamcharts.com
Steam Charts data is scraped or imported from public datasets (CSV).

### 2. Steam Store API

Used for metadata enrichment:

- Game name
- Genres
- Required age (PEGI/ESRB proxy)

API:
https://store.steampowered.com/api/appdetails

Repository structure

steam-playtime-analysis/
│
├── data/
│   ├── raw/
│   │   ├── .gitkeep
│   │   └── sample_steam_charts.csv
│   └── processed/
│       └── .gitkeep
│
├── scripts/
│   └── analyze_steam.py
│
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
├── .gitignore
└── LICENSE

## Input dataset format

The input CSV must contain:

app_id,game_name,year,month,avg_players


Example:

730,Counter-Strike 2,2023,1,620000
730,Counter-Strike 2,2023,2,610000

A small sample dataset (sample_steam_charts.csv) is provided for testing and demonstration purposes.

## How the analysis works
### 1. Load historical player counts

Monthly average concurrent players per game.

### 2. Fetch Steam Store metadata

For each app_id:

- genres
- required_age
- Results are cached to avoid API abuse.

### 3. Normalize age ratings

Mapped into buckets:

Age	Bucket
0	All ages
≤7	7+
≤12	12+
≤16	16+
>16	18+

## Playtime estimation model

Steam does not publish average hours per player.

This project uses a transparent proxy model:

estimated_hours = avg_players × 30 days × 2 hours/day


Then aggregated yearly and normalized as:

hours_per_player = total_estimated_hours / avg_players

## Why this works

- Consistent across all games
- Preserves relative differences
- Suitable for trend comparison and clustering

**Absolute values are not exact measurements.**

## Output dataset

data/processed/steam_analysis_by_game.csv

Columns:

Column	Description
year	Calendar year
app_id	Steam application ID
game_name	Official game name
genres	Steam genres
age_group	Normalized age bucket
avg_players	Yearly average players
total_hours	Estimated total hours
hours_per_player	Estimated avg hours/player

### Example output
Year	Game	Genre	Age	Hours / Player
2023	Dota 2	MOBA	12+	830
2023	Counter-Strike 2	FPS	18+	720
2023	Stardew Valley	Simulation	All ages	260

## How to run
## 1. Install dependencies
pip install -r requirements.txt

## 2. Run analysis
python scripts/analyze_steam.py

## 3. Load results

- Excel
- Power BI
- Pandas / Jupyter
- Tableau / Looker

## Intended use cases

- Game design & retention analysis
- Market research
- Academic research
- Educational data projects
- Portfolio / data storytelling

## Limitations & transparency

- No real user demographics
- No official per-user telemetry
- Age = content rating, not player age
- Playtime = estimated proxy

This repository does not claim precision, only consistency and analytical usefulness.

# License

MIT License
Free to use, fork, extend, and cite.

# Final note (straight talk)

This repo is valuable because:

- Steam doesn’t give this data
- Studios, analysts and researchers still need it
- Transparent assumptions beat black-box metrics

We’re building something useful, not perfect.

That’s how good open data work starts.