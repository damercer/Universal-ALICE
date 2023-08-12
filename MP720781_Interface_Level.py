#
# Hardware specific interface functions
# For Multicomp Pre MP720781 Scope Meter (7-27-2023)
# Written using Python version 3.7, Windows OS 
#
import usb.core
import usb.util
import usb.control
from usb.backend import libusb0, libusb1, openusb # , IBackend
be0, be1 = libusb0.get_backend(), libusb1.get_backend()
be3 = openusb.get_backend()
Tdiv.set(12)
TimeDiv = 0.0002
import yaml
#
# adjust for your specific hardware by changing these values
DevID = "MP72"
TimeSpan = 0.001
CHANNELS = 2 # Number of supported Analog input channels
AWGChannels = 1 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 0 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 # 1
EnableOhmMeter = 0
EnableDmmMeter = 0
EnableDigIO = 0
SMPfft = 4 * 300 # Set FFT size based on fixed acquisition record length
#
## Hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, core, ana_out
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig("alice-last-config.cfg")
        dev.close() # May need to be changed for specific hardware port
        # exit
    except:
        donothing()

    root.destroy()
    exit()
#
#
# USB communications with instrument
#
def send(cmd):
    global dev
    # address taken from results of print(dev):   ENDPOINT 0x1: Bulk OUT
    dev.write(0x01,cmd)
    # address taken from results of print(dev):   ENDPOINT 0x81: Bulk IN
    result = (dev.read(0x81,100000,1000))
    return result

def get_id():
    # returns a character string <Manufacturer>,<model>,<serial number>,X.XX.XX
    return str(send('*IDN?').tobytes().decode('utf-8'))
#
def get_data(ch, yscale, yoffset):
    global dev
    # first 4 bytes indicate the number of data bytes following
    rawdata = send(':DATA:WAVE:SCREen:CH{}?'.format(ch))
    length = int().from_bytes(rawdata[0:2],'little',signed=False)
    data = [[],[]] # array of datapoints, [0] is value, [1] is errorbar if available (when 600 points are returned)
    if (length == 300):
        for idx in range(4,len(rawdata),1):
            # take 1 bytes and convert these to signed integer
            point = int().from_bytes([rawdata[idx]],'little',signed=True);
            data[0].append(yscale*(point-yoffset)/25)  # vertical scale is 25/div
            data[1].append(0)  # no errorbar
    else:
        for idx in range(4,len(rawdata),2):
            # take 2 bytes and convert these to signed integer for upper and lower value
            lower = int().from_bytes([rawdata[idx]],'little',signed=True)
            upper = int().from_bytes([rawdata[idx+1]],'little',signed=True)
            data[0].append(yscale*(lower+upper-2*yoffset)/50)  # average of the two datapoints
            data[1].append(yscale*(upper-lower)/50)  # errorbar is delta between upper and lower
    #
    return data
#
def get_header():
    global dev
    # first 4 bytes indicate the number of data bytes following
    header = send(':DATA:WAVE:SCREen:HEAD?')
    header = header[4:].tobytes().decode('utf-8')
    return header
#
#
def Get_Data():
    global xscale, VBuffA, VBuffB, TRACESread, Header
    global CH1yscale, CH1yoffset, CH2yscale, CH2yoffset
    global Interp4Filter, InOffA, InOffB, InGainA, InGainB

    # Get the header and process it
    Header = yaml.safe_load(get_header())
    CH1yscale = float(Header["CHANNEL"][0]["PROBE"][0:-1]) * float(Header["CHANNEL"][0]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][0]["SCALE"][-2],1)
    CH1yoffset = int(Header["CHANNEL"][0]["OFFSET"])
    CH2yscale = float(Header["CHANNEL"][1]["PROBE"][0:-1]) * float(Header["CHANNEL"][1]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][1]["SCALE"][-2],1)
    CH2yoffset = int(Header["CHANNEL"][1]["OFFSET"])
    xscale = float(Header["TIMEBASE"]["SCALE"][0:-2]) / divfactor.get(Header["TIMEBASE"]["SCALE"][-2],1)

# Get data from instrument
    VBuff1 = get_data(1, CH1yscale, CH1yoffset)
    VBuff2 = get_data(2, CH2yscale, CH2yoffset)
