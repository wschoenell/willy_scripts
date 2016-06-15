# coding=utf-8
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt

pointings = 20
skip = 0  # Use this to skip N first pointings to resume a model session
altitude_min = 25
altitude_max = 85
azimuth_min = 5
azimuth_max = 346
plot = True
save_file_pointings = None  # 'dome_pointing.txt'  # None
save_file_done = 'pointings_done.txt'
load_file = None #'pointings_done.txt'  # 'lna_dome_model_data.txt'  # None

use_starname = True  # Use this if the method does not support pointing by chimera
use_mac_clipboard = False  # Will copy name of the stars to the clipboard. Only works on mac.
# LNA
# obs_lat = "-22:32:04"
# obs_long = "-45:34:57"
# obs_elev = 1864
# chimera_prefix = 'ssh lna'
# UFSC
obs_lat = "-27:36:12.286"
obs_long = "-48:31:20.535"
obs_elev = 25
chimera_prefix = 'ssh ufsc'
# chimera_prefix = 'ssh 150.162.131.89'

star_catalogfile = 'SAO.edb'
# star_catalogfile = 'NGC.edb'

if use_starname:
    import ephem

    with open(star_catalogfile) as f:
        star_catalog = [ephem.readdb(l) for l in f.readlines() if not l.startswith('#')]


def get_nearby_star(catalog, alt, az):
    obs = ephem.Observer()
    obs.lat = obs_lat
    obs.long = obs_long
    obs.elevation = obs_elev
    dist = []
    for star in star_catalog:
        star.compute(obs)
        dist.append(np.sqrt((alt - star.alt.real) ** 2 + (az - star.az.real) ** 2))
    nearby_star = np.argmin(dist)
    return star_catalog[nearby_star], dist[nearby_star]


def angin2pi(angle):
    return angle - int(angle / (2 * np.pi)) * 2 * np.pi


# Vogel's method to equally spaced points
# Ref: http://blog.marmakoide.org/?p=1
radius = np.sqrt(np.arange(pointings) / float(pointings)) * (altitude_min - altitude_max) + altitude_max

golden_angle = np.pi * (3 - np.sqrt(5))
theta = golden_angle * np.arange(pointings)

# Change to [0-2pi] inteval
theta = [angin2pi(a) for a in theta]

map_points = np.zeros((pointings, 2))
map_points[:, 0] = theta
map_points[:, 0] *= 180 / np.pi
map_points[:, 1] = radius

# Order by azimuth to avoid unecessary dome moves.
map_points = map_points[np.lexsort((map_points[:, 1], map_points[:, 0]))]

if load_file is not None:
    skip_too_close = list()
    # points_save = list()
    load_model = np.loadtxt(load_file).T[:2]
    for point_load in load_model.T:
        offset = 0
        for i in range(len(map_points)):
            map_point = map_points[i - offset]
            if np.sqrt((point_load[0] - map_point[0]) ** 2 + (point_load[1] - map_point[1]) ** 2) < 4:
                skip_too_close.append(map_point)
                map_points = np.delete(map_points, i, axis=0)
                offset += 1
    skip_too_close = np.array(skip_too_close)

if plot:
    plt.clf()
    ax = plt.subplot(111, projection='polar')
    ax.set_theta_zero_location("N")
    ax.scatter(map_points[:, 0] * np.pi / 180., 90 - map_points[:, 1], color='r', alpha=50, s=20)
    if load_file is not None:
        ax.scatter(load_model[0] * np.pi / 180., 90 - load_model[1], color='green', s=20)
        ax.scatter(skip_too_close[:, 0] * np.pi / 180., 90 - skip_too_close[:, 1], color='black', s=20)
        print 'Skip %d' % len(skip_too_close)
    ax.grid(True)
    ax.set_ylim(90 - altitude_min + 10, 0)
    ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))
    # plt.show()
    plt.draw()

if save_file_pointings is not None:
    np.savetxt(save_file_pointings, map_points, fmt='%6.3f')

if save_file_done is not None:
    file_pointings = open(save_file_done, 'a+')
    file_pointings.write(
        '# Measurements below initiated on %s\n# azimuth (deg)    altitude (deg)\n' % datetime.datetime.utcnow().strftime('%Y%m%d %H:%M:%S UTC'))

i = skip
for point in map_points[skip:]:
    i += 1
    alt, az = point[1], point[0]
    print('Point: # %i (alt, az): %.2f %2f' % (i, alt, az))
    # If a star name is needed to the method of pointing model, get the nearest star from the desired point.
    if use_starname:
        star, distance = get_nearby_star(star_catalog, alt * np.pi / 180, az * np.pi / 180)
        alt, az = star.alt.real * 180 / np.pi, star.az.real * 180 / np.pi
        os.system('echo %s | pbcopy' % star.name)
        s = raw_input(
            'Point Telescope to star %s (alt, az, dist): %s, %s, %.2f and press ENTER to verify S to skip. E to exit.' % (
                star.name, star.alt, star.az, distance))
        if s == 'S':
            continue
        elif s == 'E':
            break
    else:
        print('Pointing telescope...')
        os.system('%s chimera-tel --slew --alt %.2f --az %2.f' % (chimera_prefix, alt, az))
    if plot:
        ax.scatter(point[0] * np.pi / 180, 90 - point[1], color='b', s=10)
        ax.set_title("%d of %d done" % (i - 1, pointings), va='bottom')
        plt.draw()
    print('Verifying pointing...')
    print('chimera-pverify --here')
    os.system('%s chimera-pverify --here' % chimera_prefix)
    print('\a')  # Ring a bell when done.
    if save_file_done is not None:
        s = raw_input('Type N if this pointing was not okay or ENTER for the next pointing.')
        if s.lower() != 'n':
            file_pointings.write('%s    %s\n' % (az, alt))
    else:
        raw_input('Press ENTER for next pointing.')

if save_file_pointings is not None:
    file_pointings.close()
