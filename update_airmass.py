import sys

import math
from astropy.io import fits

from chimera.util.coord import Coord

for f in sys.argv[1:]:
    img = fits.open(f, mode='update')
    header = img[0].header
    print img[1].data.shape
    try:
        alt = header['ALT']
        airmass = 1 / math.cos(math.pi / 2 - Coord.fromDMS(alt).R)
        print 'file, alt, airmass', f, alt, airmass
        header.update({'AIRMASS': airmass})
    except KeyError:
        pass

    img.close()
