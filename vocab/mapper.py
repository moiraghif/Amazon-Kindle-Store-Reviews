#!/home/fede/.anaconda/bin/python


import sys
import re


def parse(line):  # ngrams
    return re.match(r"^\w+\t\d+\t\d\t(.+)", line) \
             .groups()[0] \
             .split(",")


if __name__ == "__main__":
    for line in sys.stdin:
        for ngram in parse(line):
            sys.stdout.write(ngram + "\n")
