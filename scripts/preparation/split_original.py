import os
import pandas as pd
import argparse

def split_original_dataset(input_filepath, output_dir, chunksize=250000):
    os.makedirs(output_dir, exist_ok=True)

    train_path = os.path.join(output_dir, "original_train.csv")
    test_path = os.path.join(output_dir, "original_test.csv")
    val1_path = os.path.join(output_dir, "original_val_split1.csv")
    val2_path = os.path.join(output_dir, "original_val_split2.csv")

    chunk_iter = pd.read_csv(input_filepath, chunksize=chunksize)

    counts = {'train': 0, 'test': 0, 'val1': 0, 'val2': 0}
    
    first_write = {'train': True, 'test': True, 'val1': True, 'val2': True}

    for i, chunk in enumerate(chunk_iter):
        datetime_col = pd.to_datetime(chunk['Date'])
        
        year = datetime_col.dt.year
        month = datetime_col.dt.month

        train_mask = year <= 2018
        test_mask = (year == 2019) & (month >= 7)
        val1_mask = (year == 2019) & (month <= 6)
        val2_mask = (year == 2018) & (month >= 7)

        df_train = chunk[train_mask]
        df_test = chunk[test_mask]
        df_val1 = chunk[val1_mask]
        df_val2 = chunk[val2_mask]

        counts['train'] += len(df_train)
        counts['test'] += len(df_test)
        counts['val1'] += len(df_val1)
        counts['val2'] += len(df_val2)

        if not df_train.empty: 
            df_train.to_csv(train_path, mode='w' if first_write['train'] else 'a', index=False, header=first_write['train'])
            first_write['train'] = False
            
        if not df_test.empty: 
            df_test.to_csv(test_path, mode='w' if first_write['test'] else 'a', index=False, header=first_write['test'])
            first_write['test'] = False
            
        if not df_val1.empty: 
            df_val1.to_csv(val1_path, mode='w' if first_write['val1'] else 'a', index=False, header=first_write['val1'])
            first_write['val1'] = False
            
        if not df_val2.empty: 
            df_val2.to_csv(val2_path, mode='w' if first_write['val2'] else 'a', index=False, header=first_write['val2'])
            first_write['val2'] = False


def main():
    parser = argparse.ArgumentParser(description="Split the original raw dataset into Train, Val1, Val2, and Test.")
    parser.add_argument("--input", default="final_chess_dataset_max100.csv", help="Input CSV")
    parser.add_argument("--output_dir", default="original_splits", help="Folder to save the splits")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: '{args.input}' not found. Check your file path.")
        return

    split_original_dataset(args.input, args.output_dir)

if __name__ == "__main__":
    main()
