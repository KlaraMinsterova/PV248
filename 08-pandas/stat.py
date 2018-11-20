import sys
import pandas
import numpy
import json

file = sys.argv[1]
mode = sys.argv[2]

points = pandas.read_csv(file, header=0, index_col=0)
dict = {}

if mode == 'dates':
    points.rename(lambda x: x[:10], axis=1, inplace=True)
    points = points.groupby(axis=1, level=0).sum()

if mode == 'exercises':
    points.rename(lambda x: x[-2:], axis=1, inplace=True)
    points = points.groupby(axis=1, level=0).sum()

for column in points:
    innerDict = {
        'mean': round(points[column].mean(), 2),
        'median': points[column].median(),
        'first': points[column].quantile(0.75),
        'last': points[column].quantile(0.25),
        'passed': numpy.count_nonzero(points[column])}
    dict[column] = innerDict

output = json.dumps(dict, indent=4)
print(output)
