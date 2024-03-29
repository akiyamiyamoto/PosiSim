#!/usr/bin/env python
#
#  Build scoring card data for fluka
#

import os
import json
import sys

# ====================================================
def DCYSCORE_DOSE(dcyname, postname, dcyind, unit, rmax, zmax, zmin, nbinR, nbinZ, rmin=0.0, nphi=1, scoretype="DOSE-EQ" ):

    name = "Sv"+dcyname+postname
    zero = 0.0
    blank = " "
    usrbin = "USRBIN"
    nbinFai = nphi

    card0 = "* Userbin DOES-EQ for decay period of " + name
    
    card1 = "USRBIN".ljust(10)+"11.".rjust(10) + scoretype.rjust(10)
    card1 += str(-unit).rjust(10)
    card1 += "%10.1f%10.1f%10.1f%s" % ( rmax, zero, zmax, name)

    card2  = "USRBIN".ljust(10) + "%10.1f%10.1f" % (rmin, zero)
    card2 += "%10.1f%10.1f%10.1f%10.1f &" % (zmin, nbinR, nbinFai, nbinZ) 

    card3 = "DCYSCORE".ljust(10)
    card3 += "%10.1f%20s%10s%10s%10s" % ( dcyind, blank, name, name, blank) 
    card3 += usrbin.ljust(10)

    return ["* ", card0,card1, card2, card3 ]

# ====================================================
def DCYSCORE_ACTIVITY(dcyname, postname, dcyind, unit, rmax, zmax, zmin, nbinR, nbinZ, 
    xoffset=0.0, phibin=1.0, particle_score="ALL-PART" ):

    stype = "ACTIVITY"
    stype = "ACTOMASS"
    name = "Bm"+dcyname+postname
    zero = 0.0
    blank = " "
    usrbin = "USRBIN"
    nbinFai = phibin
    len_step = 1.0

    card0 = "* Userbin Activity for decay period of " + name

    card1 = "USRBIN".ljust(10)+"1.".rjust(10) + stype.rjust(10)
    card1 += str(-unit).rjust(10)
    card1 += "%10.1f%10.1f%10.1f%s" % ( rmax, zero, zmax, name)

    card2  = "USRBIN".ljust(10) + "%10.1f%10.1f" % (zero, xoffset)
    card2 += "%10.1f%10.1f%10.1f%10.1f &" % (zmin, nbinR, nbinFai, nbinZ)

    card3 = "DCYSCORE".ljust(10)
    card3 += "%10.1f%20s%10s%10s%10.1f" % ( dcyind, blank, name, name, len_step)
    card3 += usrbin.ljust(10)

    card4 = "AUXSCORE".ljust(10) + "USRBIN".rjust(10) 
    card4 += particle_score.rjust(10)+ blank.rjust(10)
    card4 += name.rjust(10) + name.rjust(10)
    card4 += "%10.1f%10s" % ( len_step, blank)

    return ["* ", card0,card1, card2, card3, card4 ]

# ====================================================================================
def Primary_Score(name, stype, unit, rmax, zmax, zmin, nbinR, nbinF, nbinZ, rmin=0.0):

    zero = 0.0
    card = []
    card.append("*")
    card.append("USRBIN".ljust(10)+"11.".rjust(10) + stype.rjust(10))
    card[1] += str(-unit).rjust(10)
    card[1] += "%10.1f%10.1f%10.1f%s" % ( rmax, zero, zmax, name)
    card.append("USRBIN".ljust(10))
    card[2] += "%10.1f%10.1f%10.1f%10.1f%10.1f%10.1f &" % (rmin, zero, zmin, nbinR, nbinF, nbinZ)

    return card

