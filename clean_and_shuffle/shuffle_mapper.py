#!/home/fede/.anaconda/bin/python


import string
import sys
from numpy import random


RANDOM_SEED = 20191215  # date of Fat Cow Festival in Carrù, Italy
LEN = 4
SEP = "\t"

random.seed(RANDOM_SEED)



def generate_random_string(length):
    while True:
        yield "".join(random.choice(list(string.ascii_uppercase), length))


if __name__ == "__main__":
    for random_string, line in zip(generate_random_string(LEN), sys.stdin):
        sys.stdout.write(SEP.join([random_string, line.strip()]) + "\n")
