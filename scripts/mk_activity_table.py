#!/bin/env python 
#
# Print residual activity after some cooling period

import os
import json
import pprint



# =================================================
def getRegionActivity(runit_in, volregion, resnuclei, atomic_number="1", mass_number="3"):
    ''' atomic_number :  Atmic number whoes activity is reported '''
    runit = runit_in
    
    # if runit_in == 40:
    #   runit=35

    resall = resnuclei[str(runit)]
    
    activity = {}

    for detid, resdata in resall.iteritems():
        fileno = resdata["fileno"]
        detname = resdata["detname"]
        period = detname[0:2]
        # regname = detname[2:] if runit_in != 40 else "RF1solc"
        regname = detname[2:] 
        if regname not in volregion:
            print regname + " not found in volume data. set to 0"
            rvol=0
        else:
            rvol = volregion[regname]
        if "regname" not in activity: 
            activity["regname"] = regname 
            activity["volume"] = rvol
            activity["activity"] = {}
        
        bq_per_vol = 0.0
        for isotope in resdata["isotopes"]:
            if isotope[1] == atomic_number and isotope[0] == mass_number:
               bq_per_vol += float(isotope[2])
        bq = bq_per_vol * rvol
        activity["activity"][period]= {"bq_per_vol":bq_per_vol, "bq_total":bq }
        
    return activity

# ============================================================
def activity_table_csv(version, region_unit):
    # version = "-v0602"
    volregion = json.load(open("volregion%s.json" % version ))
    
    resnuclei = json.load(open("resnuclei_data/resnuclei_data.json"))

    # region_unit = [33, 34, 35, 36, 40]
    # region_unit = range(33, 50)

    csvfile="activity_table.csv"
    lines = ["Reg.,Vol.(l),"]
    pdata = ["1s", "1M", "1h", "1d", "1w", "1m", "3m", "1y", "4y", "Xy", "Zy"] 
    lines[0] += ",".join(pdata)

    data_bqrate = []
    data_bqtotal = []

    totalvol = 0.0
    totalbq = {}
    for pd in pdata:
       totalbq[pd]=0.0

    data_sum=0.0        
    for runit in region_unit:
        activity = getRegionActivity(runit, volregion, resnuclei)
        # pprint.pprint(activity)
        lines.append("%s,%8g" % ( activity["regname"], activity["volume"]/1000.0 ))
        totalvol += activity["volume"]/1000.0
        actline = []
        for pd in pdata:
           bq_per_vol = activity["activity"][pd]["bq_per_vol"]*1000.0
           lines[-1] +=",%8g" % bq_per_vol
           if pd == "1s":
               data_bqrate.append([activity["regname"], bq_per_vol])

        lines.append(" , ")
        for pd in pdata:
           bq_total = float(activity["activity"][pd]["bq_total"])
           lines[-1] +=",%8g" % bq_total
           totalbq[pd] += bq_total
           if pd == "1s":
               data_bqtotal.append([activity["regname"], bq_total])
               data_sum += bq_total

    lines.append("Total,%8g" % totalvol)
    lines.append(",")
    for pd in pdata:
       lines[-1] +=",%8g" % float(totalbq[pd])
    
    open(csvfile,"w").write("\n".join(lines))

    print "Activity summary was written to " + csvfile
    os.system("column -s, -t -c 250 %s > %s" % (csvfile, csvfile.replace(".csv",".txt")))
    print "Aligned summary was written to " + csvfile.replace(".csv",".txt")

    fout=open("bqrate.dat","w")
    for ip in range(0, len(data_bqrate)):
        fout.write(str(ip)+" "+str(data_bqrate[ip][1]) + "\n")
    fout.close()

    fout=open("bqtotal.dat","w")
    for ip in range(0, len(data_bqtotal)):
        fout.write(str(ip)+" "+str(data_bqtotal[ip][1]) + "\n")
    fout.close()

    datafile={"bqrate":data_bqrate, "bqtotal":data_bqtotal}
    glabel={"bqrate":{"ylabel":"Bq/1000cm^3", "title":"Region activity",
                      "verpos":"8.1E10", "legpos":"7E10"}, 
           "bqtotal":{"ylabel":"Bq (region total)", "title":"Total region activity",
                      "verpos":"1.62E13", "legpos":"1.3E13"}}

    vertext = version[1:] if version[0:1] == "-" else version
    for ptype in datafile.keys():
        bqrate_file="region_%s.plt" % ptype
        fout=open(bqrate_file,"w")
        gplcmd = ["load \"%s/gnuplot.flair.ini\"" % os.environ["FLUKA_SCRIPTS"], 
                  "# set terminal qt size 1000,800",
                  "set output \"figs/%s.png\"" % ptype, 
                  "set terminal png size 1000,800",
                  "set label \"2625Bx, 5Hz, 5000h beam, 1s cool.\" at screen 0.53,0.85 font \"Times,16\"",
                  "set label \"geom:%s\" at screen 0.8,0.95 font \"Times,14\"" % vertext,
                  "set size ratio 0.85",
                  "set xrange[0:%d]" % len(datafile[ptype]),
                  "set xtics rotate by -45",
                  "set grid",
                  "set ylabel \"%s\"" % glabel[ptype]["ylabel"],
                  "set xlabel \"Region name\"",
                  "set title \"%s\"" % glabel[ptype]["title"],
                  "set xtics font \"Times,13\"",
                  "set origin 0,0.01",
                  "set xlabel offset 0,-0.8", 
                  "set ylabel offset -1,0", 
                  "set title offset 0,-1"]
        if ptype == "bqtotal":
            gplcmd.append("set label \"Region sum = %e Bq\" at screen 0.53,0.78 font \"Times,16\"" % data_sum)
        # if ptype == "bqrate":
        #     gplcmd.append("set ylabel offset 0,0")

        fout.write("\n".join(gplcmd)+"\n")

        fout.write("set xtics (")
        for ip in range(0, len(datafile[ptype])):
            fout.write("\'%s\' %d" % ( datafile[ptype][ip][0], ip ))
            if ip != len(datafile[ptype])-1:
               fout.write(",")
        fout.write(")\n")
        fout.write("plot \"%s.dat\" with boxes linewidth 2 notitle \n" % ptype)
        fout.write("print \"png file was created in figs/%s.png.\"" % ptype)

        fout.close()
    
        print "Gnuplot file for activity of each region was written to " + bqrate_file
        os.system("which gnuplot44 > /dev/null 2>&1 && gnuplot44 "+bqrate_file)

    # bqtotal_file

# =================================================
if __name__ == "__main__":


    version = "-v0603"
    _WATER_UNITS = range(33, 46) + [47,46,49,48]
    # include order correction for v0602, v0603
    if os.path.exists("setting.py"):
        execfile("setting.py")
    version=_VERSION

    print "Analizing unit="+str(_WATER_UNITS)

    activity_table_csv(version, _WATER_UNITS)

