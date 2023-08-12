#
# Hardware specific interface functions
# For PC Audio Line IN (7-15-2023)
# Written using Python version 3.11, Windows OS 
#
import pyaudio
#
# adjust for your specific hardware by changing these values
global DevID; DevID = "PC Audio"
global TimeSpan; TimeSpan = 0.001
CHANNELS = TRACESopened = 2 # Number of supported input channels
AWGChannels = 2 # Number of supported output channels
EnablePGAGain = 0 # 1
EnableOhmMeter = 0
EnableDmmMeter = 0
EnableDigIO = 0
#
AUDIOdevin = 1
AUDIOdevout = 6
SAMPLErate = 96000          # Sample rate of the soundcard 22050 44100 48000 88200 96000 192000
UPDATEspeed = 1.1           # Update speed, default 1.1, for slower PC's a higher value is perhaps required
ADsens1 = 1000              # Sensitivity of AD converter CH1 1 V = 1000 levels
ADsens2 = 1000
CH1probe = 1.0              # Probe attenuation factor 1x, 10x or 0.1x channel 1
CH2probe = 1.0
TRIGGERsample = 0           # Audio sample trigger point
TRIGGERlevel = 0            # Triggerlevel in samples
#
## Hardware specific Fucntion to close and exit ALICE
def Bcloseexit():
    global RUNstatus, Closed, PA, stream
    
    RUNstatus.set(0)
    Closed = 1
    # 
    try:
        # try to write last config file, Don't crash if running in Write protected space
        BSaveConfig("alice-last-config.cfg")
        stream.stop_stream()
        stream.close()
        PA.terminate()
        # exit
    except:
        donothing()

    root.destroy()
    exit()
#
# communications with Sound Card
#
def BAudiostatus():
    global AUDIOstatus
    global RUNstatus
    
    if (AUDIOstatus == 0):
        AUDIOstatus = 1
    else:
        AUDIOstatus = 0
#
def SetSampleRate():
    global SAMPLErate

    SAMPLErate = 96000
#
def get_data():
    global CHUNK, RUNstatus, TRACESopened, SAMPLErate, TMsb, UPDATEspeed
    global stream, PA, FORMAT, TRACESopened, AUDIOdevin, AUDIOdevout
    #
    TimeDiv = UnitConvert(TMsb.get())
    CHUNK = int( float(SAMPLErate) * TimeDiv * 15) # 15 divisions of data samples
    chunkbuffer = int(UPDATEspeed * CHUNK)
    if chunkbuffer < SAMPLErate / 10:       # Prevent buffer overload if small number of samples
        chunkbuffer = int(SAMPLErate / 10)
    # print("CHUNK ", CHUNK, "chunkbuffer ", chunkbuffer)
    #
    PA = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16

    stream = PA.open(format = FORMAT,
        channels = TRACESopened, 
        rate = SAMPLErate, 
        input = True,
        output = True,
        frames_per_buffer = int(chunkbuffer),
        input_device_index = AUDIOdevin,
        output_device_index = AUDIOdevout)
    
    signals = []
    n = -1
    # print("# ", int(CHUNK / chunkbuffer))
    while n < int(CHUNK / chunkbuffer):         # Number of required buffer readings 
        signals1 = stream.read(chunkbuffer) # Read samples from the buffer
        signals.extend(signals1)                # Append to signals
        n = n + 1
    
    # RUNstatus = 3   # Stop sweep, only one sweep for longsweeps

# Start conversion audio samples to values -32767 to +32767 (one's complement)
    TRACESread = TRACESopened   # How many traces, 1 or 2
    Lsignals = len(signals)     # Lenght of signals array
    # print("Length signals ", Lsignals)
    AUDIOsignal1 = []           # Clear the AUDIOsignal1 array for trace 1
    AUDIOsignal2 = []           # Clear the AUDIOsignal1 array for trace 2

    if TRACESread == 1:         # Conversion routine for 1 trace

        Sbuffer = Lsignals / 2  # Sbuffer is number of values (2 bytes per audio sample value, 1 channel is 2 bytes)
        i = 2 * int(Sbuffer - CHUNK)    # Start value, only last part is used

        if i < 0:       # Prevent negative values for i
            i = 0
        
        s = Lsignals - 1       
        while (i < s):
            v = int(signals[i]) + 256 * int(signals[i+1])
            if v > 32767:           # One's complement correction
               v = v - 65535
            AUDIOsignal1.append(v)  # Append the value to the trace 1 array 
            i = i + 2               # 2 bytes per sample value abd 1 trace is 2 bytes totally

    if TRACESread == 2:             # Conversion routine for 2 traces
        Sbuffer = Lsignals / 4      # Sbuffer is number of values (2 bytes per audio sample value, 2 channels is 4 bytes)
        i = 4 * int(Sbuffer - CHUNK)    # Start value, only last part is used

        if i < 0:                   # Prevent negative values for i
            i = 0
        
        s = Lsignals - 1       
        while (i < s):
            v = int(signals[i]) + 256 * int(signals[i+1])
            if v > 32767:           # One's complement correction
               v = v - 65535
            AUDIOsignal1.append(v)  # Append the value to the trace 1 array  

            v = int(signals[i+2]) + 256 * int(signals[i+3])
            if v > 32767:           # One's complement correction
                v = v - 65535
            AUDIOsignal2.append(v)  # Append the value to the trace 2 array  
            i = i + 4               # 2 bytes per sample value and 2 traces is 4 bytes totally
    # print("A Length ", len(AUDIOsignal1), "B Length ", len(AUDIOsignal2))
    return AUDIOsignal1, AUDIOsignal2
