#!/bin/bash 
#
#


mydefault()
{
  infile=$1
  sed -e "s/%%CBMAX%%/1E6/g" -e "s/%%CBMIN%%/1E-6/g" \
      -e "s/%%CBTICS%%/10/g" \
      -e "s/%%XLABEL%%/Z (cm)/g" -e "s/%%YLABEL%%/Radius (cm)/g" \
      -e "s/%%DET%%/1/g" ${infile}
}

mydefault_doseeq()
{
  infile=$1
  det=$2
  sed -e "s/%%CBMAX%%/1E3/g" -e "s/%%CBMIN%%/1E-9/g" \
      -e "s/%%CBTICS%%/10/g" \
      -e "s/%%XLABEL%%/Z (cm)/g" -e "s/%%YLABEL%%/Radius (cm)/g" \
      -e "s/%%DET%%/${det}/g" ${infile}
}

project_doseeq()
{
  infile=$1
  det=$2
  sed -e "s/%%YMAX%%/1E6/g" -e "s/%%YMIN%%/1E-12/g" \
      -e "s/%%XLABEL%%/Radius (cm)/g" -e "s/%%YLABEL%%/DoseEQ (Sv\/h) (cm)/g" \
      -e "s/%%DET%%/${det}/g" ${infile}

}

mydefault_activity()
{
  infile=$1
  det=$2
  sed -e "s/%%CBMAX%%/1E-3/g" -e "s/%%CBMIN%%/1E9/g" \
      -e "s/%%CBTICS%%/10/g" \
      -e "s/%%XLABEL%%/Z (cm)/g" -e "s/%%YLABEL%%/Radius (cm)/g" \
      -e "s/%%DET%%/${det}/g" ${infile}
}

outdir="plot_example"
header="${FLUKA_SCRIPTS}/myflair.head.in"
plots="${FLUKA_SCRIPTS}/myflair.plot.in"
projection="${FLUKA_SCRIPTS}/myflair.1dproj.in"
geometry="${FLUKA_SCRIPTS}/myflair.geometry.in"

source setting.ini

outfile="${outdir}/${fluka_prefix}001.flair"

