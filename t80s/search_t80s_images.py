import datetime as dt
import sys

import pymongo
import ephem

observer = ephem.Observer()
observer.lat = "-30:10:04.31"
observer.lon = "-70:48:20.48"
observer.elevation = 2178
moon = ephem.Moon()

host = '192.168.20.118'
# host = None

client = pymongo.MongoClient(host=host)


def print_data(query, print_moonpos=True):
    for obj in query:
        if 'OBJECT' in obj.keys():
            if not "FILTER" in obj.keys():
                print('echo "Downloading {OBJECT}. Night {_night}, Exptime = {EXPTIME}"'.format(**obj))
            else:
                s = 'echo "Downloading {OBJECT}. Night {_night}, Filter = {FILTER}, Exptime = {EXPTIME}"'.format(**obj)
                if print_moonpos:
                    body = ephem.FixedBody()
                    body._ra = obj["RA"]
                    body._dec = obj["RA"]
                    observer.date = dt.datetime.strptime(obj['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
                    moon.compute(observer)
                    body.compute(observer)
                    s += ", moon_alt: %3.2f deg, moon_dist: %3.2f deg" % (moon.alt, ephem.separation(moon, body) * 57.2957795)
                print(s)
        elif 'IMAGETYP' in obj.keys():
            print('echo "Bias"')
        else:
            print('echo "Night {night}, Filter = {filter}, Exptime = {exptime}"'.format(**obj))
        print(addr_str.format(**obj))


if len(sys.argv) > 2:
    query = client.images.fits_keywords.find({"OBJECT": {"$regex": "^%s.*" % sys.argv[1]}, "FILTER": sys.argv[2]})
    addr_str = 'wget -c --no-check-certificate https://t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br/{_night}/{FILENAME}'
if sys.argv[1] == 'skyflat':
    pipe = [
        {'$match': {"$and": [{"filter": sys.argv[2]},
                             {"avg_counts": {"$gt": 8000}}, {"avg_counts": {"$lt": 45000}},
                             {'night': {'$gt': (dt.datetime.today() - dt.timedelta(days=60)).strftime('%Y%m%d')}}
                             ]}},
        # {'$li mit': 11},
        {'$sort': {"night": 1}}
    ]
    print('# Query: ' + str(pipe))
    query = client.images.skyflats.aggregate(pipeline=pipe)
    addr_str = 'wget -c --no-check-certificate https://t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br/{night}/{FILENAME}'
elif sys.argv[1] == 'skyflat-date':
    for fid in sys.argv[2].split(','):
        pipe = [
            {'$match': {"$and": [{"filter": fid},
                                 {"avg_counts": {"$gt": 8000}}, {"avg_counts": {"$lt": 45000}},
                                 {'night': {'$lt': (
                                     dt.datetime.strptime(sys.argv[3], '%Y-%m-%d') + dt.timedelta(days=10)).strftime(
                                     '%Y%m%d')}},
                                 {'night': {'$gt': (
                                     dt.datetime.strptime(sys.argv[3], '%Y-%m-%d') - dt.timedelta(days=10)).strftime(
                                     '%Y%m%d')}}
                                 ]}},
            # {'$li mit': 11},
            {'$sort': {"night": 1}}
        ]
        print('# Query: ' + str(pipe))
        query = client.images.skyflats.aggregate(pipeline=pipe)
        addr_str = 'wget -c --no-check-certificate https://t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br/{night}/{FILENAME}'
        print_data(query)
    sys.exit(0)
elif sys.argv[1] == 'skyflat-month':
    for fid in sys.argv[2].split(','):
        pipe = [
            {'$match': {"$and": [{"filter": fid},
                                 {"avg_counts": {"$gt": 8000}}, {"avg_counts": {"$lt": 45000}},
                                 {'night': {'$gt': sys.argv[3] + "00"}},
                                 {'night': {'$lt': sys.argv[3] + "32"}}
                                 ]}},
            # {'$li mit': 11},
            {'$sort': {"night": 1}}
        ]
        print('# Query: ' + str(pipe))
        query = client.images.skyflats.aggregate(pipeline=pipe)
        addr_str = 'wget -c --no-check-certificate https://t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br/{night}/{FILENAME}'
        print_data(query)
    sys.exit(0)
elif sys.argv[1] == 'bias-month':
    for night in sys.argv[2].split(','):
        pipe = [
            {'$match': {"$and": [
                {'IMAGETYP': "ZERO"},
                {'_night': {'$lt': sys.argv[2] + "32"}},
                {'_night': {'$gt': sys.argv[2] + "00"}}
            ]}},
            # {'$li mit': 11},
            {'$sort': {"night": 1}}
        ]
        print('# Query: ' + str(pipe))
        query = client.images.fits_keywords.aggregate(pipeline=pipe)
        addr_str = 'wget -c --no-check-certificate https://t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br/{_night}/{FILENAME}'
        print_data(query)
    sys.exit(0)

elif sys.argv[1] == 'bias-date':
    for night in sys.argv[2].split(','):
        pipe = [
            {'$match': {"$and": [

                {'IMAGETYP': "ZERO"},
                {'_night': {'$eq': (dt.datetime.strptime(night, '%Y-%m-%d')).strftime('%Y%m%d')}},

            ]}},
            # {'$li mit': 11},
            {'$sort': {"night": 1}}
        ]
        print('# Query: ' + str(pipe))
        query = client.images.fits_keywords.aggregate(pipeline=pipe)
        addr_str = 'wget -c --no-check-certificate https://t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br/{_night}/{FILENAME}'
        print_data(query)
    sys.exit(0)
else:
    q = {"OBJECT": {"$regex": "^%s.*" % sys.argv[1]}}
    print "#" + str(q)
    query = client.images.fits_keywords.find(q)
    addr_str = 'wget -c --no-check-certificate https://t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br/{_night}/{FILENAME}'

print_data(query)
