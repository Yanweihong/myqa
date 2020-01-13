import codecs
import logging
import pickle
from collections import Counter

import jieba
import jieba.analyse
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from myqa.retriever.doc_db import DocDB


def fetch_text(doc_id):
    global PROCESS_DB
    return PROCESS_DB.get_doc_text((doc_id,))


PROCESS_DB = DocDB(db_path=r'D:\workspace\pycharm\myQA\test1.db')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)

# 让jieba闭嘴！
jieba.setLogLevel(logging.INFO)

# 全局停用词
stopwords = []
st = codecs.open(r'D:\workspace\pycharm\myQA\stopwords.txt', 'r', 'utf-8')
for line in st:
    line = line.strip()
    stopwords.append(line)


# 取_dict中value最大的N个pairs
def get_order_dict_N(_dict, N):
    result = Counter(_dict).most_common(N)
    d = {}
    for k, v in result:
        d[k] = v
    return d


def query_process(query):
    """
    tokenize query from str to word list, then remove stopwords
    """
    query_words = [w for w in jieba.cut_for_search(query)]
    for query_word in query_words:
        if query_word in stopwords:
            query_words.remove(query_word)
    return query_words


class TfidfDocRanker(object):

    def __init__(self, tfidf_path=None, query='', k=5, doc_dict=None):
        tfidf_path = r'D:\workspace\pycharm\myQA\model\sklearn_tfidf.pkl'
        tfidf_matrix_path = r'D:\workspace\pycharm\myQA\model\tfidf_matrix.pkl'
        doc_dict_path = r'D:\workspace\pycharm\myQA\model\doc2idx.pkl'
        logger.info("TFIDF model loading……")
        self.tfidf_vectorizer = pickle.load(codecs.open(tfidf_path, 'rb'))
        self.tfidf_matrix = pickle.load(codecs.open(tfidf_matrix_path, 'rb'))
        self.doc_dict = pickle.load(codecs.open(doc_dict_path, 'rb'))
        logger.info("TFIDF model loaded")
        self.query = " ".join(jieba.cut(query))

    def closest_docs(self, query,k = 5):
        vectorizer = self.tfidf_vectorizer
        docs_tfidf = self.tfidf_matrix
        query_tfidf = vectorizer.transform([query])
        cosine_sim = cosine_similarity(query_tfidf, docs_tfidf).flatten()

        ind = np.argpartition(cosine_sim, -k)[-k:]
        o_sort = ind[np.argsort(-cosine_sim[ind])]
        doc_scores = cosine_sim[o_sort]
        doc_ids = []
        for i in o_sort:
            doc_ids.append(self.doc_dict[i])
        return o_sort.tolist(),  doc_scores.tolist()


if __name__ == '__main__':
    ranker = TfidfDocRanker()
    query = " ".join(jieba.cut(fetch_text(13)))
    indices,scores=ranker.closest_docs(query=query)
    print(indices)
    print(scores)
