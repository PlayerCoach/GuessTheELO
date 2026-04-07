import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_elo_over_time(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '1_avg_elo_by_year_site_split.csv')
    if not os.path.exists(filepath): return
    
    df = pd.read_csv(filepath)
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Year', y='Avg_Elo', hue='Site', style='Split', markers=True, dashes=False)
    plt.title("Average rating over time")
    plt.ylim(1300, 1800)
    plt.ylabel("Average elo")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '1_elo_over_time.png'), dpi=300)
    plt.close()

def plot_games_by_type(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '3_games_by_gametype.csv')
    if not os.path.exists(filepath): return
    
    df = pd.read_csv(filepath)
    
    plt.figure(figsize=(8, 8)) 
    
    plt.pie(
        df['Game_Count'], 
        labels=df['Game_Type'], 
        autopct='%1.1f%%', 
        startangle=140,
    )
    
    plt.title("Games by time control")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '2_games_by_type.png'), dpi=300)
    plt.close()

def plot_win_rates(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '5_games_by_result.csv')
    if not os.path.exists(filepath): return
    
    df = pd.read_csv(filepath)
    plt.figure(figsize=(6, 6))
    
    plt.pie(df['Game_Count'], labels=df['Result'], autopct='%1.1f%%', 
             startangle=90, wedgeprops={'edgecolor': 'gray'})
    plt.title("Win rates per color")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3_win_rates_pie.png'), dpi=300)
    plt.close()

def plot_elo_difference(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '7_elo_diff_distribution.csv')
    if not os.path.exists(filepath): return
    
    df = pd.read_csv(filepath)
    
    df['Bracket_Label'] = df['Elo_Difference_Bracket'].str.extract(r'\((.*?),\s*(.*?)]').apply(lambda x: f"{float(x[0]):.0f}", axis=1)
    
    df['Sort_Key'] = pd.to_numeric(df['Bracket_Label'])
    df = df[(df['Sort_Key'] >= -500) & (df['Sort_Key'] <= 500)]
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='Bracket_Label', y='Game_Count', color='steelblue')
    plt.title("Distribution of elo delta (white elo - black Elo)")
    plt.xlabel("Elo delta")
    plt.xticks(rotation=45)
    
    for ind, label in enumerate(plt.gca().get_xticklabels()):
        if ind % 2 == 0: label.set_visible(True)
        else: label.set_visible(False)
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '4_elo_difference_dist.png'), dpi=300)
    plt.close()

def plot_game_length_vs_elo(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '14_game_length_vs_ranking.csv')
    if not os.path.exists(filepath): return
    
    df = pd.read_csv(filepath)
    
    df['Elo_Start'] = df['Avg_Elo_Bracket'].str.extract(r'\((.*?),\s*(.*?)]')[0].astype(float)
    df = df.dropna().sort_values('Elo_Start')
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Elo_Start', y='Average_Number_of_Moves', hue='Game_Type', style='Site')
    plt.title("Average game length vs player elo")
    plt.xlabel("Average match elo")
    plt.ylabel("Average number of moves")
    plt.xlim(1000, 2800)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_game_length_vs_rating.png'), dpi=300)
    plt.close()

def plot_combined_rating_distribution(csv_dir, output_dir):
    files = {
        'Train': '10_train_rating_dist_by_year.csv',
        'Val': '11_val_rating_dist.csv',
        'Test': '12_test_rating_dist.csv'
    }
    
    all_data = []

    for set_name, filename in files.items():
        filepath = os.path.join(csv_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            df['Elo_Start'] = df['Avg_Elo_Bin'].str.extract(r'\((.*?),\s*(.*?)]')[0].astype(float)
            df = df.dropna()
            
            df_grouped = df.groupby(['Elo_Start',])['Game_Count'].sum().reset_index()
            
            df_grouped['Dataset_Set'] = set_name
            all_data.append(df_grouped)

    if not all_data:
        return

    combined_df = pd.concat(all_data)

    plt.figure(figsize=(14, 7))
    
    sns.lineplot(
        data=combined_df, 
        x='Elo_Start', 
        y='Game_Count', 
        hue='Dataset_Set', 
        linewidth=2
    )

    plt.title("Rating distribution per data split")
    plt.xlabel("Average match elo")
    plt.ylabel("Number of games")
    
    plt.xlim(800, 2800)
    

    plt.legend(title="Dataset", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '7_combined_rating_distribution.png'), dpi=300)
    plt.close()


