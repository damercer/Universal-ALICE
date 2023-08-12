#
# Hardware specific interface functions
# For XProto Lab Plain (7-20-2023)
# Written using Python version 3.10, Windows OS 
#
import usb.core
import usb.util
import usb.control
from usb.backend import libusb0, libusb1
be0, be1 = libusb0.get_backend(), libusb1.get_backend()
#import usb.backend.libusb1 as libusb1
# import usb.backend.libusb0 as libusb0
#import usb.backend.openusb as openusb

Tdiv.set(8)
TimeDiv = 0.001
# Vertical Sensitivity list in v/div
# Channel A / B gain Range: [0,6] 5.12V/div to 80mV/div
CHvpdiv = ("80mV", "160mV", "320mV", "640mV", "1.28V", "2.56V", "5.12mV")
#
## Time list in s/div
# Sampling Rate Range: [0, 21] 8 us/div to 50 s/div
TMpdiv = ("8us", "16us", "32us", "64us", "128us", "256us", "500us", "1.0ms", "2.0ms", "5.0ms",
          "10ms", "208ms", "50ms", "100ms", "200ms", "500ms", "1.0s", "2s", "5s", "10s", "20s", "50s")
#
# adjust for your specific hardware by changing these values
global DevID; DevID = "XProto"
global TimeSpan; TimeSpan = 0.001
CHANNELS = 2 # Number of supported input channels
AWGChannels = 1 # Number of supported output channels
EnablePGAGain = 0 # 1
EnableOhmMeter = 1
EnableDmmMeter = 1
EnableDigIO = 1
DBuff = []
#
## Hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, xscope
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig("alice-last-config.cfg")
        xscope.close() # May need to be changed for specific hardware port
        # exit
    except:
        donothing()

    root.destroy()
    exit()
#
# USB communications with instrument
#
#
def Get_Data():
    global xscale, VBuffA, VBuffB, DBuff, TRACESread, xscope
    global CH1vpdvLevel, CH2vpdvLevel, CHAsb, CHBsb, ep0, ep1
    global Interp4Filter, InOffA, InOffB, InGainA, InGainB

    #
    xscope.ctrl_transfer(0xC0,ord('g'),0,0,0)
    time.sleep(0.001)
    # xscope.ctrl_transfer(0xC0,ord('h'),0,0,0)
    CH1vpdvLevel = UnitConvert(CHAsb.get())
    CH2vpdvLevel = UnitConvert(CHBsb.get())
    VBuff1 = []
# Get data from instrument
#get chA, chB, dig, and frame data
#bulk transfer of 64 bytes each
#add data to VBuff1
    for u in range (13):
        data = xscope.read(ep0.bEndpointAddress,ep0.wMaxPacketSize)
        VBuff1.extend(data.tolist())
    # print( '# VBuff1 ', len(VBuff1))
    #
    DBuff = []
    frameindex = []
    #
    VBuff1 = numpy.array(VBuff1)
# Interpolate by 4
    VBuffA = [] # Clear the A array 
    VBuffB = [] # Clear the B array
    index = 0
    while index < len(VBuff1): #
        pointer = 0
        while pointer < 4:
            if index < 256:
                VBuffA.append(VBuff1[index])
            elif index >= 256 and index < 512:
                VBuffB.append(VBuff1[index])
            elif index >= 512 and index < 768:
                DBuff.append(VBuff1[index])
            else:
                frameindex.append(VBuff1[index])
                pointer = pointer + 3
            pointer = pointer + 1
        index = index + 1
    #
    # print( 'frame and index =', frameindex)
    VBuffA = numpy.array(VBuffA)
    VBuffB = numpy.array(VBuffB)
    GainA = (CH1vpdvLevel * -8)/256
    VBuffA = VBuffA - 128
    VBuffA = VBuffA * GainA
    #
    GainB = (CH2vpdvLevel * -8)/256
    VBuffB = VBuffB - 128
    VBuffB = VBuffB * GainB
    
    VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
    VBuffA = numpy.convolve(VBuffA, Interp4Filter )
    #VBuffA = numpy.roll(VBuffA, -4)
    VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
    VBuffB = numpy.convolve(VBuffB, Interp4Filter )
    #VBuffB = numpy.roll(VBuffB, -4)
    VBuffA = (VBuffA[3:1027] - InOffA) * InGainA
    VBuffB = (VBuffB[3:1027] - InOffB) * InGainB
    # Find trigger sample point if necessary
    #
    LShift = 0
    if TgInput.get() == 1:
        FindTriggerSample(VBuffA)
    if TgInput.get() == 2:
        FindTriggerSample(VBuffB)
    if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
        LShift = 0 - TRIGGERsample
        VBuffA = numpy.roll(VBuffA, LShift)
        VBuffB = numpy.roll(VBuffB, LShift)
        # print("TRIGGERsample ", TRIGGERsample, ", Length ", len(VBuffA))
