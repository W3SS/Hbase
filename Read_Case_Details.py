#!/usr/bin/python
## @package Read_Case_Details.py
#  This file contains subroutines to read following files 
# SR_Files
# Attachment Files
# KB Article Files
# Relation Files (User -> Account) or (Account -> User) Relation
# Account Files
# User or Contact Files
# Date Files
# Partner Files
# SR Notes Files
#

import sys
import pprint
import requests
import logging
import time
import re
import json
from itertools import islice
import threading
from sys import argv
from time import sleep
from requests.auth import HTTPBasicAuth
test = ''
############################################################################
## Read_SR(SR_File)
# Input: SR_File
#  This Subroutine will read SR_File and Create 
#  New file for each SR and append all the SR related files 
#  into that file for later retrieval
############################################################################
def Read_SR(SR_File):
    SR_Key = ['SRID','PROCESS_TYPE_DES','PROCESS_TYPE','DESCRIPTION','BETA_TYPE','ESCALATION_KEY','ESCALATION_DES','COURTESY_KEY','COURTESY','SEC_VULNERABILITY','PRODUCT_ID','SERIAL_NUMBER','STATUS_KEY','STATUS','REASON','PRIORITY_KEY','PRIORITY','SEVERITY_KEY','SEVERITY','CRITICAL_OUTAGE','PRODUCT_SERIES','PLATFORM','RELEASE','VERSION','SOFTWARE','SPECIAL_RELEASE','SR_CATEGORY1','SR_CATEGORY2','SR_CATEGORY3','SR_CATEGORY4','PRODUCT_SERIES_TECH','TECHNICAL_CATEGORY1','TECHNICAL_CATEGORY2','TECHNICAL_CATEGORY3','JSA_ADVISORY_BOARD','CVE','CVSS','SME_CONTACT','JTAC','SIRT_BUNDLE','REPORTER_DETAILS','EXTERNALLY_REPORTED','ENTITLEMENT_CHECKED','ENTITLED_SERIAL_NO','SERVICE_PRODUCT','ENTITLEMENT_SERVICE_LEVEL','ENTITLEMENT_SOURCE','SKU','START_DATE','END_DATE','CONTRACT_STATUS','CONTRACT_ID','WARRANTY_END_DATE','OUTAGE_KEY','OUTAGE','OUTAGE_INFO_AVAILABLE','OUTAGE_CAUSE_KEY','OUATGE_CAUSE','TOTAL_OUTAGE_TIME','OUTAGE_TYPE_KEY','OUTAGE_TYPE','OVERIDE_OUTAGE','OUTAGE_IMPACT_KEY','OUTAGE_IMPACT','EMPID','EMP_MAIL_ID','NO_OF_SYSTEMS_AFFECTED','NO_OF_USERS_AFFECTED','ZZQ1','ZZQ2','ZZQ3','ZZQ4','ZZQ5','ZZQ6','ZZQ7','ZZQ8','ZZQ9','ZZQ10','CRITICAL_ISSUE','ESCALATION_LEVEL_KEY','ESCALATION_LEVEL','INTERNAL_USE','PREVIOUS_TEAM','PREVIOUS_OWNER_SKILL','SUPPORT_24_7','KNOWLEDGE_ARTICLE','RA_FA','CC_CUSTOMER','CC_ENGINEER','ROUTER_NAME','TOP 5','BUILD','CUST_CASE_NO','VIA_key','VIA','FOLLOW_UP_METHOD','FOLLOW_UP_METHOD_KEY','THEATER_KEY','THEATER','TEMPERATURE','COUNTRY','OUTSOURCER','URGENCY_KEY','URGENCY']

    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+SR_File))
    with open("/root/HBase/CaseDetails/"+SR_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(SR_Key, m))
            if (dictionary['URGENCY'] == '|#$#%$|\n'):
                dictionary['URGENCY'] = '' 
            SRID = dictionary['SRID']
            with open("/root/HBase/CaseFiles/SRID_LIST", "a+") as testtarget:
                testtarget.write(SRID)
                testtarget.write("\n")
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/CaseFiles/"+dictionary['SRID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")

