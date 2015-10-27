import json
import itertools
import os.path
parsed_json = None
acctID = None
srid = None
val = None
with open("/root/HBase/CaseFiles/SRID_LIST") as newtarget:
    for line in newtarget:
        SRID = line
        with open("/root/HBase/ACCT_USER/SRID_ACCTID_MAP") as target:
            for acctline in target:
                parsed_json = json.loads(acctline)
                #print parsed_json
                #acctID = parsed_json.get[SRID.rstrip('\n')]
                srid = SRID.rstrip('\n')
                if srid in parsed_json:
                   acctID = parsed_json[srid].rstrip('\n')
                if (os.path.isfile("/root/HBase/ACCT_USER/0"+acctID) and ("/root/HBase/CaseFiles/"+srid)):
                   with open("/root/HBase/ACCT_USER/0"+acctID) as temptarget:
                       with open("/root/HBase/CaseFiles/"+srid,"a+") as fsttarget:
                           data = temptarget.read()
                           fsttarget.write(data)
                else:
                   continue      
