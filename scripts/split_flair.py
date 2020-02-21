#!/usr/bin/env python
#

import argparse
import os
import pprint
import json

# ###################################################################

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Split flair file into each plot component")
    parser.add_argument("infile", help="flair file.")
    parser.add_argument("-d", help="Output directory", dest="outdir", action="store", default="flsplit")

    args = parser.parse_args()

    infile=args.infile
    outdir=args.outdir

    state = ""
    outrec = {}

    lines = open(infile).readlines()
  
    curkey = ""
    while len(lines) > 0:
        line = lines.pop(0)[:-1]
        if line.startswith("#!/home/ilc"):
           curfile = "HEADER.fl"
           outrec[curfile]=[line]
        elif line.startswith("# Material"):
           mdata = lines.pop(0)[:-1]
           curfile = mdata.split(" ",1)[1]+".mat"
           outrec[curfile]=[line, mdata]
        
        elif line.startswith("# Geometry Information"):
           curfile = "GEOINFO.fl"
           outrec[curfile] = [line]
     
        elif line.startswith("# Geometry plot "):
           ndata = lines.pop(0)[:-1]
           curfile = ndata.split(" ",1)[1] + ".mat"
           outrec[curfile] = [line, ndata]

        elif line.startswith("# USRBIN plot"):
           ndata = lines.pop(0)[:-1]
           curfile = ndata.split(" ",1)[1] + ".fp"
           outrec[curfile] = [line, ndata]

        else:
           outrec[curfile].append(line)


    # pprint.pprint(outrec)
  
    json.dump(outrec, open("fdata.json","w"))

    # Output devided files
    for key in outrec:
       fout = open("/".join([outdir, key]),"w")
       fout.write("\n".join(outrec[key]))
       fout.close()