#
    xscope.ctrl_transfer(0xC0,ord('f'),0,0,0)
    time.sleep(0.01)
    TRACESread = 2
    
#
## try to connect to XProto Lab
#
def ConnectDevice():
    global xscope, cfg, untf, DevID, MaxSamples, AWGSAMPLErate, SAMPLErate
    global bcon, FWRevOne, HWRevOne, ep0, ep1, be0, be1
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv
    global CHAsb, CHBsb, TMsb
    global TgInput, TgEdge, TRIGGERlevel, TRIGGERentry

    if DevID == "No Device" or DevID == "XProto":
        #
        # Setup instrument
        #find the scope
        xscope = usb.core.find(idVendor=5840, idProduct=1785) # , backend=be1)
        if xscope is None:
            print('Xscope is not connected')
            exit()
        #find the number of configurations
        print( 'nomber of configurations : ',xscope.bNumConfigurations)
        cfg=xscope[0]

        #find the number of interfaces and alternate settings
        print( "nomber of interfaces of config 0 : ",cfg.bNumInterfaces)
        intf=cfg[0,0]
        print( "nomber of alternate settings : ",intf.bAlternateSetting)

        #find the end points
        print( "nomber of end point : ",intf.bNumEndpoints)
        ep0=intf[0]
        ep1=intf[1]
        print( "ep0 adress: ",ep0.bEndpointAddress)
        print( "ep1 :adress ",ep1.bEndpointAddress)
        print( "packet max of ep0 : ",ep0.wMaxPacketSize)
        print( "packet max of ep1 : ",ep1.wMaxPacketSize)

        #set configuration before beeing able to communicate with the scope
        xscope.set_configuration()

        #To get firmware version a:
        data = xscope.ctrl_transfer(0xC0,0x61,0,0,4)
        print( data )
        v=data.tolist()
        FWRevOne = chr(v[0])+chr(v[1])+chr(v[2])+chr(v[3])
        print("Software Rev: ", FWRevOne)
        # print(xscope)
        #to restore defaults , command is ?k?
        # xscope.ctrl_transfer(0xC0,ord('k'),0,0,0)
        # command, value, index
        xscope.ctrl_transfer(0xC0,ord('b'),32,1,0)
        xscope.ctrl_transfer(0xC0,ord('b'),32,2,0)
        xscope.ctrl_transfer(0xC0,ord('b'),0b00000001,5,0)
        xscope.ctrl_transfer(0xC0,ord('b'),0,21,0)
        xscope.ctrl_transfer(0xC0,ord('b'),0,22,0)
        xscope.ctrl_transfer(0xC0,ord('b'),0,23,0)
        xscope.ctrl_transfer(0xC0,ord('b'),0,24,0)
        xscope.ctrl_transfer(0xC0,ord('b'),127,25,0) # Set Trigger level
        xscope.ctrl_transfer(0xC0,ord('b'),120,26,0)
        xscope.ctrl_transfer(0xC0,ord('b'),128,27,0)
        xscope.ctrl_transfer(0xC0,ord('b'),100,28,0)
        # xscope.ctrl_transfer(0xC0,ord('q'),0,0,0)
        xscope.ctrl_transfer(0xC0,ord('g'),0,0,0)
        bcon.configure(text="Conn", style="GConn.TButton")
        BCHAlevel()
        BCHBlevel()
        return(True) # return a logical true if sucessful!
    else:
        return(False)

def SetAwgWidth():
    global AWGAWidthEntry

    WidthNum = UnitConvert(AWGAWidthEntry.get())
    
#
#
## Make the current selected AWG waveform
#
# Shape list SINE(1)|SQUare(2)|RAMP(3)|PULSe(4)|AmpALT(11)|AttALT(12)|StairDn(5)|StairUD(7) |
#  StairUp(6)|Besselj(8)|Bessely(9)|Sinc(10)
AwgString1 = "Sine"
AwgString2 = "Square"
AwgString3 = "Triangle"
AwgString4 = "Pulse"
AwgString5 = "Stair Down"
AwgString6 = "Stair Up"
AwgString7 = "Stair Up-Down"
AwgString8 = "Sinc"
AwgString9 = "Bessel J"
AwgString10 = "Bessel Y"
AwgString11 = "AmpALT"
AwgString12 = "AttALT"
#
def MakeAWGwaves(): # make awg waveforms in case something changed
    global AWGAShape, AWGAShapeLabel, EnableScopeOnly
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGASymmetryEntry, AWGADutyCycleEntry
    global AwgString1, AwgString2, AwgString3, AwgString4, AwgString5, AwgString6
    global AwgString7, AwgString8, AwgString9, AwgString10, AwgString11, AwgString12
    global AwgString13, AwgString14, AwgString15, AwgString16

    if AWGAShape.get()==1:
        send(":FUNCtion SINE")
        AWGAShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGAShape.get()==2:
        send(":FUNCtion SQUare")
        AWGAShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGAShape.get()==3:
        send(":FUNCtion RAMP")
        AWGAShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGAShape.get()==4:
        send(":FUNCtion PULSe")
        AWGAShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGAShape.get()==5:
        send(":FUNCtion StairDn")
        AWGAShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGAShape.get()==6:
        send(":FUNCtion StairUp")
        AWGAShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGAShape.get()==7:
        send(":FUNCtion StairUD")
        AWGAShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGAShape.get()==8:
        send(":FUNCtion Sinc")
        AWGAShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGAShape.get()==9:
        send(":FUNCtion Besselj")
        AWGAShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGAShape.get()==10:
        send(":FUNCtion Bessely")
        AWGAShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGAShape.get()==11:
        send(":FUNCtion AmpALT")
        AWGAShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGAShape.get()==12:
        send(":FUNCtion AttALT")
        AWGAShapeLabel.config(text = AwgString12) # change displayed value
    else:
        AWGAShapeLabel.config(text = "Other Shape") # change displayed value
