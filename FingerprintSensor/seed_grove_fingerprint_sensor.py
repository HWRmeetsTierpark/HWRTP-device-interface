#!/usr/bin/python

import serial
import time
import numpy

class SeeedGroveFingerprintSensor():
    
    byte = 8 # Bits per Byte
    answer = 0 # Received Data
    lastHeader = 0
    lastAddress = 0
    lastIdentifier = 0
    lastLength = 0
    lastContent = 0
    lastChecksum = 0
    
    # =====================================================================================
    # Begin of general part
    # General methods for receiving and transmitting data and setting up the connection
    # =====================================================================================
    # =====================================================================================   
    
    def __init__(self, pPort = "/dev/serial0", pChipAddress = 0xFFFFFFFF, pBaudrate = 57600):
        
        # Setting properties
        self.PORT = pPort
        self.CHIP_ADDRESS = pChipAddress
        self.BAUDRATE = pBaudrate
        self.HEADER = 0xEF01
        
        
    def open(self):
        # Opening the connection
        
        # Defining port properties
        self.uart_port = serial.Serial(
            port = self.PORT,
            baudrate = self.BAUDRATE)
        
        # Cheack if port open
        if self.uart_port.isOpen():
            self.uart_port.close()     
        self.uart_port.open()            
            
    def sendCommand(self, pIdentifier, pLength, pContents, pReadAnswer=True):
        # pLength: Length of pContents (Lenght for checksum is added in this method)
        # Data Package format according to ZFM User Manual V15 (english version)
        
        # Add Header
        transfer = 0
        transfer +=  self.HEADER

        # Add Address
        transfer = transfer << (4*self.byte)
        transfer += self.CHIP_ADDRESS
        
        # Package Identifier
        transfer = transfer << (1*self.byte)
        transfer += pIdentifier     
        
        # Package Length
        transfer = transfer << (2*self.byte)
        transfer += (pLength+2)
        
        # Package Contents
        transfer = transfer << (pLength*self.byte)
        transfer += pContents
        
        # Checksum
        transfer = transfer << (2*self.byte)
        transfer += self.calculateChecksum(pIdentifier.to_bytes(1, byteorder = 'big'), (pLength+2).to_bytes(2, byteorder = 'big'), pContents.to_bytes(pLength, byteorder='big'))

        self.send(transfer, pLength+11, pReadAnswer)
        
        
    def send(self, pTransfer, pLength, pReadAnswer):
    # Sending pTransfer to the device
                    
        if self.uart_port.isOpen():
            self.uart_port.write(pTransfer.to_bytes(pLength, byteorder='big'))
            if pReadAnswer:
                self.getStandardAnswer()
            
    
    def calculateChecksum(self, pIdentifier, pLength, pContents):
        # Checksum is calculated according to ZFM User Manual V15 (english version)
            
        checksum = numpy.uint16(sum(pIdentifier) + sum(pLength) + sum(pContents))
        
        return checksum
    
    
    def getStandardAnswer(self):
        # receives answer from the module, checks the checksum, returns content
        # Data Package format according to ZFM User Manual V15 (english version)
        
        # Read components of the package
        if self.uart_port.isOpen():
            self.lastHeader     = self.uart_port.read(2)
            self.lastAddress    = self.uart_port.read(4)
            self.lastIdentifier = self.uart_port.read(1)
            self.lastLength     = self.uart_port.read(2)
            self.lastContent    = self.uart_port.read(int.from_bytes(self.lastLength, byteorder='big')-2)
            self.lastChecksum   = self.uart_port.read(2)

            # Check checksum
            if int.from_bytes(self.lastChecksum, byteorder='big') != self.calculateChecksum(self.lastIdentifier, self.lastLength, self.lastContent):
                return 1
            return 0
        else:
            return 2

    def getDataUpStream(self):
        # reads from the device as long as it outputs data

        data = []

        while True:

            if self.getStandardAnswer() != 0:
                break
            if int.from_bytes(self.lastIdentifier, byteorder='big') == 2 or int.from_bytes(self.lastIdentifier, byteorder='big') == 8:
                row = bytes(self.lastContent)
                data.append(row)
            if int.from_bytes(self.lastIdentifier, byteorder='big') == 8:
                break

        return data
    
    def setDataDownStream(self, pData, pRowLength=128):
        # writes all the data to the device
        
        if self.lastContent == 0:
            count = 0
            for _row in pData:
                count += 1
                if count < len(pData):
                    self.sendCommand(0x02, pRowLength, int.from_bytes(_row, byteorder = 'big'), False)
                else:
                    self.sendCommand(0x08, pRowLength, int.from_bytes(_row, byteorder = 'big'), False)
            
    # =====================================================================================
    # End of general part
    # =====================================================================================
    # =====================================================================================
          
    # =====================================================================================
    # Begin of special part
    # All functions according to ZFM User Manual V15 (english version)
    # =====================================================================================
    # =====================================================================================  

    # =====================================================================================
    # System-related instructions
    # =====================================================================================

    def handshake(self):
        # Communicate link
        
        identifier = 0x01
        length     = 0x0002
        content    = 0x1700
        
        self.sendCommand(identifier, length, content)    
    
    def SetAdder(self, pNewAddress):
        # Set Module address
        
        identifier = 0x01
        length     = 0x05
        content    = 0x15 # Instruction Code
        content = content << (4*self.byte)
        content += pNewAddress
        
        self.sendCommand(identifier, length, content)
        
        self.CHIP_ADDRESS = pNewAddress 
    
    def SetSysPara(self, pParameterNumber, pContents):
        # Set module system's paeameter
        
        identifier = 0x01
        length     = 0x03
        content    = 0x0e # Instruction Code
        content = content << (1*self.byte)
        content   += pParameterNumber
        content = content << (1*self.byte)
        content   += pContents
        
        self.sendCommand(identifier, length, content)
        
    def SetBaudrate(self, pBaudrate):
        
        self.SetSysPara(4, pBaudrate//9600)
        
    def SetSecurityLevel(self, pLevel):

        self.SetSysPara(5, pLevel)
    
    def SetDataPackageLength(self, pLength):

        self.SetSysPara(6,pLength)
        
    
    def ReadSysPara(self):
        
        identifier = 0x01
        length     = 0x01
        content    = 0x0F # Instruction Code
        
        self.sendCommand(identifier, length, content)
    
    def TempleteNum(self):
        # Read valid template number
        
        identifier = 0x01
        length     = 0x01
        content    = 0x1D # Instruction Code
        
        self.sendCommand(identifier, length, content)
        
    # =====================================================================================
    # =====================================================================================

    # =====================================================================================
    # Fingerprint-processing instructions
    # =====================================================================================

    def GenImg(self):
        # Detect finger and store in Image Buffer
        
        identifier = 0x01
        length     = 0x01
        content    = 0x01 # Instruction Code
        
        self.sendCommand(identifier, length, content)
        
        
    def UpImage(self):
        # Upload Image, load image from Image_Buffer to upper computer
        
        identifier = 0x01
        length     = 0x01
        content    = 0x0A # Instruction Code
        
        self.sendCommand(identifier, length, content)        
    
    def DownImage(self):
        # Download image
        
        identifier = 0x01
        length     = 0x01
        content    = 0x0B # Instruction Code
        
        self.sendCommand(identifier, length, content)
        
    def Img2Tz(self, pBufferId):
        # Generate character file from image and store in character Buffer
        # BufferId: 1,2 -> CharBuffer1/2
        
        identifier = 0x01
        length     = 0x02
        content    = 0x02 # Instruction Code
        content = content << (1*self.byte)
        content   += pBufferId
        
        self.sendCommand(identifier, length, content)  
            
    def RegModelA(self):
        # generate template from both CharacterBuffers and store result in both
        # Use Case: Scane same finger two times for better result
        
        identifier = 0x01
        length     = 0x01
        content    = 0x05 # Instruction Code
        
        self.sendCommand(identifier, length, content)
        
    def UpChar(self, pBufferId):
        # Upload character or template to upper computer
        # pBufferId -> source...CharfBuffer1/2
        
        identifier = 0x01
        length     = 0x02
        content    = 0x08 # Instruction Code
        content = content << (1*self.byte)
        content   += pBufferId
        
        self.sendCommand(identifier, length, content)
        
    def DownChar(self, pBufferId):
        # Download Character file or template from upper computer to CharBuffer1/2
        
        identifier = 0x01
        length     = 0x02
        content    = 0x09 # Instruction Code
        content = content << (1*self.byte)
        content   += pBufferId
        
        self.sendCommand(identifier, length, content)
    
    def Store(self, pBufferId, pPageId):
        # Store template from specified Buffer (BufferId) to specified Flash Page (PageId)
        
        identifier = 0x01
        length     = 0x04
        content    = 0x06 # Instruction Code
        content = content << (1*self.byte)
        content   += pBufferId
        content = content << (2*self.byte)
        content   += pPageId
        
        self.sendCommand(identifier, length, content)
        
    def LoadChar(self, pBufferId, pPageId):
        # Load template from specified PageId to specified BufferId
        
        identifier = 0x01
        length     = 0x04
        content    = 0x07 # Instruction Code
        content = content << (1*self.byte)
        content   += pBufferId
        content = content << (2*self.byte)
        content   += pPageId
        
        self.sendCommand(identifier, length, content)
        
    def DeletChar(self, pPageId, pNumberOfTemplates):
        # Delet N (pNumberOfTemplates) from the flash library starting from PageId
        
        identifier = 0x01
        length     = 0x05
        content    = 0x0C # Instruction Code
        content = content << (2*self.byte)
        content   += pPageId
        content = content << (2*self.byte)
        content   += pNumberOfTemplates
        
        self.sendCommand(identifier, length, content)
        
    def Empty(self):
        # Delete all templates in flash library
        
        identifier = 0x01
        length     = 0x01
        content    = 0x0D # Instruction Code
        
        self.sendCommand(identifier, length, content)
        
    def Match(self):
        # Carry out precise matching of templates from both CharBuffer providing matching result
        
        identifier = 0x01
        length     = 0x01
        content    = 0x03 # Instruction Code
        
        self.sendCommand(identifier, length, content)

    def Search(self, pBufferId, pStartPage, pNumberOfTemplates):
        # Search whole library for template matching CharBuffer1/2
        # When found PageId and MatchScore is returned
        
        identifier = 0x01
        length     = 0x06
        content    = 0x04 # Instruction Code
        content = content << (1*self.byte)
        content   += pStartPage
        content = content << (2*self.byte)
        content   += pNumberOfTemplates
        
        self.sendCommand(identifier, length, content)
        
    # =====================================================================================
    # =====================================================================================

    # =====================================================================================
    # Other Instructions
    # =====================================================================================
    
    def GetRandomCode(self):
        # Generates a random number and returns it
        
        identifier = 0x01
        length     = 0x01
        content    = 0x14 # Instruction Code
        
        self.sendCommand(identifier, length, content)
        
    def WriteNotepad(self, pPageId, pData):
        # Write Data (max 32 Bytes) to specified PageId (1..15)
        
        identifier = 0x01
        length     = 0x22
        content    = 0x18 # Instruction Code
        content = content << (1*self.byte)
        content   += pPageId
        content = content << (32*self.byte)
        content   += pData    
        
        self.sendCommand(identifier, length, content)
        
    def ReadNotepad(self, pPageId):
        # Read Data from specified PageId (1..15)
        
        identifier = 0x01
        length     = 0x02
        content    = 0x19 # Instruction Code
        content = content << (1*self.byte)
        content   += pPageId 
        
        self.sendCommand(identifier, length, content)
    
    # =====================================================================================
    # =====================================================================================
    
    # =====================================================================================
    # End of special part
    # =====================================================================================
    # =====================================================================================  
            
    
