import sys


n = 0
for line in sys.stdin:
    print(n, line, end="")
    n += 1
