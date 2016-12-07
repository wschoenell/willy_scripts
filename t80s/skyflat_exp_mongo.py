# To run on all filters remotely:
# cd ~/Downloads/; for filter in U G R I Z F395 F410 F515 F378 F430 F660 F861 F660; do ssh mongo@192.168.20.118 python skyflat_exp_mongo.py $filter && scp mongo@192.168.20.118:skyflat_exp.png skyflat_exp_$filter.png && open skyflat_exp_$filter.png; doneqq

import sys
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as pl
import numpy as np
import pymongo
from scipy.optimize import curve_fit
import datetime as dt


def expArg(x, a, b, c):
    return a * np.exp(b * x) + c


colors = ['magenta', 'cyan', 'blue', 'green', 'black', 'red', 'darkmagenta', 'darkcyan', 'darkblue', 'darkgreen',
          'gray', 'darkred']

coefficients = dict()

pl.clf()
i_color = 0
for filter_id in sys.argv[-1].split(','):
    client = pymongo.MongoClient()

    pipe = [
        {'$match': {"$and": [{"avg_counts": {"$gt": 15000}}, {"avg_counts": {"$lt": 45000}}, {'filter': filter_id},
                             {'night': {'$gt': (dt.datetime.today() - dt.timedelta(days=60)).strftime('%Y%m%d')}}
                             ]}},
        # {'$group': {"_id": "$filter", "count": {"$sum": 1}}},
        # {'$sort': {"count": 1}}
    ]

    query = list(client.images.skyflats.aggregate(pipeline=pipe))

    sun_alt = np.zeros(len(query))
    count_median = np.zeros(len(query))

    i = 0
    for img in query:
        if img['sun_alt'] > -.17 and img['sun_alt'] < 0 and img['sun_alt'] < -4 / 57.30:
            count_median[i] = img['median_counts'] / img['exptime']
            sun_alt[i] = img['sun_alt']
            i += 1

    sun_alt = sun_alt[count_median > 0]
    count_median = count_median[count_median > 0]
    aux_arg = np.argsort(sun_alt)
    sun_alt = sun_alt[aux_arg]
    count_median = count_median[aux_arg]
    print sun_alt
    print count_median

    popt, pcov = curve_fit(expArg, sun_alt, count_median, maxfev=100000000, p0=[2000000, 100, 100])
    print "'%s': [%.2f, %.2f, %.2f]" % (filter_id, popt[0], popt[1], popt[2])
    coefficients[filter_id] = [popt[0], popt[1], popt[2]]
    x = np.linspace(np.min(sun_alt), np.max(sun_alt), 100)
    pl.plot(x * 57.30, expArg(x, popt[0], popt[1], popt[2]), color=colors[i_color])
    pl.plot(sun_alt * 57.30, count_median, 'o', label=filter_id, color=colors[i_color])
    pl.xlabel('Sun altitude (deg)')
    pl.ylabel('counts/sec')

    i_color += 1

pl.legend(loc=2)
# pl.show()
pl.savefig('skyflat_exp.png')

# raw_input('Press ENTER to exit')
