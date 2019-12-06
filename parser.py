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
            return db.loc[query]["number"] - 1
        return False

    return query_position, list(db.index)


def parse_text(text, ngram_size, method, vocab, N):
    ngrams = nlp.make_ngrams(text, ngram_size)
    out = np.zeros((1, N))
    for ngram in ngrams:
        pos = vocab(ngram)
        if pos:
            out[0, pos] += 1
    out[out == 0] = np.nan
    return method(out)


def parse_list(text_list, *args):
    return np.vstack([parse_text(text, *args) for text in text_list])


def parser(vocab_path, ngram_size, method):
    vocab, vocab_index = read_vocab(vocab_path)
    vocab_size = len(vocab_index)

    def parse_data(index, rate, text):
        nonlocal vocab, vocab_size
        parsed_line = parse_text(text, ngram_size, method, vocab, vocab_size)
        parsed_line = pd.DataFrame(parsed_line, index=[index])
        parsed_line[RATE_STR] = [str(rate) + "stars"]
        return parsed_line

    return parse_data, vocab_index


def term_frequency(document):
    return document / np.nansum(document)

def normalized_term_frequency(document):
    return document / np.nanmax(document)



if __name__ == "__main__":
    import sys
    import re
    VOCAB_FILE = sys.argv[1]
    METHOD = {
        "tf": term_frequency,
        "ntf": normalized_term_frequency
    }
    SEP = ","
    RATE_STR = "<RATE>"
    with open(VOCAB_FILE, "r") as f:
        N = len(f.readline().split("_"))
    PARSER, header = parser(VOCAB_FILE, N, METHOD[sys.argv[2]])
    header += [RATE_STR]
    sys.stdout.write(SEP + SEP.join(header) + "\n")
    for line in sys.stdin:
        parsed_line = re.match(r"^(\d+)\t(\d+)\t(.+)$", line).groups()
        encoded_text = PARSER(*parsed_line)
        encoded_text.to_csv(sys.stdout, sep=SEP, header=False)
