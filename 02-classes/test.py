import sys
import scorelib

printsNew = scorelib.load(sys.argv[1])
i = 0
lastIndex = len(printsNew) - 1
while i < lastIndex:
  printsNew[i].format()
  print()
  i += 1
printsNew[lastIndex].format()
