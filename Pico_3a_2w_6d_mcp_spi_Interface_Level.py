#
# Hardware specific interface functions
# For Arduino pi pico Three analog + 2 AWG + 6 digital channel scope (12-2-2023)
# Written using Python version 3.10, Windows OS 
#
try:
    import serial
    import serial.tools.list_ports
except:
    root.update()
    showwarning("WARNING","Serial Library not installed?!")
    root.destroy()
    exit()
#
# adjust for your specific hardware by changing these values in the alice.init file
CHANNELS = 3 # Number of supported Analog input channels
AWGChannels = 2 # Number of supported Analog output channels
PWMChannels = 1 # Number of supported PWM output channels
DigChannels = 0 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 #
EnableAWGNoise = 0 #
UseSoftwareTrigger = 1
AllowFlashFirmware = 1
Tdiv.set(10)
AWG_Amp_Mode.set(0)
AWGPeakToPeak = 3.29
DevID = "Pico 3 mcp"
SerComPort = 'Auto'
TimeSpan = 0.01
ADC_Cal = 3.29
AWGRes = 4095 # For 8 bits, 4095 for 12 bits, 1023 for 10 bits
InterpRate = 4
EnableInterpFilter.set(1)
MaxSampleRate = SAMPLErate = 333333*InterpRate
ATmin = 8 # set minimum DAC update rate to 8 uSec
MaxAWGSampleRate = 1.0 / (ATmin / 1000000) # set to 1 / 8 uSec
AWGSampleRate = MaxAWGSampleRate
LSBsizeA =  LSBsizeB = LSBsizeC = LSBsize = ADC_Cal/4096.0
HardwareBuffer = 2048 # Max hardware waveform buffer size
MinSamples = 2048 # capture sample buffer size
AWGBuffLen = 2048 # Max DAC hardware waveform buffer size
Cycles = 1
SMPfft = MinSamples*InterpRate # Set FFT size based on fixed acquisition record length
#
VBuffA = numpy.ones(MinSamples*InterpRate)
VBuffB = numpy.ones(MinSamples*InterpRate)
VBuffC = numpy.ones(MinSamples*InterpRate)
VBuffD = numpy.ones(MinSamples*InterpRate)
VBuffG = numpy.ones(MinSamples*InterpRate)
MBuff = numpy.ones(MinSamples*InterpRate)
MBuffX = numpy.ones(MinSamples*InterpRate)
MBuffY = numpy.ones(MinSamples*InterpRate)
VmemoryA = numpy.ones(MinSamples*InterpRate) # The memory for averaging
VmemoryB = numpy.ones(MinSamples*InterpRate) # The memory for averaging
VmemoryC = numpy.ones(MinSamples*InterpRate)
VmemoryD = numpy.ones(MinSamples*InterpRate)
#
IACMString = "+1.65"
IA_Mode.set(1)
#
## hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, ser
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        ser.write(b'Gx\n') # Turn off AWG
        ser.write(b'sx\n') # turn off PWM
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig("alice-last-config.cfg")
        # May need to be changed for specific hardware port
        ser.close()
        # exit
    except:
        donothing()

    root.destroy()
    exit()
#
# Set Scope Sample Rate based on Horz Time Scale
#
def DummySetSampleRate():
    global TimeSpan, MaxSampleRate, SHOWsamples, InterpRate, Tdiv
    global TrigSource, TriggerEdge, TriggerInt, SAMPLErate, TimeDiv, ser

    TimeDiv = UnitConvert(TMsb.get())
#
def SetSampleRate():
    global TimeSpan, SHOWsamples, InterpRate, Tdiv
    global MaxSampleRate, SAMPLErate, TimeDiv, ser

    try:
        TimeDiv = UnitConvert(TMsb.get())
    except:
        pass
    #print("TimeDiv = ", TimeDiv)
    if TimeDiv < 0.000099:
        ser.write(b't3\n') # 90.909 KSPS
    elif TimeDiv > 0.000099 and TimeDiv < 0.000199:
        ser.write(b't3\n') # 90.909 KSPS
    elif TimeDiv > 0.000199 and TimeDiv < 0.0005:
        ser.write(b't3\n') # 90.909KSPS
    elif TimeDiv >= 0.0005 and TimeDiv < 0.001:
        ser.write(b't3\n') # 90.909 KSPS
    elif TimeDiv >= 0.001 and TimeDiv < 0.002:
        ser.write(b't8\n') # 62.5 KSPS
    elif TimeDiv >= 0.002 and TimeDiv < 0.005:
        ser.write(b't16\n') # 31.250 KSPS
    elif TimeDiv >= 0.005 and TimeDiv < 0.01:
        ser.write(b't32\n') # 15.625 KSPS
    elif TimeDiv >= 0.01 and TimeDiv < 0.02:
        ser.write(b't100\n') # 10 KSPS
    else:
        ser.write(b't200\n') # 5 KSPS
    #
    time.sleep(0.005)
    #
