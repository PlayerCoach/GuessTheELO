import os
import re
import argparse
from tqdm import trange

def process_file(input_filepath, output_filepath):
    games_discarded = 0

    fics_ending_regex = re.compile(r'\{(.*?)\}\s+(?:1-0|0-1|1/2-1/2|\*)')
    result_tag_regex = re.compile(r'\[Result\s+"(.*?)"\]')
    termination_tag_regex = re.compile(r'\[Termination\s+"(.*?)"\]')

    with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_filepath, 'w', encoding='utf-8') as outfile:
        
        buffer = []
        move_lines = []
        platform = None
        result = None
        termination = None

        def evaluate_and_write_game():
            nonlocal games_discarded
            if not buffer:
                return

            keep_game = False
            moves_str = " ".join(move_lines)

            if platform == 'FICS':
                match = fics_ending_regex.search(moves_str)
                if match:
                    reason = match.group(1).lower()
                    if ('checkmated' in reason or 
                        'forfeits on time' in reason or 
                        'resigns' in reason or 
                        'draw' in reason or 
                        'no material to mate' in reason or 
                        'mating material' in reason):
                        keep_game = True

            elif platform == 'Lichess':
                if result == '1/2-1/2':
                    keep_game = True  
                elif result in ('1-0', '0-1'):
                    if termination in ('Normal', 'Time forfeit'):
                        keep_game = True
                    
            if keep_game:
                outfile.writelines(buffer)
            else:
                games_discarded += 1

        for line in infile:
            if line.startswith('[Event '):
                evaluate_and_write_game()
                
                buffer = [line]
                move_lines = []
                platform = None
                result = None
                termination = None
                
            else:
                buffer.append(line)
                
                if line.startswith('['):
                    if line.startswith('[Site "FICS'):
                        platform = 'FICS'
                    elif line.startswith('[Site "https://lichess'):
                        platform = 'Lichess'
                    elif line.startswith('[Result '):
                        match = result_tag_regex.search(line)
                        if match:
                            result = match.group(1)
                    elif line.startswith('[Termination '):
                        match = termination_tag_regex.search(line)
                        if match:
                            termination = match.group(1)
                else:
                    if line.strip():
                        move_lines.append(line.strip())
        
        evaluate_and_write_game()

    return games_discarded


def main():
    parser = argparse.ArgumentParser(description="Filter out games with non-standard endings (abandoned, disconnected).")
    parser.add_argument("--input_dir", default="../final_clean_data/", help="Directory with original files")
    parser.add_argument("--output_dir", default="../standard_endings_data/", help="Directory to save filtered files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    total_discarded = 0

    for year in range(2014, 2020):
        for month in trange(1, 13):
            filename = f"{month:02d}-{year}.txt"
            input_path = os.path.join(args.input_dir, filename)
            output_path = os.path.join(args.output_dir, filename)
            
            if os.path.exists(input_path):
                print(f"Filtering endings in {filename}...", end='\r')
                discarded = process_file(input_path, output_path)
                total_discarded += discarded

    print(f"Games discarded: {total_discarded}")
    
if __name__ == "__main__":
    main()
