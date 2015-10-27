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
##Service Insight EOL Reports ##        
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/eolreport-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)

    logging.info("The output of get request /api/juniper/serviceinsight/eolreport-management %s \n" %str(r.text))
    if re.search('/api/juniper/serviceinsight/eolreport-management/eolreports', r.text):
        pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports Rest API test Failed")
##Get All EOL Reports##
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/eolreport-management/eolreports',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/eolreport-management/eolreports %s \n" %str(r.text))
    if(r.status_code == 200): 
        f = open("tempfile","w")
        f.write(r.text)
        f.close()
        newcol = []
        count = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select reportName from SI_EOL_REPORT_ENTITY")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
               #  pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        f = open("tempfile","r")
        data = f.read()
        f.close()
        xmlData = []
        total = 0
        dom = parseString(data)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('reportName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1
        if(r.status_code == 200 and total == count):
            pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports Rest API test Failed")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports Rest API Failed:No EOL Reports are available")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports Rest API Failed")


##Export EOL Report##
    eolreportid=None
    eolreportidval=0
    m = re.search("(uri=\")(\/api\/juniper\/serviceinsight\/eolreport-management\/eolreports\/\w+)",data)
    if m:
        #print m.group(2)
        eolreportid = m.group(2)
    m = re.search("(uri=\")(\/api\/juniper\/serviceinsight\/eolreport-management\/eolreports\/)(\w+)",data)
    if m:
        #print m.group(3)
        eolreportidval = m.group(3)

    if eolreportid:
        r = requests.get('https://'+arg[1]+eolreportid+'/export',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #logging.info("The output of get request /api/juniper/serviceinsight/eolreport-management/eolreports/ID/export %s \n" %str(r.text))
        if r.status_code == 200:
            pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID/export Rest API tested successfully")
        elif(r.status_code == 204):
            pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID/export Rest API Failed:No EOL reports are available the specified ID or the ID is invalid")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID/export Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID/export Rest API Failed:No EOL Report Exist in Service Insight")

##TODO#ISSUE: Failed to get EOL Reports by providing the ID Need to look into it
##Get EOL Report By ID##
    if eolreportid:
        r = requests.get('https://'+arg[1]+eolreportid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        #print r.status_code
        logging.info("The output of get request /api/juniper/serviceinsight/eolreport-management/eolreports/ID %s \n" %str(r.text))
        if (r.status_code == 200):
            pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID Rest API Failed:No EOL Report Exist in Service Now")

##Delete EOL Report##
    if eolreportid:
        r = requests.delete('https://'+arg[1]+eolreportid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of delete request /api/juniper/serviceinsight/eolreport-management/eolreports/{ID} %s \n" %str(r.text))
        #print r.status_code
        if r.status_code == 204:
            pprint.pprint("EOL Reports are not available to delete from SI")
        elif(r.status_code == 200):
            #print r.status_code
            count=0
            newcol = []
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select reportName from SI_EOL_REPORT_ENTITY where id = %s",eolreportidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
                   
            if (r.status_code == 200 and count == 0):
                pprint.pprint("Delete Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID Rest API tested successfully")
            else:
                pprint.pprint("Delete Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID Rest API Failed")   
        else:
            pprint.pprint("Delete Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID Rest API Failed")   
    else:
        pprint.pprint("Delete Method /api/juniper/serviceinsight/eolreport-management/eolreports/ID Rest API Failed:No EOL Report Exist in Service Insight")   
##Get All Devices In Service Insight##
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/exposureanalyzer/sidevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/exposureanalyzer/sidevices %s \n" %str(r.text))
    if(r.status_code == 200):
        newcol = []
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select hostName from SI_DEVICE_ENTITY")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
               # pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('hostName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                    total = total + 1
        if(r.status_code == 200 and total == count):    
            pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices Rest API test Failed")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices Rest API Failed")
##Get Device Information by Device ID in Service Insight##
    sideviceid=None
    sideviceidval=0
    #print r.text 
    m = re.search("(uri=\")(\/api\/juniper\/serviceinsight\/exposureanalyzer\/sidevices\/\w+)",r.text)
    if m:
        #print m.group(2)
        sideviceid=m.group(2)
    m = re.search("(uri=\")(\/api\/juniper\/serviceinsight\/exposureanalyzer\/sidevices\/)(\w+)",r.text)
    if m:
        #print m.group(3)
        sideviceidval=m.group(3)

    if sideviceid:
        r = requests.get('https://'+arg[1]+sideviceid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/serviceinsight/exposureanalyzer/sidevices/ID %s \n" %str(r.text))
        if(r.status_code == 200):
            newcol = []
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select hostName from SI_DEVICE_ENTITY where id = %s",sideviceidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   # pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('hostName')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                        total = total + 1
            if(r.status_code == 200 and total == count):    
                pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices/ID Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices/ID Rest API test Failed")
        elif(r.status_code == 204):
            pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices/ID Rest API Failed:Invalid device ID")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices/ID Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/exposureanalyzer/sidevices/ID Rest API Failed:No devices Exist in Service Insight")

    #TODO: Generate EOL Report Rest API needs to be done : https://[host]/api/juniper/serviceinsight/exposureanalyzer/generateeolreport?queue=http://[host]/api/hornet-q/queues/jms.queue.[QueueName](HTTP method =POST)
    if sideviceid: 
        payload = "<?xml version='1.0' standalone='yes'?><queue name='QueueDevices'><durable>true</durable></queue>"
        headers = {'Content-Type': 'application/hornetq.jms.queue+xml'}
        r = requests.post('https://'+arg[1]+'/api/hornet-q/queues',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
        #print r.status_code
        #print r.text
        payload = '<eolreport><eolreportname>NewSDKReport</eolreportname><devices><device href="'+sideviceid+'"></devices><emails>test@juniper.com</emails></eolreport>'
        #print payload
        headers = {'Content-Type': 'application/vnd.juniper.serviceinsight.exposureanalyzer.generateeolreport+xml;version=1"+";charset=UTF-8'}
        #print headers
        r = requests.post('https://'+arg[1]+'/api/juniper/serviceinsight/exposureanalyzer/generateeolreport?queue=https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
        #print r.status_code
        #print r.text
        r = requests.delete('https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.status_code
        #print r.text
    else:
        pprint.pprint("Post Method /api/juniper/serviceinsight/exposureanalyzer/generateeolreport Rest API Failed:No devices Exist in Service Insight")









#########################################################
##Service Now Device Management REST APIs##
#########################################################
def ServiceNowDeviceMgmtRestAPIsTest():
##Device Management REST API##    
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-management  %s \n" %str(r.text))
    #print r.text
    if (r.status_code == 200 and re.search('devices', r.text) and re.search('exportDevice',r.text) and re.search('devicesToAdd',r.text) and re.search('exportDeviceInventory',r.text) and re.search('createOnDemandIncident',r.text) and re.search('associateAddressGroup',r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/device-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/device-management Rest API test Failed")
##Device Group Management REST API##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-group-management/deviceGroup',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-group-management/deviceGroup  %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        newcol = []
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select DeviceGroupName from AIM_DEVICE_GROUP")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('deviceGroupName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                    total = total + 1
        if(r.status_code == 200 and total == count):    
            pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API test Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API test Failed")
##Get All the Devices in Service Now##
    deviceid=None
    deviceidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        newcol = []
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select hostName from CMPManagedDeviceEntity")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
               # pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('hostName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                    total = total + 1
        if(r.status_code == 200 and total == count):    
            pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices Rest API test Failed")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices Rest API test Failed:No devices Found")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices Rest API test Failed")

    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
    #print r.text
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
    #print m.group(2)
    if m:
        deviceid = m.group(2)
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/)(\w+)",r.text)
    #print m.group(3)
    if m:
        deviceidval = m.group(3)

##Get Device Information According To Device ID##
    if deviceid:
        r = requests.get('https://'+arg[1]+deviceid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        logging.info("The output of get request /api/juniper/servicenow/device-management/devices/ID %s \n" %str(r.text))
        if(r.status_code == 200):
            newcol = []
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select hostName from CMPManagedDeviceEntity where id = %s",deviceidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   # pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('hostName')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                        total = total + 1
            if(r.status_code == 200 and total == count):    
                pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices/ID Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices/ID Rest API test Failed")
        elif(r.status_code == 204):
            pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices/ID Rest API Failed:No devices found")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices/ID Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/device-management/devices/ID Rest API Failed:No devices Exist in Service Now")

##Export All Devices##
    if deviceid:
        payload = '<export><devices><device uri="'+deviceid+'"/></devices></export>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.export+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices/exportDevice?csv={csv}',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        if(r.status_code == 200):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDevice Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDevice Rest API Failed:Invalid Device ID")
        elif(r.status_code == 400):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDevice Rest API Failed:Invalid type specified. The type parameter must excel or csv")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDevice Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDevice Rest API Failed:No Devices Exist in Service Now")

##Export Device Inventory##
    if deviceid:
        payload = '<export><devices><device uri="'+deviceid+'"/></devices></export>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.export+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices/exportDeviceInventory?csv={csv}',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        if(r.status_code == 200):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDeviceInventory Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDeviceInventory Rest API Failed:Invalid Device ID")
        elif(r.status_code == 400):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDeviceInventory Rest API Failed:Invalid type specified. The type parameter must excel or csv")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDeviceInventory Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/exportDeviceInventory Rest API Failed:No Devices Exist in Service Now")

##Add Device to Service Now##
    spacedeviceid=None
    r = requests.get('https://'+arg[1]+'/api/space/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    #print r.text
    m = re.search("(href=\")(\/api\/space\/device-management\/devices\/\w+)",r.text)
    if m:
        #print m.group(2)
        spacedeviceid=m.group(2)
    if spacedeviceid:
        payload = '<adddevices><devices><device href="'+spacedeviceid+'"/></devices></adddevices>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.adddevices+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices/add',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        if(r.status_code == 200 and re.search("Devices already added\/present in Service Now",r.text)):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/add Rest API tested successfully")
        elif(r.status_code == 500):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/add Rest API Failed:Service Now is in demo mode, specified device ID does not exist, or error while adding device to Service Now")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/add Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/add Rest API Failed:No devices Exist in Space to Add it into Service Now")

##Get All Device Groups##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-group-management/deviceGroup',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-group-management/deviceGroup  %s \n" %str(r.text))
   # print r.text
    if(r.status_code == 200):
        newcol = []
        count = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select DeviceGroupName from AIM_DEVICE_GROUP")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
               # pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('deviceGroupName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                    total = total + 1
        if(r.status_code == 200 and total == count):    
            pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API test Failed")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API test Failed:No device groups found")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API test Failed")
##Get Device Group By ID##
    devicegroupid=None
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-group-management\/deviceGroup\/\w+)",r.text)
    if m:
        #print m.group(2)
        devicegroupid=m.group(2)
    if devicegroupid:
        r = requests.get('https://'+arg[1]+devicegroupid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/device-group-management/deviceGroup/ID  %s \n" %str(r.text))
       # print r.text
        if(r.status_code == 200):    
            pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup/ID Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup/ID Rest API test Failed:Invalid device group identifier specified. No device group found")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup/ID Rest API test Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/device-group-management/deviceGroup/ID Rest API test Failed:No device Group Exist in Service Now")
##Associate A Device To A Device Group##
    if (devicegroupid and deviceid):
        payload = '<associatedevicegroup><devicegroup href="'+devicegroupid+'"/></associatedevicegroup>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.associatedevicegroup+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+deviceid+'/associateDeviceGroup',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        if(r.status_code == 200 and re.search("Device successfully associated with device group",r.text)):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/associateDeviceGroup Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/associateDeviceGroup Rest API Failed:Invalid device ID or device group ID")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/associateDeviceGroup Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/associateDeviceGroup Rest API Failed:No Devices and Device Group Exist in Service Now")


##Associate Device to a Device Group##
    if (devicegroupid and deviceid):
        payload = '<associatedevices><devices><device href="'+deviceid+'"/></devices></associatedevices>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-group-management.associatedevices+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+devicegroupid+'/associateDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        if(r.status_code == 200 and re.search("Device successfully associated with device group",r.text)):
            pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/{id}/associateDevices Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/{id}/associateDevices Rest API Failed:Invalid device ID or invalid device group ID specified")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/{id}/associateDevices Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/{id}/associateDevices Rest API Failed:No Devices and Device Group Exist in Service Now")

