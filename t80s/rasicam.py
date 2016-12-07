import requests
import sys
import xmltodict

import pymongo

client = pymongo.MongoClient()

while 1:
    data = requests.get('http://rasicam.ctio.noao.edu/RASICAMWebService/vi/')

    print '>>>', data.text
    if not 'Error Updating Status' in data.text:
        aux_dict = xmltodict.parse(data.text)
        if 'ChartData' in aux_dict.keys():
            aux_dict = aux_dict['ChartData']
            print '>>', aux_dict
            if aux_dict['ResponseType'] == 'Chart':
                client.environ.rasicam.insert_one(aux_dict)
        else:
            print 'Data is not Chart:', aux_dict
            sys.exit()
    else:
        print 'Skipped...'