# ===================================================================================
def resnucle_card():
    #
    #  RESNUCLE card
    #
    res_fmt = "%-10s%10.1f%10.1f%10.1f%10.1f%10s%10.1f%s"
    dcyscore_fmt = "%-10s%10.1f%10s%10s%10s%10s%10.1f%s"
    res = ["*", "* Residual nuclei","*"]
    reg_volume = 1.0  # region volume in cm^3
    # regname = ["TWdisk", "TFC", "TARwmsk", "TRDiskcp", "TRAxiscp", "TCOLIR4", 
    #           "Tmskcp", "TFCcp", "RF1cp", "RF1solc", "RF2cp", 
    #           "RF2solc", "RF3cp","RF3solc", "RF4cp", "RF4solc",
    #           "RF5cp",  "RF5solc", "RF6cp","RF6solc", "zone2c", "RockW"]
    regname = ["TWdisk", "TFC", "TARwmsk", "TRDiskcp", "TRAxiscp", "TCOLIR4", 
               "RF1solc", 
               "RF2solc", "RF3solc", "RF4solc",
               "RF5solc", "RF6solc", "zone2c", "RockW"]
    for ind in range(0, len(decaytimes)): 
        iu0 = 30
        res.append("* for decay time of %s" % decaytimes[ind])
        for ir in range(0, len(regname)):
           sname= decaytimes[ind] + regname[ir]
           unit = iu0 + ir
           res.append(res_fmt % ("RESNUCLE", 3.0, -unit, 0.0, 0.0, regname[ir], 0.0, sname))

        sname_bgn = decaytimes[ind] + regname[0]
        sname_end = decaytimes[ind] + regname[-1]
        res.append(dcyscore_fmt % ("DCYSCORE", float(ind+1), " ", " ", sname_bgn, sname_end, 1.0, "RESNUCLEI")) 

    fout = open("decayscore%s.inc" % _VERSION ,"w")
    fout.write("\n".join(res))
    fout.close()


# ========================================================================================================
def usrbdx_for_liquidseal():
    #
    # USRBDX for flux to LiquidSeal
    # 
    usrbdx_fmt1="%-10s%10.1f%10s%10.1f%10s%10s%10.1f%s"
    usrbdx_fmt2="%-10s%10.1f%10s%10.1f%10.1s%10.1s%10.1f %s"
    cards = ["*","* Score flux to LiquidSeal", "*"]
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "NEUTRON", -21, "TRAxis", "LiqSeal", 1.0, "A2SNeutron") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "NEUTRON", -22, "TRotBody", "LiqSeal", 1.0, "B2SNeutron") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "NUCLEONS", -23, "TRAxis", "LiqSeal", 1.0, "A2SNucleon") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "NUCLEONS", -24, "TRotBody", "LiqSeal", 1.0, "B2SNucleon") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "EM-ENRGY", -25, "TRAxis", "LiqSeal", 1.0,   "A2SEmEnrgy") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "EM-ENRGY", -26, "TRotBody", "LiqSeal", 1.0, "B2SEmEnrgy") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "PHOTON", -27, "TRAxis", "LiqSeal", 1.0,   "A2SPhoton") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards.append(usrbdx_fmt1 % ("USRBDX", -1.0, "PHOTON", -28, "TRotBody", "LiqSeal", 1.0, "B2SPhoton") )
    cards.append(usrbdx_fmt2 % ("USRBDX", 5.0, "1E-6", 500.0, "","", 1.0, "&"))
    cards+=["* End of usrbdx","*"]

    return cards

# ====================================================================================
def decay_score(geodata):

    # decaytimes = ["1s", "1M", "1h","1d","1w","1m","3m","1y","4y","Xy","Zy"]
    # decaytimes = ["1s", "1h","1d","1m","3m","1y","4y","Xy","Zy"]
    # decaytimes = ["1h","1m","1y","Xy","Zy"]
    # decaytimes = ["1h","1d", "4d", "1m","1y","Xy"]
    decaytimes = ["1h","1d", "4d", "1m","1y","5y"]

    par_all = geodata["par_all"]
    par_mid = geodata["par_mid"]
    par_tar = geodata["par_tar"]
    geo = geodata["geo"]
    rinshield = geo["global"]["CShIn_rmin"] + geo["global"]["CShIn_thick"]

    cards = []
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_DOSE(decaytimes[ind], "All", ind+1, 71, 
                par_all[0], par_all[1], par_all[2], par_all[3], par_all[4])
    #   cards += DCYSCORE_DOSE(decaytimes[ind], "Sout", ind+1, 77, 
    #            par_all[0], par_all[1], par_all[2], par_all[3], par_all[4], rmin=rinshield)
      
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "All", ind+1, 72, 
                par_all[0], par_all[1], par_all[2], par_all[3], par_all[4])

    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_DOSE(decaytimes[ind], "Allm", ind+1, 73, 
                par_mid[0], par_mid[1], par_mid[2], par_mid[3], par_mid[4])

