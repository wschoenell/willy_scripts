import h5py
import matplotlib.pyplot as plt
import numpy as np

# Figure 1: ALHAMBRA filter passbands
from matplotlib import cm

plt.figure(1)
plt.clf()
# Read FilterSet file
filterset = h5py.File("/Users/william/doutorado/photo_filters/Alhambra_24.hdf5")["Alhambra_24"]["1"]
max_filters = 20
# Define a mean wl vector to the filterset
filterWLs = []
filter_complete = np.array([])
sampling = np.arange(3000.0, 10000.0, 1.0)
filter = []
filter_colors = list(cm.rainbow(np.linspace(0, 1, max_filters)))

for i_filter, f in enumerate(np.unique(filterset.keys())[:max_filters]):
    filter.append(np.interp(sampling, filterset[f]['wl'], filterset[f]['transm'], left=0.0, right=0.0))
    # if i in ('J10075_1875', 'J3485_495', 'J8900_125', 'J9000_125', 'J9100_125'):
    if f in ('F_892_1', 'F_923_1', 'F_954_1', 'F_H', 'F_J', 'F_KS'):
        plt.plot(filterset[f]['wl'], filterset[f]['transm'], '--', color=filter_colors[i_filter])
    else:
        filterWLs.append(np.mean(filterset[f]['wl']))
        plt.plot(filterset[f]['wl'], filterset[f]['transm'], color=filter_colors[i_filter])
filterWLs = np.array(filterWLs)
# np.save(fits_dir+'filterWLs_50.npy', filterWLs)
plt.xlabel('$\lambda \ [\AA]$')
plt.ylabel('$T$')
plt.xlim(3000, 9871)
plt.ylim(0, 100)
ylow = .18
yupp = plt.ylim()[1]
# plt.ylim(ylow, yupp)
# plt.savefig(thesis_fig_dir + 'figure1.eps', format='eps')
