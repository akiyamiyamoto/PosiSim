#!/usr/bin/env python 

import os
import glob
import json

import ROOT

_DATA_UNITS=range(30, 38)
_INPUT_DATA_DIR="jobs/job*"
# _ROOT_FILE_NAME="resnuclei.root"
_OUTPUT_DATA_DIR="resnuclei_data"


# ####################################################
def unpack_usrsuw(inpref, fileno):
    ''' Unpack *_tab.lis file for each detector '''
    
    infile = inpref + "_tab.lis"
    data = {}
    temp = {}
    for line in open(infile):
        if "# Detector" in line:
           detnb = line[:-1].strip().split()[3]
           temp[detnb] = []
        else:
           temp[detnb].append(line[:-1])

    for detnb in temp:
       data[detnb] = {"detector":detnb, "detname":temp[detnb][0].strip(), 
               "fileno":fileno,
               "isotopes":[], "isomers":[] }
       is_isotopes=1
       for il in range(2, len(temp[detnb])):
           if "Isomers" in temp[detnb][il]:
               is_isotopes=0
           elif is_isotopes == 1:
               (a,z,nb, frac) = temp[detnb][il].split()
               # print a,z,nb

               data[detnb]["isotopes"].append([a, z, nb, frac])
           elif is_isotopes == 0:
               (a, z, m, nb, frac ) = temp[detnb][il].split()
               data[detnb]["isomers"].append([a, z, m, nb, frac])

    #    data.append(adet)

    return data

# ####################################################
def add_resnucle(out_prefix, fid):
    ''' Add resnuclei files. '''
    global _DATA_UNITS, _INPUT_DATA_DIR

    cwd = os.getcwd()
    outdir = out_prefix
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    os.chdir(outdir)
    alldata = {}

    for fu in _DATA_UNITS:
        outname = "%s-f%2.2d" % ( outdir, fu )
        flist=outname+".usrsuw" 
        tfiles = glob.glob("../%s/*_fort.%s" % ( _INPUT_DATA_DIR, str(fu) )) 
        # print tfiles
        if len(tfiles) <= 1:
           print "Target files not found. "
           print "_INPUT_DATA_DIR="+_INPUT_DATA_DIR
           print "fu="+str(fu)
           continue


        fout=open(flist,"w")
        fout.write("\n".join(tfiles + [" ", outname]))
        fout.close()

    # execute usrsuw to merge relevant files.
        cmd = "usrsuw < %s 2>&1 | tee %s.log" % ( flist, outname )
        os.system(cmd)

    # strip them to each detectors and isotopes, isomers
        alldata[fu] = unpack_usrsuw(outname, fu)
    #    json.dump(data, open("%s.json" % out_prefix, "w"))

    # Output as data file for gnuplot later
    #    for det in range(0, len(data)):
    #        detnb = data[det]["detector"]
    #        name = data[det]["detname"]
    #        fileno = data[det]["fileno"]
    #        for iso in ["isomers", "isotopes"]:
    #            fname = "%s-%s-%s.dat" % (outname, name, iso )
    #            if iso == "isomers":
    #                for adat in data[det][iso]:
    #                   nt.Fill(float(fid), float(fileno), float(det), 2., 
    #                   float(adat[0]), float(adat[1]), float(adat[2]), float(adat[3]), float(adat[4]))
    #            else:
    #                for adat in data[det][iso]:
    #                   nt.Fill(float(fid), float(fileno), float(det), 1., 
    #                   float(adat[0]), float(adat[1]), -1.0,  float(adat[2]), float(adat[3]))
                
    #            #fout=open(fname,"w")
    #            #for lut in data[det][iso]:
    #            #    fout.write(" ".join(lut+["\n"]))
    #            #fout.close()

    json.dump(alldata, open("%s.json" % out_prefix, "w"))

    os.chdir(cwd)

    return alldata
    
##########################################################
if __name__ == "__main__":

    if os.path.exists("setting.py"):
       execfile("setting.py")


    # rf = ROOT.TFile(_ROOT_FILE_NAME,"recreate")
    # nt = ROOT.TNtuple("nt","resnuclei","fid:fno:did:isiso:a:z:m:nb:r")

    data = add_resnucle(_OUTPUT_DATA_DIR, 1)

    # nt.Write()
    # rf.Close()

