#!/bin/env python

import os
import json
import pprint
import sys

from FLUdata import *

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

    
    solout = "r%dBsolo" % nrf 
    solcpo = "r%dBscpo" % nrf 
    solcpi = "r%dBscpi" % nrf 
    solin = "r%dBsoli" % nrf 

    beamoff3 = ""
    beamoff4 = ""
    beamoff5 = ""

    zbegins = zbegin
    zlen_rfs = zlen_rf
    if nrf == 1:
        zbegins -= geo["bases"]["Collimator_thickness"]
        zlen_rfs += geo["bases"]["Collimator_thickness"]
        _body.append("RCC r1Bfrg 0.0 0.0 %f 0.0 0.0 %f %f" % (zbegins, grf["collimator_frange_thickness"],
                     grf["vacuum_chamber_rmin"] +grf["vacuum_chamber_thick"] ) )
        beamoff3 = "%30s%10s%20s" % ("","VACUUM","beamoff3")
        beamoff4 = "%30s%10s%20s" % ("","VACUUM","beamoff4")
        beamoff5 = "%30s%10s%20s" % ("","VACUUM","beamoff5")

         
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solout, zbegins, zlen_rfs, sol_rmax ) )
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solcpo, zbegins, zlen_rfs, sol_cp_rmax ) )
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solcpi, zbegins, zlen_rfs, sol_cp_rmin ) )
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solin, zbegins, zlen_rfs, sol_rmin ) )

    _region += ["*", "* **** Created by crOneRFStructure  nrf=%d ************************ " % nrf,
                "R%dsolo 6 +r%dBsolo -r%dBscpo" % (nrf, nrf, nrf),
                "R%dsolc 6 +r%dBscpo -r%dBscpi" % (nrf, nrf, nrf),
                "R%dsoli 6 +r%dBscpi -r%dBsoli" % (nrf, nrf, nrf)]

    matdata = {"solo":"Copper", "solc":"WATER", "soli":"Copper"}
    if sys.version_info.major == 2:
        for reg, mat in matdata.iteritems():
            regname = "R%d%s" % (nrf, reg)
            _assignma += [ "ASSIGNMA %10s%10s" % (mat, regname) + beamoff4 ]
    else:
        for reg, mat in list(matdata.items()):
            regname = "R%d%s" % (nrf, reg)
            _assignma += [ "ASSIGNMA %10s%10s" % (mat, regname) + beamoff3 ]

    # Beam pipe after RF structure
    vcthick = grf["vacuum_chamber_thick"]
    vc_len = zlen_rf_unit + vcthick if nrf == grf["Nb_structure"] else zlen_rf_unit
    yoke_len = vc_len + geo["bases"]["Collimator_thickness"] if nrf == 1 else vc_len

    vacname = "r%dcvb" % nrf
    r_beam_pipe = grf["r_cavity_beam_pipe"]
    bp_len0 = zlen_rf_unit - zlen_rf + vcthick if nrf == grf["Nb_structure"] else zlen_rf_unit - zlen_rf
    bp_len = zlen_rf_unit - zlen_rf 

    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % (vacname, zbegin, vc_len, r_beam_pipe) )
    _body.append("RCC r%dbpw 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin + zlen_rf, 
          bp_len0, r_beam_pipe + glbal["BPthick"] ) )                
    _region += [ "R%dbpw 6 +r%dbpw -r%dcvb " % (nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dbpw" % nrf)  + beamoff3 ]

    # Vacuum chamber and surrounding vacuum
    _body.append("RCC r%dvcho 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, vc_len, 
                  grf["vacuum_chamber_rmax"] ) )
    _body.append("RCC r%dvchi 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, zlen_rf_unit, 
                  grf["vacuum_chamber_rmin"] ) )

    # Frange for pilo seal, placed at the end of RF cavity
    bpfrange_zbgn = zbegin + zlen_rf + grf["BPfrange_z_distance_from_cavity"]
    bp_frange_rmax = r_beam_pipe + glbal["BPthick"] + grf["BPfrange_r_width"]
    _body += ["RCC r%dbpfr1 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, bpfrange_zbgn, 
                      grf["BPfrange_thickness"], bp_frange_rmax) ]
    _body += ["RCC r%dbpfr2 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, 
                      bpfrange_zbgn+grf["BPfrange_thickness"]+grf["BPfrange_distance"], 
                      grf["BPfrange_thickness"], bp_frange_rmax) ]
    _region += ["R%dBPFr1 6 +r%dbpfr1 -r%dbpw" % (nrf, nrf, nrf) ]
    _region += ["R%dBPFr2 6 +r%dbpfr2 -r%dbpw" % (nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dBPFr1" % nrf) + beamoff3 ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dBPFr2" % nrf) + beamoff3 ]
 
    # Return yoke out side of solenoid
    _body += ["RCC r%dryo 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegins, yoke_len,
                  grf["solenoid_outer_radius"] + grf["solenoid_return_yoke_thick"] ) ]
    _body += ["RCC r%dryi 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegins, yoke_len,
                  grf["solenoid_outer_radius"] )]
    _region += [ "R%dyoke 6 +r%dryo  -r%dryi" % (nrf, nrf, nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dyoke" % nrf) + beamoff4 ]

    # Collimator mask for the first cavity
    if nrf == 1:
        zmsk_len = geo["bases"]["Collimator_thickness"]
        _body += ["RCC colmsko 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegins, zmsk_len, grf["Collimator_rmax"])]
        _body += ["RCC colmski 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegins, zmsk_len, grf["Collimator_rmin"])]
        _region += ["Colmsk 6 +colmsko -colmski "]
        _assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "Colmsk" ) + beamoff3 ]

    # Air outside of vacuum chamber and shield beween solenoid
    _body.append("RCC r%dairo 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + zlen_rf,
                vc_len - zlen_rf, sol_rmax) )

    gapfiller_zbgn = zlen_rf + grf["solenoid_gap_shield_z_gapsize"]
    gapfiller_zlen = grf["zlen_rf_unit"] - gapfiller_zbgn - grf["solenoid_gap_shield_z_gapsize"]

    _body.append("RCC r%dsolsi 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + gapfiller_zbgn,
                gapfiller_zlen, sol_rmax - grf["solenoid_gap_shield_r_thickness"]) )
    _body.append("RCC r%dsolso 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + gapfiller_zbgn,
                gapfiller_zlen, sol_rmax ) )

    _region += ["R%dsols 6 +r%dsolso -r%dsolsi" % (nrf, nrf, nrf) ]
    if nrf == 1:
       _region[-1] += " -colmsko "
       _region += ["Colvac 6 +colmski"]
       _assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "Colvac" ) ]
       _region += ["R%dair 6 " % nrf + 
                " +r%dairo -r%dbpw - (+r%dsolso -r%dsolsi) " % (nrf, nrf, nrf, nrf)  + 
                " -r%dbpfr1 -r%dbpfr2 " % (nrf, nrf ) + 
                " | ( +r1Bsoli -r1stro -r1Bfrg -colmsko ) "  ] 
       _region += ["R1frg 6 +r1Bfrg -colmsko"]
