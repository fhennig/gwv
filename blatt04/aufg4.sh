#!/bin/bash

outFile="aufg4.txt"

rm $outFile

for f in blatt4_environment_a.txt  blatt4_environment_b.txt feld/feld_mehrere_goals.txt
do
    echo "-------------------------------" >> $outFile
    echo "field: " $f >> $outFile
    echo "" >> $outFile
    python script.py $f >> $outFile
done
         
