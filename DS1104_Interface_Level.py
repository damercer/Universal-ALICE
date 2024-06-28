#
# Hardware specific interface functions
# For VEVOR (Owon) SDS1104 Scope (1-6-2024)
# Written using Python version 3.10, Windows OS 
#
try:
    import usb.core
    import usb.util
    import usb.control
    from usb.backend import libusb0, libusb1, openusb # , IBackend
    be0, be1 = libusb0.get_backend(), libusb1.get_backend()
    be3 = openusb.get_backend()
except:
    root.update()
    showwarning("WARNING","Pyusb not installed?!")
    root.destroy()
    exit()
Voltdiv.set(8)
Tdiv.set(15)
ZeroGrid.set(-7.5)
TimeDiv = 0.0002
import yaml
#
# adjust for your specific hardware by changing these values
DevID = "DS1104"
TimeSpan = 0.001
CHvpdiv = ("1.0mV", "2.0mV", "5.0mV", "10.0mV", "20.0mV", "50.0mV", "100mV", "200mV",
           "500mV", "1.0", "2.0","5.0", "10.0", "20.0", "50.0")
CHANNELS = 4 # Number of supported Analog input channels
# set trace colors to match scope screen
COLORtrace4 = "#00ff00"   # 100% green
COLORtrace3 = "#ff8000"   # 100% orange
COLORtrace2 = "#00ffff"   # 100% cyan
COLORtrace1 = "#ffff00"   # 100% yellow
COLORtraceR4 = "#008000"   # 50% green
COLORtraceR3 = "#905000"   # 50% orange
COLORtraceR2 = "#008080"   # 50% cyan
COLORtraceR1 = "#808000"   # 50% yellow
#
AWGChannels = 0 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 0 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 # 1
EnableOhmMeter = 0
EnableDmmMeter = 0
EnableDigIO = 0
UseSoftwareTrigger = 0
AllowFlashFirmware = 0
HardwareBuffer = 1520 # Max hardware waveform buffer size
MinSamples = 1520 # capture sample buffer size
InterpRate = 1
EnableInterpFilter.set(0)
SMPfft = InterpRate * MinSamples # Set FFT size based on fixed acquisition record length
VBuffA = numpy.ones(MinSamples*InterpRate)
VBuffB = numpy.ones(MinSamples*InterpRate)
VBuffC = numpy.ones(MinSamples*InterpRate)
VBuffD = numpy.ones(MinSamples*InterpRate)
# VBuffG = numpy.ones(MinSamples*InterpRate)
MBuff = numpy.ones(MinSamples*InterpRate)
MBuffX = numpy.ones(MinSamples*InterpRate)
MBuffY = numpy.ones(MinSamples*InterpRate)
VmemoryA = numpy.ones(MinSamples*InterpRate) # The memory for averaging
VmemoryB = numpy.ones(MinSamples*InterpRate) # The memory for averaging
VmemoryC = numpy.ones(MinSamples*InterpRate)
VmemoryD = numpy.ones(MinSamples*InterpRate)
#
## Hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, core, ana_out
    
    RUNstatus.set(0)
    Closed = 1
    ResetColors()
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
# USB communications with instrument
#
def send(cmd):
    global dev, WAddr, RAddr
    # address taken from results of print(dev):   ENDPOINT 0x1: Bulk OUT
    dev.write(WAddr,cmd) # 0x03
    # address taken from results of print(dev):   ENDPOINT 0x81: Bulk IN
    result = (dev.read(RAddr,100000,1000)) # 0x81
    return result

def get_id():
    global dev, MinSamples
    # returns a character string <Manufacturer>,<model>,<serial number>,X.XX.XX
    return str(send('*IDN?').tobytes().decode('utf-8'))
