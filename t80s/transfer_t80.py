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

header_html = """
<center>
<h1> T80S file server </h1>
Contact: wschoenell@gmail.com

</center>

<h2>How to download:</h2>
<pre>
1 - Download the csv file corresponding to the desired night based on object name list below.
2 - Filter only the objects that you want to download on using egrep.
    Example: egrep -i '(dark|skyflat|ABELL_209)' filelist_nonono.csv > download.sh
3 - Run the script file you made on the download directory: bash download.sh
</pre>

The csv file haves also image_type, object_name, filter, filename keywords for more advanced filtering.

<h2>Object names per night:</h2>
"""

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

object_list = [o.upper().replace(' ', '').strip() for o in object_list]


for night in range(nights_number):
    this_night = (jd_day - dt.timedelta(days=night)).date().strftime("%Y%m%d")
    image_dir = '%s/%s/' % (path, this_night)
    objects_html = list()
    transfer_list = list()
    targets_list = list()
    print bold('Reading directory: %s' % image_dir)
    if not os.path.isdir(image_dir):
        print bold(yellow('Skipped %s. Does not exists.' % image_dir))
    else:
        for root, directory, files in os.walk(image_dir):
            for filename in fnmatch.filter(files, "*.fits"):
                try:
                    header = fits.getheader('%s/%s' % (root, filename))
                except IOError:
                    continue
                try:
                    filter_name = header['FILTER']
                except KeyError:
                    filter_name = None
                try:
                    objname = header['OBJECT'].upper().replace(' ', '')
                except KeyError:
                    objname = None
                try:
                    imagetype = header['IMAGETYP'].upper()
                except KeyError:
                    imagetype = None

                print('Filename: %s - Object: %s' % (filename, objname))
                if objname in object_list or imagetype in object_list:
                    if objname is not None:
                        objects_html.append(objname)
                    transfer_list.append('%s/%s\n' % (this_night, filename))
                    targets_list.append('wget -c --no-check-certificate %s/%s/%s #,%s,%s,%s,%s\n' %
                                        (http_root, this_night, filename.strip(), header['IMAGETYP'], objname,
                                         filter_name, filename))

    if len(transfer_list) > 0:
        aux = list(set(objects_html))
        aux.sort()
        header_html += "<b>%s:</b> <pre>" % this_night
        header_html += ', '.join(aux)
        header_html += "</pre>"

        print bold(green('Transfering night: %s...' % night))

        # Create directories...
        cmd = '/usr/bin/ssh %s mkdir -p %s/%s' % (remote.split(':')[0], remote.split(':')[1], this_night)
        print(bold('Running: ')+cmd)
        os.system(cmd)

        # Transfer filelist:
        aux_filenames = 'filelist_%s.csv' % this_night
        aux_header = True if not os.path.exists(aux_filenames) else False
        with open(aux_filenames, 'a') as f:
            if aux_header:
                f.write('# wget, image_type, object_name, filter, filename\n')
            f.writelines(targets_list)
        cmd = '/usr/bin/sort filelist_%s.csv | /usr/bin/uniq > l && /bin/mv l filelist_%s.csv' % (this_night, this_night)
        print(bold('Running: ')+cmd)
        os.system(cmd)
        cmd = '/usr/local/bin/rsync -av --progress %s %s/' % (aux_filenames, remote)
        print(bold('Running: ')+cmd)
        os.system(cmd)

        # Transfer files
        aux_filenames = tempfile.mktemp()
        with open(aux_filenames, 'w') as f:
            f.writelines(transfer_list)
        cmd = '/usr/local/bin/rsync -avz --progress --files-from=%s %s %s/' % (aux_filenames, path, remote)
        print(bold('Running: ')+cmd)
        os.system(cmd)
        os.unlink(aux_filenames)

with open('HEADER.html', 'w') as f:
    f.write(header_html)
cmd = 'rsync -av --progress HEADER.html %s/' % remote
print(bold('Running: ')+cmd)
os.system(cmd)

