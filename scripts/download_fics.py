import re
import time
import bz2
import random
import os
import argparse

import requests
from tqdm import tqdm


BASE_URL = 'https://www.ficsgames.org'
SUBMIT_URL = f'{BASE_URL}/cgi-bin/download.cgi'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}
OUTPUT_DIR = "../raw_data/fics"


def download_single_month(output_dir, year, month, target_games):
    os.makedirs(output_dir, exist_ok=True)
    games_buffer = []
    games_seen = 0
    
    payload = {
        'gametype': '1',
        'player': '',
        'year': year,
        'month': month,
        'movetimes': '0',
        'download': 'Download'
    }

    with requests.Session() as session:
        # Get the download link
        response = session.post(SUBMIT_URL, data=payload, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error submitting form for {month:02d}-{year}")
            return -1

        match = re.search(r'<a href="(/dl/[^"]+)">', response.text)        
        if not match:
            print(f"Failed to find download link for {month:02d}-{year}")
            return -1

        full_download_url = BASE_URL + match.group(1)
        
        # Download
        file_response = session.get(full_download_url, stream=True)
        if file_response.status_code == 200:
            total_size = int(file_response.headers.get('content-length', 0))
            
            decomp = bz2.BZ2Decompressor()
            tail = b""
            
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"FICS {month:02d}-{year}") as pbar:
                for chunk in file_response.iter_content(chunk_size=1024*1024):
                    if not chunk:
                        continue
                    
                    pbar.update(len(chunk))
                    
                    try:
                        decompressed_data = decomp.decompress(chunk)
                    except EOFError:
                        break
                    
                    # Combine the tail from the last chunk with the new chunk
                    data = tail + decompressed_data
                    
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
                games_seen += 1
                if len(games_buffer) < target_games:
                    games_buffer.append(b"[Event " + tail)
                else:
                    j = random.randint(0, games_seen - 1)
                    if j < target_games:
                        games_buffer[j] = b"[Event " + tail

            extracted_path = os.path.join(output_dir, f"{month:02d}-{year}.txt")
            with open(extracted_path, 'wb') as f:
                for game in games_buffer:
                    f.write(game)
            
            return 0
        else:
            print(f"Download failed with status: {file_response.status_code}")
            return -1
        
   
if __name__ == "__main__":
    start_year = 2013
    num_years = 1
    target_games = 200_000
    for year in range(start_year, start_year+num_years):
        for month in range(1, 13):
            status = download_single_month(OUTPUT_DIR, year, month, target_games)
            if status == 0:
                print(f"Correctly downloaded the data from {month:02d}.{year}")
            else:
                print(f"Error when downloading the data from {month:02d}.{year}")
            time.sleep(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and sample PGN games from Fics.")
    parser.add_argument("--output_dir", type=str, default="../raw_data/fics", 
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