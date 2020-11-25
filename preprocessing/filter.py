import pandas as pd
from difflib import get_close_matches
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


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


class Mapper:

    def __init__(self, level='raw_descriptor', norm=None):
        self.level = level
        self.norm = Normalizer() if norm is None else norm
        self.mapping = pd.read_csv('data/descriptor_mapping_ru_norm.csv', sep=';')

    @staticmethod
    def count_matches(word, words, method='count'):
        if method == 'count':
            return words.count(word)
        elif method == 'extended_count':
            return ' '.join(words).count(word)
        elif method == 'fuzzy':
            return len(get_close_matches(word, words, cutoff=0.8))

    def map(self, norm_description):
        descriptors = self.mapping['raw_descriptor']
        description_map = {}
        for i, word in enumerate(descriptors):
            count = self.count_matches(word, norm_description)
            if count:
                description_map[self.mapping[self.level][i]] = count
        return description_map

    def map_description(self, description):
        normalised_description = self.norm.normalise_description(description)
        description_map = self.map(normalised_description)
        return ' '.join(' '.join([key] * description_map[key]) for key in description_map)


class Filter:

    def __init__(self, mapper=None):
        self.mapper = Mapper() if mapper is None else mapper

    def filter_dataset(self, data):
        filtered_data = data.copy()
        for i in data.index:
            filtered_data.loc[i, 'description'] = self.mapper.map_description(data['description'][i])
        return filtered_data