#TODO#ISSUE: Device Group is getting created with System domain but it should get created under global domain
##Create Device Group##
    temporgid=None
    tempdeviceid=None
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
    #print r.text
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/organization-management\/organization\/\w+)",r.text)
    if m:
        #print m.group(2)
        temporgid = m.group(2)

    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
    if m:
        #print m.group(2)
        tempdeviceid = m.group(2)
    if(temporgid and tempdeviceid):
        payload = '<createDeviceGroup><deviceGroupName>Juniper Device Group</deviceGroupName><defaultDeviceGroup>false</defaultDeviceGroup><organization href ="'+temporgid+'"/>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-group-management.createdevicegroup+xml;version=1;charset=UTF-8'} 
        newpayload = payload+'<devices><device href= "'+tempdeviceid+'"/></devices></createDeviceGroup>'
        #print newpayload
        r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup',data=newpayload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        if(r.status_code == 200):
            newcol = []
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute('select count(*) from AIM_DEVICE_GROUP WHERE DeviceGroupName = "Juniper Device Group"')
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                    #print "%s" % col
                    newcol.append(col)
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute('select domainId from AIM_DEVICE_GROUP WHERE DeviceGroupName = "Juniper Device Group"')
            rows = cur.fetchall()
            for row in rows:
                for tempcol in row:
                    #print "%s" % tempcol
                    newcol.append(tempcol)
   
            if(str(col) == '1' and str(tempcol) == '2' and r.status_code == 200 and re.search("Device group successfully created. and Devices are successfully associated with this device group",r.text)):
                pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup Rest API tested successfully")
            else:
#                db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
#                cur = db.cursor()
#                cur.execute("use snsi_db")
#                cur.execute('delete from AIM_DEVICE_GROUP WHERE DeviceGroupName = "Juniper Device Group" AND domainId = 1')
                pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup Rest API Failed:DeviceGroup is getting created under System Domain")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup Rest API Failed:Invalid organization ID, organization not found")
        elif(r.status_code == 400):
            pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup Rest API Failed:Invalid device group name is specified or Invalid organization name")
        elif(r.status_code == SN-1000):
            pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup Rest API Failed:Invalid device ID, device not found")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-group-management/deviceGroup/createDeviceGroup Rest API Failed:Create Device Group Failed beacause No devices and Organization Exist in Service Now")





##TODO##NOTWORKING##Create Ondemand Incident##
#    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
#    #print r.text
#    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
#    print m.group(2)
#
#    payload = "<?xml version='1.0' standalone='yes'?><queue name='QueueDevices'><durable>true</durable></queue>"
#   # payload = '<queue name=\'Queue4Devices\'><durable>true</durable></queue>'
#    headers = {'Content-Type': 'application/hornetq.jms.queue+xml'}
#    r = requests.post('https://'+arg[1]+'/api/hornet-q/queues',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
#    print r.status_code
#    print r.text
#
#    payload = '<ondemandincident><devices><device uri="'+m.group(2)+'"/></devices><followUpMethod>Email FullText Update</followUpMethod><caseCCList><email>biruk@juniper.net</email><email>apathodia@juniper.net</email></caseCCList><priority>Critical</priority><synopsisComments>These are my synopsis comments here</synopsisComments><customerComments>These are my customer comments here</customerComments><createCase>true</createCase></ondemandincident>'
#    #payload = '<ondemandincident><devices><device href="'+m.group(2)+'"/></devices><followUpMethod>Email FullText Update</followUpMethod><caseCCList><email>biruk@juniper.net</email><email>apathodia@juniper.net</email></caseCCList><priority>Critical</priority><synopsisComments>These are my synopsis comments here</synopsisComments><customerComments>These are my customer comments here</customerComments><createCase>true</createCase></ondemandincident>'
#    print payload
#    headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.ondemandincident+xml;version=3'}
#    print headers
#    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices/createOnDemandIncident?queue=https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    print r.status_code
#    print r.text
#    r = requests.delete('https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    print r.status_code
#    print r.text


##TODO##DONE##Install Event profile##
    eventprofileid=None
    tempdeviceid=None
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/event-profile-management/eventProfiles',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request api/juniper/servicenow/event-profile-management/eventProfiles   %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/event-profile-management\/eventProfiles\/\w+)",r.text)
        if m:
            eventprofileid = m.group(2) 
            #print eventprofileid
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
        if m:
            #print m.group(2)
            tempdeviceid=m.group(2)
    if(eventprofileid and tempdeviceid):
        payload = "<?xml version='1.0' standalone='yes'?><queue name='QueueDevices'><durable>true</durable></queue>"
        headers = {'Content-Type': 'application/hornetq.jms.queue+xml'}
        r = requests.post('https://'+arg[1]+'/api/hornet-q/queues',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
        payload = '<installeventprofile><eventprofile href="'+eventprofileid+'"/><neverStoreScriptBundle>false</neverStoreScriptBundle><removeScriptBundle>false</removeScriptBundle></installeventprofile>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.installeventprofile+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+tempdeviceid+'/installEventProfile?queue=https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        #print r.status_code
        time.sleep(400) 
        if(r.status_code == 202):
            m = re.search("(href=\")(\/api\/space\/job-management\/jobs\/)(\w+)",r.text)
            #print m.group(3)
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="build_db")
            cur = db.cursor()
            cur.execute("use build_db")
            cur.execute("select moState from JobInstance WHERE id = %s",m.group(3))
            rows = cur.fetchall()
            for row in rows:
               for tempcol in row:
                  #print "%s" % tempcol
                  newcol.append(tempcol)
            if(tempcol == "SUCCESS"):
                pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/installEventProfile Rest API tested successfully")
            else:
                pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/installEventProfile Rest API Failed")
   
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/installEventProfile Rest API Failed:Invalid address group ID specified")
        elif(r.status_code == SN-1007):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/installEventProfile Rest API Failed:Address type not Valid")
        elif(r.status_code == SN-1000):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/installEventProfile Rest API Failed:Invalid Devices")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/installEventProfile Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/installEventProfile Rest API Failed:Install Event Profile Failed:There is No Event Profiles or Devices in Service Now")

    r = requests.delete('https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)

##TODO##DONE##Uninstall Event profile##
    tempdeviceid=None
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
    #print r.text
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
    if m:
        #print m.group(2)
        tempdeviceid=m.group(2)
    if tempdeviceid:
        payload = "<?xml version='1.0' standalone='yes'?><queue name='QueueDevices'><durable>true</durable></queue>"
        headers = {'Content-Type': 'application/hornetq.jms.queue+xml'}
        r = requests.post('https://'+arg[1]+'/api/hornet-q/queues',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.installeventprofile+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+m.group(2)+'/uninstallEventProfile?queue=https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        #print r.status_code
        time.sleep(400)
        if(r.status_code == 202):
            m = re.search("(href=\")(\/api\/space\/job-management\/jobs\/)(\w+)",r.text)
            #print m.group(3)
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="build_db")
            cur = db.cursor()
            cur.execute("use build_db")
            cur.execute("select moState from JobInstance WHERE id = %s",m.group(3))
            rows = cur.fetchall()
            for row in rows:
               for tempcol in row:
                  #print "%s" % tempcol
                  newcol.append(tempcol)
            if(tempcol == "SUCCESS"):
                pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/uninstallEventProfile Rest API tested successfully")
            else:
                pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/uninstallEventProfile Rest API Failed")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/uninstallEventProfile Rest API Failed:Invalid address group ID specified")
        elif(r.status_code == SN-1007):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/uninstallEventProfile Rest API Failed:Address type not Valid")
        elif(r.status_code == SN-1000):
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/uninstallEventProfile Rest API Failed:Invalid Devices")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/uninstallEventProfile Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/{id}/uninstallEventProfile Rest API Failed:Uninstall Event Profile Failed:No Device Exist in Service Now")

    r = requests.delete('https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
##TODO##NOTWORKING##Request RMA Incident##
#    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
#    #print r.text
#    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
#    payload = "<?xml version='1.0' standalone='yes'?><queue name='QueueDevices'><durable>true</durable></queue>"
#   # payload = '<queue name=\'Queue4Devices\'><durable>true</durable></queue>'
#    headers = {'Content-Type': 'application/hornetq.jms.queue+xml'}
#    r = requests.post('https://'+arg[1]+'/api/hornet-q/queues',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
#    print r.status_code
#    print r.text
#    print m.group(2)
#    payload = '<requestrmaincident><followUpMethod>EmailFullTextUpdate</followUpMethod><caseCCList><email>biruk@system.net</email><email>apathodia@system.net</email></caseCCList><priority>Critical</priority><synopsisComments>These are my synopsis comments here</synopsisComments><customerComments>These are my customer comments here</customerComments><createCase>true</createCase><requestRMAParts>Routing Engine 0 Model Number: RE-400-768-S Routing Engine 0 Part Number: 740-021833 (REV 02) Routing Engine 0 SerialNumber: 9009042143 Routing Engine 0 Description: RE-400 for M10i, M7i with 768 MB Mem spare </requestRMAParts></requestrmaincident>'
#    headers = {'Content-Type': 'application/vnd.juniper.servicenow.device-management.requestrmaincident+xml;version=3'}
#    r = requests.post('https://'+arg[1]+m.group(2)+'/requestRMAIncident?queue=https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    print r.text
#    print r.status_code
##    time.sleep(600)
#    r = requests.delete('https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    print r.status_code
#    print r.text


##TODO##NOTWORKING##Associate Devices to Address Group##
#    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
#    print r.text
#    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
#    print m.group(2)
#    deviceid = m.group(2)
#    print deviceid
#    payload = '<devices><device href="'+deviceid+'"><addressType>2</addressType></device></devices>'
#    print payload
#    headers = {'Content-Type': 'application/vnd.juniper.servicenow.address-group-management.devices+xml;version=1;charset=UTF-8'}
#    print headers
#    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices/associateAddressGroup',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    print r.text
#    if(r.status_code == 200 and re.search("Devices successfully associated with address group",r.text)):
#        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/associateAddressGroup Rest API tested successfully")
#    else:
#        pprint.pprint("Post Method /api/juniper/servicenow/device-management/devices/associateAddressGroup Rest API Failed")
##Delete Device Group##
#    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-group-management/deviceGroup',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    logging.info("The output of get request /api/juniper/servicenow/device-group-management/deviceGroup  %s \n" %str(r.text))
#    #print r.text
#    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-group-management\/deviceGroup\/\w+)",r.text)
#    #print m.group(2) 
#    r = requests.delete('https://'+arg[1]+m.group(2),auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    if(r.status_code == 200 and re.search("Device group successfully deleted",r.text)):
#        pprint.pprint("Delete Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API tested successfully")
#    else:
#        pprint.pprint("Delete Method /api/juniper/servicenow/device-group-management/deviceGroup Rest API Failed")
###Delete Device by Device ID##
#    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
#    #print r.text
#    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
#    #print m.group(2)
#    deviceid = m.group(2)
#    r = requests.delete('https://'+arg[1]+deviceid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    if(r.status_code == 200 and re.search("Device successfully deleted",r.text)):
#        pprint.pprint("Delete Method /api/juniper/servicenow/device-management/devices Rest API tested successfully")
#    else:
#        pprint.pprint("Delete Method /api/juniper/servicenow/device-management/devices Rest API Failed")











#########################################################
##Service Now Event Profile Management REST APIs##
#########################################################
def ServiceNowEventProfileMgmtRestAPIsTest():
##Event Profile Management##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/event-profile-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request api/juniper/servicenow/event-profile-management   %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("\/api\/juniper\/servicenow\/event-profile-management\/eventProfiles",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management Rest API Failed")
##Get All Event Profiles##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/event-profile-management/eventProfiles',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request api/juniper/servicenow/event-profile-management/eventProfiles   %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/event-profile-management\/eventProfiles\/\w+)",r.text)
        if m:
            eventprofileid = m.group(2) 
        newcol = []
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select profile_name from AIM_AIS_PROFILE")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('profileName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                    total = total + 1
        if(total == count and r.status_code == 200 and re.search("\/api\/juniper\/servicenow\/event-profile-management\/eventProfiles",r.text)):
            pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles Rest API test Failed")

    elif(r.status_code == 404):
        pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles Rest API Failed:Invalid device group ID specified")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles Rest API Failed")