#
def get_data(ch, yscale, yoffset):
    global dev, MinSamples
    # first 4 bytes indicate the number of data bytes following
    rawdata = send(':DATA:WAVE:SCREen:CH{}?'.format(ch))
    length = int().from_bytes(rawdata[0:2],'little',signed=False)
    # print("Length = ", length)
    data = [] # array of datapoints, [0] is value, [1] is errorbar if available (when 600 points are returned)
    if (length == MinSamples):
        print("No Error Bar")
        for idx in range(4,len(rawdata),1):
            # take 1 bytes and convert these to signed integer
            point = int().from_bytes([rawdata[idx]],'little',signed=True);
            data.append(yscale*(point-yoffset)/25)  # vertical scale is 25/div
            # data[1].append(0)  # no errorbar
    else:
        idx = 4
        while idx < len(rawdata):
            # take 2 bytes and convert these to signed integer for upper and lower value
            lower = int().from_bytes([rawdata[idx]],'little',signed=True)
            upper = int().from_bytes([rawdata[idx+1]],'little',signed=True)
            # First lower byte seems to be a "Noise" adder ?
            # Second upper Byte is Waveform Data
            Temp = float(upper*1.0) # + float(lower/256.0)
            data.append((yscale*Temp/25)-(yscale*yoffset/50))
            #
            idx = idx + 2
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
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global xscale, VBuffA, VBuffB, VBuffC, VBuffD, TRACESread, Header, EnableInterpFilter
    global CH1yscale, CH1yoffset, CH2yscale, CH2yoffset
    global Interp4Filter, InOffA, InOffB, InGainA, InGainB
    global InOffC, InOffD, InGainC, InGainD, Header, TimeDiv
    global SHOWsamples, MinSamples, InterpRate, SAMPLErate, Tdiv

    # Get the header and process it
    Header = yaml.safe_load(get_header())
    CH1yscale = float(Header["CHANNEL"][0]["PROBE"][0:-1]) * float(Header["CHANNEL"][0]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][0]["SCALE"][-2],1)
    CH1yoffset = int(Header["CHANNEL"][0]["OFFSET"])
    CH2yscale = float(Header["CHANNEL"][1]["PROBE"][0:-1]) * float(Header["CHANNEL"][1]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][1]["SCALE"][-2],1)
    CH2yoffset = int(Header["CHANNEL"][1]["OFFSET"])
    CH3yscale = float(Header["CHANNEL"][2]["PROBE"][0:-1]) * float(Header["CHANNEL"][2]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][2]["SCALE"][-2],1)
    CH3yoffset = int(Header["CHANNEL"][2]["OFFSET"])
    CH4yscale = float(Header["CHANNEL"][3]["PROBE"][0:-1]) * float(Header["CHANNEL"][3]["SCALE"][0:-2]) / divfactor.get(Header["CHANNEL"][3]["SCALE"][-2],1)
    CH4yoffset = int(Header["CHANNEL"][3]["OFFSET"])
    TimeDivStr = Header["TIMEBASE"]["SCALE"]
    SAMPLERATEStr = Header["SAMPLE"]["SAMPLERATE"]
##    SRate = SAMPLERATEStr.replace("S/s","")
##    SRate = SRate.replace("(","")
##    SRate = SRate.replace(")","")
##    SAMPLErate = UnitConvert(SRate)
    TimeDiv = UnitConvert(TimeDivStr)
    TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
    TraceRate = (MinSamples / TimeSpan) # Screen display samples per second
    SAMPLErate = TraceRate
    # xscale = float(Header["TIMEBASE"]["SCALE"][0:-2]) / divfactor.get(Header["TIMEBASE"]["SCALE"][-2],1)
    #print("CH1yscale = ", CH1yscale)
    #print("CH1yoffset = ", CH1yoffset)
##    TriggerStatus = send(":TRIGger: STATus?")
##    print(TriggerStatus)
##    if TriggerStatus == "TRIG" :
##        Is_Triggered = 1
##    else:
##        Is_Triggered = 0
#    
# Get data from instrument
    TRACESread = 0
    if ShowC1_V.get() > 0:
        VBuff1 = get_data(1, CH1yscale, CH1yoffset)
        VBuff1 = numpy.array(VBuff1)
        VBuffA = [] # Clear the A array
        index = 0
        while index < len(VBuff1): # build arrays
            pointer = 0
            while pointer < InterpRate:
                VBuffA.append(VBuff1[index])
                pointer = pointer + 1
            index = index + 1
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffA = numpy.roll(VBuffA, -4)
        VBuffA = numpy.array(VBuffA)
        # do external Gain / Offset calculations?
        VBuffA = (VBuffA - InOffA) * InGainA
        SHOWsamples = len(VBuffA)
        TRACESread = TRACESread + 1
