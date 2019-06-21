#!/bin/env python

import os
import json
import pprint

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
    
    gworld = geo["world"]["para"]
    glbal = geo["global"]["para"]
    grf = geo["RF"]["para"]
    gtar = geo["Target"]["para"]

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

    # Collimator in front of RF
    zmsk_end = zend - gtar["Collimator_to_RF_gap"]
    zmsk_len = gtar["FC_to_RF_gap"] - gtar["FC_to_Collimator_gap"] - gtar["Collimator_to_RF_gap"]
    zmsk_bgn = zmsk_end - zmsk_len
    zmsk_cp_in_bgn = zmsk_bgn + gtar["Collimator_cooling_pipe_offset"]
    zmsk_cp_in_len = zmsk_end - gtar["Collimator_cooling_pipe_offset"] - zmsk_cp_in_bgn
    zmsk_cp_in_rmin = gtar["Collimator_rmin"] + gtar["Collimator_cooling_pipe_offset"]
    zmsk_cp_in_rmax = zmsk_cp_in_rmin + gtar["Collimator_cooling_pipe_thickness"]
    zmsk_cp_fr_rmin = zmsk_cp_in_rmax
    zmsk_cp_fr_rmax = gtar["Collimator_rmax"] - gtar["Collimator_cooling_pipe_offset"]

    body += ["RCC tmcpio 0.0 0.0 %f 0.0 0.0 %f %f" % ( zmsk_cp_in_bgn, zmsk_cp_in_len, zmsk_cp_in_rmax)]
    body += ["RCC tmcpii 0.0 0.0 %f 0.0 0.0 %f %f" % ( zmsk_cp_in_bgn, zmsk_cp_in_len, zmsk_cp_in_rmin)]
    body += ["RCC tmcpfo 0.0 0.0 %f 0.0 0.0 %f %f" % ( zmsk_cp_in_bgn, gtar["Collimator_cooling_pipe_thickness"], zmsk_cp_fr_rmax)]
    body += ["RCC tmcpfi 0.0 0.0 %f 0.0 0.0 %f %f" % ( zmsk_cp_in_bgn, gtar["Collimator_cooling_pipe_thickness"], zmsk_cp_fr_rmin)]
    region += ["Tmskcp 6 ( +tmcpio -tmcpii ) | ( +tmcpfo -tmcpfi ) "]
    assignma += [ "ASSIGNMA %10s%10s" % ("WATER", "Tmskcp") ]

    body += ["RCC twmsko 0.0 0.0 %f 0.0 0.0 %f %f" % ( zmsk_bgn, zmsk_len, gtar["Collimator_rmax"])]
    body += ["RCC twmski 0.0 0.0 %f 0.0 0.0 %f %f" % ( zmsk_bgn, zmsk_len, gtar["Collimator_rmin"])]
    region += ["TARwmsk 6 +twmsko -twmski - ( +tmcpio -tmcpii ) - ( +tmcpfo -tmcpfi ) "]
    assignma += [ "ASSIGNMA %10s%10s" % ("WShield", "TARwmsk") ]

    # Geometry other than collimator copper and cooling pipe
    sol_cp_rmax = grf["solenoid_outer_radius"] - ( grf["solenoid_thickness"] - grf["solenoid_cooling_pipe_thickness"] )*0.5 
    sol_cp_rmin = sol_cp_rmax - grf["solenoid_cooling_pipe_thickness"]
    sol_rmin = grf["solenoid_outer_radius"] - grf["solenoid_thickness"]
    vaccham_rmax = grf["vacuum_chamber_rmin"] + grf["vacuum_chamber_thick"]
    this_zlen = gtar["FC_to_RF_gap"] - gtar["FC_to_Collimator_gap"]
    rdata = [ glbal["CShIn_rmin"] - glbal["FeSh_thick"] , gworld["rbound1"], grf["solenoid_outer_radius"], sol_cp_rmax, sol_cp_rmin, 
              sol_rmin, vaccham_rmax, grf["vacuum_chamber_rmin"] ]
    mdata = ["AIR", "STAINLES", "Copper", "WATER", "Copper", "AIR", "STAINLES"]
    for ind in range(0, len(rdata)) :
       body += ["RCC tcolir%d 0.0 0.0 %f 0.0 0.0 %f %f" % (ind, zmsk_bgn, this_zlen, rdata[ind]) ]
       if ind > 0:
          region += ["TCOLIR%d 6 +tcolir%d -tcolir%d" % ( ind, ind-1, ind) ]
          assignma += [ "ASSIGNMA %10s%10s" % (mdata[ind-1], "TCOLIR%d" % ind) ]
    
    region += ["TCOLIRV 6 +tcolir%d - ( +twmsko -twmski ) " % ( len(rdata)-1 ) ]
    assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "TCOLIRV") ]

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

    gworld = geo["world"]["para"]
    glbal = geo["global"]["para"]
    gtar = geo["Target"]["para"]

    # Create body, region, matterial data from outside to the inside.
    body += ["* *************************************",
              "* Body data of Target : Rotation target system " ,
              "* *************************************"]
    region += ["* *************************************",
              "* Region data of Target : Rotation target system " ,
              "* *************************************"]
    # Global parameter
    zbegin = gworld["zbound2"]
    zend = gworld["zbound3"]
    zlen = zend - zbegin
    rmax = glbal["CShIn_rmin"]

    # Flux Concentrator (Adiabatic Matching Device (AMD))
    zfc_end = zend - gtar["FC_to_RF_gap"]
    zfc_bgn = zfc_end - gtar["FC_thickness"]
    zfc_cp_bgn = zfc_bgn + gtar["FC_cooling_pipe_offset"]
    zfc_cp_len = zfc_end - gtar["FC_cooling_pipe_offset"] - zfc_cp_bgn
    zfc_cp_rmax = gtar["FC_rmax"] - gtar["FC_cooling_pipe_offset"]
    zfc_cp_rmin = zfc_cp_rmax - gtar["FC_cooling_pipe_thickness"]
    zfc_cp_fr_rmin = gtar["FC_rmin_end"]

    body += ["RCC tfccpo 0.0 0.0 %f 0.0 0.0 %f %f" % ( zfc_cp_bgn, zfc_cp_len, zfc_cp_rmax) ]
    body += ["RCC tfccpi 0.0 0.0 %f 0.0 0.0 %f %f" % ( zfc_cp_bgn, zfc_cp_len, zfc_cp_rmin) ]
    body += ["RCC tfccpfo 0.0 0.0 %f 0.0 0.0 %f %f" % ( zfc_cp_bgn, gtar["Collimator_cooling_pipe_thickness"], zfc_cp_rmin) ]
    body += ["RCC tfccpfi 0.0 0.0 %f 0.0 0.0 %f %f" % ( zfc_cp_bgn, gtar["Collimator_cooling_pipe_thickness"], zfc_cp_fr_rmin) ]
    region += ["TFCcp 6 ( +tfccpo -tfccpi ) | ( +tfccpfo -tfccpfi ) "]
    assignma += [ "ASSIGNMA %10s%10s" % ("WATER", "TFCcp") ]

    body += ["RCC tfco 0.0 0.0 %f 0.0 0.0 %f %f" % ( zfc_bgn, gtar["FC_thickness"], gtar["FC_rmax"])]
    body += ["TRC tfci 0.0 0.0 %f 0.0 0.0 %f %f %f" % ( zfc_bgn, gtar["FC_thickness"], 
                      gtar["FC_rmin_begin"], gtar["FC_rmin_end"])]
    region += ["TFC 6 +tfco -tfci - ( +tfccpo -tfccpi) - ( +tfccpfo -tfccpfi ) "]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TFC") ]
    region += ["TFCvac 6 +tfci "]
    assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "TFCvac") ]
    envelops["TFC"] = " -tfco "
            
    # CastIron outside

    wdisk_zbgn = gtar["Target_wdisk_z_begin"]
    wdisk_rmin = gtar["Wdisk_rmax"] - gtar["Wdisk_hight"]
    axis_x_offset = gtar["Wdisk_axis_offset"]

    body += ["RCC twdsko %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, wdisk_zbgn, gtar["Target_thickness"], gtar["Wdisk_rmax"])]
    body += ["RCC twdski %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, wdisk_zbgn, gtar["Target_thickness"], wdisk_rmin)]
    region += ["TWdisk 6 +twdsko -twdski "]
    region += ["TCudisk 6 +twdski"]
    assignma += [ "ASSIGNMA %10s%10s" % ("WShield", "TWdisk") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TCudisk") ]
    envelops["wdisk"] = " -twdsko "

    rdisk_zbgn = wdisk_zbgn - gtar["Rotator_disk_thickness"]
    rdisk_cp_zbgn = rdisk_zbgn + (gtar["Rotator_disk_thickness"] - gtar["Rotator_cooling_pipe_thickness"])*0.5
    rdisk_cp_rmax = gtar["Rotator_cooling_pipe_rmax"]
    rdaxis_zbgn = rdisk_zbgn - gtar["Rotator_axis_length"]
    rdaxis_cp_zlen = rdisk_cp_zbgn - rdaxis_zbgn

    body += ["RCC trdisk %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdisk_zbgn, gtar["Rotator_disk_thickness"], 
                       gtar["Rotator_disk_rmax"]) ]
    body += ["RCC trdiskcp %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdisk_cp_zbgn, gtar["Rotator_cooling_pipe_thickness"], 
                       rdisk_cp_rmax)]
    body += ["RCC traxiscp %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdaxis_zbgn, rdaxis_cp_zlen, 
                       gtar["Rotator_axis_cooling_pipe_diameter"]*0.5)]
    body += ["RCC traxis %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, rdaxis_zbgn, gtar["Rotator_axis_length"], 
                       gtar["Rotator_axis_rmax"]) ]
    region += ["TRDiskcp  6 +trdiskcp"]
    region += ["TRAxiscp  6 +traxiscp"]
    region += ["TRDisk 6 +trdisk -trdiskcp -traxiscp "]
    region += ["TRAxis 6 +traxis -traxiscp "]
    assignma += [ "ASSIGNMA %10s%10s%10s" % ("WATER", "TRDiskcp", "TRAxiscp") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("Copper", "TRDisk") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "TRAxis") ]
    envelops["rotation_axis"] = " -traxis "
    envelops["trdisk"] = " -trdisk "

    # Add geometry data
    fd.Add(body, region, assignma)

    return envelops

