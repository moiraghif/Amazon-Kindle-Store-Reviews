#!/usr/bin/env python

import sys
import re
import tm_preprocessing as nlp


def decode(txt):
    txt = txt[1:-1]
    txt = re.sub(r"\\(?:n|t|r)", " ", txt)
    txt = re.sub(r"\\('|\")", "$1", txt)
    return txt


N = int(sys.argv[1]) if len(sys.argv) > 1 else 3

for row in sys.stdin:
    row_id, row_rate, row_text = re.match(r"(\d+)\t(\d+)\t(.+)$", row).groups()
    for ngram in nlp.make_ngrams(decode(row_text), N):
        sys.stdout.write(ngram + "\n")
