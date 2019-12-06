#!/usr/bin/env python

import re
import sys
import json


def parse(i, line):
    json_line = json.loads(line)
    if "overall" not in json_line.keys() or \
       "reviewText" not in json_line.keys() or \
       json_line["overall"] == 0.0:
        return None
    rate = int(json_line["overall"])
    text = repr(json_line["reviewText"]).strip()
    return str(i), str(rate), text

def generate_train_set(file_path):
    with open(file_path) as train_set_index:
        train_set_docs = {
            int(line) for line in train_set_index.readlines() }

    def query(n):
        nonlocal train_set_docs
        return int(n) in train_set_docs

    return query


def counter():
    n = 0
    while True:
        yield n
        n += 1

TRAIN_SET = generate_train_set("train_set_index.csv")
docs_counter = counter()

if __name__ == "__main__":
    for i, line in zip(docs_counter, sys.stdin):
        if not TRAIN_SET(i):
            parsed_document = parse(i, line)
            if parsed_document:
                sys.stdout.write("\t".join(parsed_document) + "\n")
