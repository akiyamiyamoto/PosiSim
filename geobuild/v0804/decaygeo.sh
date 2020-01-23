#!/bin/bash 


case_forward(){
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
    
}

case_upward(){
    reptype="upward"
    sed -e "/${reptype}2/s/VACUUM/      /g" \
        assignmat${verstr}.inc | cut -c1-80 > assignmat-decay1.inc

    cut -c1-80 assignmat${verstr}.inc > assignmat-decay2.inc
    
    cut -c1-60 assignmat${verstr}.inc > assignmat-nodecay.inc
    
}

verstr=`grep "_VERSION=" version.py | cut -d"=" -f2 | sed -e 's/\"//g'`


cp assignmat${verstr}.inc assignmat-decaygeo0.inc
reptype="upward"
maxdecay=2
for i in `seq 1 ${maxdecay}` ; do 
  k=$[${i}-1]
  sed -e "/${reptype}${i}/s/Copper/VACUUM/"     -e "/${reptype}${i}/s/STAINLES/  VACUUM/" \
      -e "/${reptype}${i}/s/TARMAT/VACUUM/"     -e "/${reptype}${i}/s/ WATER/VACUUM/" \
      -e "/${reptype}${i}/s/LIGHTSUS/  VACUUM/" -e "/${reptype}${i}/s/LIQSEAL/ VACUUM/" \
      -e "/${reptype}${i}/s/CONCRETE/  VACUUM/" -e "/${reptype}${i}/s/CASTIRON/  VACUUM/" \
         assignmat-decaygeo${k}.inc > assignmat-decaygeo${i}.inc
done

case_upward



