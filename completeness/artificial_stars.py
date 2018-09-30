from __future__ import division
import os

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.spatial import distance
from scipy.stats import mode


def add_stars(image, psf, flux=1, n_stars=100, mask=None, debug=False, minsep=0, catalog=None, sigma=0):
    """

    :param image: Input image
    :param psf: Input PSF
    :param flux: Input zero-point flux. e.g.: EXPTIME * 10 ** (-0.4 * (mag - zero_point))
    :param n_stars: Number of stars to add to the Image
    :param mask: Input mask
    :param debug: Debug?
    :param minsep: Minimum star separation
    :param catalog: Input catalog (to avoid add stars on top of existing objects)
    :param sigma: Magnitude distribution sigma (units of flux). If zero, all stars will have the same magnitude.
    :return:
    """
    n = 1
    xypos = []
    fluxes = []
    while n <= n_stars:
        x1, y1 = np.random.randint(0, high=image.shape[0]), np.random.randint(0, high=image.shape[1])
        x2, y2 = x1 + psf.shape[0], y1 + psf.shape[1]
        # Only accept stars inside the image
        if x2 <= image.shape[0] and y2 <= image.shape[1]:
            center = [x2 - (x2 - x1) / 2, y2 - (y2 - y1) / 2]
            if mask is None or np.sum(mask[x1:x2, y1:y2] != 0) == 0:
                # avoid star overlap (self + original img, if catalog provided)
                if sum(np.array([distance.euclidean((center[0], center[1]), pos) for pos in xypos]) <= minsep) == 0 and \
                        (catalog is not None and
                             sum(np.array(
                                 [distance.euclidean((center[0], center[1]), pos) for pos in catalog]) <= minsep) == 0):
                    n += 1
                    # todo: mags sigma
                    if sigma != 0:
                        raise NotImplementedError("Sigma !=0 not implemented!")
                    image[x1:x2, y1:y2] += (psf * flux)
                    xypos.append(center)
                    fluxes.append(flux)
                elif debug:
                    print("star too close to other obj %i:%i, %i:%i" % (x1, x2, y1, y2))
            elif debug:
                print("bad pixels of %i:%i, %i:%i = %i, n_stars = %i" % (x1, x2, y1, y2, np.sum(mask[x1:x2, y1:y2] == 1), len(xypos)))
    return image, np.array(xypos), fluxes


if __name__ == '__main__':
    imsize = (2453, 2436)
    image = np.zeros(imsize) + 2e-8
    mask = np.zeros(imsize)
    mask[100:130, 100:130] = 1
    psf = fits.getdata('/Users/william/data/completeness/psf_acs_f550m_dst.fits') * 10
    image, xypos = add_stars(image, psf, mask=mask)
    plt.clf()
    plt.imshow(image)
    if os.path.exists("caca.fits"):
        os.unlink("caca.fits")
    fits.writeto('caca.fits', image)
    os.system('sex -c sexconf.txt caca.fits')
    f = np.loadtxt("name.cat")
    f = f[f < 99]
    print(mode(f))
