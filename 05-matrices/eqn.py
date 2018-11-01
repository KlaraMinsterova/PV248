import numpy
import sys
import re
from copy import deepcopy

file = open(sys.argv[1], encoding="utf8")

reCoefAndVar = re.compile(r'[^a-z]*[a-z]')

leftSides = []
leftSidesDicts = []
rightSides = []

for line in file:
    sides = line.split('=')
    rightSides.append(int(sides[1].strip()))

    dict = {}
    for coefAndVar in re.findall(reCoefAndVar, sides[0]):
        coefAndVar = re.sub(' ', '', coefAndVar)
        coefficient = coefAndVar[:-1]
        variable = coefAndVar[-1:]
        if coefficient == '' or coefficient == '+' or coefficient == '-':
            coefficient += '1'
        dict[variable] = coefficient

    leftSidesDicts.append(dict)
    leftSides.append([])

variables = []
for dict in leftSidesDicts:
    for key in dict:
        if key not in variables:
            variables.append(key)

variables.sort()
for variable in variables:
    i = 0
    for dict in leftSidesDicts:
        coefficient = int(dict.get(variable, 0))
        leftSides[i].append(coefficient)
        i += 1

augmentedMatrix = deepcopy(leftSides)
i = 0
for constant in rightSides:
    augmentedMatrix[i].append(constant)
    i += 1

coefficientMatrixRank = numpy.linalg.matrix_rank(leftSides)
augmentedMatrixRank = numpy.linalg.matrix_rank(augmentedMatrix)

if coefficientMatrixRank != augmentedMatrixRank:
    print('no solution')

elif coefficientMatrixRank < len(variables):
    homogeneous = True
    for constant in rightSides:
        if constant != 0:
            homogeneous = False
    space = len(variables) - coefficientMatrixRank if homogeneous else len(variables) - len(leftSides)
    print('solution space dimension: {0}'.format(space))

else:
    result = numpy.linalg.solve(leftSides, rightSides)
    outputParts = []
    i = 0
    for variable in variables:
        outputParts.append(variable + ' = ' + str(result[i]))
        i += 1
    print('solution: {0}'.format(', '.join([str(s) for s in outputParts])))
