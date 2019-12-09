#!/bin/bash 

verstr=`grep "_VERSION=" version.py | cut -d"=" -f2 | sed -e 's/\"//g'`


sed -e "/beamoff/s/Copper/VACUUM/"     -e "/beamoff/s/STAINLES/  VACUUM/" \
    -e "/beamoff/s/TARMAT/VACUUM/"     -e "/beamoff/s/ WATER/VACUUM/" \
    -e "/beamoff/s/LIGHTSUS/  VACUUM/" -e "/beamoff/s/LIQSEAL/ VACUUM/" assignmat${verstr}.inc > assignmat-decaygeo.inc

sed -e "/beamoff2/s/VACUUM/      /g" assignmat${verstr}.inc | cut -c1-80 > assignmat-decay1.inc

cut -c1-80 assignmat${verstr}.inc > assignmat-decay2.inc

cut -c1-60 assignmat${verstr}.inc > assignmat-nodecay.inc


