#!/home/fede/.anaconda/bin/python


import re
import sys
import spacy
import pandas as pd
import numpy as np
from nltk.stem.snowball import SnowballStemmer


### PREPROCESSING
def ngrams(sent_list, n):
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
        for ngram in ngrams(sent_tokens, n):
            yield ngram


with open("english_stopwords", "r") as stopwords_file:
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



### PARSING
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
    ngrams = make_ngrams(NLP, text, ngram_size)
    out = np.zeros((1, N))
    for ngram in ngrams:
        pos = vocab(ngram)
        if pos:
            out[0, pos] += 1
    out[out == 0] = np.nan
    return method(out)


def parse_list(text_list, *args):
    return np.vstack([parse_text(text, *args) for text in text_list])


def parser(method, vocab_path, ngram_size):
    method_fn = {
        "tf": term_frequency,
        "ntf": normalized_term_frequency,
        "roberta": roberta_encoder
    }
    if method != "roberta":
        vocab, vocab_index = read_vocab(vocab_path)
        vocab_size = len(vocab_index)
    else:
        vocab, vocab_index, vocab_size = None, None, None
    encoder = method_fn[method]

    def parse_data(index, rate, text):
        nonlocal vocab, vocab_size, encoder
        parsed_line = encoder(text) if method == "roberta" \
            else  parse_text(text, ngram_size,
                             encoder,
                             vocab, vocab_size)
        parsed_line = pd.DataFrame(parsed_line, index=[index])
        parsed_line[RATE_STR] = [str(rate) + "stars"]
        return parsed_line

    return parse_data


def term_frequency(document):
    return document / np.nansum(document)

def normalized_term_frequency(document):
    return document / np.nanmax(document)

def roberta_encoder(document):
    return np.expand_dims(NLP(document).vector, 0)


RATE_STR = "<RATE>"
SEP = ","


if __name__ == "__main__":
    status = sys.argv[1]
    
    if status == "create_model":  # (no args)
        NLP = spacy.load("en_core_web_sm")
        NLP.add_pipe(NLP.create_pipe('sentencizer'))
        NLP.remove_pipe("ner")
        NLP.remove_pipe("parser")
        NLP.remove_pipe("tagger")
        NLP.to_disk("./spacy_models/my-model")
        ROBERTA = spacy.load("en_trf_robertabase_lg")
        ROBERTA.to_disk("./spacy_models/roberta")
        print("Model created")
        
    elif status == "extract_ngrams":  # ngram_size
        N = int(sys.argv[2])
        NLP = spacy.load("./spacy_models/my-model")
        for line in sys.stdin:
            text = re.match(r"^\d+\t\w+\t\d\t(.+)", line).groups()[0]
            for ngram in make_ngrams(NLP, text, N):
                sys.stdout.write(ngram + "\n")

    elif status == "encode":  # method, vocab
        METHOD = sys.argv[2]
        if METHOD == "roberta":
            NLP, VOCAB_FILE, N = spacy.load("./spacy_models/roberta"), "", 0
        else:
            NLP, VOCAB_FILE = spacy.load("./spacy_models/my-model"), sys.argv[3]
            with open(VOCAB_FILE, "r") as f:
                N = len(f.readline().split("_"))
        PARSER = parser(METHOD, VOCAB_FILE, N)
        for line in sys.stdin:
            parsed_line = re.match(r"^(\d+)\t\w+\t(\d+)\t(.+)$", line).groups()
            encoded_text = PARSER(*parsed_line)
            encoded_text.to_csv(sys.stdout, sep=SEP, header=False)
        
    else:
        print("Command not recognized")
