import os

import datetime
import pymongo
import sys

host = "192.168.20.118"
# prefix = '/Volumes/'
prefix = '/mnt/'
allsky_dir = "/%s/public/allsky/" % prefix
gif_dir = "/%s/public/allsky_gifs/" % prefix

if len(sys.argv) == 2:
    night = sys.argv[1]
else:
    localtime = datetime.datetime.now()

    if localtime.hour < 12:
        jd_day = localtime - datetime.timedelta(days=1)
    else:
        jd_day = localtime

    night = jd_day.strftime("%Y%m%d")

print 'Night:', night

gif_out = "%s/allsky_animation_%s.gif" % (gif_dir, night)

if os.path.exists(gif_out):
    print "Skipped %s. Already exists." % gif_out
    sys.exit(0)


client = pymongo.MongoClient(host)

data = client.images.fits_keywords_allsky.find({'_night': {'$eq': night}, "EXPTIME": {"$gt": 1}}).sort("_utdatetime", 1)

file_list = [d["FILENAME"].split('.')[0] + ".JPG" for d in data]

cmd = "convert -delay 20  %s/%s %s" % (allsky_dir, (" " + allsky_dir).join(file_list), gif_out)

os.system(cmd)

# -loop 0  -dither none -deconstruct -layers optimize -matte -depth 8 -map mpr:cmap
# print 'query> ', query
# -resize '400x300>'
