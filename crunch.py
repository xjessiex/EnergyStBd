#!/usr/bin/env python
# coding: utf-8


import pandas as pd


def populate_charge_discharge_values(
    file_path,
    max_budget,
    max_capacity,
    discharge_time,
    roundtrip_efficiency,
    lmp_threshold,
    capacity_reserve,
):
    """
    Description of what the function does.

    :param file_path: file path
    :param max_budget: dollars
    :param max_capacity: MW
    :param discharge_time: hours
    :param roundtrip_efficiency: Decimal
    :param lmp_threshold: dollars
    :param capacity_reserve: percent
    :return: pandas Dataframe
    """
    
    df = pd.read_csv(file_path)

    # Initialize discharge and charge capacities
    #The roundtrip efficiency is the relationship 
    # between the discharge capacity and the charge capacity
    # So if you get 5 MW of discharge in an hour, 
    # since the roundtrip efficiency is 80% you only get 4 MW of charge in an hour
    discharge_capacity = max_capacity / discharge_time
    charge_capacity = roundtrip_efficiency * discharge_capacity
 
    # Calculate charge and discharge thresholds
    #The charge threshold is the max you would want to trigger a charge at
    charge_threshold = max_capacity - discharge_capacity
    #Discharge threshold is the min you’d want to discharge to
    discharge_threshold = capacity_reserve * max_capacity

    # Initialize starting values for action, beginning and ending budgets, and capacity
    #nan is like a placeholder for a new column and float indicates it is a decimal
    df['ACTION'] = None

    df['BCAPACITY'] = float('nan')
    df['ECAPACITY'] = float('nan')
    df['BCAPACITY'][0] = max_capacity


    # beginning budget and ending budget for each hour
    df['BBUDGET']= float('nan')
    df['EBUDGET']= float('nan')
    df['BBUDGET'][0]= max_budget


    # Iterate through dataframe to ACTION, BUDGET, and CAPACITY

    for index, row in df.iterrows():
        # set ACTION
        #If the LMP (energy price) is less than the lmp threshold (e.g. $30)
        # and the capacity is less or equal to the max you would want to trigger a charge at
        # (e.g. 15 in this case) we charge the battery 
        
        
        if index==1:
            print('LMP_PRC: '+str(df['LMP_PRC'][index]))
            print('BCAPACITY: '+str(df['BCAPACITY'][index]))
            print('lmp_threshold: '+str(lmp_threshold))
            print('charge_threshold: '+str(charge_threshold))

        if index == 0: #handles budget and action for first row (0)
            #set action for first row            
            if (
                df['LMP_PRC'][index] < lmp_threshold and
                df['BCAPACITY'][index] <= charge_threshold

            ):
                df['ACTION'][index] = 'CHARGE'
                df['ECAPACITY'][index] = df['BCAPACITY'][index] + charge_capacity
            elif (
                # Todo: determing if RU_CLR_PRC signals a discharge
                df['LMP_PRC'][index] >= lmp_threshold and
                df['BCAPACITY'][index] >= discharge_threshold
            ):
                df['ACTION'][index] = 'DISCHARGE'
                df['ECAPACITY'][index] = df['BCAPACITY'][index] - discharge_capacity
            else:
                df['ACTION'][index] = 'NO ACTION'
                df['ECAPACITY'][index] = df['BCAPACITY'][index]  
                #end set action for first row
            
            if(
                df['ACTION'][index] == 'DISCHARGE'
                ):
                df['BBUDGET'][0] = max_budget
                df['EBUDGET'][0] = max_budget  + max(df['LMP_PRC'][0],df['RU_CLR_PRC'][0]) * discharge_capacity
            elif (
                df['ACTION'][0] == 'CHARGE'
            ):
                df['BBUDGET'][0] = max_budget
                df['EBUDGET'][0] = max_budget - df['LMP_PRC'][0] * charge_capacity           
            else:
                df['BBUDGET'][0] = max_budget
                df['EBUDGET'][0] = df['BBUDGET'][0]

        if index != 0:  # skip initialized values
          
             #set action for not first row       
            if (
                df['LMP_PRC'][index] < lmp_threshold and
                df['ECAPACITY'][index-1] <= charge_threshold

            ):
                df['ACTION'][index] = 'CHARGE'
                df['ECAPACITY'][index] = df['BCAPACITY'][index] + charge_capacity
            elif (
                # Todo: determing if RU_CLR_PRC signals a discharge
                df['LMP_PRC'][index] >= lmp_threshold and
                df['ECAPACITY'][index-1] >= discharge_threshold
            ):
                df['ACTION'][index] = 'DISCHARGE'
                df['ECAPACITY'][index] = df['BCAPACITY'][index] - discharge_capacity
            else:
                df['ACTION'][index] = 'NO ACTION'
                df['ECAPACITY'][index] = df['BCAPACITY'][index]   

           #end set action for not first row 
        
            # set BUDGET and CAPACITY
            #BUDGET = For Discharge, BUDGET+ (MAX of (LMP_PRC,RU_CLR_PRC) * DISCHARGED_CAP)
            last_budget = df['EBUDGET'][index-1]
            last_capacity = df['ECAPACITY'][index-1]
            if (
                df['ACTION'][index] == 'DISCHARGE'
            ):
                df['BBUDGET'][index] = last_budget
                df['EBUDGET'][index] = last_budget + max(df['LMP_PRC'][index],df['RU_CLR_PRC'][index]) * discharge_capacity
            elif (
                df['ACTION'][index] == 'CHARGE'
            ):
                df['BBUDGET'][index] = last_budget
                df['EBUDGET'][index] = last_budget - df['LMP_PRC'][index] * charge_capacity
            else:
                df['BBUDGET'][index] = last_budget 
                df['EBUDGET'][index] = df['BBUDGET'][index]
            #SET CAPACITY
            if (
                df['ACTION'][index] == 'DISCHARGE'
            ):
                df['BCAPACITY'][index] = last_capacity
                df['ECAPACITY'][index] = last_capacity - discharge_capacity
            elif (
                df['ACTION'][index] == 'CHARGE'
            ):
                df['BCAPACITY'][index] = last_capacity
                df['ECAPACITY'][index] = last_capacity + charge_capacity            
            else:
                df['BCAPACITY'][index] = last_capacity
                df['ECAPACITY'][index] = last_capacity
    return df



