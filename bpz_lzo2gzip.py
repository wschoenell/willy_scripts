import tables
import h5py
import sys
import os

__author__ = 'william'

if os.path.exists(sys.argv[2]):
    print 'File %s exists.' % sys.argv[2]
    sys.exit(0)

f1 = tables.File(sys.argv[1], 'r')
f2 = h5py.File(sys.argv[2], 'w')


def copy(node):
    print node
    ds1 = f1.get_node(node)
    ds2 = f2.create_dataset(node, data=ds1, compression='gzip', compression_opts=4)

for member in f1.get_node('/').__members__:
    copy('/%s' % member)

f1.close()
f2.close()
