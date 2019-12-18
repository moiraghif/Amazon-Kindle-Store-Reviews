#!/home/fede/.anaconda/bin/python


import re
import sys
import tm_preprocessing as nlp


def parse(line):
    return re.match(r"^\d+\t\w+\t\d\t(.+)", line).groups()[0]

def make_ngrams(n, stream):
    for line in stream:
        text = parse(line)
        for ngram in nlp.make_ngrams(text, n):
            yield ngram

N = int(sys.argv[1])


if __name__ == "__main__":
    for ngram in make_ngrams(N, sys.stdin):
        sys.stdout.write(ngram + "\n")
