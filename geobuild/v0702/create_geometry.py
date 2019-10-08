#!/bin/env python

import os
import json
import pprint

from FLUdata import *
from create_target import *

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
def crOneRFStructure(geo, fd, nrf, zbegin):
    ''' Create geometry of n'th RF structure '''

    _body=[]
    _region=[]
    _assignma = []
    
    gworld = geo["world"]
    glbal = geo["global"]
    grf = geo["RF"]

    # Create body, region, matterial data from outside to the inside.
    _body += ["* *************************************",
              "* Body data of %d-th RF Zone " % nrf, 
              "* *************************************"]
    _region += ["* *************************************",
              "* Region data of %d-th RF Zone " % nrf, 
              "* *************************************"]
    
    # #################################################

    # Solenoid, vacumme wall, etc.
    zcav = zbegin + grf["start_thick"]
    zlen = grf["deltaZ_per_cavity"]
    rcavin = grf["r_cavity_inner_wall"]
    zlen_rf_unit = grf["zlen_rf_unit"]

    zlen_rf = grf["start_thick"] + grf["deltaZ_per_cavity_structure"]*float(grf["Nb_cavity"])
    sol_rmax = grf["solenoid_outer_radius"]
    sol_rmin = sol_rmax - grf["solenoid_thickness"]
    sol_cp_rmax = sol_rmax - ( sol_rmax - sol_rmin - grf["solenoid_cooling_pipe_thickness"] ) * 0.5
    sol_cp_rmin = sol_cp_rmax - grf["solenoid_cooling_pipe_thickness"] 

    # print grf["solenoid_thickness"], grf["solenoid_cooling_pipe_thickness"] 
    # print sol_rmax, sol_rmin, sol_cp_rmax, sol_cp_rmin

    solout = "rf%dBsolo" % nrf 
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solout, zbegin, zlen_rf, sol_rmax ) )
    solcpo = "rf%dBscpo" % nrf 
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solcpo, zbegin, zlen_rf, sol_cp_rmax ) )
    solcpi = "rf%dBscpi" % nrf 
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solcpi, zbegin, zlen_rf, sol_cp_rmin ) )
    solin = "rf%dBsoli" % nrf 
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solin, zbegin, zlen_rf, sol_rmin ) )

    _region += ["*", "* **** Created by crOneRFStructure  nrf=%d ************************ " % nrf,
                "RF%dsolo 6 +rf%dBsolo -rf%dBscpo" % (nrf, nrf, nrf),
                "RF%dsolc 6 +rf%dBscpo -rf%dBscpi" % (nrf, nrf, nrf),
                "RF%dsoli 6 +rf%dBscpi -rf%dBsoli" % (nrf, nrf, nrf)]

    matdata = {"solo":"Copper", "solc":"WATER", "soli":"Copper"}
    for reg, mat in matdata.iteritems():
        regname = "RF%d%s" % (nrf, reg)
        _assignma += [ "ASSIGNMA %10s%10s" % (mat, regname)]

    # Beam pipe after RF structure
    vcthick = grf["vacuum_chamber_thick"]
    vc_len = zlen_rf_unit + vcthick if nrf == grf["Nb_structure"] else zlen_rf_unit

    vacname = "rf%dcvb" % nrf
    r_beam_pipe = grf["r_cavity_beam_pipe"]
    bp_len0 = zlen_rf_unit - zlen_rf + vcthick if nrf == grf["Nb_structure"] else zlen_rf_unit - zlen_rf
    bp_len = zlen_rf_unit - zlen_rf 

    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % (vacname, zbegin, vc_len, r_beam_pipe) )
    _body.append("RCC rf%dbpw 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin + zlen_rf, 
          bp_len0, r_beam_pipe + glbal["BPthick"] ) )                
    _region += [ "RF%dbpw 6 +rf%dbpw -rf%dcvb " % (nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "RF%dbpw" % nrf) ]

    # Vacuum chamber and surrounding vacuum
    _body.append("RCC rf%dvcho 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, vc_len, 
                  grf["vacuum_chamber_rmax"] ) )
    _body.append("RCC rf%dvchi 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, zlen_rf_unit, 
                  grf["vacuum_chamber_rmin"] ) )
    _region += [ "RF%dvch 6 +rf%dvcho -rf%dvchi" % (nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "RF%dvch" % nrf) ]
    if nrf == grf["Nb_structure"]:
        _region[-1] += " -rf%dbpw " % nrf

    # W mask at the end of RF structure
    mask_start_z = zbegin + zlen_rf_unit - grf["wmask_z_distance"] - grf["wmask_thick"]
    _body.append("RCC rf%dmsko 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, mask_start_z, 
                 grf["wmask_thick"], grf["wmask_rmax"]) )
    _body.append("RCC rf%dmski 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, mask_start_z, 
                 grf["wmask_thick"], grf["wmask_rmin"]))
    _region += [ "RF%dmsk 6 +rf%dmsko -rf%dmski " % (nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("WShield", "RF%dmsk" % nrf) ]

    # Return yoke out side of solenoid
    _body += ["RCC rf%dryo 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, vc_len,
                  grf["solenoid_outer_radius"] + grf["solenoid_return_yoke_thick"] ) ]
    _body += ["RCC rf%dryi 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, vc_len,
                  grf["solenoid_outer_radius"] )]
    _region += [ "RF%dyoke 6 +rf%dryo  -rf%dryi" % (nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "RF%dyoke" % nrf) ]

    # Air outside of vacuum chamber and shield beween solenoid
    _body.append("RCC rf%dairo 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + zlen_rf,
                vc_len - zlen_rf, sol_rmax) )

    gapfiller_zbgn = zlen_rf + grf["solenoid_gap_shield_z_gapsize"]
    gapfiller_zlen = grf["zlen_rf_unit"] - gapfiller_zbgn - grf["solenoid_gap_shield_z_gapsize"]

    _body.append("RCC rf%dsolsi 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + gapfiller_zbgn,
                gapfiller_zlen, sol_rmax - grf["solenoid_gap_shield_r_thickness"]) )
    _body.append("RCC rf%dsolso 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + gapfiller_zbgn,
                gapfiller_zlen, sol_rmax ) )

    _region += ["RF%dsols 6 +rf%dsolso -rf%dsolsi" % (nrf, nrf, nrf) ]
    _region += ["RF%dair 6 ( +rf%dBsoli -rf%dvcho ) " % (nrf, nrf, nrf) + " | +rf%dairo -rf%dvcho - (+rf%dsolso -rf%dsolsi) " % (nrf, nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("AIR", "RF%dair" % nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "RF%dsols" % nrf) ]
 

    ################################################################### 
    ## RF Structure it self
    ##  Structure is devided to front and back, to avoic FLUKA error, too many terms
    ################################################################### 

    cav_region = {"front":["+" + vacname], "back":["+" + vacname ]}
    pipe_region = {"front":[], "back":[]}
    cav_cp = grf["cavity_cooling_pipe"]

    # Water pipe inside the in-let of RF structure
    rf_rmax = grf["r_cavity_outer_wall"]
    cp_rmin = grf["cooling_pipe_rmin"]
    cp_rmax0 = grf["r_cavity_inner_wall"] + ( grf["r_cavity_outer_wall"] - grf["r_cavity_inner_wall"] -
                  grf["cavity_cooling_pipe_thickness"] ) * 0.5 
    cp_rmax1 = cp_rmax0 + grf["cavity_cooling_pipe_thickness"]
    cp_zbgn0 = zbegin + ( grf["start_thick"] - grf["cavity_cooling_pipe_thickness"] ) * 0.5
    if cav_cp:
        water_pipe_name_i = "rf%dcwi0" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_i, cp_zbgn0, 
                 grf["cavity_cooling_pipe_thickness"], cp_rmin ) )
        water_pipe_name_o = "rf%dcwo0" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_o, cp_zbgn0, 
                 grf["cavity_cooling_pipe_thickness"], cp_rmax0 ) )
        pipe_region["front"].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )
    # pipe_region["back"].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )

    zlen_cwx = zlen_rf - ( grf["start_thick"] - grf["cavity_cooling_pipe_thickness"] )
    if cav_cp:
        water_pipe_name_ix = "rf%dcwix" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_ix, cp_zbgn0, zlen_cwx, cp_rmax0 ) )
        water_pipe_name_ox = "rf%dcwox" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_ox, cp_zbgn0, zlen_cwx, cp_rmax1 ) ) 
        pipe_region["front"].append(" +%s -%s +rf%dcent" % ( water_pipe_name_ox, water_pipe_name_ix, nrf) )
        pipe_region["back"].append(" +%s -%s -rf%dcent" % ( water_pipe_name_ox, water_pipe_name_ix, nrf) )

    cp_zoffset = grf["deltaZ_per_cavity"] + ( grf["deltaZ_per_cavity_structure"] -
                 grf["deltaZ_per_cavity"] - grf["cavity_cooling_pipe_thickness"] ) *0.5   


    # Cavity structure
    centcav = 6
    fwdbck = "front"
    for nc in range(1, grf["Nb_cavity"]+1):
        if nc == centcav:
           centpln = "rf%dcent" % nrf
           _body.append("XYP %s %f " % ( centpln, zcav )) 
           fwdbck = "back"

        cavname="rf%dcav%d" % ( nrf, nc )
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( cavname, zcav, zlen, rcavin))
        cav_region[fwdbck].append("+" + cavname)           

        cp_zpos = zcav + cp_zoffset
        if cav_cp:
            water_pipe_name_i = "rf%dcwi%d" % ( nrf, nc )
            _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_i, cp_zpos, 
                     grf["cavity_cooling_pipe_thickness"], cp_rmin ) )
            water_pipe_name_o = "rf%dcwo%d" % ( nrf, nc )
            _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_o, cp_zpos, 
                     grf["cavity_cooling_pipe_thickness"], cp_rmax0 ))
            # if fwdbck == "front":
            pipe_region[fwdbck].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )


        zcav += grf["deltaZ_per_cavity_structure"]

    # Cavity and beam pipe vacuum
    vacreg = "RF%dvac" % nrf 
    vacregion = "%s 6 " % vacreg + " | ".join(cav_region["front"]+cav_region["back"])
    _region += join2FixedLength(vacregion.split())
    _assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", vacreg) ]

    # Cooling pipe in RF structure
    if cav_cp:
        cpreg = "RF%dcp" % nrf 
        cpregion = "%s 6 " % cpreg + " | ".join(pipe_region["front"] + pipe_region["back"])
        _region += join2FixedLength(cpregion.split())
        _assignma += [ "ASSIGNMA %10s%10s" % ("WATER", cpreg) ]
    
    centsign= {"front":"+", "back":"-"}
    # RF structure 
    rfstro = "rf%dstro" % nrf
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % (rfstro, zbegin, zlen_rf, rf_rmax))
    for fb in ["front", "back"]:
        rfstr = "RF%dstr%s" % (nrf, fb[0:1])
        rfstructure = "%s 6 +%s " % ( rfstr, rfstro ) +  " %srf%dcent " % (centsign[fb], nrf)
        for cav in cav_region[fb]:
            rfstructure += cav.replace("+"," -") 

        if cav_cp:
            for pipe in pipe_region[fb]:
                rfstructure += " - ( " + pipe + " )"
        
        _region += join2FixedLength(rfstructure.split())
        _assignma += [ "ASSIGNMA %10s%10s" % ("Copper", rfstr) ]

    # Vacuum out size of RF structure
    vac1 = "RF%dvaco 6 " % nrf 
    vac1 += " +rf%dvchi -rf%dstro -rf%dbpw " % (nrf, nrf, nrf) 
    vac1 += " - ( +rf%dmsko -rf%dmski ) " % (nrf, nrf) 
    _region += join2FixedLength(vac1.split())
    rfvac = "RF%dvaco" % nrf
    _assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", rfvac) ]
    
    zlast = zbegin + zlen_rf_unit

    fd.Add(_body, _region, _assignma)

    return zlast

