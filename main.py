#!/usr/bin/env python
# coding: utf-8

import os 
import sys
import csv # to import data

import requests #to send HTTP requests without the need to manually add query strings to your URLs, or to form-encode your POST data.
from io import BytesIO #to create text or binary streams from different types of data.
from zipfile import ZipFile
from xml.etree import ElementTree # 



dirpath = os.getcwd() # get working directory
# confirm working directory
foldername = os.path.basename(dirpath)
print("Directory name is : " + foldername)

#import datetime

#Set Date

#%% download LMP and AS files

def QueryAPI(query_name):
    api_url=f'http://oasis.caiso.com/oasisapi/SingleZip?queryname={query_name}&startdatetime=20180919T07:00-0000&enddatetime=20180920T07:00-0000&market_run_id=DAM&version=1'
    response = requests.get(api_url)
    zipfile = ZipFile(BytesIO(response.content))
    output_url= dirpath
    zipfile.extractall(output_url)
    #Extract all members from the archive to the current working directory.
    # Path specifies a different directory to extract to.

QueryAPI('PRC_LMP')
QueryAPI('PRC_AS')
#%% parse XML files

 # use command line argument



