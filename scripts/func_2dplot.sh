
#runyear="1"
#inifile="gnuplot.flair.ini"
#datadir="plot"

#outdir="figs"
#outfile="2dplot.plt"

# ###########################################################
PlotDoseMap()
{ 
    funit=81
    ptype="pri"
    georegion="all"
    funit=$1
    ptype=$2
    georegion=$3

    if [ "x${ptype}" == "xpri" ] ; then 
        norm=${NORM["primary"]}
        pname=${CPERIOD[$ptype]}
        datafile="f${funit}-${ptype}${georegion}.dat"    
        [ "f${funit}" == "f90" ] &&  datafile="f90-pAdoseEQ.dat"
        rangestr="[1E-6:1E6]"
    else
        norm=${NORM["decay"]}
        pname="${CPERIOD[$ptype]} cooling"
        datafile="f${funit}-Sv${ptype}${georegion}.dat"    
        rangestr="[1E-9:1E2]"
    fi

    if [ ! -e ${datadir}/${datafile} ] ; then 
       echo "${datadir}/${datafile} does not exist"
    fi
    geodata=${GEOMAP[${funit}]}
    pngfile="f${funit}-doseeq-${ptype}-${georegion}.png"
    usgeo="5:3:(0.)"


    cat >>${outfile} <<EOF
#
# Gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion}
#
load "${inifile}"
#set origin -0.02,0.0
#
set cbrange ${rangestr}
set cblabel 'Dose rate (Sv/hour)'
set ylabel offset 0.0
set ylabel 'Radius (cm)'
set xlabel 'Z (cm)'
set title '${title_beamon} beam: dose-eq ${pname}, ${georegion} (2625Bx, 5Hz)'
set terminal png size 1000,1000
set out "${outdir}/${pngfile}"
EOF

#    if [ "${georegion}" == "tarA" ] ; then 
#      cat >>${outfile} <<EOF
#set ylabel "Distance from rotation axis (cm)"
#set yrange [0:30]
#set xrange [-40:0]
#EOF
#      usgeo="5:(22.0-(\$3)):(0.)"
#    fi   

    cat >>${outfile} <<EOF
splot '${datadir}/${datafile}'  us 1:2:((\$3)*${norm}) notitle ,'${geodata}' ind 0 us ${usgeo} w l ls 1 notit
# set terminal qt size 1000,1000
# replot
print "${outdir}/${pngfile} was created."
EOF
     echo "Created gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion} in ${outfile}"
}

# ###########################################################
PlotActivityMap()
{
    funit=$1
    ptype=$2
    georegion=$3

    if [ "x${ptype}" == "xpri" ] ; then
        pname=${CPERIOD[$ptype]}
        datafile="f${funit}-${ptype}${georegion}.dat"
        rangestr="[1:1E9]"
    else
        pname="${CPERIOD[$ptype]} cooling"
        datafile="f${funit}-Bq${ptype}${georegion}.dat"
        rangestr="[1:1E12]"
    fi
    norm=${NORM["activity"]}
    geodata=${GEOMAP[${funit}]}
    pngfile="f${funit}-activity-${ptype}-${georegion}.png"
    usgeo="5:3:(0.)"

    cat >>${outfile} <<EOF
#
# Gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion}
#
load "${inifile}"
#set origin -0.02,0.0
#
set cbrange ${rangestr}
set cblabel 'Activity (Bq/cm^3)'
set ylabel offset 0.0
set ylabel 'Radius (cm)'
set xlabel 'Z (cm)'
set title '${title_beamon}  beam: Activity ${pname}, ${georegion} (2625Bx, 5Hz)'
set terminal png size 1000,1000
set out "${outdir}/${pngfile}"
EOF
    if [ "${georegion}" == "AlltAx" ] ; then
      cat >>${outfile} <<EOF
set ylabel "Distance from rotation axis (cm)"
set yrange [0:30]
set xrange [-40:0]
EOF
      usgeo="5:(22.0-(\$3)):(0.)"
    fi

    cat >>${outfile} <<EOF
splot '${datadir}/${datafile}'  us 1:2:((\$3)*${norm}) notitle ,'${geodata}' ind 0 us ${usgeo} w l ls 1 notit
# set terminal qt size 1000,1000
# replot
print "${outdir}/${pngfile} was created."
EOF
     echo "Created gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion} in ${outfile}"
}

