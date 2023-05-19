import argparse
import json
import os

# required to install "pip install moviepy"

from moviepy.editor import VideoFileClip
    
def getMetadata(video_path, objects_file_path):
    clip = VideoFileClip(video_path)
    # Opening JSON file that contains objects (it must be sorted by timestamps)
    file_objects = open(objects_file_path)
    # returns JSON object as a dictionary
    data = json.load(file_objects)

    metadata ={
            "duration_secs": int(clip.duration),
            "first-entry": data[0]["timestamp"],
            "last-entry": data[len(data)-1]["timestamp"],
        }
    return metadata

def main( input: str, output: str ):
    # input: video
    perceptionFilePath = os.path.join(output, 'detic:image.json')
    json_metadata = getMetadata(input, perceptionFilePath)

    outputPath = os.path.join(output, 'additional_metadata.json')

    if( not os.path.exists(output) ):
        os.makedirs(output)

    with open(outputPath, 'w') as f:
        f.write(json.dumps(json_metadata))


if __name__ == "__main__":

    ## Example: 
    ## python generate-metadata.py -i /foo/ngc_0293_13.mp4 -o /bar/0293_11

    parser = argparse.ArgumentParser(description='This scripts aims to generate the following metadata: duration_sec, first-entry, and last-entry, based on video and detic:image.json files')
    parser.add_argument('-i', '--input', nargs=1, required=True, default='')
    parser.add_argument('-o', '--output', nargs=1, required=True, default='')

    args = parser.parse_args()
    main(args.input[0],args.output[0])