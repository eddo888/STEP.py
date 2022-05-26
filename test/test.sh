#!/usr/bin/env bash

rscp='rsync -i --perms --times --partial'

file='Buy Side Sell Side.xmi'

$rscp ~/git/gitlab.stibo.dk/step/misc/javascript-snippets/Stibo/StepModeler/"${file}" .

pushd ../bin

horizontal.pl

./uml2step.py toSTEP  "../test/${file}"

horizontal.pl

popd

horizontal.pl

parser.py -rc "${file}.step.xml"
open "${file}.step.xml"

horizontal.pl

