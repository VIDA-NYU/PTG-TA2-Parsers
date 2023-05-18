import datetime
import calendar
import sqlite3
import pandas as pd

# import packages to write a json file
import os
import json
import argparse

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
    # read-only connection
    conn = create_connection(db_file)
    # create the dataframe from a query
    query = "SELECT * FROM " + table_name
    df = pd.read_sql_query(query, conn, chunksize=100)
    return df

# Convert date string to PTG timestamp format (epoch)
def  utc_date_to_epoch(utc_date_str):
    # utc_date_str = '2022-09-28 17:28:35.480247'
    datetime_value = datetime.datetime.strptime(utc_date_str, '%Y-%m-%d %H:%M:%S.%f')
    dt_now = datetime.datetime.now()
    # replace with current YYMMDD info so objects and actions can be synchronized.
    # this is done because action timestamps doesnt have YYMMDD info
    # when there is no YYMMDD info, the default YYMMDD is 1900-01-01 which generate a different epoch value
    dt = datetime_value.replace(year=dt_now.year, month=dt_now.month, day=dt_now.day) 
    epoch_format = calendar.timegm(dt.timetuple())
    ptg_timestamp_format = str(epoch_format* 1000)+'-0'
    return ptg_timestamp_format

def get_json_values(sql_df):
    
    target_objects = ['fdvcp', 'mfd inboard', 'mfd outboard', 'cdu']
    json_values = []

    for chunk in sql_df:
        
        df2 = chunk[chunk['timestamp'].notnull()] # remove null timestamps
        df3 = df2[pd.to_datetime(df2['timestamp'], errors='coerce',format='%Y-%m-%d %H:%M:%S.%f').notnull()] # check correct format
        uniqueTs = df3['timestamp'].unique()
    
        for ts in uniqueTs:
            detected_objects_per_ts = chunk[chunk['timestamp'] == ts]['component_id'].values
            values = []
            for obj in target_objects:
                if(obj in list(detected_objects_per_ts)):
                    values.append({
                        "xyxyn":[0,0,0,0],
                        "confidence":1,
                        "class_id":1,
                        "label":obj
                        })
            json_values.append({
                "frame_type":123,
                "values": values,
                "timestamp": utc_date_to_epoch(ts)
                })

    sorted_json_data = sorted(json_values, key=lambda d: d['timestamp'].split('-')[0])
    return sorted_json_data

def parse_row( row, formattedObject ):

    gazeOrigin = { 'x': row['origin_x'], 'y': row['origin_y'], 'z': row['origin_z'] }
    gazeDirection = { 'x': row['direction_x'], 'y': row['direction_y'], 'z': row['direction_z'] }
    timestamp = f'{int(row["timestamp"])}-0 ' 

    currentRow = {
        "GazeOrigin": gazeOrigin,
        "GazeDirection": gazeDirection,
        "timestamp": timestamp
    }

    formattedObject.append(currentRow)

def main( input: str, output: str ):

    sql_df = get_dataframe_from_sqlite(input, "hl2_rgb_bounding_boxes")
    json_perception = get_json_values(sql_df)

    outputPath = os.path.join(output, 'detic:image.json')
    if( not os.path.exists(output) ):
        os.makedirs(output)

    with open(outputPath, 'w') as f:
        f.write(json.dumps(json_perception))

if __name__ == "__main__":

    ## Example: 
    ## python perception-parser.py -i /foo/0293_11.sqlite -o /bar/0293_11

    parser = argparse.ArgumentParser(description='This scripts aims to parse the Ocarina data stored into SQLite files to NYU backend format')
    parser.add_argument('-i', '--input', nargs=1, required=True, default='')
    parser.add_argument('-o', '--output', nargs=1, required=True, default='')

    args = parser.parse_args()
    main(args.input[0],args.output[0])