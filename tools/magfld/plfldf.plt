
set grid
set xrange [-100.0:200.0]
set xrange [-5.0:40.0]

#plot "fc_dcsol_bzdips2_p1a2a_all.dat"

set title 'Abs(B) in Tesla'
set ylabel 'Abs(B) Tesla'
set xlabel 'Z (cm)'

set yrange [0.0:6.0]
bmax = 5.0
factor = bmax*0.8*0.8
f(x) = factor / ((0.8+0.27*x) )**2)

plot 'data/bfdata-r00.dat' using 1:5 title '(x,y)=(0,0)'
replot 'data/bfdata-r10.dat' using 1:5 title '(x,y)=(10,0)'
replot 'data/bfdata-r20.dat' using 1:5 title '(x,y)=(20,0)'
replot 'data/bfdata-r30.dat' using 1:5 title '(x,y)=(30,0)'
replot 'data/bfdata-r40.dat' using 1:5 title '(x,y)=(40,0)'
replot f(x)

set output "figs/absb-vs-z.png"
set terminal png size 1000,1000
replot 
