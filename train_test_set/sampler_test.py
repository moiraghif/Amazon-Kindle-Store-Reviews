#!/home/fede/.anaconda/bin/python


import re
import sys


SEP = "\t"


def parse(line):  # i, rate, text
    return re.match(r"^(\d+)\t(\d)\t(.+)", line).groups()


def generate_set_from_csv(file_path):
    with open(file_path) as train_set_index:
        train_set_docs = {
            int(line) for line in train_set_index.readlines() }

    def query(n):
        nonlocal train_set_docs
        return int(n) in train_set_docs

    return query


INDEX_FILE = "train_set_index.csv"
is_in_train_set = generate_set_from_csv(INDEX_FILE)

if __name__ == "__main__":
    for line in sys.stdin:
        n, rate, text = parse(line)
        if not is_in_train_set(n):
            sys.stdout.write(SEP.join([n, rate, text]) + "\n")