##Get All Event Profiles by Profile ID##
    #print eventprofileid
    m = re.search("(\/api\/juniper\/servicenow\/event-profile-management\/eventProfiles\/)(\w+)",eventprofileid)
    #print m.group(2)
    if m:
        eventprofileidval=m.group(2)
    if eventprofileid:
        r = requests.get('https://'+arg[1]+eventprofileid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request api/juniper/servicenow/event-profile-management/eventProfiles/{id}  %s \n" %str(r.text))
       # print r.text
        if(r.status_code == 200):
            newcol = []
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select profile_name from AIM_AIS_PROFILE WHERE id = %s",eventprofileidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('profileName')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                        total = total + 1
            if(total == count and r.status_code == 200):
                pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API test Failed")

        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API Failed:Invalid device group ID specified")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API Failed:No Event Profiles Exist in Service Now")

##TODO##NotWorking##Internal Server Error##Delete Event Profile by Event Profile ID##
#    if eventprofileid:
#        r = requests.delete('https://'+arg[1]+eventprofileid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#        logging.info("The output of delete request api/juniper/servicenow/event-profile-management/eventProfiles/{id}  %s \n" %str(r.text))
#        print r.text
#        print r.status_code
#        if(r.status_code == 200):
#            newcol = []
#            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
#            cur = db.cursor()
#            cur.execute("use snsi_db")
#            cur.execute("select profile_name from AIM_AIS_PROFILE WHERE id = %s",eventprofileidval)
#            rows = cur.fetchall()
#            for row in rows:
#                for col in row:
#                   # print "%s" % col
#                    #pprint.pprint(col)
#                    newcol.append(col)
#                    count = len(rows)
#                    print count
#            if(count == 0 and r.status_code == 200 and re.search("Event Profile successfully deleted",r.text)):
#                pprint.pprint("Delete Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API tested successfully")
#            else:
#                pprint.pprint("Delete Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API test Failed")
#        elif(r.status_code == 404):
#            pprint.pprint("Delete Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API Failed:No event profile with the specified identifier was found")
#        else:
#            pprint.pprint("Delete Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API Failed")
#    else:
#        pprint.pprint("Delete Method /api/juniper/servicenow/event-profile-management/eventProfiles/{ID} Rest API Failed:No Event Profiles Exist in Service Now")

##TODO##DONE##Install Event Profile On Devices##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/event-profile-management/eventProfiles',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request api/juniper/servicenow/event-profile-management/eventProfiles   %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/event-profile-management\/eventProfiles\/\w+)",r.text)
        if m:
            eventprofileid = m.group(2) 
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-management/devices  %s \n" %str(r.text))
    #print r.text
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
    #print m.group(2)
    payload = "<?xml version='1.0' standalone='yes'?><queue name='QueueDevices'><durable>true</durable></queue>"
    headers = {'Content-Type': 'application/hornetq.jms.queue+xml'}
    r = requests.post('https://'+arg[1]+'/api/hornet-q/queues',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
    payload = '<installeventprofile><devices><device href="'+m.group(2)+'"/></devices><neverStoreScriptBundle>false</neverStoreScriptBundle><removeScriptBundle>false</removeScriptBundle></installeventprofile>'
    headers = {'Content-Type': 'application/vnd.juniper.servicenow.event-profile-management.installeventprofile+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+eventprofileid+'/installEventProfile?queue=https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    #print r.text
    #print r.status_code
    time.sleep(400) 
    if(r.status_code == 202):
        m = re.search("(href=\")(\/api\/space\/job-management\/jobs\/)(\w+)",r.text)
        #print m.group(3)
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="build_db")
        cur = db.cursor()
        cur.execute("use build_db")
        cur.execute("select moState from JobInstance WHERE id = %s",m.group(3))
        rows = cur.fetchall()
        for row in rows:
           for tempcol in row:
              #print "%s" % tempcol
              newcol.append(tempcol)
        if(tempcol == "SUCCESS"):
            pprint.pprint("Post Method /api/juniper/servicenow/event-profile-management/eventProfiles/{id}/installEventProfile Rest API tested successfully")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/event-profile-management/eventProfiles/{id}/installEventProfile Rest API Failed")
    elif(r.status_code == 404):
        pprint.pprint("Post Method /api/juniper/servicenow/event-profile-management/eventProfiles/{id}/installEventProfile Rest API Failed:Invalid device ID or the event profile does not exist")
    elif(r.status_code == 500):
        pprint.pprint("Post Method /api/juniper/servicenow/event-profile-management/eventProfiles/{id}/installEventProfile Rest API Failed:Device not associated with any device group")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/event-profile-management/eventProfiles/{id}/installEventProfile Rest API Failed")
    r = requests.delete('https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)






#########################################################
##Service Now Incident Management REST APIs##
#########################################################
def ServiceNowIncidentMgmtRestAPIsTest():
##Incident Management##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/incident-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/incident-management %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search('\/api\/juniper\/servicenow\/incident-management\/incidents',r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/incident-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/incident-management Rest API Failed")
##Get All Incidents in Service Now##
    incidentid=None
    incidentidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/incident-management/incidents',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/incident-management/incidents %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/incident-management\/incidents\/\w+)",r.text)
        #print m.group(2)
        if m:
            incidentid = m.group(2)
    if(incidentid and r.status_code == 200 and re.search('\/api\/juniper\/servicenow\/incident-management\/incidents',r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incidents Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incidents Rest API Failed")
##Get Incident by Incident ID##
    if incidentid:
        m = re.search("(\/api\/juniper\/servicenow\/incident-management\/incidents\/)(\w+)",incidentid)
        incidentidval = m.group(2)
        #print incidentidval 
        r = requests.get('https://'+arg[1]+incidentid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/incident-management/incident/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select prbIdentifier from IncidentEntity WHERE id = %s",incidentidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   #  pprint.pprint(col)
                     newcol.append(col)
                     count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('prbIdentifier')[x].firstChild.data)
            for y in range(count):
                for z in range(count): 
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(count == total and r.status_code == 200):
                pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incidents/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incidents/{ID} Rest API test Failed")

        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incidents/{ID} Rest API Failed:Invalid incident ID, incident not found")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incidents/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incidents/{ID} Rest API Failed:No Incidents Exist in Service Now")

##TODO##NOIDEAABOUTCUSTOMERTRACKINGNUMBER##Get Incident By Customer Tracking Number##
#    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/incident-management/incidents?filter=(customerTrackingNumber eq \''+abcdef1234+'\')',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    logging.info("The output of get request /api/juniper/servicenow/incident-management/incident/customerTrackingNumber %s \n" %str(r.text))
#    print r.text
##Export JMB##
    if incidentid:
        r = requests.get('https://'+arg[1]+incidentid+'/exportJMB?type=xml&content=original',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/incident-management/incident/exportJMB %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("host-event-ID",r.text)):
            pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incident/exportJMB Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incident/exportJMB Rest API Failed:Invalid incident ID, incident not found")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incident/exportJMB Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/incident-management/incident/exportJMB Rest API Failed:No Incident Exist in Service Now")
##TODO##NOTWORKING##Save a Case##
#    payload = '<incident><siteId>1-4XUVRM</siteId><caseCreationUserName>test@nam.com</caseCreationUserName><caseCreationPassword>anVuaXBlcg==</caseCreationPassword><priority>Critical</priority><followUpMethod>Email Full Text Update</followUpMethod><synopsisComments>These are my synopsis comments here</synopsisComments><customerComments>These are my customer comments here</customerComments><caseCCList><email>biruk@mycompany.com</email><email>apathodia@mycompany.com</email></caseCCList><addressGroup href="/api/juniper/servicenow/address-group-management/addressGroups/11501570"/><coreFiles><coreFile><fileName>/var/tmp/snmpd.core-tarball.1.tgz</filename></coreFile></coreFiles><deleteCoreFiles>true</deleteCoreFiles></incident>'
#    print incidentid
#    payload = '<incident><siteId>1-4XUVRM</siteId><priority>Critical</priority><followUpMethod>Email Full Text Update</followUpMethod><synopsisComments>These are my synopsis comments here</synopsisComments><customerComments>These are my customer comments here</customerComments></incident>'
#    headers = {'Content-Type': 'application/vnd.juniper.servicenow.incident-management.incident+xml;version=3;charset=UTF-8'}
#    if incidentid:
#        r = requests.post('https://'+arg[1]+incidentid+'/saveCase',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#        print r.text
#        print r.status_code 
###TODO##NOTWORKING##Submit a Case##
#    payload = '<incident><siteId>1-4XUVRM</siteId><priority>Critical</priority><followUpMethod>Email Full Text Update</followUpMethod><synopsisComments>These are my synopsis comments here</synopsisComments><customerComments>These are my customer comments here</customerComments></incident>'
#    headers = {'Content-Type': 'application/vnd.juniper.servicenow.incident-management.incident+xml;version=3;charset=UTF-8'}
#    if incidentid:
#        r = requests.post('https://'+arg[1]+incidentid+'/submitCase',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#        print r.text
#        print r.status_code 

##Delete Incident By Incident ID##
    if incidentid:
        r = requests.delete('https://'+arg[1]+incidentid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of delete request /api/juniper/servicenow/incident-management/incident/{ID} %s \n" %str(r.text))
#        print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select prbIdentifier from IncidentEntity WHERE id = %s",incidentidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   #  pprint.pprint(col)
                     newcol.append(col)
                     count = len(rows)

            if(r.status_code == 200 and count == 0 and re.search("Incident successfully deleted",r.text)):
                pprint.pprint("Delete Method /api/juniper/servicenow/incident-management/incident/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Delete Method /api/juniper/servicenow/incident-management/incident/{ID} Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("Delete Method /api/juniper/servicenow/incident-management/incident/{ID} Rest API Failed:Invalid incident ID, incident not found")
        else:
            pprint.pprint("Delete Method /api/juniper/servicenow/incident-management/incident/{ID} Rest API Failed")
    else:
        pprint.pprint("Delete Method /api/juniper/servicenow/incident-management/incident/{ID} Rest API Failed:No Incident Exist in Service Now")








####################################################################
##Service Now Script Bundle Management REST APIs##
####################################################################
def ServiceNowScriptBundleMgmtRestAPIsTest():
##Script Bundle Management##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/scriptbundle-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/scriptbundle-management  %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/scriptbundle-management/scriptbundles",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management Rest API Failed")
##Get All Script Bundles##
    scriptbundleid=None
    scriptbundleidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/scriptbundle-management/scriptbundles',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/scriptbundle-management/scriptbundles  %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/scriptbundle-management\/scriptbundles\/\w+)",r.text)
        #print m.group(2)
        if m:
            scriptbundleid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/scriptbundle-management\/scriptbundles\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            scriptbundleidval = m.group(3)

        newcol = []
        count = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select scriptBundleName from AIScriptBundleEntity")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
               #  pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1
        if(r.status_code == 200 and total == count):
            pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles Rest API test Failed")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles Rest API Failed:No Script Bundle Exists")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles Rest API Failed")
##Get Script Bundle Info by Bundle ID##
    if scriptbundleid:
        r = requests.get('https://'+arg[1]+scriptbundleid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID}  %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select scriptBundleName from AIScriptBundleEntity WHERE id = %s",scriptbundleidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID} Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID} Rest API Failed:Invalid ScriptBundle ID ")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID} Rest API Failed:No Script Bundle Exist in Service Now")

##Get All Events In A Script Bundle##
    if scriptbundleid:
        r = requests.get('https://'+arg[1]+scriptbundleid+'/bundleEvents',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID}/bundleEvents  %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select events_id from AIScriptBundleEntity_AIM_AIS_BUNDLE_EVENT WHERE AIScriptBundleEntity_id = %s",scriptbundleidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('id')[x].firstChild.data)
            total = len(xmlData)
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID}/bundleEvents Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID}/bundleEvents Rest API test Failed")

        elif(r.status_code == 500):
            pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID}/bundleEvents Rest API Failed: No Event is available in the script bundle ")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID}/bundleEvents Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/scriptbundle-management/scriptbundles/{ID}/bundleEvents Rest API Failed:No Script Bundle Exist in Service Now")

