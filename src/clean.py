import pandas as pd
import os
import re
import gdown

# The datasets url Google Drive links
url_chess = 'https://drive.google.com/file/d/1eR3NZtwIC6ECN3vhtrynqmx8okG0twA7/view'
url_play = 'https://drive.google.com/file/d/1wCSAkGagMzWiToedLC3ZGo_lGf_laF-k/view'

# declare a variable for each dataset name
name_ds_chess="chess_games"
name_ds_play="play_data"

def load_data(url: str, local_path: str) -> pd.DataFrame:
    """Load from Google Drive URL using gdown to bypass warning screens, 
    save locally, and return as a DataFrame."""
    
    # If already downloaded, load from cache instantly
    if os.path.exists(local_path):
        print(f'Loading from cache: {local_path}')
        return pd.read_csv(local_path)
    
    print(f'Downloading from Google Drive to {local_path}...')
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # Removed the 'fuzzy' argument to fix the TypeError
    gdown.download(url, local_path, quiet=False)
    
    # Read the successfully downloaded local CSV file
    print('Download complete. Reading into DataFrame...')
    return pd.read_csv(local_path)


# This will download the raw files directly to your machine
df_chess = load_data(url_chess, '../data/raw/' + name_ds_chess + '.csv')
df_play = load_data(url_play, '../data/raw/'+ name_ds_play + '.csv')

# Q1 --> The number of recordes in chess_games is: 20058
#    -->  The number of recordes in play_data is: 215
num_rec_chess =df_chess.shape[0]
num_rec_play= df_play.shape[0]
print(f"Q1 answer --> The number of records in {name_ds_chess} is: {num_rec_chess}")
print(f"Q1 answer --> The number of records in {name_ds_play} is: {num_rec_play}")

# Q2 --> The number of duplicated rows in chess_games is: 0
#    --> The number of duplicated rows in play_data is: 0
num_duplicate_chess = df_chess.duplicated().sum()
num_duplicate_play = df_play.duplicated().sum()
print(f"Q2 answer --> The number of duplicated rows in {name_ds_chess} is: {num_duplicate_chess}")
print(f"Q2 answer --> The number of duplicated rows in {name_ds_play} is: {num_duplicate_play}")

# Q3 answer --> The number of games that have duplicate move sequences in chess_games is: 1138
duplicate_moves = df_chess.duplicated(subset=['moves']).sum()
print(f"Q3 answer --> The number of games that have duplicate move sequences in " \
      f"{name_ds_chess} is: {duplicate_moves}")

# Q4 answer --> % of missing opening_response in chess_games is: 93.98%
perc_mis_opening_response=df_chess['opening_response'].isnull().mean() * 100
print(f"Q4 answer --> % of missing opening_response in {name_ds_chess} is: {perc_mis_opening_response:.2f}%")

# Q5 answer --> % of missing opening_variation in chess_games is: 28.22%
perc_mis_opening_variation = df_chess['opening_variation'].isnull().mean() * 100
print(f"Q5 answer --> % of missing opening_variation in {name_ds_chess} is: {perc_mis_opening_variation:.2f}%")

# Q6 answer --> The minimum number of turns in any game in chess_games is: 13
#                And this suspicious because you cannot win with only one turn
min_num_turns = df_chess.groupby('game_id')['turns'].min().iloc[0]
print(f"Q6 answer --> The minimum number of turns in any game in {name_ds_chess} is: {min_num_turns}")
print(f"            And this suspicious because you cannot win with only one turn")

