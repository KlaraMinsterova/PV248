import sys
import sqlite3
import json

name = sys.argv[1]
conn = sqlite3.connect('scorelib.dat')
cur = conn.cursor()

condition = '%' + name + '%'
cur.execute("SELECT id, name FROM person WHERE name LIKE ? AND id IN (SELECT id FROM score_author)", (condition, ))
authors = cur.fetchall()
authorsList = []

for author in authors:
    authorsPrintsList = []

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

        voicesList = {}
        voices = cur.execute("SELECT number, name, range FROM voice WHERE score = ?", (authorsPrint[4], ))
        for voice in voices:
            voiceJson = {}
            if voice[1] is not None:
                voiceJson['name'] = voice[1]
            if voice[2] is not None:
                voiceJson['range'] = voice[2]
            voicesList[voice[0]] = voiceJson

        composersList = []
        composers = cur.execute("SELECT person.name, person.born, person.died "
                                "FROM score_author JOIN person ON score_author.composer = person.id "
                                "WHERE score_author.score = ?", (authorsPrint[4], ))
        for composer in composers:
            composerJson = {'name': composer[0]}
            if composer[1] is not None:
                composerJson['born'] = composer[1]
            if composer[2] is not None:
                composerJson['died'] = composer[2]
            composersList.append(composerJson)

        editorsList = []
        editors = cur.execute("SELECT person.name "
                                "FROM edition_author JOIN person ON edition_author.editor = person.id "
                                "WHERE edition_author.edition = ?", (authorsPrint[2], ))
        for editor in editors:
            editorJson = {'name': editor[0]}
            editorsList.append(editorJson)

        printJson = {'Print Number': authorsPrint[0]}
        if composersList:
            printJson['Composer'] = composersList
        if authorsPrint[5] is not None:
            printJson['Title'] = authorsPrint[5]
        if authorsPrint[6] is not None:
            printJson['Genre'] = authorsPrint[6]
        if authorsPrint[7] is not None:
            printJson['Key'] = authorsPrint[7]
        if authorsPrint[9] is not None:
            printJson['Composition Year'] = authorsPrint[9]
        if authorsPrint[3] is not None:
            printJson['Edition'] = authorsPrint[3]
        if editorsList:
            printJson['Editor'] = editorsList
        if voicesList:
            printJson['Voices'] = voicesList
        if authorsPrint[1] is not None:
            printJson['Partiture'] = authorsPrint[1]
        if authorsPrint[8] is not None:
            printJson['Incipit'] = authorsPrint[8]

        authorsPrintsList.append(printJson)

    authorJson = {author[1]: authorsPrintsList}
    authorsList.append(authorJson)

resultJson = json.dumps(authorsList, indent=4, ensure_ascii=False)
print(resultJson)
