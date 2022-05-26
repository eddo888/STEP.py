#!/usr/bin/env bash

file='../test/Buy Side Sell Side.xmi'

pushd ../bin

horizontal.pl

./uml2step.py toSTEP  "${file}"

horizontal.pl

parser.py -rc "${file}.step.xml"
open "${file}.step.xml"

horizontal.pl

popd
