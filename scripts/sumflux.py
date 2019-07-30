#!/bin/env python
#
# Sum data of two files of USRBDX
#
import os
import argparse
import pprint
import math
import glob

# ###########################################
def load_file(filename):
    data = []
    comment = []
    print "# Reading from " + filename
    comment.append(" # Read from " + filename )
    for line in open(filename):
       if "#" in line[0:5]:
          print line[:-1]
          comment.append(line[:-1])
       else:
           vals = line.replace("\n","").split()
           rec = []
           for v in vals:
               rec.append(float(v))
           data.append(rec)
    return {"data":data, "comment":comment}

# ###########################################
def sum_data(indata):

    out = []
    out.append(" # Sum of USRBDX files ")
    for dat in indata:
       com = dat["comment"]
       out += com

    lndata = len(indata[0]["data"])
    integ = 0.0
    integesq = 0.0
    for ip in range(0, lndata):
       vsum = 0.0
       errsum = 0.0
       xmin = indata[0]["data"][ip][0]
       xmax = indata[0]["data"][ip][1]
       xstep = xmax - xmin
       for jp in range(0, len(indata)):
           if indata[jp]["data"][ip][0] != xmin or indata[jp]["data"][ip][1] != xmax:
              print "FATAL ERROR: "+str(jp)+"-th file, "+str(ip)+"-th data, xmin or xmax is not consistent with other data."
              exit(0)

           val  = indata[jp]["data"][ip][2]
           rerr = indata[jp]["data"][ip][3]*0.01
           vsum += val
           errsum += rerr*rerr*val*val
           integ += val*xstep
           integesq += (val*rerr*xstep)**2
       
       relerr = math.sqrt(errsum)/vsum*100.0 if vsum > 0.0 else 0.0    
       interr = math.sqrt(integesq) 

       out.append("  ".join(["%8e" % xmin, "%8e" % xmax, "%8e" % vsum, "%8e" % relerr, "%8e"%integ, "%8e"%interr ]))

    return out

# ###########################################
if __name__ == "__main__":

    result1 = load_file(glob.glob("results/*001-f21-det0.dat")[0])
    result2 = load_file(glob.glob("results/*001-f22-det0.dat")[0])
    # pprint.pprint(dat1)
    added = sum_data([result1, result2])
    
    os.mkdir("flux")
    fout=open("flux/neutron.dat","w")
    fout.write("\n".join(added))
    fout.close()


    result3 = load_file(glob.glob("results/*001-f27-det0.dat")[0])
    result4 = load_file(glob.glob("results/*001-f28-det0.dat")[0])
    # pprint.pprint(dat1)
    photon = sum_data([result3, result4])
    
    fout=open("flux/photon.dat","w")
    fout.write("\n".join(photon))
    fout.close()

