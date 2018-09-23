import re
from collections import Counter
import sys

file = open(sys.argv[1], encoding = "utf8")

if sys.argv[2] == 'composer':

  reComposer = re.compile(r"Composer: (.*)")
  reC = re.compile(r"Key: (.*)")

  ctrComposer = Counter()

  for line in file:

    m = reComposer.match(line)
    if m is not None:
      composers = m.group(1).split(';')
      for composer in composers:
        composer = re.sub(r"\([^a-zA-Z]*\)", "", composer)
        composer = composer.strip()
        ctrComposer[composer] += 1

  ctrComposer.pop('', None)
  for k, v in ctrComposer.items():
    print('{0}: {1}'.format(k, v))

if sys.argv[2] == 'century':

  reCentury = re.compile(r"Composition Year: (.*)")
  reYear = re.compile(r".*(\d{4}).*")
  reTh = re.compile(r".*(\d{2})th.*")

  ctrCentury = Counter()

  for line in file:

    m = reCentury.match(line) 
    if m is not None:
      year = reYear.match(m.group(1))
      if year is not None:
        century = int(year.group(1)[:2]) + 1 
        ctrCentury[century] += 1
      else:
        th = reTh.match(m.group(1))
        if th is not None:
          century = int(th.group(1))
          ctrCentury[century] += 1

  ctrCentury.pop('', None)
  for k, v in ctrCentury.items():
    print('{0}th century: {1}'.format(k, v))