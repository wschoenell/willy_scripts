import os
import ephem
import numpy as np
import sys
from astropy.io import fits
import string
import matplotlib.pyplot as pl
from scipy.stats import mode
from scipy.optimize import curve_fit


def expArg(x, a, b, c):
    return a * np.exp(b * x) + c


def imlist(dir, filter_name):
    imglist = []
    for fname in os.listdir(sys.argv[1]):
        if fname.endswith('.fits'):
            fname = os.path.join(sys.argv[1], fname)
            if fits.getheader(fname)['FILTER'] == filter_name:
                imglist.append(fname)
    return imglist


pl.clf()

for filter_id in sys.argv[2].split(','):
    imglist = imlist(sys.argv[1], filter_id)
    sun_alt = np.zeros(len(imglist))
    count_median = np.zeros(len(imglist))
    i = 0
    for file in imglist:
        image = fits.open(file)
        long = image[0].header['LONGITUD']
        lat = image[0].header['LATITUDE']
        elevation = float(image[0].header['ALTITUDE'])
        date = image[0].header['DATE-OBS']
        date = string.replace(date, '-', '/')
        date = string.replace(date, 'T', ' ')
        date = string.replace(date, '\'', '')
        exptime = image[0].header['EXPTIME']
        observatory = ephem.Observer()
        observatory.long = long
        observatory.lat = lat
        observatory.elevation = elevation
        observatory.date = date
        observatory.date += 4.0 * ephem.hour
        sun = ephem.Sun()
        sun.compute(observatory)
        count_median[i] = np.average(image[0].data[1000:9000, 1000:9000]) / exptime
        # pl.imshow(image[0].data[1000:9000,1000:9000],cmap='gray')
        # pl.colorbar()
        sun_alt[i] = sun.alt
        print observatory.date, sun.alt, sun.az, exptime, sun_alt[i], count_median[i], file
        # print i,x[i],y[i]
        i += 1
        # pl.plot(image[0].data.sum(axis=0))
        # pl.show()
        image.close()

    print sun_alt
    print count_median

    popt, pcov = curve_fit(expArg, sun_alt, count_median, maxfev=1000000) #, p0=[2000000, 68, 17])
    print popt[0], popt[1], popt[2]
    pl.plot(sun_alt, expArg(sun_alt, popt[0], popt[1], popt[2]))

    pl.plot(sun_alt, count_median, label=filter_id)
    pl.xlabel('Sun altitude')
    pl.ylabel('Normalized median counts')

pl.legend()