#
def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))
#
# Main function to request and receive a set of ADC samples
#
def Get_Data():
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global TgInput, VBuffA, VBuffB, VBuffC, VBuffD, VBuffG
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on, COLORtrace8
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    global TRIGGERentry, TRIGGERsample, SaveDig, CHANNELS, TRACESread

    # Get data from Pi Pico + MCP
    #
    SaveDig = False
    if D0_is_on or D1_is_on or D2_is_on or D3_is_on or D4_is_on or D5_is_on or D6_is_on:
        SaveDig = True
        Get_Dig()
        COLORtrace8 = "#800000"   # 80% red
    else:
        SaveDig = False
    #
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() == 0:
        TRACESread = 2 # A and B
        Get_Data_Two()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() == 0 and ShowC3_V.get() > 0:
        TRACESread = 2 # A and C
        Get_Data_Two()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        TRACESread = 2 # B and C
        Get_Data_Two()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() == 0 and ShowC3_V.get() == 0:
        TRACESread = 1 # A
        Get_Data_One()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() > 0 and ShowC3_V.get() == 0:
        TRACESread = 1 # B
        Get_Data_One()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() == 0 and ShowC3_V.get() > 0:
        TRACESread = 1 # C
        Get_Data_One()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        TRACESread = 3 # A and B and C
        Get_Data_Three()
    elif SaveDig:
        pass
    else:
        return
    # do external Gain / Offset calculations before software triggering
    if ShowC1_V.get() > 0:
        VBuffA = numpy.array(VBuffA)
        VBuffA = (VBuffA - InOffA) * InGainA
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        VBuffB = numpy.array(VBuffB)
        VBuffB = (VBuffB - InOffB) * InGainB
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        VBuffC = numpy.array(VBuffC)
        VBuffC = (VBuffC - InOffC) * InGainC
#
def Get_Buffer():
    global Wait, ser, MaxSampleRate, InterpRate, SAMPLErate
    global ABuff, iterCount, SampleTime, MinSamples, TRACESread
    
    time.sleep(Wait)
    ratestring = str(ser.readline())
    # print("Raw string ", ratestring)
    if "stReal=" in ratestring: #
        DTime = ratestring.replace("b'stReal=","")
        DTime = DTime.replace("\\\\","")
        DTime = DTime.replace("r","")
        DTime = DTime.replace("n","")
        DTime = DTime.replace("\\","")
        DTime = DTime.replace("'","")
        # print(DTime, UnitConvert(DTime)/MinSamples)
        SampleTime = (UnitConvert(DTime)/MinSamples) * 1.0e-6 # convert to uSec
        # set actual samplerate from returned time per sample
        MaxSampleRate = SAMPLErate = int((1.0/SampleTime)*InterpRate)
        # print("Sample Time: ", SampleTime)
        # print("Sample Rate = ", SAMPLErate )
    #
    #StartTime = time.time()
    VBuffRaw = []
    ABuff = []
    time.sleep(Wait*TRACESread)
    ### Wait to buffer enough samples to satisfy the entire frame
    # print("iterCount = ", iterCount)
    Count = 0
    Chunk = TRACESread * MinSamples
    ## 1 chan 324, 108, 36
    ## 2 chan 640, 320, 160
    ## 3,4 chan 500, 250
    ByTwo = 500
    ByFour = 250
    ByEight = 160
    if TRACESread == 2:
        ByTwo = 640
        ByFour = 320
        ByEight = 160
    if TRACESread > 1:
        Chunk = Chunk + MinSamples
    waiting0 = ser.in_waiting
    #print("Serial Length:", waiting0)
    while waiting0 >= 1:
        # print("Number Bytes waiting = ", waiting0)
        # read in chunks divisible by 3
        # Read an integer as two bytes, big-endian
        time.sleep(0.015)
        waiting0 = ser.in_waiting
        if waiting0 > Chunk:
            VBuffRaw = ser.read(Chunk)
            Count = Count + Chunk
        elif waiting0 > MinSamples:
            VBuffRaw = ser.read(MinSamples)
            Count = Count + MinSamples
        elif waiting0 > ByTwo:
            VBuffRaw = ser.read(ByTwo)
            Count = Count + ByTwo
        elif waiting0 > ByFour:
            VBuffRaw = ser.read(ByFour)
            Count = Count + ByFour
        elif waiting0 > ByEight:
            if TRACESread == 2:
                VBuffRaw = ser.read(ByEight)
                Count = Count + ByEight
            else:
                VBuffRaw = ser.read(waiting0)
                Count = Count + waiting0
        else:
            VBuffRaw = ser.read(waiting0)
            Count = Count + waiting0
        # if TRACESread == 4:
            # print("Count = ", Count)
        # print("Length AB: Raw: ", len(ABuff), len(VBuffRaw))
        index = 0
        while index < len(VBuffRaw):
            ABuff.append(VBuffRaw[index])
            index = index + 1
        # Count = Count + waiting0
        waiting0 = ser.in_waiting
        #print("Serial Length:", waiting0)
        # time.sleep(Wait)
        if Count >= iterCount: # Sample Buffer now full
            # print("Count = ", Count, "iterCount = ", iterCount)
            break
    #print("Frames = ", Frams)
    #EndTime = time.time()
    #Elapsed = EndTime - StartTime
    #print("Elapsed Time = ", Elapsed)
    # if TRACESread == 4:
    # print("received Bytes = ", Count)
    # print("Length: ", len(ABuff))
