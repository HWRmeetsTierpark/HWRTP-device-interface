import fingerprint_object

class FingerprintData():
    
    fingers = []
    
    def __init__(self):
        self.readFromFile('Data.txt')
    
    def isRegistered(self, pId):
        for i in self.fingers:
            if i.visitorId == pId:
                return i.image
        return 0
    
    def writeFingerprint(self, pVisitorId, pImage):
        newObject = fingerprint_object.FingerprintObject()
        newObject.visitorId = pVisitorId
        newObject.image = pImage
        self.fingers.append(newObject)
        self.writeToFile('Data.txt')
        
    def writeToFile(self, pFilePath):
        
        with open(pFilePath, 'w') as f:
            for _object in self.fingers:
                f.write(str(_object.visitorId) + '\n')
                for _row in _object.image:
                    f.write(str(int.from_bytes(_row, byteorder = 'big')) + '\n')
                f.write('%%ObjectEnd%%' + '\n')
                        
    def readFromFile(self, pFilePath):
        
        count = 0
        lineIndex = 0
        newObject = fingerprint_object.FingerprintObject()
        with open(pFilePath) as f:
            for _line in f:
                if lineIndex == 0:
                    newObject.image = []
                    newObject.visitorId = _line.rstrip()
                    lineIndex += 1
                else:
                    if _line.rstrip() == '%%ObjectEnd%%':
                        self.fingers.append(newObject)
                        newObject = fingerprint_object.FingerprintObject()
                        lineIndex = 0
                    else:
                        newObject.image.append(int(_line.rstrip()).to_bytes(128, byteorder = 'big'))
                        lineIndex += 1
                    
                    
                
