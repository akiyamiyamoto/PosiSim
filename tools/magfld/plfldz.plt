set terminal qt size 800,800
set size 0.95,0.95
set origin 0.025,0.025

set title font "Times,24"
set xlabel font "Times,18"
set ylabel font "Times,18"
set tics font "Times,18"
set key font "Times,18"

set grid
# set xrange [-100.0:1000.0]
set xrange [-5.0:20.0]

#plot "fc_dcsol_bzdips2_p1a2a_all.dat"

set title 'Bz in Tesla'
set ylabel 'Bz Tesla'
set xlabel 'Z (cm)'

 plot 'data/bfdata-r00.dat' using 1:4 title '(x,y)=(0,0)'
replot 'data/bfdata-r05.dat' using 1:4 title '(x,y)=(0.5,0)'
replot 'data/bfdata-r10.dat' using 1:4 title '(x,y)=(1.0,0)'
replot 'data/bfdata-r15.dat' using 1:4 title '(x,y)=(1.5,0)'
replot 'data/bfdata-r20.dat' using 1:4 title '(x,y)=(2.0,0)'

set output "figs/bz-vs-z-near.png"
set terminal png size 800,800
replot 
print "figs/bz-vs-z-near.png was created."
