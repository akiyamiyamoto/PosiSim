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
    

    geop = geo["world"]
    glp = geo["global"]
    gtar = geo["Target"]

    body = []
    zmax = geop["blkRPP1"]
    body.append("ZCC blkRPP1 0.0 0.0 %f" % zmax )

    for iz in range(1, 6):
        bname = "zbound%d" % iz
        body.append("XYP %s %f" % ( bname, geop[bname] ) )

    rf1zend = geop["zbound3"]+geo["bases"]["Collimator_thickness"]+geo["G4Param"]["Kasokukan_one_unit_cho"]
    body.append("XYP %s %f" % ( "rf1zend", rf1zend) )

    zlen = glp["zmax"] - glp["zmin"]
    body.append("ZCC %s 0.0 0.0 %f" % ( "rbound1", geop["rbound1"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rbound2", geop["rbound2"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rbound3", geop["rbound3"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rmaxall", geop["rmax"]))

    # Concrete sheild radius common to Zone1 to 4.
    rcylout=geop["rbound2"] - glp["CWall_thick"]
    rcylmed=glp["CShIn_rmin"] + glp["CShIn_thick"]
    rcylmed2=rcylmed + glp["CShIn_thick2"]
    rcylairo=rcylmed2 + glp["SA_thick"]

    rcylfein = glp["CShIn_rmin"] - glp["FeSh_thick"]

    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylout",  rcylout))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylairo",  rcylairo))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylmed2",  rcylmed2))

    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylmed",  rcylmed))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylin",   glp["CShIn_rmin"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylfein", rcylfein))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpou", glp["BPrin"]+glp["BPthick"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpin", glp["BPrin"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpso", glp["BPrin"]+glp["BPthick"]+gtar["BP_shield_thickness"]))
    body.append("YZP yzplane 0.0")
            
    air_rmax = glp["CShIn_rmin"] - glp["FeSh_thick"]
    body.append("ZCC %s 0.0 0.0 %f" % ( "rfarmax", air_rmax ))

    region = []
    assignma = []

    # create  region data
    region += ["*", "* black hole", 
       "BlHole  6 +blkRPP1 - ( zbound5 - zbound1 + rmaxall ) "]
    #   "MontRock 6 +rmaxall -rbound3 +zbound5 -zbound1 ", 
    #   "OutShld 6 +zbound5 -zbound1 +rbound2 -rcylout ", 
    #   "MidAir  6 +zbound5 -zbound1 +rcylout -rcylmed2 ",
    #   "InShldo 6 +zbound5 -zbound1 +rcylmed2 -rcylmed ", 
    #   "InShld  6 +zbound5 -zbound1 +rcylmed -rcylin " ]

    # Assign material to each region
    assignma += ["*","* Assign material ","*",
       "*********1*********2*********3*********4*********5*********6*********7*********8",
       "*","ASSIGNMA   BLCKHOLE  BlHole"]
       # "*","ASSIGNMA %10s%10s" % ("ROCKMEAS", "MontRock"),
       #    "ASSIGNMA %10s%10s" % ("CONSHLD", "OutShld"), 
       #    "ASSIGNMA %10s%10s" % ("AIR", "MidAir"), 
       #    "ASSIGNMA %10s%10s" % ("CONCRETE", "InShldo"), 
       #    "ASSIGNMA %10s%10s" % ("CONCRETE", "InShld") ]

    #if glp['Mount_water_thickness'] > 0.0:
    #   region += ["RockW  6 +rbound3 -rbound2 +zbound5 -zbound1 "]
    #   assignma += [ "*","ASSIGNMA %10s%10s" % ("WATER", "RockW") ]

    fd.Add(body, region, assignma)

    return

# =========================================================================
def crBodies4Holes(geo):
    # create bodies for holes

    gwg = geo["Holes"]["wave_guides"]
    body = ["*** Bodies for wave guide holes",
            "YZP wgxup %f" % ( gwg["xcenter"] + gwg["width"]*0.5),
            "YZP wgxdn %f" % (gwg["xcenter"] - gwg["width"]*0.5),
            "YZP wgxwup %f" % (gwg["xcenter"] + gwg["width"]*0.5 + gwg["wall_thickness"]),
            "YZP wgxwdn %f" % (gwg["xcenter"] - gwg["width"]*0.5 - gwg["wall_thickness"]),
            "XZP wgxsdp %f" %  (gwg["height"]*0.5),
            "XZP wgxsdm %f" %  (-gwg["height"]*0.5),
            "XZP wgxwsdp %f" %  (gwg["height"]*0.5 + gwg["wall_thickness"]),
            "XZP wgxwsdm %f" % (-gwg["height"]*0.5 - gwg["wall_thickness"]),

            "XYP wgzup %f" % ( gwg["zcenter"] + gwg["width"]*0.5),
            "XYP wgzdn %f" % (gwg["zcenter"] - gwg["width"]*0.5),
            "XYP wgzwup %f" % (gwg["zcenter"] + gwg["width"]*0.5 + gwg["wall_thickness"]),
            "XYP wgzwdn %f" % (gwg["zcenter"] - gwg["width"]*0.5 - gwg["wall_thickness"]),
#            "XZP wgzsdp %f" %  (gwg["width"]*0.5),
#            "XZP wgzsdm %f" %  (-gwg["width"]*0.5),
#            "XZP wgzwsdp %f" %  (gwg["width"]*0.5 + gwg["wall_thickness"]),
#            "XZP wgzwsdm %f" % (-gwg["width"]*0.5 - gwg["wall_thickness"])]
            "XZP wgzsdp %f" %  (gwg["height"]*0.5),
            "XZP wgzsdm %f" %  (-gwg["height"]*0.5),
            "XZP wgzwsdp %f" %  (gwg["height"]*0.5 + gwg["wall_thickness"]),
            "XZP wgzwsdm %f" % (-gwg["height"]*0.5 - gwg["wall_thickness"])]

    gcb = geo["Holes"]["cables"]
    body += ["ZCC cbrot %f 0.0 %f" % ( gcb["xcenter_rotator"], gcb["radius"] ), 
             "ZCC cbgrot %f 0.0 %f" % ( gcb["xcenter_rotator"], gcb["radius"] + gcb["gap"] ), 
             "ZCC cbfc %f 0.0 %f" % ( gcb["xcenter_FC"], gcb["radius"] ), 
             "ZCC cbgfc %f 0.0 %f" % ( gcb["xcenter_FC"], gcb["radius"] + gcb["gap"] ), 
             "ZCC cbsol %f 0.0 %f" % ( gcb["xcenter_solenoid"], gcb["radius"] ), 
             "XYP cbsolzmx %f " % ( gcb["zcenter_solenoid"] + gcb["radius"]),
             "YZP cbsolxc %f " % gcb["xcenter_solenoid"], 
             "XYP cbgsolmx %f " % ( gcb["zcenter_solenoid"] + gcb["radius"] + gcb["gap"]),
             "ZCC cbgsol %f 0.0 %f" % ( gcb["xcenter_solenoid"], gcb["radius"] + gcb["gap"]), 
             "XCC cbsolz 0.0 %f %f" % ( gcb["zcenter_solenoid"], gcb["radius"] ),
             "XCC cbgsolz 0.0 %f %f" % ( gcb["zcenter_solenoid"], gcb["radius"] + gcb["gap"] )]

    gwl = geo["Holes"]["water_lines"]
    body += ["ZCC wlrot %f 0.0 %f" % ( gwl["xcenter_rotator"], gwl["radius_rotator"] ), 
             "ZCC wlfc %f 0.0 %f" % ( gwl["xcenter_FC"], gwl["radius_FC"] ), 
             "ZCC wlsol %f 0.0 %f" % ( gwl["xcenter_solenoid"], gwl["radius"] ), 
             "XYP wlsolzmx %f " % ( gwl["zcenter_solenoid"] + gwl["radius"] ), 
             "YZP wlsolxc %f " % ( gwl["xcenter_solenoid"] ), 
             "XCC wlsolz 0.0 %f %f" % ( gwl["zcenter_solenoid"], gwl["radius"] )] 

    return body

# ========================================
def crZone1(geo, fd):

    
    # Upstream shield parameter
    zb2 = geo["front"]["CSh_up_pos"] # Concrete shield Max Z (Z end ) = Iron shield Min Z (Z begin)
    zb1 = zb2 - geo["global"]["CSh_up_thick"] # Concrete shield Min Z (Z begin)
    zb3 = zb2 + geo["global"]["FeSh_thick_upstream"] # Iron shield Max Z (z end)
    z_cshup0_bgn = zb1 - geo["global"]["CSh_up_distance"]
    z_cshup0_end = z_cshup0_bgn - geo["global"]["CSh_up0_thick"]


    body = ["*  Body for Zone1",
         "XYP z1pln1 %f" % zb1,   #  
         "XYP z1pln2 %f" % zb2, 
         "XYP z1cs0bgn %f " % z_cshup0_end, 
         "XYP z1cs0end %f " % z_cshup0_bgn] 
#         "XYP z1pln3 %f" % zb3 ]

    body += crBodies4Holes(geo)

    region_wg = " +wgxup -wgxdn +wgxsdp -wgxsdm "
    region_wgw = " +wgxwup -wgxwdn +wgxwsdp -wgxwsdm "
    # region_cbwl = " -cbgrot -cbgfc -cbsol -cbgsol -wlsol -wlfc -wlrot "
    region_cbwl = " -cbgrot -cbgfc -wlfc -wlrot "

    region = ["*", "* **** Created by crZone1 ************************ ",
                "*", "* Beam pipe"]
    #            "BPvac1   6 +zbound2 -z1pln1 +rcylbpin",
    #            "BPpipe1  6 +zbound2 -z1pln1 +rcylbpou  -rcylbpin"]
    #            "Z1CSh    6 +z1pln2 -z1pln1 +rfarmax -rcylbpou %s -(%s)" % (region_cbwl, region_wgw),
    #            "Z1FeSha  6 +zbound2 -z1pln2 +rfarmax -rcylbpou %s -(%s)" % (region_cbwl, region_wgw),
    #            "Z1CSh    6 +z1pln2 -z1pln1 +rfarmax -rcylbpou %s " % (region_cbwl),
    #            "Z1FeSha  6 +zbound2 -z1pln2 +rfarmax -rcylbpou %s " % (region_cbwl),
    #            "CBrot1   6 +zbound2 -z1pln1 +cbrot",
    #            "CBgrot1  6 +zbound2 -z1pln1 +cbgrot -cbrot",
    #            "CBFC1   6 +zbound2 -z1pln1 +cbfc",
    #            "CBgFC1  6 +zbound2 -z1pln1 +cbgfc -cbfc", 
    #            "WLrot1   6 +zbound2 -z1pln1 +wlrot", 
    #            "WLFC1   6 +zbound2 -z1pln1 +wlfc"]
    
    #            "WaveG1   6 +zbound2 -z1pln1 %s " % region_wg, 
    #            "WaveGW1  6 +zbound2 -z1pln1 %s -( %s )" % (region_wgw, region_wg ), 
    #            "CBsol1   6 +zbound2 -z1pln1 +cbsol",
    #            "CBgsol1  6 +zbound2 -z1pln1 +cbgsol -cbsol",
    #            "WLsol1   6 +zbound2 -z1pln1 +wlsol"] 

    # beamoff5 = "%30s%10s%20s" % ("","VACUUM","beamoff5")
    beamoff5 = "%30s%10s%20s" % ("","","")
    assignma = ["*", "* **** Created by crZone1 ************************ "]
    #              "ASSIGNMA %10s%10s" % ("VACUUM", "BPvac1"), 
    #              "ASSIGNMA %10s%10s" % ("STAINLES", "BPpipe1") + beamoff5]
    #              "ASSIGNMA %10s%10s" % ("CONCRETE", "Z1CSh") + beamoff5,  
    #              "ASSIGNMA %10s%10s" % ("CASTIRON", "Z1FeSha") + beamoff5,  
    #              "ASSIGNMA %10s%10s" % ("AIR", "CBgFC1") + beamoff5,
    #              "ASSIGNMA %10s%10s" % ("Copper", "CBFC1") + beamoff5,
    #              "ASSIGNMA %10s%10s" % ("AIR", "CBgrot1") + beamoff5,
    #              "ASSIGNMA %10s%10s" % ("Copper", "CBrot1") + beamoff5, 
    #              "ASSIGNMA %10s%10s" % ("WATER", "WLrot1") + beamoff5, 
    #              "ASSIGNMA %10s%10s" % ("WATER", "WLFC1") + beamoff5]

    #              "ASSIGNMA %10s%10s" % ("VACUUM", "WaveG1") + beamoff5,
    #              "ASSIGNMA %10s%10s" % ("Copper", "WaveGW1") + beamoff5, 
    #              "ASSIGNMA %10s%10s" % ("AIR", "CBgsol1") + beamoff5,
    #              "ASSIGNMA %10s%10s" % ("Copper", "CBsol1") + beamoff5,
    #              "ASSIGNMA %10s%10s" % ("WATER", "WLsol1") + beamoff5 ] 

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

    region_wgw = " +wgxwup -wgxwdn +wgxwsdp -wgxwsdm "
    exclwg = " -( +wgzwup -wgzwdn +wgzwsdp -wgzwsdm +wgxwdn -yzplane ) "
    exclude = " -(+wlsolz +wlsolxc -yzplane) -(+wlsol +wlsolzmx) -(+cbsolz +cbsolxc -yzplane) -(+cbsol + cbsolzmx) "
    exclude += " -(+wgzwup %s ) " % region_wgw + exclwg
    region += ["Z3inAir1 6 +z3inpln1 -zbound3 +rcylfein -rbound1 " + exclude ] 
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
def crKyasuku(geo, fd):
    

    gc = geo["Cask"]

    body = ["XYP %s %f" % ("caskarup", gc["air_zup"]), 
             "XYP %s %f" % ("caskzup", gc["zup"]), 
             "XYP %s %f" % ("caskbhu", gc["bh_zup"]), 
             "XYP %s %f" % ("caskbhue", gc["bh_zup"] + gc["bh_size"]), 
             "XYP %s %f" % ("caskbhde", gc["bh_zdn"]), 
             "XYP %s %f" % ("caskzdn", gc["zdn"]), 
             "XYP %s %f" % ("caskardn", gc["air_zdn"]), 
             "XYP %s %f" % ("caskzmax", geo["bases"]["zmax"])] 
    body += ["ZCC %s 0.0 0.0 %f" % ("caskbhmn", gc["bh_rmin"]) ,
             "ZCC %s 0.0 0.0 %f" % ("caskrmin", gc["bh_rmax"]) ,
             "ZCC %s 0.0 0.0 %f" % ("caskrmax", gc["rmax"]), 
             "ZCC %s 0.0 0.0 %f" % ("caskarmx", gc["air_rmax"])] 

    region = ["* Cask", 
             "CaskBH 6 ( +caskrmin -caskbhu +caskbhue ) | ( +caskrmin +caskzdn -caskbhde ) | " + 
             " (-caskbhmn +caskrmin +caskbhde -caskbhue)  ", 
             "Cask 6 ( +caskrmax -caskzup +caskbhu ) | ( +caskrmax +caskardn -caskzdn ) | " + 
             " ( +caskrmax -caskrmin -caskbhu +caskzdn )  ", 
             "CaskAir 6 ( +caskarmx +caskzup -zbound1 ) | ( +caskarmx -caskardn +zbound5 ) | " + 
               "( +caskarmx -caskrmax -caskzup +caskardn )  "]


    # Assign material to each region
    # beamoffc = "%30s%10s%20s" % ("","VACUUM","")
    beamoffc = "%30s%10s%20s" % ("","AIR","")
    assignma = ["*","* Assign material to cask","*",
       "*********1*********2*********3*********4*********5*********6*********7*********8",
       "*","ASSIGNMA %10s%10s" % ("BLCKHOLE", "CaskBH") + beamoffc,
          "ASSIGNMA %10s%10s" % ("STAINLES", "Cask"),
          "ASSIGNMA %10s%10s" % ("AIR", "CaskAir")]
           

    fd.Add(body, region, assignma)


# ========================================
def crGeoKyasuku(geo, fd):

    crWorld(geo, fd)

    crZone1(geo, fd)
    # crZone4(geo, fd)

    ### TO BE ADDED crCassuku(geo, fd)

    

    #crRFZone(geo, fd)
    #crZone3(geo, fd)

    crTargetZone(geo, fd)


    # gworld = geo["world"]
    # glbal = geo["global"]

    # crRFHoles(geo, fd)

    grf = geo["RF"]
    zbegin = grf["z_rf_begin"]
    nb_structure = grf["Nb_structure"]

    #nrf=1
    #zlast = crOneRFStructure(geo, fd, nrf, zbegin)

    crKyasuku(geo, fd)

