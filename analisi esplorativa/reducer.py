import sys


prev = ""
n = 0
for line in sys.stdin:
    if line == prev:
        n += 1
    else:
        if prev:
            sys.stdout.write(prev.replace("\n", "\t") + str(n) + "\n")
        prev = line
        n = 1
sys.stdout.write(prev.replace("\n", "\t") + str(n) + "\n")