############################################################################
## Read_Attachment(Attach_File)
#  Input: Attach_File
#  This Subroutine will read Attach_File and Create new file
#  or append to existing SR_File which is already created by Read_SR(SR_File)
############################################################################
def Read_Attachment(Attach_File):
    Attach_Key = ['SNO', 'SRID', 'TITLE', 'SIZE1', 'PATH', 'PRIVATE1', 'DATE_CREATED', 'ZDATE', 'ZTIME', 'FILE_TYPE', 'CREATED_BY', 'UPLOADED_BY' ]

    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+Attach_File))
    with open("/root/HBase/CaseDetails/"+Attach_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(Attach_Key, m))
            if (dictionary['UPLOADED_BY'] == '\n'):
                dictionary['UPLOADED_BY'] = '' 
            temp = dictionary['UPLOADED_BY'].rstrip('\n')
            dictionary['UPLOADED_BY'] = temp 
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/CaseFiles/"+dictionary['SRID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")

############################################################################
## Read_KB(KB_File)
#  Input: KB_File
#  This subroutine will read KB_File and Create new file
#  or append to existing SR_File which is already created by Read_SR(SR_File)
#
############################################################################
def Read_KB(KB_File):
    KB_Key = ['INTERNALID','KBID','SRID','DESCRIPTION','STATUS','SOURCEVISIBILITY','DATA_SOURCE','URL','KBDATE','SRVISIBILITY','KB_FLAG']

    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+KB_File))
    with open("/root/HBase/CaseDetails/"+KB_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(KB_Key, m))
            temp = dictionary['KB_FLAG'].rstrip('\n')
            dictionary['KB_FLAG'] = temp 
            if (dictionary['KB_FLAG'] == '\n'):
                dictionary['KB_FLAG'] = '' 
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/CaseFiles/"+dictionary['SRID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")



############################################################################
## Read_Acct_User_Relation(Acct_User_Relation_File)
#  INPUT:Acct_User_Relation_File
#  This subroutine will read Acct_User_Relation_File and Create new file
#  or append to existing Accounts_File which is already created by Read_Acct()
#  or Read_User()
#
############################################################################
def Read_Acct_User_Relation(Acct_User_Relation_File):
    ACCT_USR_REL_Key = ['ACCOUNT_ID','CONTACT_ID','RELATIONSHIP_CODE','RELATIONSHIP_DESCRIPTION','RELATIONSHIP_CREATE_DATE','RELATIONSHIP_CREATE_TIME','RELATIONSHIP_CHANGE_DATE','RELATIONSHIP_CHANGE_TIME','VALID_TO_DATE','VALID_FROM' ]

    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+Acct_User_Relation_File))
    with open("/root/HBase/CaseDetails/"+Acct_User_Relation_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(ACCT_USR_REL_Key, m))
            temp = dictionary['VALID_FROM'].rstrip('\n')
            dictionary['VALID_FROM'] = temp 
            if (dictionary['VALID_FROM'] == '\n'):
                dictionary['VALID_FROM'] = '' 
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/ACCT_USER/"+dictionary['ACCOUNT_ID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")



