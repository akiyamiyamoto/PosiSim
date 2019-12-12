#!/bin/env python

import os
import json
import pprint
import sys

from FLUdata import *
from create_target import *
from create_cavity import *

# Since v0701, Z=0cm is the Target downstream surface.

# Fluka body data is described by free format 
# This is defined by a presence of COMBNAME in GEOBEGIN card.
# In free format, body is described by 
#    geometry code, 
#    identifier ( up to 8 characters with first charcter alphabetical )
#    a set of neumerical parameters. unit in cm.
# 
# Region card in free format
#    region name, up to 8 character, with first character alpfhabetical )
#    NAZ : a possible number of max regions
#    boolean zone expression 
#   132 character max



# ========================================
def crWorld(geo, fd):
    
    _body = []
    _region = []
    _assignma = []

    geop = geo["world"]
    glp = geo["global"]
    gtar = geo["Target"]

    zmax = geop["blkRPP1"]
    _body.append("ZCC blkRPP1 0.0 0.0 %f" % zmax )

    for iz in range(1, 6):
        bname = "zbound%d" % iz
        _body.append("XYP %s %f" % ( bname, geop[bname] ) )

    zlen = glp["zmax"] - glp["zmin"]
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rbound1", geop["rbound1"]))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rbound2", geop["rbound2"]))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rbound3", geop["rbound3"]))

    # Concrete sheild radius common to Zone1 to 4.
    rcylout=geop["rbound2"] - glp["CShOut_thick"]
    rcylmed=glp["CShIn_rmin"] + glp["CShIn_thick"]
    rcylfein = glp["CShIn_rmin"] - glp["FeSh_thick"]

    _body.append("ZCC %s 0.0 0.0 %f" % ( "rcylout",  rcylout))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rcylmed",  rcylmed))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rcylin",   glp["CShIn_rmin"]))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rcylfein", rcylfein))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpou", glp["BPrin"]+glp["BPthick"]))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpin", glp["BPrin"]))
    _body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpso", glp["BPrin"]+glp["BPthick"]+gtar["BP_shield_thickness"]))
            

    region = []
    assignma = []

    # create  region data
    _region += ["*", "* black hole", 
       "BlHole  6 +blkRPP1 - ( zbound5 - zbound1 + rbound3 ) ",
       "RockW   6 +rbound3 -rbound2 +zbound5 -zbound1 ", 
       "OutShld 6 +zbound5 -zbound1 +rbound2 -rcylout ", 
       "MidAir  6 +zbound5 -zbound1 +rcylout -rcylmed ",
       "InShld  6 +zbound5 -zbound1 +rcylmed -rcylin " ]

    # Assign material to each region
    _assignma += ["*","* Assign material ","*",
       "*********1*********2*********3*********4*********5*********6*********7*********8",
       "*","ASSIGNMA   BLCKHOLE  BlHole",
       "*","ASSIGNMA      WATER   RockW",
           "ASSIGNMA %10s%10s" % ("CONCRETE", "OutShld"), 
           "ASSIGNMA %10s%10s" % ("AIR", "MidAir"), 
           "ASSIGNMA %10s%10s" % ("CONCRETE", "InShld") ]

    fd.Add(_body, _region, _assignma)

    return

# ========================================
def crZone1(geo, fd):

    

    zb2 = geo["front"]["CSh_up_pos"]
    zb1 = zb2 - geo["global"]["CSh_up_thick"]
    zb3 = zb2 + geo["global"]["FeSh_thick"]

    body = ["*  Body for Zone1",
         "XYP z1pln1 %f" % zb1, 
         "XYP z1pln2 %f" % zb2] 
