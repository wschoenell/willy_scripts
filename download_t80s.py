import json
import sys

if len(sys.argv) < 5:
    print('Usage: %s user pass ip file.json')
    sys.exit(1)

addr_format = 'wget -c --no-check-certificate https://%s:%s@%s/{_night}/{FILENAME}' % (sys.argv[1], sys.argv[2], sys.argv[3])

with open(sys.argv[4]) as f:
    links = [addr_format.format(**json.loads(line)) for line in f.readlines()]

for link in links:
    print link
