import pandas as pd

# df = pd.read_csv('../chess_stats_6.csv')

# l_col = 'final_data_lichess'
# f_col = 'final_data_fics'
# l_total = df[l_col].sum()
# f_total = df[f_col].sum()

# print(f"The total sum of the column {l_col} is: {l_total}")
# print(f"The total sum of the column {f_col} is: {f_total}")

df = pd.read_csv(r'..\csv_analysis3_after_100_move_cutoff\12_test_rating_dist.csv')
total = df.loc[df['Site'] == 'FICS', 'Game_Count'].sum()
print(f"The conditional sum is: {total}")