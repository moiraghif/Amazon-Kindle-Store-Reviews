#!/home/fede/.anaconda/bin/python


import re
import sys
from langdetect import detect


SEP = "\t"


def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False


def parse(json_line):
    try:
        overall = re.search(r"\"overall\"\:\s(\d)", json_line).groups()[0]
        overall = int(overall)
        review = re.search(r"\"reviewText\"\:\s\"(.+?)(?<!\\)\"(?=,)",
                           json_line).groups()[0]
        review = "\"" + review + "\""
        product = re.search(r"\"asin\"\:\s\"(\w+)\"", json_line).groups()[0]
    except AttributeError:
        return None
    if overall < 1 or overall > 5 or not is_english(review):
        return None
    return str(overall), product, review


if __name__ == "__main__":
    for line in sys.stdin:
        parsed_line = parse(line)
        if parsed_line:
            rate, product, text = parsed_line
            sys.stdout.write(SEP.join([product, rate, text]) + "\n")
