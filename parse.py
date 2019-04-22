#!/usr/bin/env python3
#Make sure the file is executable if you plan to run it as a module
#>>>./parse.py Data/Raw/
import os
import sys
from xml.etree import ElementTree
import csv

directory = sys.argv[1]

#for file_name in os.listdir(directory):
    #if file_name.endswith('.xml'):
        #full_file = os.path.join(directory, file_name)
        #print(full_file)

        #dom = ElementTree.parse(full_file)
        #for value in dom.findall("./ns:MessagePayload/ns:RTO/ns:REPORT_ITEM/ns:REPORT_DATA/[ns:RESOURCE_NAME='TH_NP15_GEN-APND']/ns:VALUE", {'ns': 'http://www.caiso.com/soa/OASISReport_v1.xsd'}):
            #print("  " + value.text)
ns='{http://www.caiso.com/soa/OASISReport_v1.xsd}'
#The root will serve as the NameSpace.  
#dom = ElementTree.parse(full_file)
#root = dom.getroot()
#for value in root.findall

file_index=0

def format_datetime(datetime_, _timezone=('US/Pacific')):
    """
    Converts datetime object to yyyymmddThh24:miZ format.

    :param datetime_: datetime object
    :param timezone_: pytz.timezone object
    :return: yyyymmddThh24:miZ formatted string
    """
    # set timezone if datetime_ has no timezone
    if not datetime_.tzinfo:
        datetime_ = _timezone.localize(datetime_)

    return datetime_.strftime('%Y%m%dT%H:%M%z')

for file_name in os.listdir(directory):
    if file_name.endswith('.xml'):
        file_index+=1
        full_file = os.path.join(directory, file_name)

        print(full_file)
        tree = ElementTree.parse(full_file)
        root = tree.getroot()
        print(root.tag)
        target_filename='target_'+str(file_index)+'.csv'

        print('Processing file ' + str(file_index))

        with open(target_filename, 'w', newline='') as r:
            writer = csv.writer(r)
            writer.writerow(['RTO', 'MARKET TYPE', 'DATA ITEM', 'PRICE','LOCATION','START TIME','END TIME'])  # WRITING HEADERS
            #for child in root:
                #print (child.tag)
            
            for message in root.findall(ns+'MessagePayload'):
                for rto in message.findall(ns+'RTO'):
                    name = rto.find(ns+'name').text    
                    for item in rto.findall(ns+'REPORT_ITEM'):
                        for header in item.findall(ns+'REPORT_HEADER'):
                            mkt = header.find(ns+'MKT_TYPE').text
                        for reportdata in item.findall(ns+'REPORT_DATA'):
                            dataitem = reportdata.find(ns+'DATA_ITEM').text
                            price = reportdata.find(ns+'VALUE').text  
                            resource = reportdata.find(ns+'RESOURCE_NAME').text
                            starttime = reportdata.find(ns+'INTERVAL_START_GMT').text
                            endtime = reportdata.find(ns+'INTERVAL_END_GMT').text
                            writer.writerow([name,mkt,dataitem,price,resource,starttime,endtime])