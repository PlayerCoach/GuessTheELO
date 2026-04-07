import os
import pandas as pd
import numpy as np
from tqdm import tqdm

def load_df(filepath):
    dtype_mapping = {
        'White_Elo': 'int16', 
        'Black_Elo': 'int16',
        'Site_FICS': 'int8', 
        'Site_Lichess': 'int8',
        'Game_Type_Bullet': 'int8', 
        'Game_Type_Blitz': 'int8', 
        'Game_Type_Rapid': 'int8',
        'Result_White_Checkmate': 'int8', 'Result_Black_Checkmate': 'int8', 
        'Result_White_Resign': 'int8', 'Result_Black_Resign': 'int8', 
        'Result_White_Time': 'int8', 'Result_Black_Time': 'int8', 
        'Result_Draw': 'int8'
    }
    
    cols_to_use = list(dtype_mapping.keys()) + ['Date', 'Game']
    
    df_list = []

    # 250k rows at a time
    chunk_iter = pd.read_csv(filepath, usecols=cols_to_use, dtype=dtype_mapping, chunksize=250000)
    for i, chunk in tqdm(enumerate(chunk_iter)):
        chunk['Date'] = pd.to_datetime(chunk['Date'])
        
        # Get moves like: "1. ", "22. "
        chunk['Game_Length'] = chunk['Game'].str.count(r'\b\d+\.\s').fillna(0).astype('int16')
        chunk = chunk.drop(columns=['Game'])
        
        df_list.append(chunk)
        
    df = pd.concat(df_list, ignore_index=True)
    return df

def get_features(df):
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Avg_Elo'] = (df['White_Elo'] + df['Black_Elo']) / 2
    df['Elo_Diff'] = df['White_Elo'] - df['Black_Elo'] 
    
    df['Site'] = np.where(df['Site_FICS'] == 1, 'FICS', 'Lichess')
    
    conditions_type = [
        df['Game_Type_Bullet'] == 1,
        df['Game_Type_Blitz'] == 1,
        df['Game_Type_Rapid'] == 1
    ]
    df['Game_Type'] = np.select(conditions_type, ['Bullet', 'Blitz', 'Rapid'], default='Unknown')
    
    white_wins = df['Result_White_Checkmate'] | df['Result_White_Resign'] | df['Result_White_Time']
    black_wins = df['Result_Black_Checkmate'] | df['Result_Black_Resign'] | df['Result_Black_Time']
    
    df['Winner'] = np.select([white_wins == 1, black_wins == 1, df['Result_Draw'] == 1], 
                             ['White', 'Black', 'Draw'], default='Unknown')

    df['Winner_Elo'] = np.where(df['Winner'] == 'White', df['White_Elo'], 
                       np.where(df['Winner'] == 'Black', df['Black_Elo'], np.nan))
    
    df['Loser_Elo'] = np.where(df['Winner'] == 'White', df['Black_Elo'], 
                      np.where(df['Winner'] == 'Black', df['White_Elo'], np.nan))
                      
    return df

def generate_splits(df):
    conditions = [
        df['Year'] <= 2018,
        (df['Year'] == 2019) & (df['Month'] <= 6),
        (df['Year'] == 2019) & (df['Month'] >= 7)
    ]
    choices = ['Train', 'Val', 'Test']
    df['Split'] = np.select(conditions, choices, default='Unknown')
    
    return df

