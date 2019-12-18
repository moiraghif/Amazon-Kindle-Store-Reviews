#!/home/fede/.anaconda/bin/python


import sys

prev = ""
LIM = 2
SEP = "\t"


def counter():
    n = 0
    
    def increase():
        nonlocal n
        n += 1
        return str(n - 1)
    
    return increase


def print_ngram(ngram, count):
    if int(count) >= LIM:
        pos = POSITION()
        sys.stdout.write(pos + SEP + ngram + "\n")


if __name__ == "__main__":
    POSITION = counter()
    actual_ngram = counter()

    for line in sys.stdin:
        line = line.strip()
        if line == prev:
            actual_ngram()
        else:
            print_ngram(prev, actual_ngram())
            prev = line
            actual_ngram = counter()

    print_ngram(prev, actual_ngram())
