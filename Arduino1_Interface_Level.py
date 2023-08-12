#
# Hardware specific interface functions
# For Arduino scope on pi pico Dev Kits (7-27-2023)
# Written using Python version 3.10, Windows OS 
#
import serial
import serial.tools.list_ports
#
# adjust for your specific hardware by changing these values in the alice.init file
CHANNELS = 2 # Number of supported Analog input channels
AWGChannels = 0 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 0 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 0 # 
Tdiv.set(10)
DevID = "Ard"
SerComPort = 'Auto'
TimeSpan = 0.01
ADC_Cal = 4.745
MaxSampleRate = SAMPLErate = 15000
LSBsizeA = LSBsizeB = LSBsizeC = LSBsizeD = LSBsize = 3.3/1024.0
SMPfft = 1024 # Set FFT size based on fixed acquisition record length
PhaseOffset = 12.5
MinSamples = 3100
VBuffA = numpy.ones(MinSamples)
VBuffB = numpy.ones(MinSamples)
VBuffC = numpy.ones(MinSamples)
VBuffD = numpy.ones(MinSamples)
MBuff = numpy.ones(MinSamples)
MBuffX = numpy.ones(MinSamples)
MBuffY = numpy.ones(MinSamples)
VmemoryA = numpy.ones(MinSamples) # The memory for averaging
VmemoryB = numpy.ones(MinSamples)
VmemoryC = numpy.ones(MinSamples)
VmemoryD = numpy.ones(MinSamples)
#
## hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, core, ser
    
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
    global TimeSpan, MaxSampleRate, SHOWsamples, Power2, RateDivider, Tdiv
    global ser, TrigSource, TriggerEdge, TriggerInt, SAMPLErate, TimeDiv

    TimeSpan = (Tdiv.get() * TimeDiv)# in Seconds
    try:
        TempDivider = round((MaxSampleRate / SHOWsamples) * TimeSpan)
    except:
        TempDivider = round(( MaxSampleRate / 1024.0) * TimeSpan)
    if TempDivider == 0:
        NDiv = 1
    else:
        NDiv = 2**(TempDivider - 1).bit_length()
    SAMPLErate = MaxSampleRate #
#
# Main function to request and receive a set of ADC samples
#
def Arduino_Get_data():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global ser, SHOWsamples, RateDivider, TgInput, TimeSpan
    global RateDivider, TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    
    # Get data from CyScope
    
    if TimeSpan < 0.001:
        TimeOut = 0.001
    else:
        TimeOut = TimeSpan
    
    SHOWsamples = len(VBuffA)
    return
#
def Get_Data():
    global VBuffA, VBuffB, ShowC1_V, ShowC2_V
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global ser, SHOWsamples, TRIGGERsample, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global vct_btn, vdt_btn, HoldOff
    # Get data from CyScope
    #
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0:
        ser.write(b'2\n')
    else:
        ser.write(b'1\n')
    #
    time.sleep(0.200)
    serialString = ser.read(13000)# ser.in_waiting)
    Buffer1 = serialString.decode("Ascii")
    Buffer1 = Buffer1.split('\r')
    #print("Length: ", len(serialString), len(Buffer1))
    
    index = 0
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0:
        VBuffA = [] # Clear the A array 
        VBuffB = [] # Clear the B array
        while index < len(Buffer1):
            try:
                Buffer = Buffer1[index]
                TwoSamp = Buffer.split(',')
                VBuffA.append(int(TwoSamp[0]))
                VBuffB.append(int(TwoSamp[1]))
            except:
                pass
            index = index + 1
    else:
        VBuffA = [] # Clear the A array 
        while index < len(Buffer1):
            try:
                VBuffA.append(int(Buffer1[index]))
            except:
                pass
            index = index + 1
    ##
    if ShowC1_V.get() > 0:
        VBuffA = numpy.array(VBuffA)
        VBuffA = (VBuffA) * LSBsizeA # convert to Volts
        SHOWsamples = len(VBuffA)
    if ShowC2_V.get() > 0:
        VBuffB = numpy.array(VBuffB)
        VBuffB = (VBuffB) * LSBsizeB
        if len(VBuffA) > len(VBuffB):
            SHOWsamples = len(VBuffB)
        else:
            SHOWsamples = len(VBuffA)
    
    # Find trigger sample point if necessary
    # print("Array Len ",len(VBuffA), "SHOWsamples ", SHOWsamples)
    HoldOff = 100
    LShift = 0
    if TgInput.get() == 1:
        FindTriggerSample(VBuffA)
    if TgInput.get() == 2:
        FindTriggerSample(VBuffB)
    if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
        LShift = 0 - TRIGGERsample
        if ShowC1_V.get() > 0:
            VBuffA = numpy.roll(VBuffA, LShift)
        if ShowC2_V.get() > 0:
            VBuffB = numpy.roll(VBuffB, LShift)
#
## try to connect to Arduino board
#
def ConnectDevice():
    global ser, SerComPort, DevID, MaxSamples, SAMPLErate, RateDivider
    global bcon, FWRevOne, HWRevOne, MaxSampleRate
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv
    global CHAsb, CHBsb, TMsb, LSBsizeA, LSBsizeB, ADC_Cal
    global d0btn, d1btn, d2btn, d3btn, d4btn, d5btn, d6btn, d7btn

    if DevID == "No Device" or DevID == "Ard":
        #
        if SerComPort == 'Auto':
            ports = serial.tools.list_ports.comports()
            for port in ports: # ports:
                # loking for this ID: USB\VID_2E8A&PID_000A
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
        ser.baudrate = 230400
        ser.bytesize=8
        ser.parity='N'
        ser.stopbits=1
        ser.timeout=0
        xonxoff=0,
        ser.rtscts=1
        serialString = "none"  # Used to hold data coming over UART
        # print(ser)
        print(ser.name) # check which port was really used
        # send ID command
        ser.write(b'1\n') # write the string
        
        MaxSamples = 4000
        SAMPLErate = MaxSampleRate
        # ReMakeAWGwaves()
        Get_Data() # do a dummy first data capture
        return(True) # return a logical true if sucessful!
    else:
        return(False)
# Dummy routine
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
# The trigger voltage is calculated as follows:
    TgValue = int((TRIGGERlevel/AWGPeakToPeak)*255)
# The command would be S T DAC_Value
    # print("V, DAC ", TRIGGERlevel, TgValue) 
    SendStr = 'S T ' + str(TgValue) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
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

