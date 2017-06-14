import sys

from astropy.io import fits

for f in sys.argv[1:]:
    img = fits.open(f, mode='update')
    header = img[0].header
    header.update(img[1].header)

    img.close(output_verify="fix")
