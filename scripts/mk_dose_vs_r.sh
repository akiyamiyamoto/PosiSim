#!/bin/bash 
#
# Create a gnuplot file for 1D projection of DOSE-EQ
#

source setting.ini

infile="${FLUKA_SCRIPTS}/gnuplot.dose_vs_r.ini"
outfile="dose_vs_r.plt"
outprefix=`basename ${outfile} .plt`
outdir="plot/figs"

cat ${infile} > ${outfile}

echo "set title \"Eq Dose vs R: Conventional Target, beam ${title_beamon} 2625Bx, 5Hz\" " >> ${outfile}

echo "plot \"plot/f81-proj-priAll.dat\" using 1:(3600*1.984E14*1E-12*\$3) title \"primary\" " >> ${outfile}

declare -A CPERIOD
CPERIOD=( ["1d"]="1 day"   ["1h"]="1 hour"  ["1m"]="1 month"
    ["4d"]="100 hour", ["5y"]="5 years", 
    ["1M"]="1 minute" ["1s"]="1 second" ["1w"]="1 week" ["1y"]="1 year"
    ["3m"]="3 months" ["4y"]="4 years" ["Xy"]="10 years" ["Zy"]="50 years" )

declare -a ORDER=("1s" "1M" "1h" "1d" "4d" "1w" "1m" "3m" "1y" "4y" "5y" "Xy" "Zy")

for fn in `seq 0 12` ; do
   ftype=${ORDER[$fn]}
   f="plot/f71-proj-Sv${ftype}All.dat"  
   if [ -e ${f} ] ; then 
     pname=${CPERIOD[${ftype}]}
     echo "replot \"$f\" using 1:(3600*1E-12*\$3) title \"${pname} cooling\"" >> ${outfile}
   fi
done

if [ ! -e ${outdir} ] ; then 
  mkdir -p ${outdir}
fi
   
cat >> ${outfile} <<EOF
set output "${outdir}/${outprefix}.png"
set terminal png size 1000,1000
replot
print "${outdir}/${outprefix}.png was created."
EOF

echo "${outfile}.plt was created. Do \"gnuplot44 ${outfile}\" to create figure."
