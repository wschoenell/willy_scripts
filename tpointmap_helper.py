import os

import numpy as np
import matplotlib.pyplot as plt

pointings = 256
skip = 0  # Use this to skip N first pointings to resume a model session
altitude_min = 25
altitude_max = 85
azimuth_min = 5
azimuth_max = 346
plot = True

use_starname = True  # Use this if the method does not support pointing by chimera
use_mac_clipboard = True  # Will copy name of the stars to the clipboard. Only works on mac.
obs_lat = "-22:32:04"
obs_long = "-45:34:57"
obs_elev = 1864
star_catalogfile = 'SAO.edb'

if use_starname:
    import ephem

    with open(star_catalogfile) as f:
        star_catalog = [ephem.readdb(l) for l in f.readlines()]


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

if plot:
    plt.clf()
    ax = plt.subplot(111, projection='polar')
    ax.set_theta_zero_location("N")
    ax.scatter(map_points[:, 0] * np.pi / 180., 90 - map_points[:, 1], color='r', s=20)
    ax.grid(True)
    ax.set_ylim(90 - altitude_min + 10, 0)
    ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))
    plt.show()

i = 0
for point in map_points[skip:]:
    i += 1
    alt, az = point[1], point[0]
    print('Point: # %i (alt, az): %.2f %2f' % (i, alt, az))
    # If a star name is needed to the method of pointing model, get the nearest star from the desired point.
    if use_starname:
        star, distance = get_nearby_star(star_catalog, alt * np.pi / 180, az * np.pi / 180)
        alt, az = star.alt.real * 180 / np.pi, star.az.real * 180 / np.pi
        os.system('echo %s | pbcopy' % star.name)
        raw_input('Point Telescope to star %s (alt, az, dist): %s, %s, %.2f and press ENTER.' % (
        star.name, star.alt, star.az, distance))
    else:
        print('Pointing telescope...')
        print('chimera-tel --slew --alt %.2f --az %2.f' % (alt, az))
    if plot:
        ax.scatter(point[0] * np.pi / 180, 90 - point[1], color='b', s=10)
        ax.set_title("%d of %d done" % (i - 1, pointings), va='bottom')
        plt.draw()
    print('Verifying pointing...')
    print('chimera-pverify --here')
    print('\a')  # Ring a bell when done.
    raw_input('Press ENTER for next pointing.')
