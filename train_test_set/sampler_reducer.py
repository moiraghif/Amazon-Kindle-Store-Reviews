import sys
import json
import re
from langdetect import detect


LIM = 1e4
SEP = "\t"


def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False


def parse(line):
    n, json_line = re.findall(r"^(\d+)\s(.+)$", line)[0]
    parsed_line = json.loads(json_line)
    if "overall" not in parsed_line.keys() or \
       "reviewText" not in parsed_line.keys() or \
       not is_english(parsed_line["reviewText"]):
        return None
    rate = int(re.match(r"^\d", str(parsed_line["overall"])).group()[0])
    if rate < 1 or rate > 5:
        return None
    return n, rate, repr(parsed_line["reviewText"].strip())


def get_rates(lim):
    rates = [0 for _ in range(5)]
    completed = [False for _ in range(5)]

    def add_one(n, rate, text):
        nonlocal rates, completed
        rate -= 1
        if all(completed):
            return True
        if completed[rate] or rates[rate] == lim:
            completed[rate] = True
            return False
        else:
            rates[rate] += 1
            sys.stdout.write(str(n) + SEP + str(rate + 1) + SEP + text + "\n")
            return False

    return add_one


early_stopping = get_rates(LIM)

for line in sys.stdin:
    parsed_line = parse(line)
    if parsed_line is not None:
        if early_stopping(*parsed_line):
            break