# ========================================
def join2FixedLength(inlist, maxlength=120, nblanks=4, separator=" "):
    ''' 
    join list of strings to fixed length card format 
    output card length is limitted to maxlength
    insert nblanks of spaces to each card except first card
    output a new list 
    '''
    blank = ""
    if nblanks > 0:
       blc = [" "]*nblanks
       blank = "".join(blc)

    out = [inlist[0]+separator]
    for word in inlist[1:]:
       if len(out[-1]) + len(word) < maxlength-len(separator):
          out[-1] += word+separator
       else:
          out.append(blank + word +separator)

    return out

# ========================================
def crRFZone(geo, fd):
    ''' Create geometry of RF zone '''
 
    # global _body, _region, _assignma

    gworld = geo["world"]
    glbal = geo["global"]
    grf = geo["RF"]

    zbegin = gworld["zbound3"]
    nb_structure = grf["Nb_structure"]

    for nrf in range(1, nb_structure+1):
        zlast = crOneRFStructure(geo, fd, nrf, zbegin)
        zbegin = zlast     

    return

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
            

    # create  region data
    _region += ["*", "* black hole", 
       "BlHole  6 +blkRPP1 - ( zbound5 - zbound1 + rbound3 ) ",
       "RockW   6 +rbound3 -rbound2 +zbound5 -zbound1 "] 
    #   "*","* upstream zone ", 
    #   "Zone1 6 +zbound2 - zbound1 + rbound2 ",
    #   "*","* target zone", 
    #   "ZoneT 6 +zbound3 - zbound2 + rbound1"]
    #   "*","* rf zone", 
    #   "ZoneRF 6 +zbound4 - zbound3 + rbound1", 
    #   "*","* out side of target zone"] 
    #   "Zone2 6 +zbound3 - zbound2 + rbound2 - rbound1", 
    #   "*","* out side of RF zone", 
    #   "Zone3 6 +zbound4 - zbound3 + rbound2 - rbound1", 
    #   "*","* downstream zone", 
    #   "Zone4 6 +zbound5 - zbound4 + rbound2"] 

    # Assign material to each region
    _assignma += ["*","* Assign material ","*",
       "*********1*********2*********3*********4*********5*********6*********7*********8",
       "*","ASSIGNMA   BLCKHOLE  BlHole",
       "*","ASSIGNMA      WATER   RockW"]
    #   "*","ASSIGNMA     VACUUM    ZoneT     ZoneRF"]   
    #   "*","ASSIGNMA     VACUUM    Zone1      Zone4"]   

    fd.Add(_body, _region, _assignma)

    return

