#!/bin/bash
#
# Create plot data from bnn files
#

# #####################################################
do_gplevbin()
{
  infile=$1
  detno=$2
  nrbin=$3
  nzbin=$4
  outpref=$5

  nphibin=1

  if [ ! -e ${infile} ] ; then 
     echo "${infile} does not exist."
     return
  fi

  inpref=`basename ${infile}`
  logfile=${inpref}.gplevbin.log

cat > temp.$$.txt <<EOF
-

${infile}


${detno}

${nrbin}

${nphibin}

${nzbin}

EOF
which gplevbin

gplevbin < temp.$$.txt | tee ${logfile}

detname=`grep " NB " ${logfile} | grep " ${detno}  " | sed -e "s/  */ /g" | cut -d" " -f4`
echo "detname=${detname}"
mv gplevh.dat ${outpref}-${detname}.dat
rm -f gplevh.lim gplevh.npo gplevh.poi temp.$$.txt

}


# fluka_prefix="oneyear"

do_doseplot(){

    for detid in `seq 0 ${#RUN_TIME[@]}` ; do
      detno=$[${detid}+1]
      do_gplevbin ${fluka_prefix}001_71.bnn ${detno} 800 1000 f71
      do_gplevbin ${fluka_prefix}001_73.bnn ${detno} 400 500  f73
      do_gplevbin ${fluka_prefix}001_75.bnn ${detno} 400 500  f75
      do_gplevbin ${fluka_prefix}001_71.bnn ${detno} 800 1    f71-proj
    done
    
    detno=1
    do_gplevbin ${fluka_prefix}001_81.bnn ${detno} 800 1000 f81
    do_gplevbin ${fluka_prefix}001_82.bnn ${detno} 400 500 f82
    do_gplevbin ${fluka_prefix}001_83.bnn ${detno} 400 500 f83
    do_gplevbin ${fluka_prefix}001_81.bnn ${detno} 800 1 f81-proj
}

do_activityplot(){
    for detno in `seq 1 ${#RUN_TIME[@]}` ; do
      do_gplevbin ${fluka_prefix}001_72.bnn ${detno} 800 1000 f72
      do_gplevbin ${fluka_prefix}001_74.bnn ${detno} 400 500  f74
      do_gplevbin ${fluka_prefix}001_76.bnn ${detno} 400 500  f76
    done
    detno=1
    do_gplevbin ${fluka_prefix}001_84.bnn ${detno} 400 500 f84
    do_gplevbin ${fluka_prefix}001_90.bnn ${detno} 400 500 f90
    if [ ${VERSION_NUMBER} -lt 607 ] ; then 
      do_gplevbin ${fluka_prefix}001_85.bnn ${detno} 400 500 f85
      do_gplevbin ${fluka_prefix}001_91.bnn ${detno} 400 500 f91
      do_gplevbin ${fluka_prefix}001_92.bnn ${detno} 400 500 f92
    else
      for detno in `seq 1 ${#RUN_TIME[@]}` ; do
        do_gplevbin ${fluka_prefix}001_94.bnn ${detno} 400 500 f94
      done
      for detno in `seq 2 4` ; do
        do_gplevbin ${fluka_prefix}001_90.bnn ${detno} 400 500 f90
      done
    fi
}

if [ ! -e setting.ini ] ; then 
  echo "settings.ini does not exist in current directory"
  exit
fi
source setting.ini


if [ ! -e results ] ; then 
  echo "result directory does not exist. Create results and data there by add_usrbin.sh "
  exit
fi

if [ -e plot ] ; then 
  echo "plot directory exists already. Remove it and rerun."
  exit
fi

mkdir plot

(
  cd plot
  ln -s ../results/*.bnn . 
  ln -s ../results/*.inc . 
  ln -s ../results/*.inp . 

  for cmd in ${mkdata_cmd} ; do
    ${cmd}
  done
)

# do_activityplot

