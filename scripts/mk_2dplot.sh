#!/bin/bash 
#
# Create a gnuplot file for Dose-EQ map
#

source ${FLUKA_SCRIPTS}/constants.def

source setting.ini

#runyear="1"
inifile="${FLUKA_SCRIPTS}/gnuplot.flair.ini"
datadir="plot"
outdir="figs"
if [ ! -e ${outdir} ] ; then
    mkdir -v ${outdir}
fi
outfile="2dplot.plt"

source ${FLUKA_SCRIPTS}/func_2dplot.sh

rm -fv ${outfile}

echo "plot_command is ${plot_command}"
for cmd in ${plot_command}; do
  ${cmd}
done
# Do_Dose
# Do_Activity
# Do_Edep

#echo "Completed all"
#echo "Do \"gnuplot44 ${outfile} -\" to create figures."
