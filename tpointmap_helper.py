import numpy as np
import matplotlib.pyplot as plt

pointings = 256
skip = 0  # Use this to skip N first pointings to resume a model session
altitude_min = 25
altitude_max = 85
azimuth_min = 5
azimuth_max = 346
plot = True


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
    ax.scatter(map_points[:, 0] * np.pi / 180., 90 - map_points[:, 1], color='r', s=20)
    ax.grid(True)
    ax.set_ylim(90 - altitude_min + 10, 0)
    ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))
    plt.show()

i = 0
for point in map_points[skip:]:
    i += 1
    alt, az = point[1], point[0]
    if plot:
        ax.scatter(point[0] * np.pi / 180, 90 - point[1], color='b', s=10)
        ax.set_title("%d of %d done" % (i-1, pointings), va='bottom')
        plt.draw()
    print('Point: # %i (alt, az): %.2f %2f' % (i, alt, az))
    print('Pointing telescope...')
    print('chimera-tel --slew --alt %.2f --az %2.f' % (alt, az))
    print('Verifying pointing...')
    print('chimera-pverify --here')
    print('\a')  # Ring a bell when done.
    raw_input('Press ENTER for next pointing.')
