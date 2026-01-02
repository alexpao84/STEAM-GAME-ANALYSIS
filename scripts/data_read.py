import pandas as pd

df = pd.read_csv("data/processed/steam_snapshot_analysis.csv")

df.sort_values("hours_per_player", ascending=False).head(200)
