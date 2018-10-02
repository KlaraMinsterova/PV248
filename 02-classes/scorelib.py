# vysvetlivky
# informace v zavorkach u editoru odstranuju, nesouvisely se jmenem
# taky odstranuju 'continuo' a beru tyto pripady jako dva editory
# u partiture beru jako true vsechno co obsahuje 'yes' nebo jakoukoliv informaci jinou nez 'no'
# pro 'Publication year:' jsem nenasla v zadani zadny odpovidajici atribut, pro zachovani podobnosti ho generuju prazdny


import re


class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

    def __str__(self):
        if self.range is not None:
            if self.name is not None:
                return self.range + ', ' + self.name
            else:
                return self.range
        else:
            return self.name

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

    def __str__(self):
        if self.born is None:
            self.born = ''
        if self.died is None:
            self.died = ''
        return self.name if self.born == '' and self.died == '' else self.name + ' (' + self.born + '--' + self.died + ')'


class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors


class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name


class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        print('Print Number: {0}'.format(self.print_id))
        print('Composer: {0}'.format('; '.join([str(s) for s in self.composition().authors])))
        print('Title: {0}'.format(self.composition().name if self.composition().name is not None else ''))
        print('Genre: {0}'.format(self.composition().genre if self.composition().genre is not None else ''))
        print('Key: {0}'.format(self.composition().key if self.composition().key is not None else ''))
        print('Composition Year: {0}'.format(self.composition().year if self.composition().year is not None else ''))
        print('Publication Year: ')
        print('Edition: {0}'.format(self.edition.name if self.edition.name is not None else ''))
        print('Editor: {0}'.format(', '.join([str(s) for s in self.edition.authors])))
        print('Voice 1: {0}'.format(self.composition().voices[0] if self.composition().voices and self.composition().voices[0] is not None else ''))
        i = 1
        while i < len(self.composition().voices):
            print('Voice {0}: {1}'.format(i + 1, self.composition().voices[i] if self.composition().voices[i] is not None else ''))
            i += 1

        print('Partiture: ' + ('yes' if self.partiture else 'no'))
        print('Incipit: {0}'.format(self.composition().incipit if self.composition().incipit is not None else ''))

    def composition(self):
        return self.edition.composition


def load(filename):
    file = open(filename, encoding = "utf8")
    content = file.read()

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

    printsBefore = content.split('\n\n')
    for printBefore in printsBefore:
        itemsBefore = [rowBefore.split(': ', 1) for rowBefore in printBefore.split('\n')]

        print_id = itemsBefore[0][1].strip() if len(itemsBefore[0]) > 1 else None

        authorsC = []
        if len(itemsBefore[1]) > 1 and itemsBefore[1][1].strip() != '':
            composers = itemsBefore[1][1].split(';')
            for composer in composers:
                name = re.sub(r"\([^a-zA-Z]*\)", "", composer).strip()
                yearBorn = reYearBorn1.match(composer)
                if yearBorn is None:
                    yearBorn = reYearBorn2.match(composer)
                born = None if yearBorn is None else yearBorn.group(1)
                yearDied = reYearDied1.match(composer)
                if yearDied is None:
                    yearDied = reYearDied2.match(composer)
                died = None if yearDied is None else yearDied.group(1)
                composer = Person(name, born, died)
                authorsC.append(composer)

        title = itemsBefore[2][1].strip() if len(itemsBefore[2]) > 1 and itemsBefore[2][1].strip() != '' else None

        genre = itemsBefore[3][1].strip() if len(itemsBefore[3]) > 1 and itemsBefore[3][1].strip() != ''else None

        key = itemsBefore[4][1].strip() if len(itemsBefore[4]) > 1 and itemsBefore[4][1].strip() != '' else None

        yearsComp = reYear.findall(itemsBefore[5][1]) if len(itemsBefore[5]) > 1 else []
        yearComp = yearsComp[0] if len(yearsComp) == 1 else None

        edition = itemsBefore[7][1].strip() if len(itemsBefore[7]) > 1 and itemsBefore[7][1].strip() != '' else None

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
                    if len(m) > 0:
                        for name in m:
                            editor = Person(name, None, None)
                            authorsE.append(editor)
                    else:
                        m = reEditor3.findall(editors)
                        for name in m:
                            editor = Person(name, None, None)
                            authorsE.append(editor)

        voices = []
        i = 9
        count = 0
        while itemsBefore[i + count][0].startswith('V'):
            count += 1
        if count > 0:
            while i < 9 + count:
                if len(itemsBefore[i]) > 1 and itemsBefore[i][1].strip() != '':
                    if '--' not in itemsBefore[i][1]:
                        name = itemsBefore[i][1].strip()
                        range = None
                    else:
                        name = re.sub(reRangeWithSeparator, '', itemsBefore[i][1])
                        name = name.strip() if name.strip() != '' else None
                        range = reRange.match(itemsBefore[i][1]).group(1)
                    voice = Voice(name, range)
                    voices.append(voice)
                else:
                    voices.append(None)
                i += 1

        partiture = len(itemsBefore[i]) > 1 and len(itemsBefore[i][1].strip()) > 2

        i += 1
        incipit = itemsBefore[i][1].strip() if len(itemsBefore[i]) > 1 and itemsBefore[i][1].strip() != '' else None

        composition = Composition(title, incipit, key, genre, yearComp, voices, authorsC)
        edition = Edition(composition, authorsE, edition)
        printNew = Print(edition, print_id, partiture)
        prints.append(printNew)

    return prints
