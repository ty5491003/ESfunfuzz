#!/bin/bash

folder="."
softfiles=$(ls $folder)

for sfile in ${softfiles}
do
    uglifyjs ${sfile} -b -o ${sfile}
done
