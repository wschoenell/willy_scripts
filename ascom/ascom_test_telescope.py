# Methods from:
# http://www.ascom-standards.org/Help/Developer/html/Methods_T_ASCOM_DriverAccess_Telescope.htm
from win32com.client import Dispatch
T = Dispatch('ScopeSim.Telescope')
T.Connected = True

#Is the telescope parked?
if T.AtPark:
    print "Telescope Parked, Unparking."
    T.Unpark()
else:
    print "Telescope is not Parked"

#Is the telescope tracking?
if T.Tracking:
    print "Telescope Tracking..."
else:
    print "Telescope is not Tracking. Enabling track."
    if T.CanSetTracking:
        T.Tracking = True

#Find home
T.FindHome()

#Slew it RA, DEC
if T.CanSlew and not T.AtPark and T.Tracking:
    print "Telescope Can Slew"
	RA, dec = (3.0953796295106035, 7.238022260366756e-05)
	print("Slewing to", RA, dec)
	T.SlewToCoordinates(RA, dec)
	print("Slewing to 1 hour east of meridian...")
	RA, dec = T.RightAscension, T.Declination
	print("Before: ", RA, dec)
	T.SlewToCoordinates(T.SiderealTime + 1.0, 0)
	RA, dec = T.RightAscension, T.Declination
	print("After: ", RA, dec)
else:
    print "Telescope Can't Slew"

# Slew it Alt, Az
if T.CanSlewAltAz and not T.AtPark and T.Tracking:
    print "Telescope can slew AltAz"
    alt, az = T.Altitude,T.Azimuth
	print "Telescope is at Alt, Az", alt, az
	print "Slewing to Alt, Az: 88, 88"
	T.SlewtoAltAz(88, 88)
	alt, az = T.Altitude,T.Azimuth
	print "Telescope is at Alt, Az", alt, az

# Can the Telescope Slew Async?
if T.CanSetTracking:
	T.Tracking = True

if T.CanSlewAsync and not T.AtPark and T.Tracking:
	print "Telescope can slew Async"
	print T.Slewing
	T.SlewToCoordinatesAsync(RA, dec)
	print T.Slewing
