#
# Hardware specific interface functions
# For PSoC 5 CyScope Dev Kits (8-11-2023)
# Written using Python version 3.10, Windows OS 
#
import serial
import serial.tools.list_ports
#
# adjust for your specific hardware by changing these values
CHANNELS = 4 # Number of supported Analog input channels
AWGChannels = 3 # Number of supported Analog output channels
PWMChannels = 1 # Number of supported PWM output channels
DigChannels = 5 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
EnablePGAGain = 1 # 
Tdiv.set(10)
DevID = "CyScope"
SerComPort = 'Auto'
TimeSpan = 0.001
TrigSource = 0x00 # bit 4
TriggerEdge = 0x00 # bit 5
TriggerInt = 0x00 # bit 6
AWGPeakToPeak = 4.08
ADC_Cal = 4.745 # Calibrate this value based on the USB port voltage - diode drop
RateDivider = 3
SAMPLErate = MaxSampleRate / (2**RateDivider)
LSBsizeA = LSBsizeB = LSBsizeC = LSBsizeD = LSBsize = ADC_Cal/4096.0
SMPfft = 1024 # Set FFT size based on fixed acquisition record length
PhaseOffset = 12.5
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
    RateDivider = Power2.index(NDiv)
    RegValue = RateDivider + TrigSource + TriggerEdge + TriggerInt
    SendStr = 'S R ' + str(RegValue) +'\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    # print(RateDivider)
    SAMPLErate = MaxSampleRate / (2**RateDivider) #
#
# Main function to request and receive a set of ADC samples
#
def CyScope_Get_data():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global ser, SHOWsamples, RateDivider, TgInput, TimeSpan
    global RateDivider, TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    
    # Get data from CyScope
    
    if TimeSpan < 0.001:
        TimeOut = 0.001
    else:
        TimeOut = TimeSpan
    if TgInput.get() == 0:
        Is_Triggered = 0
        RegValue = RateDivider + TrigSource + TriggerEdge + 0x40
        SendStr = 'S R ' + str(RegValue) +'\n'
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        # ser.write(SendByt)
        time.sleep(TimeOut)
        # Force a capture request:
        ser.write(b'S D 3\n') # S D 3 Set REQ=1
        time.sleep(TimeOut)
        ser.write(b'S D 2\n') # S D 3 Set REQ=0
    else:
        Is_Triggered = 1
        RegValue = RateDivider + TrigSource + TriggerEdge + TriggerInt
        SendStr = 'S R ' + str(RegValue) +'\n'
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #
    MissTrig = 0
    ShiftA1 = 0
    ShiftB1 = 0
    # S G Scope: Go, begin capture.
    ser.write(b'S G\n')
    Count1 = 0
    while ser.in_waiting == 0:
        #Status = ser.readline()
        time.sleep(TimeOut)
        Count1 = Count1 + 1
        if Count1 > 20:
            RegValue = RateDivider + 0x40
            SendStr = 'S R ' + str(RegValue) +'\n'
            SendByt = SendStr.encode('utf-8')
            ser.write(SendByt)     # write a string
            time.sleep(TimeOut)
            # print("Timed Out after S G", Count1)
            ser.write(b'S D 5\n') # S D 5 Set MAN_TRIG=1
            time.sleep(TimeOut)
            # ser.write(SendByt)     # write a string
            ser.write(b'S D 4\n') # S D 5 Set MAN_TRIG=0
            time.sleep(TimeOut)
            MissTrig = 1
            Is_Triggered = 0
            break
    #print("After S G: ", ser.in_waiting)
    time.sleep(0.003)
    Buffer = ser.read(ser.in_waiting)
    if chr(Buffer[0]) == 'A' and len(Buffer) == 3:
