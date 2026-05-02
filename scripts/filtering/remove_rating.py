import os
import re
import argparse
from tqdm import trange


def process_file(input_filepath, output_filepath):
    games_discarded = 0

    white_pattern = re.compile(r'\[WhiteElo\s+"([^"]+)"\]')
    black_pattern = re.compile(r'\[BlackElo\s+"([^"]+)"\]')

    with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_filepath, 'w', encoding='utf-8') as outfile:
        
        buffer = []
        white_elo = None
        black_elo = None

        def evaluate_and_write_game():
            nonlocal games_discarded
            if buffer:
                white_is_valid = white_elo is not None and white_elo.isdigit()
                black_is_valid = black_elo is not None and black_elo.isdigit()

                if white_is_valid and black_is_valid:
                    outfile.writelines(buffer)
                    games_kept += 1
                else:
                    games_discarded += 1

        for line in infile:
            if line.startswith('[Event '):
                evaluate_and_write_game()
                
                buffer = [line]
                white_elo = None
                black_elo = None
                
            else:
                buffer.append(line)
                
                if line.startswith('[WhiteE'):
                    match = white_pattern.search(line)
                    if match:
                        white_elo = match.group(1)
                        
                elif line.startswith('[BlackE'):
                    match = black_pattern.search(line)
                    if match:
                        black_elo = match.group(1)
        
        evaluate_and_write_game()

    return games_discarded

def main():
    parser = argparse.ArgumentParser(description="Filter out games with non-numeric (provisional/missing) ratings.")
    parser.add_argument("--input_dir", default="../filtered_types/", help="Directory with original files")
    parser.add_argument("--output_dir", default="../final_clean_data/", help="Directory to save filtered files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    total_discarded = 0

    for year in range(2014, 2020):
        for month in trange(1, 13):
            filename = f"{month:02d}-{year}.txt"
            input_path = os.path.join(args.input_dir, filename)
            output_path = os.path.join(args.output_dir, filename)
            
            if os.path.exists(input_path):
                discarded = process_file(input_path, output_path)
                total_discarded += discarded

    print(f"Corrupt discarded: {total_discarded}")

if __name__ == "__main__":
    main()
