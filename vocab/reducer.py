#!/usr/bin/env python

import sys

prev = ""
n = 0
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 3
SEPARATOR = "\t"

def counter():
    n = 0
    def increase():
        nonlocal n
        n += 1
        return n
    return increase

n_seq = counter()


def print_line(line, count):
    if count > LIM:
        print(n_seq(), line, sep=SEPARATOR)
        return True
    return False


for line in sys.stdin:
    line = line[:-1]
    if line == prev:
        n += 1
    else:
        print_line(prev, n)
        prev = line
        n = 0
print_line(prev, n)