##        if MissTrig > 0:
##            print("A: ", Buffer[1], Buffer[2])
        ShiftA1 = Buffer[2]
        ShiftB1 = Buffer[1]
    # 
    #time.sleep(0.01)
    # S B Scope: Read scope data buffer
    ser.write(b'S B \n')
    Count = 0
    while ser.in_waiting == 0:
        time.sleep(0.001)
        Count = Count + 1
        if Count > 20:
            # print("Timed Out after S B")
            # ser.write(b'S D 5\n') # S D 5 Set MAN_TRIG=1
            # ser.write(b'S D 4\n') # S D 4 Set MAN_TRIG=0
            break
##
    #print("Wait for data to appear: ", Count)
    # print("After S B: ", ser.in_waiting)
    # print("Read back: ", ser.read(ser.in_waiting))
    # print("Bytes Waiting: ", ser.in_waiting)
    time.sleep(0.003)
    Buffer = ser.read(ser.in_waiting)
    #print("Length of Raw: ", len(Buffer))
    #print("First Byte: ", chr(Buffer[0]))
    time.sleep(0.002)
    #
    Count = 0
    while ser.in_waiting == 0:
        #Status = ser.readline()
        time.sleep(0.002)
        Count = Count + 1
        if Count > 50:
            # print("Timed Out Before receiving D")
            # ser.write(b'S D 5\n') # S D 5 Set MAN_TRIG=1
            ser.write(b'S D 4\n') # S D 4 Set MAN_TRIG=0
            time.sleep(0.02)
            ser.write(b'S B\n')
            time.sleep(0.02)
            #return
            break
##
    #print("Wait for data to appear: ", Count)
    Buffer = ser.read(ser.in_waiting)
    #print("First Bytes: ", Buffer[0], Buffer[1], Buffer[2])
    VBuffA1 = []
    VBuffB1 = []
    time.sleep(0.002)
    if chr(Buffer[0]) != 'D':
        index = 0
    else:
        index = 1
    while index < len(Buffer)-3:
        A1 = Buffer[index]
        a1 = Buffer[index+1]
        B1 = Buffer[index+2]
        b1 = Buffer[index+3]
        VBuffA1.append(a1 + (A1*256))
        VBuffB1.append(b1 + (B1*256))
        index = index + 4
    if TgInput.get() > 0:
        Roll = int((ShiftB1 * 256) + ShiftA1 + 1)
        # print('Rolling by: ', Roll)
    else:
        Roll = 0
    VBuffA = numpy.roll(VBuffA1, -Roll)
    VBuffB = numpy.roll(VBuffB1, -Roll)
    #
#    if MissTrig > 0:
    # print("Length of Raw: ", len(Buffer), len(VBuffA1), Roll)
    #print(numpy.amin(VBuffA1), numpy.amax(VBuffA1))
    #print(numpy.amin(VBuffB1), numpy.amax(VBuffB1))
    #VBuffA1 = (VBuffA1) * LSBsizeA
    #VBuffB1 = (VBuffB1) * LSBsizeB
    if len(Buffer) < 4096:
        print("Bail out because buffer was short!")
        VBuffA = numpy.array(VBuffA)
        VBuffB = numpy.array(VBuffB)
        return numpy.array(VBuffA)
    if MissTrig > 0:
        ser.write(b'S D 3\n') # S D 4 Set MAN_TRIG=0
        #print("Length A, B: ", len(VBuffA1), len(VBuffB1))
##    else:
    # VBuffA = numpy.array(VBuffA1)
    # VBuffB = numpy.array(VBuffB1)
    SHOWsamples = len(VBuffA)
    return