##    TriggerStatus = send(":TRIGger: STATus?")
##    print(TriggerStatus)
##    if TriggerStatus == "TRIG" :
##        Is_Triggered = 1
##    else:
##        Is_Triggered = 0
#
    NoiseCH1 = numpy.array(VBuff1[1])
    NoiseCH2 = numpy.array(VBuff1[1])
    VBuff1 = numpy.array(VBuff1[0])
    VBuff2 = numpy.array(VBuff2[0])
    # Interpolate by 4
    VBuffA = [] # Clear the A array 
    VBuffB = [] # Clear the B array
    index = 0
    while index < len(VBuff1): # build arrays VBuffMA, VBuffMB, VBuffMC, VBuffMD
        pointer = 0
        while pointer < 4:
            VBuffA.append(VBuff1[index])
            VBuffB.append(VBuff2[index])
            pointer = pointer + 1
        index = index + 1
    VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
    VBuffA = numpy.convolve(VBuffA, Interp4Filter )
    #VBuffA = numpy.roll(VBuffA, -4)
    VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
    VBuffB = numpy.convolve(VBuffB, Interp4Filter )
    #VBuffB = numpy.roll(VBuffB, -4)
    VBuffA = (VBuffA[3:1203] - InOffA) * InGainA
    VBuffB = (VBuffB[3:1203] - InOffB) * InGainB
    TRACESread = 2
#
## try to connect to MP720781 Scope Meter
#
def ConnectDevice():
    global dev, cfg, untf, DevID, MaxSamples, AWGSAMPLErate, SAMPLErate
    global bcon, FWRevOne, HWRevOne, Header
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv
    global CHAsb, CHBsb, TMsb
    global TgInput, TgEdge, TRIGGERlevel, TRIGGERentry

    if DevID == "No Device" or DevID == "MP72":
        #
        # Setup instrument
        dev = usb.core.find(idVendor=0x5345, idProduct=0x1234, backend=be1 )

        if dev is None:
            raise ValueError('Device not found')
            exit()
        print( 'number of configurations: ',dev.bNumConfigurations)
        cfg=dev[0]
        print( "number of interfaces of config 0: ",cfg.bNumInterfaces)
        intf=cfg[0,0]
        print( "number of end points: ",intf.bNumEndpoints)
        usb.util.claim_interface(dev, intf)
        dev.set_configuration()
        Device = get_id()
        IDN = Device.split(',')
        DevID = IDN[2]
        print("Serial#: ", DevID)
        FWRevOne = IDN[3]
        print("Software Rev: ", FWRevOne) 
        HWRevOne = IDN[1]
        print("Model#: ", HWRevOne)
        #
        Header = yaml.safe_load(get_header())
        CH1Probe = Header["CHANNEL"][0]["PROBE"]
        CH1VRange = Header["CHANNEL"][0]["SCALE"]
        CH2Probe = Header["CHANNEL"][1]["PROBE"]
        CH2VRange = Header["CHANNEL"][1]["SCALE"]
        TimeDivStr = Header["TIMEBASE"]["SCALE"]
        TiggerLevel = Header["Trig"]["Items"]["Level"]
        TriggerEdge = Header["Trig"]["Items"]["Edge"]
        TriggerChannel = Header["Trig"]["Items"]["Channel"]
##        print("Channel 1 Probe: ", CH1Probe)
##        print("Channel 2 Probe: ", CH2Probe)
##        print("Channel 1 Range: ", CH1VRange)
##        print("Channel 2 Range: ", CH2VRange)
##        print("Horz Time per Div: ", TimeDiv)
        CHAsb.delete(0,"end")
        CHAsb.insert(0,CH1VRange)
        CHBsb.delete(0,"end")
        CHBsb.insert(0,CH2VRange)
        TMsb.delete(0,"end")
        TMsb.insert(0,TimeDivStr)
        TimeDiv = UnitConvert(TMsb.get())
        TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
        SAMPLErate = (300 / TimeSpan)*4 # interpolate samples by 4x
        if TriggerChannel == "CH1":
            TgInput.set(1)
        else:
            TgInput.set(2)
        if TriggerEdge == "RISE":
            TgEdge.set(0)
        else:
            TgEdge.set(1)
        TRIGGERlevel = UnitConvert(TiggerLevel)
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0,TRIGGERlevel)
# print(dev)
        bcon.configure(text="Conn", style="GConn.TButton")
#
# AWG Stuff
#
def SetAwgAmpl():
    global AWGAAmplEntry
    
    send(":FUNCtion:LOW " + ' {0:.3f} '.format(float(AWGAAmplEntry.get())))
