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

def square(val):
    return val * val

def normalize_row(vals):
    #if isinstance(vals[0], basestring): return vals # return unmodifed row when the label column was passed
    vector_length = math.sqrt(math.fsum(map(square, map(float, vals))))
    return map(lambda x: x / vector_length, map(float, vals))

def normalize_dataset(dataset):
    print 'Normalizing dataset...'
    # rotate matrix to get lists of the column values
    rotated_matrix = map(list, zip(*map(lambda s: s.split(','), dataset)))
    normalized = map(normalize_row, rotated_matrix)
    return map(list, zip(*normalized))

def read():
    dataset = open('dataset.csv', 'r')
    datarows = []
    parties = []
    index = 0
    header = ''
    for line in dataset:
        index += 1
        if index == 1:
            header = line
            continue
        datarows.append(','.join(line.split(',')[:-1]))
        parties.append(line.split(',')[-1])

    normfile = open('nomalized_dataset.csv', 'w')
    normfile.write(header + '\n')
    normalized_dataset = normalize_dataset(datarows)
    for i in range(0, len(normalized_dataset)):
        row = normalized_dataset[i]
        normfile.write(','.join(map(str, row)) + ',' + parties[i] + '\n')
    normfile.close()



###################################
read()
