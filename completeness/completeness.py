from __future__ import division

import json
import time

# import matplotlib
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt

import os

from astropy.coordinates import SkyCoord
from astropy.io import fits, ascii
import numpy as np

from artificial_stars import add_stars
from sourceDetection import SDetection

config = {"image": os.path.expanduser("~/data/completeness/UGC3816_f814w_res.fits"),
          "mask": os.path.expanduser("~/data/completeness/UGC3816_f814wmask.fits"),
          "weight": os.path.expanduser("~/data/completeness/UGC3816_f814wWHT.fits"),
          "psf": os.path.expanduser("~/data/completeness/psf_acs_f550m_dst.fits"),
          "filter": "f814w",
          "zero_point": 25.1243,
          "niter": 20,
          "obj_minsep": 40,  # pixels
          "n_stars": 500,
          "outfile": "UGC3816_f814w_completeness.json"
          }


# config = {"image": os.path.expanduser("~/data/completeness/UGC3816_f160w_res.fits"),
#           "mask": os.path.expanduser("~/data/completeness/UGC3816_f160wmask.fits"),
#           "weight": os.path.expanduser("~/data/completeness/UGC3816_f160wWHT.fits"),
#           "psf": os.path.expanduser("~/data/completeness/psf_acs_f550m_dst.fits"),
#           "filter": "f160w",
#           "zero_point": 25.9463,
#           "niter": 20,
#           "obj_minsep": 40,  # pixels
#           "n_stars": 500,
#           "outfile": "UGC3816_f160w_completeness.json"
#           }

# run sextractor on the original image
SDetection(config["image"], config["weight"], config["filter"])
original_sex = ascii.SExtractor().read("photometry.cat")
xycatalog = [[c['X_IMAGE'], c['Y_IMAGE']] for c in original_sex]

# open images
image, header = fits.getdata(config["image"], header=True)
mask = fits.getdata(config["mask"])
psf = fits.getdata(config["psf"])

out = {}

for mag in np.arange(24, 28, 0.1):
    t0 = time.time()
    for iter in range(config["niter"]):
        # add stars
        img, xypos, mags = add_stars(np.copy(image), psf,
                                     flux=header["EXPTIME"] * 10 ** (-0.4 * (mag - config["zero_point"])),
                                     minsep=config["obj_minsep"], n_stars=config["n_stars"], mask=mask,
                                     catalog=xycatalog,
                                     sigma=0, debug=True)

        # plt.clf()
        # plt.imshow(np.log10(img), cmap=plt.cm.gray)

        # save image
        try:
            os.unlink("caca.fits")
        except OSError:
            pass
        fits.writeto("caca.fits", img, header=header)

        # source extraction
        SDetection("caca.fits", config["weight"], config["filter"])
        catalog_sex = ascii.SExtractor().read("photometry.cat")

        # filter objects with GOOD flags
        catalog_sex = catalog_sex[catalog_sex['FLAGS'] == 0]
        # limit magnitude error
        catalog_sex = catalog_sex[catalog_sex['MAGERR_ISO'] <= 0.2]
        # limit FWHM
        catalog_sex = catalog_sex[catalog_sex['FWHM_IMAGE'] > 1.0]
        catalog_sex = catalog_sex[catalog_sex['FWHM_IMAGE'] < 4.0]
        # limit stellarity
        catalog_sex = catalog_sex[catalog_sex['CLASS_STAR'] >= 0.5]


        # catalog matching
        xypos = SkyCoord(xypos[:, 1], xypos[:, 0], 0, representation='cartesian')
        # xypos = SkyCoord(xypos[:, 0], xypos[:, 1], 0, representation='cartesian')
        catalog = SkyCoord(np.array(catalog_sex['X_IMAGE']), np.array(catalog_sex['Y_IMAGE']), 0,
                           representation='cartesian')
        idx, sep2d, _ = xypos.match_to_catalog_3d(catalog)
        catalog_stars = catalog_sex[idx[np.array(sep2d) < 0.01]]
        #
        # catalog_stars.write('test.dat', format='ascii.commented_header', overwrite=True)

        # write results
        if not mag in out:
            out[mag] = {'count': [], 'mag': []}
        out[mag]['count'].append(len(catalog_stars))
        out[mag]['mag'].append(np.median(catalog_stars["MAG_APER_4"][catalog_stars['FLAGS'] == 0]))

        with open(config["outfile"], "w") as fp:
            json.dump(out, fp)

        print("Iter %i took %.2f s" % (iter, time.time() - t0))

# plots
# mag vs recover fraction


# plt.figure(1)
# plt.clf()
# x = np.sort(out.keys())
# y = np.array([np.average(np.array(out[m]['count']) / config["n_stars"]) for m in x])
# z = np.array([np.std(np.array(out[m]['count']) / config["n_stars"]) for m in x])
# plt.errorbar(x, y, yerr=z)
# # plt.scatter(x, y)
