import os
import pandas as pd
import numpy as np
import argparse

def split_dataset(input_filepath, output_dir, chunksize=250000):
    os.makedirs(output_dir, exist_ok=True)

    train_path = os.path.join(output_dir, "train.csv")
    test_path = os.path.join(output_dir, "test.csv")
    val1_path = os.path.join(output_dir, "val_split1.csv")
    val2_path = os.path.join(output_dir, "val_split2.csv")

    chunk_iter = pd.read_csv(input_filepath, chunksize=chunksize)

    counts = {'train': 0, 'test': 0, 'val1': 0, 'val2': 0}

    for i, chunk in enumerate(chunk_iter):
        angle = np.arctan2(chunk['Month_Sin'], chunk['Month_Cos'])
        month_raw = (angle * 12 / (2 * np.pi))
        
        chunk['Month_Reconstructed'] = np.round(
            np.where(month_raw <= 0.5, month_raw + 12, month_raw)
        ).astype(int)

        year = chunk['Year']
        month = chunk['Month_Reconstructed']

        train_mask = year <= 2018
        
        test_mask = (year == 2019) & (month >= 7)
        
        val1_mask = (year == 2019) & (month <= 6)
        
        val2_mask = (year == 2018) & (month >= 7)

        df_train = chunk[train_mask].drop(columns=['Month_Reconstructed'])
        df_test = chunk[test_mask].drop(columns=['Month_Reconstructed'])
        df_val1 = chunk[val1_mask].drop(columns=['Month_Reconstructed'])
        df_val2 = chunk[val2_mask].drop(columns=['Month_Reconstructed'])

        counts['train'] += len(df_train)
        counts['test'] += len(df_test)
        counts['val1'] += len(df_val1)
        counts['val2'] += len(df_val2)

        write_header = (i == 0)
        write_mode = 'w' if i == 0 else 'a'

        if not df_train.empty: df_train.to_csv(train_path, mode=write_mode, index=False, header=write_header)
        if not df_test.empty: df_test.to_csv(test_path, mode=write_mode, index=False, header=write_header)
        if not df_val1.empty: df_val1.to_csv(val1_path, mode=write_mode, index=False, header=write_header)
        if not df_val2.empty: df_val2.to_csv(val2_path, mode=write_mode, index=False, header=write_header)


def main():
    parser = argparse.ArgumentParser(description="Split the dataset into Train, Val1, Val2(subset of train), and Test.")
    parser.add_argument("--input", default="ml_ready_chess_dataset.csv", help="Preprocessed CSV")
    parser.add_argument("--output_dir", default="model_splits", help="Folder to save the splits")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: '{args.input}' not found. Check your file path.")
        return

    split_dataset(args.input, args.output_dir)

if __name__ == "__main__":
    main()