#
def SetAwgOffset():
    global AWGAOffsetEntry

    send(":FUNCtion:HIGHt " + ' {0:.3f} '.format(float(AWGAOffsetEntry.get())))
#
def SetAwgFrequency():
    global AWGAFreqEntry

    FreqNum = UnitConvert(AWGAFreqEntry.get())
    send(":FUNCtion:FREQuency " + str(FreqNum)) # ' {0:.1f} '.format(float(AWGAFreqEntry.get())))
#
def SetAwgSymmetry():
    global V

    send(":FUNCtion:RAMP:SYMMetry " + str(int(AWGASymmetryEntry.get())))
#
def SetAwgDutyCycle():
    global AWGADutyCycleEntry

    send(":FUNCtion:PULSe:DTYCycle " + str(int(AWGADutyCycleEntry.get())))
#
def SetAwgWidth():
    global AWGAWidthEntry

    WidthNum = UnitConvert(AWGAWidthEntry.get())
    send(":FUNCtion:PULSe:WIDTh " + str(WidthNum))
#
def SetAwgA_Ampl(Ampl):

    if Ampl == 0:
        send(":CHANnel OFF")
    else:
        send(":CHANnel ON")
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
    SetAwgFrequency()
    SetAwgAmpl()
    SetAwgOffset()
    time.sleep(0.1)
#
# Trigger Stuff
#
def BSetTriggerSource():
    global TgInput

    if TgInput.get() == 1:
        send(":TRIGger:SINGle:SOURce CH1")
    if TgInput.get() == 2:
        send(":TRIGger:SINGle:SOURce CH2")
#
def BSetTrigEdge():
    global TgEdge
    
    if TgEdge.get() == 0:
        send(":TRIGger:SINGle:EDGe RISE")
    else:
        send(":TRIGger:SINGle:EDGe FALL")
#
def BTriggerMode(): 
    global TgInput, ana_str

    if (TgInput.get() == 0):
         #no trigger
        send(":TRIGger:SINGle:SWEep AUTO")
    elif (TgInput.get() == 1):
         #trigger source set to detector of analog in channels
         #
        send(":TRIGger:SINGle:SWEep NORMal")
    elif (TgInput.get() == 2):
        # trigger source set to detector of analog in channels
        # 
        send(":TRIGger:SINGle:SWEep SINGle")
## evalute trigger level entry string to a numerical value and set new trigger level     
def SendTriggerLevel():
    global TRIGGERlevel, TRIGGERentry, RUNstatus

    # evalute entry string to a numerical value
    # send(":TRIGger:SINGle:EDGe:LEVel 1.0")
    send(":TRIGger:SINGle:EDGe:LEVel "+ str(TRIGGERentry.get()))
    TRIGGERlevel = UnitConvert(TRIGGERentry.get())
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
    send(":HORizontal:OFFset " + str(HozOffset))
    
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
#
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TIMEdiv/HorzValue)
    send(":HORizontal:OFFset " + str(HozOffset))
    # prevent divide by zero error
## Set Hor time scale from entry widget
def SetSampleRate():
    global TimeDiv, TMsb, RUNstatus, Tdiv
    global TimeSpan, SAMPLErate, TIMEperDiv
    
    send(":HORIzontal:SCALe " + TMsb.get())
    TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
    SAMPLErate = (300 / TimeSpan)*4 # interpolate samples by 4x 
#    
def HCHAlevel():
    global CHAsb, RUNstatus, CH1vpdvLevel
    
    send(":CH1:SCALe " + str(CHAsb.get()))

def HCHBlevel():
    global CHBsb, RUNstatus, CH2vpdvLevel
    
    send(":CH2:SCALe " + str(CHBsb.get()))  
        
def HOffsetA(event):
    global CHAOffset, CHAVPosEntry, CH1vpdvLevel, RUNstatus

    NumberOfDiv = int(CHAOffset/CH1vpdvLevel)
    send(":CH1:OFFSet " + str(NumberOfDiv))

def HOffsetB(event):
    global CHBOffset, CHBVPosEntry, CH2vpdvLevel, RUNstatus

    NumberOfDiv = int(CHBOffset/CH2vpdvLevel)
    send(":CH2:OFFSet " + str(NumberOfDiv))
#
#
def CouplCHA():
    global CHAcoupl

    send(":CH1:COUPling " + CHAcoupl.get())
#
def CouplCHB():
    global CHBcoupl

    send(":CH2:COUPling " + CHBcoupl.get())
#
