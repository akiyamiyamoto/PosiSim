#!/bin/bash 

devfile()
{
   infile=$1
   outpref=$2
   outfile=${outpref}.dummy

pwd
echo ${infile}
echo ${outpref}

python <<EOF
ncnt=-1
isopen=0
for line in open("$infile"):  
  lenline = len(line.replace("\n","").replace(" ",""))
 
  # if "#" in line or lenline < 2:
  #   print line[0:10] + " " + str(lenline)+ " " + str(ncnt) + " isopen" + str(isopen)
  

  if lenline < 2:
     if isopen != 0:
        fout.close()
        isopen = 0
  else:
     if isopen == 0:
        ncnt+=1
        outfile="${outpref}-det%d.dat" % ncnt
        fout=open(outfile,"w")
        isopen = 1
     #   print "Print after open : " + line[:-1]
     fout.write(line)

if isopen != 0:
  fout.close() 
EOF

}


exec_usrsuw()
{ 
   srcdir=${PWD}/$1
   outdir=$2
   fu=$3

   outpref=`( cd ${srcdir}/job001 && /bin/ls *.inp | sed -e "s/\.inp//g" )` 
  
#   mkdir -p ${outdir}
   ( 
      cd ${outdir}
      outname="${outpref}-f${fu}"
      find ${srcdir} -name "*_fort.${fu}" -print > ${outname}.usxsuw
      echo "" >> ${outname}.usxsuw
      echo "${outname}" >> ${outname}.usxsuw
      cat ${outname}.usxsuw
      usxsuw < ${outname}.usxsuw 2>&1 | tee  ${outname}.log  
      tabfile=`/bin/ls ${outname}_tab.lis | head -1`
      echo "######## tabfile ${tabfile} .... outname ${outname} ############ "
      devfile ${tabfile} ${outname}
   )
}

rsplit(){
  instr=$1
  sep=$2
  python <<EOF
instr="${instr}"
sep="${sep}"
ostr=instr.rsplit(sep,1)[1]
print ostr
EOF
}

source setting.ini

echo ${usrbdx_unit}

# usrbdx_unit=21
det=1
for fu in ${usrbdx_unit} ; do
  exec_usrsuw jobs results ${fu} 
done 
