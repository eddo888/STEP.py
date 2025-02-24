#!/usr/bin/env bash

file='Buy Side Sell Side.xmi'

rsync -ai ~/git/gitlab.stibo.dk/step/misc/javascript-snippets/Stibo/StepModeler/"${file}" .

if [  -e "${file}.step.xml" ]
then
	rm "${file}.step.xml"
fi

pushd ../bin

horizontal.pl

./uml2step.py toSTEP  "../test/${file}"

horizontal.pl

popd

horizontal.pl

parser.py -rc "${file}.step.xml"
open "${file}.step.xml"

horizontal.pl

