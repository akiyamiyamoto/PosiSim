#!/bin/bash 


. /sw/ilc/gcc920/setup-gcc920.sh

export FLUPRO=${HOME}/fluka/gcc92
if [ ! -e ${FLUPRO} ] ; then 
  mkdir -v ${FLUPRO}
fi

export FLUFOR=gfortran
which ${FLUFOR}

cd ${FLUPRO}

tar -zxf ../orig/fluka2011.2x-linux-gfor64bitAA-9.2.tar.gz

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

(
cd ${FLUPRO}/..
tar zxf orig/flair-2.3-0.tgz
cd flair-2.3
tar zxf ../orig/flair-geoviewer-2.3-0.tgz
ln -s flair-geoviewer-2.3 geoviewer
./install.sh install . 2>&1 | tee install.log

echo "flair was installed."
)






