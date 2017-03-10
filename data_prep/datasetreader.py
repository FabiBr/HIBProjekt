from __future__ import division
from string import punctuation
from collections import Counter
import re
from nltk.stem.porter import PorterStemmer
from itertools import groupby
import numpy as np
import math
import vsm
import datetime

###############################################################
# helpers

def getScreenName(line):
    return line.split(',')[2]

def appending(value, line):
    return line + ',' + str(value)

def drop_retweet(tweet):
    if is_retweet(tweet):
        return tweet.split(':', 1)[1].strip()
    return tweet

def drop_mentions(tweet):
    return re.sub(r'/^(?!.*\bRT\b)(?:.+\s)?@\w+/i', '', tweet)

def drop_links(tweet):
    return re.sub(r"(?:\@|https?\://)\S+", "", tweet).strip()

def raw_tweet(tweet):
    return ' '.join(tokenize(tweet=tweet))

def create_party_collection_docs(dict):
    print 'Writing collection docs...'
    for party in dict:
        doc = open(party.lower().replace(' ', '_') + '_doc.txt', 'w')
        doc.write(dict[party])
        doc.close()

def tokenize(tweet):
    regex = re.compile(r'(~\W+)', re.IGNORECASE)
    for c in tweet:
        if c in punctuation:
            tweet = tweet.replace(c, '')
    tweet = re.sub(regex, '', tweet)
    return tweet.split()

def normalize_row(vals):
    if isinstance(vals[0], basestring): return vals # return unmodifed row when the label column was passed
    vector_length = math.sqrt(math.fsum(map(square, map(float, vals))))
    return map(lambda x: x / vector_length, map(float, vals))

def normalize_dataset(dataset):
    print 'Normalizing dataset...'
    # rotate matrix to get lists of the column values
    rotated_matrix = map(list, zip(*map(lambda s: s.split(','), dataset)))
    normalized = map(normalize_row, rotated_matrix)
    return map(list, zip(*normalized))

def square(val):
    return val * val

def csv_filename(party):
    return party.lower().replace(' ', '_') + '.csv'


########################################################################
# feature extraction

def hasLinkValue(tweet):
    if 'http://' in tweet:
        return 1
    else:
        return 0

def count_hashtags(tweet):
    return len(set(part[1:] for part in tweet.split() if part.startswith('#')))

def count_mentions(tweet):
    return len(set(part[1:] for part in tweet.split() if part.startswith('@')))

def is_retweet(tweet):
    if "RT @" in tweet[:5]:
        return 1
    else:
        return 0

def upper_lower_case_ratio(tweet):
    if len(tweet.replace(' ', '')) == 0: return 0
    return sum(1 for c in tweet if c.isupper()) / len(tweet.replace(' ', ''))

def averageWordLength(tweet):
    if len(tweet.split()) == 0: return 0
    return len(tweet.replace(' ', '')) / len(tweet.split())

def count_punctuations(tweet):
    return Counter(c for c in tweet if c in punctuation)

def datarow_for_features(features):
    row = ""
    for feature in features:
        row = row + "," + str(feature)
    return row[1:]

def party(name):
    file = open('bundestagKurz.csv', "r")
    for line in file:
        line = line.replace('GR\x9aNE', 'GRUENE')
        if name.lower() == line.split(';')[-1].strip()[1:].lower():
            return line.split(';')[1]
    return 'UNBEKANNT'

########################################################################
datarows = []
parties = []

