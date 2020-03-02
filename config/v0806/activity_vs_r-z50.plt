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


set xlabel "R (cm)"
set ylabel "Activity (Bq/cm^3)"
# set title "Dose vs radius (cm): Conventional Target "

load "label100.inc"
xmin=0.0
xmax=1000.0
set yrange[1E-4:1E4]
set xrange[xmin:xmax]

set arrow from xmin,0.1 to xmax,0.1 nohead 
# set label 1 at graph 0.4,0.9 "|Z|<50cm" font "Times,14" 

set title "Activity vs R: beam 20 years 2625Bx, 5Hz, |Z| < 50cm " 
  plot "plot_v2/activproj-1h-z50.dat" using (($1+$2)/2.0):3:($3*$4/100) w errorbars title "1 hour cooling"
replot "plot_v2/activproj-1d-z50.dat" using (($1+$2)/2.0):3:($3*$4/100) w errorbars title "1 day cooling"
replot "plot_v2/activproj-4d-z50.dat" using (($1+$2)/2.0):3:($3*$4/100) w errorbars title "100 hour cooling"
replot "plot_v2/activproj-1m-z50.dat" using (($1+$2)/2.0):3:($3*$4/100) w errorbars title "1 month cooling"
replot "plot_v2/activproj-1y-z50.dat" using (($1+$2)/2.0):3:($3*$4/100) w errorbars title "1 year cooling"
replot "plot_v2/activproj-xy-z50.dat" using (($1+$2)/2.0):3:($3*$4/100) w errorbars title "10 years cooling"

set output "plot_v2/figs/activity_vs_r-z50.png"
set terminal png size 1000,1000
replot
print "figs/activity_vs_r-z50.png was created."

