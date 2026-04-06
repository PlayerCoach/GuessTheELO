import numpy as np

data = np.load("processed_data/chunk_0.npz")
X = data['x'] # (1000, 100, 17, 8, 8)

# Wybieramy: [gra_0, ruch_0, kanal_0, wszystkie_wiersze, wszystkie_kolumny]
print("Macierz kanału 0 (Białe pionki) w 1. ruchu:")
for i in range(17):
    print(f"Kanał {i}:")
    print(X[0, 0, i, :, :])