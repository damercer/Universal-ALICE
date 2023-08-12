#
# Hardware specific interface functions
# For Raspberry Pi Pico with sigrok-pico firmware Dev Kits (7-28-2023)
# Written using Python version 3.10, Windows OS 
#
import serial
import serial.tools.list_ports
#
# adjust for your specific hardware by changing these values in the alice.init file
DevID = "PiPico"
TimeSpan = 0.001
SerComPort = 'Auto' # "COM17"
CHANNELS = 3 # Number of supported Analog input channels
AWGChannels = 0 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 7 # Number of supported Dig channels
LogicChannels = 7 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 # 1
EnableBodePlotter = 0
Tdiv.set(10) # number of Horz time divisions
LSBsizeA = LSBsizeB = LSBsizeC = LSBsizeD = LSBsize = 0.0257
PhaseOffset = 12.5
MaxSampleRate = 150000 # 160000 for 3 channels
MinSamples = 4001
MaxSamples = 160000
SMPfft = 2048 # Set FFT size based on fixed acquisition record length
# set the size of these arrays if MinSamples > 1024
VBuffA = numpy.ones(MinSamples)
VBuffB = numpy.ones(MinSamples)
VBuffC = numpy.ones(MinSamples)
VBuffD = numpy.ones(MinSamples)
VmemoryA = numpy.ones(MinSamples) # The memory for averaging
VmemoryB = numpy.ones(MinSamples)
VmemoryC = numpy.ones(MinSamples)
VmemoryD = numpy.ones(MinSamples)
MBuff = numpy.ones(MinSamples)
MBuffX = numpy.ones(MinSamples)
MBuffY = numpy.ones(MinSamples)
DBuff0 = numpy.zeros(MinSamples)
DBuff1 = numpy.zeros(MinSamples)
DBuff2 = numpy.zeros(MinSamples)
DBuff3 = numpy.zeros(MinSamples)
DBuff4 = numpy.zeros(MinSamples)
DBuff5 = numpy.zeros(MinSamples)
DBuff6 = numpy.zeros(MinSamples)
#
## hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, ser
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig("alice-last-config.cfg")
        ser.close() # May need to be changed for specific hardware port
        # exit
    except:
        donothing()

    root.destroy()
    exit()
#
# Set Scope Sample Rate based on Horz Time Scale
def SetSampleRate():
    global TimeSpan, MaxSampleRate, SHOWsamples, Tdiv
    global ser, TrigSource, TriggerEdge, TriggerInt, SAMPLErate, TimeDiv
    global MinSamples, RecordLength

    TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
    # Pick sample rate based on time scale
    if TimeDiv < 0.002:
        SAMPLErate = MaxSampleRate # 160000 for 3 channels
    elif TimeDiv >= 0.002 and TimeDiv < 0.005:
        SAMPLErate = int(MaxSampleRate/2) 
    elif TimeDiv >= 0.005 and TimeDiv < 0.010:
        SAMPLErate = int(MaxSampleRate/4) 
    elif TimeDiv >= 0.0010 and TimeDiv < 0.020:
        SAMPLErate = int(MaxSampleRate/10) 
    else:
        SAMPLErate = int(MaxSampleRate/20)
    #
    SHOWsamples = int(SAMPLErate * TimeSpan * 2.5)
    if SHOWsamples < MinSamples:
        SHOWsamples = MinSamples
    RecordLength = SHOWsamples
    # Set Sample Rate
    #
    SendStr = 'R' + str(SAMPLErate) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)

    Returned = ser.readline()
    time.sleep(0.001)
    ## Set Capture Length
    SendStr = 'L' + str(RecordLength) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    
    Returned = ser.readline()
    #print("Returned: ",ser.readline())
    # print("RecordLength = ", RecordLength)
    time.sleep(0.005)
