import os
import re
import pandas as pd
import argparse
from tqdm import trange

CSV_COLUMNS = [
    'Date',
    'White_Elo', 'Black_Elo',
    'Site_FICS', 'Site_Lichess',
    'Game_Type_Bullet', 'Game_Type_Blitz', 'Game_Type_Rapid',
    'Result_White_Checkmate', 'Result_Black_Checkmate', 
    'Result_White_Resign', 'Result_Black_Resign', 
    'Result_White_Time', 'Result_Black_Time', 'Result_Draw',
    'Game'
]

def parse_game(buffer, platform):
    date = None
    game_type = None
    result_type = None
    white_elo = None
    black_elo = None
    moves = []
    
    result_tag = None
    term_tag = None
    
    for line in buffer:
        if line.startswith('['):
            if line.startswith('[Event '):
                lower_line = line.lower()
                if 'bullet' in lower_line or 'lightning' in lower_line: game_type = 'Bullet'
                elif 'blitz' in lower_line: game_type = 'Blitz'
                elif 'rapid' in lower_line or 'standard' in lower_line or 'classical' in lower_line: game_type = 'Rapid'
                    
            elif line.startswith('[Date ') or line.startswith('[UTCDate '):
                match = re.search(r'"(\d{4}\.\d{2}\.\d{2})"', line)
                if match:
                    date = match.group(1).replace('.', '-')
            
            elif line.startswith('[WhiteElo '):
                match = re.search(r'"(\d+)"', line)
                if match: white_elo = int(match.group(1))
            
            elif line.startswith('[BlackElo '):
                match = re.search(r'"(\d+)"', line)
                if match: black_elo = int(match.group(1))
                    
            elif line.startswith('[Result '):
                match = re.search(r'"(.*?)"', line)
                if match: result_tag = match.group(1)
                    
            elif line.startswith('[Termination '):
                match = re.search(r'"(.*?)"', line)
                if match: term_tag = match.group(1)
        else:
            if line.strip(): moves.append(line.strip())
                
    moves_str = " ".join(moves)
    
    if platform == 'FICS':
        match = re.search(r'\{(.*?)\}', moves_str)
        if match:
            reason = match.group(1).lower()
            if 'white checkmated' in reason: result_type = 'Result_Black_Checkmate'
            elif 'black checkmated' in reason: result_type = 'Result_White_Checkmate'
            elif 'white forfeits on time' in reason: result_type = 'Result_Black_Time'
            elif 'black forfeits on time' in reason: result_type = 'Result_White_Time'
            elif 'white resigns' in reason: result_type = 'Result_Black_Resign'
            elif 'black resigns' in reason: result_type = 'Result_White_Resign'
            elif 'draw' in reason or 'material' in reason: result_type = 'Result_Draw'
            
    elif platform == 'Lichess':
        if result_tag == '1/2-1/2': result_type = 'Result_Draw'
        elif result_tag == '1-0':
            if term_tag == 'Time forfeit': result_type = 'Result_White_Time'
            elif term_tag == 'Normal':
                if '#' in moves_str: result_type = 'Result_White_Checkmate'
                else: result_type = 'Result_White_Resign'
        elif result_tag == '0-1':
            if term_tag == 'Time forfeit': result_type = 'Result_Black_Time'
            elif term_tag == 'Normal':
                if '#' in moves_str: result_type = 'Result_Black_Checkmate'
                else: result_type = 'Result_Black_Resign'

    if date and game_type and result_type and white_elo and black_elo and moves_str:
        record = {col: 0 for col in CSV_COLUMNS}
        
        record['Date'] = date
        record['White_Elo'] = white_elo
        record['Black_Elo'] = black_elo
        record['Game'] = moves_str
        
        record[f'Site_{platform}'] = 1
        record[f'Game_Type_{game_type}'] = 1
        record[result_type] = 1
        
        return record
    else:
        raise ValueError(f"Something is missing: {date}, {game_type}, {result_type}, {white_elo}, {black_elo}, {moves_str}")

    
def extract_from_file(filepath, platform, records_list):
    if not os.path.exists(filepath):
        return

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        buffer = []
        for line in f:
            if line.startswith('[Event '):
                if buffer:
                    record = parse_game(buffer, platform)
                    if record: records_list.append(record)
                buffer = [line]
            else:
                buffer.append(line)
        
        if buffer:
            record = parse_game(buffer, platform)
            if record: records_list.append(record)

def main():
    parser = argparse.ArgumentParser(description="Build massive dataset using RAM-safe chunking, including Elo ratings.")
    parser.add_argument("--fics_dir", default="../final_dataset/fics/", help="Path to fully cleaned FICS data")
    parser.add_argument("--lichess_dir", default="../final_dataset/lichess/", help="Path to fully cleaned Lichess data")
    parser.add_argument("--output", default="final_chess_dataset.csv", help="Output CSV filename")
    args = parser.parse_args()

    pd.DataFrame(columns=CSV_COLUMNS).to_csv(args.output, index=False)

    total_games_processed = 0

    for year in range(2014, 2020):
        for month in trange(1, 13):
            filename = f"{month:02d}-{year}.txt"
            
            fics_path = os.path.join(args.fics_dir, filename)
            lichess_path = os.path.join(args.lichess_dir, filename)
            
            if not os.path.exists(fics_path) and not os.path.exists(lichess_path):
                continue

            month_records = []
            
            extract_from_file(fics_path, 'FICS', month_records)
            extract_from_file(lichess_path, 'Lichess', month_records)

            if month_records:
                df_month = pd.DataFrame(month_records, columns=CSV_COLUMNS)
                df_month = df_month.sort_values(by='Date')
                df_month.to_csv(args.output, mode='a', index=False, header=False)
                
                chunk_size = len(df_month)
                total_games_processed += chunk_size
                
                del month_records
                del df_month


if __name__ == "__main__":
    main()
