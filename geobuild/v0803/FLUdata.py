# 
# Buffer for fluka data, body, region, assignma
#
import sys

class FLUdata(object):
    ''' Stack Fluka data of body, region, and assignmat, and output to the data '''

    def __init__(self):
        self.body = []
        self.region = []
        self.assignmat = []
        self.version=""

    def SetVersion(self, version):
        self.version=str(version)

    def Add(self, body, region, assignmat):
        self.body += body
        self.region += region
        self.assignmat += assignmat

    def AddBody(self, body):
        self.body += body

    def AddRegion(self, region):
        self.region += region

    def AddAssignmat(self, assignmat):
        self.assignmat += assignmat

    def Output(self):
        outdata = {"body":self.body, "region":self.region, "assignmat":self.assignmat}
        if sys.version_info.major == 2:
            for key in outdata.keys():
                fout = open(key+self.version+".inc","w")
                fout.write("\n".join(outdata[key]))
                fout.close()
        else:
            for key in list(outdata.keys()):
                fout = open(key+self.version+".inc","w")
                fout.write("\n".join(outdata[key]))
                fout.close()
    



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