##TODO##NOTWORKING##Create an Event Profile##There is some issue in passing parameters to post request because there is no relation b/w autosubmit policy and create event profile
#    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    #print r.text 
#    m = re.search("(href=\")(\/api\/juniper\/servicenow\/autosubmit-policy-management\/autosubmitpolicies\/\w+)",r.text)
#    print m.group(2)
#    payload = '<createeventprofile><profileName> testProfile </profileName><profileDescription> testProfile </profileDescription><events><event><id>95608</id><priority>Low</priority></event></events></createeventprofile>'
#    headers = {'Content-Type': 'application/vnd.juniper.servicenow.incident-management.incident+xml;version=3;charset=UTF-8'}
#    r = requests.post('https://'+arg[1]+m.group(2)+'/createEventProfile',data=payload,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#    print r.text
#    print r.status_code 










#############################################################
##ServiceNow TechSupport Case Management##
#############################################################
def ServiceNowTechnicalSupportCaseMgmtRestAPIsTest():
##ServiceNow TechSupport Case Management##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/case-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/case-management/cases %s \n" %str(r.text))
    #print r.text 
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/case-management/cases",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/case-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/case-management Rest API Failed")
##Get All Tech Support Cases##
    techsupportcaseid=None
    techsupportcaseidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/case-management/cases',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/case-management/cases %s \n" %r.text)
    #print r.text 
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/case-management\/cases\/\w+)",r.text)
    #print m.group(2)
    if m:
        techsupportcaseid = m.group(2)
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/case-management\/cases\/)(\w+)",r.text)
    #print m.group(3)
    if m:
        techsupportcaseidval = m.group(3)
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/case-management/cases",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases Rest API tested successfully")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases Rest API Failed: Tech Support Cases Not Found")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases Rest API Failed")
##Get Tech Support Case Info by Case ID##
    if techsupportcaseid:
        r = requests.get('https://'+arg[1]+techsupportcaseid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/case-management/cases/{ID} %s \n" %r.text)
        #print r.text 
        if(r.status_code == 200):
            newcol = []
            count = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select caseId from JSSCaseEntity WHERE id = %s", techsupportcaseidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   #  pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('caseId')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases/{ID} Rest API test Failed")

        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases/{ID} Rest API Failed: Invalid CaseID Case Not Found")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/case-management/cases/{ID} Rest API Failed:No Tech Support Cases Exist in Service Now")
##Update a Case by Case ID##
    if techsupportcaseid:
        payload = '<case><notes>This is Service Now Case</notes></case>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.case-management.case+xml;version=2;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+techsupportcaseid+'/updateCase',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of post request /api/juniper/servicenow/case-management/cases/{ID}/updateCase %s \n" %r.text)
        #print r.text
        if(r.status_code == 200 and re.search("Case updated successfully",r.text)):
            pprint.pprint("Post Method /api/juniper/servicenow/case-management/cases/{ID}/updateCase Rest API tested successfully")
        elif(r.status_code == 500):
            pprint.pprint("Post Method /api/juniper/servicenow/case-management/cases/{ID}/updateCase Rest API Failed: ServiceNow cannot connect to JSS")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/case-management/cases/{ID}/updateCase Rest API Failed: Invalid CaseID Case Not Found")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/case-management/cases/{ID}/updateCase Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/case-management/cases/{ID}/updateCase Rest API Failed:No Tech Support Cases Exist in Service Now")






#############################################################
##Service Now End Customer Case Management##
#############################################################
def ServiceNowEndCustomerCaseMgmtRestAPIsTest():
##Service Now End Customer Case Management##
    endcustomercaseid=None
    endcustomercaseid=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/endcustomer-case-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/endcustomer-case-management %s \n" %r.text)
    #print r.text 
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/endcustomer-case-management/cases",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases Rest API Failed")
##Get All End Customer Cases##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/endcustomer-case-management/cases',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/endcustomer-case-management/cases %s \n" %r.text)
   # print r.text
    if(r.status_code == 200): 
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/endcustomer-case-management\/cases\/\w+)",r.text)
        #print m.group(2)
        if m:
            endcustomercaseid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/endcustomer-case-management\/cases\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            endcustomercaseidval = m.group(3)
        newcol = []
        count = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select caseId from AIM_EndCustomerCaseEntity WHERE caseId IS NOT NULL")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
               # pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('caseId')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1
        if(r.status_code == 200 and total == count and re.search("/api/juniper/servicenow/endcustomer-case-management/cases",r.text)):
            pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases Rest API tested successfully")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases Rest API Failed: No End Customer cases Found")
    elif(r.status_code == 403):
        pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases Rest API Failed: ServiceNow is not running in Mode")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases Rest API Failed")

##Get End Customer Case Info by Case ID##  
    if endcustomercaseid: 
        r = requests.get('https://'+arg[1]+endcustomercaseid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/endcustomer-case-management/cases/{ID} %s \n" %r.text)
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select caseId from AIM_EndCustomerCaseEntity WHERE id = %s",endcustomercaseidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   # pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('caseId')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases/{ID} Rest API test Failed")
  
        elif(r.status_code == 403):
            pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases/{ID} Rest API Failed:ServiceNow is not running in Mode")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases/{ID} Rest API Failed: Invalid Case ID Specified, no End Customer cases found")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/endcustomer-case-management/cases/{ID} Rest API Failed:End Customer Cases does not Exist in Service Now")






#########################################################
##Service Now Auto Submit Policy Management##
#########################################################
def ServiceNowAutoSubmitPolicyMgmtRestAPIsTest():
##Service Now Auto Submit Policy Management##
    autosubmitpolicyid=None
    autosubmitpolicyidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies %s \n" %str(r.text))
    #print r.text
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/autosubmit-policy-management\/autosubmitpolicies\/\w+)",r.text)
    #print m.group(2)
    if m:
        autosubmitpolicyid = m.group(2)
    m = re.search("(href=\")(\/api\/juniper\/servicenow\/autosubmit-policy-management\/autosubmitpolicies\/)(\w+)",r.text)
    #print m.group(3)
    if m:
        autosubmitpolicyidval = m.group(3)
 
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies Rest API Failed")
##Get All Auto Submit Policies in Service Now##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        newcol = []
        count = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select policy_name from AUTO_CASE_POLICY")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
               # pprint.pprint(col)
                newcol.append(col)
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1

        if(r.status_code == 200 and total == count and re.search("/api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies",r.text)):
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies Rest API tested successfully")     
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies Rest API test Failed")     
           
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies Rest API Failed:No Autosubmit Policy Found on Service Now")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies Rest API Failed")
##Get Auto Submit Policy Info by Policy ID##
    if autosubmitpolicyid:
        r = requests.get('https://'+arg[1]+autosubmitpolicyid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select policy_name from AUTO_CASE_POLICY")
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   # pprint.pprint(col)
                    newcol.append(col)
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1

            if(r.status_code == 200 and total == count and re.search("/api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies",r.text)):
                pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID} Rest API test Failed")

        elif(r.status_code == 204):
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID} Rest API Failed:Invalid auto submit policy ID specified")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID} Rest API Failed:No Auto Submit Policy Exist in Service Now")

##Get Devices Associated With an Auto Submit Policy##
    if autosubmitpolicyid:
        r = requests.get('https://'+arg[1]+autosubmitpolicyid+'/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/devices %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
            #print m.group(2)
            deviceassociatedwithautosubmitpolicy = m.group(2)

            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select device_id from AUTO_CASE_POLICY_DEVICE")
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            for z in range(count):
                if(re.search("/api/juniper/servicenow/device-management/devices/"+re.escape(newcol[z]),r.text)):
                    total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/devices Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/devices Rest API test Failed")

        elif(r.status_code == 500):
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/devices Rest API Failed:No devices are associated with the specified auto submit policy")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/devices Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/devices Rest API Failed:Auto Submit policy does not exist in Service Now")

##Get Events Associated With an Auto Submit Policy##
    if autosubmitpolicyid:
        r = requests.get('https://'+arg[1]+autosubmitpolicyid+'/events',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/events %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select event_id from AUTO_CASE_POLICY_EVENT WHERE policy_id = %s",autosubmitpolicyidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            total = len(xmlData)
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/events Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/events Rest API testFailed")
        elif(r.status_code == 500):
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/events Rest API Failed:No events are associated with the specified auto submit policy.")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/events Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/events Rest API Failed:Auto Submit Policy Does not exist in Service Now")

##Assign An Auto Submit Policy To A Device##  
    if autosubmitpolicyid:
        payload = '<associateDevices><devices><device href=\"'+deviceassociatedwithautosubmitpolicy+'\"/></devices></associateDevices>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.autosubmit-policy-management.associatedevices+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+autosubmitpolicyid+'/associateDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
        logging.info("The output of post request /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/associateDevices %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("Device associated successfully to auto submit policy",r.text)):
            pprint.pprint("Post Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/associateDevices Rest API tested successfully")
        elif(r.status_code == 400):
            pprint.pprint("Post Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/associateDevices Rest API Failed:Invalid Request")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/associateDevices Rest API Failed:Invalid Device ID specified")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/associateDevices Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/autosubmit-policy-management/autosubmitpolicies/{ID}/associateDevices Rest API Failed")





#########################################################
##Service Now Device Snapshot Management##
#########################################################
def ServiceNowDeviceSnapshotMgmtRestAPIsTest():
##Device Snapshot Management##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/devicesnapshot-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/devicesnapshot-management %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/devicesnapshot-management/devicesnapshots",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management Rest API Failed")
##Get All Device Snapshots in Service Now##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/devicesnapshot-management/devicesnapshots',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/devicesnapshot-management/devicesnapshots %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/devicesnapshot-management\/devicesnapshots\/\w+)",r.text)
        #print m.group(2)
        devicesnapshotid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/devicesnapshot-management\/devicesnapshots\/)(\w+)",r.text)
        #print m.group(3)
        devicesnapshotidval = m.group(3)
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select hostName from IncidentEntity WHERE id = %s",devicesnapshotidval)
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(str(col))
                count = len(rows)
        r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/devicesnapshot-management/devicesnapshots?filter=(hostName eq \'' +col+'\')',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/devicesnapshot-management/devicesnapshots %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("/api/juniper/servicenow/devicesnapshot-management/devicesnapshots/"+re.escape(devicesnapshotidval),r.text)):
            pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots Rest API tested successfully")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots Rest API Failed:No events are associated with the specified auto submit policy")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots Rest API Failed")
##Get Device Snapshot Info by Device ID##
    if devicesnapshotid:
        r = requests.get('https://'+arg[1]+devicesnapshotid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/devicesnapshot-management/devicesnapshot/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select hostName from IncidentEntity WHERE id = %s",devicesnapshotidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('hostName')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API Failed")
	
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API Failed:Invalid snapshot ID specified")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API Failed:Device Snapshot does Not exist on ServiceNow ")

##Export Device Snapshot Information by Device ID##
    if devicesnapshotid:
        r = requests.get('https://'+arg[1]+devicesnapshotid+'/export',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/devicesnapshot-management/devicesnapshot/{ID}/export %s \n" %str(r.text))
        if(r.status_code == 200):
            pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID}/export Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID}/export Rest API Failed:Invalid device snapshot ID specified")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID}/export Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID}/export Rest API Failed")

##Delete Device Snapshot by Device Snapshot ID##
    if devicesnapshotid:
        r = requests.delete('https://'+arg[1]+devicesnapshotid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of Delete request /api/juniper/servicenow/devicesnapshot-management/devicesnapshot/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("Device Snapshot deleted successfully",r.text)):
            pprint.pprint("Delete Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Delete Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API Failed:Invalid JMB ID specified")
        else:
            pprint.pprint("Delete Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API Failed")
    else:
        pprint.pprint("Delete Method /api/juniper/servicenow/devicesnapshot-management/devicesnapshots/{ID} Rest API Failed:Device Snapshots does not exist on Service Now")






