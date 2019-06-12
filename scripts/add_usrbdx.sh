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


add_usrbdx()
{ 
   tdir=$1
   outdir=$2
   mkdir -p ${outdir}
   ( 
      cd ${outdir}
      for fu in 21 22 23 ; do 
         outname="$2-f${fu}"
         find ../${tdir}/feopt2-* -name "*_fort.${fu}" -print > ${outname}.usxsuw
         echo "" >> ${outname}.usxsuw
         echo "${outname}" >> ${outname}.usxsuw
         usxsuw < ${outname}.usxsuw 2>&1 | tee  ${outname}.log  
         tabfile=`/bin/ls ${outname}_tab.lis | head -1`
         echo "######## tabfile ${tabfile} .... outname ${outname} ############ "
         devfile ${tabfile} ${outname}
      done
   )
}

add_usrbdx ../thick30  thick30
# add_usrbdx ../thick35  thick35
# add_usrbdx ../thick55  thick55
# add_usrbdx ../thick75  thick75

