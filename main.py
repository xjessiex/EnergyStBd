#!/usr/bin/env python
# coding: utf-8
import os
import sys
import csv
import numpy as np
import pandas as pd
import matplotlib

import requests #to send HTTP requests without the need to manually add query strings to your URLs, or to form-encode your POST data.
from io import BytesIO #to create text or binary streams from different types of data.
from zipfile import ZipFile
from xml.etree import ElementTree

class EnergyBid:
    # get working directory
    dirpath = os.getcwd()
    # get data directory
    datadir = os.path.join(dirpath, "data")

    # Parsing
    # ns = '{http://www.caiso.com/soa/OASISReport_v8.xsd}'
    ns = '{http://www.caiso.com/soa/OASISReport_v1.xsd}' #original

    file_index = 0

    def __init__(self):
        print("Thank you for using the energy bidding optimizer!")
        self.startdate = input("Please enter the start date you want to inspect (yyyymmdd)\n")
        self.enddate = input("Please also enter the end date you want to inspect (yyyymmdd) \n")

    def directory(self):
        # confirm working directory
        dirname = os.path.basename(self.dirpath)
        datname = os.path.basename(self.datadir)
        print("Directory name is : " + dirname)
        print("XLM files are temporarily stored in: " + datname)


#%% download LMP and AS files and extract them from zip files

    def QueryAPI(self, query_name):

        api_url=f'http://oasis.caiso.com/oasisapi/SingleZip?queryname={query_name}&startdatetime={self.startdate}T07:00-0000&enddatetime={self.enddate}T07:00-0000&market_run_id=DAM&version=1'
        response = requests.get(api_url) # HTTP GET request
        zipfile = ZipFile(BytesIO(response.content))
        output_url= self.datadir # Path specifies a different directory to extract to.
        zipfile.extractall(output_url)
        #Extract all members from the archive to the current working directory.

    #Do we let customers pick?
    #QueryAPI('PRC_LMP')
    #QueryAPI('PRC_AS')

    def format_datetime(self, _datetime, _timezone=('US/Pacific')):
    # set timezone if datetime_ has no timezone
        if not _datetime.tzinfo:
            datetime_ = _timezone.localize(_datetime)
        return _datetime.strftime('%Y%m%dT%H:%M%z')


#%% parsing
    # we only want to process PRC_LMP and PRC_AS files
    # corresponding data items: NS_CLR_PRC (NonSpin Cleared Price)

    def parsexml(self):
        for file_name in os.listdir(self.datadir):
            words = ["LMP_DAM_LMP","PRC_AS_DAM"]
            for i in words:
                if i in file_name:
                    self.file_index += 1
                    full_file = os.path.join(self.datadir, file_name)

                    print(full_file)
                    tree = ElementTree.parse(full_file)
                    root = tree.getroot()
                    print(root.tag)
                    target_filename = 'target_' + str(self.file_index) + '.csv'

                    print('Processing file ' + str(self.file_index))

                    with open(target_filename, 'w', newline='') as r:
                        writer = csv.writer(r)
                        writer.writerow(
                            ['RTO', 'MARKET TYPE', 'DATA ITEM', 'PRICE', 'LOCATION', 'START TIME', 'END TIME'])  # WRITING HEADERS

                        for message in root.findall(self.ns + 'MessagePayload'):
                            for rto in message.findall(self.ns + 'RTO'):
                                name = rto.find(self.ns + 'name').text
                                for item in rto.findall(self.ns + 'REPORT_ITEM'):
                                    for header in item.findall(self.ns + 'REPORT_HEADER'):
                                        mkt = header.find(self.ns + 'MKT_TYPE').text
                                    for reportdata in item.findall(self.ns + 'REPORT_DATA'):
                                        dataitem = reportdata.find(self.ns + 'DATA_ITEM').text
                                        price = reportdata.find(self.ns + 'VALUE').text
                                        resource = reportdata.find(self.ns + 'RESOURCE_NAME').text
                                        starttime = reportdata.find(self.ns + 'INTERVAL_START_GMT').text
                                        endtime = reportdata.find(self.ns + 'INTERVAL_END_GMT').text
                                        writer.writerow([name, mkt, dataitem, price, resource, starttime, endtime])


def main():
    test = EnergyBid()
    test.directory()
    test.QueryAPI('PRC_LMP')
    test.QueryAPI("PRC_AS")
    test.parsexml()

if __name__ == "__main__":
    main()

