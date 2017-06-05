import numpy as np
import pymongo

host = '192.168.20.118'
client = pymongo.MongoClient(host=host)
pipeline = [
    {"$match": {"OBJECT": {"$regex": "^%s.*" % "LOWC"}}},
    {"$group": {"_id": "$OBJECT", "headers": { "$push": "$$ROOT" }}},  #
    # {"count": {"$sum": 1}}
]
query = client.images.fits_keywords.aggregate(pipeline=pipeline)

for field in query:
    n = np.unique(np.sort([h["_night"] for h in field["headers"]]))
    print field["_id"],len(n), " ".join(n)