#
    if ShowC2_V.get() > 0:
        VBuff1 = get_data(2, CH2yscale, CH2yoffset)
        VBuff1 = numpy.array(VBuff1)
        VBuffB = [] # Clear the B array
        index = 0
        while index < len(VBuff1): # build arrays
            pointer = 0
            while pointer < InterpRate:
                VBuffB.append(VBuff1[index])
                pointer = pointer + 1
            index = index + 1
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffB = numpy.roll(VBuffB, -4)
            VBuffB = numpy.array(VBuffB)
        VBuffB = numpy.array(VBuffB)
        # do external Gain / Offset calculations?
        VBuffB = (VBuffB - InOffB) * InGainB
        SHOWsamples = len(VBuffB)
        TRACESread = TRACESread + 1
#
    if ShowC3_V.get() > 0:
        VBuff1 = get_data(3, CH3yscale, CH3yoffset)
        VBuff1 = numpy.array(VBuff1)
        VBuffC = [] # Clear the C array
        index = 0
        while index < len(VBuff1): # build arrays
            pointer = 0
            while pointer < InterpRate:
                VBuffC.append(VBuff1[index])
                pointer = pointer + 1
            index = index + 1
        if EnableInterpFilter.get() == 1:
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffC = numpy.roll(VBuffC, -4)
        VBuffC = numpy.array(VBuffC)
        # do external Gain / Offset calculations?
        VBuffC = (VBuffC - InOffC) * InGainC
        SHOWsamples = len(VBuffC)
        TRACESread = TRACESread + 1
#
    if ShowC4_V.get() > 0:
        VBuff1 = get_data(4, CH4yscale, CH4yoffset)
        VBuff1 = numpy.array(VBuff1)
        VBuffD = [] # Clear the B array
        index = 0
        while index < len(VBuff1): # build arrays
            pointer = 0
            while pointer < InterpRate:
                VBuffD.append(VBuff1[index])
                pointer = pointer + 1
            index = index + 1
        if EnableInterpFilter.get() == 1:
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffD = numpy.roll(VBuffD, -4)
            VBuffD = numpy.array(VBuffD)
        VBuffD = numpy.array(VBuffD)
        # do external Gain / Offset calculations?
        VBuffD = (VBuffD - InOffD) * InGainD
        SHOWsamples = len(VBuffD)
        TRACESread = TRACESread + 1
