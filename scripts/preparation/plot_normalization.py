import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def plot_combined_rating_distribution(data_dir, output_dir):
    files = {
        'Train (2014-2018)': 'train.csv', 
        'Val 1 (2019 H1)': 'val_split1.csv',
        'Val 2 (2018 H2)': 'val_split2.csv',
        'Test (2019 H2)': 'test.csv'
    }
    
    plt.figure(figsize=(14, 7))
    
    global_max_elo = 0
    
    for set_name, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Skipping {set_name}: File not found at {filepath}")
            continue
            
        
        df = pd.read_csv(filepath, usecols=['White_Elo', 'Black_Elo'])
        
        avg_elo = (df['White_Elo'] + df['Black_Elo']) / 2
        
        if avg_elo.max() > global_max_elo:
            global_max_elo = avg_elo.max()
        
        counts, bin_edges = np.histogram(avg_elo, bins=100, density=True)
        
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        plt.plot(bin_centers, counts, label=set_name, linewidth=2.5)

    plt.title("Rating Distribution per Data Split (Density Curve)")
    
    if global_max_elo < 10:
        plt.xlabel("Standardized Average Match Elo (Z-Score)")
        plt.xlim(-4, 4)
    else:
        plt.xlabel("Average Match Elo")
        plt.xlim(800, 2800)
        
    plt.ylabel("Density (Relative Frequency)")
    
    plt.legend(title="Dataset Split", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, '7_combined_rating_distribution.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    


def main():
    parser = argparse.ArgumentParser(description="Plot combined rating distributions across dataset splits.")
    parser.add_argument("--input_dir", default="model_splits", help="Folder containing split CSVs")
    parser.add_argument("--output_dir", default="png_visualizations", help="Folder to save the final PNG chart")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    
    sns.set_theme(style="whitegrid", palette="muted")

    plot_combined_rating_distribution(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
