#
# Hardware specific interface functions
# For Arduino ItsyBitsy M4 3 Scope + 2 AWG + 1 digital channel scope (1-18-2024)
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
DigChannels = 6 # Number of supported Dig channels
LogicChannels = 1 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 #
EnableAWGNoise = 0 #
AllowFlashFirmware = 1
Tdiv.set(10)
AWG_Amp_Mode.set(0)
AWGPeakToPeak = 3.28
ADC_Cal = 3.28
ScopeRes = 4096.0
LSBsizeA =  LSBsizeB = LSBsizeC = LSBsize = ADC_Cal/ScopeRes
Rint = 2.0E7 # ~2 Meg Ohm internal resistor to ground
AWGARes = 4095 # 1023 For 10 bits, 4095 for 12 bits, 255 for 8 bits
AWGBRes = 4095
DevID = "SparkFun Thing Plus 3"
SerComPort = 'Auto'
TimeSpan = 0.01
InterpRate = 4
EnableInterpFilter.set(1)
MaxSampleRate = SAMPLErate = 25000*InterpRate
AWGSampleRate = 100000
PhaseOffset = 12.5
MinSamples = 2048 # Max sample buffer size
AWGBuffLen = 2048
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
#
## hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, ser, Sucess
    
    RUNstatus.set(0)
    Closed = 1
    #
    if Sucess:
        try:
            ser.write(b'Gx\n') # Turn off AWG
            # ser.write(b'sx\n') # turn off PWM
            # try to write last config file, Don't crash if running in Write protected space
            BSaveConfig("alice-last-config.cfg")
            # May need to be changed for specific hardware port
            ser.close()
            # exit
        except:
            donothing()
    else:
        BSaveConfig("alice-last-config.cfg")
        try:
            ser.close()
        except:
            pass
#
    root.destroy()
    exit()
