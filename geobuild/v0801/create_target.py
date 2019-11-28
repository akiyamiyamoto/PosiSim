#!/bin/env python

import os
import json
import pprint
import sys
import math

from FLUdata import *

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


# =======================================
def crTargetZone(geo, fd):
    ''' Create geometry of target zone '''
    
    crTargetCollimatorZone(geo, fd)
    # Create RotationTargetSystem
    envelops=crRotationTarget(geo, fd)

    # Geometry other than rotation target and FC
    crSupportStructure(geo, fd, envelops)
  
    return

# =======================================
def crTargetCollimatorZone(geo, fd):

    body = []
    region = []
    assignma = []
    
    gworld = geo["world"]
    glbal = geo["global"]
    grf = geo["RF"]
    gtar = geo["Target"]

    # Create body, region, matterial data from outside to the inside.
    body += ["* *************************************",
              "* Body data of Target Zone " ,
              "* *************************************"]
    region += ["* *************************************",
              "* Region data of Target Zone " ,
              "* *************************************"]
    
    # CastIron outside
    zbegin = gworld["zbound2"]
    zend = gworld["zbound3"]
    zlen = zend - zbegin
    rmax = glbal["CShIn_rmin"]
    body += ["RCC z2FeSho 0.0 0.0 %f 0.0 0.0 %f %f" % (zbegin, zlen, rmax), 
             "RCC z2FeShi 0.0 0.0 %f 0.0 0.0 %f %f" % (zbegin, zlen, 
                  rmax - glbal["FeSh_thick"]) ]
    region += ["TARColim 6 +z2FeSho -z2FeShi"] 
    assignma += [ "ASSIGNMA %10s%10s" % ("CASTIRON", "TARColim") ]

    # Add geometry data
    fd.Add(body, region, assignma)

    return

