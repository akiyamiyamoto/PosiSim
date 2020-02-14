
OBJL = magfld.o
EXE  = bffluka

all: ${EXE}

magtest:  magtest.f magfld.o
	gfortran -o magtest magtest.f magfld.o

magfld.o: magfld.f
	${FLUPRO}/flutil/fff $?

${EXE}: ${OBJL}
	${FLUPRO}/flutil/lfluka -L${FLUPRO} -L${FLUPRO}/interface -L${FLUPRO}/latestRQMD \
	-l dpmjet3 -l rqmd -O dpmmvax -O rqmdmvax -m fluka -o ${EXE} ${OBJL}

install: ${EXE}
	install ${EXE} ${FLUPRO}
	install -m 644 ${EXE}.map ${FLUPRO}

clean:
	rm -fv magfld.o ${EXE} ${EXE}.map magtest