#
# Set Scope Sample Rate based on Horz Time Scale
#
def SetSampleRate():
    global TimeSpan, SHOWsamples, InterpRate, Tdiv
    global MaxSampleRate, SAMPLErate, TimeDiv, ser, TRACESread

    try:
        TimeDiv = UnitConvert(TMsb.get())
    except:
        pass
    #print("TimeDiv = ", TimeDiv)
    if TimeDiv < 0.000099:
        if TRACESread == 1:
            ser.write(b't10\n') # 100 KSPS
        elif TRACESread == 2:
            ser.write(b't15\n') # 62.5 KSPS
        else:
            ser.write(b't20\n') # 40 KSPS
    elif TimeDiv > 0.000099 and TimeDiv < 0.000199:
        if TRACESread == 1:
            ser.write(b't10\n') # 100 KSPS
        elif TRACESread == 2:
            ser.write(b't15\n') # 62.5 KSPS
        else:
            ser.write(b't20\n') # 40 KSPS
    elif TimeDiv > 0.000199 and TimeDiv < 0.0005:
        if TRACESread == 1:
            ser.write(b't10\n') # 100 KSPS
        elif TRACESread == 2:
            ser.write(b't15\n') # 62.5 KSPS
        else:
            ser.write(b't20\n') # 40 KSPS
    elif TimeDiv >= 0.0005 and TimeDiv < 0.001:
        if TRACESread == 1:
            ser.write(b't10\n') # 100 KSPS
        elif TRACESread == 2:
            ser.write(b't15\n') # 62.5 KSPS
        else:
            ser.write(b't20\n') # 40 KSPS
    elif TimeDiv >= 0.001 and TimeDiv < 0.002:
        ser.write(b't20\n') # 100 KSPS
    elif TimeDiv >= 0.002 and TimeDiv < 0.005:
        ser.write(b't32\n') # 40 KSPS
    elif TimeDiv >= 0.005 and TimeDiv < 0.01:
        ser.write(b't64\n') # 15.625 KSPS
    elif TimeDiv >= 0.01 and TimeDiv < 0.02:
        ser.write(b't128\n') # 10 KSPS
    elif TimeDiv >= 0.02 and TimeDiv < 0.05:
        ser.write(b't256\n') # 10 KSPS
    else:
        ser.write(b't512\n') # 5 KSPS
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
    global TgInput, VBuffA, VBuffB, VBuffC, VBuffG
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    global TRIGGERentry, TRIGGERsample, SaveDig, CHANNELS, TRACESread

    # Get data from QT Py
    #
    SaveDig = False
    if D0_is_on or D1_is_on or D2_is_on or D3_is_on or D4_is_on or D5_is_on or D6_is_on:
        SaveDig = True
    else:
        SaveDig = False
    #
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() == 0:
        TRACESread = 2
        SetSampleRate()
        Get_Data_Two()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() == 0 and ShowC3_V.get() > 0:
        TRACESread = 2
        SetSampleRate()
        Get_Data_Two()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        TRACESread = 2
        SetSampleRate()
        Get_Data_Two()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() == 0 and ShowC3_V.get() == 0:
        TRACESread = 1
        SetSampleRate()
        Get_Data_One()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() > 0 and ShowC3_V.get() == 0:
        TRACESread = 1
        SetSampleRate()
        Get_Data_One()
    elif ShowC1_V.get() == 0 and ShowC2_V.get() == 0 and ShowC3_V.get() > 0:
        TRACESread = 1
        SetSampleRate()
        Get_Data_One()
    elif ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        TRACESread = 3
        SetSampleRate()
        Get_Data_Three()
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
    if ShowC4_V.get() > 0 and CHANNELS >= 4:
        VBuffD = numpy.array(VBuffD)
        VBuffD = (VBuffD - InOffD) * InGainD
    # Find trigger sample point if necessary
    # print("Array Len ",len(VBuffA), "SHOWsamples ", SHOWsamples)
    LShift = 0
    if TgInput.get() == 1 and ShowC1_V.get() > 0:
        FindTriggerSample(VBuffA)
    if TgInput.get() == 2 and ShowC2_V.get() > 0:
        FindTriggerSample(VBuffB)
    if TgInput.get() == 3 and ShowC3_V.get() > 0:
        FindTriggerSample(VBuffC)
    if TgInput.get() > 4:
        TRIGGERentry.delete(0,"end")
        TRIGGERentry.insert(0,0.5)
        if TgInput.get() == 5:
            FindTriggerSample(DBuff0)
        if TgInput.get() == 6:
            FindTriggerSample(DBuff1)
        if TgInput.get() == 7:
            FindTriggerSample(DBuff2)
        if TgInput.get() == 8:
            FindTriggerSample(DBuff3)
        if TgInput.get() == 9:
            FindTriggerSample(DBuff4)
        if TgInput.get() == 10:
            FindTriggerSample(DBuff5)
        if TgInput.get() == 11:
            FindTriggerSample(DBuff6)
    if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
        LShift = 0 - TRIGGERsample
        if ShowC1_V.get() > 0:
            VBuffA = numpy.roll(VBuffA, LShift)
        if ShowC2_V.get() > 0:
            VBuffB = numpy.roll(VBuffB, LShift+2)
        if ShowC3_V.get() > 0:
            VBuffC = numpy.roll(VBuffC, LShift+2)
        if SaveDig:
            VBuffG = numpy.roll(VBuffG, LShift)
            if D0_is_on:
                DBuff0 = numpy.roll(DBuff0, LShift)
            if D1_is_on:
                DBuff1 = numpy.roll(DBuff1, LShift)
            if D2_is_on:
                DBuff2 = numpy.roll(DBuff2, LShift)
            if D3_is_on:
                DBuff3 = numpy.roll(DBuff3, LShift)
            if D4_is_on:
                DBuff4 = numpy.roll(DBuff4, LShift)
            if D5_is_on:
                DBuff5 = numpy.roll(DBuff5, LShift)
            if D6_is_on:
                DBuff6 = numpy.roll(DBuff6, LShift)
            if D7_is_on:
                DBuff7 = numpy.roll(DBuff7, LShift)
    else:
        # VBuffA = numpy.roll(VBuffA, -2)
        VBuffA = numpy.roll(VBuffA, -8)
        VBuffB = numpy.roll(VBuffB, -7)
        VBuffC = numpy.roll(VBuffC, -6)
