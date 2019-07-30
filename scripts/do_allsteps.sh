
add_usrbin.sh 2>&1 | tee add_usrbin.log

# Create data files for gnuploti

if [ ! -e ../geodata ] ; then 
   mk_flair_data.sh 
   echo "../geodata does not exist." 
   echo "Create proper on by plotting geometry data using flair in plot_example."
   exit
fi

# vi setting.ini

mkdata_usrbin.sh

mk_2dplot.sh
gnuplot44 2dplot.plt

# Dose vs r plot

mk_dose_vs_r.sh
gnuplot44 dose_vs_r.plt

# neutron and photon flux into liq. seal ( for v0607 )
add_usrbdx.sh 

sumflux.py
mk_flux_perE.sh 
mk_flux_npart.sh 
mk_flux_nint.sh

# Create trimmed figures in figs-trim
trimall.sh  figs

# ###################################################
# Analysis of residual neucleus

# Sum up fluka results of many runs by usrsuw
add_resnucle.py

# Do isotope plot
mkisotope.py

mk_activity_table.py

# trim isotopes figure 
trimall.sh figsisotopes

