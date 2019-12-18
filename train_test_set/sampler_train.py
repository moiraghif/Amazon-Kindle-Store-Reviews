#!/home/fede/.anaconda/bin/python


import sys
import re


LIM = 2e4
SEP = "\t"


def parse(line):
    return re.match(r"^(\d+)\t(\w+)\t(\d)\t(.+)", line).groups()


def get_rates(lim):
    rates = [0 for _ in range(5)]
    completed = [False for _ in range(5)]

    def add_one(n, product, rate, text):
        nonlocal rates, completed
        if all(completed):
            return True
        rate = int(rate)
        if completed[rate - 1] or rates[rate - 1] == lim:
            completed[rate - 1] = True
        else:
            sys.stdout.write(SEP.join([n, product, str(rate), text]) + "\n")
            rates[rate - 1] += 1
        return False

    return add_one


SAMPLER = get_rates(LIM)

if __name__ == "__main__":
    for line in sys.stdin:
        n, product, rate, text = parse(line)
        if SAMPLER(n, product, rate, text):
            break
