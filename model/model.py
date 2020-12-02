import pickle
from sklearn.neighbors import NearestNeighbors
from preprocessing.vectorization import Wine2Vec
from data.db import load_all
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class ModelLoader:

    def __init__(self, retrain=False):
        self.retrain = retrain

    def load(self):
        if self.retrain:
            data = load_all()
            return Model(NearestNeighbors(n_neighbors=10)).fit(data).dump()
        else:
            return self._load_model()

    def _load_model(self):
        with open('model/bin/model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model


class Model:

    def __init__(self, knn):
        self.knn = knn
        self.wine2vec = Wine2Vec()
        self.scaler = StandardScaler()
        self.vectors = None
        self.ids = None

    def fit(self, data):
        self.vectors, self.ids = self.wine2vec.fit_transform(data, return_ids=True)
        self.scaler = self.scaler.fit(self.vectors)
        self.vectors = self.scaler.transform(self.vectors)
        self.knn.fit(self.vectors)
        return self

    def dump(self):
        if self.knn is not None:
            with open('model/bin/model.pkl', 'wb') as file:
                pickle.dump(self, file)
        return self

    def k_neighbors(self, id, k, desc):
        i, = np.where(self.ids == id)
        if len(i) != 0:
            vec = self.vectors[np.where(self.ids == id)]
        else:
            d = {'id': [id], 'description': [desc]}
            df = pd.DataFrame(data=d)
            vec = self.wine2vec.fit_transform(df, overwrite_corpus=False)
            vec = self.scaler.transform(vec[0])
            # self.vectors = np.vstack([self.vectors, vec.flatten()])
            # self.ids = np.append(self.ids, id)
            # self.dump()
        self.knn.n_neighbors = k + 1
        indices = self.knn.kneighbors(vec, return_distance=False)
        if len(i) != 0:
            ind, = np.where(indices.flatten() == i[0])
            if len(ind) != 0:
                indices = np.delete(indices, ind[0])
        return indices