# =====================================================================================
def crRotationTarget(geo, fd):
    ''' Create geometry of Rotation target system '''

    body = []
    region = []
    assignma = []
    envelops = {}

    gworld = geo["world"]
    glbal = geo["global"]
    gtar = geo["Target"]

    # Create body, region, matterial data from outside to the inside.
    body += ["* *************************************",
              "* Body data of Target : Rotation target system " ,
              "* *************************************"]
    region += ["* *************************************",
              "* Region data of Target : Rotation target system " ,
              "* *************************************"]
    # Global parameter
    zbegin = gworld["zbound2"]
    zend = gworld["zbound3"] + geo["bases"]["Collimator_thickness"]
    zlen = zend - zbegin
    rmax = glbal["CShIn_rmin"]

    # Flux Concentrator, elliptical shape (Adiabatic Matching Device (AMD))
    fc_cp = gtar["FC_cooling_pipe"]
    zfc_end = zend - gtar["FC_to_RF_gap"]
    zfc_bgn = zfc_end - gtar["FC_thickness"]

    wdisk_zbgn = gtar["Target_wdisk_z_begin"]
    wdisk_rmin = gtar["Wdisk_rmax"] - gtar["Wdisk_hight"]
    axis_x_offset = gtar["Wdisk_axis_offset"]

    fcc_length = gtar["Target_to_FC_gap"] + gtar["Target_thickness"]
    zfcc_bgn = wdisk_zbgn

    fcu_length = gtar["FC_total_length"] - ( fcc_length + gtar["FC_thickness"] )
    zfcu_bgn = zfcc_bgn - fcu_length

    # FCC, downstream part.
    #                  Vx,Vy,Vz  Hx,Hy,Hz  R1x,R1y,R1z,  R2x,R2y, R2z
    body += ["REC tfco %f 0.0 %f 0.0 0.0 %f %f 0.0 0.0 0.0 %f 0.0 " % \
           ( gtar["FC_ellipse_offset"], zfc_bgn, gtar["FC_thickness"], \
             gtar["FC_ellipse_major"], gtar["FC_ellipse_minor"] ) ]

    body += ["TRC tfci 0.0 0.0 %f 0.0 0.0 %f %f %f" % ( zfc_bgn, gtar["FC_thickness"], 
                      gtar["FC_rmin_begin"], gtar["FC_rmin_end"])]

    region += ["TFC 6 +tfco -tfci "]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TFC") ]
    region += ["TFCvac 6 +tfci "]
    assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "TFCvac") ]
    envelops["TFC"] = " -tfco "

    # Downstream part of FC
    body += ["REC tfcco %f 0.0 %f 0.0 0.0 %f %f 0.0 0.0 0.0 %f 0.0 " % \
           ( gtar["FC_ellipse_offset"], zfcc_bgn, fcc_length, \
             gtar["FC_ellipse_major"], gtar["FC_ellipse_minor"] ) ]

    body += ["RCC tfcci %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, zfcc_bgn, fcc_length, 
                     gtar["Wdisk_rmax"] + gtar["FCC_Wdisk_gap"])]
    region += ["TFCC 6 +tfcco -tfcci "]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TFCC") ]
    envelops["TFCC"] = " -( +tfcco -tfcci ) "
    
    # FCC upstream part
    body += ["REC tfcuo %f 0.0 %f 0.0 0.0 %f %f 0.0 0.0 0.0 %f 0.0 " % \
           ( gtar["FC_ellipse_offset"], zfcu_bgn, fcu_length, \
             gtar["FC_ellipse_major"], gtar["FC_ellipse_minor"] ) ]

    fcu_vz = zfcc_bgn
    fcu_vx = gtar["Wdisk_axis_offset"] + gtar["Wdisk_rmax"] + gtar["FCC_Wdisk_gap"] + gtar["FCU_rspace"]
    fcu_hx = math.cos(gtar["FCU_slope"]/180.0*math.pi )
    fcu_hz = math.sin(gtar["FCU_slope"]/180.0*math.pi )

    body += ["PLA tfcui %f 0.0 %f %f 0.0 %f" % (fcu_hx, fcu_hz, fcu_vx, fcu_vz )]

    region += ["TFCU 6 +tfcuo -tfcui "]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TFCU") ]
    envelops["TFCU"] = " -( +tfcuo -tfcui ) "
    
            
    # CastIron outside


    body += ["RCC twdsko %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, wdisk_zbgn, gtar["Target_thickness"], gtar["Wdisk_rmax"])]
    body += ["RCC twdski %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, wdisk_zbgn, gtar["Target_thickness"], wdisk_rmin)]
    region += ["TWdisk 6 +twdsko -twdski "]
    region += ["TCudisk 6 +twdski"]
    assignma += [ "ASSIGNMA %10s%10s" % ("TARMAT", "TWdisk") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TCudisk") ]
    envelops["wdisk"] = " -twdsko "

    rdisk_zbgn = wdisk_zbgn - gtar["Rotator_disk_thickness"]
    rdisk_cp_zbgn = rdisk_zbgn + (gtar["Rotator_disk_thickness"] - gtar["Rotator_cooling_pipe_thickness"])*0.5
    rdisk_cp_rmax = gtar["Rotator_cooling_pipe_rmax"]
    rdaxis_zbgn = rdisk_zbgn - gtar["Rotator_axis_length"]
    rdaxis_cp_zlen = rdisk_cp_zbgn - rdaxis_zbgn

    # fsmask_zbgn = gtar["vacuum_chamber_R_z_begin"] - gtar["LiquidSeal_distance_from_vacuum_chamber"]
    # fs_zbgn = fsmask_zbgn - gtar["LiquidSeal_total_length"]
    fs_zbgn = rdisk_zbgn - gtar["LiquidSeal_total_length"] - gtar["LiquidSeal_distance_from_rotator_disk"]
    fs_rmax = gtar["Rotator_axis_rmax"] + gtar["LiquidSeal_thickness_in_r_direction"]    

    body += ["RCC trdisk %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdisk_zbgn, gtar["Rotator_disk_thickness"], 
                       gtar["Rotator_disk_rmax"]) ]
    body += ["RCC trdiskcp %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdisk_cp_zbgn, 
                       gtar["Rotator_cooling_pipe_thickness"], rdisk_cp_rmax)]
    body += ["RCC traxiscp %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdaxis_zbgn, rdaxis_cp_zlen, 
                       gtar["Rotator_axis_cooling_pipe_diameter"]*0.5)]
    body += ["RCC traxis %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdaxis_zbgn, gtar["Rotator_axis_length"], 
                       gtar["Rotator_axis_rmax"]) ]
    body += ["RCC trotbody %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdaxis_zbgn, gtar["Rotator_axis_length"], 
                       gtar["Rotator_structure_rmax"]) ]
    body += ["RCC liqseal %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, fs_zbgn, gtar["LiquidSeal_total_length"],
                       fs_rmax) ]

    region += ["TRDiskcp  6 +trdiskcp"]
    region += ["TRAxiscp  6 +traxiscp"]
    assignma += [ "ASSIGNMA %10s%10s%10s" % ("WATER", "TRDiskcp", "TRAxiscp") ]

    region += ["TRDisk 6 +trdisk -trdiskcp -traxiscp "]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TRDisk") ]

    region += ["TRAxis 6 +traxis -traxiscp "]
    region += ["TRotBody 6 +trotbody -traxis -liqseal"]
    region += ["LiqSeal 6 +liqseal -traxis"]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "TRAxis") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("LIGHTSUS", "TRotBody") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("LIQSEAL", "LiqSeal") ]
    # envelops["rotation_axis"] = " -traxis "
    envelops["rotation_body"] = " -trotbody "
    envelops["trdisk"] = " -trdisk "

    # Add geometry data
    fd.Add(body, region, assignma)

    return envelops

