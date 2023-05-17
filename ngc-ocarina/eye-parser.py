import argparse
import json
import numpy as np

debug = True


def read_json( inputPath: str ):

    jsonFile = None
    with open( inputPath) as f:
        jsonFile = json.load(f)

    return jsonFile

def main( input: str ):

    timEyeData = []

    eyeData = read_json( input )
    for index, row in enumerate(eyeData):

        gazeOrigin = { 'x': row['origin_x'], 'y': row['origin_y'], 'z': row['origin_z'] }
        gazeDirection = { 'x': row['direction_x'], 'y': row['direction_y'], 'z': row['direction_z'] }
        timestamp = f'{row["timestamp"]}-0 ' 

        currentTIMRow = {
            "GazeOrigin": gazeOrigin,
            "GazeDirection": gazeDirection,
            "timestamp": timestamp
        }

        timEyeData.append(currentTIMRow)


    with open('./eyetim.json', 'w') as f:
        f.write(json.dumps(timEyeData))


if __name__ == "__main__":

    ## Example: 
    ## python voxelization2.py --pointcloudpath ./data/pointcloud/2023.03.15-20.36.42-pointcloud.json --outputpath ./outputs/voxelizations/2023.03.15-20.36.42-voxelized-pointcloud.json

    parser = argparse.ArgumentParser(description='Arguments for point cloud voxelization.')
    parser.add_argument('-i', '--input', nargs=1, required=True, default='')

    args = parser.parse_args()
    main(args.input[0])
