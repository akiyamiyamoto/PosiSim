#!/bin/bash 
#
# Various utility function to make a sample flair data
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

# ##############################################################################
# Primary dose plot main
# ##############################################################################
Primary_Doseeq_unit81to83()
{
  plots=$1
  fluka_prefix=$2
  outfile=$3

  mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f81.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_doseeq_all/g" \
          -e "s/%%TITLE%%/Primary beam does-eq, All (2625Bx, 5Hz)/g" \
          -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
          -e "s|%%PNGFILE%%|figs/primary-doseeq-all.png|g" \
          -e "s/%%CBLABEL%%/Dose rate (Sv\/hour)/g" \
          >> ${outfile}

  mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f82.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_eqdose_mid/g" \
          -e "s/%%TITLE%%/Primary beam does-eq, middle (2625Bx, 5Hz)/g" \
          -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
          -e "s/%%CBLABEL%%/Dose rate (Sv\/hour)/g" \
          -e "s|%%PNGFILE%%|figs/primary-doseeq-middle.png|g" \
          >> ${outfile}

  mydefault ${plots} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f83.bnn/g" \
          -e "s/%%PLOTNAME%%/prim_eqdose_tar/g" \
          -e "s/%%TITLE%%/Primary beam does-eq, target (2625Bx, 5Hz)/g" \
          -e "s/%%CBLABEL%%/Dose rate (Sv\/hour)/g" \
          -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
          -e "s|%%PNGFILE%%|figs/primary-doseeq-target.png|g" \
          >> ${outfile}

}

# ############################################################################
# Decay doseeq
# ############################################################################
Decay_Doseeq_717375()
{
   plots=$1
   fluka_prefix=$2
   outfile=$3


    declare -a runtime=("${RUN_TIME[@]}")
    declare -a decayname=("${DECAY_NAME[@]}")
    declare -a decay_doseeq_unit=("${DECAY_DOSEEQ_UNIT[@]}")
    declare -a decay_doseeq_name=("${DECAY_DOSEEQ_NAME[@]}")
    
    
    echo ${runtime[@]}
    echo ${decayname[@]}
    
    for iuind in `seq 1 ${#decay_doseeq_unit[@]} ` ; do
      iu=$[${iuind}-1]
      aunit=${decay_doseeq_unit[${iu}]}
      aname=${decay_doseeq_name[${iu}]}
      echo "aunit, aname=${aunit} ${aname}"
    
      for detind in `seq 1 ${#runtime[@]} ` ; do
        det=$[${detind}-1]
        rt=${runtime[${det}]}
        dname=${decayname[${det}]}
        # echo "rt, dname= ${rt} ${dname}"
        mydefault_doseeq ${plots} ${detind}| sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f${aunit}.bnn/g" \
              -e "s/%%PLOTNAME%%/doseeq-after-${rt}-${aname}/g" \
              -e "s/%%TITLE%%/DOSE-EQ beam ${beamyear} year, ${dname} cooling (2625Bx, 5Hz)/g" \
              -e "s/%%CBLABEL%%/DOSE-EQ (Sv\/hour)/g" \
              -e "s/%%NORM%%/1E-12*3600/g" \
              -e "s|%%PNGFILE%%|figs/doseeq-after-${rt}cooling-${aname}.png|g" \
              >> ${outfile}
      done
    done
    
    
}

# ############################################################################
# Decay activity
# ############################################################################
Decay_Activity_727476()
{
   plots=$1
   fluka_prefix=$2
   outfile=$3


    declare -a runtime=("${RUN_TIME[@]}")
    declare -a decayname=("${DECAY_NAME[@]}")
    declare -a decay_activity_unit=("${DECAY_ACTIVITY_UNIT[@]}")
    declare -a decay_activity_name=("${DECAY_ACTIVITY_NAME[@]}")
    
    
    echo ${runtime[@]}
    echo ${decayname[@]}
    
    for iuind in `seq 1 ${#decay_activity_unit[@]} ` ; do
      iu=$[${iuind}-1]
      aunit=${decay_activity_unit[${iu}]}
      aname=${decay_activity_name[${iu}]}
      echo "aunit, aname=${aunit} ${aname}"
    
      for detind in `seq 1 ${#runtime[@]} ` ; do
        det=$[${detind}-1]
        rt=${runtime[${det}]}
        dname=${decayname[${det}]}
        # echo "rt, dname= ${rt} ${dname}"

        mydefault_activity ${plots} ${detind}| sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f${aunit}.bnn/g" \
              -e "s/%%PLOTNAME%%/activity-after-${rt}-${aname}/g" \
              -e "s/%%TITLE%%/Activity beam ${beamyear} year, ${dname} cooling (2625Bx, 5Hz)/g" \
              -e "s/%%CBLABEL%%/Activity (MBq\/cm^3)/g" \
              -e "s/%%NORM%%/1E-6/g" \
              -e "s|%%PNGFILE%%|figs/activity-after-${rt}cooling-${aname}.png|g" \
              >> ${outfile}

      done
    done
    
}

