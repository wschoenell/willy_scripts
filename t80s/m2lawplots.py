import math
import matplotlib.pyplot as plt
import sys
from astropy.io import fits
from chimera.util.coord import Coord, CoordUtil
import numpy as np

data = fits.getdata(sys.argv[1])


plt.clf()
# plt.scatter(data['ALT'], data['DY'])
plt.subplot(3,3,1)
plt.scatter(data['TM1'], data['Z'])
plt.xlabel('TM1')
plt.ylabel('Z')
plt.ylim(2.04, 2.14)

plt.subplot(3,3,2)
plt.scatter(data['TM2'], data['Z'])
plt.xlabel('TM2')
plt.ylabel('Z')
plt.ylim(2.04, 2.14)


plt.subplot(3,3,3)
plt.scatter(data['TM2'] - data['TM1'], data['Z'])
plt.xlabel('TM2 - TM1')
plt.ylabel('Z')
plt.ylim(2.04, 2.14)

altR = data['ALT'] * math.pi/180
azR = data['AZ'] * math.pi/180
latR = Coord.fromDMS('-30:10:04.31').R
decR = []
haR = []
for i in range(len(altR)):
    x,y = CoordUtil.coordRotate(altR[i], latR, azR[i])
    decR.append(x)#*180/math.pi)
    haR.append(y)#*180/math.pi)

plt.subplot(3,3,4)
plt.scatter(decR, data['Y'])
plt.xlabel('dec')
plt.ylabel('Y')


plt.subplot(3,3,5)
plt.scatter(haR, data['X'])
plt.xlabel('ha')
plt.ylabel('X')


# plt.subplot(3,3,6)
# plt.scatter(haR, data['Z'] - data['TM1'])
# plt.xlabel('ha')
# plt.ylabel('Z - TM1')
# plt.ylim(2.04, 2.14)



plt.show()