#
## try to connect to SDS1104 Scope Meter
#
def ConnectDevice():
    global dev, cfg, untf, DevID, MaxSamples, AWGSAMPLErate, SAMPLErate
    global bcon, FWRevOne, HWRevOne, Header, MinSamples, InterpRate
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv, TimeDivStr
    global CH3Probe, CH4Probe, CH3VRange, CH4VRange
    global CHAsb, CHBsb, CHCsb, CHDsb, TMsb, Header, WAddr, RAddr
    global TgInput, TgEdge, TRIGGERlevel, TRIGGERentry
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2
    global COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4

    # set trace colors to match scope screen
    COLORtrace4 = "#00ff00"   # 100% green
    COLORtrace3 = "#ff8000"   # 100% orange
    COLORtrace2 = "#00ffff"   # 100% cyan
    COLORtrace1 = "#ffff00"   # 100% yellow
    COLORtraceR4 = "#008000"   # 50% green
    COLORtraceR3 = "#905000"   # 50% orange
    COLORtraceR2 = "#008080"   # 50% cyan
    COLORtraceR1 = "#808000"   # 50% yellow
    #
    if DevID == "No Device" or DevID == "DS1104":
        #
        # Setup instrument
        dev = usb.core.find(idVendor=0x5345, idProduct=0x1234, backend=be1 )

        if dev is None:
            raise ValueError('Device not found')
            exit()
        # print(dev)
        print( 'number of configurations: ',dev.bNumConfigurations)
        cfg=dev[0]
        print( "number of interfaces of config 0: ",cfg.bNumInterfaces)
        # print(cfg)
        intf=cfg[0,0]
        print( "number of end points: ",intf.bNumEndpoints)
        # print( "End points: ",intf.iInterface)
        # print(intf)
        endpt1=intf[0]
        endpt2=intf[1]
        print("Read EndpointAddress = ", endpt1.bEndpointAddress)
        RAddr = endpt1.bEndpointAddress
        print("Write EndpointAddress = ", endpt2.bEndpointAddress)
        WAddr = endpt2.bEndpointAddress
        usb.util.claim_interface(dev, intf)
        dev.set_configuration()
        Device = get_id()
        print("DevID = ", Device)
        IDN = Device.split(',')
        SerNum = IDN[2]
        print("Serial#: ", DevID)
        FWRevOne = IDN[3]
        print("Software Rev: ", FWRevOne) 
        DevID = IDN[1]
        print("Model#: ", DevID)
        #
        Header = yaml.safe_load(get_header())
        # print(Header)
        CH1Probe = Header["CHANNEL"][0]["PROBE"]
        CH1VRange = Header["CHANNEL"][0]["SCALE"]
        CH1VOffset = float(Header["CHANNEL"][0]["OFFSET"])/50.0
        CH2Probe = Header["CHANNEL"][1]["PROBE"]
        CH2VRange = Header["CHANNEL"][1]["SCALE"]
        CH2VOffset = float(Header["CHANNEL"][1]["OFFSET"])/50.0
        CH3Probe = Header["CHANNEL"][2]["PROBE"]
        CH3VRange = Header["CHANNEL"][2]["SCALE"]
        CH3VOffset = float(Header["CHANNEL"][2]["OFFSET"])/50.0
        CH4Probe = Header["CHANNEL"][3]["PROBE"]
        CH4VRange = Header["CHANNEL"][3]["SCALE"]
        CH4VOffset = float(Header["CHANNEL"][3]["OFFSET"])/50.0
        TimeDivStr = Header["TIMEBASE"]["SCALE"]
        SAMPLERATEStr = Header["SAMPLE"]["SAMPLERATE"]
        MinSamples = Header["SAMPLE"]['DATALEN']
        TriggerLevel = Header["Trig"]["Items"]["Level"]
        TriggerEdge = Header["Trig"]["Items"]["Edge"]
        TriggerChannel = Header["Trig"]["Items"]["Channel"]
        print("CH1Probe = ", CH1Probe)
        print("CH1VRange = ", CH1VRange)
        print("CH1VOffset = ", CH1VOffset)
        print("CH2Probe = ", CH2Probe)
        print("CH2VRange = ", CH2VRange)
        print("CH2VOffset = ", CH2VOffset)
        print("Waveform Length = ", MinSamples)
#
        TimeDiv = UnitConvert(TimeDivStr)
        TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
        SRate = SAMPLERATEStr.replace("S/s","")
        SRate = SRate.replace("(","")
        SRate = SRate.replace(")","")
        TraceRate = (MinSamples / TimeSpan) # Screen display samples per second
        print("TimeDiv = ",TimeDiv)
        print("TimeSpan = ", TimeSpan)
        print("TraceRate = ", TraceRate)
        print("Time Base = ", UnitConvert(SRate))
        SAMPLErate = TraceRate # UnitConvert(SRate)
        print("SAMPLErate = ", SAMPLErate)
        TRIGGERlevel = UnitConvert(TriggerLevel)
        if TriggerChannel == "CH1":
            TgInput.set(1)
        else:
            TgInput.set(2)
        if TriggerEdge == "RISE":
            TgEdge.set(0)
        else:
            TgEdge.set(1)
        # bcon.configure(text="Conn", style="GConn.TButton")
        return(True) # return a logical true if sucessful!
    else:
        return(False)