def export_statistics_to_csv(df, output_dir):
    # 1. Avg ranking through the years 
    df_yearly_site = df.groupby(['Year', 'Split', 'Site'])['Avg_Elo'].mean().round(2).reset_index()
    df_yearly_site.to_csv(os.path.join(output_dir, '1_avg_elo_by_year_site_split.csv'), index=False)

    # 2. Avg ranking for each site for each game type
    df_site_gametype = df.groupby(['Site', 'Game_Type'])['Avg_Elo'].mean().round(2).reset_index()
    df_site_gametype.to_csv(os.path.join(output_dir, '2_avg_elo_by_site_gametype.csv'), index=False)

    # 3. Number of games in each game type
    df_gametype_counts = df['Game_Type'].value_counts().reset_index()
    df_gametype_counts.columns = ['Game_Type', 'Game_Count']
    df_gametype_counts.to_csv(os.path.join(output_dir, '3_games_by_gametype.csv'), index=False)

    # 4. Number of games in each year
    df_year_counts = df['Year'].value_counts().sort_index().reset_index()
    df_year_counts.columns = ['Year', 'Game_Count']
    df_year_counts.to_csv(os.path.join(output_dir, '4_games_by_year.csv'), index=False)

    # 5. Number of games with each result
    df_result_counts = df['Winner'].value_counts().reset_index()
    df_result_counts.columns = ['Result', 'Game_Count']
    df_result_counts.to_csv(os.path.join(output_dir, '5_games_by_result.csv'), index=False)

    # 6. Avg ranking of winner, loser and draw
    avg_outcomes = {
        'Outcome': ['Winner', 'Loser', 'Draw'],
        'Avg_Elo': [
            df['Winner_Elo'].mean(),
            df['Loser_Elo'].mean(),
            df[df['Winner'] == 'Draw']['Avg_Elo'].mean()
        ]
    }
    df_avg_outcomes = pd.DataFrame(avg_outcomes).round(2)
    df_avg_outcomes.to_csv(os.path.join(output_dir, '6_avg_elo_by_outcome.csv'), index=False)

    # 7. Distribution of ranking difference 
    bins_diff = range(-1000, 1050, 50)
    df['Elo_Diff_Bin'] = pd.cut(df['Elo_Diff'], bins=bins_diff)
    df_diff_dist = df['Elo_Diff_Bin'].value_counts().sort_index().reset_index()
    df_diff_dist.columns = ['Elo_Difference_Bracket', 'Game_Count']
    df_diff_dist.to_csv(os.path.join(output_dir, '7_elo_diff_distribution.csv'), index=False)

    
    # 8, 9, 10. Rating disributions per split
    elo_bins = range(500, 3550, 50)
    df['Avg_Elo_Bin'] = pd.cut(df['Avg_Elo'], bins=elo_bins)

    df_train = df[df['Split'] == 'Train']
    train_dist = df_train.groupby(['Year', 'Site', 'Avg_Elo_Bin'], observed=True).size().reset_index(name='Game_Count')
    train_dist.to_csv(os.path.join(output_dir, '10_train_rating_dist_by_year.csv'), index=False)

    df_val = df[df['Split'] == 'Val']
    val_dist = df_val.groupby(['Site', 'Avg_Elo_Bin'], observed=True).size().reset_index(name='Game_Count')
    val_dist.to_csv(os.path.join(output_dir, '11_val_rating_dist.csv'), index=False)

    df_test = df[df['Split'] == 'Test']
    test_dist = df_test.groupby(['Site', 'Avg_Elo_Bin'], observed=True).size().reset_index(name='Game_Count')
    test_dist.to_csv(os.path.join(output_dir, '12_test_rating_dist.csv'), index=False)

    # 11. Game length distiburion
    length_bins = range(0, 310, 10)
    df['Game_Length_Bin'] = pd.cut(df['Game_Length'], bins=length_bins)
    
    df_length_dist = df.groupby(['Split', 'Game_Type', 'Game_Length_Bin'], observed=True).size().reset_index(name='Game_Count')
    df_length_dist.to_csv(os.path.join(output_dir, '13_game_length_distribution.csv'), index=False)

    # 12. Game length vs ranking vs game type
    df_len_vs_elo = df.groupby(['Site', 'Game_Type', 'Avg_Elo_Bin'], observed=True)['Game_Length'].mean().round(2).reset_index()
    df_len_vs_elo.columns = ['Site', 'Game_Type', 'Avg_Elo_Bracket', 'Average_Number_of_Moves']
    df_len_vs_elo.to_csv(os.path.join(output_dir, '14_game_length_vs_ranking.csv'), index=False)


def main():
    input_file = "../dataset3.csv" 
    output_directory = "../csv_analysis3"
    
    os.makedirs(output_directory, exist_ok=True)
    
    df = load_df(input_file)
    df = get_features(df)
    df_combined = generate_splits(df)
    
    export_statistics_to_csv(df_combined, output_directory)
    
if __name__ == "__main__":
    main()
