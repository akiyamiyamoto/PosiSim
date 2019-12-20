#!/bin/bash 

indir=$1

if [ ! -e ${indir} ] ; then 
  echo "Input figure directory, ${indir}, does not exist"
  exit -1
fi

outdir="${indir}-trim"

if [ ! -e ${outdir} ] ; then 
  mkdir -p ${outdir}
fi

for f in ${indir}/*.png ; do 
   fname=`basename ${f}`
   if [ ! -e ${outdir}/${fname} ] ;then 
       convert -trim ${f} ${outdir}/${fname}
       echo "converted ${f} to ${outdir}/${fname}"
   elif [ ${f} -nt ${outdir}/${fname} ] ; then 
       convert -trim ${f} ${outdir}/${fname}
       echo "converted ${f} to ${outdir}/${fname}"
   fi
     
done


