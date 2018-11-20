import sys
import pandas
import numpy
import json
import datetime
from scipy import stats

file = sys.argv[1]
id = sys.argv[2]

points = pandas.read_csv(file, header=0, index_col=0)

# prepare table for mean, median, total and passed
pointsCopy = points.copy()
pointsCopy.rename(lambda x: x[-2:], axis=1, inplace=True)
pointsCopy = pointsCopy.groupby(axis=1, level=0).sum()
pointsCopy.loc['average'] = pointsCopy.mean()

# prepare table for regression
points['2018-09-17'] = 0.0
points.rename(lambda x: datetime.datetime.strptime(x[:10], '%Y-%m-%d').toordinal(), axis=1, inplace=True)
points = points.groupby(axis=1, level=0).sum()
points.sort_index(axis=1, inplace=True)
points = points.cumsum(axis=1)
points.loc['average'] = points.mean()

# calculate regression
slope, intercept, r_value, p_value, std_err = stats.linregress(points.columns.values, points.loc[id])
predict16 = datetime.date.fromordinal(int(((16 - intercept)/slope)//1)).isoformat() if slope > 0 else 'inf'
predict20 = datetime.date.fromordinal(int(((20 - intercept)/slope)//1)).isoformat() if slope > 0 else 'inf'

dict = {
    'mean': round(pointsCopy.loc[id].mean(), 2),
    'median': round(pointsCopy.loc[id].median(), 2),
    'total': round(pointsCopy.loc[id].sum(), 2),
    'passed': numpy.count_nonzero(pointsCopy.loc[id]),
    'regression slope': round(slope, 4),
    'date 16': predict16,
    'date 20': predict20}

output = json.dumps(dict, indent=4)
print(output)
