#!/bin/env python

import os
import json
import pprint
import math
import sys
import subprocess

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

# ========================================
def getGeant4Parameter(debug=False):
    ''' Returns cavity parameters used by Fukuda's Geant4 simulation '''

    c_light = 2.99792458e10  # cm unit
    freq = 1300.0e6
    tanban_thick = 1.0 # cm

    xlam = c_light/freq
    num_cell = 11
    kasokukan_length = 5.5 * xlam + 2*tanban_thick
    kasokukan_gap = 1.5 * xlam - 2*tanban_thick
    fAccPipeLength = 1.5 * xlam

    acc_oneunit = kasokukan_length + kasokukan_gap
    one_cell_length = 0.5*xlam

    one_cell_length = 11.53048
    acc_oneunit = 161.426708

    
    if debug:
        print("All unit is cm")
        print(("lambda=%15.10f" % xlam))
        print(("tanban_thick (fAccEndPlateLength)=%15.10f" % tanban_thick))
        print(("Kasokukan Cho (fAccLength) =%15.10f" % kasokukan_length))
        print(("(fAccPipeLength = 1.5 lambda )=%15.10f" % fAccPipeLength))
        print(("Kasokukan Gap (Kasokukan no Kankaku) =%15.10f" % kasokukan_gap))
        print(("Kasokukan One_unit Cho  =%15.10f" % acc_oneunit))
        print(("One cell length (fAccCellLength) =%15.10f" % one_cell_length))

    ret = {"acc_oneunit":acc_oneunit,
           "tanban_thick":tanban_thick,
           "one_cell_length": one_cell_length,
           "number_of_cell": num_cell,
           "lambda":xlam, 
           "Tanban_thick": tanban_thick, 
           "Kasokukan_cho": kasokukan_length, 
           "Kasokukan_gap": kasokukan_gap, 
           "Kasokukan_one_unit_cho": acc_oneunit}

    return ret


# ========================================
def createGeoParam():
    ''' Use ### to completely ignore line for comment analysis. '''
    geo = {}

    g4p = getGeant4Parameter(debug=True)

    geo["G4Param"] = g4p
    # Unit: length=cm
    #@ basic parameter to determine global Z coordinate
    geo["bases"] = {"Target_to_FC_gap": 0.2,  # Target to FC gap
                 "FC_thickness" : 10.0, # Thickness(z length) of FC(AMD)
                 "Collimator_thickness" : 12.0, # Thickness(z length) of Collimator in front of cavity
                 "FC_to_Collimator_gap" : 11.4, #  Distance from the FC to the start of collimator
                 "zmin":-800.0, # zmin of  whole area
                 "zmax":1000.0} # zmax of whole area
#                  "rmax":810.0 } # rmax of whole area
    
