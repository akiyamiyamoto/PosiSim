

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

    #print(rcylmed2)
    #print(glp["CShIn_thick2"])

    rcylfein = glp["CShIn_rmin"] - glp["FeSh_thick"]

    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylout",  rcylout))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylairo",  rcylairo))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylmed2",  rcylmed2))

    body.append("ZCC %s 0.0 0.0 %f" % ( "rcyl1",   glp["CShIn_rmin"]))
    #body.append("ZCC %s 0.0 0.0 %f" % ( "rcyl2",  rcylmed2))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcyl3",  rcylmed))

    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylmed",  rcylmed))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylin",   glp["CShIn_rmin"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylfein", rcylfein))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpou", glp["BPrin"]+glp["BPthick"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpin", glp["BPrin"]))
    body.append("ZCC %s 0.0 0.0 %f" % ( "rcylbpso", glp["BPrin"]+glp["BPthick"]+gtar["BP_shield_thickness"]))
    body.append("YZP yzplane 0.0")
            

    region = []
    assignma = []

    # create  region data
    # create holes for wave guide, waterline, etc.
    rexclude = [""]*(geo["RF"]["Nb_structure"]+1)
    rexclgap = [""]*(geo["RF"]["Nb_structure"]+1)
    nbend = geo["Holes"]["wave_guides"]["nbend"]
    # if geo["Holes"]["mode"] == "up":
    for i in range(0, int(geo["RF"]["Nb_structure"]) + 1):
       #rexclude[i] = " -cbrc%d0 -wlrc%d0 " % ( i, i )
       #rexclgap[i] = " -cbrg%d0 " % i
       for ib in range(1, nbend + 1):
          rexclude[i] += " -wgrw%d%d -wgbw%d%d -wlrc%d%d -wlbc%d%d " % (i, ib, i, ib, i, ib, i, ib )
          rexclude[i] += " -cbrc%d%d -cbbc%d%d " % (i,ib, i, ib)
          rexclgap[i] += " -cbrg%d%d " % ( i, ib )

    rextar = " -vcrw0%d" % nbend
    for ib in range(1, nbend+1):
        rextar += " -vcrw0%d - vcbw0%d " % (ib, ib)

    region += ["*", "* black hole", 
       "BlHole  6 +blkRPP1 - ( zbound5 - zbound1 + rmaxall ) ",
       "MontRock 6 +rmaxall -rbound3 +zbound5 -zbound1 ", 
       "MidAir  6 +zbound5 -zbound1 +rcylout -rcylmed ",
       "OutShld 6 +zbound5 -zbound1 +rbound2 -rcylout ", 
       "InShld  6 +zbound5 -zbound1 +rcylmed -rcylin "+ " ".join(rexclude[1:]) + " ".join(rexclgap[1:]) ] 
    #    "MidAir  6 +zbound5 -zbound1 +rcylout -rcylmed2 ",
    # "InShldo 6 +zbound5 -zbound1 +rcylmed2 -rcylmed "  + " ".join(rexclude[1:]) + " ".join(rexclgap[1:]) , 

    # Assign material to each region
    assignma += ["*","* Assign material ","*",
       "*********1*********2*********3*********4*********5*********6*********7*********8",
       "*","ASSIGNMA   BLCKHOLE  BlHole",
       "*","ASSIGNMA %10s%10s" % ("ROCKMEAS", "MontRock"),
           "ASSIGNMA %10s%10s" % ("CONSHLD", "OutShld"), 
           "ASSIGNMA %10s%10s" % ("AIR", "MidAir"), 
           "ASSIGNMA %10s%10s" % ("CONCRETE", "InShld") ]
    #     "ASSIGNMA %10s%10s" % ("CONCRETE", "InShldo"), 

    if glp['Mount_water_thickness'] > 0.0:
       region += ["RockW  6 +rbound3 -rbound2 +zbound5 -zbound1 "]
       assignma += [ "*","ASSIGNMA %10s%10s" % ("WATER", "RockW") ]

    # Region and material for WaveGuide
    nbend = int( geo["Holes"]["wave_guides"]["nbend"] )
    if nbend >= 1:
       for irf in range(1, int(geo["RF"]["Nb_structure"])+1):
           for ib in range(1, nbend + 1):
               region += [ "WGRV%d%d 6 +wgrv%d%d +rcyl3 " % ( irf, ib , irf, ib),
                           "WGBV%d%d 6 +wgbv%d%d " % (irf, ib, irf, ib ),
                           "WGRW%d%d 6 +wgrw%d%d -wgrv%d%d -wgbv%d%d +rcyl3 " % (irf, ib, irf, ib, irf, ib, irf, ib),
                           "WGBW%d%d 6 +wgbw%d%d -wgbv%d%d -wgrv%d%d" % (irf, ib, irf, ib, irf, ib, irf, ib) ]
               if ib > 0 :
                  region[-1] += " -wgrv%d%d " % ( irf, ib-1 )
               assignma += [ "ASSIGNMA %10s%8s%d%d" % ( "VACUUM", "WGRV", irf, ib),
                             "ASSIGNMA %10s%8s%d%d" % ( "VACUUM", "WGBV", irf, ib),
                             "ASSIGNMA %10s%8s%d%d" % ( "Copper", "WGRW", irf, ib),
                             "ASSIGNMA %10s%8s%d%d" % ( "Copper", "WGBW", irf, ib) ]





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
             # "XYP cbsolzmx %f " % ( gcb["zcenter_solenoid"] + gcb["radius"]),
             "XYP cbsolzmx %f " % ( gcb["zcenter_solenoid"] - gcb["radius"]),
             "YZP cbsolxc %f " % gcb["xcenter_solenoid"], 
             "XYP cbgsolmx %f " % ( gcb["zcenter_solenoid"] + gcb["radius"] + gcb["gap"]),
             "ZCC cbgsol %f 0.0 %f" % ( gcb["xcenter_solenoid"], gcb["radius"] + gcb["gap"]), 
             "XCC cbsolz 0.0 %f %f" % ( gcb["zcenter_solenoid"], gcb["radius"] ),
             "XCC cbgsolz 0.0 %f %f" % ( gcb["zcenter_solenoid"], gcb["radius"] + gcb["gap"] )]

    gwl = geo["Holes"]["water_lines"]
    body += ["ZCC wlrot %f 0.0 %f" % ( gwl["xcenter_rotator"], gwl["radius_rotator"] ), 
             "ZCC wlfc %f 0.0 %f" % ( gwl["xcenter_FC"], gwl["radius_FC"] ), 
             "ZCC wlsol %f 0.0 %f" % ( gwl["xcenter_solenoid"], gwl["radius"] ), 
             # "XYP wlsolzmx %f " % ( gwl["zcenter_solenoid"] + gwl["radius"] ), 
             "XYP wlsolzmx %f " % ( gwl["zcenter_solenoid"] - gwl["radius"] ), 
             "YZP wlsolxc %f " % ( gwl["xcenter_solenoid"] ), 
             "XCC wlsolz 0.0 %f %f" % ( gwl["zcenter_solenoid"], gwl["radius"] )] 

    return body

# =========================================================================
def crBodies4Holes_up(geo):
    # create bodies for holes, for front side replace

    gwg = geo["Holes"]["wave_guides"]
    gcb = geo["Holes"]["cables"]
    gwl = geo["Holes"]["water_lines"]

    body = ["*** Bodies for wave guide holes"]
    zlen_rf_unit = geo["RF"]["zlen_rf_unit"]
    # Wave guide max

    # TODO Wave Guid no Ichi.

    #xminb = [ 0.0,  geo["world"]["rbound1"],
    #         geo["global"]["CShIn_rmin"] + geo["global"]["CShIn_thick"],
    #         geo["global"]["CShIn_rmin"] + geo["global"]["CShIn_thick"] ]
    xminb = [ 0.0,  gwg["xcenter"]-gwg["width"]*0.5-gwg["wall_thickness"],
             geo["global"]["CShIn_rmin"] + geo["global"]["CShIn_thick"],
             geo["global"]["CShIn_rmin"] + geo["global"]["CShIn_thick"] ]

    print(" xminb="+str(xminb))


    nbend = geo["Holes"]["wave_guides"]["nbend"]
    # Water lines
    # xminb の値を変更

    #wlrbound = [ geo["RF"]["solenoid_outer_radius"] - geo["RF"]["solenoid_thickness"],
    #           xminb[1]-gwg["width"] - 2*gwg["wall_thickness"],
    #           xminb[2]-gwg["width"] - 2*gwg["wall_thickness"],
    #           xminb[3] ]
    wlrbound = [ geo["RF"]["solenoid_outer_radius"] - geo["RF"]["solenoid_thickness"],
	       gwl["xcenter_solenoid"],
               xminb[2]-gwg["width"] - 2*gwg["wall_thickness"],
               xminb[3] ]

    print(" wlrbound="+str(wlrbound))

    wlrbound[nbend+1] = xminb[-1]

    for irf in range(1, geo["RF"]["Nb_structure"]+1):
        zcenter = geo["Holes"]["water_lines"]["zcenter_solenoid"] + zlen_rf_unit*float(irf-1)
        for ib in range(0, nbend+1):
            zcenterb = zcenter - gwl["radius"]
            zcenter += geo["Holes"]["wave_guides"]["zoffset"][ib]
            xcenter = wlrbound[ib]
            rlen = wlrbound[ib+1] - wlrbound[ib] 
            body += [ "RCC wlrc%d%d %f 0.0 %f %f 0.0 0.0 %f" % ( irf, ib, wlrbound[ib],
                      zcenter, rlen, gwl["radius"] ) ]
            if ib != 0:
               zlen = geo["Holes"]["wave_guides"]["zoffset"][ib] + 2*gwl["radius"]
               body += [ "RCC wlbc%d%d %f 0.0 %f 0.0 0.0 %f %f" % (irf, ib, wlrbound[ib],
                          zcenterb, zlen, gwl["radius"] )]

    cbrbound = [ geo["RF"]["solenoid_outer_radius"] - geo["RF"]["solenoid_thickness"],
                 wlrbound[1] - 2*gwl["radius"] - gcb["gap"],  wlrbound[2] - 2*gwl["radius"] - gcb["gap"], xminb[3] ]
#                 wlrbound[1] + 2*gwl["radius"] + gcb["gap"],  wlrbound[2] + 2*gwl["radius"] + gcb["gap"], xminb[3] ]
    cbrbound[nbend+1] = xminb[-1]

    # Cable and Water line... to be removed.
    for irf in range(1, geo["RF"]["Nb_structure"]+1):
        zcenter = geo["Holes"]["cables"]["zcenter_solenoid"] + zlen_rf_unit*float(irf-1)

        for ib in range(0, nbend+1):
            zcenterb = zcenter - gcb["radius"]
            zcenter += geo["Holes"]["wave_guides"]["zoffset"][ib]
            xcenter = cbrbound[ib]
            rlen = cbrbound[ib+1] - cbrbound[ib] + gcb["radius"]
            body += [ "RCC cbrc%d%d %f 0.0 %f %f 0.0 0.0 %f" % ( irf, ib, cbrbound[ib], zcenter, rlen, gcb["radius"] ) ]
            body += [ "RCC cbrg%d%d %f 0.0 %f %f 0.0 0.0 %f" % ( irf, ib, cbrbound[ib], zcenter, rlen, gcb["radius"] +
                    gcb["gap"] ) ]
            if ib != 0:
               zlen = geo["Holes"]["wave_guides"]["zoffset"][ib] + 2*gcb["radius"]
               body += [ "RCC cbbc%d%d %f 0.0 %f 0.0 0.0 %f %f" % (irf, ib, cbrbound[ib] + gcb["radius"],
                          zcenterb, zlen, gcb["radius"] )]

    # wave guide bodies
    for irf in range(1, geo["RF"]["Nb_structure"]+1):
        zcenter = geo["Holes"]["wave_guides"]["zcenter"] + zlen_rf_unit*float(irf-1)
        #  RPP name  Xmin Xmax, Ymin, Ymax, Zmin, Zmax
        xmaxv = xminb[-1] if geo["Holes"]["wave_guides"]["nbend"] == 0 else xminb[1] + gwg["wall_thickness"]
        xmaxw = xminb[-1] if geo["Holes"]["wave_guides"]["nbend"] == 0 else xminb[1]

        body += ["RPP wgrv%d0 0.0  %f %f %f %f %f " % ( irf, xmaxv ,
                  -gwg["height"]*0.5 , gwg["height"]*0.5 ,
                  zcenter - gwg["width"]*0.5, zcenter + gwg["width"]*0.5 ),
                 "RPP wgrw%d0 0.0  %f %f %f %f %f " % ( irf, xmaxw, -gwg["height"]*0.5 - gwg["wall_thickness"],
                  gwg["height"]*0.5 + gwg["wall_thickness"],
                  zcenter - gwg["width"]*0.5 - gwg["wall_thickness"],
                  zcenter + gwg["width"]*0.5 + gwg["wall_thickness"]) ]


        zcenterb = zcenter
        for ib in range(1, nbend + 1):
            wallth = gwg["wall_thickness"]
            xming = xminb[ib]
            xmaxg = xminb[ib+1] if ib != nbend else xminb[-1]
            xmin1 = xming + wallth
            xmax1 = xmaxg if ib == nbend else xmaxg + wallth
            zcenterb += gwg["zoffset"][ib]
            # radial direction part of wave guide.
            body += ["RPP wgrv%d%d %f %f %f %f %f %f " % ( irf, ib, xmin1, xmax1,
                     -gwg["height"]*0.5, gwg["height"]*0.5,
                     zcenterb - gwg["width"]*0.5, zcenterb + gwg["width"]*0.5 ),

                     "RPP wgrw%d%d %f  %f %f %f %f %f " % ( irf, ib, xming, xmaxg,
                 -gwg["height"]*0.5 - wallth, gwg["height"]*0.5 + wallth,
                     zcenterb - gwg["width"]*0.5 - wallth,
                     zcenterb + gwg["width"]*0.5 + wallth)]
            # beam direction part of wave guide
            body += ["RPP wgbv%d%d %f %f %f %f %f %f " % ( irf, ib, xmin1, xmin1 + gwg["width"],
                     -gwg["height"]*0.5, gwg["height"]*0.5,
                     zcenterb -gwg["zoffset"][ib] - gwg["width"]*0.5, zcenterb - gwg["width"]*0.5 ),

                     "RPP wgbw%d%d %f  %f %f %f %f %f " % ( irf, ib, xmin1 - wallth, xmin1 + gwg["width"] + wallth,
                     -gwg["height"]*0.5 - wallth, gwg["height"]*0.5 + wallth,
                     zcenterb - gwg["zoffset"][ib] - gwg["width"]*0.5 - wallth,
                     zcenterb - gwg["width"]*0.5 - wallth)]


    # Vacuum pipes in target area
    r_tvcri = geo["Target"]["vacuum_chamber_R_r_max"] - geo["RF"]["vacuum_chamber_thick"] + \
              geo["Target"]["Wdisk_axis_offset"] - 2.0
    r_tshro = geo["Target"]["vacuum_chamber_R_r_max"] + geo["Target"]["WShield_thickness"] + \
              geo["Target"]["Wdisk_axis_offset"]
    rbound = [r_tvcri, r_tshro, xminb[-2], xminb[-1] ]
    rbound[nbend+1] = rbound[-1]
    zcenters = geo["Holes"]["vacpipe"]["zcenters"]
    vcrad = geo["Holes"]["vacpipe"]["radius"]
    vwrad = vcrad + geo["Holes"]["vacpipe"]["wall_thickness"]
    for ib in range(0, nbend+1):
        zcenter = zcenters[ib]
        xcenter = cbrbound[ib]
        rlen = rbound[ib+1] - rbound[ib] + vwrad
        body += [ "RCC vcrc0%d %f 0.0 %f %f 0.0 0.0 %f" % ( ib, rbound[ib] + geo["Holes"]["vacpipe"]["wall_thickness"], zcenter, rlen, vcrad ) ]
        body += [ "RCC vcrw0%d %f 0.0 %f %f 0.0 0.0 %f" % ( ib, rbound[ib], zcenter, rlen, vwrad ) ]
        if ib != 0:
           zlen = geo["Holes"]["vacpipe"]["zcenters"][ib-1] - geo["Holes"]["vacpipe"]["zcenters"][ib]
           body += [ "RCC vcbc0%d %f 0.0 %f 0.0 0.0 %f %f" % (ib, rbound[ib] + vwrad,
                      zcenter-vcrad, zlen + 2*vcrad, vcrad )]
           body += [ "RCC vcbw0%d %f 0.0 %f 0.0 0.0 %f %f" % (ib, rbound[ib] + vwrad,
                      zcenter-vwrad, zlen + 2*vwrad, vwrad )]

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
    body += crBodies4Holes_up(geo)

    #region_wg = " +wgxup -wgxdn +wgxsdp -wgxsdm "
    region_wgw = " +wgxwup -wgxwdn +wgxwsdp -wgxwsdm "
    #region_cbwl = " -cbgrot -cbgfc -cbsol -cbgsol -wlsol -wlfc -wlrot "
    region_wg = " "
    # region_wgw = " "
    region_cbwl = " -cbgrot -cbgfc -wlfc -wlrot "

    region = ["*", "* **** Created by crZone1 ************************ ",
                "*", "* Beam pipe",
                "BPvac1   6 +zbound2 -zbound1 +rcylbpin",
                "BPpipe1  6 +zbound2 -zbound1 +rcylbpou  -rcylbpin",
                "Z1upair  6 +z1pln1 -z1cs0end +rcylin - rcylbpou", 
                "Z1upair0 6 +z1cs0bgn -zbound1 +rcylin - rcylbpou", 
                "Z1CSh    6 +z1pln2 -z1pln1 +rcylin -rcylbpou %s " % (region_cbwl),
                "Z1FeSha  6 +zbound2 -z1pln2 +rcylin -rcylbpou %s " % (region_cbwl),
                # "Z1CSh    6 +z1pln2 -z1pln1 +rcylin -rcylbpou %s -(%s)" % (region_cbwl, region_wgw),
                # "Z1FeSha  6 +zbound2 -z1pln2 +rcylin -rcylbpou %s -(%s)" % (region_cbwl, region_wgw),
                "Z1CSh0   6 +z1cs0end -z1cs0bgn +rcylin -rcylbpou",
                #"WaveG1   6 +zbound2 -z1pln1 %s " % region_wg, 
                #"WaveGW1  6 +zbound2 -z1pln1 %s -( %s )" % (region_wgw, region_wg ), 
                "CBFC1   6 +zbound2 -z1pln1 +cbfc",
                "CBgFC1  6 +zbound2 -z1pln1 +cbgfc -cbfc", 
                #"CBsol1   6 +zbound2 -z1pln1 +cbsol",
                #"CBgsol1  6 +zbound2 -z1pln1 +cbgsol -cbsol",
                "CBrot1   6 +zbound2 -z1pln1 +cbrot",
                "CBgrot1  6 +zbound2 -z1pln1 +cbgrot -cbrot",
                "WLrot1   6 +zbound2 -z1pln1 +wlrot", 
                "WLFC1   6 +zbound2 -z1pln1 +wlfc"]
                #"WLsol1   6 +zbound2 -z1pln1 +wlsol"] 

    beamoff5 = "%30s%10s%20s" % ("","VACUUM","beamoff5")
    assignma = ["*", "* **** Created by crZone1 ************************ ",
                  "ASSIGNMA %10s%10s" % ("VACUUM", "BPvac1"), 
                  "ASSIGNMA %10s%10s" % ("STAINLES", "BPpipe1") + beamoff5, 
 
                  "ASSIGNMA %10s%10s" % ("AIR", "Z1upair"), 
                  "ASSIGNMA %10s%10s" % ("AIR", "Z1upair0"), 
                  "ASSIGNMA %10s%10s" % ("CONCRETE", "Z1CSh") + beamoff5,  
                  "ASSIGNMA %10s%10s" % ("CONCRETE", "Z1CSh0") ,  
                  "ASSIGNMA %10s%10s" % ("CASTIRON", "Z1FeSha") + beamoff5,  
                  #"ASSIGNMA %10s%10s" % ("VACUUM", "WaveG1") + beamoff5,
                  #"ASSIGNMA %10s%10s" % ("Copper", "WaveGW1") + beamoff5, 
                  "ASSIGNMA %10s%10s" % ("AIR", "CBgFC1") + beamoff5,
                  "ASSIGNMA %10s%10s" % ("Copper", "CBFC1") + beamoff5,
                  #"ASSIGNMA %10s%10s" % ("AIR", "CBgsol1") + beamoff5,
                  #"ASSIGNMA %10s%10s" % ("Copper", "CBsol1") + beamoff5,
                  "ASSIGNMA %10s%10s" % ("AIR", "CBgrot1") + beamoff5,
                  "ASSIGNMA %10s%10s" % ("Copper", "CBrot1") + beamoff5, 
                  "ASSIGNMA %10s%10s" % ("WATER", "WLrot1") + beamoff5, 
                  "ASSIGNMA %10s%10s" % ("WATER", "WLFC1") + beamoff5]
                  #"ASSIGNMA %10s%10s" % ("WATER", "WLsol1") + beamoff5 ] 

    # Regions and materials for Cavity's WaveGuide, Water Line, Cables

    nbend = geo["Holes"]["wave_guides"]["nbend"]
    for irf in range(1, geo["RF"]["Nb_structure"]+1):
        bodies = " +wlrc%d0 " % irf
        for ib in range(1, geo["Holes"]["wave_guides"]["nbend"]+1):
            bodies += " | +wlrc%d%d | +wlbc%d%d " % (irf, ib, irf, ib )
        regname = "WLUP%d" % irf
        region += [ regname + " 6 +rcyl3 -r%dBscpo + ( " % irf + bodies + ")"]
        assignma += [ "ASSIGNMA %10s%10s" % ("WATER", regname) ]
 
        bodies = " +cbrc%d0 " % irf
        for ib in range(1, geo["Holes"]["wave_guides"]["nbend"]+1):
            bodies += " | +cbrc%d%d | +cbbc%d%d " % (irf, ib, irf, ib )
        regname = "CBUP%d" % irf
        region += [ regname + " 6 +rcyl3 -r%dBsolo + ( " % irf + bodies + ")"]
        assignma += [ "ASSIGNMA %10s%10s" % ("Copper", regname) ]
 
        # rlimit = [ " +rbound1 -r%dBsolo "% irf , " +rcyl1 -rcylin ", " +rcyl3 -rcyl2 " ]
        rlimit = [ " +rbound1 -r%dBsolo "% irf , " +rcyl3 -rcyl1 " ]
        #if nbend == 0 and irf == 1:
        #   rlimit[1] = " +rcyl1 -rcylfein "
 
        for ib0 in range(0, len(rlimit)):
           # ib = nbend if ib0 > nbend else ib0
           # region += [ "CBGUP%d%d 6 +cbrg%d%d -cbrc%d%d" % (irf, ib0, irf, ib, irf, ib) + rlimit[ib0] ]
           region += [ "CBGUP%d%d 6 +cbrg%d%d -cbrc%d%d" % (irf, ib0, irf, ib0, irf, ib0) + rlimit[ib0] ]
           assignma += ["ASSIGNMA %10s%10s" % ("AIR", "CBGUP%d%d"%(irf,ib0)) ]

        #ib0 = 1
        #region += [ "CBGUP%d%d 6 +cbrg%d%d -cbrc%d%d" % (irf, ib0, irf, ib, irf, ib) + " +rcyl3 -rcyl1" ]
        #assignma += ["ASSIGNMA %10s%10s" % ("AIR", "CBGUP%d%d"%(irf,ib0)) ]

 


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

    zb0 = geo["Holes"]["wave_guides"]["zend"]
    zb1 = gworld["zbound3"] + glbal["FeSh_zone3_z_length"]
    zb2 = zb1 + glbal["FeSh_thick"]
    zb3 = zb2 + glbal["CSh_down_thick"]
    

    body += [  "XYP z3inpln0 %f" % zb0, 
               "XYP z3inpln1 %f" % zb1,
               "XYP z3inpln2 %f" % zb2, 
               "XYP z3inpln3 %f" % zb3 ]

    region_wgw = " +wgxwup -wgxwdn +wgxwsdp -wgxwsdm +z3inpln0 "
    exclwg =   " -( +wgzwup -wgzwdn +wgzwsdp -wgzwsdm +wgxwup -yzplane ) "
    # exclude = " -(+wlsolz +wlsolxc -yzplane ) -(+wlsol -wlsolzmx +z3inpln0 ) -(+cbsolz +cbsolxc -yzplane) -(+cbsol - cbsolzmx +z3inpln0 ) "
    # exclude += " -(-wgzwdn %s ) " % region_wgw + exclwg
    # exclude = " -(+wlsolz +wlsolxc -yzplane ) -(+wlsol -wlsolzmx ) -(+cbsolz +cbsolxc -yzplane) -(+cbsol - cbsolzmx ) "
    exclude = ""

    rexclude = [""]*(geo["RF"]["Nb_structure"]+1)
    for i in range(0, int(geo["RF"]["Nb_structure"])+1):
      rexclude[i] = " -cbrc%d0 -wlrc%d0 " % (i, i)
      for ib in range(1, int(geo["Holes"]["wave_guides"]["nbend"])+1):
         rexclude[i] += " -wgrw%d%d -wgbw%d%d -wgrw%d%d" % (i, ib, i, ib, i, ib-1)
         rexclude[i] += " -wlrc%d%d -wlbc%d%d " % (i, ib, i, ib)
         rexclude[i] += " -cbrc%d%d -cbbc%d%d " % (i, ib, i, ib)

    if int(geo["Holes"]["wave_guides"]["nbend"]) == 0:
      for i in range(1, int(geo["RF"]["Nb_structure"])+1):
         rexclude[i] += " -wgrw%d0 " % i

    region += ["Z3inAir1 6 +z3inpln1 -zbound3 +rcylfein -rbound1 "] 
    region += ["Z3inFeS1 6 +z3inpln1 -zbound3 +rcylin -rcylfein"]
    region += ["Z3inFeS2 6 +z3inpln2 -z3inpln1 +rcylin -rbound1"]
    region += ["Z3inCSh1 6 +z3inpln3 -z3inpln2 +rcylin -rbound1"]
#     region += ["Z3inAir2 6 +zbound4 -z3inpln3 +rcylin -rbound1" + exclude + " ".join(rexclude[2:]) ]
    region += ["Z3inAir2 6 +zbound4 -z3inpln3 +rcylin -rbound1" + exclude + " ".join(rexclude[1:]) ]

#    region += ["Z3inAir1 6 +z3inpln1 -zbound3 +rcylfein -rbound1 " + rexclude[1] ]
#    region += ["Z3inFeS1 6 +z3inpln1 -zbound3 +rcylin -rcylfein" + rexclude[1] + " -cbrg10 " ]
#    region += ["Z3inAir2 6 +z3inpln4 -z3inpln3 +rcylin -rbound1" + rexclude[2]]
#    region += ["Z3inAir3 6 +zbound4 -z3inpln5 +rcylin -rbound1" + " ".join(rexclude[3:]) ]
#    region += ["Z3inCSh3 6 +z3inpln5 -z3inpln4 +rcylin -rbound1" ]

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
    crZone4(geo, fd)

    

    crRFZone(geo, fd)
    crZone3(geo, fd)

    crTargetZone(geo, fd)

