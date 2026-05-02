import os
import re
import argparse

import pandas as pd
from tqdm import trange


def extract_dates_from_file(filepath):
    dates = []
    date_pattern = re.compile(r'\[Date\s+"(\d{4}\.\d{2}\.\d{2})"\]')
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            dates = date_pattern.findall(content)
    except FileNotFoundError:
        print(f"Warning: File {filepath} not found.")
    
    return dates


def main():
    parser = argparse.ArgumentParser(description="Count chess games per day and append to CSV.")
    parser.add_argument("col_name", help="The name of the new column")
    parser.add_argument("--output", default="../chess_stats.csv", help="The output CSV filename")
    parser.add_argument("--dir", help="Directory containing the {mm}-{yyyy}.txt files")
    
    args = parser.parse_args()

    all_dates = []
    
    for year in range(2014, 2020):
        for month in trange(1, 13):
            filename = f"{month:02d}-{year}.txt"
            filepath = os.path.join(args.dir, filename)
            
            if os.path.exists(filepath):
                all_dates.extend(extract_dates_from_file(filepath))

    if not all_dates:
        print("No data found. Check your file paths and format.")
        return

    df_new = pd.DataFrame(all_dates, columns=['Date'])
    counts = df_new.value_counts().reset_index()
    counts.columns = ['Date', args.col_name]
    
    counts['Date'] = counts['Date'].str.replace('.', '-', regex=False)

    if os.path.exists(args.output):
        df_existing = pd.read_csv(args.output)
        
        df_final = pd.merge(df_existing, counts, on='Date', how='outer')
    else:
        df_final = counts

    df_final = df_final.sort_values('Date').fillna(0)
    df_final.to_csv(args.output, index=False)

if __name__ == "__main__":
    main()