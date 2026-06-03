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
num_spaces = len("Q00 answer -->   ")

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

###### Stage1 Questions
def stage1_questions(df: pd.DataFrame, df2: pd.DataFrame):
    # Stage1 questions from Q1 to Q6
    # Q1 --> The number of recordes in chess_games is: 20058
    #    -->  The number of recordes in play_data is: 215
    num_rec_chess =df.shape[0]
    num_rec_play= df2.shape[0]
    print(f"Q1 answer --> The number of records in {name_ds_chess} is: {num_rec_chess}")
    print(f"Q1 answer --> The number of records in {name_ds_play} is: {num_rec_play}")

    # Q2 --> The number of duplicated rows in chess_games is: 0
    #    --> The number of duplicated rows in play_data is: 0
    num_duplicate_chess = df.duplicated().sum()
    num_duplicate_play = df2.duplicated().sum()
    print(f"Q2 answer --> The number of duplicated rows in {name_ds_chess} is: {num_duplicate_chess}")
    print(f"Q2 answer --> The number of duplicated rows in {name_ds_play} is: {num_duplicate_play}")

    # Q3 answer --> The number of games that have duplicate move sequences in chess_games is: 1138
    duplicate_moves = df.duplicated(subset=['moves']).sum()
    print(f"Q3 answer --> The number of games that have duplicate move sequences in " \
        f"{name_ds_chess} is: {duplicate_moves}")

    # Q4 answer --> % of missing opening_response in chess_games is: 93.98%
    perc_mis_opening_response=df['opening_response'].isnull().mean() * 100
    print(f"Q4 answer --> % of missing opening_response in {name_ds_chess} is: {perc_mis_opening_response:.2f}%")

    # Q5 answer --> % of missing opening_variation in chess_games is: 28.22%
    perc_mis_opening_variation = df['opening_variation'].isnull().mean() * 100
    print(f"Q5 answer --> % of missing opening_variation in {name_ds_chess} is: {perc_mis_opening_variation:.2f}%")

    # Q6 answer --> The minimum number of turns in any game in chess_games is: 13
    #                And this suspicious because you cannot win with only one turn
    min_num_turns = df.groupby('game_id')['turns'].min().iloc[0]
    print(f"Q6 answer --> The minimum number of turns in any game in {name_ds_chess} is: {min_num_turns}")
    print(f"            And this suspicious because you cannot win with only one turn")

############# Stage2 questions
def stage2_questions(df: pd.DataFrame):
    # Stage2 questions from Q7 to Q9
    # Q7 --> % of games did the higher-rated player win is: 62.21%
    # 1. Determine who the higher-rated player is
    higher_rated_is_white = df['rating_diff'] > 0
    higher_rated_is_black = df['rating_diff'] < 0

    # 2. Check if the higher-rated player won
    white_win_and_higher = higher_rated_is_white & (df['winner'] == 'White')
    black_win_and_higher = higher_rated_is_black & (df['winner'] == 'Black')

    # 3. Combine wins and filter out games with perfectly equal ratings
    higher_rated_won = white_win_and_higher | black_win_and_higher
    valid_games = df['rating_diff'] != 0 # exclude draw

    # 4. Calculate and format the percentage
    win_perc = (higher_rated_won.sum() / valid_games.sum()) * 100
    print(f"Q7 --> % of games did the higher-rated player win is: {win_perc:.2f}%")

    # Q8 --> The number of games are flagged as suspicious (< 5 turns) is: 342
    num_suspicious_games = df['is_suspicious'].sum()
    print(f"Q8 --> The number of games are flagged as suspicious (< 5 turns) is: {num_suspicious_games}")

    # Q9 --> The number of unique opening families is: 227
    num_unique_opening_family = df['opening_family'].nunique()
    print(f"Q9 --> The number of unique opening families is: {num_unique_opening_family}")

############ Stage 3 
def stage3_questions(df: pd.DataFrame):
    # Stage3 questions from Q10 to Q15
    # Q10 answer--> The win rate for each winner category is: 
    #                  White is: 0.50%
    #                  Black is: 0.45%
    #                  Draw is: 0.05%
    num_winner_cat = len(df['winner'].unique())
    print("Q10 answer--> The win rate for each winner category is: ")
    for i in range(num_winner_cat):
        raw = df['winner'].value_counts(normalize=True)
        print(f"{' ' * num_spaces} {raw.index[i]} is: {raw.iloc[i]:.2f}%")

    # Q11 answer  --> The most common way games end (The victory_status) is: 
    #                 Resign is: 55.57%
    #                 Mate is: 31.53%
    #                 Out of Time is: 8.38%
    #                 Draw is: 4.52%
    num_victory_status_cat = len(df['victory_status'].unique())
    print("Q11 answer  --> The most common way games end (The victory_status) is: ")
    for i in range(num_victory_status_cat):
        raw = df['victory_status'].value_counts(normalize=True)
        print(f"{' ' * num_spaces}{raw.index[i]} is: {raw.iloc[i]*100:.2f}%")

    # vict_stat_max_avg_turn = df.groupby('victory_status')['turns'].mean().idxmax()
    vict_stat_max_avg_turn = df.groupby('victory_status')['turns'].mean().idxmax()
    print(f"Q12 answer --> The  victory_status has the highest average number of turns is: {vict_stat_max_avg_turn}")

    # Q13 answer --> The most popular opening family when:
    #                  Black wins is: Sicilian Defense with its totals is: 1273
    #                  White wins is: Sicilian Defense with its totals is: 1173
    print("Q13 answer --> The most popular opening family when:")
    for winner in ["Black", "White"]:
        pop_opening_family_winner = df[df['winner'] == winner].groupby('opening_family').size()
        print(f"{' ' * num_spaces} {winner} wins is: {pop_opening_family_winner.idxmax()} with its totals is: {pop_opening_family_winner.max()}")

    # Q14 answer --> The White win rate if the game is :
    #                  unrated, then White Win Rate: 49.94%
    #                  rated, then White Win Rate:   49.84%
    print("Q14 answer --> The White win rate if the game is :")
    win_rates = df.groupby('rated')['winner'].apply(lambda x: (x == 'White').mean()*100)
    print(f"{' '* num_spaces} unrated, then White Win Rate: {win_rates[False]:.2f}%")
    print(f"{' '* num_spaces} rated, then White Win Rate:   {win_rates[True]:.2f}%")

    # Q15 answer --> The % of each game calssifacation Short/Medium/Long is:
    #                  Medium 71.19%
    #                  Long 23.64%
    #                  Short 5.17%
    df['game_length_category'] = df['turns'].apply(categorize_length)
    percentages = df['game_length_category'].value_counts(normalize=True) * 100
    print(f"Q15 answer --> The % of each game calssifacation Short/Medium/Long is:")
    for cat, perc in percentages.items():
        print(f"{' ' * num_spaces} {cat} {perc:.2f}%")

def categorize_length(turns):
        if turns < 15:
            return 'Short'
        elif turns <= 80:
            return 'Medium'
        else:
            return 'Long'

# This will download the raw files directly to your machine
df_chess = load_data(url_chess, '../data/raw/' + name_ds_chess + '.csv')
df_play = load_data(url_play, '../data/raw/'+ name_ds_play + '.csv')

stage1_questions(df_chess,df_play )

#df = clean_chess(df_chess)
df = df_chess.pipe(clean_chess)
stage2_questions(df)

stage3_questions(df)

