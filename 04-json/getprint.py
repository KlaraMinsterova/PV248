import sys
import sqlite3
import json

print_id = sys.argv[1]
conn = sqlite3.connect('scorelib.dat')
cur = conn.cursor()

composers = cur.execute("SELECT * FROM person WHERE id IN "
                        "(SELECT composer FROM score_author WHERE score = "
                        "(SELECT id FROM score WHERE id = "
                        "(SELECT score FROM edition WHERE id = "
                        "(SELECT edition FROM print WHERE id = ?))))", (print_id, ))

composersList = []
for row in composers:
    composer = {'name': row[3]}
    if row[1] is not None:
        composer['born'] = row[1]
    if row[2] is not None:
        composer['died'] = row[2]
    composersList.append(composer)

composersJson = json.dumps(composersList, indent=2, ensure_ascii=False)
print(composersJson)