#
# Main hardware function to request and receive a set of data samples
#
def sigrok_Get_data():
    global VBuffA, VBuffB, VBuffC, VBuffD, RecordLength
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD, LSBsize
    global ser, SHOWsamples, TgInput, TimeSpan, TimeDiv
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global ShowC1_V, ShowC2_V, ShowC3_V
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    #
    # Configure which channels are on or off
    #
    SaveDig = False
    VBuffA = []
    VBuffB = []
    VBuffC = []
    if D0_is_on or D1_is_on or D2_is_on or D3_is_on or D4_is_on or D5_is_on or D6_is_on:
        BuffD = []
        SaveDig = True
    else:
        SaveDig = False
    #
    if TimeDiv < 0.001:
        TimeOut = 0.001
    else:
        TimeOut = TimeDiv

    # Get data from Pi Pico
    #
    ser.write(b'F\n') # Get samples
    # Returned = ser.readline()
    #
    Count = 0
    while ser.in_waiting == 0:
        time.sleep(TimeOut) # + 0.001)
        Count = Count + 1
        if Count == 20:
            #print("Timed out!")
            break
    #
    time.sleep(TimeSpan)
    while ser.in_waiting != 0:
        Temp = ser.read(ser.in_waiting)
        index = 0
        if len(Temp) > 3:
            while index < len(Temp)-4:
                if SaveDig:
                    BuffD.append(Temp[index])
                    index = index + 1
                if ShowC1_V.get() > 0:
                    VBuffA.append(Temp[index]-128)
                    index = index + 1
                if ShowC2_V.get() > 0:
                    VBuffB.append(Temp[index]-128)
                    index = index + 1
                if ShowC3_V.get() > 0:
                    VBuffC.append(Temp[index]-128)
                    index = index + 1
    #print("Length of Raw 1 : ", len(VBuffA))
    #
    Reads = 0
    NeedMore = False
    if (ShowC1_V.get() > 0) and (len(VBuffA) < SHOWsamples):
        NeedMore = True
    elif (ShowC2_V.get() > 0) and (len(VBuffB) < SHOWsamples):
        NeedMore = True
    elif (ShowC2_V.get() > 0) and (len(VBuffC) < SHOWsamples):
        NeedMore = True
    else:
        NeedMore = False
    if NeedMore:
        ser.write(b'*\n') # terminate any pending sampling and data transfers
        Count = 0
        while ser.in_waiting == 0:
            time.sleep(TimeOut) # + 0.001)
            Count = Count + 1
            if Count == 25:
                #print("Timed out again!")
                break
    #
        # print("Length of Raw 1 : ", len(VBuffA))
        # time.sleep(0.003)
        Reads = 0
        while ser.in_waiting != 0:
            Temp = ser.read(ser.in_waiting)
            Reads = Reads + 1
            index = 0
            while index < len(Temp)-4:
                if SaveDig:
                    BuffD.append(Temp[index])
                    index = index + 1
                if ShowC1_V.get() > 0:
                    VBuffA.append(Temp[index]-128)
                    index = index + 1
                if ShowC2_V.get() > 0:
                    VBuffB.append(Temp[index]-128)
                    index = index + 1
                if ShowC3_V.get() > 0:
                    VBuffC.append(Temp[index]-128)
                    index = index + 1
            #print("# Reads: ", Reads)
    #print("Length of Raw 2: ", len(VBuffA))
    # print("# Reads: ", Reads)
    if SaveDig:
        if len(BuffD) > 1000:
            VBuffD = numpy.array(BuffD)
            # print("Dig Length = ", len(VBuffD))
    if ShowC1_V.get() > 0:
        if len(VBuffA) > RecordLength:
            VBuffA = numpy.array(VBuffA[0:RecordLength])
        else:
            VBuffA = numpy.array(VBuffA)
        VBuffA = VBuffA * LSBsize
    if ShowC2_V.get() > 0:
        if len(VBuffB) > RecordLength:
            VBuffB = numpy.array(VBuffB[0:RecordLength])
        else:
            VBuffB = numpy.array(VBuffB)
        VBuffB = VBuffB * LSBsize
    if ShowC3_V.get() > 0:
        if len(VBuffC) > RecordLength:
            VBuffC = numpy.array(VBuffC[0:RecordLength])
        else:
            VBuffC = numpy.array(VBuffC)
        VBuffC = VBuffC * LSBsize