# ###########################################################
PlotEdepMap()
{
    funit=$1
    ptype=$2
    georegion=$3

    pname=""
    if [ $VERSION_NUMBER -lt 607 ] ; then
        declare -A PNAME=( ["84"]="Total dose" ["91"]="Total dose" ["85"]="EM dose" ["92"]="EM dose")
        pname=${PNAME[$funit]}
    else
        declare -A PNAME=( ["pAdose"]="total" ["pAdoseEM"]="EM only" ["pANielDep"]="NIEL dep." ["pAdoseEQ"]="dose Eq.")
    fi
    for datafile in `(cd ${datadir} && /bin/ls f${funit}-*.dat)`; do

        ptype=`basename ${datafile} .dat | cut -d"-" -f2-`
        [ ${VERSION_NUMBER} -ge 607 ] && pname=${PNAME[${ptype}]}
        if [ `echo ${ptype} | grep -c "doseEQ"` -gt 0 ] ; then 
            continue 
        fi
        rangestr="[1E-4:1E4]"
        norm=${NORM["edep"]}
        geodata=${GEOMAP[${funit}]}
        pngfile="f${funit}-edep-${ptype}-${georegion}.png"
        usgeo="5:3:(0.)"
    
        cat >>${outfile} <<EOF
#
# Gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion}
#
load "${inifile}"
# set origin 0.0,0.0
#
set cbrange ${rangestr}
set cblabel 'Dose (MGy/5000hour)'
set ylabel offset -0.02,0
set ylabel 'Radius (cm)'
set xlabel 'Z (cm)'
set title '${title_beamon}  beam: Energy deposit ${pname}, ${georegion} (2625Bx, 5Hz)'
set terminal png size 1000,1000
set out "${outdir}/${pngfile}"
EOF
        if [ "${georegion}" == "tarA" ] ; then 
          cat >>${outfile} <<EOF
set ylabel "Distance from rotation axis (cm)"
set yrange [0:30]
set xrange [-40:0]
EOF
          usgeo="5:(22.0-(\$3)):(0.)"
        fi   

        cat >>${outfile} <<EOF
splot '${datadir}/${datafile}'  us 1:2:((\$3)*${norm}) notitle ,'${geodata}' ind 0 us ${usgeo} w l ls 1 notit
# set terminal qt size 1000,1000
# replot
print "${outdir}/${pngfile} was created."
EOF
         echo "Created gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion} in ${outfile}"

    done
}

# ###########################################################
PlotEdepMap_Phi()
{
    funit=$1
    ptype=$2
    georegion=$3

    # declare -A PNAME=( ["84"]="Total dose" ["91"]="Total dose" ["85"]="EM dose" ["92"]="EM dose")
    # pname=${PNAME[$funit]}
    datafile=`(cd ${datadir} && /bin/ls f${funit}-*.dat)`
    ptype=`basename ${datafile} .dat | cut -d"-" -f2-`
    rangestr="[1E-3:1E9]"
    norm=${NORM["edep"]}
    geodata=${GEOMAP["${funit}phi"]}
    pngfile="f${funit}-edep_phi-${ptype}-${georegion}.png"
    usgeo="5:3:(0.)"

    cat >>${outfile} <<EOF
#
# Gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion}
#
load "${inifile}"
# set origin 0.0,0.0
#
set cbrange ${rangestr}
set cblabel 'Dose (MGy/5000hour)'
set ylabel offset -0.02,0
set ylabel 'Radius (cm)'
set xlabel 'Z (cm)'
set title '${title_beamon}  beam: Energy deposit ${pname}, ${georegion} (2625Bx, 5Hz)'
set terminal png size 1000,1000
set out "${outdir}/${pngfile}"
splot '${datadir}/${datafile}'  us (\$2*cos(\$1)):(\$2*sin(\$1)):((\$3)*${norm}) notitle ,${geodata} ind 0 us 1:2:(0.) w l ls 1 notit
# splot 'prim_edep_taraxisphi.dat'  us (\$2*cos(\$1)):(\$2*sin(\$1)):((\$3)*${norm}) notitle ,'Red.dat' ind 0 us 1:2:(0.) w l ls 1 notit
# set terminal qt size 1000,1000
# replot
print "${outdir}/${pngfile} was created."
EOF
     echo "Created gnuplot command for file ${funit}, ptype=${ptype}, georegion=${georegion} in ${outfile}"
}




# #############################################################



Do_Dose(){

  for iu in 81 82 83 ; do
    PlotDoseMap ${iu} "pri" ${FUINFO[$iu]}
  done

  unums="71 73 75"
  for iu in ${unums}  ; do
    nloop=$[${#ORDER[@]}-1]
    for is in `seq 1 ${nloop}`;  do
        PlotDoseMap ${iu} ${ORDER[$is]} ${FUINFO[$iu]}
    done
  done
  
}

Do_Activity(){
  
  unums="72 74 76"
  [ $VERSION_NUMBER -ge 607 ] && unums="72 74 76 94"
  for iu in ${unums} ; do 
     nloop=$[${#ORDER[@]}-1]
     for is in `seq 1 ${nloop}` ; do
        PlotActivityMap ${iu} ${ORDER[$is]} ${FUINFO[$iu]}
     done
  done

}


Do_Edep(){
 
  unums="84 85 91 92"
  [ $VERSION_NUMBER -ge 607 ] && unums="90"
  
  for iu in ${unums}; do 
      PlotEdepMap ${iu} ${ORDER[$is]} ${FUINFO[$iu]}
  done

}

Do_Edep_Phi(){

  for iu in 91 92; do 
      PlotEdepMap_Phi ${iu} ${ORDER[$is]} ${FUINFO[$iu]}
  done

}

