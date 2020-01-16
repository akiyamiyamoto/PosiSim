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

    body=[]
    region=[]
    assignma = []
    
    gworld = geo["world"]
    glbal = geo["global"]
    grf = geo["RF"]

    # Create body, region, matterial data from outside to the inside.
    body += ["* *************************************",
              "* Body data of %d-th RF Zone " % nrf, 
              "* *************************************"]
    region += ["* *************************************",
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
        body.append("RCC r1Bfrg 0.0 0.0 %f 0.0 0.0 %f %f" % (zbegins, grf["collimator_frange_thickness"],
                     grf["vacuum_chamber_rmin"] +grf["vacuum_chamber_thick"] ) )
        beamoff3 = "%30s%10s%20s" % ("","VACUUM","beamoff3")
        beamoff4 = "%30s%10s%20s" % ("","VACUUM","beamoff4")
        beamoff5 = "%30s%10s%20s" % ("","VACUUM","beamoff5")

         
    body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solout, zbegins, zlen_rfs, sol_rmax ) )
    body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solcpo, zbegins, zlen_rfs, sol_cp_rmax ) )
    body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solcpi, zbegins, zlen_rfs, sol_cp_rmin ) )
    body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( solin, zbegins, zlen_rfs, sol_rmin ) )

    region += ["*", "* **** Created by crOneRFStructure  nrf=%d ************************ " % nrf ]
    exclwl = " -(+wlrc%d0 -yzplane) " % nrf
    exclcb = " -cbrg%d0 " % nrf
    exclwg = " -wgrw%d0  " % nrf
    
    region +=["R%dsolo 6 +r%dBsolo -r%dBscpo " % (nrf, nrf, nrf) + exclwl + exclwg,
                "R%dsolc 6 +r%dBscpo -r%dBscpi" % (nrf, nrf, nrf) + exclwg,
                "R%dsoli 6 +r%dBscpi -r%dBsoli" % (nrf, nrf, nrf) + exclwg ]

    matdata = {"solo":"Copper", "solc":"WATER", "soli":"Copper"}
    if sys.version_info.major == 2:
        for reg, mat in matdata.iteritems():
            regname = "R%d%s" % (nrf, reg)
            assignma += [ "ASSIGNMA %10s%10s" % (mat, regname) + beamoff4 ]
    else:
        for reg, mat in list(matdata.items()):
            regname = "R%d%s" % (nrf, reg)
            assignma += [ "ASSIGNMA %10s%10s" % (mat, regname) + beamoff3 ]

    # Beam pipe after RF structure
    vcthick = grf["vacuum_chamber_thick"]
    vc_len = zlen_rf_unit + vcthick if nrf == grf["Nb_structure"] else zlen_rf_unit
    yoke_len = vc_len + geo["bases"]["Collimator_thickness"] if nrf == 1 else vc_len

    vacname = "r%dcvb" % nrf
    r_beam_pipe = grf["r_cavity_beam_pipe"]
    bp_len0 = zlen_rf_unit - zlen_rf + vcthick if nrf == grf["Nb_structure"] else zlen_rf_unit - zlen_rf
    bp_len = zlen_rf_unit - zlen_rf 

    body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % (vacname, zbegin, vc_len, r_beam_pipe) )
    body.append("RCC r%dbpw 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin + zlen_rf, 
          bp_len0, r_beam_pipe + glbal["BPthick"] ) )                
    region += [ "R%dbpw 6 +r%dbpw -r%dcvb " % (nrf, nrf, nrf) ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dbpw" % nrf)  + beamoff3 ]

    # Vacuum chamber and surrounding vacuum
    body.append("RCC r%dvcho 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, vc_len, 
                  grf["vacuum_chamber_rmax"] ) )
    body.append("RCC r%dvchi 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegin, zlen_rf_unit, 
                  grf["vacuum_chamber_rmin"] ) )

    # Frange for pilo seal, placed at the end of RF cavity
    bpfrange_zbgn = zbegin + zlen_rf + grf["BPfrange_z_distance_from_cavity"]
    bp_frange_rmax = r_beam_pipe + glbal["BPthick"] + grf["BPfrange_r_width"]
    body += ["RCC r%dbpfr1 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, bpfrange_zbgn, 
                      grf["BPfrange_thickness"], bp_frange_rmax) ]
    body += ["RCC r%dbpfr2 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, 
                      bpfrange_zbgn+grf["BPfrange_thickness"]+grf["BPfrange_distance"], 
                      grf["BPfrange_thickness"], bp_frange_rmax) ]
    region += ["R%dBPFr1 6 +r%dbpfr1 -r%dbpw" % (nrf, nrf, nrf) ]
    region += ["R%dBPFr2 6 +r%dbpfr2 -r%dbpw" % (nrf, nrf, nrf) ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dBPFr1" % nrf) + beamoff3 ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dBPFr2" % nrf) + beamoff3 ]
 
    # Return yoke out side of solenoid
    body += ["RCC r%dryo 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegins, yoke_len,
                  grf["solenoid_outer_radius"] + grf["solenoid_return_yoke_thick"] ) ]
    body += ["RCC r%dryi 0.0 0.0 %f 0.0 0.0 %f %f" % (nrf, zbegins, yoke_len,
                  grf["solenoid_outer_radius"] )]
    region   += [ "R%dyoke 6 +r%dryo  -r%dryi " % (nrf, nrf, nrf) + exclwl  + exclcb + exclwg ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "R%dyoke" % nrf) + beamoff4 ]

    # Collimator mask for the first cavity
    if nrf == 1:
        zmsk_len = geo["bases"]["Collimator_thickness"]
        body += ["RCC colmsko 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegins, zmsk_len, grf["Collimator_rmax"])]
        body += ["RCC colmski 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegins, zmsk_len, grf["Collimator_rmin"])]
        region += ["Colmsk 6 +colmsko -colmski "]
        assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "Colmsk" ) + beamoff3 ]

    # Air outside of vacuum chamber and shield beween solenoid
    body.append("RCC r%dairo 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + zlen_rf,
                vc_len - zlen_rf, sol_rmax) )

    gapfiller_zbgn = zlen_rf + grf["solenoid_gap_shield_z_gapsize"]
    gapfiller_zlen = grf["zlen_rf_unit"] - gapfiller_zbgn - grf["solenoid_gap_shield_z_gapsize"]

    body.append("RCC r%dsolsi 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + gapfiller_zbgn,
                gapfiller_zlen, sol_rmax - grf["solenoid_gap_shield_r_thickness"]) )
    body.append("RCC r%dsolso 0.0 0.0 %f 0.0 0.0 %f %f" % ( nrf, zbegin + gapfiller_zbgn,
                gapfiller_zlen, sol_rmax ) )

    region += ["R%dsols 6 +r%dsolso -r%dsolsi" % (nrf, nrf, nrf) ]
    if nrf == 1:
       region[-1] += " -colmsko "
       region += ["Colvac 6 +colmski"]
       assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "Colvac" ) ]
       region += ["R%dair 6 " % nrf + 
                " +r%dairo -r%dbpw - (+r%dsolso -r%dsolsi) " % (nrf, nrf, nrf, nrf)  + 
                " -r%dbpfr1 -r%dbpfr2 " % (nrf, nrf ) + 
                " | ( +r1Bsoli -r1stro -r1Bfrg -colmsko %s ) " % exclwg   ] 
       region += ["R1frg 6 +r1Bfrg -colmsko"]
       assignma +=   [ "ASSIGNMA %10s%10s" % ("STAINLES", "R1frg") + beamoff3 ]

    else:
       region += ["R%dair 6 " % nrf + 
                " +r%dairo -r%dbpw - (+r%dsolso -r%dsolsi) " % (nrf, nrf, nrf, nrf)  + 
                " -r%dbpfr1 -r%dbpfr2 " % (nrf, nrf ) + 
                " | ( +r%dBsoli -r%dstro %s ) " % (nrf, nrf, exclwg ) ] 


    assignma += [ "ASSIGNMA %10s%10s" % ("AIR", "R%dair" % nrf) ]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "R%dsols" % nrf) + beamoff4 ]
 
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
        body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_i, cp_zbgn0, 
                 grf["cavity_cooling_pipe_thickness"], cp_rmin ) )
        water_pipe_name_o = "r%dcwo0" % (nrf)
        body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_o, cp_zbgn0, 
                 grf["cavity_cooling_pipe_thickness"], cp_rmax0 ) )
        pipe_region["front"].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )
    # pipe_region["back"].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )

    zlen_cwx = zlen_rf - ( grf["start_thick"] - grf["cavity_cooling_pipe_thickness"] )
    if cav_cp:
        water_pipe_name_ix = "r%dcwix" % (nrf)
        body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_ix, cp_zbgn0, zlen_cwx, cp_rmax0 ) )
        water_pipe_name_ox = "r%dcwox" % (nrf)
        body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_ox, cp_zbgn0, zlen_cwx, cp_rmax1 ) ) 
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
           body.append("XYP %s %f " % ( centpln, zcav )) 
           fwdbck = "back"

        cavname="r%dcav%d" % ( nrf, nc )
        body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( cavname, zcav, zlen, rcavin))
        cav_region[fwdbck].append("+" + cavname)           

        cp_zpos = zcav + cp_zoffset
        if cav_cp:
            water_pipe_name_i = "r%dcwi%d" % ( nrf, nc )
            body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_i, cp_zpos, 
                     grf["cavity_cooling_pipe_thickness"], cp_rmin ) )
            water_pipe_name_o = "r%dcwo%d" % ( nrf, nc )
            body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % ( water_pipe_name_o, cp_zpos, 
                     grf["cavity_cooling_pipe_thickness"], cp_rmax0 ))
            # if fwdbck == "front":
            pipe_region[fwdbck].append(" +%s -%s " % ( water_pipe_name_o, water_pipe_name_i) )


        zcav += grf["deltaZ_per_cavity_structure"]

    # Cavity and beam pipe vacuum
    vacreg = "R%dvac" % nrf 
    vacregion = "%s 6 " % vacreg + " | ".join(cav_region["front"]+cav_region["back"])
    region += join2FixedLength(vacregion.split())
    assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", vacreg) ]

    # Cooling pipe in RF structure
    if cav_cp:
        cpreg = "R%dcp" % nrf 
        cpregion = "%s 6 " % cpreg + " | ".join(pipe_region["front"] + pipe_region["back"])
        region += join2FixedLength(cpregion.split())
        assignma += [ "ASSIGNMA %10s%10s" % ("WATER", cpreg) + beamoff3 ]
    
    centsign= {"front":"+", "back":"-"}
    # RF structure 
    rfstro = "r%dstro" % nrf
    body.append("RCC %s 0.0 0.0 %f 0.0 0.0 %f %f" % (rfstro, zbegin, zlen_rf, rf_rmax))
    for fb in ["front", "back"]:
        rfstr = "R%dstr%s" % (nrf, fb[0:1])
        rfstructure = "%s 6 +%s " % ( rfstr, rfstro ) +  " %sr%dcent " % (centsign[fb], nrf)
        for cav in cav_region[fb]:
            rfstructure += cav.replace("+"," -") 

        if cav_cp:
            for pipe in pipe_region[fb]:
                rfstructure += " - ( " + pipe + " )"
        
        region += join2FixedLength(rfstructure.split())
        region[-1] += exclwg
        assignma += [ "ASSIGNMA %10s%10s" % ("Copper", rfstr) + beamoff3 ]

    zlast = zbegin + zlen_rf_unit

    fd.Add(body, region, assignma)

    return zlast