#########################################################
##Service Now Organization Management##
#########################################################
def ServiceNowOrganizationMgmtRestAPIsTest():
##Service Now Organization Management ##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/organization-management %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/organization-management/organization",r.text) and  re.search("/api/juniper/servicenow/organization-management/sites",r.text) and re.search("/api/juniper/servicenow/organization-management/jmbfilterlevels",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management Rest API Failed")

##Get All Organizations in Service Now##
    organizationid=None
    organizationidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management/organization',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/organization-management %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/organization-management\/organization\/\w+)",r.text)
        #print m.group(2)
        if m:
            organizationid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/organization-management\/organization\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            organizationidval = m.group(3)
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select siteName from ORGANIZATION_CONFIGURATION")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(str(col))
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('siteName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1
        if(r.status_code == 200 and total == count):
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization Rest API test Failed")
     
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization Rest API Failed:No organizations found in Service Now")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization Rest API Failed")

##Get An Organization Through its Site Name##
    if organizationid:
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select siteName from ORGANIZATION_CONFIGURATION where id = %s",organizationidval)
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(str(col))
                count = len(rows)
        r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management/organization?filter=(siteName eq \'' +col+'\')',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/organization-management/organization %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("/api/juniper/servicenow/organization-management/organization/"+re.escape(organizationidval),r.text)):
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/ Rest API tested successfully")
        elif(r.status_code == 204):
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/ Rest API Failed:No organizations found in Service Now")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/ Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/ Rest API Failed:No organizations found in Service Now")

##Get Organization Info by ID##
    if organizationid:
        r = requests.get('https://'+arg[1]+organizationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/organization-management/organization/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select siteName from ORGANIZATION_CONFIGURATION where id = %s",organizationidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('siteName')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API test Failed")

        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API Failed:Invalid organization ID")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API Failed")
    else:
            pprint.pprint("Get Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API Failed: organization does not Exist on Service Now")

##Get Sites Info##
    payload = '<organization><userName>test@nam.com</userName><password>anVuaXBlcg==</password></organization>'
    headers = {'Content-Type': 'application/vnd.juniper.servicenow.organization-management.organization+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/organization-management/sites',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
    logging.info("The output of post request /api/juniper/servicenow/organization-management/sites %s \n" %str(r.text))
    #print r.text

    if(r.status_code == 200 and re.search("/api/juniper/servicenow/organization-management/sites",r.text)):
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/sites Rest API tested successfully")
    elif(r.status_code == 400):
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/sites Rest API Failed:No user name specified in the input or User name is too long or No password specified in the input or Password is too long")
    elif(r.status_code == 204):
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/sites Rest API Failed:No Sites Found")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/sites Rest API Failed")

    
##Get JMB Filter Levels Info##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management/jmbfilterlevels',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/organization-management/jmbfilterlevels %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("Do not send,Send all information except configuration,Send all information with IP addresses overwritten,Send all information,Only send list of features used",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management/jmbfilterlevels Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management/jmbfilterlevels Rest API Failed")

##Get Case Submission Values##   
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management/casesubmissionvalues',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/organization-management/casesubmissionvalues %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("Real Cases,Test Cases",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management/casesubmissionvalues Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/organization-management/casesubmissionvalues Rest API Failed")

#TODO#ISSUE: New Organization is getting created with System domain but it should get created under global domain
##Add Organization##
    siteid=None
    if organizationid:
        r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management/organization',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/organization-management %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select siteIdentifier from ORGANIZATION_CONFIGURATION")
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    siteid = col
                   
    payload = '<organization><userName>test@nam.com</userName><password>anVuaXBlcg==</password></organization>'
    headers = {'Content-Type': 'application/vnd.juniper.servicenow.organization-management.organization+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/organization-management/sites',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
    logging.info("The output of post request /api/juniper/servicenow/organization-management/sites %s \n" %str(r.text))
    #print r.text
    sitecount = 0
    sitename=None
    import xml.etree.ElementTree as ET
    f = open("tempfile","w")
    f.write(r.text)
    f.close()
    tree = ET.parse("tempfile")
    for elem in tree.findall(".//siteId"):
         sitecount += 1
    xmlData = []
    total = 0
    dom = parseString(r.text)
    for x in range(sitecount):
        xmlData.append(dom.getElementsByTagName('siteId')[x].firstChild.data)
    #print xmlData
    if siteid:
        for sitename in xmlData:
            if(siteid != sitename):
                sitename=sitename
    else:
        #print sitecount
        sitename=xmlData[randrange(sitecount)]      
    #print sitename         
    payload = '<organization><siteName>NewRESTOrg</siteName><siteIdentifier>'+sitename+'</siteIdentifier><userName>test@nam.com</userName><password>anVuaXBlcg==</password><jmbFilterValue>Do not send</jmbFilterValue><submit-case-as>Real Cases</submit-case-as></organization>'
    #print payload
    headers = {'Content-Type': 'application/vnd.juniper.servicenow.organization-management.organization+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/organization-management/addorganization',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
    logging.info("The output of post request /api/juniper/servicenow/organization-management/addorganization %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select domainId from ORGANIZATION_CONFIGURATION where siteName = 'NewRESTOrg'")
        rows = cur.fetchall()
        for row in rows:
            for col in row:
                #print "%s" % col
                #pprint.pprint(col)
                newcol.append(str(col))
                count = len(rows)
        
            if(r.status_code == 200 and col == 2 and re.search("Organization created successfully. Successful Registration:  Service Now Successfully Connected to Juniper Technical Support",r.text)):
                pprint.pprint("Post Method /api/juniper/servicenow/organization-management/addorganization Rest API tested successfully")
            else:
                pprint.pprint("Post Method /api/juniper/servicenow/organization-management/addorganization Rest API test Failed:New Organization is created under SYSTEM Domain")

    elif(r.status_code == 404):
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/addorganization Rest API Failed:User name is too long or Site name is too long or Password is too long or jmbFilterValue contains an invalid value")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/addorganization Rest API Failed")

##Modify Organization By ID##
    if organizationid:
        payload = '<organization><siteName>modifedOrg</siteName></organization>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.organization-management.organization+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+organizationid+'/modifyorganization',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
        logging.info("The output of post request /api/juniper/servicenow/organization-management/modifyorganization %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("Organization updated successfully Successful Registration:  Service Now Successfully Connected to Juniper Technical Support.",r.text)):
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/modifyorganization Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/modifyorganization Rest API Failed:User name is too long or Site name is too long or Password is too long or jmbFilterValue contains an invalid value")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/modifyorganization Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/modifyorganization Rest API Failed:No Organization Exist in Service Now")

##Delete Organization by Organization ID##
#    if organizationid:
#        r = requests.delete('https://'+arg[1]+organizationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
#        logging.info("The output of Delete request /api/juniper/servicenow/organization-management/organization %s \n" %str(r.text))
#        #print r.text
#        if(r.status_code == 200 and re.search("Organization deleted successfully",r.text)):
#            pprint.pprint("Delete Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API tested successfully")
#        elif(r.status_code == 404):
#            pprint.pprint("Delete Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API Failed:Invalid organization ID")
#        else:
#            pprint.pprint("Delete Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API Failed")
#    else:
#        pprint.pprint("Delete Method /api/juniper/servicenow/organization-management/organization/{ID} Rest API Failed:No Organization Exist on Service Now")
 
##TODO#NOTWORKING##Add Connected Member Info by ID##
    payload = '<connectedmember><siteName>RestMember</siteName><userName>new@rest.com</userName><password>anVuaXBlcg==</password><jmbFilterValue>Do not send</jmbFilterValue><overrideECAddress>true</overrideECAddress></connectedmember>'
    headers = {'Content-Type': 'application/vnd.juniper.servicenow.organization-management.connectedmember+xml;version=2;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/organization-management/organization/addconnectedmember',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
    logging.info("The output of post request /api/juniper/servicenow/organization-management/organization/addconnectedmember %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("Connected Member successfully created and added to ServiceNow",r.text)):
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/addconnectedmember Rest API tested successfully")
    elif(r.status_code == 400):
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/addconnectedmember Rest API Failed:User name is too long or Site name is too long or Password is too long or jmbFilterValue contains an invalid value")
    elif(r.status_code == 503):
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/addconnectedmember Rest API Failed:Service Now is not in Partner Proxy Mode and Connected Member cannot be created in non partner proxy Mode")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/addconnectedmember Rest API Failed")

##TODO#NOTWORKING##Modify Connected Member by ID##
    if organizationid:
        payload = '<connectedmember><siteName>RestMember</siteName><overrideECAddress>false</overrideECAddress></connectedmember>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.organization-management.connectedmember+xml;version=2;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+organizationid+'/modifyconnectedmember',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
        logging.info("The output of post request /api/juniper/servicenow/organization-management/organization/{ID}/modifyconnectedmember %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("Connected Member updated successfully",r.text)):
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/{ID}/modifyconnectedmember Rest API tested successfully")
        elif(r.status_code == 400):
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/{ID}/modifyconnectedmember Rest API Failed:User name is too long or Site name is too long or Password is too long or jmbFilterValue contains an invalid value")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/{ID}/modifyconnectedmember Rest API Failed:Invalid Connected Member ID specified")
        elif(r.status_code == 503):
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/{ID}/modifyconnectedmember Rest API Failed:Service Now is not in proxy mode. Connected member can only be modified when Service Now is in proxy mode")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/{ID}/modifyconnectedmember Rest API Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/organization-management/organization/{ID}/modifyconnectedmember Rest API Failed")





#########################################################
##Service Now JMB Error Management
#########################################################
def ServiceNowJMBErrorMgmtRestAPIsTest():

##Service Now JMB Error Management##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/jmb-error-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/jmb-error-management %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/jmb-error-management/jmbs",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management Rest API Failed")

##Get All JMBs With Errors in Service Now##
    jmberrorid=None
    jmberroridval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/jmb-error-management/jmbs',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/jmb-error-management/jmbs %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/jmb-error-management\/jmbs\/\w+)",r.text)
        #print m.group(2)
        if m:
            jmberrorid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/jmb-error-management\/jmbs\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            jmberroridval = m.group(3)
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select JMB_NAME from AIM_JMB_INFO where JMB_ID = %s",jmberroridval)
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(str(col))
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('jmbName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1
        if(r.status_code == 200 and total == count and re.search("/api/juniper/servicenow/jmb-error-management/jmbs",r.text)):
            pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs Rest API test Failed")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs Rest API Failed:No JMBs with errors found in Service Now")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs Rest API Failed")


##Get JMB with Error Information by JMB ID##
    if jmberrorid:
        r = requests.get('https://'+arg[1]+jmberrorid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/jmb-error-management/jmbs/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select JMB_NAME from AIM_JMB_INFO where JMB_ID = %s",jmberroridval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('jmbName')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count and re.search("/api/juniper/servicenow/jmb-error-management/jmbs",r.text)):
                pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API Failed:No JMBs with errors found with that ID number")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API Failed:No ERROR JMBs found")
##Export JMBs with Errors by JMB ID##
    if jmberrorid:
        r = requests.get('https://'+arg[1]+jmberrorid+'/export',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/jmb-error-management/jmbs/{ID}/export %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID}/export Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID}/export Rest API Failed:No JMBs with errors found with that ID number")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID}/export Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID}/export Rest API Failed:No ERROR JMBs found")
      
##Delete JMB with Errors by JMB ID##

    if jmberrorid:
        r = requests.delete('https://'+arg[1]+jmberrorid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of Delete request /api/juniper/servicenow/jmb-error-management/jmbs/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("JMB Error successfully deleted",r.text)):
            pprint.pprint("Delete Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Delete Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API Failed:No JMBs with errors found with that ID number")
        else:
            pprint.pprint("Delete Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API Failed")
    else:
        pprint.pprint("Delete Method /api/juniper/servicenow/jmb-error-management/jmbs/{ID} Rest API Failed:No ERROR JMBs found")





#########################################################
##Service Insight PBN Report Management##
#########################################################
def ServiceInsightPBNReportsMgmtRestAPIsTest():
##Service Insight PBN Reports##
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/pbnreport-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/pbnreport-management %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/serviceinsight/pbnreport-management/pbnreports",r.text)):
        pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management Rest API Failed")
