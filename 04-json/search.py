import sys
import sqlite3
import json

name = sys.argv[1]
conn = sqlite3.connect('scorelib.dat')
cur = conn.cursor()

condition = '%' + name + '%'
cur.execute("SELECT id, name FROM person WHERE name LIKE ? AND id IN (SELECT id FROM score_author)", (condition, ))
authors = cur.fetchall()
result = {}

for author in authors:
    authorsPrintsResult = []

    cur.execute("SELECT print.id, print.partiture, edition.id, edition.name, "
                "score.id, score.name, score.genre, score.key, score.incipit, score.year "
                "FROM print "
                "JOIN edition ON print.edition = edition.id "
                "JOIN score ON edition.score = score.id "
                "JOIN score_author ON score_author.score = score.id "
                "WHERE score_author.composer = ?",
                (author[0], ))
    authorsPrints = cur.fetchall()

    for authorsPrint in authorsPrints:

        voicesResult = {}
        voices = cur.execute("SELECT number, name, range FROM voice WHERE score = ?", (authorsPrint[4], ))
        for row in voices:
            voice = {}
            if row[1] is not None:
                voice['name'] = row[1]
            if row[2] is not None:
                voice['range'] = row[2]
            voicesResult[row[0]] = voice

        composersResult = []
        composers = cur.execute("SELECT person.name, person.born, person.died "
                                "FROM score_author JOIN person ON score_author.composer = person.id "
                                "WHERE score_author.score = ?", (authorsPrint[4], ))
        for row in composers:
            composer = {'name': row[0]}
            if row[1] is not None:
                composer['born'] = row[1]
            if row[2] is not None:
                composer['died'] = row[2]
            composersResult.append(composer)

        editorsResult = []
        editors = cur.execute("SELECT person.name "
                              "FROM edition_author JOIN person ON edition_author.editor = person.id "
                              "WHERE edition_author.edition = ?", (authorsPrint[2], ))
        for row in editors:
            editor = {'name': row[0]}
            editorsResult.append(editor)

        printResult = {'Print Number': authorsPrint[0]}
        if composersResult:
            printResult['Composer'] = composersResult
        if authorsPrint[5] is not None:
            printResult['Title'] = authorsPrint[5]
        if authorsPrint[6] is not None:
            printResult['Genre'] = authorsPrint[6]
        if authorsPrint[7] is not None:
            printResult['Key'] = authorsPrint[7]
        if authorsPrint[9] is not None:
            printResult['Composition Year'] = authorsPrint[9]
        if authorsPrint[3] is not None:
            printResult['Edition'] = authorsPrint[3]
        if editorsResult:
            printResult['Editor'] = editorsResult
        if voicesResult:
            printResult['Voices'] = voicesResult
        if authorsPrint[1] is not None:
            printResult['Partiture'] = True if authorsPrint[1] == 'Y' else False
        if authorsPrint[8] is not None:
            printResult['Incipit'] = authorsPrint[8]

        authorsPrintsResult.append(printResult)

    result[author[1]] = authorsPrintsResult

resultJson = json.dumps(result, indent=4, ensure_ascii=False)
print(resultJson)
