import re
import sys
import sqlite3


class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range


class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died
        self.save()

    def save(self):
        cur.execute("SELECT id FROM person WHERE name = ?", (self.name,))
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO person (born, died, name) VALUES (?, ?, ?)", (self.born, self.died, self.name))
            self.id = cur.lastrowid
        else:
            if self.born is not None:
                cur.execute("UPDATE person SET born = ? WHERE id = ?", (self.born, row[0]))
            if self.died is not None:
                cur.execute("UPDATE person SET died = ? WHERE id = ?", (self.died, row[0]))
            self.id = row[0]


class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors
        self.save()

    def save(self):
        self.id = None
        cmd = "SELECT id FROM score WHERE "
        cmd = cmd + "name = ? " if self.name is not None else cmd + "name IS ? "
        cmd = cmd + "AND genre = ? " if self.genre is not None else cmd + "AND genre IS ? "
        cmd = cmd + "AND incipit = ? " if self.incipit is not None else cmd + "AND incipit IS ? "
        cmd = cmd + "AND key = ? " if self.key is not None else cmd + "AND key IS ? "
        cmd = cmd + "AND year = ?" if self.year is not None else cmd + "AND year IS ?"
        cur.execute(cmd, (self.name, self.genre, self.incipit, self.key, self.year))
        scores = cur.fetchall()

        if scores:
            same = True
            for score in scores:
                cur.execute("SELECT composer FROM score_author WHERE score = ?", (score[0],))
                composers = cur.fetchall()
                if len(composers) != len(self.authors):
                    same = False
                else:
                    i = 0
                    while i < len(composers):
                        if composers[i][0] != self.authors[i].id:
                            same = False
                        i += 1
                cur.execute("SELECT range, name FROM voice WHERE score = ?", (score[0],))
                voices = cur.fetchall()
                if len(voices) != len(self.voices):
                    same = False
                else:
                    i = 0
                    while i < len(voices):
                        if voices[i][0] != self.voices[i].range or voices[i][1] != self.voices[i].name:
                            same = False
                        i += 1
                if same:
                    self.id = score[0]
                    break

        if self.id is None:
            cur.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)", (self.name, self.genre, self.key, self.incipit, self.year))
            self.id = cur.lastrowid

            number = 1
            for scoreVoice in self.voices:
                cur.execute("INSERT INTO voice (number, score, range, name) VALUES (?, ?, ?, ?)", (number, self.id, scoreVoice.range, scoreVoice.name))
                number += 1

            for scoreAuthor in self.authors:
                cur.execute("INSERT INTO score_author (score, composer) VALUES (?, ?)", (self.id, scoreAuthor.id))


class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name
        self.save()

    def save(self):
        self.id = None
        cmd = "SELECT id FROM edition WHERE score = ? AND "
        cmd = cmd + "name = ?" if self.name is not None else cmd + "name IS ?"
        cur.execute(cmd, (self.composition.id, self.name))
        editions = cur.fetchall()

        if editions:
            same = True
            for edition in editions:
                cur.execute("SELECT editor FROM edition_author WHERE edition = ?", (edition[0],))
                editors = cur.fetchall()
                if len(editors) != len(self.authors):
                    same = False
                else:
                    i = 0
                    while i < len(editors):
                        if editors[i][0] != self.authors[i].id:
                            same = False
                        i += 1
                if same:
                    self.id = edition[0]
                    break

        if self.id is None:
            cur.execute("INSERT INTO edition (score, name, year) VALUES (?, ?, ?)", (self.composition.id, self.name, None))
            self.id = cur.lastrowid

            for editionAuthor in self.authors:
                cur.execute("INSERT INTO edition_author (edition, editor) VALUES (?, ?)", (self.id, editionAuthor.id))


class Print:
    def __init__(self, edition, print_id, partiture, partitureDetail):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture
        self.partitureDetail = partitureDetail
        self.save()

    def composition(self):
        return self.edition.composition

    def save(self):
        cur.execute("INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)", (self.print_id, self.partitureDetail, self.edition.id))


conn = sqlite3.connect(sys.argv[2])
cur = conn.cursor()
script = open('scorelib.sql', encoding='utf8').read()
cur.executescript(script)
file = open(sys.argv[1], encoding="utf8")
content = file.read()
content = re.sub('\n\n\n', '\n\n', content)
printsBefore = content.split('\n\n')

