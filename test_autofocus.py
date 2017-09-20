import os
from scipy import stats

from astropy.io import ascii
import numpy as np

import matplotlib.pyplot as plt

pos_list = []
fwhm_list = []
fwhm_list_m = []
fwhm_list_mm = []


# FIT : https://github.com/astroufsc/chimera-autofocus/blob/master/chimera_autofocus/controllers/autofocus.py#L115-L117

# for dirname, subdir, files in os.walk("/Users/william/Downloads/autofocus-20170919-222802/"):
# for dirname, subdir, files in os.walk("/Users/william/Downloads/autofocus-20170919-230837/"):
for dirname, subdir, files in os.walk("/Users/william/Downloads/autofocus-20170919-234911/"):
    for fname in files:
        if fname.endswith("catalog"):
            cat = ascii.read("%s/%s" % (dirname, fname))
            mask = np.bitwise_and(cat["FLAGS"] == 0, cat["FWHM_IMAGE"] > 0)
            position = int(fname.split("-")[1])
            if position < 7000:
                fwhm = stats.mode(cat["FWHM_IMAGE"][mask]).mode[0]
                avg = np.average(cat["FWHM_IMAGE"][mask])
                median = np.median(cat["FWHM_IMAGE"][mask])
                pos_list.append(position)
                fwhm_list.append(fwhm)
                fwhm_list_m.append(avg)
                fwhm_list_mm.append(median)
                print position, fwhm

plt.clf()
# plt.plot(pos_list, fwhm_list, '.-', label="mode")
plt.plot(pos_list, fwhm_list_m, '.-', label="mean")

A, B, C = np.polyfit(pos_list, fwhm_list_m, 2)
x = np.linspace(np.min(pos_list), np.max(pos_list), 100)
plt.plot(x, np.polyval([A,B,C], x),'--', label="mean fit")

plt.plot(pos_list, fwhm_list_mm, '.-', label="median")

A, B, C = np.polyfit(pos_list, fwhm_list_mm, 2)
x = np.linspace(np.min(pos_list), np.max(pos_list), 100)
plt.plot(x, np.polyval([A,B,C], x),'--', label="median fit")

plt.legend()
