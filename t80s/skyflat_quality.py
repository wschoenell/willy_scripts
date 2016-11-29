import pymongo
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import sys

# Set to True to FORCE allsky image reclassification
reclassify = True
host = "192.168.20.118"
allsky_dir = "/Volumes/public/allsky/"
file_list = np.loadtxt('skyflats_v1610.list', dtype='S60')

client = pymongo.MongoClient(host)
fig = plt.figure(1)


def press(event):
    if event.key.upper() == 'G':
        data["quality"] = 1
        client.images.skyflats_allsky_quality.update({"ALLSKY_FILENAME": data["ALLSKY_FILENAME"]},
                                                     {"$set": {"quality": 1}}, multi=True)
        print data["ALLSKY_FILENAME"], 'Good'
        fig.canvas.stop_event_loop()
    elif event.key.upper() == 'B':
        client.images.skyflats_allsky_quality.update({"ALLSKY_FILENAME": data["ALLSKY_FILENAME"]},
                                                     {"$set": {"quality": 2}}, multi=True)
        print data["ALLSKY_FILENAME"], 'Bad'
        fig.canvas.stop_event_loop()
    elif event.key.upper() == 'X':
        print data["ALLSKY_FILENAME"], 'Skip'
        fig.canvas.stop_event_loop()
    elif event.key.upper() == "Q":
        sys.exit(0)
    else:
        print "Unknown key pressed: ", event.key


checked_files = []

for file_check in file_list:
    data = client.images.skyflats_allsky_quality.find_one({'SKYFLAT_FILENAME': {"$eq": file_check}})
    # Check AllSky image only once per session
    if data["ALLSKY_FILENAME"] in checked_files:
        print 'skipped', data["ALLSKY_FILENAME"]
        continue

    if data['quality'] == 3:
        print 'No AllSky images within 10 minutes for %s' % file_check
        continue
    elif data['quality'] != 0 and not reclassify:
        print 'Skipping %s. Quality already checked.' % data["SKYFLAT_FILENAME"]
        continue
    elif data['quality'] != 0:
        print '%s: Quality already checked - %s' % (data["ALLSKY_FILENAME"], "GOOD" if data["quality"] == 1 else "BAD")

    img = mpimg.imread('%s/%s.JPG' % (allsky_dir, data["ALLSKY_FILENAME"].split('.')[0]))
    plt.clf()
    plt.imshow(img)
    ax = plt.axes()

    if data["quality"] == 1:
        q = "GOOD"
        qc = "green"
    elif data["quality"] == 2:
        q = "BAD"
        qc = "red"
    else:
        q = "N/A"
        qc = "white"
    ax.text(550, 50, q, fontsize=20, color=qc)

    plt.title("%s %s - %i sec" % (data["ALLSKY_FILENAME"], data["SKYFLAT_FILENAME"], data["time_difference"]))
    plt.xlabel("G = Good / B = Bad / X = Skip / Q = Quit")
    plt.draw()

    id = fig.canvas.mpl_connect('key_press_event', press)
    fig.canvas.start_event_loop(-1)
    fig.canvas.mpl_disconnect(id)

    checked_files.append(data["ALLSKY_FILENAME"])
