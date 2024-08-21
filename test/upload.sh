#!/usr/bin/env bash

rm -f .cache.json
rm -f schema.step.xml

../STEP/Converter.py -p XSD -r EDDO xsd2step -s schema.xsd  -o schema.step.xml

open schema.step.xml

id=$(./import.sh  -i 406608 schema.step.xml | pyson.py -tp '$.id')

echo $id

sleep 5

./report.sh -i $id | pyson.py -c


