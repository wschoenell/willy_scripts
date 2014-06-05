import bz2

from astropy.wcs import wcs
from scipy.interpolate import interp2d
from pysextractor import SExtractor
import numpy as np
import matplotlib.pyplot as plt

__author__ = 'william'

from astropy.io import ascii, fits

data_dir = '/Users/william/Downloads'
tb_galaxies = ascii.read('data/galaxies.txt')
passbands = ('u', 'g', 'r', 'i', 'z')
window_size = 320

filter_seg = 'r'


def sdss_ccd_gain(filter, camcol, run):
    # Data from http://data.sdss3.org/datamodel/files/BOSS_PHOTOOBJ/frames/RERUN/RUN/CAMCOL/frame.html
    gain = {'u': [1.62, -999, 1.59, 1.6, 1.47, 2.17],
            'g': [3.32, 3.855, 3.845, 3.995, 4.05, 4.035],
            'r': [4.71, 4.60, 4.72, 4.76, 4.725, 4.895],
            'i': [5.165, 6.565, 4.86, 4.885, 4.64, 4.76],
            'z': [4.745, 5.155, 4.885, 4.775, 3.48, 4.69]}

    if filter == 'u' and camcol == 2:
        if run <= 1100:
            return 1.595
        else:
            return 1.825
    else:
        return gain[filter][camcol - 1]


def sdss_ccd_darkvar(filter_name, camcol, run):
    # Data from http://data.sdss3.org/datamodel/files/BOSS_PHOTOOBJ/frames/RERUN/RUN/CAMCOL/frame.html
    dark = {'u': [9.61, 12.6025, 8.7025, 12.6025, 9.3025, 7.0225],
            'g': [15.6025, 1.44, 1.3225, 1.96, 1.1025, 1.8225],
            'r': [1.8225, 1.00, 1.3225, 1.3225, 0.81, 0.9025],
            'i': [7.84, -999, 4.6225, -999, 7.84, 5.0625],
            'z': [0.81, 1.0, 1.0, -999, -999, 1.21]}

    if filter_name == 'i':
        if camcol == 2:
            if run <= 1500:
                return 5.76
            else:
                return 6.25
        elif camcol == 4:
            if run <= 1500:
                return 6.25
            else:
                return 7.5625
        else:
            return dark[filter_name][camcol - 1]
    elif filter_name == 'z':
        if camcol == 4:
            if run <= 1500:
                return 9.61
            else:
                return 12.6025
        elif camcol == 5:
            if run <= 1500:
                return 1.8225
            else:
                return 2.1025
        else:
            return dark[filter_name][camcol - 1]
    else:
        return dark[filter_name][camcol - 1]


band_err = {'u': 0.05,
            'g': 0.02,
            'r': 0.02,
            'i': 0.02,
            'z': 0.03}


def get_sdss_image(f_sdss, filter_name, run, camcol):
    # Error calculation as suggested by:
    # http://data.sdss3.org/datamodel/files/BOSS_PHOTOOBJ/frames/RERUN/RUN/CAMCOL/frame.html
    img = f_sdss[0].data

    sky = f_sdss[2].data
    aux_i = interp2d(np.arange(sky['ALLSKY'].shape[1]), np.arange(sky['ALLSKY'].shape[2]), sky['ALLSKY'][0])
    simg = aux_i(sky['XINTERP'][0], sky['YINTERP'][0])

    cimg = np.repeat(f_sdss[1].data, f_sdss[0].data.shape[0]).reshape(f_sdss[0].data.shape)

    #If you have performed the above calculations, you can return the image to very close to the state it was in when input into the photometric pipeline, as follows:

    dn = img / cimg + simg

    gain = sdss_ccd_gain(filter_name, camcol, run)
    darkVariance = sdss_ccd_darkvar(filter_name, camcol, run)

    # These dn values are in the same units as the "data numbers" stored by the raw data files that come off the instrument. They are related to the detected number nelec of photo-electrons by:

    # nelec = dn * gain

    # With those values (gain and DarkVariance) in hand the following yields the errors in DN

    dn_err = np.sqrt(dn / gain + darkVariance)

    # Finally, to get those errors into nanomaggies, you simply apply back the calibration:

    img_err = dn_err * cimg

    ########################################################################################

    return img, img_err


for i_gal in range(len(tb_galaxies)):
    # 0 - Segmentation. limiar=alpha*sigma(ceu)*bin
    fname_sex = '%s/frame-%s-%06i-%i-%04i.fits' % (data_dir, filter_seg, tb_galaxies[i_gal]['run'],
                                                   tb_galaxies[i_gal]['camcol'], tb_galaxies[i_gal]['field'])

    sex = SExtractor()
    sex.config['CHECKIMAGE_TYPE'] = 'SEGMENTATION'
    sex.run(fname_sex)
    segmap = fits.open('check.fits')[0].data

    for filter_name in passbands:
        # 1 - Open the SDSS image file.
        ###  Data-Model http://data.sdss3.org/datamodel/files/BOSS_PHOTOOBJ/frames/RERUN/RUN/CAMCOL/frame.html
        f_sdss = fits.open('%s/frame-%s-%06i-%i-%04i.fits' % (data_dir, filter_name, tb_galaxies[i_gal]['run'],
                                                              tb_galaxies[i_gal]['camcol'], tb_galaxies[i_gal]['field']))

        ## 1.2 - Get the image and its errors
        img, img_err = get_sdss_image(f_sdss, filter_name, tb_galaxies[i_gal]['run'],
                                      tb_galaxies[i_gal]['camcol'])

        ## 1.3 - Get the WCS
        wcsys = wcs.WCS(header=f_sdss[0].header)

        # 2 - Cut a window around the galaxy
        y, x = wcsys.wcs_world2pix(tb_galaxies['ra'][i_gal], tb_galaxies['dec'][i_gal], 1)
        interval = (int(round(x - window_size / 2)), int(round(x + window_size / 2)), int(round(y - window_size / 2)),
                    int(round(y + window_size / 2)))
        img_cut = img[interval[0]:interval[1], interval[2]:interval[3]]
        img_cut_err = img_err[interval[0]:interval[1], interval[2]:interval[3]]

        plt.figure(1)
        plt.clf()
        plt.imshow(np.log10(img_cut))

        ## 2.1 - And around the galaxy on segmap.
        seg_cut = segmap[interval[0]:interval[1], interval[2]:interval[3]]
        plt.figure(2)
        plt.clf()
        y = np.bincount(np.ravel(seg_cut))
        arg = np.argmax(y[1:, ]) + 1
        mask = (seg_cut == arg)
        seg_cut[~mask] = 0
        seg_cut[mask] = 1
        plt.imshow(seg_cut, cmap=plt.matplotlib.cm.binary)

        raw_input('ENTER to Next..')


        # 4 - Rebin

        # 5 - Calculate pixel magnitudes

        # 6 - Save to the hdf5