#
def Get_Data():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global ser, SHOWsamples, RateDivider, TgInput, TimeSpan
    global TrigSource, TriggerEdge, TriggerInt, Is_Triggered
    global PhAScreenStatus, vct_btn, vdt_btn, ShowC3_V, ShowC4_V
    # Get data from CyScope
    #
    if PhAScreenStatus.get() > 0:
        if vct_btn.config('text')[-1] == 'ON' or vdt_btn.config('text')[-1] == 'ON':
            Get_CD = True
        else:
            Get_CD = False
    else:
        Get_CD = False
    if ShowC3_V.get() > 0 or ShowC4_V.get() > 0 or Get_CD:
        VBuffA = [] # Clear the A array 
        VBuffB = [] # Clear the B array
        # set input Mux to CH C
        ser.write(b'S M C 0\n')
        # set input Mux to CH D
        ser.write(b'S M D 0\n')
        CyScope_Get_data()
        VBuffC = (VBuffA) * LSBsizeC # convert to Volts
        VBuffD = (VBuffB) * LSBsizeD
        VBuffC = numpy.array(VBuffC)
        VBuffD = numpy.array(VBuffD)
        
    VBuffA = [] # Clear the A array 
    VBuffB = [] # Clear the B array
    # set input Mux to CH A
    ser.write(b'S M A 0\n')
    # set input Mux to CH B
    ser.write(b'S M B 0\n')
    CyScope_Get_data()
    VBuffA = (VBuffA) * LSBsizeA # convert to Volts
    VBuffB = (VBuffB) * LSBsizeB
    VBuffA = numpy.array(VBuffA)
    VBuffB = numpy.array(VBuffB)
#
## try to connect to CyScope board
#
def ConnectDevice():
    global ser, SerComPort, DevID, MaxSamples, SAMPLErate, RateDivider
    global bcon, FWRevOne, HWRevOne, MaxSampleRate
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv
    global CHAsb, CHBsb, TMsb, LSBsizeA, LSBsizeB, ADC_Cal
    global d0btn, d1btn, d2btn, d3btn, d4btn, d5btn, d6btn, d7btn

    if DevID == "No Device" or DevID == "CyScope":
        #
        if SerComPort == 'Auto':
            ports = serial.tools.list_ports.comports()
            for port in ports: # ports:
                # loking for this ID: VID:PID=04B4:F232
                if "VID:PID=04B4:F232" in port[2]:
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
        ser.write(b'i\n') # write the string
        Count = 0
        while ser.in_waiting == 0:
            # time.sleep(0.001)
            Count = Count + 1
            if Count > 50:
                break
        # print(Count, ser.in_waiting)
        serialString = ser.readline()
        DevID = serialString.decode("Ascii")
        DevID = DevID.strip('*\r\n')
        print("ID Returned: ", DevID)
        #
        MaxSamples = 2000
        SAMPLErate = MaxSampleRate / (2**RateDivider)
        # S P [A,B] Val Scope: ADC Pre-amp gain setting 0 = 1X
        ser.write(b'S P A 0\n')
        ser.write(b'S P B 0\n')
        #
        #
        # AWG Amplitude 8-bit integer (0-255) as percent 0 - 100%
        # Start up with 0 amplitude
        ser.write(b'W A 0\n') # Upper case for AWG A
        ser.write(b'W W\n') # Upper case for AWG A
        ser.write(b'W a 0\n') # Lower case for AWG B
        ser.write(b'W w\n') # V case for AWG B
        # S C C_HIGH C_LOW Scope:
        # Post trigger sample count 10 bits 512 = 1 0 (0001 0000 0000).
        ser.write(b'S C 1 6\n')
        #
        # bcon.configure(text="Conn", style="GConn.TButton")
        #
        # BTime() # initally set Sample Rate by Horz Time base
        # BSetTrigEdge()
        # BSetTriggerSource()
        # BTriglevel() # set trigger level
        #
        #default PWM output width to 0 on atartup
        WValue = 0
        SendStr = 'D D ' + str(WValue) + '\n'
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        #
        # ReMakeAWGwaves()
        Get_Data() # do a dummy first data capture
        return(True) # return a logical true if sucessful!
    else:
        return(False)
#
# ADC Input Programable Gain Controls
#
def BCHAPGAgain():
    global ser, CHApgasb, ScopePGAGain, LSBsizeA, LSBsize

    Gval = int(CHApgasb.get())
    LSBsizeA = LSBsize / Gval # LSBsize is V/LSB for 5 V FS.
    GainSet = ScopePGAGain.index(Gval)
    #  S P [A,B] Val can be 1,2,4,8,16,24,32,48,50
    SendStr = 'S P A ' + str(GainSet) +'\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
