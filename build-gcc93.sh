#!/bin/bash 

# script_dir=$(cd $(dirname $0);pwd)

fluka_dir=${HOME}/fluka
fluka_version=4-1.1

cd ${fluka_dir}
source ${fluka_dir}/init_fluka93.sh

# ################################################
echo "Installing FLUKA${fluka_version}"
tar zxf ${fluka_dir}/orig/fluka-${fluka_version}.Linux-gfor9.tgz
( cd fluka${fluka_version}/src  ;  make  )
( cd fluka${fluka_version}/bin ; ./ldpmqmd -o flukadpm )

# ################################################
echo "Installing python module"
mkdir -p ${fluka_dir}/python
python -m pip install --user pillow numpy pydicom gdcm

# ################################################
echo "Installing flair"
tar xf orig/flair-3.1-14.tgz
( cd flair-3.1 

  tar xf ../orig/dicom.tgz

  tar xf ../orig/flair-geoviewer-3.1-14.tgz
  ln -s flair-geoviewer-3.1 geoviewer
  ( cd flair-geoviewer-3.1 
    make -j 4
    make install DESTDIR=${fluka_dir}/flair-3.1
  )
)
 
echo "Build-gcc93.sh completed." 



