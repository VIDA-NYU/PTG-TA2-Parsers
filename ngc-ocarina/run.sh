#!/bin/bash
inputDB='/faststorage/OCARINA_ExtractedData/0293/0293_11.sqlite'
outputPath='/home/joaorulff/Workspace/PTG/PTG-TA2-Parsers/data/output'

echo "Generating eye data"
python eye-parser.py -i $inputDB -o $outputPath

echo "Generating perception data"
python perception-parser.py -i $inputDB -o $outputPath

echo "Generating reasoning data"
python reasoning-parser.py -i $inputDB -o $outputPath

