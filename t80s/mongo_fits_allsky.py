import os

import astropy
import datetime
import pymongo
import sys
from astropy.io import fits
from dateutil import tz
from pymongo.errors import DuplicateKeyError

client = pymongo.MongoClient()

image_dir = '/mnt/public/allsky/'
print 'image_dir = ', image_dir

with open('/home/mongo/last_skip_allsky.txt', 'r') as f:
    i_file = int(f.read())


if not 'fits_keywords_allsky' in client.images.collection_names():
    client.images.create_collection('fits_keywords_allsky')

if not 'FILENAME_1' in client.images.fits_keywords_allsky.index_information():
    client.images.fits_keywords_allsky.create_index("FILENAME", unique=True)

# for root, directory, files in os.walk(image_dir):
#     for filename in files:
#         if filename.endswith('.FIT'):
while 1:
    filename = 'AllSkyImage%09d.FIT' % i_file
    i_file += 1
    if os.path.exists(image_dir+filename):
        print 'Filename:', filename
        try:
            kws = dict(fits.getheader('%s/%s' % (image_dir, filename)))
        except IOError:
            print 'Broken file %s/%s' % (image_dir, filename)
            continue
        except astropy.io.fits.verify.VerifyError:
            continue
        if not 'FILENAME' in kws:
            kws['FILENAME'] = os.path.basename(filename)
        kws['_filename'] = os.path.basename(filename)

        if "DATE-OBS" in kws:
            kws['_utdatetime'] = datetime.datetime.strptime(kws['DATE-OBS'].split('.')[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=tz.tzutc())
            localtime = kws['_utdatetime'].astimezone(tz.tzlocal())
            if localtime.hour < 12:
                jd_day = localtime - datetime.timedelta(days=1)
            else:
                jd_day = localtime

            kws['_night'] = jd_day.strftime("%Y%m%d")

        if 'COMMENT' in kws:
            kws['COMMENT'] = str(kws['COMMENT'])
        if '' in kws:
            print 'Invalid empty key: %s' % kws.pop('')
        try:
            client.images.fits_keywords_allsky.insert_one(kws)
        except DuplicateKeyError:
            print 'Duplicate file %s' % kws['FILENAME']
    else:
        with open('/home/mongo/last_skip_allsky.txt', 'w') as f:
            f.write(str(i_file-100))
        sys.exit(0)