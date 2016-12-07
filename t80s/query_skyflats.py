import datetime as dt
import pymongo
import sys

# host = None
host = '192.168.20.118'
yaml_path = '/mnt/public/skyflats/skyflat.yaml'
filter_order = ['G', 'I', 'R', 'Z', 'F861', 'F660', 'F515', 'F410', 'F430', 'U', 'F395', 'F378']

header_yaml = """
programs:

  - name: PROG01
    pi: Tiago Ribeiro   # (optional)
    priority: 1         # (optional)
    actions:
      - action: point
        alt: "80:00:00"
        az: "78:00:00"
"""

skyflat_yaml = """
      - action: autoflat
        filter: {filter}
        frames: {frames}
"""

client = pymongo.MongoClient(host=host)

pipe = [
    {'$match': {"$and": [{"avg_counts": {"$gt": 8000}}, {"avg_counts": {"$lt": 45000}},
                         {'night': {'$gt': (dt.datetime.today() - dt.timedelta(days=30)).strftime('%Y%m%d')}}]}},
    {'$group': {"_id": "$filter", "count": {"$sum": 1}}},
    {'$sort': {"count": 1}}
]

query = client.images.skyflats.aggregate(pipeline=pipe)

if len(sys.argv) == 1:
    for img in query:
        print('{_id}: {count}'.format(**img))
else:
    if sys.argv[3] != 'morning':
        filter_order.reverse()
    scheduler_yaml = header_yaml
    skyflat_filters = list(query)[:int(sys.argv[1])]
    skyflat_filters = [i['_id'] for i in skyflat_filters]
    for filter_id in filter_order:
        if filter_id in skyflat_filters:
            scheduler_yaml += skyflat_yaml.format(**dict(filter=filter_id, frames=sys.argv[2]))

    print scheduler_yaml

    with open(yaml_path, 'w') as fp:
        fp.writelines(scheduler_yaml)



