#!/bin/bash




###############################################################################
## DEFINITION                                                                ##
###############################################################################
BASE="package-agent"

LIB_SRC="lib"
LIB_DST="${BASE}/usr/lib/python2.7/dist-packages/mct/lib/"

MCT_SRC="MCT_Agent/mct"
MCT_DST="${BASE}/usr/lib/python2.7/dist-packages/mct/"

DRV_SRC="MCT_Agent/openstack_driver"
DRV_DST="${BASE}/usr/lib/python2.7/dist-packages/nova/virt/mct/"







###############################################################################
## MAIN                                                                      ##
###############################################################################
## Copy all libraries, drives and other mct files to directory structure that 
## represent the new package.
cp --preserve=all "${LIB_SRC}"/* "${LIB_DST}"
cp --preserve=all "${MCT_SRC}"/* "${MCT_DST}"
cp --preserve=all "${DRV_SRC}"/* "${DRV_DST}"


## Create the package:
fakeroot dpkg -b ${BASE} .

## EOF.
