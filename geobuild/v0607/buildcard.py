#!/usr/bin/env python
#
#  Build scoring card data for fluka
#

import os
import json


# ====================================================
def DCYSCORE_DOSE(dcyname, postname, dcyind, unit, rmax, zmax, zmin, nbinR, nbinZ, rmin=0.0 ):

    name = "Sv"+dcyname+postname
    zero = 0.0
    blank = " "
    usrbin = "USRBIN"
    nbinFai = 1

    card0 = "* Userbin DOES-EQ for decay period of " + name
    
    card1 = "USRBIN".ljust(10)+"11.".rjust(10) + "DOSE-EQ".rjust(10)
    card1 += str(-unit).rjust(10)
    card1 += "%10.1f%10.1f%10.1f%s" % ( rmax, zero, zmax, name)

    card2  = "USRBIN".ljust(10) + "%10.1f%10.1f" % (rmin, zero)
    card2 += "%10.1f%10.1f%10.1f%10.1f &" % (zmin, nbinR, nbinFai, nbinZ) 

    card3 = "DCYSCORE".ljust(10)
    card3 += "%10.1f%20s%10s%10s%10s" % ( dcyind, blank, name, name, blank) 
    card3 += usrbin.ljust(10)

    return ["* ", card0,card1, card2, card3 ]

# ====================================================
def DCYSCORE_ACTIVITY(dcyname, postname, dcyind, unit, rmax, zmax, zmin, nbinR, nbinZ, xoffset=0.0, phibin=1.0 ):

    stype = "ACTIVITY"
    name = "Bq"+dcyname+postname
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
    card4 += "ALL-PART".rjust(10)+ blank.rjust(10)
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


# ====================================================================================
if __name__ == "__main__":
  
    execfile("version.py")


    # decaytimes = ["1s", "1M", "1h","1d","1w","1m","3m","1y","4y","Xy","Zy"]
    decaytimes = ["1s", "1h","1d","1m","3m","1y","4y","Xy","Zy"]

    dcyname = ""

    geo = json.load(open("geodata.json"))
    
    rmax_all = geo["world"]["para"]["rbound3"]
    zmin_all = geo["world"]["para"]["zbound1"]
    zmax_all = geo["world"]["para"]["zbound5"]
    rinshield = geo["global"]["para"]["CShIn_rmin"] + geo["global"]["para"]["CShIn_thick"]
    nbinZ = 1000.0
    nbinR = rmax_all
    par_all = [rmax_all, zmax_all, zmin_all, nbinR, nbinZ]
    cards = []
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_DOSE(decaytimes[ind], "All", ind+1, 71, 
                par_all[0], par_all[1], par_all[2], par_all[3], par_all[4])
       cards += DCYSCORE_DOSE(decaytimes[ind], "Sout", ind+1, 77, 
                par_all[0], par_all[1], par_all[2], par_all[3], par_all[4], rmin=rinshield)
      
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "All", ind+1, 72, 
                par_all[0], par_all[1], par_all[2], par_all[3], par_all[4])

    par_mid = [120.0, 400.0, -100.0, 400.0, 500.0]
       
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_DOSE(decaytimes[ind], "Allm", ind+1, 73, 
                par_mid[0], par_mid[1], par_mid[2], par_mid[3], par_mid[4])
       
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "Allm", ind+1, 74, 
                par_mid[0], par_mid[1], par_mid[2], par_mid[3], par_mid[4])
       
    par_tar = [30.0, 40.0, -40.0, 400.0, 500.0]
    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_DOSE(decaytimes[ind], "Allt", ind+1, 75, 
                par_tar[0], par_tar[1], par_tar[2], par_tar[3], par_tar[4])

    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "Allt", ind+1, 76, 
                par_tar[0], par_tar[1], par_tar[2], par_tar[3], par_tar[4])

    cards += Primary_Score("priAll", "DOSE-EQ", 81, 
                par_all[0], par_all[1], par_all[2], par_all[3], 1.0, par_all[4])

    cards += Primary_Score("primid", "DOSE-EQ", 82, 
                par_mid[0], par_mid[1], par_mid[2], par_mid[3], 1.0, par_mid[4])

    cards += Primary_Score("pritar", "DOSE-EQ", 83, 
                par_tar[0], par_tar[1], par_tar[2], par_tar[3], 1.0, par_tar[4])

    cards += Primary_Score("prdose", "DOSE", 83, 
                par_tar[0], par_tar[1], par_tar[2], par_tar[3], 1.0, par_tar[4])

    cards += Primary_Score("prEMdos", "DOSE-EM", 83, 
                par_tar[0], par_tar[1], par_tar[2], par_tar[3], 1.0, par_tar[4])

    cards += Primary_Score("priSout", "DOSE-EQ", 84, 
                par_all[0], par_all[1], par_all[2], par_all[3], 1.0, par_all[4],  rmin=rinshield)
# 
    par_tar = [30.0, 0.0, -40.0, 150.0, 200.0]
    usrbin_fmt1="%-10s%10.1f%10s%10.1f%10.1f%10.1f%10.1f%s"
    usrbin_fmt2="%-10s%10.1f%10.1f%10.1f%10.1f%10.1f%10.1f %s"
    xoffset = 22.0
    rmax = par_tar[0]
    phibin= 72.0 
    cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "DOSE-EQ", -90, rmax, 0.0, par_tar[1], "pAdoseEQ")) 
    cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))
    cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "DOSE", -90, rmax, 0.0, par_tar[1], "pAdose")) 
    cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))
    cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "DOSE-EM", -90, rmax, 0.0, par_tar[1], "pAdoseEM")) 
    cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))
    cards.append(usrbin_fmt1 % ("USRBIN", 11.0, "NIEL-DEP", -90, rmax, 0.0, par_tar[1], "pANielDep")) 
    cards.append(usrbin_fmt2 % ("USRBIN", 0.0, xoffset, par_tar[2], par_tar[3], phibin, par_tar[4], " &"))

    for ind in range(0, len(decaytimes)):
       cards += DCYSCORE_ACTIVITY(decaytimes[ind], "AlltAx", ind+1, 94, 
                rmax, par_tar[1], par_tar[2], par_tar[3], par_tar[4], xoffset=xoffset, phibin=phibin)
#
# USRBDX for flux to LiquidSeal
# 
    usrbdx_fmt1="%-10s%10.1f%10s%10.1f%10s%10s%10.1f%s"
    usrbdx_fmt2="%-10s%10.1f%10s%10.1f%10.1s%10.1s%10.1f %s"
    cards+= ["*","* Score flux to LiquidSeal", "*"]
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


    fout=open("scoring%s.inc" % _VERSION ,"w")
    fout.write("\n".join(cards))
    fout.close()

#
#  RESNUCLE card
#
    res_fmt = "%-10s%10.1f%10.1f%10.1f%10.1f%10s%10.1f%s"
    dcyscore_fmt = "%-10s%10.1f%10s%10s%10s%10s%10.1f%s"
    res = ["*", "* Residual nuclei","*"]
    reg_volume = 1.0  # region volume in cm^3
    regname = ["TWdisk", "TFC", "TARwmsk", "TRDiskcp", "TRAxiscp", "TCOLIR4", 
               "Tmskcp", "TFCcp", "RF1cp", "RF1solc", "RF2cp", 
               "RF2solc", "RF3cp","RF3solc", "RF4cp", "RF4solc",
               "RF5cp",  "RF5solc", "RF6cp","RF6solc", "zone2c", "RockW"]
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