##TODO##DONE##Generate PBN Report##
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/exposureanalyzer/sidevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/exposureanalyzer/sidevices %s \n" %str(r.text))
    #print r.text 
    m = re.search("(uri=\")(\/api\/juniper\/serviceinsight\/exposureanalyzer\/sidevices\/\w+)",r.text)
    #print m.group(2)
    payload = "<?xml version='1.0' standalone='yes'?><queue name='QueueDevices'><durable>true</durable></queue>"
    headers = {'Content-Type': 'application/hornetq.jms.queue+xml'}
    r = requests.post('https://'+arg[1]+'/api/hornet-q/queues',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False) 
    payload = '<pbnreport><pbnreportname>NewSDKReport</pbnreportname><devices><device href = "'+m.group(2)+'"/></devices><emails>aprasar@mycompany.net</emails></pbnreport>'
    headers = {'Content-Type': 'application/vnd.juniper.serviceinsight.exposureanalyzer.generatepbnreport+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/serviceinsight/exposureanalyzer/generatepbnreport?queue=https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    #print r.text
    #print r.status_code
    time.sleep(400) 
    if(r.status_code == 202):
        newcol = []
        domaincol = []
        m = re.search("(href=\")(\/api\/space\/job-management\/jobs\/)(\w+)",r.text)
        #print m.group(3)
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="build_db")
        cur = db.cursor()
        cur.execute("use build_db")
        cur.execute("select moState from JobInstance WHERE id = %s",m.group(3))
        rows = cur.fetchall()
        for row in rows:
           for tempcol in row:
              #print "%s" % tempcol
              newcol.append(tempcol)
        if(tempcol == "SUCCESS"):
            pprint.pprint("Post Method /api/juniper/serviceinsight/exposureanalyzer/generatepbnreport Rest API tested successfully")
        else:
            pprint.pprint("Post Method /api/juniper/serviceinsight/exposureanalyzer/generatepbnreport Rest API Failed")
   
    elif(r.status_code == 400):
        pprint.pprint("Post Method /api/juniper/serviceinsight/exposureanalyzer/generatepbnreport Rest API Failed:Invalid PBN report name")
    else:
        pprint.pprint("Post Method /api/juniper/serviceinsight/exposureanalyzer/generatepbnreport Rest API Failed")

    r = requests.delete('https://'+arg[1]+'/api/hornet-q/queues/jms.queue.QueueDevices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)

##Get All PBN Reports in Service Insight##
    pbnreportid=None
    pbnreportidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/pbnreport-management/pbnreports',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/pbnreport-management/pbnreports %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200): 
        m = re.search("(uri=\")(\/api\/juniper\/serviceinsight\/pbnreport-management\/pbnreports\/\w+)",r.text)
        #print m.group(2)
        if m:
            pbnreportid = m.group(2)
        m = re.search("(uri=\")(\/api\/juniper\/serviceinsight\/pbnreport-management\/pbnreports\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            pbnreportidval = m.group(3)
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select reportName from SI_PBN_REPORT_ENTITY WHERE id = %s",pbnreportidval)
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(str(col))
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('reportName')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1
 
        if(r.status_code == 200 and total == count):
            pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports Rest API tested successfully")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports Rest API Failed: No PBN reports were found")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports Rest API Failed")
##Get All PBN Reports in Service Insight by Report ID##
    if pbnreportid:
        r = requests.get('https://'+arg[1]+pbnreportid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select reportName from SI_PBN_REPORT_ENTITY WHERE id = %s",pbnreportidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('reportName')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
 
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API test Failed")
        elif(r.status_code == 204):
            pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API Failed: No PBN reports with this ID were found ")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API Failed:No PBN Reports Exist in Service Insight")

##Export PBN Report in Service Insight##
    if pbnreportid:
        r = requests.get('https://'+arg[1]+pbnreportid+'/export',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #logging.info("The output of get request /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID}/export %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID}/export Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID}/export Rest API Failed: No PBN reports with this ID were found ")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID}/export Rest API Failed")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID}/export Rest API Failed:No PBN Reports Exist in Service Insight")

##Delete PBN Report in Service Insight##
    if pbnreportid:
        r = requests.delete('https://'+arg[1]+pbnreportid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of Delete request  /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("PBN Report successfully deleted",r.text)):
            pprint.pprint("Delete Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API tested successfully")
        elif(r.status_code == 204):
            pprint.pprint("Delete Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API Failed: No PBN reports with this ID were found")
        else:
            pprint.pprint("Delete Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API Failed")
    else:
        pprint.pprint("Delete Method /api/juniper/serviceinsight/pbnreport-management/pbnreports/{ID} Rest API Failed:No PBN Reports Exist in Service Insight")






#########################################################
##Service Now Address Group Management##
#########################################################
def ServiceNowAddressGroupMgmtRestAPIsTest():
##Address Group Management##
    addressgroupid=None
    addressgroupidval=0   
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/address-group-management',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/address-group-management %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/address-group-management/addressGroups",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/address-group-management Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/address-group-management Rest API Failed")

##Get All Address Groups##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/address-group-management/addressGroups',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/address-group-management/addressGroups %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/address-group-management\/addressGroups\/\w+)",r.text)
        #print m.group(2)
        if m:
            addressgroupid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/address-group-management\/addressGroups\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            addressgroupidval = m.group(3)
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select Address_Group_Name from AIM_ADDRESS_GROUP WHERE id = %s",addressgroupidval)
        rows = cur.fetchall()
        for row in rows:
            for col in row:
               # print "%s" % col
                #pprint.pprint(col)
                newcol.append(str(col))
                count = len(rows)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
        for y in range(count):
            for z in range(count):
                if(xmlData[y] == newcol[z]):
                   total = total + 1
        if(r.status_code == 200 and total == count):
            pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups Rest API tested successfully")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups Rest API test Failed")
    elif(r.status_code == 204):
        pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups Rest API Failed: No address groups were found within Service Now")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups Rest API Failed")

##Get Address Group By Address Group ID##
    if addressgroupid:
        r = requests.get('https://'+arg[1]+addressgroupid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/address-group-management/addressGroups/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200): 
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select Address_Group_Name from AIM_ADDRESS_GROUP WHERE id = %s",addressgroupidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups/{ID} Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups/{ID} Rest API Failed:Invalid address group ID or No address group with this ID was found within Service Now")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups/{ID} Rest API Failed")
    else:
            pprint.pprint("Get Method /api/juniper/servicenow/address-group-management/addressGroups/{ID} Rest API Failed: No address group was found in Service Now")

##TODO#ISSUE:Modified address group has domain ID of NULL##Modify Address Group##
    if addressgroupid:
        payload = '<addressGroup><address1>Plot No. 66</address1><address2>Bagmane Tech Park</address2><city>Bangalore</city><state>Karnataka</state><country>India</country><zipCode>566093</zipCode><contactName>Jim</contactName><contactPhone>9878906754</contactPhone><alternativePhone>687677868</alternativePhone><notes>This is juniper bangalore address</notes></addressGroup>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.address-group-management.addressgroup+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+addressgroupid+'/modify',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        logging.info("The output of Post request /api/juniper/servicenow/address-group-management/addressGroups/{ID}/modify %s \n" %str(r.text))
        if(r.status_code == 200):
             addresscol = []
             newcol = []
             tempcol = []
             db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
             cur = db.cursor()
             cur.execute("use snsi_db")
             cur.execute("select Address_Group_Name from AIM_ADDRESS_GROUP WHERE id = %s",addressgroupidval)
             rows = cur.fetchall()
             for row in rows:
                 for addresscol in row:
                     #print "%s" % addresscol
                     newcol.append(addresscol)


             db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
             cur = db.cursor()
             cur.execute("use snsi_db")
             cur.execute("select domainId from AIM_ADDRESS_GROUP WHERE Address_Group_Name = %s", addresscol)
             rows = cur.fetchall()
             for row in rows:
                 for tempcol in row:
                     #print "%s" % tempcol
                     newcol.append(tempcol)


             if(r.status_code == 200 and tempcol == 2 and re.search("Bagmane Tech Park",r.text)):
                  pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/modify Rest API tested successfully")
             else:
                  pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/modify Rest API test Failed")
 
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/modify Rest API test Failed:Address group ID not found in Service Now")
        elif(r.status_code == 400):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/modify Rest API test Failed:Address group name is null or empty or Address group name already exists in Service Now or Address field(s) are empty or City field is empty or State field is empty or Zip code field is empty")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/modify Rest API test Failed")
    else:
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/modify Rest API test Failed:No Address Group already existed in Service Now")

##TODO#ISSUE:Address Group is created with system domain##Create Address Group##
    payload = '<addressGroup><name>Juniper Networks</name><address1>Plot No. 66</address1><address2>Bagmane Tech Park</address2><city>Bangalore</city><state>Karnataka</state><country>India</country><zipCode>566093</zipCode><contactName>Jim</contactName><contactPhone>9878906754</contactPhone><alternativePhone>687677868</alternativePhone><notes>This is juniper bangalore address</notes></addressGroup>'
    headers = {'Content-Type': 'application/vnd.juniper.servicenow.address-group-management.addressgroup+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/address-group-management/addressGroups/create',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    #print r.text
    logging.info("The output of Post request /api/juniper/servicenow/address-group-management/addressGroups/create %s \n" %str(r.text))
    if(r.status_code == 200):
         newcol=[]
         db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
         cur = db.cursor()
         cur.execute("use snsi_db")
         cur.execute('select domainId from AIM_ADDRESS_GROUP WHERE Address_Group_Name = "Juniper Networks"')
         rows = cur.fetchall()
         for row in rows:
             for tempcol in row:
                 #print "%s" % tempcol
                 newcol.append(tempcol)

         if(r.status_code == 200 and tempcol == 2 and re.search("Juniper Networks",r.text)):
              pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/create Rest API tested successfully")
         else:
              pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/create Rest API test Failed")

    elif(r.status_code == 400):
        pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/create Rest API test Failed:Address group name is null or empty or Address group name already exists in Service Now or Address field(s) are empty or City field is empty or State field is empty or Zip code field is empty")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/create Rest API test Failed")

##Associate Devices to Address Group##
    if addressgroupid:
        addressgrpdeviceid=None
        r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-management/devices',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-management\/devices\/\w+)",r.text)
        if m:
            addressgrpdeviceid = m.group(2)
        payload = '<devices><device href="'+addressgrpdeviceid+'"><addressType>2</addressType></device></devices>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.address-group-management.devices+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+addressgroupid+'/associateDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        logging.info("The output of Post request /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices %s \n" %str(r.text))
        if(r.status_code == 200):
            if(r.status_code == 200 and re.search("Device successfully associated with address group",r.text)):
                 pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices Rest API tested successfully")
            else:
                 pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices Rest API test Failed")

        elif(r.status_code == SN-1000):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices Rest API test Failed:Specified devices are not valid")
        elif(r.status_code == SN-1007):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices Rest API test Failed:Address type is not valid")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices Rest API test Failed:Address group ID not found in Service Now")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices Rest API test Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/associateDevices Rest API test Failed:No Address Group Exist in Service Now")
