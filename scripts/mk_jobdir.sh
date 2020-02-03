#!/bin/bash 



# ########################### main part to create job-directory


curdir=`pwd`
jobs="jobs"
njob_begin=1
njob_end=200
job_queue="l"
nrun_begin=0
nrun_end=2
opts=""
sourcedir="${FLUKA}/init_fluka92.sh"
fluka_inp=""
jobname_key=""

if [ -e ${jobs} ] ; then 
   echo "Error: ${jobs} directory exist. Remove it before re-create."
   exit -1
fi

source setting.ini

[ "x${fluka_inp}" == "x" ] && fluka_inp="${fluka_prefix}.inp"
[ "x${jobname_key}" == "x" ] && jobname_key="${version:4:2}J${fluka_inp:0:2}"

fkey=`basename ${fluka_inp} .inp`

mkdir -p ${jobs}
(
  cd ${jobs}
  for jseq in `seq ${njob_begin} ${njob_end}`; do
    ( 
       jseqstr=`printf "%3.3d" ${jseq}`
       jobdir="job${jseqstr}"
       mkdir -p ${jobdir}
       cd ${jobdir}
       ( 
          logfile="${fkey}.log"
          thisinp="${fkey}${jseqstr}.inp"
          ln -s ${curdir}/${fluka_inp} ${thisinp}
          if [ -e ${curdir}/geobuild ] ; then 
             ln -s ${curdir}/geobuild . 
          fi
          ranv=`printf "%d%3.3d" ${RANDOM} ${jseq}`
          printf "%-10s%9d.%9d." "RANDOMIZ" 1 ${ranv} > random.inc
          cmd="rflukadpm3 ${opts} -N${nrun_begin} -M${nrun_end} ${thisinp}"
          echo "Fluka command is ${cmd}" >> ${logfile}
          echo "" >> ${logfile}
          jobid="${jobname_key}${jseqstr}"
          echo "bsub -o sub.log -q ${job_queue} -J ${jobid} \"( source ${sourcedir} && ${cmd} > sub.log 2>&1 )\" " > bsub.sh
          echo "bsub.sh was created in ${jobdir}"
       )
    )
  done
) 

cat <<EOF
Job scripts were created. To submit jobs, do as follows.

for n in \`seq -w ${njob_begin} ${njob_end}\` ; do ( cd jobs/job\${n} && . bsub.sh ) ; done
EOF