#
def Get_Dig():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global LoopBack, LBsb, InterpRate
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    SetSampleRate()
    Wait = 0.02
    #
    ser.write(b'0') # capture just dig channels
    #
    time.sleep(Wait)
    ratestring = str(ser.readline())
    # print("Raw string ", ratestring)
    if "stReal=" in ratestring: #
        DTime = ratestring.replace("b'stReal=","")
        DTime = DTime.replace("\\\\","")
        DTime = DTime.replace("r","")
        DTime = DTime.replace("n","")
        DTime = DTime.replace("\\","")
        DTime = DTime.replace("'","")
        # print(DTime, UnitConvert(DTime)/MinSamples)
        SampleTime = (UnitConvert(DTime)/MinSamples) * 1.0e-6 # convert to uSec
        # set actual samplerate from returned time per sample
        MaxSampleRate = SAMPLErate = int((1.0/SampleTime)*InterpRate)
        # print("Sample Time: ", SampleTime)
        # print("Sample Rate = ", SAMPLErate )
    # 
    iterCount = (MinSamples * 2) # 2 bytes for one channel
    #
    #StartTime = time.time()
    VBuffRaw = []
    ABuff = []
    time.sleep(Wait)
    ### Wait to buffer enough samples to satisfy the entire frame
    # print("iterCount = ", iterCount)
    Count = 0
    waiting0 = ser.in_waiting
    #print("Serial Length:", waiting0)
    while waiting0 >= 1:
        # print("Number Bytes waiting = ", waiting0)
        # read in chunks divisible by 3
        # Read an integer as two bytes, big-endian
        time.sleep(0.010)
        waiting0 = ser.in_waiting
        if waiting0 > MinSamples:
            VBuffRaw = ser.read(MinSamples)
            Count = Count + MinSamples
        elif waiting0 > 324:
            VBuffRaw = ser.read(324)
            Count = Count + 324
        elif waiting0 > 108:
            VBuffRaw = ser.read(108)
            Count = Count + 108
        elif waiting0 > 36:
            VBuffRaw = ser.read(36)
            Count = Count + 36
        else:
            VBuffRaw = ser.read(waiting0)
            Count = Count + waiting0
        # print("Count = ", Count)
        # print("Length AB: Raw: ", len(ABuff), len(VBuffRaw))
        index = 0
        while index < len(VBuffRaw):
            ABuff.append(VBuffRaw[index])
            index = index + 1
        # Count = Count + waiting0
        waiting0 = ser.in_waiting
        #print("Serial Length:", waiting0)
        # time.sleep(Wait)
        if Count >= iterCount: # Sample Buffer now full
            # print("Count = ", Count, "iterCount = ", iterCount)
            break
    #
    #EndTime = time.time()
    #Elapsed = EndTime - StartTime
    #print("Elapsed Time = ", Elapsed)
    # print("received Bytes = ", Count)
    # print("Length: ", len(ABuff))
    #
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    VBuffG = []
    # Interpolate 
    while index < len(ABuff): # build array 
        pointer = 0
        while pointer < InterpRate:
            VBuffG.append(ABuff[index])
            pointer = pointer + 1
        index = index + 1
    # Extract Digital buffers if needed
    VBuffG = numpy.array(VBuffG) * 1
    if SaveDig:
        VBuffG = VBuffG.astype(int)
        if D0_is_on:
            DBuff0 = VBuffG & 1
        if D1_is_on:
            DBuff1 = VBuffG & 2
            DBuff1 = DBuff1 / 2
        if D2_is_on:
            DBuff2 = VBuffG & 4
            DBuff2 = DBuff2 / 4
        if D3_is_on:
            DBuff3 = VBuffG & 8
            DBuff3 = DBuff3 / 8
        if D4_is_on:
            DBuff4 = VBuffG & 16
            DBuff4 = DBuff4 / 16
        #
    else:
        SaveDig = False
        DBuff0 = []
        DBuff1 = []
        DBuff2 = []
        DBuff3 = []
        DBuff4 = []
        DBuff5 = []
        DBuff6 = []
        DBuff7 = []
#
def Get_Data_One():
    global VBuffA, VBuffB, VBuffC, VBuffD, VBuff1
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global LoopBack, LBsb, TRACESread, Wait, iterCount
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    SetSampleRate()
    Wait = 0.02
    if SAMPLErate <= 4000:
        Wait = 0.08
    #
    if ShowC1_V.get() > 0:
        ser.write(b'A0\n') # capture on A1
    elif ShowC2_V.get() > 0:
        ser.write(b'A1\n') # capture on A2
    elif ShowC3_V.get() > 0:
        ser.write(b'A2\n') # capture on A3
    else:
        return
    ser.write(b'1') # capture one channel
    #
    iterCount = (MinSamples * 2) # 2 bytes for one channel
    #
    Get_Buffer()
    #
    VBuff1=[]
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    while index < MinSamples: # len(ABuff)-2:
        #Frams = Frams + 1
        # Get CH 1 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff1.append(data)
        index = index + 1
    #
    VBuffG=[]
    #
    # Interpolate data samples by 4X
    #
    index = 0
    if ShowC1_V.get() > 0:
        VBuffA=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffA = VBuffA[4:SHOWsamples+4]
        #
    elif ShowC2_V.get() > 0:
        VBuffB=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffB = VBuffB[4:SHOWsamples+4]
        #
    elif ShowC3_V.get() > 0:
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffC)
        if EnableInterpFilter.get() == 1:
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffC = VBuffC[4:SHOWsamples+4]
        #
    elif ShowC4_V.get() > 0:
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffD)
        if EnableInterpFilter.get() == 1:
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffD = VBuffD[4:SHOWsamples+4]
        #
    else:
        return
