#!/bin/env python

import os
import json
import pprint

from FLUdata import *
from create_geometry import *

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



# _body = []
# _region = []
# _assignma = []

# ========================================
def createGeoParam():

    geo = {}
    geo["global"] = {"para":
       {"zmin":-500.0, "zmax": 1200.0, "rmax":810.0,  # zmin, zmax, rmax of whole area
        "Mount_water_thickness":10.0, # Thickness of water layer out side of outer concrete tunnel
        "CShOut_thick":200.0, "CShIn_thick":200, # Thickness of tunnel concrete, larger and smaller
        "CShIn_rmin":120.0,  # inner radius of smaller concrete sheild
        "CSh_up_thick":100.0, "CSh_down_thick":150.0, # Thickness of Upstream and down sream concrete sheield
        "FeSh_thick": 30.0, # Thickness of Iron sheild inside of concrete sheild
        "BPrin":3.2, "BPthick":0.2}} # Beam pipe inner radius and thickness


    glp = geo["global"]["para"]
    geo["world"] = {"para":{"zbound1":glp["zmin"], 
			    "zbound2":-100.0, 
                            "zbound3":17.53, 
                            "zbound5":glp["zmax"],
                            "rbound2":glp["rmax"] - glp["Mount_water_thickness"], 
                            "rbound3":glp["rmax"],
                            "blkRPP1":5000000.0}}
    gwp = geo["world"]["para"]

    geo["front"] = {"para":{"CSh_up_pos":-170}} # Z position of concrete sheild closest to the target 

    geo["RF"] = {"para":{"Nb_structure":6, # Number of RF structure
                 # "zlen_rf_unit": 146.43, # length in Z of 1 RF unit. 
                 "zlen_rf_unit": 163.4, # length in Z of 1 RF unit. 
                 "Nb_cavity":11, # Nb of cavities per RF structure
                 "start_thick":3.6,  # Thickness of upstream structure wall
                 "deltaZ_per_cavity_structure":11.53, # Z increment per each cavity.
                 "deltaZ_per_cavity":7.93, # The size of cavity vacuum in Z direction.
                 "r_cavity_inner_wall":9.0, # Radius of cavity inner wall.
                 "r_cavity_outer_wall":11.0, # Radius of cavity outer wall
                 "r_cavity_beam_pipe":3.0,   # Radius of cavity beam pipe 
                 "cavity_cooling_pipe_thickness":1.0,  # Thickness(diameter) of cavity cooling pipe. 
                 "solenoid_return_yoke_thick" : 4.0,   # Outer radius of solenoid
                 "solenoid_outer_radius" : 55.0,   # Outer radius of solenoid
                 "solenoid_thickness":34.0,    # Total Thickness (r direction ) of solenoid
                 #"solenoid_cooling_pipe_thickness":8.6,  # Total thickness of solenoid cooling pipe in r direction
                 #           # Assumes 8mm phi pipe in 13.5mmx13.5mm cross section hollocon
                 "solenoid_cooling_pipe_thickness":4.3,  # Total thickness of solenoid cooling pipe in r direction
                 #           # Half of Assumes 8mm phi pipe in 13.5mmx13.5mm cross section hollocon
                 "vacuum_chamber_thick":1.0, # Thickness of vacuum chamber
                 "vacuum_chamber_rmin":15.0, # Inner radius of vacuum chamber
                 "solenoid_gap_shield_z_gapsize": 5.0,  # shield to fill gap between solenoid, z gap ( both upstream and down stream )
                 "solenoid_gap_shield_r_thickness": 10.0, # shield to fill gap betwnn solenoid, thickness in R
            
                 "wmask_thick":5.0, # W mask ( at the end ) thickness
                 "wmask_z_distance":5.0, # W mask Z position ( distance from the end of RF structure )
                 "wmask_rmin": 3.5, # W mask rmin
                 "wmask_rmax": 11.0}}  # W mask rmax 

    grfp=geo["RF"]["para"]
    grfp["cooling_pipe_rmin"] = grfp["r_cavity_beam_pipe"] + grfp["cavity_cooling_pipe_thickness"]
    grfp["vacuum_chamber_rmax"] = grfp["vacuum_chamber_rmin"] + grfp["vacuum_chamber_thick"]

    gwp["rbound1"] = grfp["solenoid_return_yoke_thick"] + grfp["solenoid_outer_radius"]
    gwp["zbound4"] = gwp["zbound3"] + grfp["zlen_rf_unit"] * grfp["Nb_structure"] + grfp["vacuum_chamber_thick"]

    glp["FeSh_zone3_z_length"] = grfp["zlen_rf_unit"]*2  # Fe Shied length in zone 3. ( to the Fe Shield upstream surface )


    geo["Target"] = {"para": { "FC_to_RF_gap":20.0, # Distance from the FC end to the RF entrance 
                 "FC_to_Collimator_gap":4.0, # Distance from the FC to the start of collimator
                 "Collimator_to_RF_gap":4.0, # Distance from the collimator to the RF
                 "Target_to_FC_gap": 0.5, # Target to FC gap
                 "Target_thickness" : 1.6, # Target thickness
                 "WShield_thickness": 10.0, # W shield surrounding target system
                 #
                 "Wdisk_rmax" : 25.0, # Max radius of Rotating W disk
                 "Wdisk_hight" : 8.0,  # height in r-direction ( width ) of W disk
                 "Wdisk_axis_offset" : 22.0, # off set of rotation axis ( in x direction )
                 "Rotator_disk_rmax" : 19.0, # rmax of rotator(cu) disk attached to the cudisk
                 "Rotator_cooling_pipe_thickness" : 1.5, # Thickness ( diameter like ) of cooling pipe inside rotator
                 "Rotator_cooling_pipe_rmax" : 17.0, # Radius of the cooling pipe inside rotator 
                 "Rotator_disk_thickness" : 3.0, # Thickness ( in Z direction ) of rotator disk 
                 "Rotator_axis_rmax" : 3.0, # Radius of rotation axis
                 # "Rotator_axis_length" : 10.0, # Length of rotation axis
                 "Rotator_axis_cooling_pipe_diameter" : 1.5, # Diameter of cooling pipe inside the rotation axis
                 "Rotator_disk_to_vacuum_chamber_gap" : 5.0, # Rotator disk to VC gap in z and R
                 #
                 "FC_thickness" : 10.0, # Thickness(z length) of FC(AMD)
                 "FC_rmin_begin" : 0.8,  # FC upstream inner radius
                 "FC_rmin_end"  : 3.5,   # FC downstream inner radius
                 "FC_cooling_pipe_thickness":0.7, # Collimator cooling pipe thickness
                 "FC_cooling_pipe_offset" : 1.0, # FC cooling pipe offset
                                          # distance from the FC outer surface to the cooling pipe 
                                          # and the distance fron the FC front and back surface. 
                 "Collimator_cooling_pipe_thickness": 0.7, # Collimator cooling pipe thickness
                 "Collimator_cooling_pipe_offset": 1.0 }} # Collimator cooling pipe 
                                          # distance fron front, back, and inner surface.
    gtar = geo["Target"]["para"]
    gtar["Collimator_rmax"] = grfp["r_cavity_outer_wall"]
    gtar["Collimator_rmin"] = grfp["r_cavity_beam_pipe"]
    gtar["FC_rmax"] = grfp["r_cavity_outer_wall"]

    gtar["Target_wdisk_z_begin"] = gwp["zbound3"] - ( gtar["FC_to_RF_gap"] + gtar["FC_thickness"] + 
                    gtar["Target_to_FC_gap"] + gtar["Target_thickness"] )
    gtar["vacuum_chamber_R_z_begin"] = gtar["Target_wdisk_z_begin"] - ( gtar["Rotator_disk_thickness"] +
                    gtar["Rotator_disk_to_vacuum_chamber_gap"] )
    gtar["vacuum_chamber_R_r_max"] = gtar["Wdisk_rmax"] + ( gtar["Rotator_disk_to_vacuum_chamber_gap"] +
                    grfp["vacuum_chamber_thick"] )
    gtar["Rotator_axis_length"] = ( gtar["Rotator_disk_to_vacuum_chamber_gap"] +
                    grfp["vacuum_chamber_thick"] + gtar["WShield_thickness"] )

    return geo

# ========================================
if __name__ == "__main__":
   
    execfile("version.py")

    geo = createGeoParam()

    fd = FLUdata()
    fd.SetVersion(_VERSION)
    
    crGeoInput(geo, fd)

    fd.Output()