#
# Trigger Stuff
#
def BSetTriggerSource():
    global TgInput

    if TgInput.get() == 1:
        send(":TRIGger:SINGle:SOURce CH1")
    if TgInput.get() == 2:
        send(":TRIGger:SINGle:SOURce CH2")
    if TgInput.get() == 3:
        send(":TRIGger:SINGle:SOURce CH3")
    if TgInput.get() == 4:
        send(":TRIGger:SINGle:SOURce CH4")
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
    TRIGGERlevel = UnitConvert(TRIGGERentry.get())
    # send(":TRIGger:SINGle:EDGe:LEVel 1.0")
    send(":TRIGger:SINGle:EDGe:LEVel "+ str(TRIGGERentry.get()))
    
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
    HozOffset = HorzValue * 1.0
    send(":HORizontal:OFFset " + str(HozOffset))
    
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
#
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TIMEdiv/HorzValue)
    #send(":HORizontal:OFFset " + str(HozOffset))
    # prevent divide by zero error
## Set Hor time scale from entry widget
def SetSampleRate():
    global TimeDiv, TMsb, RUNstatus, Tdiv, MinSamples
    global TimeSpan, SAMPLErate, TIMEperDiv
    
    send(":HORIzontal:SCALe " + TMsb.get())
    TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
    TraceRate = (MinSamples / TimeSpan) # Screen display samples per second
    SAMPLErate = TraceRate
#    
def HCHAlevel():
    global CHAsb, RUNstatus, CH1vpdvLevel
    
    send(":CH1:SCALe " + str(CHAsb.get()))

def HCHBlevel():
    global CHBsb, RUNstatus, CH2vpdvLevel
    
    send(":CH2:SCALe " + str(CHBsb.get()))  
#    
def HCHClevel():
    global CHCsb, RUNstatus, CH3vpdvLevel
    
    send(":CH3:SCALe " + str(CHBsb.get()))

def HCHDlevel():
    global CHDsb, RUNstatus, CH4vpdvLevel
    
    send(":CH4:SCALe " + str(CHDsb.get()))  
                
def HOffsetA():
    global CHAOffset, CHAVPosEntry, CH1vpdvLevel, RUNstatus

    NumberOfDiv = -1.0*(CHAOffset/CH1vpdvLevel)
    # print("NumberOfDiv = ", NumberOfDiv)
    send(":CH1:OFFSet " + str(NumberOfDiv))

def HOffsetB():
    global CHBOffset, CHBVPosEntry, CH2vpdvLevel, RUNstatus

    NumberOfDiv = -1.0*(CHBOffset/CH2vpdvLevel)
    send(":CH2:OFFSet " + str(NumberOfDiv))
    
def HOffsetC():
    global CHCOffset, CHCVPosEntry, CH3vpdvLevel, RUNstatus

    NumberOfDiv = -1.0*(CHCOffset/CH3vpdvLevel)
    # print("NumberOfDiv = ", NumberOfDiv)
    send(":CH3:OFFSet " + str(NumberOfDiv))

def HOffsetD():
    global CHDOffset, CHDVPosEntry, CH4vpdvLevel, RUNstatus

    NumberOfDiv = -1.0*(CHDOffset/CH4vpdvLevel)
    send(":CH4:OFFSet " + str(NumberOfDiv))
#
##
def CouplCHA():
    global CHAcoupl

    send(":CH1:COUPling " + CHAcoupl.get())
#
def CouplCHB():
    global CHBcoupl

    send(":CH2:COUPling " + CHBcoupl.get())
#
def CouplCHC():
    global CHCcoupl

    send(":CH3:COUPling " + CHCcoupl.get())
#
def CouplCHD():
    global CHDcoupl

    send(":CH4:COUPling " + CHDcoupl.get())
#
def HardwareSelectChannels():
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V

    if ShowC1_V.get() > 0:
        send(":CH1:DISPlay ON")
    else:
        send(":CH1:DISPlay OFF")
    if ShowC2_V.get() > 0:
        send(":CH2:DISPlay ON")
    else:
        send(":CH2:DISPlay OFF")
    if ShowC3_V.get() > 0:
        send(":CH3:DISPlay ON")
    else:
        send(":CH3:DISPlay OFF")
    if ShowC4_V.get() > 0:
        send(":CH4:DISPlay ON")
    else:
        send(":CH4:DISPlay OFF")