# Na22, Co60, Eu152, Eu154 
    nbinr = float(int(par_all[3]/5))
    nbinz = float(int(par_all[4]/5))
# Na22(Z=11, A=22
    z=11    
    a=22
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "ANa22", ind+1, 91, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz,
                particle_score=str(pcode))
# Co60(Z=27, A=60)
    z=27    
    a=60
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "ACo60", ind+1, 92, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz, 
                particle_score=str(pcode))

# Eu152(Z=63, A=152)
    z=63    
    a=152
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "AEu152", ind+1, 93, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz, 
                particle_score=str(pcode))

# Eu154(Z=63, A=154)
    z=63    
    a=154
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "AEu154", ind+1, 94, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz,
                particle_score=str(pcode))

# H3(Z=1, A=3)
    z=1 
    a=3
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "AH3", ind+1, 95, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz,
                particle_score=str(pcode))

# Fe55(Z=26, A=55)
    z=26
    a=55
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "AFE55", ind+1, 95, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz,
                particle_score=str(pcode))

# Mn54(Z=25, A=54)
    z=25
    a=54
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "AMN54", ind+1, 95, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz,
                particle_score=str(pcode))

# Ca45(Z=20, A=45)
    z=20
    a=45
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "ACA45", ind+1, 95, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz,
                particle_score=str(pcode))

# Sc46(Z=21, A=46)
    z=21
    a=46
    pcode=-(z*100+a*100000)
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "ASC46", ind+1, 95, 
                par_all[0], par_all[1], par_all[2], nbinr, nbinz,
                particle_score=str(pcode))


    #for ind in range(0, len(decaytimes)):
    #   cards += DCYSCORE_ACTIVITY(decaytimes[ind], "Allm", ind+1, 74, 
    #            par_mid[0], par_mid[1], par_mid[2], par_mid[3], par_mid[4])
       
    #par_tar = [30.0, 40.0, -40.0, 400.0, 500.0]
    #for ind in range(0, len(decaytimes)):
    #   cards += DCYSCORE_DOSE(decaytimes[ind], "Allt", ind+1, 75, 
    #            par_tar[0], par_tar[1], par_tar[2], par_tar[3], par_tar[4])

     # Decay score of region upstream of target
    # def DCYSCORE_DOSE(dcyname, postname, dcyind, unit, rmax, zmax, zmin, nbinR, nbinZ, rmin=0.0, scoretype="DOSE-EQ" ):
    #for ind in range(0, len(decaytimes)):
    #   cards += DCYSCORE_DOSE(decaytimes[ind], "Fhim", ind+1, 76,
    #            120.0, -107.0, -137.0,  120.0, 4.0, nphi=500.0 )
    #   cards += DCYSCORE_DOSE(decaytimes[ind], "Almz", ind+1, 77,
    #            120.0, 20.0, -600.0, 120.0, 720.0)

    # for ind in range(0, len(decaytimes)):
    #    cards += DCYSCORE_DOSE(decaytimes[ind], "edep", ind+1, 78, 
    #            20.0, 69.8, -10.2, 200, 800, scoretype="DOSE")

    #for ind in range(0, len(decaytimes)):
    #   cards += DCYSCORE_ACTIVITY(decaytimes[ind], "Allt", ind+1, 76, 
    #            par_tar[0], par_tar[1], par_tar[2], par_tar[3], par_tar[4])

    usrbin_fmt1="%-10s%10.1f%10s%10.1f%10.1f%10.1f%10.1f%s"
    usrbin_fmt2="%-10s%10.1f%10.1f%10.1f%10.1f%10.1f%10.1f %s"
    #xoffset = 22.0
    #rmax = par_tar[0]
    # phibin= 72.0 
    #phibin= 1.0 
    #cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "DOSE-EQ", -90, rmax, 0.0, par_tar[1], "pAdoseEQ")) 
    #cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))
    #cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "DOSE", -90, rmax, 0.0, par_tar[1], "pAdose")) 
    #cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))
    #cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "DOSE-EM", -90, rmax, 0.0, par_tar[1], "pAdoseEM")) 
    #cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))
    #cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "NIEL-DEP", -90, rmax, 0.0, par_tar[1], "pANielDep")) 
    #cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))

    #for ind in range(0, len(decaytimes)):
    #   cards += DCYSCORE_ACTIVITY(decaytimes[ind], "AlltAx", ind+1, 94, 
    #            rmax, par_tar[1], par_tar[2], par_tar[3], par_tar[4], xoffset=xoffset, phibin=phibin)
    return cards