#       _assignma +=   [ "ASSIGNMA %10s%10s%40s%10s%10s" % ("STAINLES", "R1frg","","VACUUM","beamoff3") ]
       _assignma +=   [ "ASSIGNMA %10s%10s" % ("STAINLES", "R1frg") + beamoff3 ]
    else:
       _region += ["R%dair 6 " % nrf + 
                " +r%dairo -r%dbpw - (+r%dsolso -r%dsolsi) " % (nrf, nrf, nrf, nrf)  + 
                " -r%dbpfr1 -r%dbpfr2 " % (nrf, nrf ) + 
                " | ( +r%dBsoli -r%dstro ) " % (nrf, nrf) ] 


    _assignma += [ "ASSIGNMA %10s%10s" % ("AIR", "R%dair" % nrf) ]
    _assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "R%dsols" % nrf) + beamoff4 ]
 





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
        water_pipe_name_i = "r%dcwi0" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_i, cp_zbgn0, 
                 grf["cavity_cooling_pipe_thickness"], cp_rmin ) )
        water_pipe_name_o = "r%dcwo0" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_o, cp_zbgn0, 
                 grf["cavity_cooling_pipe_thickness"], cp_rmax0 ) )
        pipe_region["front"].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )
    # pipe_region["back"].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )

    zlen_cwx = zlen_rf - ( grf["start_thick"] - grf["cavity_cooling_pipe_thickness"] )
    if cav_cp:
        water_pipe_name_ix = "r%dcwix" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_ix, cp_zbgn0, zlen_cwx, cp_rmax0 ) )
        water_pipe_name_ox = "r%dcwox" % (nrf)
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_ox, cp_zbgn0, zlen_cwx, cp_rmax1 ) ) 
        pipe_region["front"].append(" +%s -%s +r%dcent" % ( water_pipe_name_ox, water_pipe_name_ix, nrf) )
        pipe_region["back"].append(" +%s -%s -r%dcent" % ( water_pipe_name_ox, water_pipe_name_ix, nrf) )

    cp_zoffset = grf["deltaZ_per_cavity"] + ( grf["deltaZ_per_cavity_structure"] -
                 grf["deltaZ_per_cavity"] - grf["cavity_cooling_pipe_thickness"] ) *0.5   


    # Cavity structure
    centcav = 6
    fwdbck = "front"
    for nc in range(1, grf["Nb_cavity"]+1):
        if nc == centcav:
           centpln = "r%dcent" % nrf
           _body.append("XYP %s %f " % ( centpln, zcav )) 
           fwdbck = "back"

        cavname="r%dcav%d" % ( nrf, nc )
        _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( cavname, zcav, zlen, rcavin))
        cav_region[fwdbck].append("+" + cavname)           

        cp_zpos = zcav + cp_zoffset
        if cav_cp:
            water_pipe_name_i = "r%dcwi%d" % ( nrf, nc )
            _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_i, cp_zpos, 
                     grf["cavity_cooling_pipe_thickness"], cp_rmin ) )
            water_pipe_name_o = "r%dcwo%d" % ( nrf, nc )
            _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_o, cp_zpos, 
                     grf["cavity_cooling_pipe_thickness"], cp_rmax0 ))
            # if fwdbck == "front":
            pipe_region[fwdbck].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )


        zcav += grf["deltaZ_per_cavity_structure"]

    # Cavity and beam pipe vacuum
    vacreg = "R%dvac" % nrf 
    vacregion = "%s 6 " % vacreg + " | ".join(cav_region["front"]+cav_region["back"])
    _region += join2FixedLength(vacregion.split())
    _assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", vacreg) ]

    # Cooling pipe in RF structure
    if cav_cp:
        cpreg = "R%dcp" % nrf 
        cpregion = "%s 6 " % cpreg + " | ".join(pipe_region["front"] + pipe_region["back"])
        _region += join2FixedLength(cpregion.split())
        _assignma += [ "ASSIGNMA %10s%10s" % ("WATER", cpreg) + beamoff3 ]
    
    centsign= {"front":"+", "back":"-"}
    # RF structure 
    rfstro = "r%dstro" % nrf
    _body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % (rfstro, zbegin, zlen_rf, rf_rmax))
    for fb in ["front", "back"]:
        rfstr = "R%dstr%s" % (nrf, fb[0:1])
        rfstructure = "%s 6 +%s " % ( rfstr, rfstro ) +  " %sr%dcent " % (centsign[fb], nrf)
        for cav in cav_region[fb]:
            rfstructure += cav.replace("+"," -") 

        if cav_cp:
            for pipe in pipe_region[fb]:
                rfstructure += " - ( " + pipe + " )"
        
        _region += join2FixedLength(rfstructure.split())
        _assignma += [ "ASSIGNMA %10s%10s" % ("Copper", rfstr) + beamoff3 ]

    # Vacuum out size of RF structure
    # vac1 = "R%dvaco 6 " % nrf 
    # vac1 += " +r%dvchi -r%dstro -r%dbpw " % (nrf, nrf, nrf) 
    # vac1 += " - ( +r%dmsko -r%dmski ) " % (nrf, nrf) 
    # _region += join2FixedLength(vac1.split())
    # rfvac = "R%dvaco" % nrf
    # _assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", rfvac) ]
    
    zlast = zbegin + zlen_rf_unit

    fd.Add(_body, _region, _assignma)

    return zlast


# ========================================
def crRFZone(geo, fd):
    ''' Create geometry of RF zone '''

    # global _body, _region, _assignma

    gworld = geo["world"]
    glbal = geo["global"]
    grf = geo["RF"]

    zbegin = grf["z_rf_begin"]
    nb_structure = grf["Nb_structure"]

    for nrf in range(1, nb_structure+1):
        zlast = crOneRFStructure(geo, fd, nrf, zbegin)
        zbegin = zlast

    return