prints = []
reYearBorn1 = re.compile(r".*(\d{4})-.*")
reYearBorn2 = re.compile(r".*\*(\d{4}).*")
reYearDied1 = re.compile(r".*-(\d{4}).*")
reYearDied2 = re.compile(r".*\+(\d{4}).*")
reYear = re.compile(r"(\d{4})")
reEditor1 = re.compile(r"^([^ ,]+, [^ ,]+)$")
reEditor2 = re.compile(r"([^ ,]+ [^ ,]+[^,]*)")
reEditor3 = re.compile(r"([^ ,]+, [^ ,]+)")
reRangeWithSeparator = re.compile(r"([^ ]*--[^ ]*)")
reRange = re.compile(r"([^ ,;]*--[^ ,;]*)")

for printBefore in printsBefore:
    itemsBefore = [rowBefore.split(': ', 1) for rowBefore in printBefore.split('\n')]

    print_id = int(itemsBefore[0][1].strip()) if len(itemsBefore[0]) > 1 else None

    authorsC = []
    if len(itemsBefore[1]) > 1 and itemsBefore[1][1].strip() != '':
        composers = itemsBefore[1][1].split(';')
        for composer in composers:
            name = re.sub(r"\([^a-zA-Z]*\)", "", composer).strip()
            yearBorn = reYearBorn1.match(composer)
            if yearBorn is None:
                yearBorn = reYearBorn2.match(composer)
            born = None if yearBorn is None else int(yearBorn.group(1))
            yearDied = reYearDied1.match(composer)
            if yearDied is None:
                yearDied = reYearDied2.match(composer)
            died = None if yearDied is None else int(yearDied.group(1))
            composer = Person(name, born, died)
            composer.save()
            authorsC.append(composer)

    title = itemsBefore[2][1].strip() if len(itemsBefore[2]) > 1 and itemsBefore[2][1].strip() != '' else None

    genre = itemsBefore[3][1].strip() if len(itemsBefore[3]) > 1 and itemsBefore[3][1].strip() != ''else None

    key = itemsBefore[4][1].strip() if len(itemsBefore[4]) > 1 and itemsBefore[4][1].strip() != '' else None

    yearsComp = reYear.findall(itemsBefore[5][1]) if len(itemsBefore[5]) > 1 else []
    yearComp = yearsComp[0] if len(yearsComp) == 1 else None

    editionName = itemsBefore[7][1].strip() if len(itemsBefore[7]) > 1 and itemsBefore[7][1].strip() != '' else None

    authorsE = []
    if len(itemsBefore[8]) > 1 and itemsBefore[8][1].strip() != '':
        editors = itemsBefore[8][1].strip()
        editors = re.sub(r"\(.*\)", "", editors).strip()
        editors = re.sub(r"continuo: ", "", editors).strip()
        editors = re.sub(r"continuo by ", "", editors).strip()
        if ',' not in editors:
            name = editors
            editor = Person(name, None, None)
            authorsE.append(editor)
        else:
            m = reEditor1.match(editors)
            if m is not None:
                name = m.group(1)
                editor = Person(name, None, None)
                authorsE.append(editor)
            else:
                m = reEditor2.findall(editors)
                if len(m) == 0:
                    m = reEditor3.findall(editors)
                for name in m:
                    editor = Person(name, None, None)
                    authorsE.append(editor)

    voices = []
    i = 9
    count = 0
    while itemsBefore[i + count][0].startswith('V'):
        count += 1
    if count > 1 or (count == 1 and len(itemsBefore[i]) > 1 and itemsBefore[i][1].strip() != ''):
        while i < 9 + count:
            name = None
            voiceRange = None
            if len(itemsBefore[i]) > 1 and itemsBefore[i][1].strip() != '':
                if '--' not in itemsBefore[i][1]:
                    name = itemsBefore[i][1].strip()
                else:
                    name = re.sub(reRangeWithSeparator, '', itemsBefore[i][1])
                    name = name.strip() if name.strip() != '' else None
                    voiceRange = reRange.match(itemsBefore[i][1]).group(1)
            voice = Voice(name, voiceRange)
            voices.append(voice)
            i += 1
    else:
        i += 1

    partiture = len(itemsBefore[i]) > 1 and len(itemsBefore[i][1].strip()) > 2
    if partiture:
        if re.match(r".*partial.*", itemsBefore[i][1]) is not None or re.match(r".*incomplete.*", itemsBefore[i][1]) is not None:
            partitureDetail = 'P'
        else:
            partitureDetail = 'Y'
    else:
        partitureDetail = 'N'

    i += 1
    incipit = itemsBefore[i][1].strip() if len(itemsBefore[i]) > 1 and itemsBefore[i][1].strip() != '' else None

    composition = Composition(title, incipit, key, genre, yearComp, voices, authorsC)
    edition = Edition(composition, authorsE, editionName)
    printNew = Print(edition, print_id, partiture, partitureDetail)
    prints.append(printNew)

conn.commit()