#
# main routine entry point to request sample data
def Get_Data():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global ShowC1_V, ShowC2_V, ShowC3_V
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD, LSBsize
    global InOffA, InOffB, InOffC, InGainA, InGainB, InGainC
    global ser, SHOWsamples, TgInput, TimeSpan, RecordLength
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global TRACESread, TRIGGERsample, TRIGGERentry
    global PhAScreenStatus, vct_btn, vdt_btn, ShowC3_V, ShowC4_V
    # 
    # time.sleep(0.005)
    # Get data from Pico
    sigrok_Get_data()
    #
    # Extract Digital buffers if needed
    SaveDig = False
    if D0_is_on or D1_is_on or D2_is_on or D3_is_on or D4_is_on or D5_is_on or D6_is_on:
        SaveDig = True
        VBuffD = VBuffD - 128
        VBuffD = VBuffD.astype(int)
        if D0_is_on:
            DBuff0 = VBuffD & 1
        if D1_is_on:
            DBuff1 = VBuffD & 2
            DBuff1 = DBuff1 / 2
        if D2_is_on:
            DBuff2 = VBuffD & 4
            DBuff2 = DBuff2 / 4
        if D3_is_on:
            DBuff3 = VBuffD & 8
            DBuff3 = DBuff3 / 8
        if D4_is_on:
            DBuff4 = VBuffD & 16
            DBuff4 = DBuff4 / 16
        if D5_is_on:
            DBuff5 = VBuffD & 32
            DBuff5 = DBuff5 / 32
        if D6_is_on:
            DBuff6 = VBuffD & 64
            DBuff6 = DBuff6 / 64
    else:
        SaveDig = False 
    #
    TRACESread = 3
    if (len(VBuffA) > 1000) or (len(VBuffB) > 1000) or (len(VBuffC) > 1000) or (len(VBuffD) > 1000):
        # Find trigger sample point if necessary
        #print("Array Len ",len(VBuffA), "SHOWsamples ", SHOWsamples)
        LShift = 0
        if TgInput.get() == 1:
            FindTriggerSample(VBuffA)
        if TgInput.get() == 2:
            FindTriggerSample(VBuffB)
        if TgInput.get() == 3:
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
            # if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
            # Average mode 1, add difference / TRACEaverage to array
        if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
            LShift = 0 - TRIGGERsample
            if ShowC1_V.get() > 0:
                VBuffA = numpy.roll(VBuffA, LShift)
            if ShowC2_V.get() > 0:
                VBuffB = numpy.roll(VBuffB, LShift)
            if ShowC3_V.get() > 0:
                VBuffC = numpy.roll(VBuffC, LShift)
            if SaveDig:
                VBuffD = numpy.roll(VBuffD, LShift)
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
                MakeDigitalTrace(len(VBuffD))
            # print("TRIGGERsample ", TRIGGERsample, ", Length ", len(VBuffA))
#
## try to connect to Pi Pico (sigrok) board
#
def ConnectDevice():
    global ser, SerComPort, DevID, MaxSamples, SAMPLErate
    global bcon, FWRevOne, HWRevOne, MaxSampleRate, MinSamples
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv
    global CHAsb, CHBsb, TMsb, LSBsizeA, LSBsizeB, ADC_Cal

    if DevID == "No Device" or DevID == "PiPico":
        #
        if SerComPort == 'Auto':
            ports = serial.tools.list_ports.comports()
            for port in ports: # ports:
                # looking for this ID:VID 2E8A & PID 000A
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
        ser.baudrate = 921600
        ser.bytesize=8
        ser.parity='N'
        ser.stopbits=1
        ser.timeout=0
        xonxoff=0,
        ser.rtscts=1
        serialString = "none"  # Used to hold data coming over UART
        # print(ser)
        print(ser.name) # check which port was really used
        ser.write(b'*\n') # sent abort command
        #
        Returned = ser.readline()
        #
        ser.write(b'+\n') # send reset command
        #
        Returned = ser.readline()
        # send ID command
        ser.write(b'i\n') # write the string
        print("Returned: ", ser.readline())
        #
        SAMPLErate = MaxSampleRate
        ##
        SendStr = 'R' + str(SAMPLErate) + '\n'
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        # ser.write(b'R160000\n') # Set Sample Rate
        #print(ser.in_waiting)
        serialString = ser.readline()
        print("Returned: ", serialString)
        DevID = str(serialString[0:6])
        DevID = DevID[2:8]
        print("ID Returned: ", DevID)
        #print("Returned: ",ser.readline())
        #
        ## Set Capture Length
        SendStr = 'L' + str(MinSamples) + '\n'
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        #ser.write(b'L2400\n') # Set Capture Length
        #print(ser.in_waiting)
        print("Returned: ",ser.readline())
        HardwareSelectChannels()
        SetDigPin()
        Get_Data() # do a dummy first data capture
        return(True) # return a logical true if sucessful!
    else:
        return(False)