# ############################################################################
# Doseeq R Projection 
# ############################################################################
Doseeq_R_Projection()
{
   plots=$1
   fluka_prefix=$2
   outfile=$3

   declare -a runtime=("${RUN_TIME[@]}")
   declare -a decayname=("${DECAY_NAME[@]}")


   aunit=71
   aname="projall"
 
   for detid in `seq 1 ${#runtime[@]} ` ; do
     det=$[${detid}-1]
     rt=${runtime[${det}]}
     dname=${decayname[${det}]}
     project_doseeq ${projection} ${detid}| sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f${aunit}.bnn/g" \
           -e "s/%%PLOTNAME%%/projdoseeq-${rt}-${aname}/g" \
           -e "s/%%TITLE%%/DOSE-EQ beam ${beamyear} year, ${dname} cooling (2625Bx, 5Hz)/g" \
           -e "s/%%NORM%%/1E-12*3600/g" \
           -e "s|%%PNGFILE%%|figs/projdoseeq-after-${rt}cooling-${aname}.png|g" \
           >> ${outfile}
   done
 
   detid=1
   project_doseeq ${projection} ${detid} | sed -e "s/%%DATAFILE%%/${fluka_prefix}001-f81.bnn/g" \
           -e "s/%%PLOTNAME%%/projdoseeq-primary-${aname}/g" \
           -e "s/%%TITLE%%/DOSE-EQ primary projection (2625Bx, 5Hz)/g" \
           -e "s/%%NORM%%/1.968E14*1E-12*3600/g" \
           -e "s|%%PNGFILE%%|projdoseeq-primary-${aname}.png|g" \
           >> ${outfile}
 
}

# ###### Primary Dose plot options upto v0606
Primary_Dose_v0606()
{
   plots=$1
   fluka_prefix=$2
   outfile=$3

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

}

# ###### Primary Dose plot options upto v0606
Primary_Dose_v0607()
{
   plots=$1
   fluka_prefix=$2
   outfile=$3

   declare -a detname=("doseEQ" "Edep" "EdepEM" "EdepNiel")

   echo ${declare[@]}

   for detind in `seq 1 ${#detname[@]}` ; do 
     det=$[${detind}-1]
     detn=${detname[${det}]}
     echo "$det $detn "
     pngfile="primary-${detname[${det}]}-target-axis.png"
     normalization="1.602176462E-7*1.968E14*1E-6*3600*5000"
     cblabel="Energy deposite (MGy\/5000 hours)"
     cbmax="1E3"
     cbmin="1E-3"
     if [ ${detn} == "doseEQ" ] ; then  
        normalization="1.968E14*1E-12*3600"
        cblabel="Dose EQ (Sv\/h)"
        cbmax="1E0"
        cbmin="1E9"
     fi
     cat ${plots} | \
        sed -e "s/%%CBMAX%%/1E3/g" -e "s/%%CBMIN%%/1E-3/g" \
            -e "s/%%CBTICS%%/10/g" \
            -e "s/%%XLABEL%%/Z (cm)/g" -e "s/%%YLABEL%%/Radius (cm)/g" \
            -e "s/%%DET%%/${detind}/g" \
            -e "s/%%DATAFILE%%/${fluka_prefix}001-f90.bnn/g" \
            -e "s/%%PLOTNAME%%/prim_${detn}_taraxis/g" \
            -e "s/%%TITLE%%/Primary ${detn}, target axis symmetry (2625Bx, 5Hz)/g" \
            -e "s/%%CBLABEL%%/${cblabel}/g" \
            -e "s/%%NORM%%/${normalization}/g" \
            -e "s/%%PNGFILE%%/${pngfile}/g" \
            >> ${outfile}
   done
}


