import os
import pandas as pd

fbref_dir = 'data/FPL/2025/fbref'
print(os.listdir(fbref_dir))
print(pd.read_csv(f'{fbref_dir}/standard.csv').head())