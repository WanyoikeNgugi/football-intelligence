import soccerdata as sd
import pandas as pd
import os

STAT_TYPES = ['standard', 'keeper', 'shooting', 'playing_time', 'misc']

def flatten_columns(df):
    df.columns = [
        '_'.join(col).strip('_') if isinstance(col, tuple) else col
        for col in df.columns
    ]
    return df

def fetch_fbref_stats(fbref, stat_type):
    df = fbref.read_player_season_stats(stat_type=stat_type)
    df = flatten_columns(df)
    return df

def save_fbref_stats(output_dir):
    fbref_dir = os.path.join(output_dir, 'fbref')
    os.makedirs(fbref_dir, exist_ok=True)
    fbref = sd.FBref(leagues="ENG-Premier League", seasons=2025)
    for stat_type in STAT_TYPES:
        df = fetch_fbref_stats(fbref, stat_type)
        df.reset_index().to_csv(os.path.join(fbref_dir, f'{stat_type}.csv'), index=False)
    
def run_fbref_pipeline(output_dir):
    print("Fetching FBref stats...")
    save_fbref_stats(output_dir)
    print("FBref pipeline complete")

if __name__ == '__main__':
    output_dir = r'data\FPL\2025'
    os.makedirs(output_dir, exist_ok=True)
    run_fbref_pipeline(output_dir)
