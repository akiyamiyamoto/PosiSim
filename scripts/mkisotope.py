#!/usr/bin/env python 

import os
import glob
import json
import pprint

import ROOT

_DATA_UNITS=range(30, 38)
_INPUT_DATA_DIR="jobs/job*"
_ROOT_FILE_NAME="isotope.root"
_OUTPUT_DATA_DIR="resnuclei_data"

# ####################################################
def get_hot_atoms(jdata, thick, fu, fout, actmin = 1.0):
    #
    # Find active isotopes of each region.
    # First 10 history 
    atomname={"75":["Re", "Rhenium"], 
          "74":["W", "Tungsten"], "73":["Ta","Tantalium"], 
          "72":["Hf", "Hafnium"], "71":["Lu", "Lutetium"], 
          "70":["Yb", "Ytterbium"],"69":["Tm", "Thulium"],
          "66":["Dy", "Dysprosium"], "64":["Gd", "Gadolinium"], 
          "63":["Eu", "Europium"], 
          "29":["Cu", "Copper"], "28":["Ni", "Nickel"], 
          "27":["Co", "Cobalt"], "26":["Fe", "Iron"], 
          "25":["Mn", "Manganese"], "24":["Cr", "Chromium"],
          "20":["Ca", "Calsium"], 
          "18":["Ar", "Argon"],
          "15":["P", "Phosphorous"], "16":["S", "Sulfur"],
          "14":["Si", "Silicon"], "13":["Al", "Aluminum"],
          "12":["Mg", "Magnesium"], "11":["Na", "Sodium"],
          "10":["Ne", "Neon"], "9":["F", "Fluorine"],
          "8":["O", "Oxygen"],"7":["N","Nitrogen"], 
          "6":["C", "Carbon"], "5":["B","Boron"],
          "4":["Be","Berylium"], "3":["Li","Lithium"], 
          "2":["He","Helium"], "1":["H", "Hydrogen"]}


    isotype="isotopes"
    ipiso = 2
    
    period=["1s", "1M", "1h", "1d", "1w", "1m", "3m", "1y", "4y", "Xy", "Zy"]
    _PLOT_PERIOD=[1, 6, 8, 10, 11]
    _PLOT_PERIOD=[1, 2, 4, 5, 6, 8, 9, 10, 11]
    # ind=0
    # colorcode=[0,1,2,3,4,6]
    key="f%d-dn1" % ( int(fu)) 
    header = [ jdata[key]["detname"][2:] ]

    atom_index = []
    active_atom = {}
    for dtype in _PLOT_PERIOD:
       key="f%d-dn%d" % ( int(fu), int(dtype) )
       hotatom = []       
       header.append( jdata[key]["detname"][0:2] )
       period = jdata[key]["detname"][0:2]
       # if len(line) > 0:
       #     for il in range(0, len(line)):
       #         line[il].append([" "])  
       for adat in jdata[key][isotype]:
           nb = adat[ipiso]
           #if float(nb) > actmin :
           if float(nb) > 1.0  :
              hotatom.append([adat[0], adat[1], float(nb)])

       if len(hotatom) > 0:
         nout=0
         # print jdata[key]["detname"] + " hotatom="
         for atom in sorted(hotatom, key=lambda x: x[2], reverse=True):
             nout +=1
             if nout < 20:
                 # print atom[0].rjust(3) + atomname[atom[1]][0].ljust(2) + " %8e"% (atom[2])      
                 aname = atomname[atom[1]][0] if atom[1] in atomname else atom[1]

                 ainfo = atom[0].rjust(3) + (aname +"(%s)" % atom[1]).ljust(6)
                 if ainfo not in active_atom:
                    active_atom[ainfo] = {period:"%6.2e" % atom[2]}
                    atom_index.append(ainfo)
                 else:
                    active_atom[ainfo][period] = "%6.2e" % atom[2]
 
    fout.write(",".join(header)+"\n")
    for ip in atom_index:
       fout.write(ip)
       for hn in header[1:]:
          if hn in active_atom[ip]:
             fout.write(","+active_atom[ip][hn])
          else:
             fout.write(", ")
       fout.write("\n")
    

