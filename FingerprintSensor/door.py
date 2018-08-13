import seed_grove_fingerprint_sensor as sensor
import time
import fingerprint_data

class Door():

    
    def __init__(self):
        
        self.data = fingerprint_data.FingerprintData()              
        self.process()
        
        
    def process(self):
        
        while True:
        
            self.readVisitorIdfromInput()
            self.image = self.data.isRegistered(self.visitorId)
            if self.image != 0:
                self.login()
            else:
                self.register()
            
        
    def readVisitorIdfromInput(self):
        
        print("\n\n")
        print("Please scan your Visitorcard")
        self.visitorId = input()
        print("Piep!")
        
            
    def login(self):
        
        print("Welcome valued Visitor!")
        print("Please wait while the computer is fetching your data.")
        
        com = self.setUpSensor()
        com.DownChar(1)
        com.setDataDownStream(self.image)
                
        print("Please verify with your registered fingerprint.")
        print("Please put your finger on the sensor.")
        
        self.scanFinger(com)
        
        com.Img2Tz(2)
        com.Match()
        if int.from_bytes(com.lastContent, byteorder='big') <= 65535:
            print("Fingerprint matching. Welcome!")
        else:
            print("Fingerprint not matching. Make sure you use the same finger as when registering.")
            print("Lost your finger? Change your stored fingerprint? Please contact the visitor service.")
        
        
    def register(self):
        
        print("There is no stored fingerprint for this visitor account.")
        print("Please put your finger on the sensor.")
        
        com = self.setUpSensor()
        
        self.scanFinger(com)
        com.Img2Tz(1)
        com.UpChar(1)
        char = com.getDataUpStream()
        
        self.data.writeFingerprint(self.visitorId, char)
        
        print("Your fingerprint was registered.")
        
      
    def setUpSensor(self):
        
        com = sensor.SeeedGroveFingerprintSensor("/dev/serial0", 0xAABBCCDD, 115200)
        com.open()
        com.handshake()
        
        return com
    
    
    def scanFinger(self, com):
        
        count = 0
        while True:
        
            com.GenImg()
            if int.from_bytes(com.lastContent, byteorder='big') == 0:
                break
            count +=1
            
            if count>3000:
                return -1
            
            
        print("Finger detected.")
        
        

door = Door()
