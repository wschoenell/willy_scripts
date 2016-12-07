import os
import stat

import ephem
import numpy as np
import datetime as dt
import time

# set True to test:
test = False

# Paths
path = os.path.dirname(os.path.abspath(__file__))
star_filename = os.path.join(path, 'SAO.edb')
pointings_file = 'm2pointings.txt'
m2law_data_dir = os.path.expanduser('~/data/m2law/')
skip_file = "%s/m2law_iskip.txt" % path
file_prefix = 'm2controllaw_table10_'

# Star catalog
obs_lat = "-30:10:04.31"
obs_long = "-70:48:20.48"
obs_elev = 2187

# Tolerances for the reference
reference_tolerance_pointings = 7
reference_tolerance_time = 1  # hours

# Save kill script on ~/.chimera/m2law_stop.sh
with open(os.path.expanduser('~/.chimera/m2law_stop.sh'), 'w') as f:
    f.write("#!/bin/bash\nkill -9 " + str(os.getpid()) + "\n")

st = os.stat(os.path.expanduser('~/.chimera/m2law_stop.sh'))
os.chmod(os.path.expanduser('~/.chimera/m2law_stop.sh'), st.st_mode | stat.S_IEXEC)

try:
    with open(skip_file, 'r') as f:
        i_skip = int(f.read())
except:
    i_skip = 0

raw_input("Please load the last model, i.e.: chimera-m2control --load -f %s/%s%03d.fits && chimera-m2control --deact && chimera-m2control --fit && chimera-m2control --deac" % (
m2law_data_dir, file_prefix, i_skip))


class StarCatalog(object):
    def __init__(self, filename, obs_lat, obs_long, obs_elev):
        with open(filename) as f:
            self.star_catalog = [ephem.readdb(l) for l in f.readlines()]

    def update_observer(self):
        self.obs = ephem.Observer()
        self.obs.lat = obs_lat
        self.obs.long = obs_long
        self.obs.elevation = obs_elev

    def get_nearby_star(self, alt, az):
        self.update_observer()
        dist = []
        for star in self.star_catalog:
            star.compute(self.obs)
            dist.append(np.sqrt((alt - star.alt.real) ** 2 + (az - star.az.real) ** 2))
        nearby_star = np.argmin(dist)
        return self.star_catalog[nearby_star], dist[nearby_star]


m2_map = np.loadtxt(pointings_file, dtype=np.dtype([('az', float), ('alt', float), ('i_dec', float)]))
Catalog = StarCatalog(star_filename, obs_lat, obs_long, obs_elev)

i_dec_now = None
last_ref = 0
last_reftime = dt.datetime.now()

for obj in m2_map[i_skip:]:
    while True:
        if obj['i_dec'] != i_dec_now or last_ref >= reference_tolerance_pointings or \
                        dt.datetime.now() >= last_reftime + dt.timedelta(hours=reference_tolerance_time):
            print "\tDeleting ~/images/*"
            for cmd in ("rm -fr %s/*" % os.path.expanduser("~/images/"),):
                print "\tRunning: %s" % cmd
                if not test:
                    os.system(cmd)
            # print "\tDoing Reference..."
            # star, _ = Catalog.get_nearby_star(77. * np.pi / 180., 102. * np.pi / 180.)
            # for cmd in ('python ~/ir_lights.py 1',
            #             # 'chimera-tel --slew --object "%s"' % star.name,
            #             'chimera-tel --slew --ra "%s" --dec "%s"' % (star.ra, star.dec),
            #             'python ~/ir_lights.py 0',
            #             'chimera-autoalign --auto -t 10 --minimum 100 --niter 10 --filter R',
            #             'chimera-m2control --set-reference',
            #             'chimera-m2control --add --name "%s"' % star.name,
            #             'chimera-cam --disable-display -t 10 -f R --object "%s reference" -o "%s-\$DATE-\$TIME.fits"' % (
            #                     star.name, star.name.replace(' ', ''))):
            #     print "\tRunning: %s" % cmd
            #     if not test:
            #         os.system(cmd)
            #     print('\a')  # Ring a bell when done.
            #     if 'chimera-m2control --set' in cmd:
            #         raw_input('\tENTER for next...')
            #         for _ in range(3):
            #             print('\a')
            #             time.sleep(.2)
            i_dec_now = obj['i_dec']
            last_ref = 0
            last_reftime = dt.datetime.now()

            # # Ring three times when done
            # for _ in range(3):
            #     print('\a')
            #     time.sleep(.5)

        else:
            print "\tDoing grid (%3.2f, %3.2f)..." % (obj['alt'], obj['az'])
            star, _ = Catalog.get_nearby_star(obj['alt'] * np.pi / 180, obj['az'] * np.pi / 180)
            for cmd in ('python ~/ir_lights.py 1',
                        # 'chimera-tel --slew --object "%s"' % star.name,
                        'chimera-tel --slew --ra "%s" --dec "%s"' % (star.ra, star.dec),
                        'python ~/ir_lights.py 0',
                        'chimera-m2control --update',
                        "chimera-autoalign --auto -t 10 --minimum 100 --niter 10 --filter R",
                        'chimera-m2control --add --name "%s"' % star.name,
                        'chimera-m2control --save -f "%s/%s%03d.fits"' % (m2law_data_dir, file_prefix, i_skip + 1),
                        'chimera-cam --disable-display -t 10 -f R --object "%s grid" -o "%s%03d-\$DATE-\$TIME.fits"' % (
                                star.name, file_prefix, i_skip + 1),
                        'chimera-pverify --here',
                        'chimera-astelcopm --add --name "%s"' % star.name,
                        ):
                print "\tRunning: %s" % cmd
                if not test:
                    os.system(cmd)
                print('\a')  # Ring a bell when done.
                if 'chimera-m2control --add' in cmd:
                    raw_input('\tENTER for next...')
                    for _ in range(3):
                        print('\a')
                        time.sleep(.2)
            i_skip += 1
            last_ref += 1

            with open(skip_file, 'w') as f:
                f.write(str(i_skip))
            break

    # Ring three times when done
    for _ in range(3):
        print('\a')
        time.sleep(.5)

        # raw_input('Next...')
