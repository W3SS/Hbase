import json
import itertools
import os.path
parsed_json = None
acctID = None
srid = None
val = None
with open("/home/regress/HBase/CaseFiles/SRID_LIST") as newtarget:
    for line in newtarget:
        SRID = line
        with open("/home/regress/HBase/ACCT_USER/SRID_ACCTID_MAP") as target:
            for acctline in target:
                parsed_json = json.loads(acctline)
                #print parsed_json
                #acctID = parsed_json.get[SRID.rstrip('\n')]
                srid = SRID.rstrip('\n')
                if srid in parsed_json:
                   acctID = parsed_json[srid].rstrip('\n')
                if (os.path.isfile("/home/regress/HBase/ACCT_USER/"+acctID) and ("/home/regress/HBase/CaseFiles/"+srid)):
                   with open("/home/regress/HBase/ACCT_USER/"+acctID) as temptarget:
                       with open("/home/regress/HBase/CaseFiles/"+srid,"a+") as fsttarget:
                           data = temptarget.read()
                           fsttarget.write(data)
                else:
                   continue      
