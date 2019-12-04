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


def all_numbers(txt):
    return not bool(re.sub("\d+", "", txt))


def clean_sentence(text):
    text = re.sub(r"\s+", " ", text)  # "     " -> " "
    text = re.sub(r"\.{3,}", "...", text)  # ...... -> ...
    text = re.sub(r"\bim\b", "I'm", text)  # im -> I'm
    text = re.sub(r"\bdont\b", "don't", text)  # dont -> don't
    text = re.sub(r"\bdidnt\b", "didn't", text)  # didnt -> didn't
    text = re.sub(r"\bgive\sup\b", "giveup", text)  # give up -> giveup
    text = re.sub(r"\b(have|has)\sto\b", "must", text)  # have/has to -> must
    text  =re.sub(r"\b(is|are)\sgoing\sto\b", "will", text)  # is/are going to -> will
    #     because they are both stopwords but toghether they have a strong meaning
    text = re.sub(r"\$\d+\s*(?:\.\d+)", "money", text)  # $0.99 -> money
    text = re.sub(r"\d+\s*(?:\.\d+)\$", "money", text)  # 0.99$ -> money
    text = re.sub(r"\Bn\'t\b", " not", text)  # SOMETHINGn't -> SOMETHING not
    return text


def clean(word):
    # remove ' and " if delimiters of all text
    # word = re.sub(r"(?<=^)(?:'|\")", "", word)
    # word = re.sub(r"(?:'|\")(?=$)", "", word)
    word = re.sub(r"(?:'d|'m|'re|'ve'|'s|'ll)", "", word)  # remove contractions
    word = re.sub(r"\W", "", word)  # remove punctuation
    word = re.sub(r"n't", "not", word)  # n't -> not
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
    out = []
    if is_english(sentence):
        sentence = clean_sentence(sentence.lower())
        for s in SENT_TOKENIZER.tokenize(sentence):
            tokens = tokenize(s)
            out += list(ngrams(tokens, n))
    return map(lambda ngram: "_".join(ngram), out)


try:
    STOPWORDS = {w.lower() for w in stopwords.words("english")}
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = {w.lower() for w in stopwords.words("english")}

STOPWORDS |= {"also", "could", "would"}
STOPWORDS |= {"page", "pages", "read", "review", "reviews", "write", "written"}
STOPWORDS -= {"few", "further", "over", "again", "no", "nor",
              "not", "only", "very"}

TOKENIZER = TreebankWordTokenizer()

try:
    SENT_TOKENIZER = nltk.data.load("tokenizers/punkt/english.pickle")
except LookupError:
    nltk.download("punkt")
    SENT_TOKENIZER = nltk.data.load("tokenizers/punkt/english.pickle")

STEMMER = PorterStemmer()
