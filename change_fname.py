import os

import pyfits as pf
import sys

for fname in sys.argv[1:]:
    print 'Updating %s' % fname
    a = pf.open(fname, 'update')
    a[0].header.set('FILENAME', os.path.basename(fname))
    a.close()
