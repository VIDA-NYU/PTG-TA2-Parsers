# import packages to read sqlite file
import sqlite3
import pandas as pd
import time  
import datetime
import calendar
import argparse

# import packages to write a json file
import os
import json



def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, uri=True)
    except Exception as e:
        print(e)
    return conn

def get_dataframe_from_sqlite(db_file, table_name):
    # fancy read-only connection
    conn = create_connection(db_file)
    # create the dataframe from a query
    query = "SELECT * FROM " + table_name
    df = pd.read_sql_query(query, conn)
    return df

# Convert date string (HHMMSS) to PTG timestamp format (epoch)
def  utc_hms_date_to_epoch(utc_date_str):
    # utc_date_str = '17:29:43.005'
    datetime_value = datetime.datetime.strptime(utc_date_str, '%H:%M:%S.%f')
    dt_now = datetime.datetime.now()
    # set year, month, day of the datetime object to current date's year, month and day via replace
    # since there is no Year, Month, Day info (this info is required to computed a positive epoch value. otherwise it will be negative (1900-01-01))
    dt = datetime_value.replace(year=dt_now.year, month=dt_now.month, day=dt_now.day) # replace with current YYMMDD info
    epoch_format = calendar.timegm(dt.timetuple())
    ptg_timestamp_format = str(epoch_format*1000)+'-0'
    return ptg_timestamp_format   

def get_actions_json(df):
    json_values = []
    unique_actions = df["Event"].unique()
    
    df2 = df[df['timestamp'].notnull()] # remove null timestamps
    df3 = df2[pd.to_datetime(df2['timestamp'], errors='coerce',format='%H:%M:%S.%f').notnull()] # check correct format
    uniqueTs = df3['timestamp'].unique()
    for ts in uniqueTs:
        detected_actions_per_ts = df[df['timestamp'] == ts]['Event'].values
        row_dic = {"timestamp": utc_hms_date_to_epoch(ts) } # get time from sqlite file
        for action in unique_actions:
            if(action in list(detected_actions_per_ts)):
                row_dic[action] = 1
            else:
                row_dic[action] = 0
        json_values.append(row_dic)        
        sorted_json_data = sorted(json_values, key=lambda d: d['timestamp'].split('-')[0])     
    return sorted_json_data

def get_steps_json(df):
    json_values = []
    
    df2 = df[df['timestamp'].notnull()] # remove null timestamps
    df3 = df2[pd.to_datetime(df2['timestamp'], errors='coerce',format='%H:%M:%S.%f').notnull()] # check correct format
    uniqueTs = df3['timestamp'].unique()
    for ts in uniqueTs:
        detected_steps_per_ts = df[df['timestamp'] == ts]['Step'].values
        step = list(detected_steps_per_ts)[0]
        timestamp_value = utc_hms_date_to_epoch(ts)# get time from sqlite file
        row_dic = {"step_id": step,
                    "step_status": "NEW",
                    "step_description": "",
                    "error_status": False,
                    "error_description": "",
                    "timestamp": timestamp_value
                   }
        json_values.append(row_dic)        
        sorted_json_data = sorted(json_values, key=lambda d: d['timestamp'].split('-')[0])     
    return sorted_json_data

def main( input: str, output: str ):

    sql_df = get_dataframe_from_sqlite(input, "ocarina_mission_log")
    json_actions = get_actions_json(sql_df)

    json_steps = get_steps_json(sql_df)

    outputPathActions = os.path.join(output, 'egovlp:action:steps.json')
    outputPathSteps = os.path.join(output, 'reasoning:check_status.json')

    if( not os.path.exists(output) ):
        os.makedirs(output)

    with open(outputPathActions, 'w') as f:
        f.write(json.dumps(json_actions))
    with open(outputPathSteps, 'w') as f:
        f.write(json.dumps(json_steps))

if __name__ == "__main__":

    ## Example: 
    ## python reasoning-parser.py -i /foo/0293_11.sqlite -o /bar/0293_11

    parser = argparse.ArgumentParser(description='This scripts aims to parse the Ocarina data stored into SQLite files to NYU backend format')
    parser.add_argument('-i', '--input', nargs=1, required=True, default='')
    parser.add_argument('-o', '--output', nargs=1, required=True, default='')

    args = parser.parse_args()
    main(args.input[0],args.output[0])