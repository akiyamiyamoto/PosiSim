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
set ytics format "10^{%T}"
set ytics 10

set logscale y 10
set grid
set yrange[1E-12:1E4]
set xrange[0:1050.0]


set xlabel "r (cm)"
set ylabel "Dose (Sv/hour)"
# set title "Dose vs radius (cm): Conventional Target "

load "label100.inc"
xmin=0.0
xmax=1000.0

set arrow from xmin,100.0E-3 to xmax,100.0E-3 nohead 
set arrow from xmin,20.0E-6 to xmax,20.0E-6 nohead 
set arrow from xmin,1.5E-6 to xmax,1.5E-6 nohead 
set arrow from xmin,0.2E-6 to xmax,0.2E-6 nohead 


set title "Eq Dose vs R(|Z|<50cm): Bend0, beam 1 year 2625Bx, 5Hz" 
plot   "plot_v2/projZ0-doseeq-primary-projall.dat" using 1:(3600*1.984E14*1E-12*$3) title "primary" 
replot "plot_v2/projZ0-doseeq-1h-projall01.dat" using 1:(3600*1E-12*$3) title "1 hour cooling"
replot "plot_v2/projZ0-doseeq-1d-projall01.dat" using 1:(3600*1E-12*$3) title "1 day cooling"
replot "plot_v2/projZ0-doseeq-4d-projall.dat" using 1:(3600*1E-12*$3) title "100 hour cooling"
replot "plot_v2/projZ0-doseeq-1m-projall01.dat" using 1:(3600*1E-12*$3) title "1 month cooling"
replot "plot_v2/projZ0-doseeq-1y-projall01.dat" using 1:(3600*1E-12*$3) title "1 year cooling"
replot "plot_v2/projZ0-doseeq-Xy-projall01.dat" using 1:(3600*1E-12*$3) title "10 years cooling"

set output "plot_v2/figs/dose_vs_r_z50.png"
set terminal png size 1000,1000
replot
print "figs/dose_vs_r_z50.png was created."