# ####################################################
def mk_plots_isotopes(jdata, thick, fu, rf, xaxis="Z"):
    #

    # key="f%d-dn%d" % ( int(fu), int(k), v["detname"][0:2] )
    detectors = [ "1h", "1d", "1m", "1y", "10y"]
    plots = {}
    isotype="isotopes"
    ipiso = 2
    xdata={"A":{"index":0, "label":"Mass Number (A)"}, 
           "Z":{"index":1, "label":"Atomic Number (Z)"}}

    ROOT.gStyle.SetOptLogy(1)
    ROOT.gStyle.SetPadGridX(1)
    ROOT.gStyle.SetPadGridY(1)
    ROOT.gStyle.SetOptStat(0)

    xmin=0.0
    xmax=80.0
    xdiv=500

    cv = ROOT.TCanvas("cv","Funit%d"%int(fu), 1200,1000)
    ind=0
    # find xmin and xmax first
    xmin = 200.0
    xmax = -100.0
    ymin = 10000000.0
    # for dtype in [1, 2, 3, 4, 7]:
    for dtype in [1]:
        key="f%d-dn%d" % ( int(fu), int(dtype) )
        for adat in jdata[key][isotype]:
           xv = float(adat[xdata[xaxis]["index"]])
           xmin = xv if xv < xmin else xmin
           xmax = xv if xv > xmax else xmax
           # yv = float(adat[ipiso])
           # ymin = yv if yv < ymin and yv > 0.0 else ymin

    ymin = 1.0E-3
    xmin = xmin - 1.0
    xmax = xmax + 1.0
    xdiv = int(( xmax - xmin +1.0) * 5.0)
    detlist=""
    # Index for _PLOT_PERIOD
    #         0      1    2     3     4     5     6     7     8     9     10    11
    period=["pri", "1s", "1M", "1h", "1d", "1w", "1m", "3m", "1y", "4y", "Xy", "Zy"]
    # _PLOT_PERIOD=[1, 6, 8, 10, 11]
    _PLOT_PERIOD=[1, 4, 7, 8, 10]
    for dtype in _PLOT_PERIOD:
       key="f%d-dn%d" % ( int(fu), int(dtype) )
       detlist += ":%s" % jdata[key]["detname"][0:2]
    detlist += "| det=%s" % jdata["f%d-dn7"%int(fu)]["detname"]
    
    print "xmin=%f xmax=%f xdiv=%f ymin=%f" % ( xmin, xmax, xdiv, ymin)
    ind=0
    colorcode=[0,1,2,3,4,6]
    for dtype in _PLOT_PERIOD:
       plname = "pl%d" % dtype    
       ind +=1 
       # ic = ind if dtype != 7 else 6
       ic=ind
       key="f%d-dn%d" % ( int(fu), int(dtype) )
       
       htitle = "%s:%s,fort%d %s%s" % ( isotype, thick, int(fu), jdata[key]["detname"], detlist)
       plots[plname] = ROOT.TH1D(plname, htitle, xdiv, xmin, xmax)
       plots[plname].SetFillColor(colorcode[ic])
       plots[plname].SetLineColor(colorcode[ic])
       plots[plname].SetLineWidth(0)
       plots[plname].SetMinimum(ymin)
       plots[plname].SetXTitle(xdata[xaxis]["label"])
       plots[plname].SetYTitle("Total activity (Bq)")
       for adat in jdata[key][isotype]:
           # a = adat[0]
           # z = adat[1]
           xvalue = adat[xdata[xaxis]["index"]]
           nb = adat[ipiso]
           # xv = float(z)*5.0 + float(ind-1)
           xv = float(xvalue) + 0.2*float(ind-1) + 0.02
           if nb > 0.0 :
              plots[plname].Fill(xv, float(nb))

       if ind == 1:
           plots[plname].Draw("HIST")    
       else:
           plots[plname].Draw("HISTSAME")

       plots[plname].Write()

    figdir="figs%s" % isotype
    if not os.path.exists(figdir):
       os.mkdir(figdir)

    cv.Print("%s/%s%s-%s-fort%d.png" % (figdir, xaxis, isotype, thick, int(fu)))

# ########################################################
def do_plot(jdata, data_units, data_name):
    ''' Create figures of active atoms '''

    rf = ROOT.TFile("feplot-isopote.root","recreate")
  
  
    jconv = {}
      
    # for fus in range(30, 37) + range(38, 42) :
    for fus in data_units:
        fu = str(fus)
        print jdata.keys()
        # print jdata[fu].keys()
        for k,v in jdata[fu].iteritems():
           key="f%d-dn%d" % ( int(fu), int(k) )
           print key+" "+v["detname"]
           jconv[key]={"isomers": v["isomers"], "isotopes": v["isotopes"], "detname":v["detname"] }
  
        # mk_plots_isotopes(jconv, data_name, fu, rf)
        mk_plots_isotopes(jconv, data_name, fu, rf, xaxis="A")

    rf.Close()


##########################################################
if __name__ == "__main__":

    if os.path.exists("setting.py"):
       execfile("setting.py")

    dataname = "resnuclei_data"
    jdata = json.load(open("%s/%s.json" % ( dataname, dataname ) ))
    do_plot(jdata, _DATA_UNITS, dataname)

    # Print A and Z of active atoms

    jconv = {}
      
    # for fus in range(30, 37) + range(38, 42) :
    # print "###################################"
    resactive = "residual_activity.csv"
    fout=open(resactive,"w")

    # for fus in range(30, 33) + [50]:
    for fus in range(30, 52):
        fu = str(fus)
        # print jdata.keys()
        # print jdata[fu].keys()
        for k,v in jdata[fu].iteritems():
           key="f%d-dn%d" % ( int(fu), int(k) )
           # print key+" "+v["detname"]
           jconv[key]={"isomers": v["isomers"], "isotopes": v["isotopes"], "detname":v["detname"] }
  
        # mk_plots_isotopes(jconv, thick, fu, rf)
        # mk_plots_isotopes(jconv, dataname, fu, rf, xaxis="A")

        get_hot_atoms(jconv, dataname, fu, fout, actmin = 1E9)
    
    fout.close()
    # rf.Close()

    os.system("column -s, -t -c 250 %s > %s" % (resactive, resactive.replace(".csv",".txt")))
    print "Results are written in %s and %s" % (resactive, resactive.replace(".csv",".txt"))

