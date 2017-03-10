dataset = open('normalized_dataset.csv', 'r')
learning_set = open('learning_set.csv', 'w')
test_set = open('test_set.csv', 'w')

rows = filter(lambda line: line != '\n' and line.split(',')[-1] not in ['\n', 'UNBEKANNT', 'UNBEKANNT\n'], dataset.readlines())
header = rows[0].split(',')
header.remove('mentions_count')
header = ','.join(header)
rows = rows[1:]

learning_set.write(header)
test_set.write(header)

test_rows = {}

for row in rows:
    label = row.split(',')
    row = row.split(',')
    label = row[-1].strip('\n')
    row = row[:-2] + [row[-1]]
    row = ','.join(row)

    if label in test_rows:
        if test_rows[label] < 200:
            test_set.write(row)
            test_rows[label] += 1
        else:
            learning_set.write(row)
    else:
        test_rows[label] = 1
        test_set.write(row)

dataset.close()
learning_set.close()
test_set.close()

print test_rows.keys()

learning_set = open('learning_set.csv', 'r')
test_set = open('test_set.csv', 'r')

print 'Learning datapoints: ' + str(len(learning_set.readlines()) - 1)
print 'Test datapoints: ' + str(len(test_set.readlines()) - 1)