############################################################################
## Read_Acct(Acct_File)
#  INPUT:Acct_File
#  This subroutine will read Acct_File and Create new file
#  or append to existing Accounts_File which is already created by Read_User()
#  or Read_Acct_User_Relation()
#
############################################################################
def Read_Acct(Acct_File):
    ACCT_Key = ['PARTNER_ID','PARTNER _TYPE _KEY','PARTNER_TYPE','CONTACT_FIRST_NAME','CONTACT_LAST_NAME','ACCOUNT_NAME','SAP_CREATE_DATE','SAP_CREATE_TIME','SAP_CHANGE_DATE','SAP_CHANGE_TIME','HOUSE_NUMBER','STREET_1','STREET_2','STREET_3','STREET_4','CITY','REGION','POSTAL _CODE','COUNTRY','TRANSPORT ZONE','PHONE','EXTENSION','E-MAIL','COMMUNICATION_TYPE_KEY','COMMUNICATION_TYPE','RATING_KEY','RATING','ACCOUNT_TYPE_KEY','ACCOUNT_TYPE','ACCOUNT_CLASS_KEY','ACCOUNT_CLASS','DATA_ORIGIN_KEY','DATA_ORIGIN','SERVICE_RENEWAL_DATE','CUSTOMER_SINCE','COMMON_ID','STATUS','STATUS_KEY','TRAN_BLOCK_REASON_KEY','TRAN_BLOCK_REASON','ARCHIVING_FLAG','ACCOUNT_GROUP_KEY','ACCOUNT_GROUP','LANGUAGE','WEBSITE','PARTNER_GROUPING_KEY','PARTNER_GROUPING','ACCOUNT_SERVICE_LEVEL','ACCOUNT_TEMPERATURE','ANALYSIS_FLAG','AUTHORIZED_FOR_RMA','CITIZENSHIP','COURTESY_CALL','SR_BY_EMAIL','TEMPERATURE_END_DATE','ENTITLEMENT_VALID_TILL','RMA_ENTITLEMENT','SR_ENTITLEMENT','SERVICE_REQUEST_ENTITLEMENT']

    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+Acct_File))
    with open("/root/HBase/CaseDetails/"+Acct_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(ACCT_Key, m))
            if (dictionary['SERVICE_REQUEST_ENTITLEMENT'] == '\n'):
                dictionary['SERVICE_REQUEST_ENTITLEMENT'] = '' 
            temp = dictionary['SERVICE_REQUEST_ENTITLEMENT'].rstrip('\n')
            dictionary['SERVICE_REQUEST_ENTITLEMENT'] = temp 
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/ACCT_USER/"+dictionary['PARTNER_ID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")


############################################################################
## Read_User(User_File)
#  INPUT:User_File
#  This subroutine will read User_File and Create new file
#  or append to existing Accounts_File which is already created by Read_Acct()
#  or Read_Acct_User_Relation()
#
############################################################################
def Read_User(User_File):
    USER_Key = ['PARTNER_ID','PARTNER _TYPE _KEY','PARTNER_TYPE','CONTACT_FIRST_NAME','CONTACT_LAST_NAME','ACCOUNT_NAME','SAP_CREATE_DATE','SAP_CREATE_TIME','SAP_CHANGE_DATE','SAP_CHANGE_TIME','HOUSE_NUMBER','STREET_1','STREET_2','STREET_3','STREET_4','CITY','REGION','POSTAL _CODE','COUNTRY','TRANSPORT ZONE','PHONE','EXTENSION','E-MAIL','COMMUNICATION_TYPE_KEY','COMMUNICATION_TYPE','RATING_KEY','RATING','ACCOUNT_TYPE_KEY','ACCOUNT_TYPE','ACCOUNT_CLASS_KEY','ACCOUNT_CLASS','DATA_ORIGIN_KEY','DATA_ORIGIN','SERVICE_RENEWAL_DATE','CUSTOMER_SINCE','COMMON_ID','STATUS','STATUS_KEY','TRAN_BLOCK_REASON_KEY','TRAN_BLOCK_REASON','ARCHIVING_FLAG','ACCOUNT_GROUP_KEY','ACCOUNT_GROUP','LANGUAGE','WEBSITE','PARTNER_GROUPING_KEY','PARTNER_GROUPING','ACCOUNT_SERVICE_LEVEL','ACCOUNT_TEMPERATURE','ANALYSIS_FLAG','AUTHORIZED_FOR_RMA','CITIZENSHIP','COURTESY_CALL','SR_BY_EMAIL','TEMPERATURE_END_DATE','ENTITLEMENT_VALID_TILL','RMA_ENTITLEMENT','SR_ENTITLEMENT','SERVICE_REQUEST_ENTITLEMENT']

    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+User_File))
    with open("/root/HBase/CaseDetails/"+User_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(USER_Key, m))
            if (dictionary['SERVICE_REQUEST_ENTITLEMENT'] == '\n'):
                dictionary['SERVICE_REQUEST_ENTITLEMENT'] = '' 
            temp = dictionary['SERVICE_REQUEST_ENTITLEMENT'].rstrip('\n')
            dictionary['SERVICE_REQUEST_ENTITLEMENT'] = temp 
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/ACCT_USER/"+dictionary['PARTNER_ID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")


