#!/bin/bash 

# script_dir=$(cd $(dirname $0);pwd)

fluka_dir=${HOME}/fluka

cd ${fluka_dir}
source ${fluka_dir}/init_fluka93.sh

tar zxf ${fluka_dir}/orig/fluka-4-1.1.Linux-gfor9.tgz

( 
  cd fluka-4-1.1
  make 

)

mkdir -p ${fluka_dir}/python

python -m pip install --user pillow pydicom gdcm



cd ${FLUPRO}

tar -zxf ../orig/fluka2021.2-linux-gfor64bit-10.3-AA.tar.gz

make -j20

cd ${FLUPRO}
flutil/ldpmqmd
echo "flukadpm3 was created."
(
  cd ${FLUPRO}/flutil
  sed -e "s|FTOP/flukahp|FTOP/flukadpm3|g" rfluka > rflukadpm3
  chmod +x rflukadpm3
  echo "rflukadpm was created in `pwd`"
)

exit

(
tar xf ${fluka_dir}/orig/flair-3.1-14.tgz
cd flair-3.1
tar xf ${fluka_dir}/orig/flair-geoviewer-3.1-14.tgz
ln -s flair-geoviewer-3.1 geoviewer
./install.sh install . 2>&1 | tee install.log

echo "flair was installed."
)






