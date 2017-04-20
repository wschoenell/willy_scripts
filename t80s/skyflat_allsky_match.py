import datetime
import pymongo

host = "192.168.20.118"

client = pymongo.MongoClient(host)
if not 'skyflats_allsky_quality' in client.images.collection_names():
    client.images.create_collection('skyflats_allsky_quality')

if not 'SKYFLAT_FILENAME_1' in client.images.skyflats_allsky_quality.index_information():
    client.images.skyflats_allsky_quality.create_index("SKYFLAT_FILENAME", unique=True)


#for skyflat in client.images.skyflats.find({"night": {"$gt": 20161101}}):
for skyflat in client.images.skyflats.aggregate([{'$match': {'night': {'$gt': (datetime.datetime.today() - datetime.timedelta(days=30)).strftime('%Y%m%d')}}}]):
    skyflat_allsky_data = {'SKYFLAT_%s' % kw: skyflat[kw] for kw in skyflat.keys() if kw != '_id'}
    skyflat_allsky_data["quality"] = 0
    # Quality:
    # 0 - not assesed
    # 1 - good/clear
    # 2 - bad/cloudy
    # 3 - no allsky data in 15 minutes

    utdate = datetime.datetime.strptime(skyflat["date"].split('.')[0], "%Y/%m/%d %H:%M:%S")

    pipe = [
        {"$match": {"_utdatetime": {"$gte": utdate}}},
        {"$sort": {"_utdatetime": 1}},
        {"$limit": 1}
    ]
    try:
        nearest_allsky = client.images.fits_keywords_allsky.aggregate(pipeline=pipe).next()
    except StopIteration:
        # There maybe still no image older than this date, so we skip to next run...
        print 'Skipped %s! No allsky image older than it!' % skyflat_allsky_data['SKYFLAT_FILENAME']
        continue

    tdiff = nearest_allsky['_utdatetime'] - utdate
    if tdiff > datetime.timedelta(minutes=15):
        skyflat_allsky_data["quality"] = 3

    skyflat_allsky_data.update({'ALLSKY_%s' % kw: nearest_allsky[kw] for kw in nearest_allsky.keys() if kw != '_id'})
    skyflat_allsky_data["time_difference"] = tdiff.total_seconds()
    try:
        client.images.skyflats_allsky_quality.insert_one(skyflat_allsky_data)
        print 'Done %s!' % skyflat_allsky_data['SKYFLAT_FILENAME']
    except:
        print 'Skipping %s. Already done.' % skyflat_allsky_data['SKYFLAT_FILENAME']



    # .find({"_utdate": [{"$gte": utdate}]}).sort({"time": 1}).limit(1)
