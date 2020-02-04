#!/usr/bin/python


import re
import sys
import spacy
from nltk.stem.snowball import SnowballStemmer


# PREPROCESSING
def extract_ngrams(sent_list, n):
    for i in range(len(sent_list) - (n - 1)):
        yield "_".join(sent_list[i:i+n])


def decode(txt):
    txt = txt[1:-1]
    txt = re.sub(r"\\(?:n|t|r)", " ", txt)
    txt = re.sub(r"\\(\'|\")", "$1", txt)
    return txt


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
    text = re.sub(r"\bcannot\b", "can not", text)  # cannot -> can not
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
    text = re.sub(r"pgs\b", "pages", text)  # pgs -> pages
    text = re.sub(r"(\d+)\s?yo\b", r"\1 year old", text)  # 15yo -> 15 year old
    text = re.sub(r"(\d+)\s?yrs?\b", r"\1 year", text)  # 5yr -> 5 year
    text = re.sub(r"\bmin\b", "minute", text)  # min -> minute
    text = re.sub(r"(\d+)min\b", r"\1 minute", text)  # 10min -> 10 minute
    text = re.sub(r"\bhrs?\b", "hour", text)  # hrs -> hour
    text = re.sub(r"(\d+)hrs?\b", r"\1 hour", text)  # 10hrs -> 10 hour
    text = re.sub(r"\b(?:19)?([0-9]0)s\b", "\1 years", text)  # 1950s -> 50 years
    text = re.sub(r"\b(\d+)(\w+)\b", r"\1 \2", text)  # 15fold -> 15 fold
    text = re.sub(r"\d", "", text)  # remove numbers
    return text.strip()


def clean(word):
    word = re.sub(r"(.)\1{2,}", r"\1\1", word)  # goooooood -> good
    word = re.sub(r"\'(?:d|m|re|ve|s|ll)", "", word)  # remove contractions
    word = re.sub(r"[\W\_]", "", word)  # remove punctuation
    word = re.sub(r"\bdid\b", "do", word)  # did -> do
    word = re.sub(r"\bcould\b", "can", word)  # could -> can
    word = re.sub(r"\b(?:would|should)\b", "will", word)  # would/should -> will
    word = re.sub(r"\bmight\b", "may", word)  # might -> may
    return word if (len(word) > 1 and word not in STOPWORDS) else ""


def make_ngrams(nlp, text, n=1):
    text = decode(text)
    text = clean_sentence(text)
    for sentence in nlp(text).sents:
        sent_tokens = []
        for token in sentence:
            if token.is_currency:
                sent_tokens.append("money")
            elif not token.is_digit:
                token_str = clean(token.text.strip().lower())
                if token_str:
                    token_str = STEMMER.stem(token_str)
                    sent_tokens.append(token_str)
        for ngram in extract_ngrams(sent_tokens, n):
            yield ngram


with open("./spacy_model/english_stopwords", "r") as stopwords_file:
    STOPWORDS = {w.lower().strip() for w in stopwords_file.readlines()}

# custom stopwords
# amazon slang
STOPWORDS |= {"amazon", "kindle", "product", "products", "item"}
# books slang
STOPWORDS |= {"author", "authors", "book", "books", "page", "pages", "read",
              "review", "reviews", "write", "written"}
# remove some stopwords that are meaningfull
STOPWORDS -= {"few", "further", "over", "again", "no", "nor",
              "not", "only", "very"}

STEMMER = SnowballStemmer("english")

SEP = "\t"


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "create_model":
        NLP = spacy.load("en_core_web_sm")
        NLP.add_pipe(NLP.create_pipe('sentencizer'))
        NLP.remove_pipe("ner")
        NLP.remove_pipe("parser")
        NLP.remove_pipe("tagger")
        NLP.to_disk("./spacy_model")
        print("Model created")

    else:
        NLP = spacy.load("./spacy_model")
        for line in sys.stdin:
            prev, text, summary = re.match(r"^(\w+\t\d+\t\d\t)(.+)\t(.+)", line).groups()
            sys.stdout.write(prev)            
            sys.stdout.write(text+"\t")
            for ngram in make_ngrams(NLP, text):
                sys.stdout.write(ngram + " ")
            sys.stdout.write("\t" + summary)
            sys.stdout.write("\n")
