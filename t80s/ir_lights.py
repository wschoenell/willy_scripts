import sys
import requests

if sys.argv[1] not in ('0', '1'):
    print 'Usage: %s 0 or %s 1' % (sys.argv[0], sys.argv[0])
    sys.exit()

# D-LINK
for i in range(1,4):
    requests.post("http://admin:@192.168.20.11%i/nightmodecontrol.cgi" % i, data={'IRLed': sys.argv[1]})

# Axis
url="http://192.168.20.102/vapix/services"

headers = {'content-type': 'text/xml'}

if sys.argv[1] == '1':
    body = """
<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ali="http://www.axis.com/vapix/ws/light" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:soap="http://www.w3.org/2003/05/soap-envelope"><soap:Body><ali:ActivateLight xmlns="http://www.axis.com/vapix/ws/light"><LightID>led0</LightID></ali:ActivateLight></soap:Body></soap:Envelope>
"""
else:
    body = """
<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ali="http://www.axis.com/vapix/ws/light" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:soap="http://www.w3.org/2003/05/soap-envelope"><soap:Body><ali:DeactivateLight xmlns="http://www.axis.com/vapix/ws/light"><LightID>led0</LightID></ali:DeactivateLight></soap:Body></soap:Envelope>
"""

response = requests.post(url,data=body,headers=headers)