def readDataSet(filename):
    print 'Loading input file...'
    file = open(filename, "r")
    index = 0
    people = []
    tweetsPerParty = {}
    collections = {}
    raw_tweets = []
    party_datarows = {}
    opened_party_files = {}
    csv_header = 'cdu_sim, csu_sim, afd_sim, linke_sim, gruene_sim, spd_sim, words_count,average_word_length,case_ratio,screen_name_length,is_retweet,has_link,hashtags_count,mentions_count,party'

    print 'Loading output file...'
    output_file = open("dataset.csv", "w")
    output_file.write(csv_header)

    print 'Loading party comparison file...'
    party_comparision_file = open('party_comparision.csv', 'w')
    party_comparision_file.write('party,average_words_count,average_word_length,average_case_ratio,average_screen_name_length,average_is_retweet,average_has_link,average_hashtags_count,average_mentions_count')

    csu_doc = vsm.textFromFile('csu_doc.txt')
    linke_doc = vsm.textFromFile('die_linke_doc.txt')
    cdu_doc = vsm.textFromFile('cdu_doc.txt')
    gruene_doc = vsm.textFromFile('gruene_doc.txt')
    afd_doc = vsm.textFromFile('afd_doc.txt')
    spd_doc = vsm.textFromFile('spd_doc.txt')
    partyy_docs = [csu_doc, linke_doc, cdu_doc, gruene_doc, afd_doc, spd_doc]

    print 'Processing dataset...'
    for line in file:
        # if index == 0: continue
        # if index not in range(0, 100): return

        # line processing
        screenNameLength = len(getScreenName(line=line))

        # tweet processing
        tweet = ''.join(line.split(',')[3:])
        tweet = tweet.rstrip() # strip all leading and trailing whitespaces

        isRetweet = is_retweet(tweet=tweet)
        tweet = drop_retweet(tweet=tweet)

        hasLink = hasLinkValue(tweet=tweet)
        tweet = drop_links(tweet=tweet)

        mentionsCount = count_mentions(tweet=tweet)
        tweet = drop_mentions(tweet=tweet)

        hashtagsCount = count_hashtags(tweet=tweet)

        tweet = raw_tweet(tweet=tweet)
        raw_tweets.append(tweet)
        wordsCount = len(tweet.split())

        caseRatio = upper_lower_case_ratio(tweet=tweet)
        avrgLettersPerWord = averageWordLength(tweet=tweet)
        partei = party(name=getScreenName(line))

        people.append((getScreenName(line=line)))

        if partei in tweetsPerParty:
            tweetsPerParty[partei].append(tweet)
        else: tweetsPerParty[partei] = []

        # # create party collections
        # if partei in collections:
        #     collections[partei] += ' ' + tweet
        # else: collections[partei] = ''

        cos_sims = vsm.cosine_similarities(query=tweet, documents=partyy_docs)
        spd_sim = cos_sims['spd']
        linke_sim = cos_sims['linke']
        cdu_sim = cos_sims['cdu']
        gruene_sim = cos_sims['gruene']
        afd_sim = cos_sims['afd']
        csu_sim = cos_sims['csu']

        datarow = datarow_for_features([cdu_sim, csu_sim, afd_sim, linke_sim, gruene_sim, spd_sim, wordsCount, avrgLettersPerWord, caseRatio, screenNameLength, isRetweet, hasLink, hashtagsCount, mentionsCount, partei])
        datarows.append(datarow)
        parties.append(partei)

        if index % 100 == 0: print str(index / 30000) + '%'
        # print datarow
        index += 1

    print 'Writing to files...'
    for datarow in datarows:
        output_file.write('\n' + datarow)

    file.close()

    # normalize
    normfile = open('nomalized_dataset.csv', 'w')
    normfile.write(csv_header + '\n')
    normalized_dataset = normalize_dataset(datarows)
    for i in range(0, len(normalized_dataset)):
        row = normalized_dataset[i]
        normfile.write(','.join(map(str, row)) + ',' + parties[i] + '\n')
    normfile.close()

    normalized_rotated = map(list, zip(*normalized_dataset))

    file = open(filename, "r")
    ik = 0
    for line in file:
        partei = party(name=getScreenName(line))
        datarow = normalized_dataset[ik]
        if partei not in party_datarows:
            party_datarows[partei] = [datarow]
        else:
            party_datarows[partei].append(datarow)

        if partei not in opened_party_files:
            party_file = open(csv_filename(partei), "w")
            party_file.write(csv_header + '\n')
            opened_party_files[partei] = party_file

        opened_party_files[partei].write(','.join(map(str, datarow )) + ',' + partei + '\n')
        ik += 1

    # create_party_collection_docs(dict=collections)

    output_file.close()
    party_comparision_file.close()


    # cosine similarities


##############################################################
readDataSet("all-tweets.csv")











































    # for word in reversed(Counter(''.join(tweetsPerParty['GR\x9aNE']).split(' ')).most_common()):
    #     print word

    # uniquePeople = set(people)
    # tuples = []
    #
    # tweetsPerParty = {}
    # peopleInParty = {}
    #
    # for p in people:
    #     partei = party(name=p)
    #     tuples.append((p, partei))
    #     if partei not in tweetsPerParty:
    #         tweetsPerParty[partei] = 1
    #     else:
    #         tweetsPerParty[partei] += 1
    #
    # for p in uniquePeople:
    #     partei = party(name=p)
    #     tuples.append((p, partei))
    #     if partei not in peopleInParty:
    #         peopleInParty[partei] = 1
    #     else:
    #         peopleInParty[partei] += 1
    #
    # avrTweets = {}
    # for key in tweetsPerParty:
    #     avrTweets[key] = tweetsPerParty[key] / peopleInParty[key]
    #
    # # print tweetsPerParty
    # print peopleInParty
    # # print avrTweets
