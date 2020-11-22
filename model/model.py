import pickle
from sklearn.neighbors import NearestNeighbors
from preprocessing.vectorization import Wine2Vec
from data.db import load_all
import numpy as np
from sklearn.preprocessing import StandardScaler


class ModelLoader:

    def __init__(self, retrain=False):
        self.retrain = retrain

    def load(self):
        if self.retrain:
            data = load_all()
            return Model(NearestNeighbors(n_neighbors=10)).fit(data).dump()
        else:
            return Model(self._load_model())

    def _load_model(self):
        with open('bin/knn.pkl', 'rb') as f:
            model = pickle.load(f)
        return model


class Model:

    def __init__(self, knn):
        self.knn = knn
        self.wine2vec = Wine2Vec()
        self.vectors = []

    def fit(self, data):
        wine_review_vectors = self.wine2vec.fit_transform(data)
        X = np.array([np.array(w[0]).flatten() for w in wine_review_vectors])
        X = StandardScaler().fit_transform(X)
        self.vectors = wine_review_vectors
        self.knn.fit(X)
        return self

    def dump(self):
        if self.knn is not None:
            with open('bin/knn.pkl', 'wb') as file:
                pickle.dump(self.knn, file)
        return self

    def k_neighbors(self, x):
        if self.knn is not None:
            vec = np.array([w[0].flatten() for w in self.vectors if w[1] == x])
            return self.knn.kneighbors(vec)
