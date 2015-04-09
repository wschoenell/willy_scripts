import sys
import ephem
import astropy.units as u

__author__ = 'william'

# Calculates given ra, dec, lat, long, elev.
if len(sys.argv) < 6:
    print('Usage %s "long" "lat" elev "ra" "dec" [yr mo da hh mm ss]' % sys.argv[0])
    print('Example: python altaz_calc.py -48.522371 -27.603413 20 "18 10 46" "-36 38 56" ')
    print('Example: python altaz_calc.py -48.522371 -27.603413 20 "18 10 46" "-36 38 56" 2015 4 26 02 04 13')
    sys.exit(1)

observatory_lon, observatory_lat, observatory_elevation, ra, dec = sys.argv[1:6]
observatory = ephem.Observer()
observatory.lon = observatory_lon
observatory.lat = observatory_lat
observatory.elevation = float(observatory_elevation)

if len(sys.argv) > 6:
    observatory.date = tuple(int(i) for i in sys.argv[6:])




obj = ephem.FixedBody()
obj._ra, obj._dec = ra, dec
obj.compute(observatory)

print 'Alt: ',  (obj.alt * u.rad).to(u.deg)
print 'Az: ',  (obj.az * u.rad).to(u.deg)