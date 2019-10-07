
OBJL = source.o

all: myfluka

source.o: source.f
	${FLUPRO}/flutil/fff $?.f

myfluka: ${OBJL}
	${FLUPRO}/flutil/lfluka -L${FLUPRO} -L${FLUPRO}/interface -L${FLUPRO}/latestRQMD \
	-l dpmjet3 -l rqmd -O dpmmvax -O rqmdmvax -m fluka -o myfluka ${OBJL}

install: myfluka
	install myfluka ${FLUPRO}
	install -m 644 myfluka.map ${FLUPRO}

