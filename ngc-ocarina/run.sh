#!/bin/bash
# inputDB='/faststorage/OCARINA_ExtractedData/0293/0293_13.sqlite'
# outputPath='/home/joaorulff/Workspace/PTG/PTG-TA2-Parsers/data/output'
# videoPath='/home/joaorulff/Workspace/PTG/PTG-TA2-Parsers/data/output/main.mp4'

## ADD path to the 3D model
# model='/foo/bar/model.fbx'

# echo "Generating eye data"
# python eye-parser.py -i $inputDB -o $outputPath

# echo "Generating perception data"
# python perception-parser.py -i $inputDB -o $outputPath

# echo "Generating reasoning data"
# python reasoning-parser.py -i $inputDB -o $outputPath

echo "Generating video"
python image_extractor.py

# echo "Generating medatada"
# python generate-metadata.py -i $videoPath -o $outputPath


