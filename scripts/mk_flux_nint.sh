#!/bin/bash 
#
# Create a gnuplot file to plot flux
#

# Number of primary electron per second
export NBE_PER_SEC=1.968E14
# Normalization, integrated over 2pi
export NORM=`echo print ${NBE_PER_SEC}*2*3.14159265 | python -`


# #########################################################
print_template_header(){

cat <<EOF
#
# Plot Primary dose data
#
set terminal qt size 800,800
set size 0.95,0.95
set origin 0.025,0.025
set title font "Times,18"
set xlabel font "Times,14"
set ylabel font "Times,14"
set tics font "Times,14"
set key font "Times,14"
# set ytics format "10^{%T}"
# set ytics 10

set logscale y 10
set logscale x 10
set grid
set yrange[1E9:2E13]
set key at 100,1E12
# set ylabel "Nb. of Particles /cm^2/primary particle"
set ylabel "Integrated nb. of particles /cm^2/sec"
set label 10 at 0.7,2E10 "2.6nC/Bx, 2625Bx/pulse, 5Hz" font "Times,14"
set label 11 at 0.7,0.8E10 "Spectrum was integrated from 0 to X-max" font "Times,14"


set xlabel "Integration range max, X-max (MeV)"
set title "Integrated nb of particles ( to Liq. Seal)"
# set label 1 at 0.01,0.0007 "A: From rotation axis" font "Times,14"
# set label 2 at 0.01,0.0003 "B: From support structure" font "Times,14"


#
# Data order : xmin, xmax, y, dY in percentage
EOF
}

# ############################################################
print_template_plot(){
  plotcmd=$1
  plotfile=$2  
  plottitle=$3
  cat <<EOF
  $plotcmd   "${plotfile}" using ((\$1+\$2)/2*1000.0):(\$5*${NORM}):(0.0):(\$6*${NORM})  with xyerrorlines title "${plottitle}"
EOF
}

############################################################
print_template_trailer(){
  cat <<EOF

set terminal png size 800,800
set output "figs/flux_nint.png"
replot

set terminal qt size 800,800
EOF
}

############################################################
gpl_neutron_photon_only(){
    source setting.ini
    outfile="flux_nint.plt"
    print_template_header > ${outfile}
    print_template_plot plot flux/neutron.dat "Neutron" >> ${outfile}
    print_template_plot replot flux/photon.dat "Photon" >> ${outfile}
    print_template_trailer >> ${outfile}
    echo "A file ${outfile} was created. Run gnuplot44 to create figure."
    gnuplot44 ${outfile}
    echo "gnuplot44 command completed."

}

############################################################


gpl_neutron_photon_only