##
def Get_Data():
    global xscale, VBuffA, VBuffB, TRACESread, TRIGGERsample
    global ADsens1, CH1yoffset, ADsens2, CH2yoffset
    global Interp3Filter, InOffA, InOffB, InGainA, InGainB

    
# Get data from instrument
    VBuff1, VBuff2 = get_data()
#
    VBuffA = numpy.array(VBuff1)
    VBuffB = numpy.array(VBuff2)
    VBuffA = VBuffA / ADsens1 # Scale by audio card gain
    VBuffB = VBuffB / ADsens2
    VBuffA = (VBuffA - InOffA) * InGainA
    VBuffB = (VBuffB - InOffB) * InGainB
    TRACESread = 2
# Find trigger sample point if necessary
    LShift = 0
    if TgInput.get() == 1:
        FindTriggerSample(VBuffA)
    if TgInput.get() == 2:
        FindTriggerSample(VBuffB)
    if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
        # Average mode 1, add difference / TRACEaverage to array
        if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
            LShift = 0 - TRIGGERsample
            VBuffA = numpy.roll(VBuffA, LShift)
            VBuffB = numpy.roll(VBuffB, LShift)
            #TRIGGERsample = hozpos # set trigger sample to index 0 offset by horizontal position
#
## try to connect to Sound card
#
def ConnectDevice():
    global PA, FORMAT, DevID, MaxSamples, AWGSAMPLErate, SAMPLErate
    global bcon, FWRevOne, HWRevOne, stream, AUDIOdevin, AUDIOdevout
    global CH1Probe, CH2Probe, CH1VRange, CH2VRange, TimeDiv
    global CHAsb, CHBsb, TMsb, UPDATEspeed, TRACESopened
    global TgInput, TgEdge, TRIGGERlevel, TRIGGERentry

    if DevID == "No Device" or DevID == "PC Audio":
        #
        SELECTaudiodevice()
        TimeDiv = UnitConvert(TMsb.get())
        # Setup instrument
        PA = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHUNK = int(float(SAMPLErate) * TimeDiv * 15)
        chunkbuffer = int(UPDATEspeed * CHUNK)
        if chunkbuffer < SAMPLErate / 10: # Prevent buffer overload if small number of samples
            chunkbuffer = int(SAMPLErate / 10)
        #
        try:
            stream = PA.open(format = FORMAT,
                channels = TRACESopened, 
                rate = SAMPLErate, 
                input = True,
                output = True,
                frames_per_buffer = int(chunkbuffer),
                input_device_index = AUDIOdevin,
                output_device_index = AUDIOdevout)
        except:
            RUNstatus = 0
            txt = "Sample rate: " + str(SAMPLErate) + ", try a lower sample rate.\nOr another audio device."
            showerror("Cannot open Audio Stream", txt)
# print(dev)
        bcon.configure(text="Conn", style="GConn.TButton")
##
#
def SELECTaudiodevice():        # Select an audio device
    global AUDIOdevin, AUDIOdevout

    PA = pyaudio.PyAudio()
    ndev = PA.get_device_count()

    n = 0
    ai = ""
    ao = ""
    while n < ndev:
        s = PA.get_device_info_by_index(n)
        # print( n, s )
        if s['maxInputChannels'] > 0:
            ai = ai + str(s['index']) + ": " + s['name'] + "\n"
        if s['maxOutputChannels'] > 0:
            ao = ao + str(s['index']) + ": " + s['name'] + "\n"
        n = n + 1
    PA.terminate()

    AUDIOdevin = None
    
    s = askstring("Device","Select audio INPUT device:\nPress Cancel for Windows Default\n\n" + ai + "\n\nNumber: ")
    if (s != None):         # If Cancel pressed, then None
        try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
            v = int(s)
        except:
            s = "error"

        if s != "error":
            if v < 0 or v > ndev:
                v = 0
            AUDIOdevin = v

    AUDIOdevout = None

    s = askstring("Device","Select audio OUTPUT device:\nPress Cancel for Windows Default\n\n" + ao + "\n\nNumber: ")
    if (s != None):         # If Cancel pressed, then None
        try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
            v = int(s)
        except:
            s = "error"

        if s != "error":
            if v < 0 or v > ndev:
                v = 0
            AUDIOdevout = v
#
# AWG Stuff
#
def AWGANoiseToggle():
    donothing()
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
        AWGAShapeLabel.config(text = AwgString9) # change displayed value
    elif AWGBShape.get()==10:
        AWGAMakeHalfWaveSine()
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
# Trigger Stuff
#
def BSetTriggerSource():
    global TgInput
    donothing()
#
def BSetTrigEdge():
    global TgEdge
    donothing()
#
def BTriggerMode(): 
    global TgInput, ana_str
    donothing()
    
## evalute trigger level entry string to a numerical value and set new trigger level     
def SendTriggerLevel():
    global TRIGGERlevel, TRIGGERentry, RUNstatus

    # evalute entry string to a numerical value
    #
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
    
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
#
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TIMEdiv/HorzValue)

    # prevent divide by zero error
#    
def HCHAlevel():
    global CHAsb, RUNstatus, CH1vpdvLevel
    
    donothing()

def HCHBlevel():
    global CHBsb, RUNstatus, CH2vpdvLevel
    
    donothing()  
        
def HOffsetA(event):
    global CHAOffset, CHAVPosEntry, CH1vpdvLevel, RUNstatus

    NumberOfDiv = int(CHAOffset/CH1vpdvLevel)
    donothing()

def HOffsetB(event):
    global CHBOffset, CHBVPosEntry, CH2vpdvLevel, RUNstatus

    NumberOfDiv = int(CHBOffset/CH2vpdvLevel)
    donothing()
##
def CouplCHA():
    global CHAcoupl

    donothing()
#
def CouplCHB():
    global CHBcoupl

    donothing()
#