# =======================================
def crSupportStructure(geo, fd, envelops):

    body = []
    region = []
    assignma = []

    gworld = geo["world"]
    glbal = geo["global"]
    grf = geo["RF"]
    gtar = geo["Target"]

    # Create body, region, matterial data from outside to the inside.
    body += ["* *************************************",
              "* Body data of Target Zone : Other than FC and support structure " ,
              "* *************************************"]
    region += ["* *************************************",
              "* Region data of Target Zone : Other than FC and support structure " ,
              "* *************************************"]

    # Global parameter
    zbegin = gworld["zbound2"]
    zend = gworld["zbound3"] + geo["bases"]["Collimator_thickness"]
    zlen = zend - zbegin
    rmax = glbal["CShIn_rmin"]

    # Vacuum chamber surrounding FC and rotation target 
    zfc_end = zend - gtar["FC_to_RF_gap"]
    vc_thick = grf["vacuum_chamber_thick"]
    vcb_rmin = grf["vacuum_chamber_rmin"]
    vcr_zlen = zfc_end - gtar["vacuum_chamber_R_z_begin"]
    vcb_zlen = (zfc_end + gtar["FC_to_Collimator_gap"] ) - gtar["vacuum_chamber_R_z_begin"]
    axis_x_offset = gtar["Wdisk_axis_offset"]

    body += ["RCC tvcro %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, gtar["vacuum_chamber_R_z_begin"], 
                       vcr_zlen, gtar["vacuum_chamber_R_r_max"])] 
    body += ["RCC tvcri %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, gtar["vacuum_chamber_R_z_begin"], 
                       vcr_zlen, gtar["vacuum_chamber_R_r_max"] - vc_thick)] 
    body += ["RCC tvcrsi %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, gtar["vacuum_chamber_R_z_begin"]+vc_thick, 
                       vcr_zlen - 2*vc_thick, gtar["vacuum_chamber_R_r_max"] - vc_thick)] 
    body += ["RCC tvcbo 0.0 0.0 %f 0.0 0.0 %f %f" % ( gtar["vacuum_chamber_R_z_begin"], 
                       vcb_zlen, vcb_rmin + vc_thick)] 
    body += ["RCC tvcbi 0.0 0.0 %f 0.0 0.0 %f %f" % ( gtar["vacuum_chamber_R_z_begin"], 
                       vcb_zlen, vcb_rmin ) ] 
    body += ["RCC tvcbsi 0.0 0.0 %f 0.0 0.0 %f %f" % ( gtar["vacuum_chamber_R_z_begin"] + vc_thick, 
                       vcb_zlen-vc_thick, vcb_rmin ) ] 
    region += ["TVCwall  6 ( +tvcro | +tvcbo ) - tvcri - tvcbi "]
    region += ["TVCwalld  6 ( +tvcri | +tvcbi ) - tvcrsi - tvcbsi -tvcbpo " + envelops["rotation_body"] ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "TVCwall") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "TVCwalld") ]

    notvac = ""
    if sys.version_info.major == 2:
       for key in envelops.keys():
          notvac += envelops[key]
    else:
       for key in list(envelops.keys()):
          notvac += envelops[key]
    # print notvac
    region += ["TVCvac 6 ( +tvcrsi | +tvcbsi ) " + notvac ]
    assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "TVCvac") ]

    # Beam pipe upstream of target
    bp_zlen = gtar["vacuum_chamber_R_z_begin"] + vc_thick -zbegin
    bpshld_zlen = bp_zlen - vc_thick - gtar["WShield_thickness"]
    body += ["RCC tvcbpo 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegin, bp_zlen, glbal["BPrin"] + glbal["BPthick"] ) ]
    body += ["RCC tvcbpi 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegin, bp_zlen, glbal["BPrin"] ) ]
    bpshield_rmax = glbal["BPrin"] + glbal["BPthick"] + gtar["BP_shield_thickness"]
    body += ["RCC tbpshld 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegin, bpshld_zlen, bpshield_rmax ) ]

    region += ["TVCbpvac 6 +tvcbpi"]
    region += ["TVCbpwal 6 +tvcbpo -tvcbpi"]
    # region += ["TBPShld 6 +tbpshld -tvcbpo"]
    assignma +=  [ "ASSIGNMA %10s%10s" % ("VACUUM", "TVCbpvac") ]
    assignma +=  [ "ASSIGNMA %10s%10s" % ("STAINLES", "TVCbpwal") ]
    # assignma +=  [ "ASSIGNMA %10s%10s" % ("AIR", "TBPShld") ]

    # W target shield
    sh_zbgn = gtar["vacuum_chamber_R_z_begin"] - gtar["WShield_thickness"] 
    shr_zlen = zend - gtar["FC_to_RF_gap"] - sh_zbgn

    shr_rmax = gtar["vacuum_chamber_R_r_max"] + gtar["WShield_thickness"]
    shb_rmax = vcb_rmin + vc_thick + gtar["WShield_thickness"]
    body += ["RCC tshro %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, sh_zbgn, shr_zlen, shr_rmax) ]
    body += ["RCC tshbo 0.0 0.0 %f 0.0 0.0 %f %f" % ( sh_zbgn, shr_zlen, shb_rmax ) ]
    region += ["TWShield  6 ( +tshro | +tshbo ) - tvcro - tvcbo -tvcbpo " + envelops["rotation_body"] ]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TWShield") ]

    # Air surrounding target area
    crgap = gtar["Collimator_to_RF_gap"] if gtar["Collimator_to_RF_gap"] > 0.0 else 0.0 
    zmsk_end = zend - crgap
    zmsk_len = gtar["FC_to_RF_gap"] - gtar["FC_to_Collimator_gap"] - crgap
    zmsk_bgn = zmsk_end - zmsk_len
    air_zlen = zmsk_bgn - zbegin
    air_rmax = glbal["CShIn_rmin"] - glbal["FeSh_thick"] 

    # Additional W shield to fill gap between TWShield and Solenoid
    # zmsk2_bgn  = zmsk_bgn - gtar["WShield_thickness"] - 10.0
    zmsk2_bgn = sh_zbgn + shr_zlen
    zmsk2_len = zmsk_bgn - zmsk2_bgn
    # zmsk2_rmax = shb_rmax + gtar["WShield_thickness"] 
    zmsk2_rmax = vcb_rmin + vc_thick + gtar["WShield_thickness"] 
    body += ["RCC tshb2o 0.0 0.0 %f 0.0 0.0 %f %f " % ( zmsk2_bgn, zmsk2_len, zmsk2_rmax)]
    # body += ["RCC tshb2i 0.0 0.0 %f 0.0 0.0 %f %f " % ( zmsk2_bgn, zmsk2_len, shb_rmax)]
    body += ["RCC tshb2i 0.0 0.0 %f 0.0 0.0 %f %f " % ( zmsk2_bgn, zmsk2_len, vcb_rmin + vc_thick)]
    body += ["RCC tshr2o %f 0.0 %f 0.0 0.0 %f %f " % ( axis_x_offset, zfc_end, gtar["FC_to_Collimator_gap"], shr_rmax)]
    body += ["RCC tshr2i %f 0.0 %f 0.0 0.0 %f %f " % ( axis_x_offset, zfc_end, gtar["FC_to_Collimator_gap"], 
                  gtar["vacuum_chamber_R_r_max"] )]
    # region += ["TWShld2 6 ( +tshb2o | +tshr2o ) -tshb2i -tshro - tshr2i -tvcro "]
    # region += ["TWShld2 6 ( +tshr2o | +tshr2o ) -tvcbo "]
    # region += ["TWShld2 6 ( +tshb2o -tvcro | +tshr2o -tshr2i ) "]
    region += ["TWShld2 6 ( +tshb2o -tvcbo -tshr2i ) | ( +tshr2o -tshr2i -tshb2o ) "]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TWShld2") ]     

    # Air body, region, assignma
    body += ["RCC tarair 0.0 0.0 %f 0.0 0.0 %f %f " % ( zbegin, air_zlen,  air_rmax)]
    # region += ["TARair 6 +tarair -tvcbpo -tshbo -tshro -tshb2o -tshr2o -( +tvcro | +tvcbo ) "]
    region += ["TARair 6 +tarair -tvcbpo -tshbo -tshro -tshb2o -tshr2o -trotbody "]
    # region += ["TARair 6 +tarair -tbpshld -tshbo -tshro -tshr2o -trotbody "]
    region += ["TARair2 6 ( +tshb2i -tvcbo -tshbo ) | (+tshr2i -tvcbo -tvcro) "]
    assignma += ["ASSIGNMA %10s%10s" % ("AIR", "TARair") ]  
    assignma += ["ASSIGNMA %10s%10s" % ("AIR", "TARair2") ]  



    # Add geometry data
    fd.Add(body, region, assignma)
