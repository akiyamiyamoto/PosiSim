
# Setup fluka built with gcc83


. ${HOME}/soft/gcc830/init_gcc830.sh 

export FLUKA=${HOME}/fluka
export FLUPRO=${FLUKA}/gcc83
export FLUFOR=gfortran
export FLUKA_SCRIPTS=${FLUKA}/scripts

export PATH=${FLUKA_SCRIPTS}:${FLUPRO}:${FLUPRO}/flutil:${FLUKA}/flair-2.3:${FLUKA}/au-fluka-tools:${PATH}
export PYTHONPATH=${FLUKA_SCRIPTS}:${PYTHONPATH}

if [ "x`echo ${PWD} | grep fluka`" == "x" ] ; then 
  cd ${FLUKA}
fi

