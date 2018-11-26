import sys
import pandas
import numpy
import json
import datetime
from scipy import stats

file = sys.argv[1]
id = sys.argv[2]
if id != 'average':
    id = int(id)

points = pandas.read_csv(file, header=0, index_col=0)

# prepare table for mean, median, total and passed
pointsCopy = points.copy()
pointsCopy.rename(lambda x: x[-2:], axis=1, inplace=True)
pointsCopy = pointsCopy.groupby(axis=1, level=0).sum()
pointsCopy.loc['average'] = pointsCopy.mean()

# prepare table for regression
startDate = datetime.datetime.strptime('2018-09-17', '%Y-%m-%d').toordinal()
points['2018-09-17'] = 0.0
points.rename(lambda x: datetime.datetime.strptime(x[:10], '%Y-%m-%d').toordinal() - startDate, axis=1, inplace=True)
points = points.groupby(axis=1, level=0).sum()
points.sort_index(axis=1, inplace=True)
points = points.cumsum(axis=1)
points.loc['average'] = points.mean()

# calculate regression
x = numpy.array(points.columns.values).reshape(-1, 1)
y = numpy.array(points.loc[id])
slope = numpy.linalg.lstsq(x, y, rcond=None)[0][0]

predict16 = datetime.date.fromordinal(int((16/slope)//1) + startDate).isoformat() if slope > 0 else 'inf'
predict20 = datetime.date.fromordinal(int((20/slope)//1) + startDate).isoformat() if slope > 0 else 'inf'

dict = {
    'mean': pointsCopy.loc[id].mean(),
    'median': pointsCopy.loc[id].median(),
    'total': pointsCopy.loc[id].sum(),
    'passed': numpy.count_nonzero(pointsCopy.loc[id]),
    'regression slope': slope,
    'date 16': predict16,
    'date 20': predict20}

output = json.dumps(dict, indent=4)
print(output)