############################################################################
## Read_Date(Date_File)
#  Input: Date_File
#  This subroutine will read Date_File and Create new file
#  or append to existing SR_File which is already created by Read_SR(SR_File)
#  
############################################################################
def Read_Date(Date_File):
    DATE_Key = ['SRID','DATE_TYPE','DATE_STAMP','DURATION','TIME_UNIT']

    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+Date_File))
    with open("/root/HBase/CaseDetails/"+Date_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(DATE_Key, m))
            if (dictionary['TIME_UNIT'] == '\n'):
                dictionary['TIME_UNIT'] = '' 
            temp = dictionary['TIME_UNIT'].rstrip('\n')
            dictionary['TIME_UNIT'] = temp 
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/CaseFiles/"+dictionary['SRID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")


############################################################################
## Read_PartnerFunction(Partner_File)
#  Input: Partner_File
#  This subroutine will read Partner_File and Create new file
#  or append to existing SR_File which is already created by Read_SR(SR_File)
#  
############################################################################
def Read_PartnerFunction(Partner_File):
    PARTNER_Key = ['SRID','PARTNERFUNCTION_NAME','PARTNERFUNCTION_KEY','PARTNERID','PARTNER_NAME']
    newdict = {}
    num_lines = sum(1 for line in open('/root/HBase/CaseDetails/'+Partner_File))
    with open("/root/HBase/CaseDetails/"+Partner_File, 'r') as target:
        for data in islice(target, 1, num_lines):
            m = re.split(('\|\$\@\$\|'), data)
            dictionary = dict(zip(PARTNER_Key, m))
            if (dictionary['PARTNER_NAME'] == '\n'):
                dictionary['PARTNER_NAME'] = ''
            temp = dictionary['PARTNER_NAME'].rstrip('\n')
            dictionary['PARTNER_NAME'] = temp 
            if (dictionary['PARTNERFUNCTION_NAME'] == "Sold-To Party"):
                partnerId = dictionary['PARTNERID']
                SRId = dictionary['SRID']
                newdict[SRId] = partnerId 
                json2 = json.dumps(newdict, ensure_ascii=False)
                newdict.clear()
                with open("/root/HBase/ACCT_USER/SRID_ACCTID_MAP","a+") as temptarget:
                    temptarget.write(json2)
                    temptarget.write("\n") 
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/CaseFiles/"+dictionary['SRID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")


############################################################################
## Read_SR_Notes(SR_NOTES_File)
#  Input: SR_NOTES_File
#  This subroutine will read SR_NOTES_File and Create new file
#  or append to existing SR_File which is already created by Read_SR(SR_File)
#  
############################################################################
def Read_SR_Notes(SR_NOTES_File):
    SRNOTES_Key = ['SRID','NOTE_TYPE_DESC','SAP_NOTE_ID','NOTE_TYPE','ORIGINATOR_SUPERVISOR','ORIGINATOR_THEATER','NOTE_LAST_UPDATE_DATE','NOTE_LAST_UPDATE_TIME','ORIGINATOR_ROLE','CREATE_METHOD','ORIGINATOR_COUNTRY','NOTE_ORIGINATOR','ORIGINATOR_RESPONSIBLE_GROUP','PRIVATE_NOTE','NOTE']
    with open("/root/HBase/CaseDetails/"+SR_NOTES_File,'r') as target:
        target.seek(298)
        data = target.readlines()
        str1 = ''.join(data)
        m = re.split('\|\#\$\#\%\$\|\\n',str1)
        for count in range(0,(len(m) -1)):
            str2 = ''.join(m[count])
            n = re.split('\|\$\@\$\|',str2)
            dictionary = dict(zip(SRNOTES_Key, n))
            json1 = json.dumps(dictionary, ensure_ascii=False)
            with open("/root/HBase/CaseFiles/"+dictionary['SRID'],"a+") as newtarget:
                newtarget.write(json1)
                newtarget.write("\n")
############################################################################