#
def Get_Data_One():
    global VBuffA, VBuffB, VBuffC, VBuffG
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    Wait = 0.02
    if SAMPLErate <= 4000:
        Wait = 0.08
    # 
    ## send command to readout data
    if ShowC1_V.get() > 0:
        ser.write(b'0') # capture on A and D4
    elif ShowC2_V.get() > 0:
        ser.write(b'5') # capture on B and D4
    elif ShowC3_V.get() > 0:
        ser.write(b'6') # capture on C and D4
    else:
        return
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
    iterCount = (MinSamples * 3) # 3 bytes for one channel plus digital byte
    #
    #StartTime = time.time()
    VBuffRaw = []
    ABuff = []
    VBuff1=[]
    VBuff2=[]
    VBuff3=[]
    BuffD=[]
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
        time.sleep(0.040)
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
    while index < MinSamples: # len(ABuff)-2:
        #Frams = Frams + 1
        # Get CH 1 data
        inputHigh = ABuff[index]
        inputLow = ABuff[index+MinSamples]
        data = ((inputHigh*256)+inputLow)
        VBuff1.append(data)
        index = index + 1
    index = 2 * MinSamples # skip ahead MinSamples
    while index < 3*MinSamples:
        # Get digital inputs data
        data = ABuff[index]
        BuffD.append(data)
        index = index + 1  
    #
    #print("Frames = ", Frams)
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
                if SaveDig:
                    VBuffG.append(BuffD[index])
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
                if SaveDig:
                    VBuffG.append(BuffD[index])
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
                if SaveDig:
                    VBuffG.append(BuffD[index])
                pointer = pointer + 1
            index = index + 1
        SHOWsamples = len(VBuffB)
        if EnableInterpFilter.get() == 1:
            VBuffC = numpy.pad(VBuffC, (4, 0), "edge")
            VBuffC = numpy.convolve(VBuffC, Interp4Filter )
            VBuffC = VBuffC[4:SHOWsamples+4]
        #
    else:
        return
    VBuffG = numpy.array(VBuffG) * 1
    # Extract Digital buffers if needed
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
        if D5_is_on:
            DBuff5 = VBuffG & 32
            DBuff5 = DBuff5 / 32
        if D6_is_on:
            DBuff6 = VBuffG & 64
            DBuff6 = DBuff6 / 64
        if D7_is_on:
            DBuff7 = VBuffG & 128
            DBuff7 = DBuff7 / 128
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
def Get_Data_Two():
    global VBuffA, VBuffB, VBuffC, VBuffG
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    Wait = 0.02
    if SAMPLErate <= 4000:
        Wait = 0.08
    # 
    ## send command to readout data
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0:
        ser.write(b'1') # capture on A and B and D4
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0:
        ser.write(b'2') # capture on A and C and D4
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        ser.write(b'3') # capture on B and C and D4
    else:
        return
    #
    time.sleep(0.010)
    ratestring = str(ser.readline())
    #print("Raw string ", ratestring)
    if "stReal=" in ratestring: #
        DTime = ratestring.replace("b'stReal=","")
        DTime = DTime.replace("\\\\","")
        DTime = DTime.replace("r","")
        DTime = DTime.replace("n","")
        DTime = DTime.replace("\\","")
        DTime = DTime.replace("'","")
        # print(DTime)
        SampleTime = (UnitConvert(DTime)/MinSamples) * 1.0e-6 # convert to uSec
        # SampleTime = UnitConvert(DTime) * 1.0e-6 # convert to uSec
        # set actual samplerate from returned time per sample
        MaxSampleRate = SAMPLErate = (1.0/SampleTime)*InterpRate
        # print("Sample Time: ", SampleTime)
        # print("Sample Rate = ", SAMPLErate )
    # 
    iterCount = (MinSamples * 5) # 5 bytes for two channels plus digital byte
    #
    #StartTime = time.time()
    VBuffRaw = []
    ABuff = []
    VBuff1=[]
    VBuff2=[]
    VBuff3=[]
    BuffD=[]
    time.sleep(Wait*2)
    ### Wait to buffer enough samples to satisfy the entire frame
    # print("iterCount = ", iterCount)
    Count = 0
    waiting0 = ser.in_waiting
    while waiting0 >= 1:
        # print("Number Bytes waiting = ", waiting0)
        # read in chunks divisible by 5
        # Read an integer as two bytes, big-endian
        time.sleep(0.040)
        waiting0 = ser.in_waiting
        Chunk = 3 * MinSamples
        if waiting0 > Chunk:
            VBuffRaw = ser.read(Chunk)
            Count = Count + Chunk
        elif waiting0 > MinSamples:
            VBuffRaw = ser.read(MinSamples)
            Count = Count + MinSamples
        elif waiting0 > 640:
            VBuffRaw = ser.read(640)
            Count = Count + 640
        elif waiting0 > 320:
            VBuffRaw = ser.read(320)
            Count = Count + 320
        elif waiting0 > 160:
            VBuffRaw = ser.read(160)
            Count = Count + 160
        else:
            VBuffRaw = ser.read(waiting0)
            Count = Count + waiting0
        #print("Count = ", Count)
        #print("Length AB: Raw: ", len(ABuff), len(VBuffRaw))
        index = 0
        while index < len(VBuffRaw):
            ABuff.append(VBuffRaw[index])
            index = index + 1
        # Count = Count + waiting0
        waiting0 = ser.in_waiting
        # print("Serial Length:", waiting0)
        # time.sleep(Wait)
        if Count >= iterCount: # Sample Buffer now full
            # print("Count = ", Count, "iterCount = ", iterCount)
            break
    #
    #EndTime = time.time()
    #Elapsed = EndTime - StartTime
    #print("Elapsed Time = ", Elapsed)
    #print("received Bytes = ", Count)
    #print("Length: ", len(ABuff))
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
        # Get digital inputs data
        data = ABuff[index]
        BuffD.append(data)
        index = index + 1
    #
    #print("Frames = ", Frams)
    #
    VBuffG=[]
    #
    # Interpolate data samples by 4X
    #
    index = 0
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0:
        VBuffA=[]
        VBuffB=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffB.append(float(samp) * LSBsizeB)
                if SaveDig:
                    VBuffG.append(BuffD[index])
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
    elif ShowC1_V.get() > 0 and ShowC3_V.get() > 0:
        VBuffA=[]
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffA.append(float(samp) * LSBsizeA)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                if SaveDig:
                    VBuffG.append(BuffD[index])
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
    elif ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        VBuffB=[]
        VBuffC=[]
        while index < len(VBuff1): # build array 
            pointer = 0
            while pointer < 4:
                samp = VBuff1[index]
                VBuffB.append(float(samp) * LSBsizeB)
                samp = VBuff2[index]
                VBuffC.append(float(samp) * LSBsizeC)
                if SaveDig:
                    VBuffG.append(BuffD[index])
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
    else:
        return
    VBuffG = numpy.array(VBuffG) * 1
    # Extract Digital buffers if needed
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
        if D5_is_on:
            DBuff5 = VBuffG & 32
            DBuff5 = DBuff5 / 32
        if D6_is_on:
            DBuff6 = VBuffG & 64
            DBuff6 = DBuff6 / 64
        if D7_is_on:
            DBuff7 = VBuffG & 128
            DBuff7 = DBuff7 / 128
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
def Get_Data_Three():
    global VBuffA, VBuffB, VBuffC, VBuffG
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global LSBsizeA, LSBsizeB, LSBsizeC
    global MaxSampleRate, SAMPLErate, EnableInterpFilter
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff, MinSamples, Interp4Filter
    global SaveDig, D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    
    #
    Wait = 0.02
    if SAMPLErate <= 4000:
        Wait = 0.08
    # 
    ## send command to readout data
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and ShowC3_V.get() > 0:
        ser.write(b'4') # capture on A, B and C and D4
    else:
        return
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
        # print(DTime)
        # SampleTime = UnitConvert(DTime) * 1.0e-6 # convert to uSec
        SampleTime = (UnitConvert(DTime)/MinSamples) * 1.0e-6 # convert to uSec
        # set actual samplerate from returned time per sample
        MaxSampleRate = SAMPLErate = (1.0/SampleTime)*InterpRate
        # print("Sample Time: ", SampleTime)
        # print("Sample Rate = ", SAMPLErate )
    # 
    iterCount = (MinSamples * 7) # 7 bytes for two channels plus digital byte
    #
    #StartTime = time.time()
    VBuffRaw = []
    ABuff = []
    VBuff1=[]
    VBuff2=[]
    VBuff3=[]
    BuffD=[]
    time.sleep(Wait*3)
    ### Wait to buffer enough samples to satisfy the entire frame
    # print("iterCount = ", iterCount)
    Count = 0
    waiting0 = ser.in_waiting
    while waiting0 >= 1:
        # print("Number Bytes waiting = ", waiting0)
        # read in chunks divisible by 7
        # Read an integer as two bytes, big-endian
        time.sleep(0.040)
        waiting0 = ser.in_waiting
        Chunk = 4 * MinSamples
        if waiting0 > Chunk:
            VBuffRaw = ser.read(Chunk)
            Count = Count + Chunk
        elif waiting0 > MinSamples:
            VBuffRaw = ser.read(MinSamples)
            Count = Count + MinSamples
        elif waiting0 > 500:
            VBuffRaw = ser.read(500)
            Count = Count + 500
        elif waiting0 > 250:
            VBuffRaw = ser.read(250)
            Count = Count + 250
        else:
            VBuffRaw = ser.read(waiting0)
            Count = Count + waiting0
        #print("Count = ", Count)
        #print("Length AB: Raw: ", len(ABuff), len(VBuffRaw))
        index = 0
        while index < len(VBuffRaw):
            ABuff.append(VBuffRaw[index])
            index = index + 1
        # Count = Count + waiting0
        waiting0 = ser.in_waiting
        # print("Serial Length:", waiting0)
        # time.sleep(Wait)
        if Count >= iterCount: # Sample Buffer now full
            # print("Count = ", Count, "iterCount = ", iterCount)
            break
    #
    #EndTime = time.time()
    #Elapsed = EndTime - StartTime
    #print("Elapsed Time = ", Elapsed)
    #print("received Bytes = ", Count)
    #print("Length: ", len(ABuff))
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
    index = index + MinSamples # skip ahead MinSamples
    while index < 7 * MinSamples:
        # Get digital inputs data
        data = ABuff[index]
        BuffD.append(data)
        index = index + 1
    #
    #print("Frames = ", Frams)
    #
    VBuffA=[]
    VBuffB=[]
    VBuffC=[]
    VBuffG=[]
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
            if SaveDig:
                VBuffG.append(BuffD[index])
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
    #
    VBuffG = numpy.array(VBuffG) * 1
    # Extract Digital buffers if needed
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
        if D5_is_on:
            DBuff5 = VBuffG & 32
            DBuff5 = DBuff5 / 32
        if D6_is_on:
            DBuff6 = VBuffG & 64
            DBuff6 = DBuff6 / 64
        if D7_is_on:
            DBuff7 = VBuffG & 128
            DBuff7 = DBuff7 / 128
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
def SetBufferLength(NewLength):
    global ser, MinSamples

    MinSamples = NewLength

    ## send Scope Buffer Length
    SendStr = 'b' + str(MinSamples) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    # ser.write(b'b1024\n')  
    time.sleep(0.005)
    #print("set Scope Samples: ", MinSamples)
