import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime

def textFromFile(filename):
    txt_file = open(filename, 'r')
    text = txt_file.read().replace('\n', '')
    txt_file.close()
    return text

def cosine_similarities(query, documents):
    # query = ' '.join(sys.argv[1:])
    doc_names = ['query', 'csu', 'linke', 'cdu', 'gruene', 'afd', 'spd']
    #print '\nRanking for query: "' + query + '"\n'

    docs = [query] + documents
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(docs)

    ranking = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)

    scores = {}
    for i in range(0, len(ranking[0])):
        scores[doc_names[i]] = ranking[0][i]
    # scores.sort(key=lambda tuple: tuple[1], reverse=True)

    #for tup in scores: print tup[0] + ': ' + str(tup[1])

    return scores
