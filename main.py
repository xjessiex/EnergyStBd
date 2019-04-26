#!/usr/bin/env python
# coding: utf-8


import os
import sys
import csv # to import data

import requests #to send HTTP requests without the need to manually add query strings to your URLs, or to form-encode your POST data.
from io import BytesIO #to create text or binary streams from different types of data.
from zipfile import ZipFile
from xml.etree import ElementTree #

class EnergyBid:
    # get working directory
    dirpath = os.getcwd()
    # get data directory
    datadir = os.path.join(dirpath, "data")

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


#%% download LMP and AS files

    def QueryAPI(self, query_name):

        api_url=f'http://oasis.caiso.com/oasisapi/SingleZip?queryname={query_name}&startdatetime={self.startdate}T07:00-0000&enddatetime={self.enddate}T07:00-0000&market_run_id=DAM&version=1'
        response = requests.get(api_url)
        zipfile = ZipFile(BytesIO(response.content))
        output_url= self.datadir # Path specifies a different directory to extract to.
        zipfile.extractall(output_url)
        #Extract all members from the archive to the current working directory.

    #Do we let customers pick?
    #QueryAPI('PRC_LMP')
    #QueryAPI('PRC_AS')


def main():
    test = EnergyBid()
    test.directory()
    test.QueryAPI('PRC_LMP')
    test.QueryAPI("PRC_AS")


if __name__ == "__main__":
    main()

