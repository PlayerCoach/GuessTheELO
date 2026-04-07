import os
import re
import argparse
from tqdm import trange

def process_file(input_filepath, output_filepath):
    year_pattern = re.compile(r'\[(?:UTC)?Date\s+"(\d{4})\.\d{2}\.\d{2}"\]')
    
    games_discarded = 0

    with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_filepath, 'w', encoding='utf-8') as outfile:
        
        buffer = []
        keep_game = True 
        
        for line in infile:
            if line.startswith('[Event '):
                if buffer:
                    if keep_game:
                        outfile.writelines(buffer)
                    else:
                        games_discarded += 1
                
                buffer = [line]
                keep_game = True
            else:
                buffer.append(line)
                
                if keep_game and line.startswith('['):
                    match = year_pattern.search(line)
                    if match:
                        year = int(match.group(1))
                        if year < 2014:
                            keep_game = False
        
        if buffer:
            if keep_game:
                outfile.writelines(buffer)
            else:
                games_discarded += 1

    return games_discarded

def main():
    parser = argparse.ArgumentParser(description="Filter out games from before 2014.")
    parser.add_argument("--input_dir", help="Directory with original files")
    parser.add_argument("--output_dir", help="Directory to save filtered files")
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

    print(f"Games discarded: {total_discarded}")

if __name__ == "__main__":
    main()
