#!/bin/sh
# Script to ping some address and close the dome if lost contact.
# Add to crontab to run every 20min:
# */20 * * * * /path/to/ping_test.sh ip.addres.to.ping 
# Example:
# */20 * * * * /path/to/ping_test.sh 8.8.8.8  # Google DNS server 
 
ping -q -c5 $1 > /dev/null 
# -q quiet
# -c nb of pings to perform
 
if [ $? -eq 0 ]
then
	echo "ok"
else
	chimera-dome --close
fi
