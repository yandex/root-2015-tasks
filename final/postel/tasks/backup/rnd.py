#!/usr/bin/env python

import random, sys
import datetime

CATEGORIES = [
    'agrobiologia', 'astronomy', 'chemistry', 'estetica', 'geography',
    'geology', 'gyroscope', 'law', 'literature', 'marketing', 'mathematics',
    'music', 'philosophy', 'physics', 'polit', 'psychology',
]
FILES = 100

def files(iteration):
    random.seed(iteration)
    if iteration == 1:
        files = ['{}/{}'.format(category, 1 + random.randrange(FILES))
                 for category in CATEGORIES]
    else:
        nr_files = random.randrange(1, len(CATEGORIES)/2)
        files = ['{}/{}'.format(CATEGORIES[random.randrange(len(CATEGORIES))],
                                1 + random.randrange(FILES))
                 for i in range(nr_files)]
    for filename in files:
        sys.stdout.write('{}\0'.format(filename))

def key(iteration):
    symbols = '0123456789ABCDEF'
    random.seed(iteration)
    print ''.join([symbols[random.randrange(len(symbols))]
                   for _ in range(32)])

def date(iteration):
    startdate = datetime.date(2011, 3, 25)
    print datetime.datetime.strftime(
        startdate + datetime.timedelta(days=7) * (iteration-1), "%Y-%m-%d")

if __name__ == '__main__':
    if sys.argv[1] == 'files':
        files(int(sys.argv[2]))
    elif sys.argv[1] == 'key':
        key(int(sys.argv[2]))
    elif sys.argv[1] == 'date':
        date(int(sys.argv[2]))
    else:
        sys.exit(1)