if [ ! -e ${outdir} ] ; then 
    mkdir -p ${outdir}
    ( cd ${outdir} 
      ln -s ../results/*.inc . 
      ln -s ../results/*.inp . 
      ln -s ../results/*.bnn .
      [ -e ../geobuild ] && ln -s ../geobuild .
    )   
fi

sed -e "s|%%INPUT%%|${fluka_prefix}001.inp|" ${header} > ${outfile}

cat ${geometry} >> ${outfile}

mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f81.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_doseeq_all/g" \
          -e "s/%%TITLE%%/Primary beam does-eq, All (2625Bx, 5Hz)/g" \
          -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
          -e "s/%%PNGFILE%%/primary-doseeq-all.png/g" \
          -e "s/%%CBLABEL%%/Dose rate (Sv\/hour)/g" \
          >> ${outfile}

mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f82.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_eqdose_mid/g" \
          -e "s/%%TITLE%%/Primary beam does-eq, middle (2625Bx, 5Hz)/g" \
          -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
          -e "s/%%CBLABEL%%/Dose rate (Sv\/hour)/g" \
          -e "s/%%PNGFILE%%/primary-doseeq-middle.png/g" \
          >> ${outfile}

mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f83.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_eqdose_tar/g" \
          -e "s/%%TITLE%%/Primary beam does-eq, target (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/Dose rate (Sv\/hour)/g" \
          -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
          -e "s/%%PNGFILE%%/primary-doseeq-target.png/g" \
          >> ${outfile}

mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f84.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_edep_tar/g" \
          -e "s/%%TITLE%%/Primary energy deposit, target area (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/Energy deposite (MGy\/5000 hours)/g" \
          -e "s/%%NORM%%/1.602176462E-7*1.968E14*1E-6*3600*5000/g" \
          -e "s/%%PNGFILE%%/primary-energy-deposit-target.png/g" \
          >> ${outfile}

mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f85.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_edepEM_tar/g" \
          -e "s/%%TITLE%%/Primary EM energy deposit, target area (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/Energy deposite (MGy\/5000 hours)/g" \
          -e "s/%%NORM%%/1.602176462E-7*1.968E14*1E-6*3600*5000/g" \
          -e "s/%%PNGFILE%%/primary-energy-deposit-EM-target.png/g" \
          >> ${outfile}

mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f91.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_edep_taraxis/g" \
          -e "s/%%TITLE%%/Primary energy deposit, target axis symmetry (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/Energy deposite (MGy\/5000 hours)/g" \
          -e "s/%%NORM%%/1.602176462E-7*1.968E14*1E-6*3600*5000/g" \
          -e "s/%%PNGFILE%%/primary-energy-deposit-target-axis.png/g" \
          >> ${outfile}

mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f92.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_edepem_taraxis/g" \
          -e "s/%%TITLE%%/Primary EM energy deposit , target axis symmetry (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/Energy deposite (MGy\/5000 hours)/g" \
          -e "s/%%NORM%%/1.602176462E-7*1.968E14*1E-6*3600*5000/g" \
          -e "s/%%PNGFILE%%/primary-energy-deposit-EM-target-axis.png/g" \
          >> ${outfile}


# Plot DOSE-equivalent 
declare -a unitdata=(71 73 75)
declare -a unitname=("all" "mid" "tar")
declare -a runtime=("1s" "1M" "1h" "1d" "1w" "1m" "3m" "1y" "4y" "Xy" "Zy")
declare -a decayname=("1 sec" "1 minutes" "1 hour" "1 day" "1 week" "1 month" "3 month" "1 year" "4 year" "10 year" "50 year" )

for iu in `seq 0 2` ; do
  aunit=${unitdata[${iu}]}
  aname=${unitname[${iu}]}
  
  for det in `seq 0 10` ; do 
    rt=${runtime[${det}]}
    dname=${decayname[${det}]}
    mydefault_doseeq ${plots} ${det}| sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f${aunit}.bnn/g" \
          -e "s/%%PLOTNAME%%/doseeq-after-${rt}-${aname}/g" \
          -e "s/%%TITLE%%/DOSE-EQ beam ${beamyear} year, ${dname} cooling (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/DOSE-EQ (Sv\/hour)/g" \
          -e "s/%%NORM%%/1E-12*3600/g" \
          -e "s/%%PNGFILE%%/doseeq-after-${rt}cooling-${aname}.png/g" \
          >> ${outfile}
  done
done


# Plot Activity 
declare -a activedata=(72 74 76 93)
# declare -a unitname=("all" "mid" "tar" "off22)
# declare -a runtime=("1s" "1M" "1h" "1d" "1w" "1m" "3m" "1y" "4y" "Xy" "Zy")

for iu in `seq 0 2` ; do
  aunit=${activedata[${iu}]}
  aname=${unitname[${iu}]}
  for det in `seq 0 10` ; do
    rt=${runtime[${det}]}
    dname=${decayname[${det}]}
    mydefault_activity ${plots} ${det}| sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f${aunit}.bnn/g" \
          -e "s/%%PLOTNAME%%/activity-after-${rt}-${aname}/g" \
          -e "s/%%TITLE%%/Activity beam ${beamyear} year, ${dname} cooling (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/Activity (MBq\/cm^3)/g" \
          -e "s/%%NORM%%/1E-6/g" \
          -e "s/%%PNGFILE%%/activity-after-${rt}cooling-${aname}.png/g" \
          >> ${outfile}
  done
done



  aunit=71
  aname="projall"

  for det in `seq 0 10` ; do
    rt=${runtime[${det}]}
    dname=${decayname[${det}]}
    project_doseeq ${projection} ${det}| sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f${aunit}.bnn/g" \
          -e "s/%%PLOTNAME%%/projdoseeq-${rt}-${aname}/g" \
          -e "s/%%TITLE%%/DOSE-EQ beam ${beamyear} year, ${dname} cooling (2625Bx, 5Hz)/g" \
          -e "s/%%NORM%%/1E-12*3600/g" \
          -e "s/%%PNGFILE%%/projdoseeq-after-${rt}cooling-${aname}.png/g" \
          >> ${outfile}
  done

  det=1
  project_doseeq ${projection} ${det} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f81.bnn/g" \
          -e "s/%%PLOTNAME%%/projdoseeq-primary-${aname}/g" \
          -e "s/%%TITLE%%/DOSE-EQ primary projection (2625Bx, 5Hz)/g" \
          -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
          -e "s/%%PNGFILE%%/projdoseeq-primary-${aname}.png/g" \
          >> ${outfile}

# ###############################################
  echo "flair file to plot fluka results was created in ${outfile}"
  echo "cd to ${outdir}, then run flair to create png files of results"