#                 "shield_rin": 120.0 } # Inner radius of inner concrete shield


    geo["bases"]["FC_to_RF_gap"] = geo["bases"]["FC_to_Collimator_gap"] + geo["bases"]["Collimator_thickness"]
    zbound3 = geo["bases"]["Target_to_FC_gap"] + geo["bases"]["FC_thickness"] + geo["bases"]["FC_to_Collimator_gap"]

    print( "zbound3="+str(zbound3) )

    #@ front
    geo["front"] = {"CSh_up_pos":-75} # Z position of concrete sheild closest to the target 

    #@ global
    # zmax is determined as the end of RF + 1.0 cm
    geo["global"] = {
        "zmin":geo["bases"]["zmin"],  # zmin of whole area
    #     "zmax":1.3E3, # zmax of whole area
    #    "rmax":1100.0,  # rmax of whole area
        "Mount_rock_thickness":310.0, # Thickness of water layer out side of outer concrete tunnel
        "Mount_water_thickness":-10.0, # Thickness of water layer out side of outer concrete tunnel( negative to no water)
        "CWall_thick":10.0, # Thickness of tunnel wall concrete, 
        "SA_thick":200.0, # Servie Area thickness
        "CShIn_thick2":0.0, # Thickness of 2nd inner shield
        "CShIn_thick":200.0, # Thickness of inner Shield 
        "CShIn_rmin":100.0,  # inner radius of smaller concrete sheild
        "CSh_up_thick":30.0, # Thickness of upstream concrete shield covering target area
        "CSh_up0_thick":150.0, # Thickness of first upstream concrete
        "CSh_up_distance":350.0, # Distance between first and second concrete sheild in the upstream
        "CSh_down_thick":30.0, # Thickness of downsream concrete sheield coverging target area
        "FeSh_thick": 20.0, # Thickness of Iron sheild inside of concrete sheild
        "FeSh_thick_upstream": 20, # Thickness of Iron shield of upstream.
        "BPrin":3.2, # Beam pipe inner radius 
        "BPthick":0.5} # Beam pipe thickness

    glp = geo["global"]
                            

    #@ world
    geo["world"] = {"zbound1":glp["zmin"], 
		     "zbound2":-55.0, # Boundary between front(upstream) part and target & RF area
                     "zbound3":zbound3, # First RF cavity Z begin coordinate
                     "blkRPP1":5000000.0}
    gwp = geo["world"]
    gwp["rbound2"] =  glp["CShIn_rmin"] + glp["CShIn_thick"] + glp["CShIn_thick2"] + \
                      glp["SA_thick"] + glp["CWall_thick"]  
    gwp["rbound3"] = gwp["rbound2"] + glp["Mount_water_thickness"] if glp["Mount_water_thickness"] > 0.0 else gwp["rbound2"]
    gwp["rmax"] = gwp["rbound3"] + glp["Mount_rock_thickness"]
    geo["bases"]["rmax"] = gwp["rmax"]
    geo["global"]["rmax"] = gwp["rmax"]

    #@ RF
    geo["RF"] = {"z_rf_begin": zbound3 + geo["bases"]["Collimator_thickness"], # Z_begin of 1st cavity
                 "cavity_cooling_pipe": False, #  True to include cavity cooling pipe
                 # "Nb_structure":36, # Number of RF structure for G4data simulation
                 "Nb_structure":6, # Number of RF structure
                 ### "zlen_rf_unit": 146.43, # length in Z of 1 RF unit. 
                 "zlen_rf_unit": g4p["acc_oneunit"], # length in Z of 1 RF unit. 
                 "Nb_cavity":g4p["number_of_cell"], # Nb of cavities per RF structure
                 "start_thick":2.0,  # Thickness of upstream structure wall
                 "deltaZ_per_cavity_structure":g4p["one_cell_length"], # Z increment per each cavity.
                 "deltaZ_per_cavity":g4p["one_cell_length"] - 2*g4p["tanban_thick"], # The size of cavity vacuum in Z direction.
                 "r_cavity_inner_wall":7.0, # Radius of cavity inner wall.
                 "r_cavity_outer_wall":9.0, # Radius of cavity outer wall
                 "r_cavity_beam_pipe":3.0,   # Radius of cavity beam pipe 
                 "cavity_cooling_pipe_thickness":0.5,  # Thickness(diameter) of cavity cooling pipe. 
                 "solenoid_return_yoke_thick" : 4.0,   # Outer radius of solenoid
                 "solenoid_outer_radius" : 55.0,   # Outer radius of solenoid
                 "solenoid_thickness":34.0,    # Total Thickness (r direction ) of solenoid
                 "solenoid_cooling_pipe_thickness":8.6,  # Total thickness of solenoid cooling pipe in r direction
                            # Assumes 8mm phi pipe in 13.5mmx13.5mm cross section hollocon
                 ###"solenoid_cooling_pipe_thickness":4.7,  # Total thickness of solenoid cooling pipe in r direction
                 ###           # Half of Assumes 8mm phi pipe in 13.5mmx13.5mm cross section hollocon
                 "vacuum_chamber_thick":1.0, # Thickness of vacuum chamber
                 "vacuum_chamber_rmin":15.0, # Inner radius of vacuum chamber
                 "solenoid_gap_shield_z_gapsize": 0.5,  # shield to fill gap between solenoid, z gap ( both upstream and down stream )
                 "solenoid_gap_shield_r_thickness": 10.0, # shield to fill gap betwnn solenoid, thickness in R
                 "collimator_frange_thickness": 2.0, # Thickness of frange for collimator"
                 "BPfrange_thickness": 2.0, # Thickness in Z direction for beam pipe frange at the end of cavity
                 "BPfrange_r_width": 3.0, # beam pipe frange, thickness in r direction
                 "BPfrange_z_distance_from_cavity": 10.0, # beam pipe frange z distance from the end of RF cavity
                 "BPfrange_distance": 10.0, # Z distance between 1st and 2nd beam pipe frange  
                 "wmask_thick":5.0, # W mask ( at the end ) thickness
                 "wmask_z_distance":5.0, # W mask Z position ( distance from the end of RF structure )
                 "wmask_rmin": 3.5, # W mask rmin
                 "wmask_rmax": 11.0}  # W mask rmax 

    grfp=geo["RF"]
    grfp["cooling_pipe_rmin"] = grfp["r_cavity_beam_pipe"] + grfp["cavity_cooling_pipe_thickness"]
    grfp["vacuum_chamber_rmax"] = grfp["vacuum_chamber_rmin"] + grfp["vacuum_chamber_thick"]

    gwp["rbound1"] = grfp["solenoid_return_yoke_thick"] + grfp["solenoid_outer_radius"]
    gwp["zbound4"] = gwp["zbound3"]  + geo["bases"]["Collimator_thickness"] + grfp["zlen_rf_unit"] * grfp["Nb_structure"] + grfp["vacuum_chamber_thick"]
    gwp["zbound5"] = math.ceil(gwp["zbound4"] + 1.0)
    gwp["zbound5"] = math.ceil(gwp["zbound4"] + 1.0)
    geo["global"]["zmax"] = gwp["zbound5"]
   

    # glp["FeSh_zone3_z_length"] = grfp["zlen_rf_unit"]  + geo["bases"]["Collimator_thickness"]  # Fe Shied length in zone 3. ( to the Fe Shield upstream surface )
    glp["FeSh_zone3_z_length"] = geo["bases"]["Collimator_thickness"]  # Fe Shied length in zone 3. ( to the Fe Shield upstream surface )

    #@ Target

    geo["Target"] = {"FC_cooling_pipe": False, # True to Include FC cooling pipe
                 "Collimator_cooling_pipe": False, # True to include Collimator cooling pipe
                 "FC_to_RF_gap":geo["bases"]["FC_to_RF_gap"], # Distance from the FC end to the RF entrance 
                 "FC_to_Collimator_gap":geo["bases"]["FC_to_Collimator_gap"], # Distance from the FC to the start of collimator
                 "Collimator_to_RF_gap":-1.0, # Distance from the collimator to the RF. Negative for not include
                 "Target_to_FC_gap": geo["bases"]["Target_to_FC_gap"], # Target to FC gap
                 "Target_thickness" : 1.6, # Target thickness
                 "WShield_thickness": 10.0, # W shield surrounding target system

                 "Wdisk_rmax" : 25.0, # Max radius of Rotating W disk
                 "Wdisk_hight" : 8.0,  # height in r-direction ( width ) of W disk
                 "Wdisk_axis_offset" : 22.0, # off set of rotation axis ( in x(?y) direction )
                 "Rotator_disk_rmax" : 19.0, # rmax of rotator(cu) disk attached to the cudisk
                 "Rotator_cooling_pipe_thickness" : 1.5, # Thickness ( diameter like ) of cooling pipe inside rotator
                 "Rotator_cooling_pipe_rmax" : 17.0, # Radius of the cooling pipe inside rotator 
                 "Rotator_disk_thickness" : 3.0, # Thickness ( in Z direction ) of rotator disk 
              # Update in v0607
                 "Rotator_axis_rmax" :2.6, # Radius of rotation axis ( rotation axis itself made by Stainless)
                 "Rotator_axis_cooling_pipe_diameter" : 1.1, # Diameter of cooling pipe inside the rotation axis
                 "Rotator_disk_to_vacuum_chamber_gap" : 0.5, # Rotator disk to VC gap in z and R
                 "Rotator_structure_rmax": 8.50, # Radius of target rotator ( pump, etc. fixed part )
                 "Rotator_structure_total_length": 39.5, # Length from rotating copper disk, including vacuum gap and thickness of vacuum chamber
                 "Rotator_support_rthick": 5.0, # R-thickness of rotator support body 
                 "LiquidSeal_thickness_in_r_direction": 1.5, # LiquidSeal thickness in r direction
                 "LiquidSeal_total_length": 6.0, # Total length of LiquidSeal
                 # "LiquidSeal_distance_from_vacuum_chamber": 1.0, # Distance in Z from vacuum chamber
                 "LiquidSeal_distance_from_rotator_disk": 1.0, # Z-distance from rotator disk 
                 "BP_shield_thickness":7.0, # Thickness of beam pipe shield in upstream of target region
              # End of update in v0607                                          

                 "FC_thickness" : geo["bases"]["FC_thickness"], # Thickness(z length) of FC(AMD)
                 "FC_rmin_begin" : 0.8,  # FC upstream inner radius
                 "FC_rmin_end"  : 3.5,   # FC downstream inner radius
                 "FC_cooling_pipe_thickness":0.7, # Collimator cooling pipe thickness
                 "FC_cooling_pipe_offset" : 1.0, # FC cooling pipe offset
                                          # distance from the FC outer surface to the cooling pipe 
                                          # and the distance fron the FC front and back surface. 
                 "FC_ellipse_major": 10.0,  # major axis of FC ellipse 
                 "FC_ellipse_minor": 7.0,  # minor axis of FC ellipse 
                 "FC_ellipse_offset": -3.0, # Offset of center of ellipse                  
                 "FCC_Wdisk_gap": 1.0, # Distance in R direction in the central part of FC.
                 "FC_total_length": 20.0, # Total length of FC, including FC downstream part and upstream part
                 "FC_to_vacuum_chamber_zgap": 5.0, # Z distance between vacuum chamber to FC upstream surface
                 "FCU_rspace": 0.5, # DeltaR in upstream part relative to FC central part 
                 "FCU_slope": 15.0, # Angle of FC upstream part of plane   

                 "Collimator_cooling_pipe_thickness": 0.7, # Collimator cooling pipe thickness
                 "Collimator_cooling_pipe_offset": 1.0 } # Collimator cooling pipe 
                                          # distance fron front, back, and inner surface.
    gtar = geo["Target"]
    grfp["Collimator_rmax"] = grfp["r_cavity_outer_wall"]
    grfp["Collimator_rmin"] = grfp["r_cavity_beam_pipe"]
    gtar["FC_rmax"] = 6.0

    gtar["Target_wdisk_z_begin"] = gwp["zbound3"] - ( gtar["FC_to_Collimator_gap"] +gtar["FC_thickness"] + 
                    gtar["Target_to_FC_gap"] + gtar["Target_thickness"] )
    gtar["vacuum_chamber_R_z_begin"] = gtar["Target_wdisk_z_begin"] \
           - ( gtar["FC_total_length"] - gtar["FC_thickness"] - gtar["Target_to_FC_gap"] - gtar["Target_thickness"] ) \
           -   gtar["FC_to_vacuum_chamber_zgap"] 

    gtar["vacuum_chamber_R_r_max"] = gtar["Wdisk_rmax"] + ( gtar["Rotator_disk_to_vacuum_chamber_gap"] +
                    grfp["vacuum_chamber_thick"] )
    gtar["Rotator_axis_length"] = gtar["Rotator_structure_total_length"]

    #@holes
    # Parameters for various holes; wave guide, cabling, cooling pipe
    geo["Holes"] = { "wave_guides":{}, "cables":{}, "water_lines":{}}
    geo["Holes"]["wave_guides"] = {
                     "width": 8.255, # longer side
                     "height":16.51, # shorter side
                     "wall_thickness": 0.5,   # wall thickness
                     "xcenter": 74.5, # X center position, which runs in Z direction.
                     "zcenter": 98.02,  # Z center position, which runs in X direction
                     "zend": 160.0, # } # Last point in Z of Wave Guide
                     "zoffset": [ 0.0, 25.0, 18.0 ] } # offset in Z direction, when wave guide was bended.
                     # "zoffset": [ 0.0, 92.0, 18.0 ] } # offset in Z direction, when wave guide was bended.
                     #  "zoffset": [ 0.0, 25.0, 25.0 ] } # offset in Z direction, when wave guide was bended.
                                                 # This applies to cables and water_lines as well.
                                                 # First entry is for the one attached to the cavity
    geo["Holes"]["wave_guides"]["nbend"] = 1

    # Adjust Z position when width is changed.
    geo["Holes"]["wave_guides"]["zcenter"] += (geo["Holes"]["wave_guides"]["width"] - 8.50)*0.5
    geo["Holes"]["cables"] = {"radius":1.0, # Radius of cable
                     "gap":0.5, # gap between cable and concrete/castiron
                     "xcenter_FC":-9.0, # X center for FC cable
                     "xcenter_rotator":27.0, # X center for target rotating system
                     "xcenter_solenoid":64.0, # X center for Solenoid power cable
                     "zcenter_solenoid":109.0} # Z center for Solenoid power cable
    geo["Holes"]["water_lines"] = {"radius":2.0, # Radius of water line,
                     "radius_rotator": 0.5*geo["Target"]["Rotator_axis_cooling_pipe_diameter"],
                     "radius_FC":1.0, # FC water line radius
                     "xcenter_FC": -12.0, # xcenter for Flux concentrator
                     "xcenter_rotator": 22.0, # xcenter for target cooling pipe
                     "xcenter_solenoid":67.5, # x center for solenoid cooling water.
                     "zcenter_solenoid": 105.0} # z center for solenoid cooling water  
    geo["Holes"]["vacpipe"] = { "radius":2.5, # Radius of the vacuum part of vacuum pipe for target area
                     "wall_thickness": 0.5, # Thickness of vacuum pipe
                     "zcenters":[5.0, -20.0, -70.0] } # Zcenter of vacuum pipe

    geo["Holes"]["water_lines"]["zcenter_solenoid"] = geo["Holes"]["wave_guides"]["zcenter"] + \
           geo["Holes"]["wave_guides"]["width"]*0.5 + \
           geo["Holes"]["wave_guides"]["wall_thickness"]*2 + \
           geo["Holes"]["water_lines"]["radius"]
    geo["Holes"]["cables"]["zcenter_solenoid"] = geo["Holes"]["water_lines"]["zcenter_solenoid"] + \
               geo["Holes"]["water_lines"]["radius"] + \
               geo["Holes"]["cables"]["radius"] + \
               geo["Holes"]["cables"]["gap"]*2


    print("water_lines:zcenter_solenoid=" + str(geo["Holes"]["water_lines"]["zcenter_solenoid"] ))
    print("cables:zcenter_solenoid     =" + str(geo["Holes"]["cables"]["zcenter_solenoid"] ))




    return geo

# ========================================
if __name__ == "__main__":
   
    if sys.version_info.major == 2:
        execfile("version.py")
    else:
        exec(compile(open("version.py").read(), "version.py", 'exec'))

    geo = createGeoParam()
    json.dump(geo, open("geodata.json","w"))

    fd = FLUdata()
    fd.SetVersion(_VERSION)
    
    crGeoInput(geo, fd)

    fd.Output()

    cmdout = subprocess.check_output("./decaygeo.sh".split())
    print(cmdout)

