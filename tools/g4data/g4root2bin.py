#!/usr/bin/env python 
#
# Read Geant4 data prepared by Fukuda-san and output binary data 
# readable by Fluka's user source program.
# writebin.so is required to run this program. It can be build by 
# make_writebin.sh script, which uses f2py command.
# 


import ROOT
import math
import writebin
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert Geant4 data in root to Fortran binary file.")
    parser.add_argument("-i", help="Input Geant4 root file name", dest="g4root",
                              action="store", default="g4dump.root")
    parser.add_argument("-o", help="Output fortran binary file name", dest="g4out", 
                              action="store", default="g4data.dat")
    parser.add_argument("--zmax", help="Maximum Z position (mm unit)of particles for output.",
                              dest="zmax", action="store", default="10000.0")
    parser.add_argument("--nout_per_file", help="Number of events per output file. 0 for no limit",
                              dest="nout_per_file", action="store", default="0")
    parser.add_argument("--nout_max", help="Max number of output particles. 0 for no limit",
                              dest="nout_max", action="store", default="0")
    parser.add_argument("--nprint_rate", help="Rate to printout particle information.",
                              dest="nprint_rate", action="store", default="10000L")

    args = parser.parse_args()
    

    g4root = args.g4root
    g4out = args.g4out
    zmax = float(args.zmax)
    nout_per_file = long(args.nout_per_file)
    nout_max = long(args.nout_max)
    nprint_rate = long(args.nprint_rate)


    tf = ROOT.TFile(g4root)
    nt = tf.Get("fluka")
    nentry = nt.GetEntries()
    
    varnam = ["evnID", "pdgID", "t","x", "y", "z", "px", "py", "pz", "e"]

    (pref, ftype) = g4out.rsplit('.',1)
    pidfound = {}
    
    myunit=45
    nread = 0
    nototal = 0
    if nout_per_file == 0:
        writebin.open(myunit, g4out )
        print "Opened %s for output data" % g4out
        nout = 0
    else:
        nfile = 1
        g4out = "%s.%s.%s" % (pref, str(nfile), ftype)
        writebin.open(myunit, g4out )
        print "Opened %s for output data" % g4out
        nout = 0
    
    iout_max = nentry if nout_max == 0 else nout_max
    while nread < nentry  and nototal < iout_max:
       nt.GetEntry(nread)
       nread += 1L
       if nt.z > zmax:
           continue
       # r = math.sqrt(nt.x*nt.x + nt.y*nt.y)
       nout += 1L
       nototal += 1L
       if nout_per_file != 0 and nout > nout_per_file:
          writebin.close(myunit)
          nfile += 1L
          print "Closed %s with %d particles." % (g4out, nout-1),
          g4out = "%s.%s.%s" % (pref, str(nfile), ftype)
          writebin.open(myunit, g4out )
          print "Opened %s at nread=%d, nout_total=%d" % (g4out, nread, nototal)
          nout = 1
          
       if nototal < 5 or long(nototal)%nprint_rate == 0L:
         print("%d, %d ID=%d (t,x,y,z)=(%g, %g, %g, %g) (e,px,py,pz)=(%g, %g, %g, %g)" % (nototal, nt.evnID, nt.pdgID, 
                   nt.t, nt.x, nt.y, nt.z, nt.e, nt.px, nt.py, nt.pz) )
    
       evtID = long(nt.evnID)
       pdgID = long(nt.pdgID)
       x = [nt.t, nt.x, nt.y, nt.z]
       y = [nt.e, nt.px, nt.py, nt.pz]
       writebin.write(myunit, evtID, pdgID, x, y)
    
       if pdgID in pidfound:
           pidfound[pdgID] += 1
       else:
           pidfound[pdgID] = 1

    writebin.close(myunit)
    
    print "Output binary data has completed."
    print "Input Geant 4 data : " + g4root
    print "Read  "+ str(nread) + " entries"
    if nout_per_file == 0:
        print "Output binary data : " + g4out
        print "Write " + str(nototal) + " particles in total."
    else:
        print "Last output binary data was %s. Output %d files." % (g4out, nfile)
        print "Write " + str(nout) + " particles in last file."
    print "  Applied cut on Z, Zmax = " + str(zmax)
    
    print "Particle ID found and number of particles."
    for k in pidfound.keys():
        print str(k) + ":" + str(pidfound[k])


