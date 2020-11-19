import pandas as pd


def load_all() -> pd.DataFrame:
    return pd.read_csv('data/alcohol.csv').head(100)


def load_by_ids(ids):
    winestyle_filtered = pd.read_csv('data/winestyle_filtered.csv', index_col='id')
    return winestyle_filtered.iloc[list(ids)]