# ===================================================================================
def primary_score(geodata):

    par_all = geodata["par_all"]
    par_mid = geodata["par_mid"]
    par_tar = geodata["par_tar"]
    geo = geodata["geo"]
    rinshield = geo["global"]["CShIn_rmin"] + geo["global"]["CShIn_thick"]

#    rmax_all = geo["world"]["rbound3"]
#    zmin_all = geo["world"]["zbound1"]
#    zmax_all = geo["world"]["zbound5"]
#    nbinZ = 1000.0
#    nbinR = rmax_all
#    par_all = [rmax_all, zmax_all, zmin_all, nbinR, nbinZ]

#    par_mid = [120.0, 400.0, -100.0, 400.0, 500.0]
#    par_tar = [30.0, 0.0, -40.0, 150.0, 200.0]

    cards = []
    cards += Primary_Score("priAll", "DOSE-EQ", 81, 
                par_all[0], par_all[1], par_all[2], par_all[3], 1.0, 1405.0)

    cards += Primary_Score("pDose", "DOSE", 81, 
                par_all[0], par_all[1], par_all[2], par_all[3], 1.0, 1405.0)

    cards += Primary_Score("pEMDose", "DOSE-EM", 81, 
                par_all[0], par_all[1], par_all[2], par_all[3], 1.0, 1405.0)

    cards += Primary_Score("primid", "DOSE-EQ", 82, 
                par_mid[0], par_mid[1], par_mid[2], par_mid[3], 1.0, par_mid[4])
    #cards += Primary_Score("primidf", "DOSE-EQ", 82, 
    #            par_mid[0], -107.0, -137.0,  120.0, 500.0, 4.0)
    #cards += Primary_Score("primidz", "DOSE-EQ", 82, 
    #            par_mid[0], 20.0, -600.0,  120.0, 1.0, 720.0)

#    cards += Primary_Score("pritar", "DOSE-EQ", 83, 
#                par_tar[0], par_tar[1], par_tar[2], par_tar[3], 1.0, par_tar[4])

#    cards += Primary_Score("tdose",     "DOSE", 85, 5.0, 0.1, -1.9, 500, 1, 200 )
#    cards += Primary_Score("tdEMd",  "DOSE-EM", 85, 5.0, 0.1, -1.9, 500, 1, 200 )
#    cards += Primary_Score("tdNiel", "NIEL-DEP", 85,5.0, 0.1, -1.9, 500, 1, 200 )

# 
# def Primary_Score(name, stype, unit, rmax, zmax, zmin, nbinR, nbinF, nbinZ, rmin=0.0):
# Primary Energy deposit to Target
#    cards += Primary_Score("rfdose1",     "DOSE", 86, 10.0,100.0, 0.0, 100, 1,1000 )    
#    cards += Primary_Score("rfEMd1",   "DOSE-EM", 86, 10.0,100.0, 0.0, 100, 1,1000 )    
#    cards += Primary_Score("rfNiel1", "NIEL-DEP", 86, 10.0,100.0, 0.0, 100, 1,1000 )    

#    cards += Primary_Score("rfdose2",     "DOSE", 87, 10.0,5900.0, 5400.0, 100, 1, 1000 )  
#    cards += Primary_Score("rfEMd2",   "DOSE-EM", 87, 10.0,5900.0, 5400.0, 100, 1, 1000 )  
#    cards += Primary_Score("rfNiel2", "NIEL-DEP", 87, 10.0,5900.0, 5400.0, 100, 1, 1000 )  