# =======================================
def crSupportStructure(geo, fd, envelops):

    body = []
    region = []
    assignma = []

    gworld = geo["world"]["para"]
    glbal = geo["global"]["para"]
    grf = geo["RF"]["para"]
    gtar = geo["Target"]["para"]

    # Create body, region, matterial data from outside to the inside.
    body += ["* *************************************",
              "* Body data of Target Zone : Other than FC and support structure " ,
              "* *************************************"]
    region += ["* *************************************",
              "* Region data of Target Zone : Other than FC and support structure " ,
              "* *************************************"]

    # Global parameter
    zbegin = gworld["zbound2"]
    zend = gworld["zbound3"]
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
    region += ["TVCwalld  6 ( +tvcri | +tvcbi ) - tvcrsi - tvcbsi -tvcbpo " + envelops["rotation_axis"] ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "TVCwall") ]
    assignma += [ "ASSIGNMA %10s%10s" % ("STAINLES", "TVCwalld") ]

    notvac = ""
    for key in envelops.keys():
      notvac += envelops[key]
    # print notvac
    region += ["TVCvac 6 ( +tvcrsi | +tvcbsi ) " + notvac ]
    assignma += [ "ASSIGNMA %10s%10s" % ("VACUUM", "TVCvac") ]

    # Beam pipe upstream of target
    bp_zlen = gtar["vacuum_chamber_R_z_begin"] + vc_thick -zbegin
    body += ["RCC tvcbpo 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegin, bp_zlen, glbal["BPrin"] + glbal["BPthick"] ) ]
    body += ["RCC tvcbpi 0.0 0.0 %f 0.0 0.0 %f %f" % ( zbegin, bp_zlen, glbal["BPrin"] ) ]
    region += ["TVCbpwal 6 +tvcbpo -tvcbpi"]
    region += ["TVCbpvac 6 +tvcbpi"]
    assignma +=  [ "ASSIGNMA %10s%10s" % ("STAINLES", "TVCbpwal") ]
    assignma +=  [ "ASSIGNMA %10s%10s" % ("VACUUM", "TVCbpvac") ]

    # W target shield
    sh_zbgn = gtar["vacuum_chamber_R_z_begin"] - gtar["WShield_thickness"] 
    shr_zlen = zend - gtar["FC_to_RF_gap"] - sh_zbgn

    shr_rmax = gtar["vacuum_chamber_R_r_max"] + gtar["WShield_thickness"]
    shb_rmax = vcb_rmin + vc_thick + gtar["WShield_thickness"]
    body += ["RCC tshro %f 0.0 %f 0.0 0.0 %f %f" % ( axis_x_offset, sh_zbgn, shr_zlen, shr_rmax) ]
    body += ["RCC tshbo 0.0 0.0 %f 0.0 0.0 %f %f" % ( sh_zbgn, shr_zlen, shb_rmax ) ]
    region += ["TWShield  6 ( +tshro | +tshbo ) - tvcro - tvcbo - tvcbpo" + envelops["rotation_axis"] ]
    assignma += [ "ASSIGNMA %10s%10s" % ("WShield", "TWShield") ]

    # Air surrounding target area
    zmsk_end = zend - gtar["Collimator_to_RF_gap"]
    zmsk_len = gtar["FC_to_RF_gap"] - gtar["FC_to_Collimator_gap"] - gtar["Collimator_to_RF_gap"]
    zmsk_bgn = zmsk_end - zmsk_len
    air_zlen = zmsk_bgn - zbegin
    air_rmax = glbal["CShIn_rmin"] - glbal["FeSh_thick"] 

    # Additional W shield to fill gap between TWShield and Solenoid
    zmsk2_bgn  = zmsk_bgn - gtar["WShield_thickness"]
    zmsk2_rmax = shb_rmax + gtar["WShield_thickness"]
    body += ["RCC tshb2o 0.0 0.0 %f 0.0 0.0 %f %f " % ( zmsk2_bgn, gtar["WShield_thickness"], zmsk2_rmax)]
    body += ["RCC tshb2i 0.0 0.0 %f 0.0 0.0 %f %f " % ( zmsk2_bgn, gtar["WShield_thickness"], shb_rmax)]
    body += ["RCC tshr2o %f 0.0 %f 0.0 0.0 %f %f " % ( axis_x_offset, zfc_end, gtar["FC_to_Collimator_gap"], shr_rmax)]
    body += ["RCC tshr2i %f 0.0 %f 0.0 0.0 %f %f " % ( axis_x_offset, zfc_end, gtar["FC_to_Collimator_gap"], 
                  gtar["vacuum_chamber_R_r_max"] )]
    region += ["TWShld2 6 ( +tshb2o | +tshr2o ) -tshb2i -tshro - tshr2i -tvcro "]
    assignma += [ "ASSIGNMA %10s%10s" % ("WShield", "TWShld2") ]     

    # Air body, region, assignma
    body += ["RCC tarair 0.0 0.0 %f 0.0 0.0 %f %f " % ( zbegin, air_zlen,  air_rmax)]
    # region += ["TARair 6 +tarair -tvcbpo -tshbo -tshro -tshb2o -tshr2o -( +tvcro | +tvcbo ) "]
    region += ["TARair 6 +tarair -tvcbpo -tshbo -tshro -tshb2o -tshr2o "]
    region += ["TARair2 6 ( +tshb2i -tvcbo -tshbo ) | (+tshr2i -tvcbo -tvcro) "]
    assignma += ["ASSIGNMA %10s%10s" % ("AIR", "TARair") ]  
    assignma += ["ASSIGNMA %10s%10s" % ("AIR", "TARair2") ]  



    # Add geometry data
    fd.Add(body, region, assignma)
