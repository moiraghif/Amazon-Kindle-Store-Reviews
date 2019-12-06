#!/usr/bin/env python


import re
import nltk.data
from langdetect import detect
from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk import ngrams


def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False


def decode(txt):
    txt = txt[1:-1]
    txt = re.sub(r"\\(?:n|t|r)", " ", txt)
    txt = re.sub(r"\\(\'|\")", "$1", txt)
    return txt


def all_numbers(txt):
    return not bool(re.sub(r"\d+", "", txt))


def clean_sentence(text):
    text = re.sub(r"\<.+?\>", "", text)  # removes HTML tags
    text = re.sub(r"\s+", " ", text)  # "     " -> " "
    text = re.sub(r"\.{3,}", "...", text)  # ...... -> ...
    text = re.sub(r"\bim\b", "I'm", text)  # im -> I'm
    text = re.sub(r"\bdont\b", "don't", text)  # dont -> don't
    text = re.sub(r"\bdidnt\b", "didn't", text)  # didnt -> didn't
    text = re.sub(r"\bgive\sup\b", "giveup", text)  # give up -> giveup
    #     because they are both stopwords but toghether they have a strong meaning
    text = re.sub(r"\b(have|has)\sto\b", "must", text)  # have/has to -> must
    text = re.sub(r"\b(is|are)\sgoing\sto\b", "will", text)  # is/are going to -> will
    text = re.sub(r"\bwon\'?t\b", "will not", text)  # wont -> will not
    text = re.sub(r"\be(books?)\b", "$1", text)  # ebook(s) -> book(s)
    # a lot of amazon products...
    text = re.sub(r"\bamazon\s(?:prime|video|music|books)\b",
                  "amazon", text)  # jsut amazon sub-sites
    text = re.sub(r"\bkindle\s(?:edition|touch|paperwhite|paper\swhite|file|fire\shd|fire|format|unlimited|version|store)\b",
                  "kindle", text)  # yeah, KINDLE slang is very rich!
    text = re.sub(r"(?:\$|\€|\£)\s*\d+(?:\.\d+)", "money", text)  # $0.99 -> money
    text = re.sub(r"\d+(?:\.\d+)\s*(?:\$|\€|\£)", "money", text)  # 0.99$ -> money
    text = re.sub(r"\b1\s?st\b", "first", text)   # 1st -> first
    text = re.sub(r"\b2\s?nd\b", "second", text)  # 2nd -> second
    text = re.sub(r"\b3\s?rd\b", "third", text)   # 3rd -> third
    text = re.sub(r"\b\d+\s?th\b", "", text)      # other ordinals are just erased
    text = re.sub(r"\Bn\'t\b", " not", text)  # SOMETHINGn't -> SOMETHING not
    return text


def clean(word):
    word = re.sub(r"\'(?:d|m|re|ve|s|ll)", "", word)  # remove contractions
    word = re.sub(r"[\W\_]", "", word)  # remove punctuation
    word = re.sub(r"\bdid\b", "do", word)  # did -> do
    word = re.sub(r"\bcould\b", "can", word)  # could -> can
    word = re.sub(r"\bwould\b", "will", word)  # would -> will
    word = re.sub(r"\bmight\b", "may", word)  # might -> may
    if not word or \
       word in STOPWORDS or \
       all_numbers(word):
        return ""
    return stemmer(word)


def stemmer(text):
    return STEMMER.stem(text)


def tokenize(text):
    out = list()
    for token in TOKENIZER.tokenize(text):
        clean_token = clean(token)
        if clean_token:
            out.append(clean_token)
    return out


def make_ngrams(sentence, n=1):
    sentence = decode(sentence)
    if is_english(sentence):
        sentence = clean_sentence(sentence.lower())
        for s in SENT_TOKENIZER.tokenize(sentence):
            tokens = tokenize(s)
            for ngram in ngrams(tokens, n):
                yield "_".join(ngram)


# standard stopwords
try:
    STOPWORDS = {w.lower() for w in stopwords.words("english")}
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = {w.lower() for w in stopwords.words("english")}

# custom stopwords
# amazon slang
STOPWORDS |= {"amazon", "kindle", "product", "products", "item"}
# books slang
STOPWORDS |= {"author", "authors", "book", "books", "page", "pages", "read",
              "review", "reviews", "write", "written"}
# remove some stopwords that are meaningfull
STOPWORDS -= {"few", "further", "over", "again", "no", "nor",
              "not", "only", "very"}

TOKENIZER = TreebankWordTokenizer()

try:
    SENT_TOKENIZER = nltk.data.load("tokenizers/punkt/english.pickle")
except LookupError:
    nltk.download("punkt")
    SENT_TOKENIZER = nltk.data.load("tokenizers/punkt/english.pickle")

STEMMER = PorterStemmer()
