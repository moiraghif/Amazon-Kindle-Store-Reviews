#!/home/fede/.anaconda/bin/python


import re
import sys


SEP = "\t"


def parse(line):  # product, vote, rate, text
    return re.match(r"^\w+\t(\w+)\t(\d)\t(.+)",
                    line).groups()


def counter():
    n = 0
    while True:
        yield str(n)
        n += 1


if __name__ == "__main__":
    for i, line in zip(counter(), sys.stdin):
        product, rate, text = parse(line)
        sys.stdout.write(SEP.join([i, rate, text]) + "\n")