#
def BCHBPGAgain():
    global ser, CHBpgasb, ScopePGAGain, LSBsize, LSBsizeB
    
    Gval = int(CHBpgasb.get())
    LSBsizeB = LSBsize / Gval # LSBsize is V/LSB for 5 V FS.
    GainSet = ScopePGAGain.index(Gval)
    #  S P [A,B] Val can be 1,2,4,8,16,24,32,48,50
    SendStr = 'S P B ' + str(GainSet) +'\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
#
def BCHCPGAgain():
    global ser, CHCpgasb, ScopePGAGain, LSBsizeC, LSBsize

    Gval = int(CHApgasb.get())
    LSBsizeC = LSBsize / Gval # LSBsize is V/LSB for 5 V FS.
    GainSet = ScopePGAGain.index(Gval)
    #  S P [A,B] Val can be 1,2,4,8,16,24,32,48,50
    SendStr = 'S P C ' + str(GainSet) +'\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
#
def BCHDPGAgain():
    global ser, CHDpgasb, ScopePGAGain, LSBsizeD, LSBsize
    
    Gval = int(CHBpgasb.get())
    LSBsizeD = LSBsize / Gval # LSBsize is V/LSB for 5 V FS.
    GainSet = ScopePGAGain.index(Gval)
    #  S P [A,B] Val can be 1,2,4,8,16,24,32,48,50
    SendStr = 'S P D ' + str(GainSet) +'\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
#
# Hardware specific AWG / Signal Generator Functions
#
def AWGASendWave(AWG3):
    global ser, AWGARecLength, MaxSamples
    global AWGAAmplvalue, AWGAOffsetvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    AWG3 = AWG3 * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    MinCode = int((AWGAAmplvalue / AWGPeakToPeak) * 255)
    if MinCode < 0:
        MinCode = 0
    if MinCode > 255:
        MinCode = 255
    MaxCode = int((AWGAOffsetvalue / AWGPeakToPeak) * 255)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > 255:
        MaxCode = 255
    # Scale to high and low voltage values
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1).astype('i1')
    #
    AWGARecLength = len(AWG1)
    if AWGARecLength > MaxSamples:
        AWGARecLength = MaxSamples
    if len(AWG1) < MaxSamples:
        # split the buffer length in to upper and lower bytes
        UByte = (AWGARecLength & 0x0000ff00) >> 8
        LByte = (AWGARecLength & 0x000000ff)
        #
        SendStr = 'W L ' + str(UByte) + ' ' + str(LByte) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        UByte = (MaxSamples & 0x0000ff00) >> 8
        LByte = (MaxSamples & 0x000000ff)
        #
        SendStr = 'W L ' + str(UByte) + ' ' + str(LByte) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGARecLength:
        data = AWG1[index]
        # split the address index in to upper and lower bytes
        UByte = (index & 0x0000ff00) >> 8
        LByte = (index & 0x000000ff)
        # 
        SendStr = 'W S ' + str(UByte) + ' ' + str(LByte) + ' ' + str(data) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
        
    ser.write(b'W P\n') # Send the waveform buffer to change the output waveform
