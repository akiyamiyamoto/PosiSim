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
set ylabel "Activity per unit mass (Bq/g)"
# set title "Dose vs radius (cm): Conventional Target "

load "label100.inc"
xmin=0.0
xmax=1000.0
set yrange[1E-4:1E4]
set xrange[xmin:xmax]

set arrow from xmin,0.1 to xmax,0.1 nohead 

set title "Activity per unit mass vs R: |Z|<50cm beam 20 y, cooling 100h" 
  plot "plot_v2/actomass-4dprojZ50-total.dat" using (($1+$2)/2.0):3 w steps lw 1 lc 1 title "Total", \
       "" using (($1+$2)/2.0):3:($3*$4/100) w errorbars lw 1 pt 0 lc 1 notitle
replot "plot_v2/actomass-4dprojZ50-h3.dat" using (($1+$2)/2.0):3 w steps lw 1 lc 2 title "H3", \
       ""  using (($1+$2)/2.0):3:($3*$4/100) w errorbars lw 1 pt 0 lc 2 notitle
replot "plot_v2/actomass-4dprojZ50-na22.dat" using (($1+$2)/2.0):3 w steps lw 1 lc 3 title "Na22", \
       "" using (($1+$2)/2.0):3:($3*$4/100) w errorbars lw 1 pt 0 lc 3 notitle
replot "plot_v2/actomass-4dprojZ50-mn54.dat" using (($1+$2)/2.0):3 w steps lw 1 lc 4 title "Mn54", \
       "" using (($1+$2)/2.0):3:($3*$4/100) w errorbars lw 1 pt 0 lc 4 notitle 
replot "plot_v2/actomass-4dprojZ50-co60.dat" using (($1+$2)/2.0):3 w steps lw 1 lc 5 title "Co60", \
       "" using (($1+$2)/2.0):3:($3*$4/100) w errorbars lw 1 pt 0 lc 5 notitle

replot "plot_v2/actomass-4dprojZ50-eu152.dat" using (($1+$2)/2.0):3 w steps lw 1 lc 6 title "Eu152", \
       "" using (($1+$2)/2.0):3:($3*$4/100) w errorbars lw 1 pt 0 lc 6 notitle
replot "plot_v2/actomass-4dprojZ50-eu154.dat" using (($1+$2)/2.0):3 w steps lw 1 lc 7 title "Eu154", \
       "" using (($1+$2)/2.0):3:($3*$4/100) w errorbars lw 1 pt 0 lc 7 notitle

set output "plot_v2/figs/actomass4d_vs_r-Z50.png"
set terminal png size 1000,1000
replot
print "figs/actomass4d_vs_r-Z50.png was created."

