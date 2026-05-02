import os
import re
import argparse

def process_file(input_filepath, output_filepath):
    games_discarded = 0

    date_pattern = re.compile(r'\[(?:UTC)?Date\s+"(\d{4}\.\d{2}\.\d{2})"\]')

    with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_filepath, 'w', encoding='utf-8') as outfile:
        
        buffer = []
        keep_game = True 

        def evaluate_and_write_game():
            nonlocal games_discarded
            if buffer:
                if keep_game:
                    outfile.writelines(buffer)
                else:
                    games_discarded += 1

        for line in infile:
            if line.startswith('[Event '):
                evaluate_and_write_game()
                
                buffer = [line]
                keep_game = True 
            else:
                buffer.append(line)
                
                if keep_game and line.startswith('['):
                    if 'Date' in line:
                        match = date_pattern.search(line)
                        if match:
                            date_str = match.group(1)
                            if date_str < "2014.02.01":
                                keep_game = False
        
        evaluate_and_write_game()

    return games_discarded

def main():
    parser = argparse.ArgumentParser(description="Filter out games played before Feb 1, 2014.")
    parser.add_argument("--input_dir", default="../standard_endings_data/", help="Directory with original files")
    parser.add_argument("--output_dir", default="../final_dataset/", help="Directory to save filtered files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    total_discarded = 0

    for year in range(2014, 2020):
        for month in range(1, 13):
            filename = f"{month:02d}-{year}.txt"
            input_path = os.path.join(args.input_dir, filename)
            output_path = os.path.join(args.output_dir, filename)
            
            if os.path.exists(input_path):
                discarded = process_file(input_path, output_path)
                total_discarded += discarded

    print(f"Games discarded: {total_discarded}")
    
if __name__ == "__main__":
    main()
