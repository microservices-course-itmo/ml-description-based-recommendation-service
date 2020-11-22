import pandas as pd


def load_all():
    return pd.read_csv('data/alcohol.csv')


def load_by_ids(ids):
    alcohol = pd.read_csv('data/alcohol.csv')
    return alcohol.iloc[ids]



