#!/usr/bin/env python
# coding: utf-8
import os
import sys
import csv
import numpy as np
import pandas as pd
# import matplotlib
import time

import requests # to send HTTP requests without the need to manually add query strings to your URLs, or to form-encode your POST data.
from io import BytesIO # to create text or binary streams from different types of data.
from zipfile import ZipFile
from xml.etree import ElementTree
from datetime import datetime, timedelta

class EnergyBid:
    """
    Description of what the function does.
    :param dirpath: file path
    :param datadir: data file path
    :param max_budget: dollars
    :param max_capacity: MW
    :param discharge_time: hours
    :param roundtrip_efficiency: Decimal
    :param lmp_threshold: dollars
    :param capacity_reserve: percent
    """

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
        # pick dates
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
        # delete files that contains "LMP_DAM_LMP", "PRC_AS_DAM"
        for filename in os.listdir(self.datadir):
            if query_name in filename:
                os.remove(os.path.join(self.datadir, filename))
        startdate_dt = datetime.strptime(self.startdate, '%Y%m%d')
        enddate_dt = datetime.strptime(self.enddate, '%Y%m%d')

        # check if input multiple days
        if (enddate_dt - startdate_dt).days > 1:
            # construct a moving start and end scrapping date
            split_start_date_dt = startdate_dt
            split_end_date_dt = startdate_dt + timedelta(days=1)
            while (enddate_dt - split_end_date_dt).days > 0:
                split_start_date_str = split_start_date_dt.strftime('%Y%m%d')
                split_end_date_str = split_end_date_dt.strftime('%Y%m%d')
                api_url =f'http://oasis.caiso.com/oasisapi/SingleZip?queryname={query_name}&startdatetime={split_start_date_str}T07:00-0000&enddatetime={split_end_date_str}T07:00-0000&market_run_id=DAM&version=1'
                print(f'pulling from API:{api_url}')
                response = requests.get(api_url) # HTTP GET request
                print(f'response:{response.content}')
                zipfile = ZipFile(BytesIO(response.content))
                output_url = self.datadir # Path specifies a different directory to extract to.
                zipfile.extractall(output_url)
                split_start_date_dt = split_start_date_dt + timedelta(days=1)
                split_end_date_dt = split_end_date_dt + timedelta(days=1)

                # take a 10sec break during scrapping to prevent throttle
                time.sleep(10)
                #Extract all members from the archive to the current working directory.

        else:
            api_url =f'http://oasis.caiso.com/oasisapi/SingleZip?queryname={query_name}&startdatetime={self.startdate}T07:00-0000&enddatetime={self.enddate}T07:00-0000&market_run_id=DAM&version=1'
            response = requests.get(api_url) # HTTP GET request
            zipfile = ZipFile(BytesIO(response.content))
            output_url = self.datadir # Path specifies a different directory to extract to.
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
        words = ["LMP_DAM_LMP", "PRC_AS_DAM"]

        # set up empty compile csv with headers for LMP and AS prices
        for i in words:
            with open(i +'.csv', 'w') as r:
                writer = csv.writer(r)
                writer.writerow(
                    ['RTO', 'MARKET TYPE', 'DATA ITEM', 'PRICE', 'LOCATION', 'START TIME',
                     'END TIME'])  # WRITING HEADERS

        # loop through each day of prices and append them in the compile csv
        for file_name in os.listdir(self.datadir):
            # create empty csv
            if any(name in file_name for name in words):
                self.file_index += 1
                full_file = os.path.join(self.datadir, file_name)

                #print(full_file)
                tree = ElementTree.parse(full_file)
                root = tree.getroot()
                print(root.tag)
                item = [name for name in words if name in file_name]
                target_filename = str(item[0]) + '.csv'

                print('Processing file ' + str(self.file_index))

                with open(target_filename, 'a') as r:
                    writer = csv.writer(r)

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

    def mergedf(self):
        #merge pricing for AS and LMP

        # process LMP file
        lmpdf = pd.read_csv(os.path.join(self.dirpath, "LMP_DAM_LMP.csv"))
        # filter location
        lmpdf_f = lmpdf[lmpdf["LOCATION"] == "TH_NP15_GEN-APND"]
        lmpdf_f.drop(['DATA ITEM', "LOCATION"], axis=1)
        # change column name
        lmpdf_f = lmpdf_f.rename(columns={'PRICE': 'LMP_PRC'})

        # process AS file
        asdf = pd.read_csv(os.path.join(self.dirpath, "PRC_AS_DAM.csv"))
        # filter price
        asdf = asdf[asdf["DATA ITEM"] == "RU_CLR_PRC"]

        # merge price for AS_CAISO and AS_CAISO_EXP
        asdf_ac = asdf[asdf["LOCATION"] == "AS_CAISO"]
        asdf_acc = asdf[asdf["LOCATION"] == "AS_CAISO_EXP"]
        asdf_m = pd.merge(asdf_ac, asdf_acc, on="START TIME")
        asdf_m["SUM_PRC"] = asdf_m["PRICE_x"] + asdf_m["PRICE_y"]
        # asdf_f.head()

        asdf_f = asdf_m[["START TIME", "SUM_PRC"]]
        asdf_f = asdf_f.rename(columns={'SUM_PRC':'RU_CLR_PRC'})

        self.mergedf = pd.merge(lmpdf_f, asdf_f, on="START TIME")


        print(f'we now have {self.mergedf.shape[0]} hours in the price dataframe!')


    def inputbudget(self):
        print("The files are downloaded and parsed.")
        self.max_budget = int(input("Please enter the maximum budget (e.g. 200)\n"))
        self.max_capacity = int(input("Please enter the maximum MW capacity (e.g. 20)\n"))
        self.discharge_time = int(input("Please enter the discharge hours (e.g. 4)\n"))
        self.roundtrip_efficiency = float(input("Please enter the roundtrip efficiency percent(e.g. 0.8)\n"))
        self.lmp_threshold = int(input("Please enter the $ LMP threshold (e.g. 30)\n"))
        self.capacity_reserve = int(input("Please enter the capacity reserve (e.g. 10)\n"))

        self.discharge_capacity = self.max_capacity / self.discharge_time
        self.charge_capacity = self.roundtrip_efficiency * self.discharge_capacity

        # Calculate charge and discharge thresholds
        # The charge threshold is the max you would want to trigger a charge at
        self.charge_threshold = self.max_capacity - self.discharge_capacity
        # Discharge threshold is the min you’d want to discharge to
        self.discharge_threshold = self.capacity_reserve * self.max_capacity


    def outputbudget(self):
        pd.options.mode.chained_assignment = None  # default='warn'
        # transfer all the necessary variables
        _max_budget = self.max_budget
        _max_capacity = self.max_capacity
        _discharge_time = self.discharge_time
        _roundtrip_efficiency = self.roundtrip_efficiency
        _lmp_threshold = self.lmp_threshold
        _capacity_reserve = self.capacity_reserve
        _charge_capacity = self.charge_capacity
        _charge_threshold = self.charge_threshold
        _discharge_threshold = self.discharge_threshold
        _discharge_capacity = self.discharge_capacity
        df = self.mergedf

        df['ACTION'] = None
        df['BCAPACITY'] = np.nan
        df['ECAPACITY'] = np.nan
        df['BCAPACITY'][0] = _max_capacity

        # beginning budget and ending budget for each hour
        df['BBUDGET'] = np.nan
        df['EBUDGET'] = np.nan
        df['BBUDGET'][0] = _max_budget

        # Iterate through dataframe to ACTION, BUDGET, and CAPACITY
        for index, row in df.iterrows():
            # set ACTION
            # If the LMP (energy price) is less than the lmp threshold (e.g. $30)
            # and the capacity is less or equal to the max you would want to trigger a charge at
            # (e.g. 15 in this case) we charge the battery
            if index == 1:
                print('LMP_PRC: ' + str(df['LMP_PRC'][index]))
                print('BCAPACITY: ' + str(df['BCAPACITY'][index]))
                print('lmp_threshold: ' + str(_lmp_threshold))
                print('charge_threshold: ' + str(_charge_threshold))

            if index == 0:  # handles budget and action for first row (0)
                # set action for first row
                if (
                    df['LMP_PRC'][index] < _lmp_threshold and
                    df['BCAPACITY'][index] <= _charge_threshold
                ):
                    df['ACTION'][index] = 'CHARGE'
                    df['ECAPACITY'][index] = df['BCAPACITY'][index] + _charge_capacity
                elif (
                    # Todo: determing if RU_CLR_PRC signals a discharge
                    df['LMP_PRC'][index] >= _lmp_threshold and
                    df['BCAPACITY'][index] > _discharge_capacity #battery limitation
                ):
                    df['ACTION'][index] = 'DISCHARGE'
                    df['ECAPACITY'][index] = df['BCAPACITY'][index] - _discharge_capacity
                else:
                    df['ACTION'][index] = 'NO ACTION'
                    df['ECAPACITY'][index] = df['BCAPACITY'][index]
                    # end set action for first row

                if (
                    df['ACTION'][index] == 'DISCHARGE'
                ):
                    df['BBUDGET'][0] = _max_budget
                    df['EBUDGET'][0] = _max_budget + max(df['LMP_PRC'][0], df['RU_CLR_PRC'][0]) * _discharge_capacity
                elif (
                    df['ACTION'][0] == 'CHARGE'
                ):
                    df['BBUDGET'][0] = _max_budget
                    df['EBUDGET'][0] = _max_budget - df['LMP_PRC'][0] * _charge_capacity
                else:
                    df['BBUDGET'][0] = _max_budget
                    df['EBUDGET'][0] = df['BBUDGET'][0]

            if index != 0:  # skip initialized values

                # set action for not first row
                if (
                    df['LMP_PRC'][index] < _lmp_threshold and
                    df['ECAPACITY'][index - 1] <= _charge_threshold
                ):
                    df['ACTION'][index] = 'CHARGE'
                    df['ECAPACITY'][index] = df['BCAPACITY'][index] + _charge_capacity
                elif (
                    # Todo: determing if RU_CLR_PRC signals a discharge
                    df['LMP_PRC'][index] >= _lmp_threshold and
                    df['ECAPACITY'][index - 1] >= _discharge_capacity
                ):
                    df['ACTION'][index] = 'DISCHARGE'
                    df['ECAPACITY'][index] = df['BCAPACITY'][index] - _discharge_capacity
                else:
                    df['ACTION'][index] = 'NO ACTION'
                    df['ECAPACITY'][index] = df['BCAPACITY'][index]

                # end set action for not first row

                # set BUDGET and CAPACITY
                # BUDGET = For Discharge, BUDGET+ (MAX of (LMP_PRC,RU_CLR_PRC) * DISCHARGED_CAP)
                last_budget = df['EBUDGET'][index - 1]
                last_capacity = df['ECAPACITY'][index - 1]
                if (
                    df['ACTION'][index] == 'DISCHARGE'
                ):
                    df['BBUDGET'][index] = last_budget
                    df['EBUDGET'][index] = last_budget + max(df['LMP_PRC'][index],
                                                             df['RU_CLR_PRC'][index]) * _discharge_capacity
                elif (
                    df['ACTION'][index] == 'CHARGE'
                ):
                    df['BBUDGET'][index] = last_budget
                    df['EBUDGET'][index] = last_budget - df['LMP_PRC'][index] * _charge_capacity
                else:
                    df['BBUDGET'][index] = last_budget
                    df['EBUDGET'][index] = df['BBUDGET'][index]
                # SET CAPACITY
                if (
                    df['ACTION'][index] == 'DISCHARGE'
                ):
                    df['BCAPACITY'][index] = last_capacity
                    df['ECAPACITY'][index] = last_capacity - _discharge_capacity
                elif (
                    df['ACTION'][index] == 'CHARGE'
                ):
                    df['BCAPACITY'][index] = last_capacity
                    df['ECAPACITY'][index] = last_capacity + _charge_capacity
                else:
                    df['BCAPACITY'][index] = last_capacity
                    df['ECAPACITY'][index] = last_capacity
        self.output = df
        print(self.output)

    def saveresult(self):
        self.output.to_csv("output_table.csv", index=False)
        
def main():
    test = EnergyBid()
    test.directory()
    test.QueryAPI('PRC_LMP')
    test.QueryAPI("PRC_AS")
    test.parsexml()
    test.mergedf()
    test.inputbudget()
    test.outputbudget()
    test.saveresult()

if __name__ == "__main__":
    main()



