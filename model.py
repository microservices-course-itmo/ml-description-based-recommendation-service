import pandas as pd

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from gensim.models.word2vec import Text8Corpus

from gensim.models import Word2Vec
from difflib import get_close_matches

from sklearn.feature_extraction.text import TfidfVectorizer
from operator import itemgetter

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

import pickle


def read_data():
    winestyle = pd.read_csv('data/alcohol.csv', index_col='id')
    winestyle = winestyle.drop(columns=['url', 'image_url', 'strength'])
    winestyle['description'] = winestyle['aroma'] + ' ' + winestyle['taste'] + ' ' + winestyle['description']
    winestyle = winestyle.drop(columns=['aroma', 'taste', 'food_pairing'])
    return winestyle


class Normalizer:

    def __init__(self, lang='russian'):
        self.stemmer = SnowballStemmer(lang)
        self.stop = stopwords.words(lang)
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')

    def normalise_description(self, description, to_string=False):
        description = str(description)
        description = description.replace('-', ' ')
        tokens = word_tokenize(description.lower())
        normalised_tokens = [self.stemmer.stem(w) for w in tokens if w.isalpha() and w not in self.stop]
        return normalised_tokens if not to_string else ' '.join(normalised_tokens)


def create_corpus(descriptions):
    norm = Normalizer()
    with open('data/corpus_winestyle.txt', 'w') as corpus_file:
        for d in descriptions:
            print(norm.normalise_description(d, to_string=True), file=corpus_file)


def word2vec():
    data = Text8Corpus('data/corpus_winestyle.txt')
    return Word2Vec(data, size=300)


def count_matches(word, string, method='count'):
    if method == 'fuzzy':
        return len(get_close_matches(word, string, cutoff=0.8))
    elif method == 'count':
        return ' '.join(string).count(word)


def map_descriptors(normalised_description, level='raw_descriptor'):
    descriptor_mapping_ru = pd.read_csv('data/descriptor_mapping_ru_norm.csv', sep=';')
    descriptors = descriptor_mapping_ru['raw_descriptor']
    descriptorised_description = {}
    for i, word in enumerate(descriptors):
        count = count_matches(word, normalised_description)
        if count:
            descriptorised_description[descriptor_mapping_ru[level][i]] = count
    return descriptorised_description


def return_descriptor_from_mapping(desc, norm):
    normalised_description = norm.normalise_description(desc)
    description_to_return = ''
    map = map_descriptors(normalised_description, level='level_3')
    for key in map.keys():
        words = ''
        for i in range(map.get(key)):
            words += key + ' '
        words = words.rstrip(' ')
        description_to_return += words + ' '
    description_to_return = description_to_return.rstrip(' ')
    return description_to_return


def filtration(winestyle):
    norm = Normalizer()
    for id in winestyle.index:
        winestyle.loc[id, 'description'] = return_descriptor_from_mapping(winestyle['description'][id], norm)
    winestyle.to_csv('data/winestyle_filtered.csv')
    return winestyle


def vectorization(wine2vec, winestyle_filtered):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit(winestyle_filtered['description'].values.astype('U'))
    dict_of_tfidf_weightings = dict(zip(X.get_feature_names(), X.idf_))

    wine_review_vectors = []
    wtf_terms = []
    for i, d in enumerate(winestyle_filtered['description'].values.astype('U')):
        descriptor_count = 0
        weighted_review_terms = []
        terms = d.split(' ')
        for term in terms:
            if term in dict_of_tfidf_weightings.keys():
                tfidf_weighting = dict_of_tfidf_weightings[term]
                try:
                    word_vector = wine2vec.wv.get_vector(term).reshape(1, 300)
                except:
                    wtf_terms.append(term)
                weighted_word_vector = tfidf_weighting * word_vector
                weighted_review_terms.append(weighted_word_vector)
                descriptor_count += 1
            else:
                continue
        try:
            review_vector = sum(weighted_review_terms) / len(weighted_review_terms)
        except:
            review_vector = []
        vector_and_count = [terms, review_vector, descriptor_count, i]
        wine_review_vectors.append(vector_and_count)

    winestyle_filtered['normalized_descriptors'] = list(map(itemgetter(0), wine_review_vectors))
    winestyle_filtered['review_vector'] = list(map(itemgetter(1), wine_review_vectors))
    winestyle_filtered['descriptor_count'] = list(map(itemgetter(2), wine_review_vectors))
    winestyle_filtered.reset_index(inplace=True)
    winestyle_filtered = pd.read_csv('data/winestyle_filtered.csv', index_col='id')
    return wine_review_vectors, winestyle_filtered


def preprocessing():
    winestyle = read_data()
    create_corpus(winestyle['description'])  # долго
    print('create successful')
    winestyle_filtered = filtration(winestyle)  # долго
    print('create filter')
    return vectorization(word2vec(), winestyle_filtered)


def knn(wine_review_vectors):
    wine_review_vectors = [w for w in wine_review_vectors if w[2] > 5]
    X = np.array([w[1].flatten() for w in wine_review_vectors])
    y = np.array([w[3] for w in wine_review_vectors])
    X = StandardScaler().fit_transform(X)
    model = NearestNeighbors(n_neighbors=10, metric='euclidean').fit(X)
    return model, X, y


if __name__ == '__main__':
    with open('models/preprocessing.pkl', 'wb') as file:
        pickle.dump(preprocessing(), file)

    with open('models/preprocessing.pkl', 'rb') as f:
        wine_review_vectors, winestyle_filtered = pickle.load(f)

    with open('models/knn.pkl', 'wb') as file:
        pickle.dump(knn(wine_review_vectors), file)
