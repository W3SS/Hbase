#!/usr/bin/python
import sys
from random import randrange
import pprint
import requests
from requests.auth import HTTPBasicAuth
import MySQLdb
import logging
import time
import re
from xml.dom.minidom import parseString
if len(sys.argv) < 3:
    pprint.pprint("Please pass Console IP and VIP of the space device ./RestApiTest.py <VIP> <ConsoleIP>")
    sys.exit()
arg = sys.argv
logging.basicConfig(format='%(asctime)s %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p',filemode='w',filename='RestAPITest.log', level=logging.INFO)





#########################################################
##Service Insight REST APIs##
#########################################################
def ServiceInsightRestAPIsTest():
##Service Insight Exposure Analyzer##
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/exposureanalyzer',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/exposureanalyzer %s \n" %str(r.text))
    if (r.status_code == 200 and re.search('generateeolreport', r.text) and re.search('generatepbnreport',r.text) and re.search('sidevices',r.text)):
        pprint.pprint("Get Method api/juniper/serviceinsight/exposureanalyzer Rest API tested successfully")
    else:
        pprint.pprint("Get Method api/juniper/serviceinsight/exposureanalyzer Rest API test Failed")
#########################################################
ServiceInsightRestAPIsTest()