#
# Select which analog inputs to enable
def HardwareSelectChannels():
    global ser, ShowC1_V, ShowC2_V, ShowC3_V
    
    if ShowC1_V.get() > 0:
        ser.write(b'A100\n') # Enable Analog Cha 0
    else:
        ser.write(b'A000\n') # Disable Analog Cha 0
    if ShowC2_V.get() > 0:
        ser.write(b'A101\n') # Enable Analog Cha 1
    else:
        ser.write(b'A001\n') # Disable Analog Cha 1
    if ShowC3_V.get() > 0:
        ser.write(b'A102\n') # Enable Analog Cha 2
    else:
        ser.write(b'A002\n') # Disable Analog Cha 2
#
def HardwareStop():
    global ser

    #
    ser.write(b'*\n') # sent abort command
    #print(ser.in_waiting)
    Returned = ser.readline()
    #
    ser.write(b'+\n') # send reset command
    #print(ser.in_waiting)
    Returned = ser.readline()
#
AwgString9 = "Full Wave Sine"
AwgString10 = "Half Wave Sine"
AwgString11 = "Fourier Series"
AwgString12 = "Schroeder Chirp"
## Make or update the current selected AWG waveform
def MakeAWGwaves(): # re make awg waveforms in case something changed
    global AWGAShape, AWGAShapeLabel, AWGBShape, AWGBShapeLabel
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
    SendStr = 'S C ' + str(T_High) + ' ' + str(T_Low) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    # ser.write(b'S C 1 0\n')
#
## evalute trigger level entry string to a numerical value and set new trigger level     
def SendTriggerLevel():
    global TRIGGERlevel, TRIGGERentry, RUNstatus

    # evalute entry string to a numerical value
    #
    TRIGGERlevel = UnitConvert(TRIGGERentry.get())
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
# Set Internal / External triggering bits
def BTrigIntExt():
    global TgSource, TriggerInt

    donothing()
    
# Triggering dummy routines for Pi Pico (no hardware triggering)
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
#
# Hardware Specific digital input control function
#
def SetDigPin():
    global ser
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line

    if D0_is_on:
        ser.write(b'D100\n') # Enable Digital Cha 0
    else:
        D0line = []
        ser.write(b'D000\n') # Disable Digital Cha 0
    if D1_is_on:
        ser.write(b'D101\n') # Enable Digital Cha 1
    else:
        D1line = []
        ser.write(b'D001\n') # Disable Digital Cha 1
    if D2_is_on:
        ser.write(b'D102\n') # Enable Digital Cha 2
    else:
        D2line = []
        ser.write(b'D002\n') # Disable Digital Cha 2
    if D3_is_on:
        ser.write(b'D103\n') # Enable Digital Cha 3
    else:
        D3line = []
        ser.write(b'D003\n') # Disable Digital Cha 3
    if D4_is_on:
        ser.write(b'D104\n') # Enable Digital Cha 4
    else:
        D4line = []
        ser.write(b'D004\n') # Disable Digital Cha 4
    if D5_is_on:
        ser.write(b'D105\n') # Enable Digital Cha 5
    else:
        D5line = []
        ser.write(b'D005\n') # Disable Digital Cha 5
    if D6_is_on:
        ser.write(b'D106\n') # Enable Digital Cha 6
    else:
        D6line = []
        ser.write(b'D006\n') # Disable Digital Cha 6
#
