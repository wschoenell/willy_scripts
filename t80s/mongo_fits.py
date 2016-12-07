import os
import re
import string
import sys
import astropy
import datetime

import ephem
import pymongo
from astropy.io import fits
import numpy as np
from pymongo.errors import DuplicateKeyError

client = pymongo.MongoClient()

if len(sys.argv) == 2:
    image_dir = sys.argv[1]
else:
    localtime = datetime.datetime.now()

    if localtime.hour < 12:
        jd_day = localtime - datetime.timedelta(days=1)
    else:
        jd_day = localtime #- datetime.timedelta(days=0)

    # image_dir = '/mnt/smaps/t80s/%s' % jd_day.strftime("%Y%m%d")
    image_dir = '/mnt/images/%s' % jd_day.strftime("%Y%m%d")
    print 'image_dir = ', image_dir

if not 'fits_keywords' in client.images.collection_names():
    client.images.create_collection('fits_keywords')

if not 'FILENAME_1' in client.images.fits_keywords.index_information():
    client.images.fits_keywords.create_index("FILENAME", unique=True)

if not 'skyflats' in client.images.collection_names():
    client.images.create_collection('skyflats')

if not 'FILENAME_1' in client.images.skyflats.index_information():
    client.images.skyflats.create_index("FILENAME", unique=True)


for root, directory, files in os.walk(image_dir):
    night = re.findall('[0-9]+', root)[-1]
    print '@@@> night: ' + night
    for filename in files:
        try:
            kws = dict(fits.getheader('%s/%s' % (root, filename)))
        except IOError:
            print 'Broken file %s' % filename
            continue
        except astropy.io.fits.verify.VerifyError:
            continue
        if not 'FILENAME' in kws:
            kws['FILENAME'] = os.path.basename(filename)
        kws['_night'] = night
        kws['_filename'] = os.path.basename(filename)
        if 'COMMENT' in kws:
            kws['COMMENT'] = str(kws['COMMENT'])
        if '' in kws:
            print 'Invalid empty key: %s' % kws.pop('')
        try:
            client.images.fits_keywords.insert_one(kws)
        except DuplicateKeyError:
            print 'Duplicate file %s' % kws['FILENAME']

        if kws['IMAGETYP'] in ['skyflat', 'sky-flat']:
            try:
                data = fits.getdata('%s/%s' % (root, filename))
            except TypeError:
                print 'Broken file %s' % filename
                continue

            long = kws['LONGITUD']
            lat = kws['LATITUDE']
            elevation = float(kws['ALTITUDE'])
            date = kws['DATE-OBS']
            date = string.replace(date, '-', '/')
            date = string.replace(date, 'T', ' ')
            date = string.replace(date, '\'', '')
            observatory = ephem.Observer()
            observatory.long = long
            observatory.lat = lat
            observatory.elevation = elevation
            observatory.date = date
            sun = ephem.Sun()
            sun.compute(observatory)


            avg, median, stdev = np.average(data), np.median(data), np.std(data)
            try:
                aux = dict(FILENAME=filename, night=night, avg_counts=avg, median_counts=median, stdev_counts=stdev,
                           date=date,
                           sun_az=sun.az,
                           sun_alt=sun.alt,
                           tel_alt=kws['ALT'],
                           tel_az=kws['AZ'],
                           exptime=kws['EXPTIME'],
                           filter=kws['FILTER'])
            except KeyError:
                pass
            try:
                client.images.skyflats.insert_one(aux)
                print('Added skyflat %s.' % aux['FILENAME'])
            except DuplicateKeyError:
                pass
            del data