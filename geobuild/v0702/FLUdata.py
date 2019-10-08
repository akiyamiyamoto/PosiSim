# 
# Buffer for fluka data, body, region, assignma
#

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
        for key in outdata.keys():
            fout = open(key+self.version+".inc","w")
            fout.write("\n".join(outdata[key]))
            fout.close()