#
    #SetAwgFrequency()
    #SetAwgAmpl()
    #SetAwgOffset()
    time.sleep(0.1)
#
# Trigger Stuff
#
def BSetTriggerSource():
    global TgInput

    if TgInput.get() == 1:
        xscope.ctrl_transfer(0xC0,ord('b'),0,24,0)
    if TgInput.get() == 2:
        xscope.ctrl_transfer(0xC0,ord('b'),1,24,0)
        
#
def BSetTrigEdge():
    global TgEdge
    
    if TgEdge.get() == 0:
        xscope.ctrl_transfer(0xC0,ord('b'),0,5,0)
    else:
        xscope.ctrl_transfer(0xC0,ord('b'),8,5,0)
#
def BTriggerMode(): 
    global TgInput, ana_str

    if (TgInput.get() == 0):
         #no trigger
        xscope.ctrl_transfer(0xC0,ord('b'),0,5,0)
    elif (TgInput.get() == 1):
         #trigger source set to detector of analog in channels
         #
        xscope.ctrl_transfer(0xC0,ord('b'),0,5,0)
    elif (TgInput.get() == 2):
        # trigger source set to detector of analog in channels
        #
        xscope.ctrl_transfer(0xC0,ord('b'),0,5,0)
        
## evalute trigger level entry string to a numerical value and set new trigger level     
def SendTriggerLevel():
    global TRIGGERlevel, TRIGGERentry, RUNstatus

    # evalute entry string to a numerical value
    # send(":TRIGger:SINGle:EDGe:LEVel 1.0")
    
    TRIGGERlevel = UnitConvert(TRIGGERentry.get())
    xscope.ctrl_transfer(0xC0,ord('b'),128,25,0)
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
# Set Internal / External triggering 
def BTrigIntExt(): # Dummy Routine because hardware does not support external triggering
    global TgSource, TriggerInt

    donothing()
    
# Set Horz possition from entry widget
def SetHorzPoss():
    global HozPoss, HozPossentry, RUNstatus

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TIMEdiv/HorzValue)
    
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
#
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TIMEdiv/HorzValue)
    
    # prevent divide by zero error
## Set Hor time scale from entry widget
def SetSampleRate():
    global TimeDiv, TMsb, RUNstatus, Tdiv, TMpdiv
    global TimeSpan, SAMPLErate, TIMEperDiv

    Level = TMpdiv.index(TMsb.get())
    #to set timescale (index 0 ) to level 5?:
    xscope.ctrl_transfer(0xC0,ord('b'),Level,0,0)
    TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
    #print("Time per div: ", TimeDiv)
    SAMPLErate = (256 / TimeSpan)*2 # interpolate samples by 4x 
#    
def HCHAlevel():
    global CHAsb, RUNstatus, CH1vpdvLevel, xscope, CHvpdiv

    pointer = CHvpdiv.index(CHAsb.get())
    Level = 6 - pointer
    # Channel A gain Range: [0,6] 5.12V/div to 80mV/div
    # to set channel A gain (index 12 ) to level 3?:
    xscope.ctrl_transfer(0xC0,ord('b'),Level,12,0)

def HCHBlevel():
    global CHBsb, RUNstatus, CH2vpdvLevel, xscope, CHvpdiv

    pointer = CHvpdiv.index(CHBsb.get())
    Level = 6 - pointer
    # Channel B gain Range: [0,6] 5.12V/div to 80mV/div
    #to set channel B gain (index 13 ) to level 5?:
    xscope.ctrl_transfer(0xC0,ord('b'),Level,13,0)  
        
def HOffsetA(event):
    global CHAOffset, CHAVPosEntry, CH1vpdvLevel, RUNstatus

    NumberOfDiv = int(CHAOffset/CH1vpdvLevel)
    

def HOffsetB(event):
    global CHBOffset, CHBVPosEntry, CH2vpdvLevel, RUNstatus

    NumberOfDiv = int(CHBOffset/CH2vpdvLevel)
    
#