# ========================================
def crTunnelShield(geo, zone_no, fd):
    ''' Create regions of Concrete sheild for zone of given zone_no ( 1 to 4 ) '''
    
    # global _body, _region, _assignma

    zbound_min = "zbound%d" % zone_no
    zbound_max = "zbound%d" % (zone_no+1)
    region_name_pref = "zone%d" % zone_no
    rbound = {"a":["rbound2", "rcylout"], "b":["rcylout", "rcylmed"], 
              "c":["rcylmed", "rcylin"] }

    body = []
    region = []
    assignma = []
    for rn in ["a", "b", "c"]:
        region += ["*","* Concrete shield of tunnel for zone %d" % zone_no, 
                region_name_pref + rn +  " 6 +%s -%s +%s -%s" % ( zbound_max, zbound_min, rbound[rn][0], rbound[rn][1] )]

        material = "AIR" if rn == "b" else "CONCRETE"
        assignma += ["ASSIGNMA %10s%10s" % (material, region_name_pref+rn)]

    fd.Add(body, region, assignma)

# ========================================
def crZone1(geo, fd):

    # global _body, _region, _assignma

    

    zb2 = geo["front"]["CSh_up_pos"]
    zb1 = zb2 - geo["global"]["CSh_up_thick"]
    zb3 = zb2 + geo["global"]["FeSh_thick"]

    body = ["*  Body for Zone1",
         "XYP z1pln1 %f" % zb1, 
         "XYP z1pln2 %f" % zb2, 
         "XYP z1pln3 %f" % zb3 ]


    region = ["*", "* **** Created by crZone1 ************************ ",
                "*", "* Beam pipe",
                "BPvac1   6 +zbound2 -zbound1 +rcylbpin",
                "BPpipe1  6 +zbound2 -zbound1 +rcylbpou  -rcylbpin",
                "BPShld1  6 +zbound2 -z1pln3 +rcylbpso  -rcylbpou",
                "Z1upair  6 +z1pln1 -zbound1 +rcylin - rcylbpou", 
                "Z1CSh    6 +z1pln2 -z1pln1 +rcylin -rcylbpou", 
                "Z1FeSha  6 +z1pln3 -z1pln2 +rcylin -rcylbpou", 
                "Z1FeShb  6 +zbound2 -z1pln3 +rcylin -rcylfein", 
                "Z1dwnair 6 +zbound2 -z1pln3 +rcylfein -rcylbpso"]

    assignma = ["*", "* **** Created by crZone1 ************************ ",
                  "ASSIGNMA %10s%10s" % ("VACUUM", "BPvac1"), 
                  "ASSIGNMA %10s%10s" % ("STAINLES", "BPpipe1"), 
                  "ASSIGNMA %10s%10s" % ("WShield", "BPShld1"), 
 
                  "ASSIGNMA %10s%10s" % ("AIR", "Z1upair"), 
                  "ASSIGNMA %10s%10s" % ("CONCRETE", "Z1CSh"), 
                  "ASSIGNMA %10s%10s%10s" % ("CASTIRON", "Z1FeSha", "Z1FeShb"), 
                  "ASSIGNMA %10s%10s" % ("AIR", "Z1dwnair")] 

    fd.Add(body, region, assignma)

    crTunnelShield(geo, 1, fd)

    fd.Add([], ["***** End of crZone1 region. ****","*"],  ["**** End of crZone1 assignmat. ****", "*"] )

