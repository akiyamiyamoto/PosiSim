#!/bin/bash
#
# Create plot data from bnn files
#

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

${FLUPRO}/flutil/gplevbin < temp.$$.txt | tee ${logfile}

detname=`grep " NB " ${logfile} | grep " ${detno}  " | sed -e "s/  */ /g" | cut -d" " -f4`
echo "detname=${detname}"
mv gplevh.dat ${outpref}-${detname}.dat
rm -f gplevh.lim gplevh.npo gplevh.poi temp.$$.txt

}


# fluka_prefix="oneyear"

do_doseplot(){

    for detno in `seq 1 11` ; do
      do_gplevbin ${fluka_prefix}001-f71.bnn ${detno} 800 1000 f71
      do_gplevbin ${fluka_prefix}001-f73.bnn ${detno} 400 500  f73
      do_gplevbin ${fluka_prefix}001-f75.bnn ${detno} 400 500  f75
      do_gplevbin ${fluka_prefix}001-f71.bnn ${detno} 800 1    f71-proj
    done
    
    detno=1
    do_gplevbin ${fluka_prefix}001-f81.bnn ${detno} 800 1000 f81
    do_gplevbin ${fluka_prefix}001-f82.bnn ${detno} 400 500 f82
    do_gplevbin ${fluka_prefix}001-f83.bnn ${detno} 400 500 f83
    do_gplevbin ${fluka_prefix}001-f81.bnn ${detno} 800 1 f81-proj
}

do_activityplot(){
    for detno in `seq 1 11` ; do
      do_gplevbin ${fluka_prefix}001-f72.bnn ${detno} 800 1000 f72
      do_gplevbin ${fluka_prefix}001-f74.bnn ${detno} 400 500  f74
      do_gplevbin ${fluka_prefix}001-f76.bnn ${detno} 400 500  f76
    done
    detno=1
    do_gplevbin ${fluka_prefix}001-f84.bnn ${detno} 400 500 f84
    do_gplevbin ${fluka_prefix}001-f85.bnn ${detno} 400 500 f85
    do_gplevbin ${fluka_prefix}001-f90.bnn ${detno} 400 500 f90
    do_gplevbin ${fluka_prefix}001-f91.bnn ${detno} 400 500 f91
    do_gplevbin ${fluka_prefix}001-f92.bnn ${detno} 400 500 f92

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

