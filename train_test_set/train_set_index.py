#!/usr/bin/env python

import re
import sys


def get_index(line):
    return re.match(r"^(\d+)", line).groups()[0]


if __name__ == "__main__":
    for line in sys.stdin:
        number = get_index(line)
        sys.stdout.write(number + "\n")
