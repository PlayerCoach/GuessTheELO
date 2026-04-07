import os
import argparse
from tqdm import trange

def process_file(input_filepath, output_filepath):
    games_kept = 0
    games_discarded = 0

    valid_types = ['bullet', 'lightning', 'blitz', 'rapid', 'standard', 'classical']

    with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_filepath, 'w', encoding='utf-8') as outfile:
        
        buffer = []
        keep_game = False 
        
        for line in infile:
            if line.startswith('[Event '):
                if buffer:
                    if keep_game:
                        outfile.writelines(buffer)
                        games_kept += 1
                    else:
                        games_discarded += 1
                
                buffer = [line]
                
                lower_line = line.lower()
                if any(keyword in lower_line for keyword in valid_types):
                    keep_game = True
                else:
                    keep_game = False
            else:
                buffer.append(line)
        
        if buffer:
            if keep_game:
                outfile.writelines(buffer)
                games_kept += 1
            else:
                games_discarded += 1

    return games_kept, games_discarded

def main():
    parser = argparse.ArgumentParser(description="Filter out non-standard games.")
    parser.add_argument("--input_dir", help="Directory with original files")
    parser.add_argument("--output_dir", help="Directory to save filtered files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    total_kept = 0
    total_discarded = 0

    for year in range(2014, 2020):
        for month in trange(1, 13):
            filename = f"{month:02d}-{year}.txt"
            input_path = os.path.join(args.input_dir, filename)
            output_path = os.path.join(args.output_dir, filename)
            
            if os.path.exists(input_path):
                kept, discarded = process_file(input_path, output_path)
                total_kept += kept
                total_discarded += discarded

    print(f"Games discarded:{total_discarded}")

if __name__ == "__main__":
    main()
