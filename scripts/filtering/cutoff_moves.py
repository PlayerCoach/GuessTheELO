import os
import pandas as pd
import argparse
from tqdm import tqdm

def filter_long_games(input_filepath, output_filepath, max_moves=100, chunksize=250000):
    if not os.path.exists(input_filepath):
        print(f"Error: Could not find {input_filepath}. Check your path.")
        return

    chunk_iter = pd.read_csv(input_filepath, chunksize=chunksize)
    
    total_kept = 0
    total_discarded = 0
    
    for i, chunk in tqdm(enumerate(chunk_iter)):
        
        # Get moves like: "1. ", "22. "
        move_counts = chunk['Game'].astype(str).str.count(r'\b\d+\.\s').fillna(0)
        
        mask = move_counts <= max_moves
        filtered_chunk = chunk[mask]
        
        kept = len(filtered_chunk)
        discarded = len(chunk) - kept
        total_kept += kept
        total_discarded += discarded
        
        write_header = (i == 0)
        write_mode = 'w' if i == 0 else 'a'
        
        filtered_chunk.to_csv(output_filepath, mode=write_mode, index=False, header=write_header)
        
    
def main():
    parser = argparse.ArgumentParser(description="Filter out long games.")
    parser.add_argument("--input", default="final_chess_dataset.csv", help="Original CSV")
    parser.add_argument("--output", default="final_chess_dataset_max100.csv", help="Output CSV")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of moves allowed")
    args = parser.parse_args()

    filter_long_games(args.input, args.output, max_moves=args.limit)

if __name__ == "__main__":
    main()
