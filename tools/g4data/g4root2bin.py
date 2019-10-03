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

# if __name__ == "__main__":

g4root = "g4dump.root"
tf = ROOT.TFile(g4root)
nt = tf.Get("fluka")
zmax = 10000.0

g4out = "g4data.dat"
nentry = nt.GetEntries()

varnam = ["evnID", "pdgID", "t","x", "y", "z", "px", "py", "pz", "e"]

myunit=45
writebin.open(myunit, g4out )

maxent = 100
nout = 0
nread = 0
for i in range(0, nentry):
   nt.GetEntry(i)
   nread += 1L
   if nt.z > zmax:
       continue
   # r = math.sqrt(nt.x*nt.x + nt.y*nt.y)
   nout += 1L
   if nout < 5 or long(nout)%10000L == 0L:
     print("%d, %d ID=%d (t,x,y,z)=(%g, %g, %g, %g) (e,px,py,pz)=(%g, %g, %g, %g)" % (nout, nt.evnID, nt.pdgID, 
               nt.t, nt.x, nt.y, nt.z, nt.e, nt.px, nt.py, nt.pz) )

   evtID = long(nt.evnID)
   pdgID = long(nt.pdgID)
   x = [nt.t, nt.x, nt.y, nt.z]
   y = [nt.e, nt.px, nt.py, nt.pz]
   writebin.write(myunit, evtID, pdgID, x, y)

writebin.close(myunit)

print "Output binary data has completed."
print "Input Geant 4 data : " + g4root
print "Output binary data : " + g4out
print "Read  "+ str(nread) + " entries"
print "Write " + str(nout) + " entries"
print "  Applied cut on Z, Zmax = " + str(zmax)