def plot_overall_site_distribution(csv_dir, output_dir):
    files = [
        '10_train_rating_dist_by_year.csv',
        '11_val_rating_dist.csv',
        '12_test_rating_dist.csv'
    ]
    
    all_dfs = []
    for f in files:
        path = os.path.join(csv_dir, f)
        if os.path.exists(path):
            temp_df = pd.read_csv(path)
            all_dfs.append(temp_df)
            
    if not all_dfs:
        return

    df = pd.concat(all_dfs)

    df['Elo_Start'] = df['Avg_Elo_Bin'].str.extract(r'\((.*?),\s*(.*?)]')[0].astype(float)
    df = df.dropna()

    df_combined = df.groupby(['Site', 'Elo_Start'])['Game_Count'].sum().reset_index()

    plt.figure(figsize=(12, 6))
    
    sns.lineplot(data=df_combined, x='Elo_Start', y='Game_Count', hue='Site', linewidth=3)

    for site in df_combined['Site'].unique():
        subset = df_combined[df_combined['Site'] == site]
        plt.fill_between(subset['Elo_Start'], subset['Game_Count'], alpha=0.2)

    plt.title("Rating distribution per site")
    plt.xlabel("Average match elo")
    plt.ylabel("Total number of games")
    
    plt.xlim(800, 2800)
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '8_overall_site_distribution.png'), dpi=300)
    plt.close()


def plot_game_length_distribution(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '13_game_length_distribution.csv')
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    df = pd.read_csv(filepath)
    
    df['Bin_Start'] = df['Game_Length_Bin'].str.extract(r'\((\d+),')[0].astype(float)
    df = df.dropna(subset=['Bin_Start'])
    
    df_combined = df.groupby(['Game_Type', 'Bin_Start'])['Game_Count'].sum().reset_index()
    
    plt.figure(figsize=(14, 8))
    
    sns.lineplot(
        data=df_combined, 
        x='Bin_Start', 
        y='Game_Count', 
        hue='Game_Type',
        markers=True, 
        linewidth=2.5
    )
    
    plt.title("Game length distribution per game type", fontsize=15, pad=20)
    plt.xlabel("Game length in moves", fontsize=12)
    plt.ylabel("Number of games", fontsize=12)
    
    ax = plt.gca()
    current_values = ax.get_yticks()
    ax.set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
    
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.legend(title="Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, '11_game_length_by_type.png')
    plt.savefig(save_path, dpi=300)
    plt.close()

def games_over_time(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '4_games_by_year.csv')
    if not os.path.exists(filepath): return
    
    df = pd.read_csv(filepath)
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Year', y='Game_Count', markers=True, dashes=False)
    plt.title("Number of games over time")
    plt.ylabel("Number of games")
    plt.ylim(4e6, 5e6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '9_games_over_time.png'), dpi=300)
    plt.close()

def plot_elo_by_outcome(csv_dir, output_dir):
    filepath = os.path.join(csv_dir, '6_avg_elo_by_outcome.csv')
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    df = pd.read_csv(filepath)
    
    plt.figure(figsize=(8, 6))
    
    ax = sns.barplot(data=df, x='Outcome', y='Avg_Elo', palette='viridis')

    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.2f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 9), 
                    textcoords='offset points',
                    fontsize=10, 
                    fontweight='bold')

    plt.ylim(1500, 1700)

    plt.title("Average elo rating by match outcome", fontsize=14, pad=20)
    plt.ylabel("Average elo", fontsize=12)
    plt.xlabel("Match result", fontsize=12)
    
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, '10_elo_by_outcome.png')
    plt.savefig(save_path, dpi=300)
    plt.close()

def main():
    csv_directory = "../csv_analysis3_after_100_move_cutoff"
    output_directory = "../png_visualizations_after_100_move_cutoff"
    
    if not os.path.exists(csv_directory):
        print(f"Error: Could not find the '{csv_directory}' folder.")
        return
        
    os.makedirs(output_directory, exist_ok=True)
    
    sns.set_theme(style="whitegrid", palette="muted")
    
    plot_elo_over_time(csv_directory, output_directory)
    plot_games_by_type(csv_directory, output_directory)
    plot_win_rates(csv_directory, output_directory)
    plot_elo_difference(csv_directory, output_directory)
    plot_game_length_vs_elo(csv_directory, output_directory)
    plot_combined_rating_distribution(csv_directory, output_directory)
    plot_overall_site_distribution(csv_directory, output_directory)
    games_over_time(csv_directory, output_directory)
    plot_elo_by_outcome(csv_directory, output_directory)
    plot_game_length_distribution(csv_directory, output_directory)

if __name__ == "__main__":
    main()