#         "XYP z1pln3 %f" % zb3 ]


    region = ["*", "* **** Created by crZone1 ************************ ",
                "*", "* Beam pipe",
                "BPvac1   6 +zbound2 -zbound1 +rcylbpin",
                "BPpipe1  6 +zbound2 -zbound1 +rcylbpou  -rcylbpin",
                "Z1upair  6 +z1pln1 -zbound1 +rcylin - rcylbpou", 
                "Z1CSh    6 +z1pln2 -z1pln1 +rcylin -rcylbpou",
                "Z1FeSha  6 +zbound2 -z1pln2 +rcylin -rcylbpou",]

    beamoff5 = "%30s%10s%20s" % ("","VACUUM","beamoff5")
    assignma = ["*", "* **** Created by crZone1 ************************ ",
                  "ASSIGNMA %10s%10s" % ("VACUUM", "BPvac1"), 
                  "ASSIGNMA %10s%10s" % ("STAINLES", "BPpipe1") + beamoff5, 
 
                  "ASSIGNMA %10s%10s" % ("AIR", "Z1upair"), 
                  "ASSIGNMA %10s%10s" % ("CONCRETE", "Z1CSh") + beamoff5,  
                  "ASSIGNMA %10s%10s" % ("CASTIRON", "Z1FeSha") + beamoff5 ] 

    fd.Add(body, region, assignma)

    fd.Add([], ["***** End of crZone1 region. ****","*"],  ["**** End of crZone1 assignmat. ****", "*"] )

# ========================================
def crZone3(geo, fd):

    body = []
    region = []
    assignma = []

    gworld = geo["world"]
    glbal = geo["global"]
    grf = geo["RF"]
    gtar = geo["Target"]

    # Create body, region, matterial data from outside to the inside.
    body += ["* *************************************",
              "* Body data of zone3in " ,
              "* *************************************"]
    region += ["* *************************************",
              "* Region data of zone3in " ,
              "* *************************************"]

    zb1 = gworld["zbound3"] + glbal["FeSh_zone3_z_length"]
    zb2 = zb1 + glbal["FeSh_thick"]
    zb3 = zb2 + glbal["CSh_down_thick"]


    body += [  "XYP z3inpln1 %f" % zb1,
               "XYP z3inpln2 %f" % zb2, 
               "XYP z3inpln3 %f" % zb3 ]

    region += ["Z3inAir1 6 +z3inpln1 -zbound3 +rcylfein -rbound1"]
    region += ["Z3inFeS1 6 +z3inpln1 -zbound3 +rcylin -rcylfein"]
    region += ["Z3inFeS2 6 +z3inpln2 -z3inpln1 +rcylin -rbound1"]
    region += ["Z3inCSh1 6 +z3inpln3 -z3inpln2 +rcylin -rbound1"]
    region += ["Z3inAir2 6 +zbound4 -z3inpln3 +rcylin -rbound1"]

    assignma += [ "ASSIGNMA %10s%10s" % ("AIR", "Z3inAir1") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("CASTIRON", "Z3inFeS1") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("CASTIRON", "Z3inFeS2") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("CONCRETE", "Z3inCSh1") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("AIR", "Z3inAir2") ]

    fd.Add(body, region, assignma)

# ========================================
def crZone4(geo, fd):

    global _body, _region, _assignma

    fd.AddRegion(["*", "* **** Created by crZone4 ************************ ",
                "*", "* Beam pipe",
                "BPvac4   6 +zbound5 -zbound4 +rcylbpin",
                "BPpipe4  6 +zbound5 -zbound4 +rcylbpou  -rcylbpin",
                "Z4air    6 +zbound5 -zbound4 +rcylin -rcylbpou"])

    fd.AddAssignmat(["*", "* **** Created by crZone1 ************************ ",
                  "ASSIGNMA %10s%10s" % ("VACUUM", "BPvac4"),
                  "ASSIGNMA %10s%10s" % ("STAINLES", "BPpipe4"),
                  "ASSIGNMA %10s%10s" % ("AIR", "Z4air")])

    fd.AddRegion(["***** End of crZone4 region. ****","*"])
    fd.AddAssignmat( ["**** End of crZone4 assignmat. ****", "*"])


# ========================================
def crGeoInput(geo, fd):

    crWorld(geo, fd)

    crZone1(geo, fd)
    crZone3(geo, fd)
    crZone4(geo, fd)

    

    crRFZone(geo, fd)

    crTargetZone(geo, fd)

