import fnmatch
import os
import sys
import datetime as dt
import tempfile

import pyfits as fits

__author__ = 'william'

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def bold(s):
    return color.BOLD + s + color.END

def yellow(s):
    return color.YELLOW + s + color.END

def red(s):
    return color.RED + s + color.END

def green(s):
    return color.GREEN + s + color.END

if len(sys.argv) < 6:
    print bold(red("Usage: %s nights_number object_file path remote http_root" % sys.argv[0]))
    sys.exit(1)

nights_number, object_file, path, remote, http_root = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]

localtime = dt.datetime.now()

if localtime.hour < 12:
    jd_day = localtime - dt.timedelta(days=1)
else:
    jd_day = localtime

with open(object_file) as f:
    object_list = f.readlines()

object_list = [o.strip().upper() for o in object_list]


for night in range(nights_number):
    this_night = (jd_day - dt.timedelta(days=night)).date().strftime("%Y%m%d")
    image_dir = '%s/%s/' % (path, this_night)
    transfer_list = list()
    targets_list = list()
    print bold('Reading directory: %s' % image_dir)
    if not os.path.isdir(image_dir):
        print bold(yellow('Skipped %s. Does not exists.' % image_dir))
    else:
        for root, directory, files in os.walk(image_dir):
            for filename in fnmatch.filter(files, "*.fits"):
                header = fits.getheader('%s/%s' % (root, filename))
                try:
                    filter_name = header['FILTER']
                except KeyError:
                    filter_name = None
                try:
                    objname = header['OBJECT'].upper()
                except KeyError:
                    objname = None
                try:
                    objname = header['OBJECT'].upper()
                    print('Filename: %s - Object: %s' % (filename, objname))
                    if objname in object_list:
                        transfer_list.append('%s/%s\n' % (root, filename))
                        targets_list.append('wget -c %s/%s/%s #,%s,%s,%s,%s\n' %
                                            (http_root, this_night, filename.strip(), header['IMAGETYP'], objname,
                                             filter_name, filename))
                except KeyError:
                    print bold(red('Skipping %s. No IMAGETYP keyword.' % filename))

    if len(transfer_list) > 0:
        print bold(green('Transfering night: %s...' % night))

        # Create directories...
        print('ssh %s mkdir -p %s/%s' % (remote.split(':')[0], remote.split(':')[1], this_night))

        # Transfer filelist:
        aux_filenames = 'filelist_%s.csv' % this_night
        aux_header = True if not os.path.exists(aux_filenames) else False
        with open(aux_filenames, 'a') as f:
            if aux_header:
                f.write('# wget, image_type, object_name, filter, filename\n')
            f.writelines(targets_list)
        os.system('sort filelist_%s.csv | uniq > l && mv l filelist_%s.csv' % (this_night, this_night))
        print('rsync -av --progress %s %s/' % (aux_filenames, remote))

        # Transfer files
        aux_filenames = tempfile.mktemp()
        with open(aux_filenames, 'w') as f:
            f.writelines(transfer_list)
        print('rsync -av --progress --include-file %s %s/%s/' % (aux_filenames, remote, this_night)) #os.system
        os.unlink(aux_filenames)

