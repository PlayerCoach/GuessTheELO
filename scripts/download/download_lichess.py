import random
import time
import os
import argparse

import requests
import zstandard as zstd
from tqdm import tqdm


BASE_URL = 'https://database.lichess.org/standard'
SUBMIT_URL = f'{BASE_URL}/lichess_db_standard_rated_'
OUTPUT_DIR = "../raw_data/lichess"


def download_single_month(output_dir, year, month, target_games):
    try:
        os.makedirs(output_dir, exist_ok=True)
        games_buffer = []
        
        url = f"{SUBMIT_URL}{year}-{month:02d}.pgn.zst"

        with requests.get(url, stream=True) as response:
            if response.status_code != 200:
                print(f"Download failed. Status: {response.status_code}")
                return -1
            
            total_size = int(response.headers.get('content-length', 0))
            decomp = zstd.ZstdDecompressor()
            
            with tqdm.wrapattr(response.raw, "read", total=total_size, desc=f"{month:02d}-{year}") as wrapped_raw:
                with decomp.stream_reader(wrapped_raw) as reader:
                    games_seen = 0
                    tail = b""
                    
                    while True:
                        chunk = reader.read(8 * 1024 * 1024)
                        if not chunk:
                            break
                            
                        # Combine the tail from the last chunk with the new chunk
                        data = tail + chunk
                        
                        parts = data.split(b"\n[Event ")
                        
                        # The last part might be an incomplete game, save it for the next loop
                        tail = parts.pop()
                        
                        for part in parts:
                            # Re-add the marker that split() removed
                            game_bytes = b"[Event " + part 
                            games_seen += 1
                            
                            if len(games_buffer) < target_games:
                                games_buffer.append(game_bytes)
                            else:
                                j = random.randint(0, games_seen - 1)
                                if j < target_games:
                                    games_buffer[j] = game_bytes
        
        if tail:
            game_bytes = b"[Event " + tail
            games_seen += 1
            if len(games_buffer) < target_games:
                games_buffer.append(game_bytes)
            else:
                j = random.randint(0, games_seen - 1)
                if j < target_games:
                    games_buffer[j] = game_bytes

        extracted_path = os.path.join(output_dir, f"{month:02d}-{year}.txt")
        with open(extracted_path, 'wb') as f:
            for game in games_buffer:
                f.write(game)
        return 0

    except Exception as e:
        print(f"Error processing {month:02d}.{year}: {e}")
        return -1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and sample PGN games from Lichess.")
    parser.add_argument("--output_dir", type=str, default="../raw_data/lichess", 
                        help="Directory to save the sampled PGN files")
    parser.add_argument("--start_year", type=int, default=2014, 
                        help="Year to start downloading from")
    parser.add_argument("--num_years", type=int, default=1, 
                        help="Number of years to download")
    parser.add_argument("--target_games", type=int, default=200_000, 
                        help="Number of random games to sample per month")

    args = parser.parse_args()
    
    for year in range(args.start_year, args.start_year + args.num_years):
        for month in range(1, 13):
            status = download_single_month(args.output_dir, year, month, args.target_games)
            if status == 0:
                print(f"Correctly downloaded the data from {month:02d}.{year}")
            else:
                print(f"Error when downloading the data from {month:02d}.{year}")
            time.sleep(10)