# =======================================
def crRFHoles(geo, fd, nrf):
    ''' 
    Create holes by wave guide, water lines, cable lines 
    '''
    # Waveguide, cable and water lines for solenoid and cavity
    region_wg = " +wgxup -wgxdn +wgxsdp -wgxsdm "
    region_wgw = " +wgxwup -wgxwdn +wgxwsdp -wgxwsdm "
    region_zwg = " +wgzup -wgzdn +wgzsdp -wgzsdm "
    region_zwgw = " +wgzwup -wgzwdn +wgzwsdp -wgzwsdm "
    region_cbwl = " -cbgsol -wlsol "
    exclg3 = " -( -wgzdn +wgxup )"
    exclg3w = " -( -wgzwdn +wgxup )"
    exclg3z= " -( wgxsdp -wgxsdm +wgzdn -wgzwdn +wgxup -wgxdn ) "

    body = ["* Holes in cavity region " ]
    region = ["* Holes in cavity region "]
    assignma = ["* Holes in cavity region" ] 
    beamoff4 = "%30s%10s%20s" % ("","VACUUM","beamoff4")

    if geo["Holes"]["mode"] == "front":
        if nrf == 1:
            region += [ "WaveG3   6 -zbound3 +wgzup  %s %s " % (region_wg,exclg3), 
                        "WaveGW3  6 -zbound3 +wgzwup  %s -( %s ) %s " % (region_wgw, region_wg, exclg3w ),
                        "CBsol3   6 -zbound3 +cbsolzmx +cbsol ",
                        "WLsol3   6 -zbound3 +wlsolzmx +wlsol "]
            assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "WaveG3") ,
                         "ASSIGNMA %10s%10s" % ("Copper", "WaveGW3") + beamoff4 ,
                         "ASSIGNMA %10s%10s" % ("Copper", "CBsol3") + beamoff4 ,
                         "ASSIGNMA %10s%10s" % ("WATER", "WLsol3") + beamoff4 ]
            region += ["WaveZG3   6 %s +wgxup -yzplane -r1cav6 -r1cav7 -r1cav8 -r1cvb " % region_zwg ,
                       "WaveZGW3  6  %s -( %s ) +wgxup -yzplane -r1cav6 -r1cav7 -r1cav8 -r1cvb %s " % (region_zwgw, region_zwg, exclg3z )]
            rmax_cbsol3z = " +cbsolz -cbsol +cbsolxc"
            rmax_wlsol3z = " +wlsolz -wlsol +wlsolxc "
            region +=  [ "CBs3z%d  6 %s -r%dBsolo -yzplane " % (nrf, rmax_cbsol3z2, nrf),
                         "CBgs3z%d  6 +cbgsolz%d +rbound1 -cbsolz%d -r%dBsolo -yzplane " % (nrf, nrf, nrf, nrf),
                         "WLs3z%d  6 %s -r%dBscpo -yzplane " % (nrf, rmax_wlsol3z2, nrf) ]
        
            assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "CBs3z%d" % nrf ) + beamoff4,
                          "ASSIGNMA %10s%10s" % ("AIR", "CBgs3z%d" % nrf ) + beamoff4,
                          "ASSIGNMA %10s%10s" % ("WATER", "WLs3z%d" % nrf ) + beamoff4 ]

    elif geo["Holes"]["mode"] == "up":
        rmax_cbsol3z2= " +cbrc%d0 +rcyl3 " % nrf
        rmax_wlsol3z2= " +wlrc%d0 +rcyl3 " % nrf
        region_zwg2 = " +wgrv%d0 " % nrf 
        region_zwgw2 = " +wgrw%d0 " % nrf
        exclcav = " -r%dcav6 -r%dcav7 -r%dcav8 -r%dcvb " % (nrf, nrf, nrf, nrf ) 
        region += ["WavZG3%d   6 %s  -yzplane %s " % (nrf, region_zwg2, exclcav ),
              "WavZGW3%d  6  %s -( %s )  -yzplane %s " % (nrf, region_zwgw2, region_zwg2, exclcav )]
        assignma += ["ASSIGNMA %10s%10s" % ("VACUUM", "WavZG3%d" % nrf ) ,
                     "ASSIGNMA %10s%10s" % ("Copper", "WavZGW3%d" % nrf) + beamoff4]

        # rbound = [ " -r%dBscpo " % nrf, " -wgbw%d1 -rbound1 " % nrf, 
        #           " -wgbw%d2 -rcyl1 " % nrf ] 
     
    fd.Add(body, region, assignma)

    return

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
        crRFHoles(geo, fd, nrf)
        zlast = crOneRFStructure(geo, fd, nrf, zbegin)
        zbegin = zlast

    return