# def Primary_Score(name, stype, unit, rmax, zmax, zmin, nbinR, nbinF, nbinZ, rmin=0.0):
# Primary Energy deposit to Target
#    cards += Primary_Score("rfdose1",     "DOSE", 86, 20.0,69.8, -10.2, 200, 1,800 )
#    cards += Primary_Score("rfEMd1",   "DOSE-EM", 86, 10.0,70.2, -10.2, 100, 1,800 )
#    cards += Primary_Score("rfNiel1", "NIEL-DEP", 86, 10.0,70.2, -10.2, 100, 1,800 )
#    cards += Primary_Score("rfDPA",    "DPA-SCO", 86, 20.0,69.8, -10.2, 200, 1,800 )
# energy deposit to cavity/solenoid and downstream frange 
#    cards += Primary_Score("soldose",     "DOSE", 86, 60.0,200.6, 10.6, 380, 1,400 )
#    cards += Primary_Score("frgdose",     "DOSE", 86, 7.0,187.435,171.435, 35, 1,80 )
# DPA and Edep to target and FC, phi dis.
#    cards += Primary_Score("tardose",     "DOSE", 86, 20.0,1.0,-2.0, 100, 150, 30 )
#    cards += Primary_Score("tardpa",    "DPA-SCO", 86, 20.0,1.0,-2.0, 100, 150, 30 )

#
# Does and DPA to Frange


# 

    return cards

# ===================================================================================
def set_geodata(geo):

    rmax_all = geo["world"]["rmax"]
    zmin_all = geo["world"]["zbound1"]
    zmax_all = geo["world"]["zbound5"]
    nbinZ = 1000.0
    nbinR = rmax_all
    par_all = [rmax_all, zmax_all, zmin_all, nbinR, nbinZ]

    par_mid = [120.0,400.0, -200.0, 200.0, 300.0]
    par_tar = [30.0, 25.0, -15.0, 150.0, 200.0]

    ret = {"geo":geo, "par_all":par_all, "par_mid":par_mid, "par_tar":par_tar}

    return ret

# ====================================================================================
def resnucle_card(version, decaytimes):
#
#  RESNUCLE card
#
    res_fmt = "%-10s%10.1f%10.1f%10.1f%10.1f%10s%10.1f%s"
    dcyscore_fmt = "%-10s%10.1f%10s%10s%10s%10s%10.1f%s"
    res = ["*", "* Residual nuclei","*"]
    reg_volume = 1.0  # region volume in cm^3
    # regname = ["InShld", "InShldo", "MidAir", "OutShld", "MontRock", "RockW"]
    # regname = ["InShld", "InShldo", "MidAir", "OutShld", "MontRock"]
    regname = ["InShld", "MidAir", "OutShld", "MontRock"]
    for ind in range(0, len(decaytimes)): 
        iu0 = 30
        res.append("* for decay time of %s" % decaytimes[ind])
        for ir in range(0, len(regname)):
           sname= decaytimes[ind] + regname[ir]
           unit = iu0 + ir
           res.append(res_fmt % ("RESNUCLE", 3.0, -unit, 0.0, 0.0, regname[ir], 0.0, sname))

        sname_bgn = decaytimes[ind] + regname[0]
        sname_end = decaytimes[ind] + regname[-1]
        res.append(dcyscore_fmt % ("DCYSCORE", float(ind+1), " ", " ", sname_bgn, sname_end, 1.0, "RESNUCLEI")) 

    fout = open("resnucle%s.inc" % version ,"w")
    fout.write("\n".join(res))
    fout.close()





# ====================================================================================
if __name__ == "__main__":

    if sys.version_info.major == 2:  
        execfile("version.py")
    else:
        exec(compile(open("version.py").read(), "version.py", 'exec'))



    geo = json.load(open("geodata.json"))

    geodata = set_geodata(geo)

    cards = primary_score(geodata)

    cards += decay_score(geodata)
#     cards += usrbdx_for_liquidseal()


    fout=open("scoring%s.inc" % _VERSION ,"w")
    fout.write("\n".join(cards))
    fout.close()

    # decaytimes = ["1h","1d", "4d", "1m","1y","Xy"]
    decaytimes = ["1h","1d", "4d", "1m","1y","5y"]
    resnucle_card(_VERSION, decaytimes)
