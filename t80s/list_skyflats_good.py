import pymongo

pipe = [
    {"$match": {"quality": {"$eq": 1}}},
    {"$sort": {"_utdatetime": 1}},
]

host = "192.168.20.118"
client = pymongo.MongoClient(host)

files_good = list()
for img in client.images.skyflats_allsky_quality.aggregate(pipeline=pipe):
    print img
    files_good.append(img['SKYFLAT_FILENAME'])