#
# Hardware Help
#
## try to connect to Arduino XIAO board
#
def ConnectDevice():
    global SerComPort, DevID, MaxSamples, SAMPLErate, MinSamples, AWGSampleRate
    global bcon, FWRevOne, HWRevOne, MaxSampleRate, ser, SHOWsamples
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv
    global CHAsb, CHBsb, TMsb, LSBsizeA, LSBsizeB, ADC_Cal, LSBsize
    global d0btn, d1btn, d2btn, d3btn, d4btn, d5btn, d6btn, d7btn

    # print("SerComPort: ", SerComPort)
    if DevID == "No Device" or DevID == "SparkFun Thing Plus 3":
        #
        if SerComPort == 'Auto':
            ports = serial.tools.list_ports.comports()
            for port in ports: # ports:
                # looking for this ID: USB\VID:PID=1B4F:F016
                if "VID:PID=1B4F:F016" in port[2]:
                    print("Found: ", port[0])
                    SerComPort = port[0]
        # Setup instrument connection
        print("Trying to open ", SerComPort)
        try:
            ser = serial.Serial(SerComPort)  # open serial port
        except:
            return
        if ser is None:
            print('Device not found!')
            return
            # Bcloseexit()
            # exit()
        #
        ser.baudrate = 2000000 # Dummy number USB runs at max supported speed
