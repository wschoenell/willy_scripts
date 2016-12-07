import os

import astropy
import datetime
import pymongo
from astropy.io import fits
from pymongo.errors import DuplicateKeyError

client = pymongo.MongoClient()

image_dir = '/mnt/public/allsky/'
print 'image_dir = ', image_dir

if not 'fits_keywords_allsky' in client.images.collection_names():
    client.images.create_collection('fits_keywords_allsky')

if not 'FILENAME_1' in client.images.fits_keywords_allsky.index_information():
    client.images.fits_keywords_allsky.create_index("FILENAME", unique=True)

for root, directory, files in os.walk(image_dir):
    for filename in files:
        if filename.endswith('.FIT'):
            print 'Filename:', filename
            try:
                kws = dict(fits.getheader('%s/%s' % (root, filename)))
            except IOError:
                print 'Broken file %s' % filename
                continue
            except astropy.io.fits.verify.VerifyError:
                continue
            if not 'FILENAME' in kws:
                kws['FILENAME'] = os.path.basename(filename)
            kws['_filename'] = os.path.basename(filename)

            if "DATE-OBS" in kws:
                kws['_utdatetime'] = datetime.datetime.strptime(kws['DATE-OBS'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                kws['_utdate'] = kws['_utdatetime'].strftime("%Y%m%d")

            if 'COMMENT' in kws:
                kws['COMMENT'] = str(kws['COMMENT'])
            if '' in kws:
                print 'Invalid empty key: %s' % kws.pop('')
            try:
                client.images.fits_keywords_allsky.insert_one(kws)
            except DuplicateKeyError:
                print 'Duplicate file %s' % kws['FILENAME']