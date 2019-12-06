#!/usr/bin/env python

import sys
import re


for line in sys.stdin:
    n = re.match(r"^(\d+)\t", line).group()
    sys.stdout.write(n + "\n")