# ###### Primary Dose plot options upto v0702
Primary_Dose_v0702()
{
   plots=$1
   fluka_prefix=$2
   outfile=$3

   declare -a detname=("rfdose1" "rfEMd1" "rfNiel1" "rfDPA" )

   echo ${declare[@]}

   for detind in `seq 1 ${#detname[@]}` ; do
     det=$[${detind}-1]
     detn=${detname[${det}]}
     echo "$det $detn "
     pngfile="primary-${detname[${det}]}-cavity.png"
     # 1.602176462E-7 : Convert  GeV/g to Gy/g
     # 1Gy = 1J/1kg
     # 1eV = 1.602176[634]E-19J
     if [ ${detn} == "rfDPA" ] ; then
       normalization="1.968E14*3600.0*5000.0*20.0"
       cblabel="Displacement per Atom for 20 years beam"
       cbmax="1.0"
       cbmin="1E-6"
       titopt="2625Bx, 5Hz, 20 years beam"
     else
       normalization="1.602176462E-7*1.968E14*1E-6*3600*5000"
       cblabel="Energy deposite (MGy\/5000 hours)"
       cbmax="1E3"
       cbmin="1E-3"
       titopt="2625Bx, 5Hz"
     fi
     cat ${plots} | \
        sed -e "s/%%CBMAX%%/${cbmax}/g" -e "s/%%CBMIN%%/${cbmin}/g" \
            -e "s/%%CBTICS%%/10/g" \
            -e "s/%%XLABEL%%/Z (cm)/g" -e "s/%%YLABEL%%/Radius (cm)/g" \
            -e "s/%%DET%%/${detind}/g" \
            -e "s/%%DATAFILE%%/${fluka_prefix}001-f86.bnn/g" \
            -e "s/%%PLOTNAME%%/prim_${detn}_cavity/g" \
            -e "s/%%TITLE%%/Primary ${detn}, cavity ${titopt}/g" \
            -e "s/%%CBLABEL%%/${cblabel}/g" \
            -e "s/%%NORM%%/${normalization}/g" \
            -e "s/%%PNGFILE%%/${pngfile}/g" \
            >> ${outfile}
   done

   for detind in 1 2 3 ; do
     det=$[${detind}-1]
     detn=${detname[${det}]}
     echo "$det $detn "
     pngfile="primary-${detname[${det}]}-cavity-miniplus.png"
     # normalization="1.602176462E-7*1.968E14*1E-6*3600*5000"
     # 4.8nC = 4.8E-9 x 6.24153E18 electrons
     # 1 GeV = 1.602176462E-10 J
     # 18122051 events per 100000 G4 particles, means 181 primary for 1 beam e-.
     normalization="1.602176462E-10*4.8E-9*6.24153E18*66.0*181.22"
     cblabel="Energy deposite (J\/g\/66Bxs)"
     cbmax="1E3"
     cbmin="1E-3"
     cat ${plots} | \
        sed -e "s/%%CBMAX%%/1.0/g" -e "s/%%CBMIN%%/1E-4/g" \
            -e "s/%%CBTICS%%/10/g" \
            -e "s/%%XLABEL%%/Z (cm)/g" -e "s/%%YLABEL%%/Radius (cm)/g" \
            -e "s/%%DET%%/${detind}/g" \
            -e "s/%%DATAFILE%%/${fluka_prefix}001-f86.bnn/g" \
            -e "s/%%PLOTNAME%%/prim_${detn}_cavity-minipulse/g" \
            -e "s/%%TITLE%%/Primary ${detn}, cavity (J\/g\/mini-pulse, 4.8nC x 66 bunches)/g" \
            -e "s/%%CBLABEL%%/${cblabel}/g" \
            -e "s/%%NORM%%/${normalization}/g" \
            -e "s/%%PNGFILE%%/${pngfile}/g" \
            >> ${outfile}
   done
}

