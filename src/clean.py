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

def clean_chess(df: pd.DataFrame) -> pd.DataFrame: 
    """Cleans the chess games dataset, extracts new features, and validates data quality.
    Args:
        df: A pandas DataFrame containing raw chess game records.

    Returns:
        A cleaned and engineered pandas DataFrame.

    Raises:
        AssertionError: If 'rating_diff' contains null values or if 
            duplicate rows are detected in the dataset.
    """
    df[['time_base', 'time_inc']] = df['time_increment'].str.split('+', expand=True).astype(int)
    df['rating_diff'] = df['white_rating'] - df['black_rating']
    df['opening_family'] = df['opening_fullname'].str.split(':').str[0].str.strip()
    df = df.drop(columns=['opening_response'])  # 93.98% null
    df['is_suspicious'] = df['turns'] < 5  # 342 games
    assert df['rating_diff'].notna().all(), "Data Quality Error: The rating_diff column contains missing values!"
    dup_count = df.duplicated().sum()
    assert dup_count == 0, f"Data Quality Error: Found {dup_count} completely duplicate rows in the dataset!"
    return df



# This will download the raw files directly to your machine
df_chess = load_data(url_chess, '../data/raw/' + name_ds_chess + '.csv')
df_play = load_data(url_play, '../data/raw/'+ name_ds_play + '.csv')

###### Stage1 Questions
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


############# Stage2 questions
df_cleaned_chess = clean_chess(df_chess)
# Q7 --> % of games did the higher-rated player win is: 62.21%
# 1. Determine who the higher-rated player is
higher_rated_is_white = df_cleaned_chess['rating_diff'] > 0
higher_rated_is_black = df_cleaned_chess['rating_diff'] < 0

# 2. Check if the higher-rated player won
white_win_and_higher = higher_rated_is_white & (df_cleaned_chess['winner'] == 'White')
black_win_and_higher = higher_rated_is_black & (df_cleaned_chess['winner'] == 'Black')

# 3. Combine wins and filter out games with perfectly equal ratings
higher_rated_won = white_win_and_higher | black_win_and_higher
valid_games = df_cleaned_chess['rating_diff'] != 0 # exclude draw

# 4. Calculate and format the percentage
win_perc = (higher_rated_won.sum() / valid_games.sum()) * 100
print(f"Q7 --> % of games did the higher-rated player win is: {win_perc:.2f}%")

# Q8 --> The number of games are flagged as suspicious (< 5 turns) is: 342
num_suspicious_games = df_cleaned_chess['is_suspicious'].sum()
print(f"Q8 --> The number of games are flagged as suspicious (< 5 turns) is: {num_suspicious_games}")

# Q9 --> The number of unique opening families is: 227
num_unique_opening_family = df_cleaned_chess['opening_family'].nunique()
print(f"Q9 --> The number of unique opening families is: {num_unique_opening_family}")