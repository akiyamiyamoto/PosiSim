
add_usrbin.sh 2>&1 | tee add_usrbin.log

# Create data files for gnuploti

# vi setting.ini

mkdata_usrbin.sh

mk_2dplot.sh
gnuplot44 2dplot.plt

# Dose vs r plot

mk_dose_vs_r.sh
gnuplot44 dose_vs_r.plt

# Create trimmed figures in figs-trim
trimall.sh



# ###################################################
# Analysis of residual neucleus

# Sum up fluka results of many runs by usrsuw
add_resnucle.py

# Do isotope plot
mkisotope.py



