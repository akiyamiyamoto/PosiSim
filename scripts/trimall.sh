#!/bin/bash 

indir=figs
outdir=figs-trim

if [ ! -e ${outdir} ] ; then 
  mkdir -p ${outdir}
fi

for f in ${indir}/*.png ; do 
   fname=`basename ${f}`
   convert -trim ${f} ${outdir}/${fname}
   echo "converted ${f} to ${outdir}/${fname}"
done


