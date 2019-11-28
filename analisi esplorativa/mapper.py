import sys
import json


def mapper(line):
    json_line = json.loads(line)
    try:
        return str(json_line["overall"])
    except KeyError:
        return None


for line in sys.stdin:
    line_parsed = mapper(line)
    if line_parsed is not None:
        sys.stdout.write(line_parsed + "\n")
