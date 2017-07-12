# Mollewide projection exmaple from:
# http://balbuceosastropy.blogspot.com.br/2013/09/the-mollweide-projection.html

import json
from math import pi

import matplotlib.pyplot as plt
import numpy as np
from astropy.coordinates import Angle
from astropy.io import ascii

# Load files
splus_gal_tiles = ascii.read("splus_gal_tiles.csv")
splus_main_tiles = ascii.read("splus_tiles.csv")

with open("splus_completed.json", "r") as fp:
    splus_completed_tiles = json.load(fp)

# Filter completed fields
splus_gal_completed = [splus_gal_tiles["NAME"].searchsorted(field) for field in splus_completed_tiles if
                       field.startswith("SPLUS-b")]
splus_main_completed = [splus_gal_tiles["NAME"].searchsorted(field) for field in splus_completed_tiles if
                        field.startswith("SPLUS-n") or field.startswith("SPLUS-s")]

# Plot init.

fig = plt.figure(1, figsize=(8, 6))
fig.clf()
ax = fig.add_subplot(111, projection="mollweide")
tick_labels = np.array([150, 120, 90, 60, 30, 0, 330, 300, 270, 240, 210])
tick_labels = np.remainder(tick_labels + 360, 360)
ax.set_xticklabels(tick_labels)
# ax.set_xticklabels(['14h', '16h', '18h', '20h', '22h', '0h', '2h', '4h', '6h', '8h', '10h'])
ax.grid(True)

# Galactic


splus_gal_ra = np.array([Angle(ra + " hours").to("radian").value for ra in splus_gal_tiles['RA']])

splus_gal_ra = np.remainder(splus_gal_ra + 2 * pi, 2 * pi)  # shift RA values
ind = splus_gal_ra > pi
splus_gal_ra[ind] -= 2 * pi  # scale conversion to [-180, 180]
splus_gal_ra *= -1  # reverse the scale: East to the left

splus_gal_dec = np.array([Angle(dec + " degrees").to("radian").value for dec in splus_gal_tiles['DEC']])

ax.scatter(splus_gal_ra, splus_gal_dec, alpha=.5)  # , color='#2ca02c')
ax.scatter(splus_gal_ra[splus_gal_completed], splus_gal_dec[splus_gal_completed], alpha=.5, color='#2ca02c')

# Main


splus_main_ra = np.array([Angle(ra + " hours").to("radian").value for ra in splus_main_tiles['RA']])

splus_main_ra = np.remainder(splus_main_ra + 2 * pi, 2 * pi)  # shift RA values
ind = splus_main_ra > pi
splus_main_ra[ind] -= 2 * pi  # scale conversion to [-180, 180]
splus_main_ra *= -1  # reverse the scale: East to the left

splus_main_dec = np.array([Angle(dec + " degrees").to("radian").value for dec in splus_main_tiles['DEC']])
# splus_main_dec[splus_main_dec > pi] = pi - splus_main_dec[splus_main_dec > pi]

ax = fig.add_subplot(111, projection="mollweide")
ax.scatter(splus_main_ra, splus_main_dec, alpha=.5)  # , color='#2ca02c')
ax.scatter(splus_main_ra[splus_main_completed], splus_main_dec[splus_main_completed], alpha=.5, color='#2ca02c')

# Final labels
plt.title("Main: %i/%i Galactic: %i/%i" % (
    len(splus_main_completed), len(splus_main_tiles), len(splus_gal_completed), len(splus_gal_tiles)))
