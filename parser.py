#!/usr/bin/env python

import pandas as pd
import numpy as np
import tm_preprocessing as nlp


def read_vocab(file_path):
    db = pd.read_csv(file_path,
                     sep="\t",
                     header=None,
                     names=["number", "ngram"],
                     index_col="ngram")

    def query_position(query):
        nonlocal db
        if query in db.index:
            return db.loc[[query]]["number"].values[0] - 1
        return False

    return query_position, db.shape[0]


def parse_text(text, ngram_size, method, vocab, N):
    ngrams = nlp.make_ngrams(text, ngram_size)
    out = np.zeros((1, N))
    for ngram in ngrams:
        pos = vocab(ngram)
        if pos:
            out[0, pos] += 1
    return method(out)


def parse_list(text_list, *args):
    return np.vstack([parse_text(text, *args) for text in text_list])


def parser(vocab_path, ngram_size, method):
    vocab, vocab_size = read_vocab(vocab_path)

    def parse_data(x):
        nonlocal vocab, vocab_size
        return parse_list(x, ngram_size, method, vocab, vocab_size)

    return parse_data


def term_frequency(document):
    denominator = document.sum() or 1
    return document / denominator

def normalized_term_frequency(document):
    denominator = document.max() or 1
    return document / denominator



if __name__ == "__main__":
    import sys
    import re
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    PARSER = parser("./creazione vocabolario/vocab_{}.csv".format(n),
                    n, normalized_term_frequency)
    SEP = ","
    for line in sys.stdin:
        index, rate, text = re.match(r"^(\d+)\t(\d+)\t(.+)$", line).groups()
        encoded_text = PARSER([text])[0].tolist()
        sys.stdout.write(index + SEP + rate + SEP + SEP.join(encoded_text) + "\n")
