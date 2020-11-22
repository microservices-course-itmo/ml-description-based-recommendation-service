import pandas as pd


def load_all():
    return pd.read_csv('data/alcohol.csv').head(1000)


def load_by_ids(ids):
    alcohol = pd.read_csv('data/alcohol.csv')
    return alcohol.iloc[ids]



