import os
import ephem
import numpy as np
import sys
from astropy.io import fits
import string
import matplotlib.pyplot as pl
from scipy.optimize import curve_fit


def expArg(x, a, b, c):
    return a * np.exp(b * x) + c


def imlist(dirs, filter_name):
    imglist = []
    for dirname in dirs:
        for fname in os.listdir(dirname):
            if fname.endswith('.fits'):
                # try:
                fname = os.path.join(dirname, fname)
                header = fits.getheader(fname)
                if header['FILTER'] == filter_name and header['EXPTIME'] > 0:
                    imglist.append(fname)
                    # except:
                    #     pass
    return imglist


colors = ['magenta', 'cyan', 'blue', 'green', 'black', 'red', 'darkmagenta', 'darkcyan', 'darkblue', 'darkgreen',
          'gray', 'darkred']

coefficients = dict()

pl.clf()
i_color = 0
for filter_id in sys.argv[-1].split(','):
    for dirname in sys.argv[1:-1]:
        imglist = imlist([dirname], filter_id)
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
            sun = ephem.Sun()
            sun.compute(observatory)
            aux_counts = np.average(image[0].data[1000:9000, 1000:9000])
            if aux_counts < 65000 and image[0].header['IMAGETYP'].startswith(
                    'sky') and sun.alt > -0.17:  # To remove saturated images
                count_median[i] = aux_counts / exptime
                sun_alt[i] = sun.alt
                print observatory.date, sun.alt, sun.az, exptime, sun_alt[i], count_median[i], file
                i += 1
            image.close()

        sun_alt = sun_alt[count_median > 0]
        count_median = count_median[count_median > 0]
        aux_arg = np.argsort(sun_alt)
        sun_alt = sun_alt[aux_arg]
        count_median = count_median[aux_arg]
        print sun_alt
        print count_median

        popt, pcov = curve_fit(expArg, sun_alt, count_median, maxfev=100000000, p0=[2000000, 100, 100])
        print filter_id, popt[0], popt[1], popt[2]
        coefficients[filter_id] = [popt[0], popt[1], popt[2]]
        x = np.linspace(np.min(sun_alt), np.max(sun_alt), 100)
        pl.plot(x * 57.30, expArg(x, popt[0], popt[1], popt[2]), color=colors[i_color])
        pl.plot(sun_alt * 57.30, count_median, 'o', label=filter_id, color=colors[i_color])
        pl.xlabel('Sun altitude (deg)')
        pl.ylabel('counts/sec')

        i_color += 1

pl.legend()
