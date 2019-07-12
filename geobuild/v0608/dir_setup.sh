#!/bin/bash
# A script to copy files from previous version 
# to create geobuild scripts.
#

if [ `/bin/ls | wc -l` -gt 1 ] ; then 
  echo "It seems this directory is not empty."
  echo "Please proceed after removing files. "
  echo "All files except this script will be over-written."
  exit
fi

srcdir=../v0607
srcversion="v0607"
echo "Get sample files from ${srcdir}"
version=`basename ${PWD}`

cp -p ${srcdir}/*.py .
sed -e "s/${srcversion}/${version}/g" ${srcdir}/version.py > version.py
cp -p ${srcdir}/*.inc .
rm -f *-${srcversion}.inc
sed -e "s/${srcversion}/${version}/g" ${srcdir}/geotest.inp > geotest.inp
cp -p ${srcdir}/.gitignore .

mkdir temp
( 
  cd temp
  ln -s ../*.inc .
  ln -s ../geotest.inp .
)

datestr=`date`
changelog="Changes.txt"
cat > ${changelog} <<EOF
# ########################################################
${version} created on ${datestr}

EOF
cat ${srcdir}/${changelog} >> ${changelog}

