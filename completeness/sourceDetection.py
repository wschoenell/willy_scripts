import os

from astropy.io import fits
import numpy as np

dir_oriImages = './'
ddrp = ''  # ''sextractor_'
dir_galsub = './'
SEx = '/usr/local/bin/sex'
sx_configFile = './sexconf.txt'


def SDetection(ima, wei, filter, thr=2, minarea=5, FWHMpix=2.5, conv="2.5"):
    data, hdr = fits.getdata(ima, header=True)
    if filter == 'f160w':
        mag_zp = 25.9463
    elif filter == 'f814w':
        mag_zp = 25.1243  # 25.947
    # GAIN = hdr['CCDGAIN']
    else:
        raise Exception("Unknown filter %s" % filter)
    print(dict(hdr))
    EXPTIME = hdr['EXPTIME']
    PIXEL_SCALE = hdr['D001SCAL']
    # PIXEL_SCALE = hdr['PIXSCALE']
    SEEING_FWHM = FWHMpix * PIXEL_SCALE
    # dataADUs = data * EXPTIME
    SATUR_LEVEL = 12000  # 0.6 * np.max(dataADUs)
    ZEROPOINT = mag_zp + 2.5 * np.log10(EXPTIME)
    sxBG = 32
    A = ' -CATALOG_NAME ' + 'photometry.cat '
    B = ' -DETECT_MINAREA  ' + str(minarea)
    C = ' -DETECT_THRESH   ' + str(thr)
    C2 = ' -FILTER_NAME     ' + dir_galsub + 'gauss_' + conv + '_5x5.conv '
    D = ' -SATUR_LEVEL    ' + str(SATUR_LEVEL)
    E = ' -MAG_ZEROPOINT  ' + str(ZEROPOINT)
    F = ' -PHOT_APERTURES   4,6,8,10,14,18,24,32 '
    G = ' -GAIN           1.0  '
    # G = ' -GAIN           ' + str(GAIN)
    H = ' -PIXEL_SCALE    ' + str(PIXEL_SCALE)
    I = ' -SEEING_FWHM    ' + str(SEEING_FWHM)
    J = ' -WEIGHT_TYPE      MAP_WEIGHT  '
    K = ' -WEIGHT_IMAGE   ' + wei
    # K = ' -WEIGHT_IMAGE    NONE '
    L = ' -CHECKIMAGE_TYPE  APERTURES '
    M = ' -CHECKIMAGE_NAME  checkimage.fits '
    N = ' -BACK_SIZE ' + str(sxBG)
    O = ' -BACK_FILTERSIZE   3 '
    #
    cmd = SEx + " " + ddrp + ima + ' -c ' + sx_configFile + A + B + C + C2 + D + E + F + G + H + I + J + K + L + M + N + O
    print("Running: %s" % cmd)
    os.system(
        SEx + " " + ddrp + ima + ' -c ' + sx_configFile + A + B + C + C2 + D + E + F + G + H + I + J + K + L + M + N + O)
