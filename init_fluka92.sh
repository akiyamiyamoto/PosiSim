
# Setup fluka built with gcc920


# . ${HOME}/soft/gcc830/init_gcc830.sh 

. /sw/ilc/gcc920/setup-gcc920-py3.sh 

export PATH=/sw/ilc/gcc920/binutils/2.33.1/bin:${PATH}

# QT setup
#--------------------------------------------------------------------------------
#     QT
#--------------------------------------------------------------------------------
#export QTDIR="/cvmfs/ilc.desy.de/sw/x86_64_gcc49_sl6/v02-00-02/QT/4.7.4"
#export QMAKESPEC="$QTDIR/mkspecs/linux-g++"
#export PATH="$QTDIR/bin:$PATH"
#export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${QTDIR}/lib"




export FLUKA=${HOME}/fluka
export FLUPRO=${FLUKA}/gcc92
export FLUFOR=gfortran
export FLUKA_SCRIPTS=${FLUKA}/scripts

export PATH=${FLUKA_SCRIPTS}:${FLUPRO}:${FLUPRO}/flutil:${FLUKA}/flair-2.3:${FLUKA}/au-fluka-tools:${PATH}
export PYTHONPATH=${FLUKA_SCRIPTS}:${PYTHONPATH}