#
        #print("sending I")
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
            if ID != "SpakFu Thig Plus Scope 3.0":
                showwarning("WARNING","Board firmware does not match this interface. Switch boards or interface software.")
            #
            ser.write(b't25\n') # send Scope sample time in uSec
            time.sleep(0.005)
            print("set dt: 25 uSec")
            MaxSampleRate = SAMPLErate = 40000*InterpRate
            #
            ser.write(b'T10\n') # send AWG sample time in uSec
            time.sleep(0.005)
            print("set at: 10 uSec")
            AWGSampleRate = 100000
            ## send Scope Buffer Length
            SendStr = 'b' + str(MinSamples) + '\n'
            # print(SendStr)
            SendByt = SendStr.encode('utf-8')
            ser.write(SendByt)
            # ser.write(b'b1024\n')  
            time.sleep(0.005)
            print("set Scope Samples: ", MinSamples)
            #
            ser.write(b'N1024\n') # send AWG A Buffer Length
            ser.write(b'M1024\n') # send AWG B Buffer Length
            time.sleep(0.005)
            print("set AWG Samples: 1024")
            # ser.write(b'p64000\n') # send PWM (AWG) frequency
            
            MaxSamples = 4096 # assume 4X interpolation
            #
            ser.write(b'Rx\n') # turn off AWG sync by default
            #
            # ser.write(b'sx\n') # turn off PWM output by default
            ser.write(b'Gx\n') # turn off AWG A by default
            ser.write(b'gx\n') # turn off AWG B by default
    #
            print("Get a sample: ")
            Get_Data() # grap a check set of samples
            print("After Interp ", len(VBuffA), len(VBuffB))
            SHOWsamples = len(VBuffA)
            return(True) # return a logical true if sucessful!
        else:
            print("No response so asking to load firmware")
            if askyesno("Load Firmware?", "Do You Wish to load firmware on this board?"):
                ser.baudrate = 1200 # Opening serial port at 1200 Baud for a short while will reset board
                time.sleep(0.05)
                if ser.in_waiting > 0:
                    IDstring = str(ser.readline()) # read something
                    print(IDstring)
                time.sleep(0.05)
                ser.close()
                # if this worked a USB drive window should open.
                time.sleep(1.0) # wait 1 sec
                # attempt to copy .uf2 file to USB drive
                if platform.system() == "Windows":
                    os.system("copy XIAO_Scope_pwm_awg.uf2 E:")

            return(False)
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
def AWGASendWave(AWG3): # Analog DAC on A0
    global ser, AWGARecLength, AWGBuffLen, AWGARes
    global AWGAAmplvalue, AWGAOffsetvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # scale values to send to 0 to 255 8 bits
    AWG3 = AWG3 * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    MinCode = int((AWGAAmplvalue / AWGPeakToPeak) * AWGARes)
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGARes:
        MinCode = AWGARes
    MaxCode = int((AWGAOffsetvalue / AWGPeakToPeak) * AWGARes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGARes:
        MaxCode = AWGARes
    # print("MinCode = ", MinCode, "MaxCode = ", MaxCode)
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
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'N' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #
    index = 0
    # print(AWGARecLength)
    while index < AWGARecLength:
        data = AWG1[index]
        # send buffer index and waveform sample data
        SendStr = 'L' + str(index) + 'D' + str(data) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
#
##    
def AWGBSendWave(AWG3): # PWM DAC on D10
    global ser, AWGBLastWave, AWGBRecLength, AWGARecLength, AWGBuffLen, AWGBRes
    global AWGBAmplvalue, AWGBOffsetvalue, AWGPeakToPeak, AWGSampleRate
    global AWGBFreqvalue, AWGBFreqEntry, AWGBPhaseEntry
    global AWGBdelayvalue, AWGBPhaseDelay, AWGBperiodvalue, AWGBPhasevalue
    # Expect array values normalized from -1 to 1
    # 
    AWGBLastWave = AWG3
    AWG3 = AWG3 * 0.5 # scale by 1/2
    # shift waveform array left or right based on phase / delay entry
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    AWGBPhasevalue = float(eval(AWGBPhaseEntry.get()))
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGSAMPLErate / 1000
    AWG3 = numpy.roll(AWG3, int(AWGBdelayvalue))
    #
    # Get Low and High voltage levels
    MinCode = int((AWGBAmplvalue / AWGPeakToPeak) * AWGBRes)
    if MinCode < 0:
        MinCode = 0
    if MinCode > AWGBRes:
        MinCode = AWGBRes
    MaxCode = int((AWGBOffsetvalue / AWGPeakToPeak) * AWGBRes)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > AWGBRes:
        MaxCode = AWGBRes
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
        # print(SendStr)
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        SendStr = 'M' + str(AWGBuffLen) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #
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
def BAWGSync():
    global AWGSync

    if AWGSync.get() > 0:
        ser.write(b'Ro\n') # turn on sync
    else:
        ser.write(b'Rx\n') # turn off sync
#
##    
#
def SetAwgSampleRate():
    global AWGAFreqEntry, AWGBFreqEntry, FSweepMode
    global AWGBuffLen, AWGSampleRate, AWGBuffLen

    BAWGAFreq()
    # BAWGBFreq()

    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    FreqA = UnitConvert(AWGAFreqEntry.get())
    #reqB = UnitConvert(AWGBFreqEntry.get())
    Cycles = 1
    if FSweepMode.get() == 1: # If doing a frequency sweep only make new AWG A sine wave
        if FreqA > MaxRepRate:
            Cycles = numpy.ceil(FreqA/MaxRepRate)
            if Cycles <= 0: # check if divide by zero
                Cycles = 1
            FreqA = FreqA/Cycles
    # Set the AWG buffer Rep rate (Freq for one cycle of buffer)
        SetAwgSampleFrequency(FreqA)
        AWGRepRate = FreqA
        # AWGSampleRate = FreqA * AWGBuffLen
            # AWGSampleRate = FreqB * MaxSamples
    # print("Cycles = ", Cycles)
#
def SetAwgSampleFrequency(FreqANum):
    global AWGBuffLen
    #
    NewSampleRate = FreqANum * AWGBuffLen # Samples per second
    NewAT = int(1000000/NewSampleRate) # in uSec
    if NewAT < 15:
        NewAT = 15
    SendStr = 'T' + str(NewAT) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    # print(SendByt)
    ser.write(SendByt) #
#
# for built in firmware waveforms...
#
def SetAwgA_Ampl(Ampl): # used to toggle on / off AWG output
    global ser, AwgBOnOffBt, AwgaOnOffLb, AwgbOnOffLb, AWGSampleRate

    # AwgBOnOffBt.config(state=DISABLED)
    AwgaOnOffLb.config(text="AWG A Output ")
    AwgbOnOffLb.config(text="AWG B Output ")
    # AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        ser.write(b'Gx\n')
    else:
        ser.write(b'Go\n')
#
def SetAwgB_Ampl(Ampl): # used to toggle on / off AWG output
    global ser, AwgBOnOffBt, AwgaOnOffLb, AwgbOnOffLb, AWGSampleRate

    # AwgBOnOffBt.config(state=DISABLED)
    AwgbOnOffLb.config(text="AWG B Output ")
    # AwgbOnOffLb.config(text=" ")
    if Ampl == 0:
        ser.write(b'gx\n')
    else:
        ser.write(b'go\n')
#
def SetAWG_Ampla():
    global AWGAAmplEntry, ADC_Cal, ser, AWGRes

    MaxLimit = int(AWGRes/2)
    Vampl = float(AWGAAmplEntry.get())
    Bampl = int((Vampl/ADC_Cal)*MaxLimit)
    if Bampl > MaxLimit:
        Bampl = MaxLimit
    if Bampl < 0:
        Bampl = 0
    # print("Bampl = ", Bampl)
    ByteStr = 'A' + str(Bampl) + "\n"
    SendByt = ByteStr.encode('utf-8')
    ser.write(SendByt) #
#
def SetAWG_Offseta():
    global AWGAOffsetEntry, ADC_Cal, ser, AWGRes

    Voffset = float(AWGAOffsetEntry.get())
    Boffset = int((Voffset/ADC_Cal)*(AWGRes+1))
    # print("Boffset = ", Boffset)
    ByteStr = 'O' + str(Boffset) + "\n"
    SendByt = ByteStr.encode('utf-8')
    ser.write(SendByt) #
#
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
AwgString14 = "Uniform Noise"
AwgString15 = "Gaussian Noise"
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
        AWGAShapeLabel.config(text = AwgString13) # change displayed value
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
        AWGAMakeUUNoise()
        AWGAShapeLabel.config(text = AwgString14) # change displayed value
    elif AWGAShape.get()==15:
        AWGAMakeUGNoise()
        AWGAShapeLabel.config(text = AwgString15) # change displayed value
    else:
        AWGAShapeLabel.config(text = "Other Shape") # change displayed value
#
    if AWGBShape.get()== 0:
        AWGBMakeDC()
        AWGBShapeLabel.config(text = "DC") # change displayed value
    elif AWGBShape.get()==1:
        AWGBMakeSine()
        AWGBShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGBShape.get()==2:
        AWGBMakeSquare()
        AWGBShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGBShape.get()==3:
        AWGBMakeTriangle()
        AWGBShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGBShape.get()==4:
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
    elif AWGBShape.get()==14:
        AWGBMakeUUNoise()
        AWGBShapeLabel.config(text = AwgString14) # change displayed value
    elif AWGBShape.get()==15:
        AWGBMakeUGNoise()
        AWGBShapeLabel.config(text = AwgString15) # change displayed value
    else:
        AWGBShapeLabel.config(text = "Other Shape") # change displayed value

#
    time.sleep(0.01)
#
def MakeAWG_internal_waves(): # re make awg waveforms in case something changed
    global ser, AWGAShape, AWGAShapeLabel, AWGBShape, AWGBShapeLabel
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGASymmetryEntry, AWGADutyCycleEntry
    global AWGAAmplvalue, AWGBOffsetvalue, AWGBAmplvalue, AWGBOffsetvalue
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBSymmetryEntry, AWGBDutyCycleEntry
    global FSweepMode, MaxSampleRate
    global AwgString1, AwgString2, AwgString3, AwgString4, AwgString5, AwgString6
    global AwgString7, AwgString8, AwgString9, AwgString10, AwgString11, AwgString12
    global AwgString13, AwgString14, AwgString15, AwgString16
    
    #
    time.sleep(0.01)
    #
    if AWGAShape.get()==0:
        ser.write(b'W0\n')
        AWGAShapeLabel.config(text = AwgString0) # change displayed value
    elif AWGAShape.get()==1:
        ser.write(b'W1\n')
        AWGAShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGAShape.get()==2:
        ser.write(b'W2\n')
        AWGAShapeLabel.config(text = AwgString2) # change displayed value
    elif AWGAShape.get()==3:
        ser.write(b'W3\n')
        AWGAShapeLabel.config(text = AwgString3) # change displayed value
    elif AWGAShape.get()==4:
        ser.write(b'W4\n')
        AWGAShapeLabel.config(text = AwgString4) # change displayed value
    elif AWGAShape.get()==5:
        ser.write(b'W5\n')
        AWGAShapeLabel.config(text = AwgString5) # change displayed value
    elif AWGAShape.get()==6:
        ser.write(b'W6\n')
        AWGAShapeLabel.config(text = AwgString6) # change displayed value
    elif AWGAShape.get()==7:
        ser.write(b'W7\n')
        AWGAShapeLabel.config(text = AwgString7) # change displayed value
    #
    if AWGBShape.get()==0:
        ser.write(b'w0\n')
        AWGBShapeLabel.config(text = AwgString0) # change displayed value
    elif AWGBShape.get()==1:
        ser.write(b'w1\n')
        AWGBShapeLabel.config(text = AwgString1) # change displayed value
    elif AWGBShape.get()==2:
        ser.write(b'w2\n')
        AWGBShapeLabel.config(text = AwgString2) # change displayed value
    #SetAwgFrequency()
    SetAWG_Ampla()
    SetAWG_Offseta()
    SetAWG_Amplb()
    SetAWG_Offsetb()
    time.sleep(0.1)
#
# Hardware Specific PWM control functions
#
def PWM_On_Off():
    global PWM_is_on, ser

    if PWM_is_on:
        #print("Set pwm on")
        UpdatePWM()
        ser.write(b'so\n')
    else:
        #print("Set pwm off")
        ser.write(b'sx\n')
#
def UpdatePWM():
    global PWMDivEntry, PWMWidthEntry, PWMLabel, ser

    PWMLabel.config(text = "PWM Frequency")

    FreqValue = int(UnitConvert(PWMDivEntry.get()))
    # print("FreqValue = ", FreqValue)
    ByteStr = 'p' + str(FreqValue) + "\n"
    SendByt = ByteStr.encode('utf-8')
    ser.write(SendByt)
    time.sleep(0.1)
    
    DutyCycle = int(PWMWidthEntry.get())
    DutyCycle = DutyCycle * 10 # value can be 0 to 1000
    #
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