##De-associate Devices From an Address Group##
    if addressgroupid:
        payload = '<devices><device href="'+addressgrpdeviceid+'"><addressType>2</addressType></device></devices>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.address-group-management.devices+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+addressgroupid+'/deassociateDevices',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        logging.info("The output of Post request /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices %s \n" %str(r.text))
        if(r.status_code == 200):
            if(r.status_code == 200 and re.search("Device successfully deassociated from address group",r.text)):
                 pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API tested successfully")
            else:
                 pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API test Failed")
        elif(r.status_code == SN-1000):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API test Failed:Specified devices are not valid")
        elif(r.status_code == SN-1008):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API test Failed:Device is not associated with the address group")
        elif(r.status_code == SN-1007):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API test Failed:Address type is not valid")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API test Failed:Address group ID not found in Service Now")
        else:
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API test Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/addressGroups/{ID}/deassociateDevices Rest API test Failed:No Address Groups exist in Service Now")
##Get All End Customer Address Groups##
    ecaddressgrpid=None
    ecaddressgrpidval=0
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/address-group-management/endCustomerAddressGroups',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/address-group-management/endCustomerAddressGroups %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/address-group-management\/endCustomerAddressGroups\/\w+)",r.text)
        #print m.group(2)
        if m:
            ecaddressgrpid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/address-group-management\/endCustomerAddressGroups\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            ecaddressgrpidval = m.group(3)
        if(r.status_code == 200 and re.search("endCustomerAddressGroups",r.text)):
             pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups Rest API tested successfully")
        else:
             pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups Rest API test Failed")

    elif(r.status_code == 204):
        pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups Rest API test Failed:No end-customer address groups found")
    elif(r.status_code == 403):
        pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups Rest API test Failed:Service Now is not running in Proxy mode")
    else:
        pprint.pprint("Post Method  /api/juniper/servicenow/address-group-management/endCustomerAddressGroups Rest API test Failed")
##Get End Customer Address Groups By ID##
    if ecaddressgrpid:
        r = requests.get('https://'+arg[1]+ecaddressgrpid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/address-group-management/endCustomerAddressGroups/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200):
            if(r.status_code == 200 and re.search("endCustomerAddressGroups",r.text)):
                 pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups/{ID} Rest API tested successfully")
        elif(r.status_code == 403):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups/{ID} Rest API test Failed:Service Now is not running in Proxy mode")
        elif(r.status_code == 404):
            pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups/{ID} Rest API test Failed:Invalid address group ID")
        else:
            pprint.pprint("Post Method  /api/juniper/servicenow/address-group-management/endCustomerAddressGroups/{ID} Rest API test Failed")
    else:
        pprint.pprint("Post Method /api/juniper/servicenow/address-group-management/endCustomerAddressGroups Rest API test Failed:No end-customer address groups found")
##Delete Address Group by Address Group ID##
    if addressgroupid:
        r = requests.delete('https://'+arg[1]+addressgroupid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of Delete request /api/juniper/servicenow/address-group-management/addressGroups/{id}  %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200 and re.search("Address Group successfully deleted",r.text)):
            pprint.pprint("Delete Method /api/juniper/servicenow/address-group-management/addressGroups/{id} Rest API tested successfully")
        elif(r.status_code == 404):
            pprint.pprint("Delete Method /api/juniper/servicenow/address-group-management/addressGroups/{id} Rest API Failed: No address group with the specified identifier was found")
        else:
            pprint.pprint("Delete Method /api/juniper/servicenow/address-group-management/addressGroups/{id} Rest API Failed")
    else:
            pprint.pprint("Delete Method /api/juniper/servicenow/address-group-management/addressGroups/{id} Rest API Failed:No Address Group exist in Service Now")


#########################################################
##Service Now Notifications Management##
#########################################################
def ServiceNowNotificationsMgmtRestAPIsTest():
    notificationid=None
    notificationidval=0 
    valfound=0 
    str1=None 

##Create Service Now Notifications##
    payload = '<notification><name>Test Notification</name><emails><email>test@juniper.net</email></emails><filters><deviceName>TEST</deviceName><serialNumber>12345</serialNumber><priority>Medium</priority></filters><trigger>POLICY_TRIGGER_NEW_INCIDENT_DETECTED</trigger><jmbAttachment>true</jmbAttachment></notification>'
    headers = {'Content-Type': 'application/vnd.juniper.servicenow.notification-management.createNotification+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/servicenow/notification-management/createNotification',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of POST request /api/juniper/servicenow/notification-management/createNotification %s \n" %str(r.text))
    #print r.text
    if(re.search("already exists",r.text)):
        pprint.pprint("POST Method /api/juniper/servicenow/notification-management/createNotification Rest API Failed: SN Test Notification already Exists!!")
    elif(r.status_code == 200 and re.search("Notifications: successfully created",r.text)):
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select id from AIM_REACTION_POLICY WHERE name = %s","Test Notification")
        rows = cur.fetchall()
        for row in rows:
           for col in row:
               #print "%s" % col
               #pprint.pprint(col)
               newcol.append(str(col))
               count = len(rows)
        r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/notification-management/notifications/'+str(col),auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(str1 == "Test Notification"):
            total = total + 1
        if(total == 1): 
            pprint.pprint("POST Method /api/juniper/servicenow/notification-management/createNotification Rest API tested successfully")
        else:
            pprint.pprint("POST Method /api/juniper/servicenow/notification-management/createNotification Rest API test Failed")
    else:
        pprint.pprint("POST Method /api/juniper/servicenow/notification-management/createNotification Rest API test Failed")
##ServiceNow Notifications Mgmt##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/notification-management/notifications/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/notification-management/notifications/ %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/servicenow/notification-management/notifications/",r.text)):
        pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/ Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/ Rest API Failed")
##Get All ServiceNow Notifications##
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/notification-management/notifications/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/notification-management/notifications/ %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/notification-management\/notifications\/\w+)",r.text)
        #print m.group(2)
        if m:
            notificationid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/notification-management\/notifications\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            notificationidval = m.group(3)
            valfound = 1
        if(valfound == 1):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select name from AIM_REACTION_POLICY WHERE id = %s",notificationidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                    #print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/ Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/ Rest API test Failed")
        elif(valfound == 0):
            pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/ Rest API Failed: No Notifications were found within Service Now")
    else:
        pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/ Rest API Failed")

##Get ServiceNow Notifications By Notification ID##
    if notificationidval:
        r = requests.get('https://'+arg[1]+notificationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/notification-management/notifications/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200): 
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select name from AIM_REACTION_POLICY WHERE id = %s",notificationidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API Failed:Invalid SN Notification ID or No SN Notifications with this ID was found within Service Now")
        else:
            pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API Failed")
    else:
            pprint.pprint("Get Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API Failed: No Notifications was found in Service Now")
