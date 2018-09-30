import json
import matplotlib.pyplot as plt
import numpy as np

fname = "UGC3816_f814w_completeness.json"

with open(fname) as fp:
    data = json.load(fp)

count = 500.
x, y, yerr = [], [], []
xx = []
for mag in data:
    xx.append(float(mag))
    x.append(np.median(data[mag]['mag']))
    y.append(np.median(data[mag]['count']) / count)
    yerr.append(np.std(data[mag]['count']) / count)

plt.clf()
# plt.plot(x, y, '.')
plt.plot(xx, y, '.')
plt.title(fname.split('.')[0])
