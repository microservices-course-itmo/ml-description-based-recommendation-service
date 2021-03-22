from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models.word2vec import Text8Corpus
from gensim.models import Word2Vec
from preprocessing.filter import Filter
import numpy as np


class Wine2Vec:

    def __init__(self):
        self.tf_idf = TfidfVectorizer()
        self.word2vec = None
        self.filter = Filter()
        self.corpus_path = 'data/corpus_winestyle.txt'

    def save_corpus(self, filtered_data):
        with open(self.corpus_path, 'w') as corpus_file:
            for d in filtered_data['description']:
                print(d, file=corpus_file)

    def fit_transform(self, data, return_ids=False, overwrite_corpus=True):
        filtered_data = self.filter.filter_dataset(data)
        if overwrite_corpus:
            self.save_corpus(filtered_data)
            self.tf_idf = self.tf_idf.fit(filtered_data['description'].values.astype('U'))
            corpus = Text8Corpus(self.corpus_path)
            self.word2vec = Word2Vec(corpus, size=300, min_count=1)
        tf_idf_weightings = dict(zip(self.tf_idf.get_feature_names(), self.tf_idf.idf_))
        vectors = []
        ids = []
        counter_empty = 0
        for i, d in enumerate(filtered_data['description'].values.astype('U')):
            descriptor_count = 0
            weighted_terms = []
            terms = d.split(' ')
            for term in terms:
                if term in tf_idf_weightings.keys():
                    tf_idf_weighting = tf_idf_weightings[term]
                    word_vector = self.word2vec.wv.get_vector(term).reshape(1, 300)
                    weighted_word_vector = tf_idf_weighting * word_vector
                    weighted_terms.append(weighted_word_vector)
                    descriptor_count += 1
            if len(weighted_terms) == 0:
                counter_empty += 1
            review_vector = [np.zeros(300)] if not len(weighted_terms) else sum(weighted_terms) / len(weighted_terms)
            vectors.append(review_vector)
            ids.append(filtered_data['wine_id'][i])
        # print('Вин без описания', counter_empty)
        vectors = np.concatenate(vectors)
        return vectors, np.array(ids) if return_ids else vectors
