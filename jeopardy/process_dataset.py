import numpy as np
from rank_bm25 import BM25Okapi
from nltk.corpus import stopwords
import re
from tqdm import tqdm
import pandas as pd
import nltk
from gensim.models import Word2Vec
from scipy.spatial.distance import cosine




english_stopwords = list(set(stopwords.words('english')))

def strip_characters(text):
    t = re.sub('\(|\)|:|,|;|\.|’|”|“|\?|%|>|<', '', text)
    t = re.sub('/', ' ', t)
    t = t.replace("'",'')
    return t

def clean(text):
    t = text.lower()
    t = strip_characters(t)
    return t

def tokenize(text):
    words = nltk.word_tokenize(text)
    return list(set([word for word in words 
                     if len(word) > 1
                     and not word in english_stopwords
                     and not (word.isnumeric() and len(word) != 4)
                     and (not word.isnumeric() or word.isalpha())] )
               )

def preprocess(text):
    t = clean(text)
    tokens = tokenize(t)
    return tokens

class Engine():
    def __init__(self):
        ds_path = "JEOPARDY_QUESTIONS1.json"
        self.df = pd.read_json(ds_path)
        tokenized_corpus = [preprocess(doc.lower()) for doc in tqdm(self.df.question)]
        ans_tokenized = [preprocess(doc.lower()) for doc in tqdm(self.df.answer)]
        self.model = Word2Vec(sentences=np.ravel(ans_tokenized+tokenized_corpus)).wv
        self.bm25 = BM25Okapi(tokenized_corpus)

    def query(self, query, n=10):
        def not_similar(q1, q2):
            try:
                if tokenize(q1) == tokenize(q2):
                    return False
                elif cosine(np.sum(self.model[tokenize(q1.lower())], axis=0), np.sum(self.model[tokenize(q2.lower())], axis=0))>0.95:
                    return False
                return True
            except:
                return True

        doc_scores = self.bm25.get_scores(tokenize(query.lower()))
        ind = np.argsort(doc_scores)[::-1][:n*2]
        res = self.df.iloc[ind]
        return [{'title':f['category'], 'body':f['question'], 'answer':f['answer']}\
            for _,f in res.iterrows() if not_similar(f['answer'], query)][:n]

if __name__ == "__main__":
    eng = Engine()
    print(eng.query('horse'))

