#!/usr/bin/env python 
#
# Read Geant4 data prepared by Fukuda-san and output binary data 
# readable by Fluka's user source program.
# writebin.so is required to run this program. It can be build by 
# make_writebin.sh script, which uses f2py command.
# 


import math
import writebin
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert ascii magfield data to Fortran binary file.")
    parser.add_argument("-i", help="Input magfld data", dest="magin",
                              action="store", default="fc_magfld.dat")
    parser.add_argument("-o", help="Output fortran binary file name", dest="magout", 
                              action="store", default="fc_magfld.bnn")
    parser.add_argument("--zmax", help="Maximum Z position (mm unit)of particles for output.",
                              dest="zmax", action="store", default="300.0")
    parser.add_argument("--zmin", help="Minmum Z position (mm unit)of particles for output.",
                              dest="zmin", action="store", default="-10.0")
    parser.add_argument("--nprint_rate", help="Rate to printout particle information.",
                              dest="nprint_rate", action="store", default="10000L")

    args = parser.parse_args()
    
    magin = args.magin
    magout = args.magout
    zmax = float(args.zmax)
    zmin = float(args.zmin)
 
    myunit = 45    
    writebin.open(myunit, args.magout)
    print("Opened %s to output mag field data in binary format" % magout)
    nout = 0

    for fin in open(magin):
       data = fin[:-1].split()
       znow = float(data[0])
       if znow < zmin : 
           continue
       elif znow <= zmax :
#          print(str(data[0]) + " " + str(data[1])+" "+str(data[3])+" " +str(data[5]))
           x = [ data[0], data[1], data[3], data[5] ]
           writebin.write(myunit, x )
           nout += 1
       else:
           break
   
    writebin.close(myunit)
 
    print(" %d of data from %g to %g was written to %s " % (nout, zmin, zmax, magout ))

'''
    tf = ROOT.TFile(g4root)
    nt = tf.Get("fluka")
    nentry = nt.GetEntries()
    
    varnam = ["evnID", "pdgID", "t","x", "y", "z", "px", "py", "pz", "e"]

    (pref, ftype) = g4out.rsplit('.',1)
    pidfound = {}
    
    myunit=45
    nread = 0
    nototal = 0

    stats = {"zin":{"esum":0.0, "entries":0L}, 
             "zout":{"esum":0.0, "entries":0L},
             "vaccum":{"entries":0L} }

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
           stats["zout"]["esum"] += nt.e
           stats["zout"]["entries"] += 1L
           continue
       # r = math.sqrt(nt.x*nt.x + nt.y*nt.y)
       stats["zin"]["esum"] += nt.e
       stats["zin"]["entries"] += 1L
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
       p = [nt.e, nt.px, nt.py, nt.pz]
       r = math.sqrt(nt.x*nt.x + nt.y*nt.y)
       #if nt.z > 150.0 and nt.z < 50000.0 and r < 3.0:
       #   print("Warning ---Particle position is in vaccum of RF cavity regions. ")
       #   print("Entry is %d, %d ID=%d (t,x,y,z)=(%g, %g, %g, %g) (e,px,py,pz)=(%g, %g, %g, %g)" % (nototal, nt.evnID, nt.pdgID, 
       #            nt.t, nt.x, nt.y, nt.z, nt.e, nt.px, nt.py, nt.pz) )
       #   stats["vaccum"]["entries"] += 1L
                     
       writebin.write(myunit, evtID, pdgID, x, p)
    
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

    print ""
    print "Zin  particle: Total kinetic energy sum=%g, Nb. entries=%d" % (stats["zin"]["esum"], stats["zin"]["entries"] )
    print "Zout particle: Total kinetic energy sum=%g, Nb. entries=%d" % (stats["zout"]["esum"], stats["zout"]["entries"] )
    #print ""
    #print "# of particles in cavity vaccum region=%d" % stats["vaccum"]["entries"]
    

'''