#
##    
def AWGBSendWave(AWG3):
    global ser, AWGBLastWave, AWGBRecLength, MaxSamples
    global AWGBAmplvalue, AWGBOffsetvalue, AWGPeakToPeak
    # Expect array values normalized from -1 to 1
    # AWG3 = numpy.roll(AWG3, -68)
    AWGBLastWave = AWG3
    AWG3 = AWG3 * 0.5 # scale by 1/2
    # Get Low and High voltage levels
    MinCode = int((AWGBAmplvalue / AWGPeakToPeak) * 255)
    if MinCode < 0:
        MinCode = 0
    if MinCode > 255:
        MinCode = 255
    MaxCode = int((AWGBOffsetvalue / AWGPeakToPeak) * 255)
    if MaxCode < 0:
        MaxCode = 0
    if MaxCode > 255:
        MaxCode = 255
    #
    Gain = MaxCode - MinCode
    Offset = int((MaxCode + MinCode)/2)
    AWG3 = (AWG3 * Gain) + Offset
    n = 0
    AWG1 = []
    while n < len(AWG3):
        AWG1.append(int(AWG3[n]))
        n = n + 1
    AWG1 = numpy.array(AWG1).astype('i1')
    #
    AWGBRecLength = len(AWG1)
    if AWGBRecLength > MaxSamples:
        AWGBRecLength = MaxSamples
    if len(AWG1) < MaxSamples:
        # split the buffer length in to upper and lower bytes
        UByte = (AWGBRecLength & 0x0000ff00) >> 8
        LByte = (AWGBRecLength & 0x000000ff)
        #
        SendStr = 'W l ' + str(UByte) + ' ' + str(LByte) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    else:
        UByte = (MaxSamples & 0x0000ff00) >> 8
        LByte = (MaxSamples & 0x000000ff)
        #
        SendStr = 'W l ' + str(UByte) + ' ' + str(LByte) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
    #    
    AWG1 = AWG1.tobytes()
    index = 0
    while index < AWGBRecLength:
        data = AWG1[index]
        # split the address index in to upper and lower bytes
        UByte = (index & 0x0000ff00) >> 8
        LByte = (index & 0x000000ff)
        # 
        SendStr = 'W s ' + str(UByte) + ' ' + str(LByte) + ' ' + str(data) + '\n'
        #
        SendByt = SendStr.encode('utf-8')
        ser.write(SendByt)
        index = index + 1
        
    ser.write(b'W p\n') # Send the waveform buffer to change the output waveform
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
        AWGAMakeFullWaveSine()
        AWGAShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGAShape.get()==10:
        AWGAMakeHalfWaveSine()
        AWGAShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGAShape.get()==11:
        AWGAMakeFourier()
        AWGAShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGAShape.get()==12:
        SetAwgSampleRate()
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
        NrTones = int(eval(AWGADutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGASendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGAShapeLabel.config(text = AwgString12) # change displayed value
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
        AWGBMakeFullWaveSine()
        AWGBShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGBShape.get()==10:
        AWGBMakeHalfWaveSine()
        AWGBShapeLabel.config(text = AwgString10) # change displayed value
    elif AWGBShape.get()==11:
        AWGBMakeFourier()
        AWGBShapeLabel.config(text = AwgString11) # change displayed value
    elif AWGBShape.get()==12:
        SetAwgSampleRate()
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
        AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
        NrTones = int(eval(AWGBDutyCycleEntry.get()))
        ampl = 3.0/NrTones
        if ampl > 0.25:
            ampl = 0.25
        AWGBSendWave(SchroederPhase(MaxSamples, NrTones, ampl))
        AWGBShapeLabel.config(text = AwgString12) # change displayed value
    else:
        AWGBShapeLabel.config(text = "Other Shape") # change displayed value
#
    time.sleep(0.01)
#
def SetAwgA_Ampl(Ampl):
    
    # Amplitude 8-bit integer (0-255) as percent 0 - 100%
    SendStr = 'W A ' + str(Ampl) + '\n' # Upper case A for AWG A
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    # print(SendByt)
    ser.write(SendByt) #
    # ser.write(b'W A 255\n')
#
def SetAwgB_Ampl(Ampl):
    
    # Amplitude 8-bit integer (0-255) as percent 0 - 100%
    SendStr = 'W a ' + str(Ampl) + '\n' # Lower case a for AWG B
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    # print(SendByt)
    ser.write(SendByt) #
    # ser.write(b'W a 255\n')
#
def SetAwgSampleRate():
    global AWGAFreqEntry, AWGBFreqEntry, FSweepMode
    global MaxSamples, MaxSampleRate, AWGSampleRate

    MaxRepRate = numpy.ceil(MaxSampleRate / MaxSamples)
    FreqA = UnitConvert(AWGAFreqEntry.get())
    FreqB = UnitConvert(AWGBFreqEntry.get())
    Cycles = 1
    if FSweepMode.get() == 1: # If doing a frequency sweep only make new AWG A sine wave
        if FreqA > MaxRepRate:
            Cycles = numpy.ceil(FreqA/MaxRepRate)
            #Cycles = Cycles + 1
            FreqA = FreqA/Cycles
    # Set the AWG buffer Rep rate (Freq for one cycle of buffer)
        SetAwgA_Frequency(FreqA)
        AWGRepRate = FreqA
        AWGSampleRate = FreqA * MaxSamples
    else:
        if FreqA <= FreqB:
            
            if FreqA > MaxRepRate:
                Cycles = numpy.ceil(FreqA/MaxRepRate)
                #Cycles = Cycles + 1
                FreqA = FreqA/Cycles
        # Set the AWG buffer Rep rate (Freq for one cycle of buffer)
            SetAwgA_Frequency(FreqA)
            AWGRepRate = FreqA
            AWGSampleRate = FreqA * MaxSamples
        else:
            if FreqB > MaxRepRate:
                
                Cycles = numpy.ceil(FreqB/MaxRepRate)
                #Cycles = Cycles + 1
                FreqB = FreqB/Cycles
        # Set the AWG buffer Rep rate (Freq for one cycle of buffer)
            AWGRepRate = FreqB
            SetAwgA_Frequency(FreqB)
            AWGSampleRate = FreqB * MaxSamples
def SetAwgA_Frequency(FreqANum):
    global MaxSamples
    #
    MagicNum = 0.09313225746 * (2048 / MaxSamples)
    PhaseValue = int( FreqANum / MagicNum )
    # Split the phase value 10737 into four bytes:
    F0 = (PhaseValue & 0xff000000) >> 24
    F1 = (PhaseValue & 0x00ff0000) >> 16
    F2 = (PhaseValue & 0x0000ff00) >> 8
    F3 = (PhaseValue & 0x000000ff)
    # print(F0, F1, F2, F3) # Upper case F for AWG A
    SendStr = 'W F ' + str(F0) + ' ' + str(F1) + ' ' + str(F2) + ' ' + str(F3) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    # print(SendByt)
    ser.write(SendByt) #
##
def SetAwgB_Frequency(FreqBNum):
    #
    PhaseValue = int(FreqBNum / 0.09313225746)
    # Split the phase value into four bytes:
    F0 = (PhaseValue & 0xff000000) >> 24
    F1 = (PhaseValue & 0x00ff0000) >> 16
    F2 = (PhaseValue & 0x0000ff00) >> 8
    F3 = (PhaseValue & 0x000000ff)
    # print(F0, F1, F2, F3) # Lower case f for AWG B
    SendStr = 'W f ' + str(F0) + ' ' + str(F1) + ' ' + str(F2) + ' ' + str(F3) + '\n'
    # print(SendStr)
    SendByt = SendStr.encode('utf-8')
    # print(SendByt)
    ser.write(SendByt) #
##
def AWGANoiseToggle():
    global AwgANoiseBt, ser

    if AwgANoiseBt.config('text')[-1] == 'ON':
        AwgANoiseBt.config(text='OFF', style="Stop.TButton")
        ser.write(b'W W\n')
    else:
        AwgANoiseBt.config(text='ON', style="Run.TButton")
        ser.write(b'W N\n')
#
def AWGA_Cycles():
    global ser, SAMPLErate, AWGAFreqvalue, AWGAFreqEntry
    global MaxSamples, AWGARecLength, MaxSampleRate, AWGSampleRate

    FreqA = UnitConvert(AWGAFreqEntry.get())
    # 
    # If requested Frequency is greater than MaxRepRate calculate number of cycles in buffer
    Cycles = 1
    # BufRepRate = FreqA
    MinRepRate = int(AWGSampleRate / MaxSamples)
    if FreqA > MinRepRate:
        Cycles = int(FreqA/MinRepRate)
        Cycles = Cycles + 1
        FreqA = FreqA/Cycles
    #
    if Cycles < 1:
        Cycles = 1
    #
    return(Cycles)
#
#
def AWGB_Cycles():
    global ser, SAMPLErate, AWGBFreqvalue, AWGBFreqEntry
    global MaxSamples, AWGBRecLength, MaxSampleRate

    FreqB = UnitConvert(AWGBFreqEntry.get())
    # If requested Frequency is greater than MaxRepRate calculate number of cycles in buffer
    Cycles = 1
    #BufRepRate = FreqB
    MaxRepRate = int(MaxSampleRate / MaxSamples)
    if FreqB > MaxRepRate:
        Cycles = int(FreqB/MaxRepRate)
        Cycles = Cycles + 1
        FreqB = FreqB/Cycles
    # Set the AWG buffer Rep rate (Freq for one cycle of buffer)
    SetAwgB_Frequency(FreqB)
    #
    if Cycles < 1:
        Cycles = 1
    #
    return(Cycles)
#
## Hardware Specific AUX DAC function
#
def UpdateAuxDAC():
    global AuxDACEntry, ser, AWGPeakToPeak

    DacVal = float(AuxDACEntry.get())
    if DacVal > AWGPeakToPeak:
        DacVal = AWGPeakToPeak
        AuxDACEntry.delete(0,"end")
        AuxDACEntry.insert(0, ' {0:.2f} '.format(4.08))
    if DacVal < 0.0:
        DacVal = 0.0
        AuxDACEntry.delete(0,"end")
        AuxDACEntry.insert(0, ' {0:.2f} '.format(0.0))
    # evalute entry string to a numerical value
    # representa a 8-bit number (0-255) sent to DAC
    # The DAC voltage is calculated as follows:
    DACValue = int((DacVal/AWGPeakToPeak)*255)
    # print(DACValue)
    # W X VAL 0 to 255 equals 0 to 4.0 V
    SendStr = 'W X ' + str(DACValue) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
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
#
# Hardware Specific function to control PWM digital output(s)
#
def UpdatePWM():
    global PWMDivEntry, PWMWidthEntry, ser

    DivVal = float(PWMDivEntry.get())
    if DivVal < 0:
        DacVal = 0
        PWMDivEntry.delete(0,"end")
        PWMDivEntry.insert(0, 0)
    # evalute entry string to upper and lower byte value
    HValue = int(DivVal/256)
    LValue = int(DivVal - (HValue * 256))
    # D F H_VAL L_VAL 
    SendStr = 'D F ' + str(HValue) + ' ' + str(LValue) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
    WidthVal = float(PWMWidthEntry.get())
    if WidthVal < 0:
        WidthVal = 0
        PWMWidthEntry.delete(0,"end")
        PWMWidthEntry.insert(0, 0)
    if WidthVal > 100:
        WidthVal = 100
        PWMWidthEntry.delete(0,"end")
        PWMWidthEntry.insert(0, 100)
    WValue = int((WidthVal/100)*255)
    SendStr = 'D D ' + str(WValue) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
#
# Hardware Specific digital output control function
#
def SetDigPin():
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on, D3_is_on, ser

    DigOut = 0
    if D0_is_on:
        DigOut = DigOut + 1
    if D1_is_on:
        DigOut = DigOut + 2
    if D2_is_on:
        DigOut = DigOut + 4
    if D3_is_on:
        DigOut = DigOut + 8
    if D4_is_on:
        DigOut = DigOut + 16
    # D O N, where N is the output byte value as an ascii 8 bit number
    SendStr = 'D O ' + str(DigOut) + '\n'
    SendByt = SendStr.encode('utf-8')
    ser.write(SendByt)
#
