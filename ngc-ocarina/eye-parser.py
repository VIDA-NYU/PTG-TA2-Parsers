import argparse
import json
import numpy as np
import sqlite3
import pandas as pd
import os

def read_db( inputPath: str ):

    conn = sqlite3.connect(inputPath)
    df = pd.read_sql("SELECT timestamp, origin_x, origin_y, origin_z, direction_x, direction_y, direction_z FROM hl2_gaze", conn)

    ## parsing timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce') 

    ## dropping all NaN columns
    df.dropna(axis=0, inplace=True)
    
    ## transforming into miliseconds
    df['timestamp'] = df['timestamp'].values.astype(np.int64) // 10 ** 6

    formattedObject = []
    df.apply( lambda row: parse_row(row, formattedObject), axis=1)
    
    return formattedObject

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

    eyeData = read_db( input )

    outputPath = os.path.join(output, 'eye.json')
    if( not os.path.exists(output) ):
        os.makedirs(output)

    with open(outputPath, 'w') as f:
        f.write(json.dumps(eyeData))


if __name__ == "__main__":

    ## Example: 
    ## python eye-parser.py -i /faststorage/OCARINA_ExtractedData/0293/0293_11.sqlite -o ../data/output/0293_11

    parser = argparse.ArgumentParser(description='This scripts aims to parse the Ocarina data stored into SQLite files to NYU backend format')
    parser.add_argument('-i', '--input', nargs=1, required=True, default='')
    parser.add_argument('-o', '--output', nargs=1, required=True, default='')

    args = parser.parse_args()
    main(args.input[0],args.output[0])