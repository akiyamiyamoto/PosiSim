#!/bin/env python 
# Find volume of given region

import os
import json
import math

# ####################################
def getBodyData(body_file):

    data = {}
    for line in open(body_file):
        if line[0:1] == "*":
            continue
        whats = line.replace("\n","").split()
        gshape=whats[0]
        bname=whats[1]
        data[bname] = {"shape":gshape, "geom":whats[2:]}

        vol = calcVolumeRCC(data[bname]["geom"]) if gshape == "RCC" else 0.0
        data[bname]["volume"] = vol
  
    return data

# ####################################
def getRegionData(region_file):
    
    data={}
    lines=[]
    for line in open(region_file):
        # print line
        if line[0:1] == "*":
            continue
        if line[0:1] == " ":
            lines[-1] += line.replace("\n","")
        else:
            lines.append(line.replace("\n",""))

    for line in lines:
        whats=line.split()
        data[whats[0]] = whats[2:]

    return data

# ####################################
def calcVolumeRCC(body):
    #
    r = float(body[6])
    z = float(body[5])
    vol = math.pi * r * r * z

    return vol 

# ####################################
if __name__ == "__main__":

    #version="-v0603"
    execfile("version.py")
    version = _VERSION

    body_data=getBodyData("body%s.inc" % version)

    region_data=getRegionData("region%s.inc" % version)

    tregions=["TRDiskcp", "TRAxiscp", "TCOLIR4",
               "Tmskcp", "TFCcp", "RF1cp", "RF1solc", "RF2cp",
               "RF2solc", "RF3cp","RF3solc", "RF4cp", "RF4solc",
               "RF5solc", "RF5cp","RF6solc", "RF6cp", "RockW"]



    volregion = {}

    for tr in tregions:
        print ""
        print "# Region " + tr
        region_card=" ".join(region_data[tr])
        print "  region card="+region_card
        volregion[tr] = 0.0

        subregions = []
        if "|" not in region_card:
            subregions = [region_card]
        else:
            for sub in region_card.split("|"):
               sub2 = sub.replace("(","").replace(")","")
               print sub2
               if "rf" in sub2 and "cent" in sub2:
                   sub2 = " ".join(sub2.split()[0:2])
                   print "Special treatment (neglect) for RF*cent body" 
               if sub2 not in subregions:
                   subregions.append(sub2)
               else:
                   print "??? WARNING ??? zone " + sub + " duplicates. ?????????????????????"

        volsum = 0
        for isub in range(0, len(subregions)):
            print "### "+subregions[isub]+"  ##################"
            vols = subregions[isub].split()
            volnow = 0.0
            print vols
            if len(vols) == 0:
               bname = vols.replace("+")
               volsum += body_data[bname]["volume"]
               volnow += body_data[bname]["volume"]
               print body_data[bname]["shape"] + ":"+" ".join(body_data[bname]["geom"])+" Vol.="+str(olnow)
            else:               
               for v in vols:
                  bname=v[1:]
                  vol = body_data[bname]["volume"]
                  print v+" "+body_data[bname]["shape"]+":"+" ".join(body_data[bname]["geom"]) + " Vol.="+str(vol),
                  if v[0:1] == "+":
                     volsum += vol
                  elif v[0:1] == "-":
                     volsum -= vol
                  else:
                    print 
                    print "Undefined sign word v="+v
                  print "  volsum="+str(volsum)
               print "Volsum="+str(volsum)
        volregion[tr] = volsum 
        print "Region: "+tr+" Volume="+str(volregion[tr])+" cm^3"
        

        #subregions = " ".join(region_data[tr]).split("|")
        #for body in region_data[tr]:
        #    if body == "|": 
        #        continue
        #    bname=body.replace("+","").replace("-","").replace("|","")
        #    vol = body_data[bname]["volume"] if "volume" in body_data[bname] else 0.0
        #    print bname+":"+body_data[bname]["shape"]+":"+" ".join(body_data[bname]["geom"]) + " Volume="+str(vol)+"cm^3"
               
        
    json.dump(volregion,open("volregion%s.json" % version ,"w"))
    print "Volumes of selected region was dumped in volregion%s.json" % version
