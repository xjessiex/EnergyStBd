#!/usr/bin/env python
# coding: utf-8


import requests
#Requests allows you to send HTTP requests without the need to manually add query strings to your URLs, or to form-encode your POST data.
from io import BytesIO
#A way to create text or binary streams from different types of data.
from zipfile import ZipFile
import os

cwd = os.getcwd()

#import datetime

#Set Date

#%%

def QueryAPI(query_name):
    api_url=f'http://oasis.caiso.com/oasisapi/SingleZip?queryname={query_name}&startdatetime=20180919T07:00-0000&enddatetime=20180920T07:00-0000&market_run_id=DAM&version=1'
    response = requests.get(api_url)
    zipfile = ZipFile(BytesIO(response.content))
    output_url="/data/"
    zipfile.extractall(output_url)
    #Extract all members from the archive to the current working directory.
    # Path specifies a different directory to extract to.

QueryAPI('PRC_LMP')
QueryAPI('PRC_AS')
