#!/bin/bash 

verstr=`grep "_VERSION=" version.py | cut -d"=" -f2 | sed -e 's/\"//g'`


cp assignmat${verstr}.inc assignmat-decaygeo0.inc
for i in `seq 1 5` ; do 
  k=$[${i}-1]
  sed -e "/beamoff${i}/s/Copper/VACUUM/"     -e "/beamoff${i}/s/STAINLES/  VACUUM/" \
      -e "/beamoff${i}/s/TARMAT/VACUUM/"     -e "/beamoff${i}/s/ WATER/VACUUM/" \
      -e "/beamoff${i}/s/LIGHTSUS/  VACUUM/" -e "/beamoff${i}/s/LIQSEAL/ VACUUM/" \
      -e "/beamoff${i}/s/CONCRETE/  VACUUM/" -e "/beamoff${i}/s/CASTIRON/  VACUUM/" \
         assignmat-decaygeo${k}.inc > assignmat-decaygeo${i}.inc
done

sed -e "/beamoff2/s/VACUUM/      /g" -e "/beamoff3/s/VACUUM/      /g" \
    -e "/beamoff4/s/VACUUM/      /g" -e "/beamoff5/s/VACUUM/      /g" \
    assignmat${verstr}.inc | cut -c1-80 > assignmat-decay1.inc

sed -e "/beamoff3/s/VACUUM/      /g" \
    -e "/beamoff4/s/VACUUM/      /g" -e "/beamoff5/s/VACUUM/      /g" \
    assignmat${verstr}.inc | cut -c1-80 > assignmat-decay2.inc

sed -e "/beamoff4/s/VACUUM/      /g" -e "/beamoff5/s/VACUUM/      /g" \
    assignmat${verstr}.inc | cut -c1-80 > assignmat-decay3.inc

sed -e "/beamoff5/s/VACUUM/      /g" \
    assignmat${verstr}.inc | cut -c1-80 > assignmat-decay4.inc

cut -c1-80 assignmat${verstr}.inc > assignmat-decay5.inc

cut -c1-60 assignmat${verstr}.inc > assignmat-nodecay.inc


