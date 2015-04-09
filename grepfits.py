#!/usr/bin/env python
import sys
from astropy.io import fits
for f_ in sys.argv[1:]:
   print '%s: %s' % (f_, fits.getheader(f_)['OBJECT'])