# ========================================
def crZone2(geo, fd):

    fd.AddRegion(["*", "* **** Created by crZone4 ************************ ",
                "*** zone2in 6 +zbound3 -zbound2 +rcylin - rbound1"])
    # fd.AddAssignmat(["ASSIGNMA %10s%10s" % ("AIR", "zone2in")])
    crTunnelShield(geo, 2, fd)

# ========================================
def crZone3(geo, fd):

    # fd.AddRegion(["*", "* **** Created by crZone4 ************************ ",
    #            "zone3in 6 +zbound4 -zbound3 +rcylin - rbound1"])
    # fd.AddAssignmat(["ASSIGNMA %10s%10s" % ("AIR", "zone3in")])

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

    fesh_zbgn = gworld["zbound3"]
    fesh_zlen = glbal["FeSh_zone3_z_length"]
    fesh_rmin = glbal["CShIn_rmin"] - glbal["FeSh_thick"]

    zb1 = gworld["zbound3"] + glbal["FeSh_zone3_z_length"]
    zb2 = zb1 + glbal["FeSh_thick"]
    zb3 = zb2 + glbal["CSh_down_thick"]


    body += [  "XYP z3inpln1 %f" % zb1,
               "XYP z3inpln2 %f" % zb2, 
               "XYP z3inpln3 %f" % zb3 ]

    # body += ["RCC z3air1o 0.0 0.0 %f 0.0 0.0 %f %f" % (fesh_zbgn, fesh_zlen, gworld["zbound3"], fesh_rmin) ]
#    body += ["RCC fesh1o 0.0 0.0 %f 0.0 0.0 %f %f " % (fesh_zbgn, fesh_zlen,  
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

    crTunnelShield(geo, 3, fd)

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

    crTunnelShield(geo, 4, fd)

    fd.AddRegion(["***** End of crZone4 region. ****","*"])
    fd.AddAssignmat( ["**** End of crZone4 assignmat. ****", "*"])


# ========================================
def crGeoInput(geo, fd):

    crWorld(geo, fd)

    crZone1(geo, fd)
    crZone2(geo, fd)
    crZone3(geo, fd)
    crZone4(geo, fd)

    crRFZone(geo, fd)

    crTargetZone(geo, fd)

