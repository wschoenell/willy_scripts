import sys
from astropy.io import fits

img = fits.open(sys.argv[1])
fits.writeto('wcsfix_' + sys.argv[1], data=img[0].data.T, header=img[0].header)
print('Fixed %s' % sys.argv[1])