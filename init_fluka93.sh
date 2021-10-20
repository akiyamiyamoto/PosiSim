
# gcc9.3.0 setup
. /cvmfs/sft.cern.ch/lcg/contrib/gcc/9.3.0/x86_64-centos7-gcc9-opt/setup.sh

# python3.8.6 setup
lcg=/cvmfs/sft.cern.ch/lcg/releases/LCG_100

export LD_LIBRARY_PATH=${lcg}/Python/3.8.6/x86_64-centos7-gcc9-opt/lib:${LD_LIBRARY_PATH}
export PATH=${lcg}/Python/3.8.6/x86_64-centos7-gcc9-opt/bin:${PATH}

# CMake setup
export PATH=${lcg}/CMake/3.20.0/x86_64-centos7-gcc9-opt/bin:${PATH}

export FLUKA=${HOME}/fluka
export FLUKA_SCRIPTS=${FLUKA}/scripts


# PYTHON PIP install directory
export PYTHONUSERBASE=${HOME}/fluka/python
#
# To install python package, do 
#  python -m pip install --user <module>
#

#export FLUPRO=${FLUKA}/gcc103
#export FLUFOR=gfortran
#export FLUKA_SCRIPTS=${FLUKA}/scripts

# Fluka binary
export PATH=${FLUKA}/scripts:${FLUKA}/fluka4-1.1/bin:${FLUKA}/flair-3.1:${FLUKA}/python/bin:${PATH}

# export PATH=${FLUKA_SCRIPTS}:${FLUPRO}:${FLUPRO}/flutil:${FLUKA}/flair-2.3:${PATH}
export PYTHONPATH=${FLUKA}/scripts:${FLUKA}/python:${PYTHONPATH}

if [ "x`echo ${PWD} | grep fluka`" == "x" ] ; then 
  cd ${FLUKA}
fi

