#!/usr/bin/python3


import re
import sys
#from langdetect import detect
from pycld2 import detect


SEP = "\t"


#def is_english(text):
#    try:
#        return detect(text) == "en"
#    except:
#        return False

def is_english(text):
    isReliable, textBytesFound, details = detect(text)
    if isReliable and (details[0][0] == 'ENGLISH'):
        return True
    return False

def parse(json_line):
    try:
        overall = re.search(r"\"overall\"\:\s(\d)", json_line).groups()[0]
        overall = int(overall)
        review = re.search(r"\"reviewText\"\:\s\"(.+?)(?<!\\)\"(?=,)",
                           json_line).groups()[0]
        review = "\"" + review + "\""
        product = re.search(r"\"asin\"\:\s\"(\w+)\"", json_line).groups()[0]
        summary = re.search(r"\"summary\"\:\s\"(.+?)(?<!\\)\"(?=,)",
                           json_line).groups()[0]
        summary = "\"" + summary + "\""
    except AttributeError:
        return None
    vote = re.search(r"\"vote\"\:\s\"(\d+)\"", json_line)
    vote = str(int(vote.groups()[0]) + 1) if vote else "1"
    if overall < 1 or overall > 5 or not is_english(review):
        return None
    return str(overall), product, vote, review, summary


if __name__ == "__main__":
    for line in sys.stdin:
        parsed_line = parse(line)
        if parsed_line:
            rate, product, vote, text, summary = parsed_line
            sys.stdout.write(SEP.join([product, vote, rate, text, summary]) + "\n")
