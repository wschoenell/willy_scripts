# input file is made by: du -m 201* | sort > dum.log
import numpy as np
import sys

def print_tarcmd():
    print "# Tape %02d - %d MB" % (i_tape, total_megs)
    print "tar cvf /dev/sa0 %s" % " ".join(total_dirs)

megas = list()
dirs = list()
with open(sys.argv[1]) as fp:
    for line in fp.readlines():
        megas.append(line.split()[0])
        dirs.append(line.split()[1].split('/')[0])

args = np.argsort(dirs)
dirs = np.array(dirs)[args]
megas = np.array(megas)[args]

limit = 2.49e6 # megas (I leave 10 Gb for the end of the tape)

total_megs = 0
total_dirs = []
i_tape = 1
for i_dir, d in enumerate(dirs):
    if int(megas[i_dir]) + total_megs > limit:
        print_tarcmd()
        total_dirs = []
        total_megs = 0
        i_tape += 1
    total_dirs.append(d)
    total_megs += int(megas[i_dir])


print_tarcmd()