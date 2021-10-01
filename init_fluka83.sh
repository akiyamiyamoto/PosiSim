
# gcc83 setup
. /cvmfs/sft.cern.ch/lcg/contrib/gcc/8.3.0/x86_64-centos7/setup.sh

# python2.7 setup
lcg=/cvmfs/sft.cern.ch/lcg/releases/LCG_98

export LD_LIBRARY_PATH=${LCG}/Python/2.7.16/x86_64-centos7-gcc8-opt/lib:${LD_LIBRARY_PATH}
export PATH=${LCG}/Python/2.7.16/x86_64-centos7-gcc8-opt/bin:${PATH}

# CMake setup
export PATH=${lcg}/CMake/3.17.3/x86_64-centos7-gcc8-opt/bin:${PATH}

export FLUKA=${HOME}/fluka
export FLUPRO=${FLUKA}/gcc83
export FLUFOR=gfortran
export FLUKA_SCRIPTS=${FLUKA}/scripts

export PATH=${FLUKA_SCRIPTS}:${FLUPRO}:${FLUPRO}/flutil:${FLUKA}/flair-2.3:${PATH}
export PYTHONPATH=${FLUKA_SCRIPTS}:${PYTHONPATH}

if [ "x`echo ${PWD} | grep fluka`" == "x" ] ; then 
  cd ${FLUKA}
fi