#
def Get_Data_Two():
    global VBuffA, VBuffB, VBuffC, VBuffD, ABuff
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC,  LSBsizeD
    global LoopBack, LBsb, Wait, iterCount
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    SetSampleRate()
    Wait = 0.015
    if SAMPLErate <= 4000:
        Wait = 0.08
    ### send command to readout data
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0: # capture on A1 and A2
        ser.write(b'A0\n') 
        ser.write(b'B1\n')
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0: # capture on A1 and A3
        ser.write(b'A0\n')
        ser.write(b'B2\n')
    elif ShowC1_V.get() > 0 and ShowC4_V.get() > 0: # capture on A1 and A4
        ser.write(b'A0\n') 
        ser.write(b'B3\n')
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on A2 and A3
        ser.write(b'A1\n') 
        ser.write(b'B2\n')
    elif ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on A2 and A4
        ser.write(b'A1\n') 
        ser.write(b'B3\n')
    elif ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A3 and A4
        ser.write(b'A2\n') 
        ser.write(b'B3\n')
    else:
        return
    ser.write(b'2') # capture two channels
    #
    iterCount = (MinSamples * 4) # 4 bytes for two channels
    #
    Get_Buffer()
    #
    VBuff1=[]
    VBuff2=[]
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    while index < MinSamples: # len(ABuff)-2:
        #Frams = Frams + 1
        # Get CH 1 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff1.append(data)
        index = index + 1
    index = index + MinSamples # skip ahead MinSamples
    while index < 3 * MinSamples:
        # Get CH 2 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff2.append(data)
        index = index + 1
    #
    #print("Frames = ", Frams)
    #
    VBuffG=[]
    #
    # Interpolate data samples by 4X
    #
    index = 0
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0: # capture on A and B
        VBuffA=[]
        VBuffB=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffB.append(float(samp) * LSBsizeB)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffA = VBuffA[4:SHOWsamples+4]
            VBuffB = VBuffB[4:SHOWsamples+4]
        #
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0: # capture on A and C
        VBuffA=[]
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffA = VBuffA[4:SHOWsamples+4]
            VBuffC = VBuffC[4:SHOWsamples+4]
        #
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on B and C
        VBuffB=[]
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffB = VBuffB[4:SHOWsamples+4]
            VBuffC = VBuffC[4:SHOWsamples+4]
        #
    elif ShowC1_V.get() > 0 and ShowC4_V.get() > 0: # capture on A and D
        VBuffA=[]
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffA = VBuffA[4:SHOWsamples+4]
            VBuffD = VBuffD[4:SHOWsamples+4]
        #
    elif ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on B and D
        VBuffB=[]
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff2[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffB = VBuffB[4:SHOWsamples+4]
            VBuffD = VBuffD[4:SHOWsamples+4]
        #
    elif ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on C and D
        VBuffC=[]
        VBuffD=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffC.append(float(samp) * LSBsizeC)
                samp = VBuff2[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffC)
        if EnableInterpFilter.get() == 1:
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffC = VBuffC[4:SHOWsamples+4]
            VBuffD = VBuffD[4:SHOWsamples+4]
        #
    else:
        return
#    
def Get_Data_Three():
    global VBuffA, VBuffB, VBuffC, VBuffD, ABuff
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC
    global LoopBack, LBsb, Wait, iterCount
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    SetSampleRate()
    Wait = 0.015
    if SAMPLErate <= 4000:
        Wait = 0.08
    # 
    # send command to readout data
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on A1 A2 and A3
        ser.write(b'A0\n') 
        ser.write(b'B1\n')
        ser.write(b'C2\n')
    elif ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on A1 A2 and A4
        ser.write(b'A0\n') 
        ser.write(b'B1\n')
        ser.write(b'C3\n')
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A2 A3 and A4
        ser.write(b'A1\n') 
        ser.write(b'B2\n')
        ser.write(b'C3\n')
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A1 A3 and A4
        ser.write(b'A0\n') 
        ser.write(b'B2\n')
        ser.write(b'C3\n')
    else:
        #print("none of the cases found?")
        return
    time.sleep(0.015)
    ser.write(b'3') # capture three channels
    #
    iterCount = (MinSamples * 6) # 6 bytes for three channels
    #
    Get_Buffer()
    #
    VBuff1=[]
    VBuff2=[]
    VBuff3=[]
    #
    waiting0 = ser.in_waiting
    if waiting0 > 0:
        # print("Serial Length:", waiting0)
        dump = ser.read(waiting0)
    #Frams = 0
    index = 0
    while index < MinSamples: # len(ABuff)-2:
        #Frams = Frams + 1
        # Get CH 1 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff1.append(data)
        index = index + 1
    index = index + MinSamples # skip ahead MinSamples
    while index < 3 * MinSamples:
        # Get CH 2 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff2.append(data)
        index = index + 1
    index = index + MinSamples # skip ahead MinSamples
    while index < 5 * MinSamples:
        # Get CH 3 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+ MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff3.append(data)
        index = index + 1
    #
    #print("Frames = ", Frams)
    #
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0: # capture on A B and C
        VBuffA=[]
        VBuffB=[]
        VBuffC=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff3[index]
                VBuffC.append(float(samp) * LSBsizeC)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffA = VBuffA[4:SHOWsamples+4]
            VBuffB = VBuffB[4:SHOWsamples+4]
            VBuffC = VBuffC[4:SHOWsamples+4]
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC4_V.get() > 0: # capture on A B and D
        VBuffA=[]
        VBuffB=[]
        VBuffD=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff3[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffA = VBuffA[4:SHOWsamples+4]
            VBuffB = VBuffB[4:SHOWsamples+4]
            VBuffD = VBuffD[4:SHOWsamples+4]
    if ShowC2_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on B C and D
        VBuffB=[]
        VBuffC=[]
        VBuffD=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                samp = VBuff3[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffB = numpy.pad(VBuffB, (4, 0), "edge")
            VBuffB = numpy.convolve(VBuffB, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffB = VBuffB[4:SHOWsamples+4]
            VBuffC = VBuffC[4:SHOWsamples+4]
            VBuffD = VBuffD[4:SHOWsamples+4]
    if ShowC1_V.get() > 0 and ShowC3_V.get() > 0 and ShowC4_V.get() > 0: # capture on A B and D
        VBuffA=[]
        VBuffC=[]
        VBuffD=[]
        #
        # Interpolate data samples by 4X
        #
        index = 0
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                samp = VBuff3[index]
                VBuffD.append(float(samp) * LSBsizeD)
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffA)
        if EnableInterpFilter.get() == 1:
            VBuffA = numpy.pad(VBuffA, (4, 0), "edge")
            VBuffA = numpy.convolve(VBuffA, Interp4Filter )
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffD = numpy.pad(VBuffD, (4, 0), "edge")
            VBuffD = numpy.convolve(VBuffD, Interp4Filter )
            VBuffA = VBuffA[4:SHOWsamples+4]
            VBuffC = VBuffC[4:SHOWsamples+4]
            VBuffD = VBuffD[4:SHOWsamples+4]
#
# Hardware Help
#
def PrintID():
    global ser
    
    ser.write(b'I\n') # request board ID
    time.sleep(0.05)
    #print("sent I, wating for response")
    if ser.in_waiting > 0:
        IDstring = str(ser.readline())
        ID = IDstring.replace("b'","")
        ID = ID.replace("\\\\","")
        ID = ID.replace("r","")
        ID = ID.replace("n","")
        ID = ID.replace("\\","")
        ID = ID.replace("'","")
        print("ID string ", ID)
#
def SetBufferLength(NewLength):
    global ser, MinSamples, MaxSamples, InterpRate, HardwareBuffer

    if NewLength > HardwareBuffer:
        NewLength = HardwareBuffer
    MinSamples = NewLength
    MaxSamples = MinSamples * InterpRate
    ## send Scope Buffer Length
    SendStr = 'b' + str(MinSamples) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    # ser.write(b'b1024\n')  
    time.sleep(0.005)
    #print("set Scope Samples: ", MinSamples)
#
# try to connect to Arduino Pi Pico board
#
def ConnectDevice():
    global SerComPort, DevID, MaxSamples, SAMPLErate, MinSamples, AWGSampleRate
    global bcon, FWRevOne, HWRevOne, MaxSampleRate, MaxAWGSampleRate, ser, SHOWsamples
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv, ATmin
    global CHAsb, CHBsb, TMsb, LSBsizeA, LSBsizeB, ADC_Cal, LSBsize
    global d0btn, d1btn, d2btn, d3btn, d4btn, d5btn, d6btn, d7btn

    # print("SerComPort: ", SerComPort)
    if DevID == "No Device" or DevID == "Pico 3 mcp":
        #
        if SerComPort == 'Auto':
            ports = serial.tools.list_ports.comports()
            for port in ports: # ports:
                # looking for this ID: USB\VID_2E8A&PID_000A
                if "VID:PID=2E8A:000A" in port[2]:
                    print("Found: ", port[0])
                    SerComPort = port[0]
        # Setup instrument connection
        print("Trying to open ", SerComPort)
        ser = serial.Serial(SerComPort)  # open serial port
        if ser is None:
            print('Device not found!')
            Bcloseexit()
            #exit()
        #
        ser.baudrate = 2000000 # Dummy number USB runs at max supported speed
#
        ser.write(b'I\n') # request board ID
        time.sleep(0.005)
        IDstring = str(ser.readline())
        ID = IDstring.replace("b'","")
        ID = ID.replace("\\\\","")
        ID = ID.replace("r","")
        ID = ID.replace("n","")
        ID = ID.replace("\\","")
        ID = ID.replace("'","")
        print("ID string ", ID)
        #
        ser.write(b'V\n') # Read Bacl VDD (.3.) supply voltage
        time.sleep(0.005)
        VDDstring = str(ser.readline())
        # print("VDD string ", VDDstring)
        if "V=" in VDDstring: #
            VDD = VDDstring.replace("b'V=","")
            VDD = VDD.replace("\\\\","")
            VDD = VDD.replace("r","")
            VDD = VDD.replace("n","")
            VDD = VDD.replace("\\","")
            VDD = VDD.replace("'","")
            Vsys = (int(VDD) * LSBsize) * 3.0 # 1/3 voltage divider
            print("Board Vsys = ", Vsys)
        #
        ser.write(b't3\n') # send Scope sample time in uSec
        time.sleep(0.005)
        print("set dt: 3 uSec")
        MaxSampleRate = SAMPLErate = 333333*InterpRate
        #
        SendStr = 'T' + str(ATmin) + '\n'
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        # ser.write(b'T8\n') # send AWG sample time in uSec
        time.sleep(0.005)
        print("set at: ", ATmin , " uSec")
        AWGSampleRate = MaxAWGSampleRate = 1.0 / (ATmin / 1000000)
        #
        ser.write(b'Gx\n') # default with both AWG off
        ser.write(b'gx\n') 
        ## send Scope Buffer Length
        SendStr = 'b' + str(MinSamples) + '\n'
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        # ser.write(b'b1024\n')  
        time.sleep(0.005)
        print("set Scope Samples: ", MinSamples)
        #
        #
        ser.write(b'N1024\n') # send AWG A Buffer Length
        ser.write(b'M1024\n') # send AWG B Buffer Length 
        time.sleep(0.005)
        print("set AWG Samples: 1024")
        #
        # ser.write(b'p500000\n')
        ser.write(b'R0\n') # default with AWG reset off
        ser.write(b'r0\n') # default with AWG pointer at loc 0
        #
        ser.write(b'Sx\n') # turn off AWG A by default
        MaxSamples = 4096 # assume 4X interpolation
#
        print("Get a sample: ")
        Get_Data() # grap a check set of samples
        print("After Interp ", len(VBuffA), len(VBuffB))
        SHOWsamples = len(VBuffA)
        return(True) # return a logical true if sucessful!
    else:
        return(False)
#
def UpdateFirmware():
    global ser, Sucess, bcon

    if askyesno("Load Firmware?", "Do You Wish to load firmware on this board?"):
        try:
            ser.baudrate = 1200 # Opening serial port at 1200 Baud for a short while will reset board
            time.sleep(0.05)
            if ser.in_waiting > 0:
                IDstring = str(ser.readline()) # read something
                print(IDstring)
            time.sleep(0.05)
            ser.close()
            Sucess = False
            bcon.configure(text="Recon", style="RConn.TButton")
        except:
            pass
        # if this worked a USB drive window should open.
#
# AWG Stuff
#
def AWGASendWave(AWG3):
    global ser, AWGARecLength, AWGBuffLen, AWGRes
    global AWGAAmplvalue, AWGAOffsetvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # scale values to send to 0 to 255 8 bits
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    MinCode = int((AWGAAmplvalue / AWGPeakToPeak) * AWGRes)
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGRes:
        MinCode = AWGRes
    MaxCode = int((AWGAOffsetvalue / AWGPeakToPeak) * AWGRes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGRes:
        MaxCode = AWGRes
    # print("MaxCode = ", MaxCode, "MinCode = ", MinCode)
    # Scale to high and low voltage values
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1)
    #
    AWGARecLength = len(AWG1)
    if AWGARecLength > AWGBuffLen:
        AWGARecLength = AWGBuffLen
    if len(AWG1) < AWGBuffLen:
        # ser.write(b'B1024\n') # send AWG Buffer Length
        SendStr = 'N' + str(len(AWG1)) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'N' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    #AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGARecLength:
        data = AWG1[index]
        # send buffer index and waveform sample data
        SendStr = 'L' + str(index) + 'D' + str(data) + '\n'
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
#
##    
def AWGBSendWave(AWG3):
    global ser, AWGBLastWave, AWGBRecLength, AWGBuffLen, AWGRes
    global AWGBAmplvalue, AWGBOffsetvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # AWG3 = numpy.roll(AWG3, -68)
    AWGBLastWave = numpy.array(AWG3)
    AWG3 = numpy.array(AWG3) * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    MinCode = int((AWGBAmplvalue / AWGPeakToPeak) * AWGRes)
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGRes:
        MinCode = AWGRes
    MaxCode = int((AWGBOffsetvalue / AWGPeakToPeak) * AWGRes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGRes:
        MaxCode = AWGRes
    #
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1)
    #
    AWGBRecLength = len(AWG1)
    if AWGBRecLength > AWGBuffLen:
        AWGBRecLength = AWGBuffLen
    if len(AWG1) < AWGBuffLen:
        SendStr = 'M' + str(len(AWG1)) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'M' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    #AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGBRecLength:
        data = AWG1[index]
        #
        SendStr = 'l' + str(index) + 'D' + str(data) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
#
#
def BAWGSync():
    global AWGSync

    if AWGSync.get() > 0:
        ser.write(b'R1\n') # turn on sync
    else:
        ser.write(b'R0\n') # turn off sync
#
def SetAwgSampleRate():
    global AWGAFreqEntry, AWGBFreqEntry, FSweepMode, MaxAWGSampleRate
    global AWGBuffLen, AWGSampleRate, AWGBuffLen, MaxRepRate

    BAWGAFreq()
    # BAWGBFreq()

    MaxRepRate = numpy.ceil(MaxAWGSampleRate / AWGBuffLen)
    FreqA = UnitConvert(AWGAFreqEntry.get())
##    FreqB = UnitConvert(AWGBFreqEntry.get())
##    if FreqB < FreqA:
##        FreqA = FreqB
    Cycles = 1
    #print("MaxRepRate = ", MaxRepRate)
    #print("FreqA = ", FreqA)
    # if FSweepMode.get() == 1: # If doing a frequency sweep only make new AWG A sine wave
    if FreqA < MaxRepRate:
        CycFrac = FreqA/MaxRepRate
        #print("Cycles = ", CycFrac)
        if CycFrac > 0.9:
            CycFrac = 0.9
        FreqA = FreqA * CycFrac
# Set the AWG buffer Rep rate (Freq for one cycle of buffer)
    SetAwgSampleFrequency(FreqA)
    AWGRepRate = FreqA
    # AWGSampleRate = FreqA * AWGBuffLen
        # AWGSampleRate = FreqB * MaxSamples
    # 
#
def SetAwgSampleFrequency(FreqANum):
    global AWGBuffLen, AWGSampleRate, MaxAWGSampleRate, ATmin
    #
    NewSampleRate = FreqANum * AWGBuffLen # Samples per second
    if NewSampleRate > MaxAWGSampleRate:
        NewSampleRate = MaxAWGSampleRate
    NewAT = int(1000000/NewSampleRate) # in uSec
    if NewAT < ATmin:
        NewAT = ATmin
    if NewAT > 500:
        NewAT = 500
    SendStr = 'T' + str(NewAT) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    # print(SendByt)
    ser.write(SendByt) #
    AWGSampleRate = int(1000000/NewAT)
    # print("AWGSampleRate = ", AWGSampleRate)
#
# for built in firmware waveforms...
#
def SetAwgA_Ampl(Ampl): # used to toggle on / off AWG output
    global ser, AwgBOnOffBt, AwgaOnOffLb, AwgbOnOffLb

    #AwgBOnOffBt.config(state=DISABLED)
    #AwgaOnOffLb.config(text="AWG Output ")
    #AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        ser.write(b'Gx\n')
    else:
        ser.write(b'Go\n')
#
def SetAwgB_Ampl(Ampl): # used to toggle on / off AWG output
    global ser, AwgBOnOffBt, AwgAOnOffBt, AwgaOnOffLb, AwgbOnOffLb

    #AwgBOnOffBt.config(state=DISABLED)
    #AwgaOnOffLb.config(text="AWG Output ")
    #AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        ser.write(b'gx\n')
    else:
        AwgAOnOffBt.config(text='ON', style="Run.TButton")
        ser.write(b'go\n')
#
## Make the current selected AWG waveform
#
##AwgString1 = "Sine"
##AwgString2 = "Triangle"
##AwgString3 = "Ramp Up"
##AwgString4 = "Ramp Down"
##AwgString5 = "Stair Up"
##AwgString6 = "Stair Down"
##AwgString7 = "Stair Up-Down"
AwgString9 = "Cosine"
AwgString10 = "Full Wave Sine"
AwgString11 = "Half Wave Sine"
AwgString12 = "Fourier Series"
AwgString13 = "Schroeder Chirp"
AwgString14 = "Sine Power Pulse"

#
## Make or update the current selected AWG waveform
def MakeAWGwaves(): # re make awg waveforms in case something changed
    global AWGAShape, AWGAShapeLabel, AWGBShape, AWGBShapeLabel
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGASymmetryEntry, AWGADutyCycleEntry
    global AWGAAmplvalue, AWGBOffsetvalue, AWGBAmplvalue, AWGBOffsetvalue, AWGAFreqvalue
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBSymmetryEntry, AWGBDutyCycleEntry
    global FSweepMode, MaxSampleRate, BisCompA
    global AwgString1, AwgString2, AwgString3, AwgString4, AwgString5, AwgString6
    global AwgString7, AwgString8, AwgString9, AwgString10, AwgString11, AwgString12
    global AwgString13, AwgString14, AwgString15, AwgString16
    
    if FSweepMode.get() == 1: # If doing a frequency sweep only make new AWG A sine wave
        if AWGAShape.get()==1:
            AWGAMakeSine()
            AWGAShapeLabel.config(text = AwgString1) # change displayed value
        return
# Shape list        
    if AWGAShape.get()== 0:
        AWGAMakeDC()
        AWGAShapeLabel.config(text = "DC") # change displayed value
    elif AWGAShape.get()==1:
        AWGAMakeSine()
        AWGAShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGAShape.get()==2:
        AWGAMakeSquare()
        AWGAShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGAShape.get()==3:
        AWGAMakeTriangle()
        AWGAShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGAShape.get()==4:
        AWGAMakePulse()
        AWGAShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGAShape.get()==5:
        AWGAMakeRampDn()
        AWGAShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGAShape.get()==6:
        AWGAMakeRampUp()
        AWGAShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGAShape.get()==7:
        AWGAMakeStair()
        AWGAShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGAShape.get()==8:
        AWGAMakeSinc()
        AWGAShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGAShape.get()==9:
        AWGAMakeSine()
        AWGAShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGAShape.get()==10:
        AWGAMakeFullWaveSine()
        AWGAShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGAShape.get()==11:
        AWGAMakeHalfWaveSine()
        AWGAShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGAShape.get()==12:
        AWGAMakeFourier()
        AWGAShapeLabel.config(text = AwgString12) # change displayed value
    elif AWGAShape.get()==13:
        SetAwgSampleRate()
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
        NrTones = int(eval(AWGADutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGASendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGAShapeLabel.config(text = AwgString13) # change displayed value
    elif AWGAShape.get()==14:
        SetAwgSampleRate()
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
        Power = int(eval(AWGADutyCycleEntry.get()))
        Power = Power / 100.0
        ampl = 1
        AWGASendWave(SinePower(100, Power, 180, ampl))
        AWGAShapeLabel.config(text = AwgString14) # change displayed value
    else:
        AWGAShapeLabel.config(text = "Other Shape") # change displayed value
#
    if BisCompA.get() == 1:
        SetBCompA()
#
    if AWGBShape.get() == 0:
        AWGBMakeDC()
        AWGBShapeLabel.config(text = "DC") # change displayed value
    elif AWGBShape.get() == 1:
        AWGBMakeSine()
        AWGBShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGBShape.get() == 2:
        AWGBMakeSquare()
        AWGBShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGBShape.get() == 3:
        AWGBMakeTriangle()
        AWGBShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGBShape.get() == 4:
        AWGBMakePulse()
        AWGBShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGBShape.get()==5:
        AWGBMakeRampDn()
        AWGBShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGBShape.get()==6:
        AWGBMakeRampUp()
        AWGBShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGBShape.get()==7:
        AWGBMakeStair()
        AWGBShapeLabel.config(text = AwgString7) # change displayed value
    elif AWGBShape.get()==8:
        AWGBMakeSinc()
        AWGBShapeLabel.config(text = AwgString8) # change displayed value
    elif AWGBShape.get()==9:
        AWGBMakeSine()
        AWGBShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGBShape.get()==10:
        AWGBMakeFullWaveSine()
        AWGBShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGBShape.get()==11:
        AWGBMakeHalfWaveSine()
        AWGBShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGBShape.get()==12:
        AWGBMakeFourier()
        AWGBShapeLabel.config(text = AwgString12) # change displayed value
    elif AWGBShape.get()==13:
        SetAwgSampleRate()
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
        AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
        NrTones = int(eval(AWGBDutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGBSendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGBShapeLabel.config(text = AwgString13) # change displayed value
    else:
        AWGBShapeLabel.config(text = "Other Shape") # change displayed value
#
    time.sleep(0.01)
#
# Hardware Specific PWM control functions
#
def PWM_On_Off():
    global PWM_is_on, ser

    if PWM_is_on:
        #print("Set pwm on")
        ser.write(b'so\n')
    else:
        #print("Set pwm off")
        ser.write(b'sx\n')
#
def UpdatePWM():
    global PWMDivEntry, PWMWidthEntry, PWMLabel, ser

    PWMLabel.config(text = "PWM Frequency")

    FreqValue = int(UnitConvert(PWMDivEntry.get()))
    #PeriodValue = int(( 133e6 / 256 ) / FreqValue)
    #print("FreqValue = ", FreqValue, "PeriodValue = ",PeriodValue)
    ByteStr = 'p' + str(FreqValue) + "\n"
    SendByt = ByteStr.encode('utf-8')
    ser.write(SendByt)
    time.sleep(0.1)
    
    DutyCycle = int(PWMWidthEntry.get())
    #WidthFraction = float((DutyCycle/100.0))
    #Width = int(PeriodValue * WidthFraction)
    ByteStr = 'm' + str(DutyCycle) + "\n"
    SendByt = ByteStr.encode('utf-8')
    ser.write(SendByt)
    time.sleep(0.1)
#
# Hardware Specific Trigger functions
#
def SendTriggerLevel():
    global TRIGGERlevel, ser, RUNstatus, AWGPeakToPeak
    # Min and Max trigger level specific to hardware
    if TRIGGERlevel > 4.0:
        TRIGGERlevel = 4.0
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0, ' {0:.2f} '.format(4.0))
    if TRIGGERlevel < 0.0:
        TRIGGERlevel = 0.0
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0, ' {0:.2f} '.format(0.0))
# Adjust trigger level.
# representa a 8-bit number (0-255) sent to DAC

# Set Horz possition from entry widget
def SetHorzPoss():
    global HozPossentry, ser

    HzSteps = int(float(HozPossentry.get()))
    Hz_Value = 511-HzSteps
    if Hz_Value > 256:
        T_High = 1
        T_Low = Hz_Value - 256
    else:
        T_High = 0
        T_Low = Hz_Value
#
# Set Internal / External triggering bits
def BTrigIntExt():
    global TgSource, TriggerInt

    if TgSource.get() == 0:
        TriggerInt = 0x00 # bit 7 0x00 = Internal
    if TgSource.get() == 1:
        TriggerInt = 0x80 # bit 7 0x80 = External
# Set Triggering source bits
def BSetTriggerSource():
    global TgInput, TrigSource, TriggerInt

    if TgInput.get() == 1:
        TrigSource = 0x00 # bit 4 0x00 = Channel A
    if TgInput.get() == 2:
        TrigSource = 0x10 # bit 4 0x10 = Channel B
    if TgInput.get() == 0:
        TriggerInt = 0x40 # bit 6 0x40 No Triggers (free-run)?
# Set Trigger edge bits
def BSetTrigEdge():
    global TgEdge, TriggerEdge
    
    if TgEdge.get() == 0:
        TriggerEdge = 0x00 # bit 5 0x00 = Rising Edge
    else:
        TriggerEdge = 0x20 # bit 5 0x20 = Falling Edge