##Copy ServiceNow Notifications##
    if notificationidval:
        payload = '<notification><name>COPY Test Notification</name><emails><email>test@juniper.net</email></emails><filters><deviceName></deviceName><priority>Medium</priority></filters><jmbAttachment>true</jmbAttachment></notification>'
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.notification-management.copyNotification+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+notificationid+'/copy',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of POST request /api/juniper/servicenow/notification-management/notifications/{ID}/copy %s \n" %str(r.text))
        #print r.text
        if(re.search("already exists",r.text)):
            pprint.pprint("POST Method /api/juniper/servicenow/notification-management/notifications/{ID}/copy Rest API Failed: SN COPY Test Notification already Exists!!")
        elif(r.status_code == 200 and re.search("Notifications: successfully copied",r.text)): 
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select id from AIM_REACTION_POLICY WHERE name = %s","COPY Test Notification")
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   # pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
##Not Working Copy Notification is created with domainId = 1 ie SYSTEM Domain below we are setting it to globaldomain but query not working
            #db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            #cur = db.cursor()
            #cur.execute("use snsi_db")
            #cur.execute("""
            #    UPDATE AIM_REACTION_POLICY 
            #    SET domainId=%s where id = %s
            #""",('2', str(col)))
            #rows = cur.fetchall()
            if(r.status_code == 200 and count == 1):
                pprint.pprint("POST Method /api/juniper/servicenow/notification-management/notifications/{ID}/copy Rest API tested successfully")
            else:
                pprint.pprint("POST Method /api/juniper/servicenow/notification-management/notifications/{ID}/copy Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("POST Method /api/juniper/servicenow/notification-management/notifications/{ID}/copy Rest API Failed:Invalid SN Notification ID or No SN Notifications with this ID was found within Service Now")
        else:
            pprint.pprint("POST Method /api/juniper/servicenow/notification-management/notifications/{ID}/copy Rest API Failed")
    else:
            pprint.pprint("POST Method /api/juniper/servicenow/notification-management/notifications/{ID}/copy Rest API Failed: No Notifications was found in Service Now")
##Change Status of ServiceNow Notifications##
    if notificationidval:
        r = requests.put('https://'+arg[1]+notificationid+'/changeStatus',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of PUT request /api/juniper/servicenow/notification-management/notifications/{ID}/changestatus %s \n" %str(r.text))
        #print r.text
        xmlData =[]
        dom = parseString(r.text)
        xmlData.append(dom.getElementsByTagName('status')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(str1 == 'Disabled'):
            r = requests.put('https://'+arg[1]+notificationid+'/changeStatus',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        else:
            pprint.pprint("The Notifications is already in Enabled State")
        if(r.status_code == 200):
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/changeStatus Rest API tested successfully")
        else:
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/changeStatus Rest API test Failed")
    else:
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/changeStatus Rest API Failed: No Notifications was found in Service Now")
##Edit Filter and Actions of Service Now Notifications
    organizationid=None
    organizationidval=0
    devicegroupid=None
    devicegroupidval=0
    snmpid=None
    snmpidval=0

    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management/organization/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/organization-management/organization %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        xmlData =[]
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('isConnectedMember')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(str1 == 'false'):
            m = re.search("(href=\")(\/api\/juniper\/servicenow\/organization-management\/organization\/\w+)",r.text)
            #print m.group(2)
            if m:
                organizationid = m.group(2)
            m = re.search("(href=\")(\/api\/juniper\/servicenow\/organization-management\/organization\/)(\w+)",r.text)
            #print m.group(3)
            if m:
                organizationidval = m.group(3)
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-group-management/deviceGroup/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-group-management/deviceGroup %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-group-management\/deviceGroup\/\w+)",r.text)
        #print m.group(2)
        if m:
            devicegroupid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-group-management\/deviceGroup\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            devicegroupidval = m.group(3)
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/global-setting-management/snmp-configuration-management/snmpConfiguration',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/global-setting-management/snmp-configuration-management/snmpConfiguration %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/global-setting-management\/snmp-configuration-management\/snmpConfiguration\/\w+)",r.text)
        #print m.group(2)
        if m:
            snmpid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/global-setting-management\/snmp-configuration-management\/snmpConfiguration\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            snmpidval = m.group(3)
    if notificationidval:
        payload = '<notification><emails><email>test@juniper.net</email></emails><snmpTraps><snmpTrap uri="'+snmpid+'" href="'+snmpid+'"/></snmpTraps><filters><deviceName>Hello</deviceName><serialNumber>12345</serialNumber><hasTheWords>Temp</hasTheWords><doesnotHave>newtemp</doesnotHave><organization uri="'+organizationid+'" href="'+organizationid+'"/><deviceGroup uri="'+devicegroupid+'" href="'+devicegroupid+'"/><priority>Medium</priority></filters><jmbAttachment>true</jmbAttachment></notification>' 
        headers = {'Content-Type': 'application/vnd.juniper.servicenow.notification-management.editFiltersAndActions+xml;version=1;charset=UTF-8'}
        r = requests.put('https://'+arg[1]+notificationid+'/editFilterAndAction',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of PUT request /api/juniper/servicenow/notification-management/notifications/{ID}/editFilterAndAction %s \n" %str(r.text))
        if(r.status_code == 200 and re.search("Notifications: successfully edited",r.text)):
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/editFilterAndAction Rest API tested successfully")
        else:
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/editFilterAndAction Rest API test Failed")

        r = requests.get('https://'+arg[1]+notificationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/servicenow/notification-management/notifications/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200): 
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('deviceName')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(r.status_code == 200 and str1 == 'Hello'):
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/editFilterAndAction Rest API tested successfully")
        else:
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/editFilterAndAction Rest API test Failed")
    else:
            pprint.pprint("PUT Method /api/juniper/servicenow/notification-management/notifications/{ID}/editFilterAndAction Rest API Failed: No Notifications was found in Service Now")
##Delete Service Now Notification##
    if notificationidval:
        r = requests.delete('https://'+arg[1]+notificationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of delete request /api/juniper/servicenow/notification-management/notifications/{ID} %s \n" %str(r.text))
        #print r.text 
        if(r.status_code == 200 and re.search("Notifications: successfully deleted",r.text)):
            pprint.pprint("DELETE Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API tested successfully")
        else:
            pprint.pprint("DELETE Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API test Failed")
    else:
            pprint.pprint("DELETE Method /api/juniper/servicenow/notification-management/notifications/{ID} Rest API Failed: No Notifications was found in Service Now")
#########################################################
##Service Insight Notifications Management##
#########################################################
def ServiceInsightNotificationsMgmtRestAPIsTest():
    sinotificationid=None
    sinotificationidval=0 
    valfound=0  
##Create Service Insight Notifications##
    payload = '<notification><name>EOL MATCH Notification</name><emails><email>test@juniper.net</email></emails><filters><deviceName>TEST</deviceName><serialNumber>12345</serialNumber><tag>None</tag></filters><trigger>NEW_EOL_MATCH</trigger></notification>'
    headers = {'Content-Type': 'application/vnd.juniper.serviceinsight.notification-management.createNotification+xml;version=1;charset=UTF-8'}
    r = requests.post('https://'+arg[1]+'/api/juniper/serviceinsight/notification-management/createNotification',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of POST request /api/juniper/serviceinsight/notification-management/createNotification %s \n" %str(r.text))
    #print r.text
    if(re.search("already exists",r.text)):
        pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/createNotification Rest API Failed: SN Test Notification already Exists!!")
    elif(r.status_code == 200 and re.search("successfully created notification with name",r.text)):
        newcol = []
        count = 0
        total = 0
        db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
        cur = db.cursor()
        cur.execute("use snsi_db")
        cur.execute("select id from SI_NOTIFICATIONS WHERE name = %s","EOL MATCH Notification")
        rows = cur.fetchall()
        for row in rows:
           for col in row:
               #print "%s" % col
               #pprint.pprint(col)
               newcol.append(str(col))
               count = len(rows)
        r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/notification-management/notifications/'+str(col),auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        xmlData = []
        total = 0
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(str1 == "EOL MATCH Notification"):
            total = total + 1
        if(total == 1): 
            pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/createNotification Rest API tested successfully")
        else:
            pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/createNotification Rest API test Failed")
    else:
        pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/createNotification Rest API test Failed")
##ServiceInsight Notifications Mgmt##
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/notification-management/notifications/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/notification-management/notifications/ %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200 and re.search("/api/juniper/serviceinsight/notification-management/notifications/",r.text)):
        pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/ Rest API tested successfully")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/ Rest API Failed")
##Get All ServiceInsight Notifications##
    r = requests.get('https://'+arg[1]+'/api/juniper/serviceinsight/notification-management/notifications/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/serviceinsight/notification-management/notifications/ %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/serviceinsight\/notification-management\/notifications\/\w+)",r.text)
        #print m.group(2)
        if m:
            sinotificationid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/serviceinsight\/notification-management\/notifications\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            sinotificationidval = m.group(3)
            valfound = 1
        if(valfound == 1):
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select name from SI_NOTIFICATIONS WHERE id = %s",sinotificationidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                    #print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/ Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/ Rest API test Failed")
        elif(valfound == 0):
            pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/ Rest API Failed: No Notifications were found within serviceinsight")
    else:
        pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/ Rest API Failed")
##Get ServiceInsight Notifications By Notification ID##
    if sinotificationidval:
        r = requests.get('https://'+arg[1]+sinotificationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/serviceinsight/notification-management/notifications/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200): 
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select name from SI_NOTIFICATIONS WHERE id = %s",sinotificationidval)
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                    #pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('name')[x].firstChild.data)
            for y in range(count):
                for z in range(count):
                    if(xmlData[y] == newcol[z]):
                       total = total + 1
            if(r.status_code == 200 and total == count):
                pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API tested successfully")
            else:
                pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API Failed:Invalid SI Notification ID or No SI Notifications with this ID was found within Service Insight")
        else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API Failed")
    else:
            pprint.pprint("Get Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API Failed: No Notifications was found in Service Insight")
##Copy ServiceInsight Notifications##
    if sinotificationidval:
        payload = '<notification><name>COPY EOL MATCH Notification</name><emails><email>test@juniper.net</email></emails><filters><deviceName>TEST</deviceName><serialNumber>12345</serialNumber></filters><trigger>NEW_EOL_MATCH</trigger></notification>'
        headers = {'Content-Type': 'application/vnd.juniper.serviceinsight.notification-management.copyNotification+xml;version=1;charset=UTF-8'}
        r = requests.post('https://'+arg[1]+sinotificationid+'/copy',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of POST request /api/juniper/serviceinsight/notification-management/notifications/{ID}/copy %s \n" %str(r.text))
        #print r.text
        if(re.search("already exists",r.text)):
            pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/copy Rest API Failed: SI COPY EOL MATCH Notification already Exists!!")
        elif(r.status_code == 200 and re.search("successfully created notification with name",r.text)): 
            newcol = []
            count = 0
            total = 0
            db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            cur = db.cursor()
            cur.execute("use snsi_db")
            cur.execute("select id from SI_NOTIFICATIONS WHERE name = %s","COPY EOL MATCH Notification")
            rows = cur.fetchall()
            for row in rows:
                for col in row:
                   # print "%s" % col
                   # pprint.pprint(col)
                    newcol.append(str(col))
                    count = len(rows)
##Not Working Copy Notification is created with domainId = 1 ie SYSTEM Domain below we are setting it to globaldomain but query not working
            #db = MySQLdb.connect(host=arg[2],user="jboss",passwd="netscreen",db="snsi_db")
            #cur = db.cursor()
            #cur.execute("use snsi_db")
            #cur.execute("""
            #    UPDATE AIM_REACTION_POLICY 
            #    SET domainId=%s where id = %s
            #""",('2', str(col)))
            #rows = cur.fetchall()
            if(r.status_code == 200 and count == 1):
                pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/copy Rest API tested successfully")
            else:
                pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/copy Rest API test Failed")
        elif(r.status_code == 404):
            pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/copy Rest API Failed:Invalid SI Notification ID or No SI Notifications with this ID was found within Service Insight")
        else:
            pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/copy Rest API Failed")
    else:
            pprint.pprint("POST Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/copy Rest API Failed: No Notifications was found in Service Insight")
##Change Status of ServiceNow Notifications##
    if sinotificationidval:
        r = requests.put('https://'+arg[1]+sinotificationid+'/changeStatus',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of PUT request /api/juniper/serviceinsight/notification-management/notifications/{ID}/changestatus %s \n" %str(r.text))
        #print r.text
        xmlData =[]
        dom = parseString(r.text)
        xmlData.append(dom.getElementsByTagName('status')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(str1 == 'Disabled'):
            r = requests.put('https://'+arg[1]+sinotificationid+'/changeStatus',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        else:
            pprint.pprint("The Notifications is already in Enabled State")
        if(r.status_code == 200):
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/changeStatus Rest API tested successfully")
        else:
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/changeStatus Rest API test Failed")
    else:
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/changeStatus Rest API Failed: No Notifications was found in Service Insight")
##Edit Filter and Actions of Service Now Notifications
    organizationid=None
    organizationidval=0
    devicegroupid=None
    devicegroupidval=0
    snmpid=None
    snmpidval=0

    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/organization-management/organization/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/organization-management/organization %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        xmlData =[]
        dom = parseString(r.text)
        for x in range(count):
            xmlData.append(dom.getElementsByTagName('isConnectedMember')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(str1 == 'false'):
            m = re.search("(href=\")(\/api\/juniper\/servicenow\/organization-management\/organization\/\w+)",r.text)
            #print m.group(2)
            if m:
                organizationid = m.group(2)
            m = re.search("(href=\")(\/api\/juniper\/servicenow\/organization-management\/organization\/)(\w+)",r.text)
            #print m.group(3)
            if m:
                organizationidval = m.group(3)
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/device-group-management/deviceGroup/',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/device-group-management/deviceGroup %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-group-management\/deviceGroup\/\w+)",r.text)
        #print m.group(2)
        if m:
            devicegroupid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/device-group-management\/deviceGroup\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            devicegroupidval = m.group(3)
    r = requests.get('https://'+arg[1]+'/api/juniper/servicenow/global-setting-management/snmp-configuration-management/snmpConfiguration',auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
    logging.info("The output of get request /api/juniper/servicenow/global-setting-management/snmp-configuration-management/snmpConfiguration %s \n" %str(r.text))
    #print r.text
    if(r.status_code == 200):
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/global-setting-management\/snmp-configuration-management\/snmpConfiguration\/\w+)",r.text)
        #print m.group(2)
        if m:
            snmpid = m.group(2)
        m = re.search("(href=\")(\/api\/juniper\/servicenow\/global-setting-management\/snmp-configuration-management\/snmpConfiguration\/)(\w+)",r.text)
        #print m.group(3)
        if m:
            snmpidval = m.group(3)
    if sinotificationidval:
        payload = '<notification><emails><email>test@juniper.net</email></emails><snmpTraps><snmpTrap uri="'+snmpid+'" href="'+snmpid+'"/></snmpTraps><filters><deviceName>Hello</deviceName><serialNumber>12345</serialNumber><organization uri="'+organizationid+'" href="'+organizationid+'"/><deviceGroup uri="'+devicegroupid+'" href="'+devicegroupid+'"/></filters></notification>'
        headers = {'Content-Type': 'application/vnd.juniper.serviceinsight.notification-management.editFiltersAndActions+xml;version=1;charset=UTF-8'}
        r = requests.put('https://'+arg[1]+sinotificationid+'/editFiltersAndAction',data=payload,headers=headers,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        #print r.text
        logging.info("The output of PUT request /api/juniper/serviceinsight/notification-management/notifications/{ID}/editFilterAndAction %s \n" %str(r.text))
        if(r.status_code == 200 and re.search("Filters and actions edited successfully",r.text)):
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/editFilterAndAction Rest API tested successfully")
        else:
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/editFilterAndAction Rest API test Failed")

        r = requests.get('https://'+arg[1]+sinotificationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of get request /api/juniper/serviceinsight/notification-management/notifications/{ID} %s \n" %str(r.text))
        #print r.text
        if(r.status_code == 200): 
            xmlData = []
            total = 0
            dom = parseString(r.text)
            for x in range(count):
                xmlData.append(dom.getElementsByTagName('deviceName')[x].firstChild.data)
        str1 = ''.join(xmlData)
        if(r.status_code == 200 and str1 == 'Hello'):
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/editFilterAndAction Rest API tested successfully")
        else:
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/editFilterAndAction Rest API test Failed")
    else:
            pprint.pprint("PUT Method /api/juniper/serviceinsight/notification-management/notifications/{ID}/editFilterAndAction Rest API Failed: No Notifications was found in Service Now")
##Delete Service Now Notification##
    if sinotificationidval:
        r = requests.delete('https://'+arg[1]+sinotificationid,auth=HTTPBasicAuth('super', 'juniper123'),verify=False)
        logging.info("The output of DELETE request /api/juniper/serviceinsight/notification-management/notifications/{ID} %s \n" %str(r.text))
        #print r.text 
        if(r.status_code == 200 and re.search("Notification: successfully deleted",r.text)):
            pprint.pprint("DELETE Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API tested successfully")
        else:
            pprint.pprint("DELETE Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API test Failed")
    else:
            pprint.pprint("DELETE Method /api/juniper/serviceinsight/notification-management/notifications/{ID} Rest API Failed: No Notifications was found in Service Insight")




#########################################################
#ServiceInsightRestAPIsTest()



#ServiceNowDeviceMgmtRestAPIsTest()
#ServiceNowEventProfileMgmtRestAPIsTest()
#ServiceNowIncidentMgmtRestAPIsTest()
#ServiceNowScriptBundleMgmtRestAPIsTest()
#ServiceNowTechnicalSupportCaseMgmtRestAPIsTest()
#ServiceNowEndCustomerCaseMgmtRestAPIsTest()
#ServiceNowAutoSubmitPolicyMgmtRestAPIsTest()
#ServiceNowDeviceSnapshotMgmtRestAPIsTest()
#ServiceNowOrganizationMgmtRestAPIsTest()
#ServiceNowJMBErrorMgmtRestAPIsTest()
#ServiceInsightPBNReportsMgmtRestAPIsTest()
#ServiceNowAddressGroupMgmtRestAPIsTest()
#ServiceNowNotificationsMgmtRestAPIsTest()
ServiceInsightNotificationsMgmtRestAPIsTest()
#########################################################
