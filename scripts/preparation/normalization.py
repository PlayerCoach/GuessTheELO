import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import argparse

def fit_scaler_on_train(input_filepath, chunksize=250000):
    scaler = StandardScaler()
    
    cols_to_use = ['Date', 'White_Elo', 'Black_Elo']
    chunk_iter = pd.read_csv(input_filepath, usecols=cols_to_use, chunksize=chunksize)
    
    train_games_counted = 0
    
    for i, chunk in enumerate(chunk_iter):
        chunk['Date'] = pd.to_datetime(chunk['Date'])
        train_mask = chunk['Date'].dt.year <= 2018
        train_data = chunk[train_mask]
        
        if not train_data.empty:
            combined_elos = pd.concat([train_data['White_Elo'], train_data['Black_Elo']]).values.reshape(-1, 1)
            
            scaler.partial_fit(combined_elos)
            train_games_counted += len(train_data)
            
    return scaler


def transform_and_save(input_filepath, output_filepath, scaler, chunksize=250000):
    chunk_iter = pd.read_csv(input_filepath, chunksize=chunksize)
    
    for i, chunk in enumerate(chunk_iter):
        chunk['White_Elo'] = scaler.transform(chunk[['White_Elo']].values)
        chunk['Black_Elo'] = scaler.transform(chunk[['Black_Elo']].values)
        
        chunk['Date'] = pd.to_datetime(chunk['Date'])
        
        chunk['Year'] = chunk['Date'].dt.year
        chunk['Month'] = chunk['Date'].dt.month
        chunk['DayOfWeek'] = chunk['Date'].dt.dayofweek # 0=Monday, 6=Sunday
        
        chunk['Month_Sin'] = np.sin(2 * np.pi * chunk['Month'] / 12.0)
        chunk['Month_Cos'] = np.cos(2 * np.pi * chunk['Month'] / 12.0)
        
        chunk['DayOfWeek_Sin'] = np.sin(2 * np.pi * chunk['DayOfWeek'] / 7.0)
        chunk['DayOfWeek_Cos'] = np.cos(2 * np.pi * chunk['DayOfWeek'] / 7.0)
        
        chunk = chunk.drop(columns=['Date', 'Month', 'DayOfWeek'])
        
        cols = chunk.columns.tolist()
        cols.remove('Game')
        cols.append('Game')
        chunk = chunk[cols]
        
        write_header = (i == 0)
        write_mode = 'w' if i == 0 else 'a'
        
        chunk.to_csv(output_filepath, mode=write_mode, index=False, header=write_header)
        

def main():
    parser = argparse.ArgumentParser(description="Standardize Elo and encode dates.")
    parser.add_argument("--input", default="final_chess_dataset_max100.csv", help="Input dataset")
    parser.add_argument("--output", default="ml_ready_chess_dataset.csv", help="Output ML-ready dataset")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found.")
        return

    fitted_scaler = fit_scaler_on_train(args.input)
    
    transform_and_save(args.input, args.output, fitted_scaler)

if __name__ == "__main__":
    main()
