#!/bin/bash




###############################################################################
## DEFINITION                                                                ##
###############################################################################
BASE="package-main"

LIB_SRC="lib"
LIB_DST="${BASE}/usr/lib/python2.7/dist-packages/mct/lib/"

MCT_SRC="MCT_Main"
MCT_DST="${BASE}/usr/lib/python2.7/dist-packages/mct/"







###############################################################################
## MAIN                                                                      ##
###############################################################################
## Copy all libraries, drives and other mct files to directory structure that 
## represent the new package.
cp --preserve=all "${LIB_SRC}"/* "${LIB_DST}"
cp --preserve=all "${MCT_SRC}"/* "${MCT_DST}"


## Create the package:
fakeroot dpkg -b ${BASE} .

## EOF.
