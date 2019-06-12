#!/bin/bash 


add_usrbin()
{ 
   tdir=$1
   outname=$2
   # dpref=`echo ${outname} | cut -d"-" -f1`
   #for fu in `seq 71 76` `seq 81 85` `seq 90 93` ; do 
   echo "fort data with unit ${usrbin_unit} are added"
   for fu in ${usrbin_unit} ; do
       outname="$2-f${fu}"
       find ${tdir}/job* -name "*_fort.${fu}" -print > ${outname}.usbsuw
       echo "" >> ${outname}.usbsuw
       echo "${outname}" >> ${outname}.usbsuw

       usbsuw < ${outname}.usbsuw 2>&1 | tee  ${outname}.log  

       usbrea  <<EOF
${outname}.bnn
${outname}.subrea  
EOF
    done

}

source setting.ini

mkdir -p results

(
   cd results
   cp ../jobs/job001/*.inp . 
   cp ../jobs/job001/*.log . 
   cp ../jobs/job001/*.out . 
   cp ../jobs/job001/*.err .
   cp ../jobs/job001/*.inc .

   add_usrbin ../jobs  ${fluka_prefix}001
)
