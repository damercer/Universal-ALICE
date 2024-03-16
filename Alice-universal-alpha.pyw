#!/usr/bin/python
# -*- coding: cp1252 -*-
#
# Alice-universal-alpha.py(w) (3-15-2024)
# Written using Python version 3.10, Windows OS 
# Requires a hardware interface level functions add-on file
# Created by D Mercer ()
#
import __future__
import math
import time
#
try:
    import numpy
    numpy_found = True
except:
    numpy_found = False
#
# If runing from source you can un-comment the following to include pyplot
try:
    from matplotlib import pyplot as plt
    matplot_found = True
except:
    matplot_found = False
#
import csv
import wave
import os
import sys
import struct
import subprocess
from time import gmtime, strftime

# Check to see if user passed init file name on command line
if len(sys.argv) > 1:
    InitFileName = str(sys.argv[1])
    print( 'Init file name: ' + InitFileName )
else:
    InitFileName = 'alice_init.ini'

if sys.version_info[0] == 2:
    print ("Python 2.x")
    import urllib2
    import tkFont
    from Tkinter import *
    from ttk import *
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
    from tkSimpleDialog import askstring
    from tkMessageBox import *
    from tkColorChooser import askcolor
if sys.version_info[0] == 3:
    print ("Python 3.x")    
    import urllib.request, urllib.error, urllib.parse
    import tkinter
    from tkinter.font import *
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import *
    from tkinter.colorchooser import askcolor
#
import webbrowser
#
# check which operating system
import platform
#
RevDate = "15 March 2024"
SWRev = "1.0 "
#
# small bit map of triangle logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root=Tk()
root.title("ALICE Universal Alpha " + SWRev + RevDate)
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
print("Windowing System is " + str(root.tk.call('tk', 'windowingsystem')))
# Place holder for hardware functions file name:
HardwareFile = "Alice_Interface_Level.py"
CHANNELS = 1                # Number of Channel traces 1 to 4
AWGChannels = 1
AWGPeakToPeak = 5.0
AllowFlashFirmware = 0
TRACESread = 0              # Number of traces that have been read
## Window graphics area Values that can be modified
GRW = 720                   # Width of the time grid 720 default
GRH = 390                   # Height of the time grid 390 default
X0L = 55                    # Left top X value of time grid
Y0T = 25                    # Left top Y value of time grid
#
GRWF = 720                  # Width of the spectrum grid 720 default
GRHF = 390                  # Height of the spectrum grid 390 default
X0LF = 45                   # Left top X value of spectrum grid
Y0TF = 25                   # Left top Y value of spectrum grid
#
GRWBP = 720                 # Width of the Bode Plot grid 720 default
GRHBP = 390                 # Height of the Bode Plot grid 390 default
X0LBP = 45                  # Left top X value of Bode Plot grid
Y0TBP = 25                  # Left top Y value of Bode Plot grid
#
GRWXY = 500                 # Width of the XY grid 420 default
GRHXY = 470                 # Height of the XY grid 390 default
X0LXY = 55                  # Left top X value of XY grid
Y0TXY = 25                  # Left top Y value of XY grid
#
GRWIA = 400                 # Width of the grid 400 default
GRHIA = 400                 # Height of the grid 400 default
X0LIA = 37                  # Left top X value of grid
Y0TIA = 25                  # Left top Y value of grid
#
GRWNqP = 400                # Width of the Nyquist plot grid 400 default
GRHNqP = 400                # Height of the grid 400 default
X0LNqP = 25                 # Left top X value of grid
Y0TNqP = 25                 # Left top Y value of grid
#
GRWNiC = 400                # Width of the Nichols plot grid 400 default
GRHNiC = 400                # Height of the grid 400 default
X0LNiC = 25                 # Left top X value of grid
Y0TNiC = 25                 # Left top Y value of grid
#
GRWPhA = 400                # Width of the grid 400 default
GRHPhA = 400                # Height of the grid 400 default
X0LPhA = 37                 # Left top X value of grid
Y0TPhA = 25                 # Left top Y value of grid
# Analog Meter Variables
MGRW = 400                 # Width of the Analog Meter face 400 default
MGRH = 400                 # Height of the Analog Meter face 400 default
MXcenter = int(MGRW/2.0)   # Meter Center
MYcenter = int(MGRH/2.0)
MRadius = MXcenter - 50    # Meter Radius
Mmin = 0.0                 # Meter Scale Min Value
Mmax = 5.0                 # Meter Scale Max Value
MajorDiv = 10              # Meter Scale number of div
MinorDiv = 5
DialSpan = 270             # Number of degrees for analog meter dial
MeterLabelText = "Volts"
#
RDX0L = 20  # Left top X value of Res Div Schem
RDY0T = 20  # Left top Y value of Res Div Schem
RDGRW = 530 - ( RDX0L + 230 ) # Width of the Res Div Schem
RDGRH = 275 - ( 2 * RDY0T )   # Height of the Res Div Schem
R1 = StringVar()  
R2 = StringVar()
Voff = StringVar()
VR2 = StringVar()
ResDivStatus = IntVar()
ResDivStatus.set(0)
ResDivDisp = IntVar()
ResDivDisp.set(0)
SetResDivA = IntVar()
SetResDivB = IntVar()
SetResDivC = IntVar()
SetResDivD = IntVar()
SetResDivA.set(0)
SetResDivB.set(0)
SetResDivC.set(0)
SetResDivD.set(0)
Rint = 1.0E7 # 10 Meg Ohm internal resistor to ground
Cint = 1.25E-12 # ADC input switched capacitor value
RDeffective = Rint
RDGain = 1.0
RDOffset = 0.0
CHAIleak = 1.30917E-09 # 300E-9 # Channel A leakage current
CHBIleak = 1.30917E-09 # 300E-9 # Channel B leakage current
#
MinRes = 10
ADC_Cal = 5.0 # adjust for your hardware by changing this value in the alice.init file
LSBsizeA = LSBsizeB = LSBsizeC = LSBsizeD = LSBsize = ADC_Cal/4096.0
#
FontSize = 8
BorderSize = 1
MouseX = MouseY = -10
MouseCAV = MouseCBV = MouseCCV = MouseCDV = -10
## Colors that can be modified Use function to reset to "factory" colors
def ResetColors():
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline, COLORdial
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8
    
    COLORtext = "#ffffff"     # 100% white
    COLORtrigger = "#ff0000"  # 100% red
    COLORsignalband = "#ff0000" # 100% red
    COLORframes = "#000080"   # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
    COLORcanvas = "#000000"   # 100% black
    COLORgrid = "#808080"     # 50% Gray
    COLORzeroline = "#0000ff" # 100% blue
    COLORtrace1 = "#00ff00"   # 100% green
    COLORtrace2 = "#ff8000"   # 100% orange
    COLORtrace3 = "#00ffff"   # 100% cyan
    COLORtrace4 = "#ffff00"   # 100% yellow
    COLORtrace5 = "#ff00ff"   # 100% magenta
    COLORtrace6 = "#C80000"   # 90% red
    COLORtrace7 = "#8080ff"   # 100% purple
    COLORtrace8 = "#C8C8C8"     # 75% Gray
    COLORtraceR1 = "#008000"   # 50% green
    COLORtraceR2 = "#905000"   # 50% orange
    COLORtraceR3 = "#008080"   # 50% cyan
    COLORtraceR4 = "#808000"   # 50% yellow
    COLORtraceR5 = "#800080"   # 50% magenta
    COLORtraceR6 = "#800000"   # 80% red
    COLORtraceR7 = "#4040a0"  # 80% purple
    COLORtraceR8 = "#808080"  # 50% Gray
    COLORdial = "#404040"     # 25% Gray
#
ResetColors()
COLORwhite = "#ffffff" # 100% white
COLORblack = "#000000" # 100% black
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
GUITheme = "Light"
ButtonOrder = 0
SBoxarrow = 11
Closed = 0
ColorMode = IntVar()
# # Can be Light or Dark or Blue or LtBlue or Custom where:
FrameBG = "#d7d7d7" # Background color for frame
ButtonText = "#000000" # Button Text color
# Widget relief can be RAISED, GROOVE, RIDGE, and FLAT
ButRelief = RAISED
LabRelief = FLAT
FrameRelief = RIDGE
LocalLanguage = "English"
#
Power2 = [ 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
UseSoftwareTrigger = 0
# Set sample buffer size
HoldOff = 5
LShift = 0
SAMPLErate = MaxSampleRate = 818200 # Max Scope sample rate can be decimated
AWGSampleRate = MaxSampleRate
MinSamples = SHOWsamples = RecordLength = 1024
AWGARecLength = 2048
AWGBRecLength = 2048
MaxSamples = 2048
SMPfft = 4096
HardwareBuffer = 0
DISsamples = GRW
First_Slow_sweep = 0
Slow_Sweep_Limit = 200
# set initial trigger conditions
TRIGGERlevel = 2.0  # Triggerlevel in volts
## default math equations
MathString = "VBuffA + VBuffB"
MathUnits = " V"
MathXString = "VBuffA"
MathXUnits = " V"
MathYString = "VBuffB"
MathYUnits = " V"
UserAString = "MaxV1-VATop"
UserALabel = "OverShoot"
UserBString = "MinV2-VBBase"
UserBLabel = "UnderShoot"
MathAxis = "V-A"
MathXAxis = "V-A"
MathYAxis = "V-B"
#
FFTUserWindowString = "numpy.kaiser(SHOWsamples, 14) * 3"
DigFilterAString = "numpy.sinc(numpy.linspace(-1, 1, 91))"
DigFilterBString = "numpy.sinc(numpy.linspace(-1, 1, 91))"
#
ChaMeasString1 = "DCV1"
ChaMeasString2 = "DCV2"
ChaMeasString3 = "SV1"
ChaMeasString4 = "MaxV1-MinV1"
ChaMeasString5 = "MaxI1-MinI1"
ChaMeasString6 = "math.sqrt(SV1**2 - DCV1**2)"
ChbMeasString1 = "DCV3"
ChbMeasString2 = "DCV4"
ChbMeasString3 = "SV2"
ChbMeasString4 = "MaxV2-MinV2"
ChbMeasString5 = "MaxV3-MinV3"
ChbMeasString6 = "math.sqrt(SV2**2 - DCV2**2)"
ChaLableSrring1 = "CA-DCV "
ChaLableSrring2 = "CB-DCV "
ChaLableSrring3 = "CA-TRMS "
ChaLableSrring4 = "CA-VP-P "
ChaLableSrring5 = "CA-IP-P "
ChaLableSrring6 = "CA-ACRMS "
ChbLableSrring1 = "CC-DCV "
ChbLableSrring2 = "CD-DCV "
ChbLableSrring3 = "CB-TRMS "
ChbLableSrring4 = "CB-VP-P "
ChbLableSrring5 = "CC-VP-P "
ChbLableSrring6 = "CB-ACRMS "
LabelPlotText = IntVar()
PlotLabelText = "Custom Plot Label"
## defaukt trace width in pixels / number of averages
GridWidth = IntVar()
GridWidth.set(1)
TRACEwidth = IntVar()
TRACEwidth.set(1)
TRACEaverage = IntVar() # Number of average sweeps for average mode
TRACEaverage.set(8)
Vdiv = IntVar()
Vdiv.set(10)            # Number of vertical divisions for spectrum / Bode
Tdiv = IntVar()
Tdiv.set(10)            # Number of Horz Time divisions for scope
ZeroGrid = IntVar() # set which horizontal grid is time zero
ZeroGrid.set(0)
LPFTrigger = IntVar() # software triggering trigger lpf on/off
LPFTrigger.set(0)
Trigger_LPF_length = IntVar()
Trigger_LPF_length.set(10) # Length of software Trigger box car LPF in samples
# AWG waveform names:
AwgString0 = "DC"
AwgString1 = "Sine"
AwgString2 = "Square"
AwgString3 = "Triangle"
AwgString4 = "Pulse"
AwgString5 = "Ramp Down"
AwgString6 = "Ramp Up"
AwgString7 = "Stair Up"
AwgString8 = "Sinc"
AwgString9 = "Other"
AwgString10 = "Other"
AwgString11 = "Other"
AwgString12 = "Other"
AwgString13 = "Other"
AwgString14 = "Other"
AwgString15 = "Other"
AwgString16 = "Other"
#
IACMString = "+2.5"
IA_Mode = IntVar()
IA_Mode.set(0)
#
HarmonicMarkers = IntVar()
HarmonicMarkers.set(3)
AWGShowAdvanced = IntVar()
AWGShowAdvanced.set(0)
AWG_Amp_Mode = IntVar()
AWG_Amp_Mode.set(0) # 0 = Min/Max mode, 1 = Amp/Offset
#
Roll_Mode = IntVar() # select roll sweep (slow) mode
Roll_Mode.set(0)
#
UnAvgSav = IntVar() # Flag to save un trace averaged buffers
UnAvgSav.set(0)
ZEROstuffing = IntVar() # The zero stuffing value is 2 ** ZERO stuffing, calculated on initialize
ZEROstuffing.set(1)
FFTwindow = IntVar()   # FFT window function variable
FFTwindow.set(5)        # FFTwindow 0=None (rectangular B=1), 1=Cosine (B=1.24), 2=Triangular non-zero endpoints (B=1.33),
                        # 3=Hann (B=1.5), 4=Blackman (B=1.73), 5=Nuttall (B=2.02), 6=Flat top (B=3.77)
RelPhaseCorrection = 15 # Relative Phase error seems to be a random number each time board is powered up
RelPhaseCenter = IntVar()
RelPhaseCenter.set(0) # Center line value for phase plots
ImpedanceCenter = IntVar()
ImpedanceCenter.set(0) # Center line value for impedance plots
IgnoreFirmwareCheck = 0
EnableScopeOnly = 0
EnableXYPlotter = 1
EnablePhaseAnalizer = 1
EnableSpectrumAnalizer = 1
EnableBodePlotter = 1
EnableImpedanceAnalizer = 1
EnableOhmMeter = 1
EnableDmmMeter = 1
EnableDigIO = 1
EnableCommandInterface = 0
EnablePGAGain = 1
EnableLoopBack = 0
LoopBack = IntVar()
LoopBack.set(0)
LBList = ("CH A", "CH B", "CH C", "CH D")
EnableAWGNoise = 0 #
EnableDigitalFilter = 0
EnableInterpFilter = IntVar()
EnableInterpFilter.set(0)
EnableMeasureScreen = 0
EnableUserEntries = 0
CHANNELS = 2 # Number of supported Analog input channels
AWGChannels = 2 # Number of supported Analog output channels
PWMChannels = 0 # Number of supported PWM output channels
DigChannels = 0 # Number of supported Dig channels
LogicChannels = 0 # Number of supported Logic Analyzer channels
DeBugMode = 0
ShowTraceControls = 0
MouseFocus = 1
HistAsPercent = 0
ShowBallonHelp = 0
contloop = 0
discontloop = 0
AwgLayout = "Horz"
MarkerLoc = 'UL' # can be UL, UR, LL or LR
CHA_TC1 = DoubleVar()
CHA_TC1.set(1)
CHA_TC2 = DoubleVar()
CHA_TC2.set(1)
CHB_TC1 = DoubleVar()
CHB_TC1.set(1)
CHB_TC2 = DoubleVar()
CHB_TC2.set(1)
CHA_A1 = DoubleVar()
CHA_A1.set(1)
CHA_A2 = DoubleVar()
CHA_A2.set(1)
CHB_A1 = DoubleVar()
CHB_A1.set(1)
CHB_A2 = DoubleVar()
CHB_A2.set(1)
#
CHC_TC1 = DoubleVar()
CHC_TC1.set(1)
CHC_TC2 = DoubleVar()
CHC_TC2.set(1)
CHD_TC1 = DoubleVar()
CHD_TC1.set(1)
CHD_TC2 = DoubleVar()
CHD_TC2.set(1)
CHC_A1 = DoubleVar()
CHC_A1.set(1)
CHC_A2 = DoubleVar()
CHC_A2.set(1)
CHD_A1 = DoubleVar()
CHD_A1.set(1)
CHD_A2 = DoubleVar()
CHD_A2.set(1)
# 
#('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
# 'aqua' built-in native Mac OS X only; Native Mac OS X
windowingsystem = root.tk.call('tk', 'windowingsystem')
ScreenWidth = root.winfo_screenwidth()
ScreenHeight = root.winfo_screenheight()
# print(str(ScreenWidth) + "X" + str(ScreenHeight))
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    Style_String = 'aqua'
    # On Macs, allow the dock icon to deiconify.
    root.createcommand('::tk::mac::ReopenApplication', root.deiconify)
    root.createcommand('::tk::mac::Quit', root.destroy)# Bcloseexit)
    # On Macs, set up menu bar to be minimal.
    root.option_add('*tearOff', False)
    if sys.version_info[0] == 2:
        menubar = tKinter.Menu(root)
        appmenu = tKinter.Menu(menubar, name='apple')
    else:
        menubar = tkinter.Menu(root)
        appmenu = tkinter.Menu(menubar, name='apple')
    # menubar = tk.Menu(root)
    # appmenu = tk.Menu(menubar, name='apple')
    menubar.add_cascade(menu=appmenu)
    # appmenu.add_command(label='Exit', command=Bcloseexit)
    root['menu'] = menubar
else:
    Style_String = 'alt'
# Check if there is an alice_init.ini file to read in
try:
    import alice
    import pathlib
# pathlib only available as standard in Python 3.4 and higher. For Python 2.7 must manually install package
    path = pathlib.Path(alice.__file__).parent.absolute()
    filename = os.path.join(path, "resources", InitFileName) # "alice_init.ini")
    InitFile = open(filename)
    for line in InitFile:
        try:
            exec( line.rstrip(), globals(), globals())
            #exec( line.rstrip() )
        except:
            print("Skiping " + line.rstrip()) 
    InitFile.close()
except:
    try:
        InitFile = open(InitFileName) # "alice_init.ini"
        for line in InitFile:
            try:
                exec( line.rstrip(), globals(), globals())
                #exec( line.rstrip() )
            except:
                print("Skiping " + line.rstrip()) 
        InitFile.close()
    except:
        print( "No Init File Read. " + InitFileName + " Not Found")
#
XOLXY = X0L = FontSize * 7
XOLF = XOLBP = XOLIA = int(FontSize * 4.625)
XOLNqP = XOLNiC = int(FontSize * 3.125)
root.style = Style()
try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
if MouseFocus == 1:
    root.tk_focusFollowsMouse()
#
if sys.version_info[0] == 2:
    default_font = tkFont.nametofont("TkDefaultFont")
if sys.version_info[0] == 3:
    default_font = tkinter.font.nametofont("TkDefaultFont")
try:
    default_font.config(size=FontSize) # or .configure ?
except:
    print("Warning! Default Font Size was not set")
#
## Vertical Sensitivity list in v/div
CHvpdiv = ("1.0mV", "2.0mV", "5.0mV", "10.0mV", "20.0mV", "50.0mV", "100mV", "200mV", "330mV",
           "500mV", "1.0", "2.0","5.0", "10.0", "20.0", "50.0")
XYvpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.33, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0)
divfactor = {
    "m" : 1000, # milli 
    "u" : 1000000, # micro 
    "n" : 1000000000, # nano 
}
## SA Lin scale Max Min values
SAMagdiv = ("10nV", "100nV", "1uV", "10uV", "100uV", "1mV", "10mV", "0.1", "1.0", "10.0")
## Time list in s/div
TMpdiv = ("5us", "10us", "20us", "50us", "100us", "200us", "500us", "1.0ms", "2.0ms", "5.0ms",
          "10ms", "20ms", "50ms", "100ms", "200ms", "500ms", "1.0s", "2.0s", "5.0s")
# TMpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)
ResScalediv = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000)
ScopePGAGain = (1, 2, 4, 8, 16, 24, 32, 48, 50)
NoiseList = ("None", "Uniform", "Gaussian")
TimeDiv = 0.0002
RefPhase = ("CH-A", "CH-B", "CH-C", "CH-D")
#Interp8Filter = [0.083, 0.083, 0.084, 0.25, 0.25, 0.084, 0.083, 0.083]
Interp8Filter = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
Interp4Filter = [0.25, 0.25, 0.25, 0.25]
Interp3Filter = [0.333, 0.334, 0.333]
Interp2Filter = [0.5, 0.5]
## AWG variables
AWGAAmplvalue = 0.0
AWGAOffsetvalue = 0.0
AWGAFreqvalue = 100.0
AWGAPhasevalue = 0
AWGAdelayvalue = 0
AWGADutyCyclevalue = 50
AWGAWave = 'dc'

AWGACycles = 1
Reset_Freq = 300
MeasGateLeft = 0.0
MeasGateRight = 0.0 # in mSec
MeasGateNum = 0
MeasGateStatus = IntVar()
MeasGateStatus.set(0)
#
DCV1 = DCV2 = MinV1 = MaxV1 = MinV2 = MaxV2 = MidV1 = PPV1 = MidV2 = PPV2 = SV1 = SV2 = 0
DCV3 = DCV4 = MinV3 = MaxV3 = MinV4 = MaxV4 = MidV3 = PPV3 = MidV4 = PPV4 = SV3 = SV4 = 0
PeakVA = PeakVB = PeakVAB = PeakVC = PeakVD = 0.0
PeakfreqVA = PeakfreqVB = PeakfreqVC = PeakfreqVD = PeakfreqIAB = 0.0
PeakphaseVA = PeakphaseVB = PeakphaseVC = PeakphaseVD = PeakphaseVAB = PeakphaseIAB = 0.0
CHADCy = CHBDCy = CHCDCy = CHDDCy = 0
CHAperiod = CHAfreq = CHBperiod = CHBfreq = 0
CHCperiod = CHCfreq = CHDperiod = CHBfreq = 0
# Calibration coefficients
CHAVGain = CHBVGain = InGainA = InGainB = 1.0
CHAVOffset = CHBVOffset = 0.0
CHCVGain = CHDVGain = InGainC = InGainD = 1.0
CHCVOffset = CHDVOffset = 0.0
CHCpdvRange = CHDpdvRange = 0.500
# Initialisation of general variables
CHAOffset = CHBOffset = CHCOffset = CHDOffset = 2.5
InOffA = InOffB = InOffC = InoffD = 0.0
# Other global variables required in various routines
CANVASwidth = GRW + 2 * X0L # The canvas width
CANVASheight = GRH + Y0T + (FontSize * 7)     # The canvas height

VBuffA = []
VBuffB = []
VBuffC = []
VBuffD = []
VBuffG = []
MBuff = []
MBuffX = []
MBuffY = []
NoiseCH1 = []
NoiseCH2 = []
#
VUnAvgA = []
VUnAvgB = []
#
VAresult = []
VBresult = []
PhaseVA = []
PhaseVB = []
VCresult = []
VDresult = []
PhaseVC = []
PhaseVD = []
DFiltACoef = [1]
DFiltBCoef = [1]
DigFiltA = IntVar()
DigFiltA.set(0)
DigFiltABoxCar = IntVar()
DigFiltBBoxCar = IntVar()
DigDeSkewVA = IntVar()
DigDeSkewVB = IntVar()
DigDeSkewVC = IntVar()
DigDeSkewVD = IntVar()
DigFiltB = IntVar()
DigFiltB.set(0)
VFilterA = {}
VFilterB = {}
SampleRateStatus = IntVar()
#
VBuffA = numpy.ones(1024)
VBuffB = numpy.ones(1024)
VBuffC = numpy.ones(1024)
VBuffD = numpy.ones(1024)
MBuff = numpy.ones(1024)
MBuffX = numpy.ones(1024)
MBuffY = numpy.ones(1024)
VmemoryA = numpy.ones(1024)       # The memory for averaging
VmemoryB = numpy.ones(1024)
VmemoryC = numpy.ones(1024)       # The memory for averaging
VmemoryD = numpy.ones(1024)
TRACEresetTime = True           # True for first new trace, false for averageing
TRACEresetFreq = True           # True for first new trace, false for averageing
AWGScreenStatus = IntVar()
## Trace line Array Variables used
T1Vline = []                # Voltage Trace line channel A
T2Vline = []                # Voltage Trace line channel B
T3Vline = []                # Voltage Trace line channel C
T4Vline = []                # Voltage Trace line channel D
XYlineVA = []               # XY Trace lines
XYlineVB = []
XYlineVC = []
XYlineVD = []
XYlineM = []
XYlineMX = []
XYlineMY = []
XYRlineVA = []               # XY reference trace lines
XYRlineVB = []
XYRlineM = []
XYRlineMX = []
XYRlineMY = []
Tmathline = []              # Time Math trace line
TMXline = []                # Time X math Trace line
TMYline = []                # Time Y math Trace line
T1VRline = []               # V reference Trace line channel A
T2VRline = []               # V reference Trace line channel B
T3VRline = []               # V reference Trace line channel C
T4VRline = []               # V reference Trace line channel D
TMRline = []                # Math reference Trace line
Triggerline = []            # Triggerline
Triggersymbol = []          # Trigger symbol
D0line = []
D1line = []
D2line = []
D3line = []
D4line = []
D5line = []
D6line = []
D7line = []
# 
SCstart = 0                 # Start sample of the trace
HozPoss = 0.0
Is_Triggered = 0
#
ScreenTrefresh = IntVar()
ScreenXYrefresh = IntVar()
#
NSteps = IntVar()  # number of frequency sweep steps
NSteps.set(128)
LoopNum = IntVar()
LoopNum.set(1)
CurrentFreqX = X0LBP + 14
SAfreq_max = 100000
SAfreq_min = 1
SAnum_bins = 1024
FBinWidth = SAfreq_max / SAnum_bins
FStep = numpy.linspace(0, 1024, num=NSteps.get())
FSweepMode = IntVar()
FSweepCont = IntVar()
FStepSync = IntVar()
FSweepSync = IntVar()
ShowCA_VdB = IntVar()   # curves to display variables
ShowCA_P = IntVar()
ShowCB_VdB = IntVar()
ShowCB_P = IntVar()
ShowMarkerBP = IntVar()
ShowCA_RdB = IntVar()
ShowCA_RP = IntVar()
ShowCB_RdB = IntVar()
ShowCB_RP = IntVar()
ShowMathBP = IntVar()
ShowRMathBP = IntVar()
SingleShotSA = IntVar() # variable for Single Shot sweeps
FSweepAdB = []
FSweepBdB = []
FSweepAPh = []
FSweepBPh = []
NSweepSeriesR = []
NSweepSeriesX = []
NSweepSeriesMag = [] # in ohms 
NSweepSeriesAng = [] # in degrees
NSweepParallelR = []
NSweepParallelC = []
NSweepParallelL = []
NSweepSeriesC = []
NSweepSeriesL = []
NetworkScreenStatus = IntVar()
BDSweepFile = IntVar()
FileSweepFreq = []
FileSweepAmpl = []
#
MarkerNum = MarkerFreqNum = 0
ShowTCur = IntVar()
ShowVCur = IntVar()
TCursor = VCursor = 0
ShowXCur = IntVar()
ShowYCur = IntVar()
XCursor = YCursor = 0
ShowFCur = IntVar()
ShowdBCur = IntVar()
FCursor = dBCursor = 0
ShowBPCur = IntVar()
ShowBdBCur = IntVar()
BPCursor = BdBCursor = 0
RUNstatus = IntVar()       # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop
TRIGGERsample = 0           # AD sample trigger point
DX = 0                      # interpolated trigger point
## Spectrum Analyzer Values that can be modified
DBdivlist = [1, 2, 3, 5, 10, 15, 20]    # dB per division
DBdivindex = IntVar()      # 10 dB/div as initial value
DBdivindex.set(4)
DBlevel = IntVar()     # Reference level
DBlevel.set(0)
DBdivindexBP = IntVar()      # 10 dB/div as initial value
DBdivindexBP.set(4)
DBlevelBP = IntVar()     # Reference level
DBlevelBP.set(0)
hldn = 0
SpectrumScreenStatus = IntVar()
SmoothCurvesSA = IntVar()
SmoothCurvesBP = IntVar()
CutDC = IntVar()
IAScreenStatus = IntVar()
NqPScreenStatus = IntVar()
NqPDisp = IntVar()
NiCScreenStatus = IntVar()
NiCDisp = IntVar()
ImpedanceMagnitude  = 0.0 # in ohms 
ImpedanceAngle = 0.0 # in degrees 
ImpedanceRseries = 0.0 # in ohms 
ImpedanceXseries = 0.0 # in ohms
Show_Rseries = IntVar()
Show_Xseries = IntVar()
Show_Magnitude = IntVar()
Show_Angle = IntVar()
Show_RseriesRef = IntVar()
Show_XseriesRef = IntVar()
Show_MagnitudeRef = IntVar()
Show_AngleRef = IntVar()
## Impedance Analyzer sweep bode plot and reference line variables
TIARline = []
TIAXline = []
TIAMagline = []
TIAAngline = []
TIAMline = []
TIAMRline = []
RefIARline = []
RefIAXline = []
RefIAMagline = []
RefIAAngline = []
IASource = IntVar()
IAGridType = IntVar()
## In IA display series or parallel values
DisplaySeries = IntVar() 
IA_Ext_Conf = IntVar()
IA_Ext_Conf.set(0)
IASweepSaved = IntVar()
OverRangeFlagA = 0
OverRangeFlagB = 0
PeakdbA = 10
PeakdbB = 10
PeakRelPhase = 0.0
PeakfreqA = 100
PeakfreqB = 100
OhmStatus = IntVar()
OhmRunStatus = IntVar()
DMMRunStatus = IntVar()
FFTbandwidth = 0                # The FFT bandwidth
FFTBuffA = [] # Clear the FFTBuff array for trace A
FFTBuffB = [] # Clear the FFTBuff array for trace B
FFTresultA = []                 # FFT result CHA
PhaseA = []
FFTresultB = []                 # FFT result CHB
PhaseB = []
FFTresultAB = []
FFTwindowname = "--"            # The FFT window name
FFTmemoryA = numpy.ones(1)       # The memory for averaging
PhaseMemoryA = numpy.ones(1)
FFTmemoryB = numpy.ones(1)       # The memory for averaging
PhaseMemoryB = numpy.ones(1)
Two28 = 268435456
FFTwindowshape = numpy.ones(SMPfft) # The FFT window curve (Box Car)
## Frequency Array Variables
T1Fline = []                # Frequency Trace line channel A
T2Fline = []                # Frequency Trace line channel B
T1Pline = []                # Phase angle Trace line channel A - B
T2Pline = []                # Phase angle Trace line channel B - A
T1FRline = []               # F reference Trace line channel A
T2FRline = []               # F reference Trace line channel B
T1PRline = []               # Phase reference Trace line channel A - B
T2PRline = []               # Phase reference Trace line channel B - A
TFMline = []                # Frequency Math Trace
TFRMline = []               # Frequency reference Math Trace
FreqTraceMode = IntVar()   # 1 normal mode, 2 max hold mode, 3 average mode
FreqTraceMode.set(1)
## Bode Array Variables
TAFline = []                # Bode Freq Trace line channel A
TBFline = []                # Bode Freq Trace line channel B
TAPline = []                # Bode Phase angle Trace line channel A - B
TBPline = []                # Bode Phase angle Trace line channel B - A
TAFRline = []               # Bode F reference Trace line channel A
TBFRline = []               # Bode F reference Trace line channel B
TAPRline = []               # Bode Phase reference Trace line channel A - B
TBPRline = []               # Bode Phase reference Trace line channel B - A
TBPMline = []               # Bode Frequency Math Trace
TBPRMline = []              # Bode Frequency reference Math Trace
#
MinSamplesSA = 1024
MaxSamplesSA = 2048
#
MathScreenStatus = IntVar()
ColorScreenStatus = IntVar()
XYScreenStatus = IntVar()
DigScreenStatus = IntVar()
Xsignal = IntVar()   # Signal for X axis variable
Xsignal.set(1)
YsignalVA = IntVar()   # Signal for Y axis variable
YsignalVB = IntVar()
YsignalVC = IntVar()
YsignalVD = IntVar()
YsignalM = IntVar()
YsignalMX = IntVar()
YsignalMY = IntVar()
YsignalVB.set(1)
XYRefAV = IntVar()   # show reference XY traces
XYRefBV = IntVar()
XYRefM = IntVar()
XYRefMX = IntVar()
XYRefMY = IntVar()
# Analog DMM stuff
OnBoardRes = 1500
DMMStatus = IntVar()
DMMDisp = IntVar()
MAScreenStatus = IntVar()
# Digital flags
D0_is_on = False
D1_is_on = False
D2_is_on = False
D3_is_on = False
D4_is_on = False
D5_is_on = False
D6_is_on = False
D7_is_on = False
PWM_is_on = False
# Digital waveform buffers
DBuff0 = []
DBuff1 = []
DBuff2 = []
DBuff3 = []
DBuff4 = []
DBuff5 = []
DBuff6 = []
DBuff7 = []
## 25x25 bit map of high going pulse in .gif
hipulse = """
R0lGODlhGQAYAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/
/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm
AABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/
MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm
ZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/
mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm
zGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/
/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ
AJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA
M8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ
ZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A
mf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z
zP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///ywAAAAAGQAYAAAIZwAfCBxI
sKDBgw8AKFzIsKFChA4jMoQoUSJFAAgHLryYUeDGgx8zhiw4EuRDkxg7ltR4UmRLki9RclQZk2VK
lzdh5pTJE+dMnz1/6uyYsKZHowRXHt1pcGREohUbQo2qNKlDolgFBgQAOw==
"""
hipulseimg = PhotoImage(data=hipulse)
## 25x25 bit map of low going pulse in .gif
lowpulse = """
R0lGODlhGQAYAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/
/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm
AABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/
MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm
ZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/
mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm
zGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/
/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ
AJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA
M8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ
ZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A
mf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z
zP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///ywAAAAAGQAYAAAIZwAfCBxI
sKBBggASKgRwEOHChwsbDoRIkaHEBxQdWpSosGHHix8NhvSYkORGkyhBljw4kuVKkS9TwjzpkubE
mDVl6tR4ESPOmzYLtgTac6hAozxzqgzqkynRmhUhmoz6cCpVpD0vBgQAOw==
"""
lowpulseimg = PhotoImage(data=lowpulse)
# shaded round button widgets
round_red = 'iVBORw0KGgoAAAANSUhEUgAAABgAAAAZCAYAAAArK+5dAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAGHRFWHRTb2Z0d2FyZQBwYWludC5uZXQgNC4xLjFjKpxLAAAGfklEQVR42o1W6VNTVxR/Kv4Htp1xZA0JhCWsAQmQAC4Yd0GtKBqXUUAREBdE8pYAWVhUotVWVOpGpzpVqI51pnas+sFtOnXUmXY6o10sErYASUAgybun5yUEoWOnfvjNOe/dc35nufe9cymO4ygBLMt6JMey01mansmaTJS5sVFRrdlsrpq/0LVNEk62RkTB5vBIvjBKRiqyFz0zlpQydUeOUFU6HcVoaT8fzwQXYgo5yzDTWGGhtpYyFO+u2afK7EBSt0Yk5ncEBUGJvz+UInYEBZMtoRKyPSaOr1i67EEDTS+r1usphqan+4jfBXhHPp3FTKppes6hJUvvbhWHQ1FgEDQEBpAboiB4mhQPr5Sp8EqVCk8T4+F6oD8cDphDivwDoCRBDrrtO3RCYsjjN6UC1tcWJGcrKz8pT1X+tkMkhkZRiPNhYABvkUoBtmkIGGsBmj/3os5ARlfnkI7AYHgSEuxuCPQfLcKEKtZvqNLp3wURIJDPoIWIWu3H5WnKX4pDxXAlVDTWKZGABdswuGwZcTc1grPtKrifPPLA9e01cNYboTNeTrok4dApCSPtIcFju0NEsD9v/QEdtktot6cCbVXVTKPROKsmd83z3WIJ3BaLXD3SCOjAjXwtkcLQVg3wF88B/9MTICMjHgg6f74F+ubPh9fiMNIRKYPeiEhyJzTEWYYclRpNuQ7bhXviR9EGPVVfVsaUR8mgTSIe60PjjugY8kYWAx1hUrCvWwv8hRZwP3oIZKAfeAFCJWeboSctHTqkkfAG7f+OjgFrVDRpw9YeTEyCOi2diZ2ZTh0xmRIPZas7T4QE813RMt4Sm0A6ZbFgiY2HTnTqmZsCTqYKyDeXgdy/C/y9H4FcvQKOokLoxKQsMXFeW1ksQV+wREW7zKIQol3z6S0WW0XpC4qauNg4eC4Nhz48DZa4BOiKT/TAIkh07sUg9o35MHLoIIxUHYTB9XnQHY92k2y78Bl9iTVBzt8Xi3itUvXaVFc3m+Jy1wx8KQ3jrXHx0C1PJt1YXo882YtxvRsDd2Om3UjUgxD0CZtJEHz7kubCXzKZ67AsGuh9+6TUfiS+FxUBtpRU6MZMe1MUU9CH7/sUiNQ06EXZ69Px/b9thXb2pKSS/uRk/hxW0cTpzJQ+Jpq8iI2BAUUaLiq8ZON4F0QxQewL5LHxrU+yFzhsqN+QhEKLlgXqs8hw+D0pEWyqDOhPV0K/UuWFoOO7wQULYDA7GwbVarAtXjwB4Xlw4UIYmDcPrJP8+hBDGZnkVkQYmItLXNTRSKn7ZbIcHJmZSKiCgYwMGEDpIczJAVturgf298C3ZluxAgYxkOBnRf9h5PouXAJnOQ6oRkUKPEtKIMP40fRnZZEBXLTlrALH5s1g27QJ7AjHuJwCjcYjbRs3gh1t7fn5nor6szLJcNY8cgMPTuuRo72UYX3+D3cSYmF4vFzb8uVgLyoCe2GhBw5B/x/YBNtduzxBbQsWglWV7vpakQwGjlNStfsrdp5PTXFZM1XEplYTzIo4DhwAe3k5OPbu/SAItnaUtj17yFBODv9nstx9Mjvbom9omEXp6utmNK7Lu/04IY68VatdtoICcHAcsdM0OBjmw+C1JTaUb1evdt7FU2koKGDp6mr82XEsZaKZeedxc96kK9wjBYXEXl8PQwYDDBmNHwSHwUDsJiOM1NTwHco0d8uiRf26mtqPWIaeSQnjkaupoYy7issvyxPcg4vVo6NGI3GcOEGGjh4lw2YzDB879p8YamoijqYmGGludg9szHdez1CCWVddSnvnjN/EqGQwyKmS0kc38Mh2r1ox5jx5gn/b2gqOlhYyfPo0vAdk6MwZMnzxIjhbW139xTvh+0wVmLX0floYXiwzg500MqcJ/26TyTT78K5i/Vcpc+FFlgo3rtzlPHPWPXbtGhlpayOjbe3gwbU2MtbeDs7LV9x2g8H568rlcCkr4w8TTS/iqms843f8AjE+9McfGIbBPeGo45WHmLOrVva1yxPhUUY6vNyQ5+7aWei2Vh4gVm0l6dm7x/1yi8b1eIkarmMyp/LWPahmOZHgyzHMjMkXiYnhzHrlNKFvQol6nS7gWFlZ48k1a38+hx/fJSS6kJwE5xGCfhG/m9Mb8p9+wenqaGHYe5OcQj4lADc+pH2Ggq7FY8YZDFQ9w8h1FQfjb5qPPb9pPv6cQ/1wba2cw7tTlUCGSSGm+Tox+dryD68sSIU4MRj4AAAAAElFTkSuQmCC'
round_green = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAGHRFWHRTb2Z0d2FyZQBwYWludC5uZXQgNC4xLjFjKpxLAAAHAElEQVR42o1WaVBUVxZ+CvmbmuhEoUyMJMaJWCQGUNawLwINFEtkp4GGprsBW2Vp6O639M4iLVAzjomaURKNCCONsimKogwko6IwgnEJOEaBTCpJZRaTorvvmXtfwIAmVf746p5733fOd8/prnsOxXEctQCWZfmVYWhHjtVQ5toGSq1XyhMLBD3uca72V31ftq3zc4a1vqttb0W42LdlhfSUM7t3mGv3UizNUTTxWxRnAb9sWG5egHHQafQUyzErU4oSO92iNjzGQZGT90totd+L4ByMEfgiOPn8Dr3iswq5hr/xY3xeVKfGyPrpdQbeH8dZtljoaQFHvdZAFVVIpO6xrg+cvV+CteEr4G2RM8Sa3EF6JBZ2tiSB/FgCpDb5god8Dbwev5IIgnvcRpCWi6XEX62ml2bypEQs42jQGSlhcYZkfcgaWBe6Crx2rLNG/PE1pOhNRGe/bEafP+yCGzP9cG26DwYfnERcfyaKOeCCgrg3rOtjV1ldApwhT55Vuaduz+/VtPpJRgsCDlpcIpFcKHEJcoKN8Wus2+o22NJb3CDz+GZ0/LoZrjzogy++vgpffX8PJr8dh5szQ9A5cQiyPvVA6S1vQ9JHrsij8JU5l5DVUKQS9xrxhXFllvOZkAw0nJZS6RRit5j14Jb66lzSQVd7TpsHpB99B0naAqD3djOMzw7DN/99BHZkh8dz/4H7303A36ZOQYklHNKOuiHhCQ+U3fouCqRdfno91GkutyRLRkqH/0QOFE3TDgaDfkV0XvDsxgRn2/uH3Gyi9i0gbPEkjpDTtgUs4x/AxOxnMPPv+/CT9TH88OO3vMiFeycg/68+IDzhDjknPHmIOjyRf7mLzSPxLWD0aj+WYZdRRl01JVfLmE2CtRBrdp0rPO0Nea1bUf5JLyg46Q3C1nfB0J8LQ//sgjv/GoEH39+GKVyusZlBMF8uxgKbeR7hi9q2ImLntHpaN2evQcni2FMkPlVfY14uyA275lPyml122s8mtfgjqcUPZB3+TyCx+IDyTCL85aoWOnBWLaP1oO/PBkm7D0gX8YiftN0PlXS/Z4+q2WAPTPO8X1tT60Tpa7nS4GzPx0n73GBHdyCSWfyh6NR7z6DQ4g0F7Vt5W4JtcbvXr/KIWPHpAMg9vsXqlfMmlCl2v0ml5Sdy/uI/gAzfYldXEMg7A2EnXpciGH/D6A7h97u6f7GfBu/fGYR29gTZfYvX2bU17F4qs3B7Q7hiEyo9GwJlvWGorDcUys+EPQHZl86fVZwNh6q+SKjsi4CKM+FQ3hsGpT0hsNiH2GU9oaA4Hw4R9AbQmKuAKtidfSbe8A6oLm7jAxAoz2H73M82czEGqoeTof5KKjRcS4em65k8iE3OTEPJPIf3PTfvezYS6EvRSGByBbm6YI5KFSUp4vWbkXogClTnopDqPF4xmAsx0HA1HfaP5sIHY3nPYOH8wzERbzdcycA+AlCe5+MAe1kAAv0m0NbjTPKKMw1xKg8gIuxALL6VALiBONh/IwcO3RTDARzkwD/yfxtj+TyHcP+MfTSX4oG+IEDaoTgUzbnaG/fVfkM1NppLkxVB/9t1OhiZhpOQ5lIc+tOIED6ZkMHhm4VwZFwCRyak8+u8/fQe24T7MfbZd10IussJWCjGmkB7A6dhfKk6Y/2ygsrUGzkHvaB+JMVG6v/xRBF8+sUOOHarhF+fBwvc5nEZMl9Ls8stQbbtZWGPak17VlLk3dJVs/KEKi8rezHW2jiSgY7fkqO2O7uh9fYuIOvzYJ6LWm7JoWk0Yy5t7xYoqhBVajkdRbrZC8SQKrP60vGHxtEMKyF23C1H7XfLoONe+XOh/W4pstzB/KlyW0V3hC1TGTmr0+pWkB6FOyC7HL/5Dhod5yxUCr4u+MjfdvhO4VzvpAq6vqxEGNA9WYWh/A1UQSfh3auE8w9Zm/nzlDlhdSjoa1gxx3AkvsNCb1/O4oO6BpM4j40G8eEAOHq7yHrxoQb1T3Gob5JGfVM0/Ar4bwNfadHAtMZqHkwDkTkCOKNSQmYEFvcp0nWJ0rwQg7sYRxmrdYHZFdEjWWZfqO5PsZ6aLLcOTuvtwzMmNDRtRMPTJsDAqxE+mzWhS9M627GxEmvp0UjIVEWOaHVsIPmdcTy+YZH4S6YUkhpDs5RGy60s04u70lQBkNPkB4rWaGgaFNoOXS20fTJaDM3XZfYP/55vM/a8by8+GAapWvyoMpldHB4+SEX4DBbFfWYc4rAQyYi0Y41B5S9ns7tzlNGPUmk/SGF9IFntBdsZH0jFEDIRINdlDxnr2RINq+MHEnLRp8eiJVMFSY3lJxcWl45x5MVYA2UwGBxprcKd1ii2Nnc0gXm/bl8VXeZeU2dw02tMFMke+zrypf9ZaEnc/wNvUH/BVaIfLQAAAABJRU5ErkJggg=='
round_orange = 'iVBORw0KGgoAAAANSUhEUgAAABgAAAAZCAYAAAArK+5dAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAGHRFWHRTb2Z0d2FyZQBwYWludC5uZXQgNC4xLjFjKpxLAAAGzklEQVR42o2W+1dTVxbHr6+/wIJj0LRCYUZ88JRQFJTBB2q1yzrooCjIq8griIAxyc3NDXmQF/JQQNuq1Qqo1IK2S9GO1XbGcYpWxzVWZK2xRYUEE5JAEALJPXvOvQnodKar/eGz9j53f/c+9+ys3H0IuVxOsFAUxVk5RU2nSHIWpdURNXp9nCJtR614RZw7MyAAZQTwIYM3H3L4fCRfk+TW5eXWNjU2xkmVKkKGc3D+dMpXb5L/Kk7JZNM4gVJJqPPzKstjY55nzud7Mng8JmeeHxQHzubIxX7G3LlMzluBSLQq4SdaWLSJVqkJKSnFdahpUy/LbfCq+HSKVhAKUjpPkpx0I2vu72Av3w/0cXNQx5950CVaBt3qROjWJMKdgzFwMTUADMv9Ud682ZAdwAPDnrQbRqNxvlgiYetNmzwJQU22BRenxKI5+wXhj3MD/EAXHzDxj0I+Y6oMgqHm3Wj021oY7TrlBfuOlnTUj2NdxW8yxpW88VzebKjLyXhsqDb6k1LpDFyTOwlbfAbJnoKU+pcJwn8oWOAP57a/OW5ShcCAMgiZj72HHN80wciDL2Cs9y4H6ztuHgHToQQ0oHwbmTW/h/ad/DFhoB+QO7ZXU7hdbEe4E0glklmaqqo3VFvWPygOmgPXcoPcVn0o9KkXoWeKYLC25sHI3bPgenYPmAkXh+v5fXDeaYGBpo3wnH4baxejQX0o+jovcKIk2B+ku1JLaRX3w88kpGoNod9XICsLnQ9tOwPHbTVLoU8Xhkz6cOjXLATLJ6l4g1Zw9XYBM+rgcPXeAWdXMww0JkN/VSiY9GHQp10K9rpwdCVrgVscFQxaUpyIOzOdqNZVRZOrl/cbEniMyRjGmKujUL8xAszVkWAyRoL5UBTYOspwWy7C2JNbHCP/vAj2Swdxi6LBVD2pjUD92FrrI90nNgUg6XsbLlMaDUHo9mbUiKKD4UZRCNiOxHBJ5ppoGKhdxmGuieKwNqeB47IcHFfkYG1J5zTs8ykdxlQTjSyHBUw39QdGnRzxVKPV8QjNlnX2qsQFTK8hAiwN76CBegEMHI59jXe81OFi9TFeWB/HXnCx17Q411wfC7YmgbttRxAcKBIuJCpwv05uCwHrUSxuXIFZDi+aVvwPlqPx2Mb71vFg+T8aFnPDcmT/OIH5riyYOSSuqCVEghDUnr0QHMcTYODYSnhxLAEsH670wvq4MGdxzPrRKrAeTwQLtt5nvtik/kNvvg1rejRh0CorAuKgIBg6ixbD8KerwXJyNQx+4uNkEgyeWgO2s5vA/tlWsH+eAo6ObWBr3w72C9vw+k9gb9sCtuYNr3Kw3oqt/dO16GmdAE6UprkJSVyIp7NoCTibcfC1DeznNoPj4nZwfLEDhl7n0ivfG0sFB97MdmY92Hy5jjPr4GldDJxXCoFQrw2HjrwlyHluPfs2yHYmGSdshaFrGeDo3A1Dnbswu3+ZKzh+NZ2z9tZ38UbJyNm2GT3WRzHnDJSF0Kdv/up02kIYbE7Ggo24He/D8I0sTCYMf50JTuz/GpzuZhbeJA1sLRvB2bbJfVcRC4qDogTCcKA4vyFlqfunxkQ0fOF9NNS5E43c+gCcf82Gkb/l/CYmtc5vs5Hj8xTG0ZLsaSteaZKr9G8QtFY/49Ced6/9ZX8YGrmU4h6+ngEv7+Sjka692GK6fgPfcRY5b38AL6+mTTzUxYIuP5UiK1UEIZErCC0pSjqdHgHPPl7jGbuZhV7eL4TRewUwep+l8Ne5V4BeYr3rfiHzomWDp7UgwUZTtB9FyWbhzyoejwoloSvJLL2QHeqxd2x1jT8UotFHJWjsByFydZeAq3vfLzL2CGsfCmHiSQUavr5z4lp5LNTRohISzxc5JZs5NSplChVxvHzX7SuFS8DSnjLO/Luccf1YAWM9pcjVUwqunv0/o9Qbe1IOqE/M2K/vGr8uioN62f4Kkq7EY1g2g5qcyeyIY7/dVVotr0aYprqQuxgeNSTByO0cN9N7wMOYJMjTL8ZIwIsYMWYJQv0Sz9i/itw9J9bBlyUCOEyVidnichk503eB8A1930JGygj2aA2UUHY6N956Gf8B7+rj4cfzWz2Wr3Z77LeykOPv2Wjwmz2eZ+0pnns1q+Dqvgg4lZ/UpyXL11OKSrbleJJRUxeJqenvG9LT2L6RtJJQVcr5Ryr2GD7K/eP3rZkR0Ja5CM5nefksexGczY6G43lrvz8m3Wuo0qj5Uormxq/3lvKza8vkcSgOOUFjIetLaBVBqbSEnhYto0X7IjuPKh6w0AdKIo1KcplcrSPE8kpCJiPZ6wp3J/K++atry38AI6a42QLVvMIAAAAASUVORK5CYII='

if sys.version_info[0] == 3:
    RoundRedBtn = PhotoImage(data=round_red)
    RoundGrnBtn = PhotoImage(data=round_green)
    RoundOrBtn = PhotoImage(data=round_orange)
#
# Import Hardware Specific control I/O functions:
#
if DeBugMode == 2:
    exec( open(HardwareFile).read() )
else:
    try:
        exec( open(HardwareFile).read() )
    except:
        root.update()
        showwarning("WARNING","Trouble Reading Hardware Specific File!")
        HardwareFile = askopenfilename(defaultextension = ".py", filetypes=[("Hardware File:", "*.py")])
        if HardwareFile == None:
            root.destroy()
            exit()
        else:
            try:
                exec( open(HardwareFile).read() )
            except:
                root.update()
                showwarning("WARNING","Trouble Reading Hardware Specific File!")
                root.destroy()
                exit()
#print("Traces = ", CHANNELS)
## Tool Tip Ballon help stuff
class CreateToolTip(object):
    ## create a tooltip for a given widget
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 100   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
    ## Action when mouse enters
    def enter(self, event=None):
        self.schedule()
    ## Action when mouse leaves
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    ## Sehedule Action
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
    ## Un-schedule Action
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    ## Display Tip Text
    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                    background="#ffffe0", foreground="#000000",
                    relief='solid', borderwidth=1,
                    wraplength = self.wraplength)
        label.pack(ipadx=1)
    ## Hide Tip Action
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
    ## Re Configure text string
    def configure(self, text):
        self.text = text
#
# Converts a numeric string with "M" e6 or "k" e3 or "m" e-3 or "u" e-6
# to floating point number so calculations can be done on the user inputs
def UnitConvert(Value):
    
    Value = str.strip(Value,'V')
    Value = str.strip(Value,'s')
    if 'K' in Value:
        Value = str.strip(Value,'K') #
        Value = float(Value) * math.pow(10,3)
    elif 'k' in Value:
        Value = str.strip(Value,'k') #
        Value = float(Value) * math.pow(10,3)
    elif 'm' in Value:
        Value = str.strip(Value,'m') #
        Value = float(Value) * math.pow(10,-3)
    elif 'M' in Value:
        Value = str.strip(Value,'M') #
        Value = float(Value) * math.pow(10,6)
    elif 'u' in Value:
        Value = str.strip(Value,'u') #
        Value = float(Value) * math.pow(10,-6)
    elif 'n' in Value:
        Value = str.strip(Value,'n') #
        Value = float(Value) * math.pow(10,-9)
    else:
        Value = float(Value)
    return Value
# Take just integer part of digits
def UnitIntConvert(Value):
    
    Value = str.strip(Value,'V')
    Value = str.strip(Value,'s')
    if 'K' in Value:
        Value = str.strip(Value,'K') #
        Value = int(Value) * 1000
    elif 'k' in Value:
        Value = str.strip(Value,'k') #
        Value = int(Value) * 1000
    elif 'm' in Value:
        Value = str.strip(Value,'m') #
        Value = int(Value) * 0.001
    elif 'M' in Value:
        Value = str.strip(Value,'M') #
        Value = int(Value) * 1000000
    elif 'u' in Value:
        Value = str.strip(Value,'u') #
        Value = int(Value) * 0.000001
    elif 'n' in Value:
        Value = str.strip(Value,'n') #
        Value = int(Value) * 0.000000001
    else:
        Value = int(Value)
    return Value
#
# =========== Start widgets routines =============================
## Save current configureation to file
#
def BSaveConfig(filename):
    global TgInput, TgEdge, ManualTrigger, SingleShot, AutoLevel, SingleShotSA
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, AutoCenterA, AutoCenterB
    global YsignalVA, YsignalVB, YsignalM, YsignalMX, YsignalMY
    global CHAsb, CHBsb, CHMsb, HScale, FreqTraceMode
    global CHAsbxy, CHCsbxy, CHBsbxy, CHDsbxy, CHANNELS
    global CHAVPosEntryxy, CHBVPosEntryxy, CHMXPosEntry, CHMYPosEntry
    global ShowC1_V, ShowC3_v, ShowC2_V, ShowC24_V, MathTrace, MathXUnits, MathYUnits
    global CHAVPosEntry, CHCVPosEntry, CHBVPosEntry, CHDVPosEntry, CHMVPosEntry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGAMode
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGASymmetryEntry, AWGBShape, AWGBMode, AWGSync
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1, MeasDCV3, MeasMinV3
    global MeasMaxV3, MeasMidV3, MeasPPV3, MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2
    global MeasPPV2, MeasDCV4, MeasMinV4, MeasMaxV4, MeasMidV4, MeasPPV4, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasRMSV3, MeasRMSV4, MeasPhase
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ, IASource, DisplaySeries
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC, DacScreenStatus, DigScreenStatus
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, XYScreenStatus, IAScreenStatus, SpectrumScreenStatus
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry, AWGAPhaseDelay, AWGBPhaseDelay
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasDelay
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry, HozPossentry
    global SmoothCurvesBP, bodewindow, AWG_Amp_Mode, ColorMode
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMarkerBP, BodeDisp
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP, ShowMathBP, ShowRMathBP
    global BPSweepMode, BPSweepCont, BodeScreenStatus, RevDate, SweepStepBodeEntry
    global HScaleBP, StopBodeEntry, StartBodeEntry, ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global MathAxis, MathXAxis, MathYAxis, Show_MathX, Show_MathY, MathScreenStatus, MathWindow
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global RelPhaseCenter, ImpedanceCenter, NetworkScreenStatus
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global Show_Rseries, Show_Xseries, Show_Magnitude, Show_Angle
    global AWGBPhaseEntry, AWGChannels
    global DigFiltStatus, DigFiltABoxCar, DigFiltBBoxCar, BCALenEntry, BCBLenEntry
    global phawindow, PhAca, PhAScreenStatus, PhADisp
    global GRWPhA, X0LPhA, GRHPhA, Y0TPhA, BoardStatus, boardwindow, BrdSel
    global VScale, IScale, RefphEntry, EnableScopeOnly, Roll_Mode
    global vat_btn, vbt_btn, vct_btn, vdt_btn, vabt_btn
    global ScreenWidth, ScreenHeight
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8
    # open Config file for Write?
    try:
        ConfgFile = open(filename, "w")
    except: # didn't work? then just return
        return
    # Save Window placements
    ConfgFile.write("root.geometry('+" + str(root.winfo_x()) + '+' + str(root.winfo_y()) + "')\n")
    if EnableScopeOnly == 0:
        if AWGChannels >=1:
            ConfgFile.write("awgwindow.geometry('+" + str(awgwindow.winfo_x()) + '+' + str(awgwindow.winfo_y()) + "')\n")
    ConfgFile.write('GRW = ' + str(GRW) + '\n')
    ConfgFile.write('GRH = ' + str(GRH) + '\n')
    ConfgFile.write('ColorMode.set(' + str(ColorMode.get()) + ')\n')
    # Windows configuration
    ConfgFile.write('MathString = "' + MathString + '"\n')
    ConfgFile.write('MathUnits = "' + MathUnits + '"\n')
    ConfgFile.write('MathAxis = "' + MathAxis + '"\n')
    ConfgFile.write('MathXString = "' + MathXString + '"\n')
    ConfgFile.write('MathXUnits = "' + MathXUnits + '"\n')
    ConfgFile.write('MathXAxis = "' + MathXAxis + '"\n')
    ConfgFile.write('MathYString = "' + MathYString + '"\n')
    ConfgFile.write('MathYUnits = "' + MathYUnits + '"\n')
    ConfgFile.write('MathYAxis = "' + MathYAxis + '"\n')
    # Save Color Def
    ConfgFile.write('COLORtext = "' + COLORtext + '"\n')
    ConfgFile.write('COLORcanvas = "' + COLORcanvas + '"\n')
    ConfgFile.write('COLORtrigger = "' + COLORtrigger + '"\n')
    ConfgFile.write('COLORsignalband = "' + COLORsignalband + '"\n')
    ConfgFile.write('COLORframes = "' + COLORframes + '"\n')
    ConfgFile.write('COLORgrid = "' + COLORgrid + '"\n')
    ConfgFile.write('COLORtrace1 = "' + COLORtrace1 + '"\n')
    ConfgFile.write('COLORtraceR1 = "' + COLORtraceR1 + '"\n')
    ConfgFile.write('COLORtrace2 = "' + COLORtrace2 + '"\n')
    ConfgFile.write('COLORtraceR2 = "' + COLORtraceR2 + '"\n')
    ConfgFile.write('COLORtrace3 = "' + COLORtrace3 + '"\n')
    ConfgFile.write('COLORtraceR3 = "' + COLORtraceR3 + '"\n')
    ConfgFile.write('COLORtrace4 = "' + COLORtrace4 + '"\n')
    ConfgFile.write('COLORtraceR4 = "' + COLORtraceR4 + '"\n')
    ConfgFile.write('COLORtrace5 = "' + COLORtrace5 + '"\n')
    ConfgFile.write('COLORtraceR5 = "' + COLORtraceR5 + '"\n')
    ConfgFile.write('COLORtrace6 = "' + COLORtrace6 + '"\n')
    ConfgFile.write('COLORtraceR6 = "' + COLORtraceR6 + '"\n')
    ConfgFile.write('COLORtrace7 = "' + COLORtrace7 + '"\n')
    ConfgFile.write('COLORtraceR7 = "' + COLORtraceR7 + '"\n')
    ConfgFile.write('COLORtrace8 = "' + COLORtrace8 + '"\n')
    ConfgFile.write('COLORtraceR8 = "' + COLORtraceR8 + '"\n')
    #
    if MathScreenStatus.get() > 0:
        ConfgFile.write('NewEnterMathControls()\n')
        ConfgFile.write("MathWindow.geometry('+" + str(MathWindow.winfo_x()) + '+' + str(MathWindow.winfo_y()) + "')\n")
    else:
        ConfgFile.write('DestroyMathScreen()\n')
    if XYScreenStatus.get() > 0:
        ConfgFile.write('GRWXY = ' + str(GRWXY) + '\n')
        ConfgFile.write('GRHXY = ' + str(GRHXY) + '\n')
        ConfgFile.write('MakeXYWindow()\n')
        ConfgFile.write("xywindow.geometry('+" + str(xywindow.winfo_x()) + '+' + str(xywindow.winfo_y()) + "')\n")
        if CHANNELS >= 1:
            ConfgFile.write('CHAsbxy.delete(0,END)\n')
            ConfgFile.write('CHAsbxy.insert(0, ' + CHAsbxy.get() + ')\n')
            ConfgFile.write('CHAVPosEntryxy.delete(0,END)\n')
            ConfgFile.write('CHAVPosEntryxy.insert(4, ' + CHAVPosEntryxy.get() + ')\n')
        if CHANNELS >= 2:
            ConfgFile.write('CHBsbxy.delete(0,END)\n')
            ConfgFile.write('CHBsbxy.insert(0, ' + CHBsbxy.get() + ')\n')
            ConfgFile.write('CHBVPosEntryxy.delete(0,END)\n')
            ConfgFile.write('CHBVPosEntryxy.insert(4, ' + CHBVPosEntryxy.get() + ')\n')
        if CHANNELS >= 3:
            ConfgFile.write('CHCsbxy.delete(0,END)\n')
            ConfgFile.write('CHCsbxy.insert(0, ' + CHCsbxy.get() + ')\n')
            ConfgFile.write('CHCVPosEntryxy.delete(0,END)\n')
            ConfgFile.write('CHCVPosEntryxy.insert(4, ' + CHCVPosEntryxy.get() + ')\n')
        if CHANNELS >= 4:
            ConfgFile.write('CHDsbxy.delete(0,END)\n')
            ConfgFile.write('CHDsbxy.insert(0, ' + CHDsbxy.get() + ')\n')
            ConfgFile.write('CHDVPosEntryxy.delete(0,END)\n')
            ConfgFile.write('CHDVPosEntryxy.insert(4, ' + CHDVPosEntryxy.get() + ')\n')
        
        ConfgFile.write('CHMXsb.delete(0,END)\n')
        ConfgFile.write('CHMXsb.insert(0, ' + CHMXsb.get() + ')\n')
        ConfgFile.write('CHMXPosEntry.delete(0,END)\n')
        ConfgFile.write('CHMXPosEntry.insert(4, ' + CHMXPosEntry.get() + ')\n')
        ConfgFile.write('CHMYsb.delete(0,END)\n')
        ConfgFile.write('CHMYsb.insert(0, ' + CHMYsb.get() + ')\n')
        ConfgFile.write('CHMYPosEntry.delete(0,END)\n')
        ConfgFile.write('CHMYPosEntry.insert(4, ' + CHMYPosEntry.get() + ')\n')      
    else:
        ConfgFile.write('DestroyXYScreen()\n')
    if IAScreenStatus.get() > 0:
        ConfgFile.write('GRWIA = ' + str(GRWIA) + '\n')
        ConfgFile.write('GRHIA = ' + str(GRHIA) + '\n')
        ConfgFile.write('MakeIAWindow()\n')
        ConfgFile.write("iawindow.geometry('+" + str(iawindow.winfo_x()) + '+' + str(iawindow.winfo_y()) + "')\n")
        ConfgFile.write('IASource.set(' + str(IASource.get()) + ')\n')
        ConfgFile.write('DisplaySeries.set(' + str(DisplaySeries.get()) + ')\n')
        ConfgFile.write('RsystemEntry.delete(0,END)\n')
        ConfgFile.write('RsystemEntry.insert(5, ' + RsystemEntry.get() + ')\n')
        ConfgFile.write('ResScale.delete(0,END)\n')
        ConfgFile.write('ResScale.insert(5, ' + ResScale.get() + ')\n')
        ConfgFile.write('GainCorEntry.delete(0,END)\n')
        ConfgFile.write('GainCorEntry.insert(5, ' + GainCorEntry.get() + ')\n')
        ConfgFile.write('PhaseCorEntry.delete(0,END)\n')
        ConfgFile.write('PhaseCorEntry.insert(5, ' + PhaseCorEntry.get() + ')\n')
        ConfgFile.write('NetworkScreenStatus.set(' + str(NetworkScreenStatus.get()) + ')\n')
    else:
        ConfgFile.write('DestroyIAScreen()\n')
    if SpectrumScreenStatus.get() > 0:
        ConfgFile.write('GRWF = ' + str(GRWF) + '\n')
        ConfgFile.write('GRHF = ' + str(GRHF) + '\n')
        ConfgFile.write('RelPhaseCenter.set(' + str(RelPhaseCenter.get()) + ')\n')
        ConfgFile.write('MakeSpectrumWindow()\n')
        ConfgFile.write("freqwindow.geometry('+" + str(freqwindow.winfo_x()) + '+' + str(freqwindow.winfo_y()) + "')\n")
        ConfgFile.write('ShowC1_VdB.set(' + str(ShowC1_VdB.get()) + ')\n')
        ConfgFile.write('ShowC1_P.set(' + str(ShowC1_P.get()) + ')\n')
        ConfgFile.write('ShowC2_VdB.set(' + str(ShowC2_VdB.get()) + ')\n')
        ConfgFile.write('ShowC2_P.set(' + str(ShowC2_P.get()) + ')\n')
        ConfgFile.write('StartFreqEntry.delete(0,END)\n')
        ConfgFile.write('StartFreqEntry.insert(5, ' + StartFreqEntry.get() + ')\n')
        ConfgFile.write('StopFreqEntry.delete(0,END)\n')
        ConfgFile.write('StopFreqEntry.insert(5, ' + StopFreqEntry.get() + ')\n')
        ConfgFile.write('HScale.set(' + str(HScale.get()) + ')\n')
        ConfgFile.write('FreqTraceMode.set(' + str(FreqTraceMode.get()) + ')\n')
        ConfgFile.write('SingleShotSA.set(' + str(SingleShotSA.get()) + ')\n')
    else:
        ConfgFile.write('DestroySpectrumScreen()\n')
    if DigFiltStatus.get() == 1:
        ConfgFile.write('MakeDigFiltWindow()\n')
        ConfgFile.write("digfltwindow.geometry('+" + str(digfltwindow.winfo_x()) + '+' + str(digfltwindow.winfo_y()) + "')\n")
        ConfgFile.write('DigFiltABoxCar.set(' + str(DigFiltABoxCar.get()) + ')\n')
        ConfgFile.write('DigFiltBBoxCar.set(' + str(DigFiltBBoxCar.get()) + ')\n')
        ConfgFile.write('BCALenEntry.delete(0,"end")\n')
        ConfgFile.write('BCALenEntry.insert(0, ' + BCALenEntry.get() + ')\n')
        ConfgFile.write('BCBLenEntry.delete(0,"end")\n')
        ConfgFile.write('BCBLenEntry.insert(0, ' + BCBLenEntry.get() + ')\n')
##        ConfgFile.write('AWGALenEntry.delete(0,"end")\n')
##        ConfgFile.write('AWGALenEntry.insert(0, ' + AWGALenEntry.get() + ')\n')
##        ConfgFile.write('AWGFiltABoxCar.set(' + str(AWGFiltABoxCar.get()) + ')\n')
##        ConfgFile.write('AWGBLenEntry.delete(0,"end")\n')
##        ConfgFile.write('AWGBLenEntry.insert(0, ' + AWGBLenEntry.get() + ')\n')
##        ConfgFile.write('AWGFiltBBoxCar.set(' + str(AWGFiltBBoxCar.get()) + ')\n')
        ConfgFile.write('BuildBoxCarA()\n')
        ConfgFile.write('BuildBoxCarB()\n')
##        ConfgFile.write('BuildAWGBoxCarA()\n')
##        ConfgFile.write('BuildAWGBoxCarB()\n')
    else:
        ConfgFile.write('DestroyDigFiltScreen()\n')
    # Save Phase Anayzer stuff after Analog Mux in case they are both open
    if PhAScreenStatus.get() > 0:
        ConfgFile.write('GRWPhA = ' + str(GRWPhA) + '\n')
        ConfgFile.write('GRHPhA = ' + str(GRHPhA) + '\n')
        ConfgFile.write('MakePhAWindow()\n')
        ConfgFile.write("phawindow.geometry('+" + str(phawindow.winfo_x()) + '+' + str(phawindow.winfo_y()) + "')\n")
        ConfgFile.write('VScale.delete(0,END)\n')
        ConfgFile.write('VScale.insert(0, ' + str(VScale.get()) + ')\n')
        ConfgFile.write('RefphEntry.delete(0,END)\n')
        ConfgFile.write('RefphEntry.insert(0, "' + str(RefphEntry.get()) + '")\n')
        if vat_btn.config('text')[-1] == 'OFF':
            ConfgFile.write('vat_btn.config(text="OFF", style="Stop.TButton")\n')
        else:
            ConfgFile.write('vat_btn.config(text="ON", style="Run.TButton")\n')
        if vbt_btn.config('text')[-1] == 'OFF':
            ConfgFile.write('vbt_btn.config(text="OFF", style="Stop.TButton")\n')
        else:
            ConfgFile.write('vbt_btn.config(text="ON", style="Run.TButton")\n')
        #
        if CHANNELS >= 3:
            if vct_btn.config('text')[-1] == 'OFF':
                ConfgFile.write('vct_btn.config(text="OFF", style="Stop.TButton")\n')
            else:
                ConfgFile.write('vct_btn.config(text="ON", style="Run.TButton")\n')
        if CHANNELS >= 4:
            if vdt_btn.config('text')[-1] == 'OFF':
                ConfgFile.write('vdt_btn.config(text="OFF", style="Stop.TButton")\n')
            else:
                ConfgFile.write('vdt_btn.config(text="ON", style="Run.TButton")\n')
    else:
        ConfgFile.write('DestroyPhAScreen()\n')
    if BodeScreenStatus.get() == 1:
        ConfgFile.write('GRWBP = ' + str(GRWBP) + '\n')
        ConfgFile.write('GRHBP = ' + str(GRHBP) + '\n')
        ConfgFile.write('RelPhaseCenter.set(' + str(RelPhaseCenter.get()) + ')\n')
        ConfgFile.write('ImpedanceCenter.set(' + str(ImpedanceCenter.get()) + ')\n')
        ConfgFile.write('MakeBodeWindow()\n')
        ConfgFile.write("bodewindow.geometry('+" + str(bodewindow.winfo_x()) + '+' + str(bodewindow.winfo_y()) + "')\n")
        ConfgFile.write('ShowCA_VdB.set(' + str(ShowCA_VdB.get()) + ')\n')
        ConfgFile.write('ShowCB_VdB.set(' + str(ShowCB_VdB.get()) + ')\n')
        ConfgFile.write('ShowCA_P.set(' + str(ShowCA_P.get()) + ')\n')
        ConfgFile.write('ShowCB_P.set(' + str(ShowCB_P.get()) + ')\n')
        ConfgFile.write('ShowCA_RdB.set(' + str(ShowCA_RdB.get()) + ')\n')
        ConfgFile.write('ShowCA_RP.set(' + str(ShowCA_RP.get()) + ')\n')
        ConfgFile.write('ShowCB_RdB.set(' + str(ShowCB_RdB.get()) + ')\n')
        ConfgFile.write('ShowCB_RP.set(' + str(ShowCB_RP.get()) + ')\n')
        ConfgFile.write('BodeDisp.set(' + str(BodeDisp.get()) + ')\n')
        ConfgFile.write('ShowMarkerBP.set(' + str(ShowMarkerBP.get()) + ')\n')
        ConfgFile.write('ShowMathBP.set(' + str(ShowMathBP.get()) + ')\n')
        ConfgFile.write('ShowRMathBP.set(' + str(ShowRMathBP.get()) + ')\n')
        ConfgFile.write('HScaleBP.set(' + str(HScaleBP.get()) + ')\n')
        ConfgFile.write('NSteps.set(' + str(NSteps.get()) + ')\n')
        ConfgFile.write('DBdivindexBP.set(' + str(DBdivindexBP.get()) + ')\n')
        ConfgFile.write('DBlevelBP.set(' + str(DBlevelBP.get()) + ')\n')
        ConfgFile.write('FSweepMode.set(' + str(FSweepMode.get()) + ')\n')
        ConfgFile.write('SweepStepBodeEntry.delete(0,END)\n')
        ConfgFile.write('SweepStepBodeEntry.insert(4, ' + SweepStepBodeEntry.get() + ')\n')
        ConfgFile.write('StopBodeEntry.delete(0,END)\n')
        ConfgFile.write('StopBodeEntry.insert(4, ' + StopBodeEntry.get() + ')\n')
        ConfgFile.write('StartBodeEntry.delete(0,END)\n')
        ConfgFile.write('StartBodeEntry.insert(4, ' + StartBodeEntry.get() + ')\n')
        ConfgFile.write('Show_Rseries.set(' + str(Show_Rseries.get()) + ')\n')
        ConfgFile.write('Show_Xseries.set(' + str(Show_Xseries.get()) + ')\n')
        ConfgFile.write('Show_Magnitude.set(' + str(Show_Magnitude.get()) + ')\n')
        ConfgFile.write('Show_Angle.set(' + str(Show_Angle.get()) + ')\n')
    else:
        ConfgFile.write('DestroyBodeScreen()\n')
    if MeasureStatus.get() == 1:
        # Save strings
        ConfgFile.write('ChaLableSrring1 = "' + ChaLableSrring1 + '"\n')
        ConfgFile.write('ChaLableSrring2 = "' + ChaLableSrring2 + '"\n')
        ConfgFile.write('ChaLableSrring3 = "' + ChaLableSrring3 + '"\n')
        ConfgFile.write('ChaLableSrring4 = "' + ChaLableSrring4 + '"\n')
        ConfgFile.write('ChaLableSrring5 = "' + ChaLableSrring5 + '"\n')
        ConfgFile.write('ChaLableSrring6 = "' + ChaLableSrring6 + '"\n')
        ConfgFile.write('ChbLableSrring1 = "' + ChbLableSrring1 + '"\n')
        ConfgFile.write('ChbLableSrring2 = "' + ChbLableSrring2 + '"\n')
        ConfgFile.write('ChbLableSrring3 = "' + ChbLableSrring3 + '"\n')
        ConfgFile.write('ChbLableSrring4 = "' + ChbLableSrring4 + '"\n')
        ConfgFile.write('ChbLableSrring5 = "' + ChbLableSrring5 + '"\n')
        ConfgFile.write('ChbLableSrring6 = "' + ChbLableSrring6 + '"\n')
        ConfgFile.write('ChaMeasString1 = "' + ChaMeasString1 + '"\n')
        ConfgFile.write('ChaMeasString2 = "' + ChaMeasString2 + '"\n')
        ConfgFile.write('ChaMeasString3 = "' + ChaMeasString3 + '"\n')
        ConfgFile.write('ChaMeasString4 = "' + ChaMeasString4 + '"\n')
        ConfgFile.write('ChaMeasString5 = "' + ChaMeasString5 + '"\n')
        ConfgFile.write('ChaMeasString6 = "' + ChaMeasString6 + '"\n')
        ConfgFile.write('ChbMeasString1 = "' + ChbMeasString1 + '"\n')
        ConfgFile.write('ChbMeasString2 = "' + ChbMeasString2 + '"\n')
        ConfgFile.write('ChbMeasString3 = "' + ChbMeasString3 + '"\n')
        ConfgFile.write('ChbMeasString4 = "' + ChbMeasString4 + '"\n')
        ConfgFile.write('ChbMeasString5 = "' + ChbMeasString5 + '"\n')
        ConfgFile.write('ChbMeasString6 = "' + ChbMeasString6 + '"\n')
        ConfgFile.write('MakeMeasureScreen()\n')
        ConfgFile.write("measurewindow.geometry('+" + str(measurewindow.winfo_x()) + '+' + str(measurewindow.winfo_y()) + "')\n")
    else:
        ConfgFile.write('DestroyMeasuewScreen()\n')
    #
    ConfgFile.write('TRIGGERentry.delete(0,END)\n')
    ConfgFile.write('TRIGGERentry.insert(4, ' + TRIGGERentry.get() + ')\n')
    ConfgFile.write('HozPossentry.delete(0,"end")\n')
    ConfgFile.write('HozPossentry.insert(0, ' + HozPossentry.get() + ')\n')
    ConfgFile.write('TMsb.delete(0,END)\n')
    ConfgFile.write('TMsb.insert(0, "' + TMsb.get() + '")\n')
    ConfgFile.write('TgInput.set(' + str(TgInput.get()) + ')\n')
    ConfgFile.write('AutoLevel.set(' + str(AutoLevel.get()) + ')\n')
    ConfgFile.write('ManualTrigger.set(' + str(ManualTrigger.get()) + ')\n')
    ConfgFile.write('SingleShot.set(' + str(SingleShot.get()) + ')\n')
    ConfgFile.write('TgEdge.set(' + str(TgEdge.get()) + ')\n')
    ConfgFile.write('Roll_Mode.set(' + str(Roll_Mode.get()) + ')\n')
    ConfgFile.write('Xsignal.set(' + str(Xsignal.get()) + ')\n')
    ConfgFile.write('YsignalVA.set(' + str(YsignalVA.get()) + ')\n')
    ConfgFile.write('YsignalVB.set(' + str(YsignalVB.get()) + ')\n')
    ConfgFile.write('YsignalM.set(' + str(YsignalM.get()) + ')\n')
    ConfgFile.write('YsignalMX.set(' + str(YsignalMX.get()) + ')\n')
    ConfgFile.write('YsignalMY.set(' + str(YsignalMY.get()) + ')\n')
    #
    ConfgFile.write('TimeDisp.set(' + str(TimeDisp.get()) + ')\n')
    ConfgFile.write('XYDisp.set(' + str(XYDisp.get()) + ')\n')
    ConfgFile.write('FreqDisp.set(' + str(FreqDisp.get()) + ')\n')
    ConfgFile.write('IADisp.set(' + str(IADisp.get()) + ')\n')
    ConfgFile.write('ShowC1_V.set(' + str(ShowC1_V.get()) + ')\n')
    ConfgFile.write('ShowC2_V.set(' + str(ShowC2_V.get()) + ')\n')
    ConfgFile.write('ShowC3_V.set(' + str(ShowC3_V.get()) + ')\n')
    ConfgFile.write('ShowC4_V.set(' + str(ShowC4_V.get()) + ')\n')
    ConfgFile.write('Show_MathX.set(' + str(Show_MathX.get()) + ')\n')
    ConfgFile.write('Show_MathY.set(' + str(Show_MathY.get()) + ')\n')
    ConfgFile.write('AutoCenterA.set(' + str(AutoCenterA.get()) + ')\n')
    ConfgFile.write('AutoCenterB.set(' + str(AutoCenterB.get()) + ')\n')
    ConfgFile.write('TRACEmodeTime.set(' + str(TRACEmodeTime.get()) + ')\n')
    if CHANNELS >= 1:
        ConfgFile.write('CHAVPosEntry.delete(0,END)\n')
        ConfgFile.write('CHAVPosEntry.insert(4, ' + CHAVPosEntry.get() + ')\n')
        ConfgFile.write('CHAsb.delete(0,END)\n')
        ConfgFile.write('CHAsb.insert(0, "' + CHAsb.get() + '")\n')
        ConfgFile.write('CHAVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHAVGainEntry.insert(4, ' + CHAVGainEntry.get() + ')\n')
        ConfgFile.write('CHAVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHAVOffsetEntry.insert(4, ' + CHAVOffsetEntry.get() + ')\n')
    if CHANNELS >= 2:
        ConfgFile.write('CHBVPosEntry.delete(0,END)\n')
        ConfgFile.write('CHBVPosEntry.insert(4, ' + CHBVPosEntry.get() + ')\n')
        ConfgFile.write('CHBsb.delete(0,END)\n')
        ConfgFile.write('CHBsb.insert(0, "' + CHBsb.get() + '")\n')
        ConfgFile.write('CHBVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
        ConfgFile.write('CHBVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')
    if CHANNELS >= 3:
        ConfgFile.write('CHCVPosEntry.delete(0,END)\n')
        ConfgFile.write('CHCVPosEntry.insert(4, ' + CHCVPosEntry.get() + ')\n')
        ConfgFile.write('CHCsb.delete(0,END)\n')
        ConfgFile.write('CHCsb.insert(0, "' + CHCsb.get() + '")\n')
        ConfgFile.write('CHCVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHCVGainEntry.insert(4, ' + CHCVGainEntry.get() + ')\n')
        ConfgFile.write('CHCVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHCVOffsetEntry.insert(4, ' + CHCVOffsetEntry.get() + ')\n')
    if CHANNELS >= 4:
        ConfgFile.write('CHDVPosEntry.delete(0,END)\n')
        ConfgFile.write('CHDVPosEntry.insert(4, ' + CHDVPosEntry.get() + ')\n')
        ConfgFile.write('CHDsb.delete(0,END)\n')
        ConfgFile.write('CHDsb.insert(0, "' + CHDsb.get() + '")\n')
        ConfgFile.write('CHDVGainEntry.delete(0,END)\n')
        ConfgFile.write('CHDVGainEntry.insert(4, ' + CHDVGainEntry.get() + ')\n')
        ConfgFile.write('CHDVOffsetEntry.delete(0,END)\n')
        ConfgFile.write('CHDVOffsetEntry.insert(4, ' + CHDVOffsetEntry.get() + ')\n')
    ConfgFile.write('CHMVPosEntry.delete(0,END)\n')
    ConfgFile.write('CHMVPosEntry.insert(4, ' + CHMVPosEntry.get() + ')\n')
    ConfgFile.write('CHMsb.delete(0,END)\n')
    ConfgFile.write('CHMsb.insert(0, "' + CHMsb.get() + '")\n')
    # AWG stuff
    ConfgFile.write('AWG_Amp_Mode.set('+ str(AWG_Amp_Mode.get()) + ')\n')
    if AWGChannels >=1:
        ConfgFile.write('AWGAPhaseDelay.set('+ str(AWGAPhaseDelay.get()) + ')\n')
        ConfgFile.write('AWGAAmplEntry.delete(0,END)\n')
        ConfgFile.write('AWGAAmplEntry.insert(4, ' + AWGAAmplEntry.get() + ')\n')
        ConfgFile.write('AWGAOffsetEntry.delete(0,END)\n')
        ConfgFile.write('AWGAOffsetEntry.insert(4, ' + AWGAOffsetEntry.get() + ')\n')
        ConfgFile.write('AWGAFreqEntry.delete(0,END)\n')
        ConfgFile.write('AWGAFreqEntry.insert(4, ' + AWGAFreqEntry.get() + ')\n')
        #ConfgFile.write('AWGASymmetryEntry.delete(0,END)\n')
        #ConfgFile.write('AWGASymmetryEntry.insert(4, ' + AWGASymmetryEntry.get() + ')\n')
        #ConfgFile.write('AWGAWidthEntry.delete(0,END)\n')
        #ConfgFile.write('AWGAWidthEntry.insert(4, ' + AWGAWidthEntry.get() + ')\n')
        ConfgFile.write('AWGADutyCycleEntry.delete(0,END)\n')
        ConfgFile.write('AWGADutyCycleEntry.insert(4, ' + AWGADutyCycleEntry.get() + ')\n')
        ConfgFile.write('AWGAShape.set(' + str(AWGAShape.get()) + ')\n')
    #
    if AWGChannels >=2:
        ConfgFile.write('AWGBPhaseDelay.set('+ str(AWGBPhaseDelay.get()) + ')\n')
        ConfgFile.write('AWGBAmplEntry.delete(0,END)\n')
        ConfgFile.write('AWGBAmplEntry.insert(4, ' + AWGBAmplEntry.get() + ')\n')
        ConfgFile.write('AWGBOffsetEntry.delete(0,END)\n')
        ConfgFile.write('AWGBOffsetEntry.insert(4, ' + AWGBOffsetEntry.get() + ')\n')
        ConfgFile.write('AWGBFreqEntry.delete(0,END)\n')
        ConfgFile.write('AWGBFreqEntry.insert(4, ' + AWGBFreqEntry.get() + ')\n')
        #ConfgFile.write('AWGBSymmetryEntry.delete(0,END)\n')
        #ConfgFile.write('AWGBSymmetryEntry.insert(4, ' + AWGBSymmetryEntry.get() + ')\n')
        #ConfgFile.write('AWGBWidthEntry.delete(0,END)\n')
        #ConfgFile.write('AWGBWidthEntry.insert(4, ' + AWGBWidthEntry.get() + ')\n')
        ConfgFile.write('AWGBPhaseEntry.delete(0,END)\n')
        ConfgFile.write('AWGBPhaseEntry.insert(4, ' + AWGBPhaseEntry.get() + ')\n')
        ConfgFile.write('AWGBDutyCycleEntry.delete(0,END)\n')
        ConfgFile.write('AWGBDutyCycleEntry.insert(4, ' + AWGBDutyCycleEntry.get() + ')\n')
        ConfgFile.write('AWGBShape.set(' + str(AWGBShape.get()) + ')\n')
    #
    ConfgFile.write('MeasDCV1.set(' + str(MeasDCV1.get()) + ')\n')
    ConfgFile.write('MeasMinV1.set(' + str(MeasMinV1.get()) + ')\n')
    ConfgFile.write('MeasMaxV1.set(' + str(MeasMaxV1.get()) + ')\n')
    ConfgFile.write('MeasBaseV1.set(' + str(MeasBaseV1.get()) + ')\n')
    ConfgFile.write('MeasTopV1.set(' + str(MeasTopV1.get()) + ')\n')
    ConfgFile.write('MeasMidV1.set(' + str(MeasMidV1.get()) + ')\n')
    ConfgFile.write('MeasPPV1.set(' + str(MeasPPV1.get()) + ')\n')
    ConfgFile.write('MeasRMSV1.set(' + str(MeasRMSV1.get()) + ')\n')
    ConfgFile.write('MeasDiffAB.set(' + str(MeasDiffAB.get()) + ')\n')
    ConfgFile.write('MeasDCV2.set(' + str(MeasDCV2.get()) + ')\n')
    ConfgFile.write('MeasMinV2.set(' + str(MeasMinV2.get()) + ')\n')
    ConfgFile.write('MeasMaxV2.set(' + str(MeasMaxV2.get()) + ')\n')
    ConfgFile.write('MeasBaseV2.set(' + str(MeasBaseV2.get()) + ')\n')
    ConfgFile.write('MeasTopV2.set(' + str(MeasTopV2.get()) + ')\n')
    ConfgFile.write('MeasMidV2.set(' + str(MeasMidV2.get()) + ')\n')
    ConfgFile.write('MeasPPV2.set(' + str(MeasPPV2.get()) + ')\n')
    ConfgFile.write('MeasRMSV2.set(' + str(MeasRMSV2.get()) + ')\n')
    ConfgFile.write('MeasDiffBA.set(' + str(MeasDiffBA.get()) + ')\n')
    ConfgFile.write('MeasDCV3.set(' + str(MeasDCV3.get()) + ')\n')
    ConfgFile.write('MeasMinV3.set(' + str(MeasMinV3.get()) + ')\n')
    ConfgFile.write('MeasMaxV3.set(' + str(MeasMaxV3.get()) + ')\n')
    ConfgFile.write('MeasMidV3.set(' + str(MeasMidV3.get()) + ')\n')
    ConfgFile.write('MeasRMSV3.set(' + str(MeasRMSV3.get()) + ')\n')
    ConfgFile.write('MeasPPV3.set(' + str(MeasPPV3.get()) + ')\n')
    ConfgFile.write('MeasDCV4.set(' + str(MeasDCV4.get()) + ')\n')
    ConfgFile.write('MeasMinV4.set(' + str(MeasMinV4.get()) + ')\n')
    ConfgFile.write('MeasMaxV4.set(' + str(MeasMaxV4.get()) + ')\n')
    ConfgFile.write('MeasMidV4.set(' + str(MeasMidV4.get()) + ')\n')
    ConfgFile.write('MeasPPV4.set(' + str(MeasPPV4.get()) + ')\n')
    ConfgFile.write('MeasRMSV4.set(' + str(MeasRMSV4.get()) + ')\n')
    #
    ConfgFile.write('MeasAHW.set(' + str(MeasAHW.get()) + ')\n')
    ConfgFile.write('MeasALW.set(' + str(MeasALW.get()) + ')\n')
    ConfgFile.write('MeasADCy.set(' + str(MeasADCy.get()) + ')\n')
    ConfgFile.write('MeasAPER.set(' + str(MeasAPER.get()) + ')\n')
    ConfgFile.write('MeasAFREQ.set(' + str(MeasAFREQ.get()) + ')\n')
    ConfgFile.write('MeasBHW.set(' + str(MeasBHW.get()) + ')\n')
    ConfgFile.write('MeasBLW.set(' + str(MeasBLW.get()) + ')\n')
    ConfgFile.write('MeasBDCy.set(' + str(MeasBDCy.get()) + ')\n')
    ConfgFile.write('MeasBPER.set(' + str(MeasBPER.get()) + ')\n')
    ConfgFile.write('MeasBFREQ.set(' + str(MeasBFREQ.get()) + ')\n')
    ConfgFile.write('MeasPhase.set(' + str(MeasPhase.get()) + ')\n')
    ConfgFile.write('MeasDelay.set(' + str(MeasDelay.get()) + ')\n')
    #
    ConfgFile.write('MathTrace.set(' + str(MathTrace.get()) + ')\n')
    # Save strings
    ConfgFile.write('UserAString = "' + UserAString + '"\n')
    ConfgFile.write('UserALabel = "' + UserALabel + '"\n')
    ConfgFile.write('UserBString = "' + UserBString + '"\n')
    ConfgFile.write('UserBLabel = "' + UserBLabel + '"\n')
    ConfgFile.write('FFTUserWindowString= "' +  FFTUserWindowString + '"\n')
    ConfgFile.write('DigFilterAString = "' + DigFilterAString + '"\n')
    ConfgFile.write('DigFilterBString = "' + DigFilterBString + '"\n')
    # extra Spectrum stuff
    if SpectrumScreenStatus.get() > 0 or IAScreenStatus.get() > 0 or BodeScreenStatus.get() > 0:
        ConfgFile.write('FFTwindow.set(' + str(FFTwindow.get()) + ')\n')
        ConfgFile.write('ZEROstuffing.set(' + str(ZEROstuffing.get()) + ')\n')
        ConfgFile.write('Vdiv.set(' + str(Vdiv.get()) + ')\n')
        #
        ConfgFile.write('DBdivindex.set(' + str(DBdivindex.get()) + ')\n')
        ConfgFile.write('DBlevel.set(' + str(DBlevel.get()) + ')\n')
        # ConfgFile.write('TRACEaverage.set(' + str(TRACEaverage.get()) + ')\n')
        ConfgFile.write('CutDC.set(' + str(CutDC.get()) + ')\n')
    #
    ConfgFile.close()
## Save current configuration from IA window
def BSaveConfigIA():
    global iawindow

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=iawindow)
    BSaveConfig(filename)
## Save current configuration from SA window
def BSaveConfigSA():
    global freqwindow

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=freqwindow)
    BSaveConfig(filename)
## Save current configuration from Bode window
def BSaveConfigBP():
    global bodewindow

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=bodewindow)
    BSaveConfig(filename)
## Save current configuration from Scope window
def BSaveConfigTime():
    global root
    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=root)
    BSaveConfig(filename)
## Load configuration from a file    
def BLoadConfig(filename):
    global TgInput, TgEdge, SingleShot, AutoLevel, SingleShotSA, ManualTrigger
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, AutoCenterA, AutoCenterB
    global YsignalVA, YsignalVB, YsignalM, YsignalMX, YsignalMY
    global CHAsb, CHBsb, CHMsb, HScale, FreqTraceMode
    global CHAsbxy, CHAsbxy, CHBsbxy, CHBsbxy, CHANNELS
    global CHAVPosEntryxy, CHBVPosEntryxy
    global ShowC1_V, ShowC3_V, ShowC2_V, ShowC4_V, MathTrace, MathXUnits, MathYUnits
    global CHAVPosEntry, CHBVPosEntry, CHMPosEntry, HozPossentry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGATerm, AWGAMode, AWGARepeatFlag, AWGBRepeatFlag
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBPhaseEntry, AWGBShape, AWGBTerm, AWGBMode, AWGSync, AWGAIOMode, AWGBIOMode
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1, MeasDCV3, MeasMinV3
    global MeasMaxV3, MeasMidV3, MeasPPV3, MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2
    global MeasPPV2, MeasDCV4, MeasMinV4, MeasMaxV4, MeasMidV4, MeasPPV4, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasRMSV3, MeasRMSV4, MeasPhase, MeasDelay
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ, IASource, DisplaySeries
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC, AWG_Amp_Mode
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, AWGAPhaseDelay, AWGBPhaseDelay
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global MathAxis, MathXAxis, MathYAxis, Show_MathX, Show_MathY, MathScreenStatus, MathWindow
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2, CHAI_RC_HP, CHBI_RC_HP
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2, RelPhaseCenter, ImpedanceCenter
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global Show_Rseries, Show_Xseries, Show_Magnitude, Show_Angle
    global AWGABurstFlag, AWGACycles, AWGABurstDelay, AWGAwaveform, AWGAcsvFile, AWGBcsvFile
    global AWGBBurstFlag, AWGBCycles, AWGBBurstDelay, AWGBwaveform, AWGAwavFile, AWGBwavFile
    global SCLKPort, SDATAPort, SLATCHPort, FminEntry, HtMulEntry
    global phawindow, PhAca, PhAScreenStatus, PhADisp
    global GRWPhA, X0LPhA, GRHPhA, Y0TPhA, EnableScopeOnly
    global VScale, IScale, RefphEntry, BoardStatus, boardwindow, BrdSel
    global vat_btn, vbt_btn, vct_btn, vdt_btn, vabt_btn, iapbt_btn, RollBt, Roll_Mode
    global ScreenWidth, ScreenHeight
    global TRACEwidth, ColorMode, ca, COLORcanvas, COLORtrace4, COLORtraceR4, COLORtext
    global AWGANoiseEntry, AWGBNoiseEntry, AWGAsbnoise, AWGBsbnoise
    global AWGFiltA, AWGALenEntry, AWGFiltABoxCar, AWGFiltALength, digfltwindow
    global AWGFiltB, AWGBLenEntry, AWGFiltBBoxCar, AWGFiltBLength
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8
    # Read configuration values from file
    try:
        ConfgFile = open(filename)
        for line in ConfgFile:
            try:
                exec( line.rstrip(), globals(), globals())
                #exec( line.rstrip() )
            except:
                print( "Skipping " + line.rstrip())
        ConfgFile.close()
    except:
        print( "Config File Not Found.")
    if ScreenWidth < root.winfo_x() or ScreenHeight < root.winfo_y(): # check if main window will be placed off screen?
        root.geometry('+0+0')
    try:
        if ScreenWidth < awgwindow.winfo_x() or ScreenHeight < awgwindow.winfo_y(): # check if AWG window will be placed off screen?
            awgwindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < xywindow.winfo_x() or ScreenHeight< xywindow.winfo_y(): # check if XY window will be placed off screen?
            xywindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < iawindow.winfo_x() or ScreenHeight < iawindow.winfo_y(): # check if IA window will be placed off screen?
            iawindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < freqwindow.winfo_x() or ScreenHeight < freqwindow.winfo_y(): # check if SA window will be placed off screen?
            freqwindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < win1.winfo_x() or ScreenHeight < win1.winfo_y(): # check if DAC1 window will be placed off screen?
            win1.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < win2.winfo_x() or ScreenHeight < win2.winfo_y(): # check if DAC2 window will be placed off screen?
            win2.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < minigenwindow.winfo_x() or ScreenHeight < minigenwindow.winfo_y(): # check if mini gen window will be placed off screen?
            minigenwindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < phawindow.winfo_x() or ScreenHeight < phawindow.winfo_y(): # check if PhA window will be placed off screen?
            phawindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < bodewindow.winfo_x() or ScreenHeight < bodewindow.winfo_y(): # check if Bode window will be placed off screen?
            bodewindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < measurewindow.winfo_x() or ScreenHeight < measurewindow.winfo_y(): # check if Measure window will be placed off screen?
            measurewindow.geometry('+0+0')
    except:
        donothing()
    try:
        if ScreenWidth < etswindow.winfo_x() or ScreenHeight < etswindow.winfo_y(): # check if ETS window will be placed off screen?
            etswindow.geometry('+0+0')
    except:
        donothing()
##        if Roll_Mode.get() == 0:
##            RollBt.config(style="RollOff.TButton",text="Roll-Off")
##        else:
##            RollBt.config(style="Roll.TButton",text="Roll-On")
#        if DevID != "No Device":
##        if ColorMode.get() > 0: # White background
##            # print("White background")
##            if TRACEwidth.get() < 2:
##                TRACEwidth.set(2)
##            COLORtext = "#000000"   # 100% black
##            COLORtrace4 = "#a0a000" # 50% yellow
##            COLORtraceR4 = "#606000"   # 25% yellow
##            COLORcanvas = "#ffffff"     # 100% white
##        else:
##            # print("Black background")
##            COLORcanvas = "#000000"   # 100% black
##            COLORtrace4 = "#ffff00" # 100% yellow
##            COLORtraceR4 = "#808000"   # 50% yellow
##            COLORtext = "#ffffff"     # 100% white
    ca.config(background=COLORcanvas)
    # Needs to reload from waveform files
    # Regenerate waveform from formula
    #if AWGAShape.get()==10:
    #    AWGAConfigMath()
    if EnableScopeOnly == 0:
        #UpdateAWGWin()
        # TimeCheckBox()
        if TimeDisp.get() == 1:
            ckb1.config(style="Enab.TCheckbutton")
        XYCheckBox()
        try:
            FreqCheckBox()
        except:
            donothing()
        try:
            BodeCheckBox()
        except:
            donothing()
        try:
            IACheckBox()
        except:
            donothing()
        try:
            OhmCheckBox()
        except:
            donothing()
    else:
        TimeCheckBox()
        XYCheckBox()
        UpdateAWGWin()
#
    time.sleep(0.05)
    # turn off unused channels
    if CHANNELS < 2:
        ShowC2_V.set(0)
    if CHANNELS < 3:
        ShowC3_V.set(0)
    if CHANNELS < 4:
        ShowC4_V.set(0)
    #MakeAWGwaves()
# Add this to turn off outputs after first time loading a config?
    #BTime()
#
#
# Waveform Function Gen Stuff
#
def AWGAReadFile():
    global AWGALength, awgwindow, AWGAcsvFile

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    AWGAcsvFile = filename
    AWGALoadCSV()
#
def AWGALoadCSV():
    global AWGALength, awgwindow, AWGAcsvFile, AWGAOffsetvalue, AWGAShapeLabel

    BAWGAOffset(0)
    try:
        CSVFile = open(AWGAcsvFile)
        # dialect = csv.Sniffer().sniff(CSVFile.read(128))
        CSVFile.seek(0)
        #csv_f = csv.reader(CSVFile, dialect)
        csv_f = csv.reader(CSVFile, csv.excel)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
    # print csv_f.dialect
    AWG1 = []
    ColumnNum = 0
    ColumnSel = 0
    RowNum = 0
    for row in csv_f:
        # print 'found row = ', row
        if len(row) > 1 and ColumnSel == 0:
            RequestColumn = askstring("Which Column?", "File contains 1 to " + str(len(row)) + " columns\n\nEnter column number to import:\n", initialvalue=1, parent=awgwindow)
            ColumnNum = int(RequestColumn) - 1
            ColumnLen = str(len(row))
            ColumnSel = 1
        try:
            colnum = 0
            for col in row:
                if colnum == ColumnNum:
                    AWG1.append(float(col))
                colnum += 1
        except:
            print( 'skipping non-numeric row', RowNum)
        RowNum += 1
    AWG1 = numpy.array(AWG1)
    CSVFile.close()
    AWGALength.config(text = "L = " + str(int(len(AWG1)))) # change displayed value
    AWGAShapeLabel.config(text = "CSV File") # change displayed value
    AWGASendWave(AWG1)
#
def AWGBReadFile():
    global AWGBLength, awgwindow, AWGBcsvFile

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    AWGBcsvFile = filename
    AWGBLoadCSV()
#
def AWGBLoadCSV():
    global AWGBLength, awgwindow, AWGBcsvFile, AWGBOffsetvalue, AWGBShapeLabel

    BAWGBOffset(0)
    try:
        CSVFile = open(AWGBcsvFile)
        # dialect = csv.Sniffer().sniff(CSVFile.read(128))
        CSVFile.seek(0)
        #csv_f = csv.reader(CSVFile, dialect)
        csv_f = csv.reader(CSVFile, csv.excel)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
    # print csv_f.dialect
    AWG1 = []
    ColumnNum = 0
    ColumnSel = 0
    RowNum = 0
    for row in csv_f:
        # print 'found row = ', row
        if len(row) > 1 and ColumnSel == 0:
            RequestColumn = askstring("Which Column?", "File contains 1 to " + str(len(row)) + " columns\n\nEnter column number to import:\n", initialvalue=1, parent=awgwindow)
            ColumnNum = int(RequestColumn) - 1
            ColumnLen = str(len(row))
            ColumnSel = 1
        try:
            colnum = 0
            for col in row:
                if colnum == ColumnNum:
                    AWG1.append(float(col))
                colnum += 1
        except:
            print( 'skipping non-numeric row', RowNum)
        RowNum += 1
    AWG1 = numpy.array(AWG1)
    CSVFile.close()
    AWGBLength.config(text = "L = " + str(int(len(AWG1)))) # change displayed value
    AWGBShapeLabel.config(text = "CSV File") # change displayed value
    AWGBSendWave(AWG1)
#
def BAWGAAmpl():
    global AWGAAmplEntry, AWGAAmplvalue, AWGAMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGPeakToPeak
    
    try:
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    except:
        AWGAAmplEntry.delete(0,"end")
        AWGAAmplEntry.insert(0, AWGAAmplvalue)
    #
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGAMode.get() == 0: # 
            if AWGAAmplvalue > AWGPeakToPeak:
                AWGAAmplvalue = AWGPeakToPeak
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
            if AWGAAmplvalue < 0.00:
                AWGAAmplvalue = 0.00
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
    elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
        if AWGAMode.get() == 0: # 
            if AWGAAmplvalue > (AWGPeakToPeak/2.0):
                AWGAAmplvalue = AWGPeakToPeak/2.0
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
            if AWGAAmplvalue < (AWGPeakToPeak/ -2.0):
                AWGAAmplvalue = AWGPeakToPeak/ -2.0
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
#
def BAWGAOffset():
    global AWGAOffsetEntry, AWGAOffsetvalue, AWGAMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGPeakToPeak
    
    try:
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    except:
        AWGAOffsetEntry.delete(0,"end")
        AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGAMode.get() == 0: # 
            if AWGAOffsetvalue > AWGPeakToPeak:
                AWGAOffsetvalue = AWGPeakToPeak
                AWGAOffsetEntry.delete(0,"end")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
            if AWGAOffsetvalue < 0.00:
                AWGAOffsetvalue = 0.00
                AWGAOffsetEntry.delete(0,"end")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
        elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
            if AWGAOffsetvalue > (AWGPeakToPeak/2.0):
                AWGAOffsetvalue = AWGPeakToPeak/2.0
                AWGAOffsetEntry.delete(0,"end")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
            if AWGAOffsetvalue < (AWGPeakToPeak / -2.0):
                AWGAOffsetvalue = AWGPeakToPeak / -2.0
                AWGAOffsetEntry.delete(0,"end")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
#
def BAWGAFreq():
    global AWGAFreqEntry, AWGAFreqvalue, LockFreq
    global BodeScreenStatus, BodeDisp, AWGARecLength

    try:
        AWGAFreqvalue = float(eval(AWGAFreqEntry.get()))
    except:
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue > 100000: # max freq is 50KHz
        AWGAFreqvalue = 100000
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue < 0: # Set negative frequency entry to 10
        AWGAFreqvalue = 1
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if LockFreq.get() == 1: # If freq lock flag set change AWGB Freq to same value
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGAFreqvalue)
    #UpdateAWGA()
def BAWGBAmpl():
    global AWGBAmplEntry, AWGBAmplvalue, AWGBMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGPeakToPeak
    try:
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    except:
        AWGBAmplEntry.delete(0,"end")
        AWGBAmplEntry.insert(0, AWGBAmplvalue)
    #
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGBMode.get() == 0: # 
            if AWGBAmplvalue > AWGPeakToPeak:
                AWGBAmplvalue = AWGPeakToPeak
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
            if AWGBAmplvalue < 0.00:
                AWGBAmplvalue = 0.00
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
    elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
        if AWGBMode.get() == 0: # 
            if AWGBAmplvalue > (AWGPeakToPeak/2.0):
                AWGBAmplvalue = 2.0/ 1
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
            if AWGBAmplvalue < (AWGPeakToPeak / -2.0):
                AWGBAmplvalue = AWGPeakToPeak / -2.0
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
#
def BAWGBOffset():
    global AWGBOffsetEntry, AWGBOffsetvalue, AWGBMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGPeakToPeak
    try:
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    except:
        AWGBOffsetEntry.delete(0,"end")
        AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGBMode.get() == 0: # 
            if AWGBOffsetvalue > AWGPeakToPeak:
                AWGBOffsetvalue = AWGPeakToPeak
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            if AWGBOffsetvalue < 0.00:
                AWGBOffsetvalue = 0.00
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
        elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
            if AWGBOffsetvalue > (AWGPeakToPeak/2.0):
                AWGBOffsetvalue = AWGPeakToPeak/2.0
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            if AWGBOffsetvalue < (AWGPeakToPeak/-2.0):
                AWGBOffsetvalue = AWGPeakToPeak/-2.0
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
#
def BAWGBFreq():
    global AWGBFreqEntry, AWGBFreqvalue
    global BodeScreenStatus, BodeDisp, AWGBRecLength

    try:
        AWGBFreqvalue = float(eval(AWGBFreqEntry.get()))
    except:
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue > 100000: # max freq is 50KHz
        AWGBFreqvalue = 100000
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue < 0: # Set negative frequency entry to 10
        AWGBFreqvalue = 1
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if LockFreq.get() == 1: # If freq lock flag set change AWGB Freq to same value
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGBFreqvalue)
    #UpdateAWGB()
def SetBCompA():
    global AWGAAmplEntry, AWGBAmplEntry, AWGAOffsetEntry, AWGBOffsetEntry, AWGAFreqEntry, AWGBFreqEntry
    global AWGAPhaseEntry, AWGBPhaseEntry, AWGADutyCycleEntry, AWGBDutyCycleEntry, AWGAShape, AWGBShape
    global BisCompA, AWGAWave, AWG_Amp_Mode
    if BisCompA.get() == 1:
        if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode, 1 = Amp/Offset
            # sawp Min and Max values
            if AWGAShape.get() == 0: # if AWGAWave == 'dc':
                AWGBAmplvalue = float(eval(AWGAAmplEntry.get()))
                AWGBOffsetvalue = 2.5 - (float(eval(AWGAOffsetEntry.get()))-2.5)
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            else:
                AWGBAmplvalue = float(eval(AWGAAmplEntry.get()))
                AWGBOffsetvalue = float(eval(AWGAOffsetEntry.get()))
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBOffsetvalue)
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBAmplvalue)
            try:
                AWGBPhasevalue = float(eval(AWGAPhaseEntry.get()))
                AWGBPhaseEntry.delete(0,"end")
                AWGBPhaseEntry.insert(0, AWGBPhasevalue)
            except:
                    pass
        else:
            if AWGAShape.get() == 0: # if AWGAWave == 'dc':
                AWGBAmplvalue = float(eval(AWGAAmplEntry.get()))
                AWGBOffsetvalue = 2.5 - (float(eval(AWGAOffsetEntry.get()))-2.5)
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            else:
                AWGBAmplvalue = float(eval(AWGAAmplEntry.get()))
                AWGBOffsetvalue = 0.0 - (float(eval(AWGAOffsetEntry.get())))
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
                try:
                    AWGBPhasevalue = float(eval(AWGAPhaseEntry.get())) + 180.0
                    AWGBPhaseEntry.delete(0,"end")
                    AWGBPhaseEntry.insert(0, AWGBPhasevalue)
                except:
                    pass
        # copy everything else
        AWGBFreqvalue = float(eval(AWGAFreqEntry.get()))
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
        AWGBDutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
        AWGBShape.set(AWGAShape.get())
        #

def UpdateAWGA():
    global ana_out, fg
    global AWGAAmplvalue, AWGAOffsetvalue, EnableScopeOnly
    global AWGAFreqvalue, AWGAPhasevalue, AWGAPhaseDelay
    global AWGADutyCyclevalue, FSweepMode
    global AWGAWave, AWGAMode, AWGAwaveform
    global AWGSAMPLErate, HWRevOne, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global amp1lab, off1lab, AWGBWave
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    BAWGAAmpl()
    BAWGAOffset()
    BAWGAFreq()
    BAWGAPhase()
    BAWGADutyCycle()
    BAWGAShape()
    
    AWGAperiodvalue = 1.0/AWGAFreqvalue
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode, 1 = Amp/Offset
        amp1lab.config(text = "Min Ch A" ) # change displayed value
        off1lab.config(text = "Max Ch A" ) # change displayed value
    else:
        amp1lab.config(text = "Amp Ch A" )
        off1lab.config(text = "Off Ch A" )
#
def UpdateAWGB():
    global ana_out, fg
    global AWGBAmplvalue, AWGBOffsetvalue, EnableScopeOnly
    global AWGBFreqvalue, AWGBPhasevalue, AWGBPhaseDelay
    global AWGBDutyCyclevalue, FSweepMode, AWGBRepeatFlag, AWGSync
    global AWGBWave, AWGBMode, AWGBTerm, AWGBwaveform, AWGBIOMode
    global AWGSAMPLErate, HWRevOne, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global amp1lab, off1lab, AWGBWave
    global AWGB_Ext_Gain, AWGB_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    BAWGBAmpl()
    BAWGBOffset()
    BAWGBFreq()
    BAWGBPhase()
    BAWGBDutyCycle()
    BAWGBShape()
    
    AWGBperiodvalue = 1.0/AWGBFreqvalue
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode, 1 = Amp/Offset
        amp1lab.config(text = "Min Ch B" ) # change displayed value
        off1lab.config(text = "Max Ch B" ) # change displayed value
    else:
        amp1lab.config(text = "Amp Ch B" )
        off1lab.config(text = "Off Ch B" )

#
def UpdateAwgContRet(temp):
    MakeAWGwaves()
 
# waveform build routines

def build_sine_wave(cycle_len, num_cycles=1, phase_degree=0, low_level=0, high_level=2**16-1, dac_min=0, dac_max=2**16-1):
    '''Build Sine Wave
    
    :param cycle_len: cycle length (in points).
    :param num_cycles: number of cycles.
    :param phase_degree: starting-phase (in degrees)
    :param low_level: the sine low level.
    :param high_level: the sine high level.
    :param dac_min: DAC minimal value.
    :param dac_max: DAC maximal value.
    :returns: `numpy.array` with the wave data (DAC values)        
    '''        
    cycle_len = int(cycle_len)
    num_cycles = int(num_cycles)
    
    if cycle_len <= 0 or num_cycles <= 0:
        return None   
    
    wav_len = cycle_len * num_cycles
    
    phase = float(phase_degree) * numpy.pi / 180.0
    x = numpy.linspace(start=phase, stop=phase+2*numpy.pi, num=cycle_len, endpoint=False)
    
    zero_val = (low_level + high_level) / 2.0
    amplitude = (high_level - low_level) / 2.0
    y = numpy.sin(x) * amplitude + zero_val
    y = numpy.clip(y, dac_min, dac_max)    
    
    y = y.astype(numpy.uint16)
    
    wav = numpy.empty(wav_len, dtype=numpy.uint16)
    for n in range(num_cycles):
        wav[n * cycle_len : (n + 1) * cycle_len] = y
    
    return numpy.array(wav).astype('i1')
#
def build_triangle_wave(cycle_len, num_cycles=1, phase_degree=0, low_level=0, high_level=2**16-1, dac_min=0, dac_max=2**16-1):
    '''Build Triangle Wave
    
    :param cycle_len: cycle length (in points).
    :param num_cycles: number of cycles.
    :param phase_degree: starting-phase (in degrees)
    :param low_level: the triangle low level.
    :param high_level: the triangle high level.
    :param dac_min: DAC minimal value.
    :param dac_max: DAC maximal value.
    :returns: `numpy.array` with the wave data (DAC values)        
    '''        
    cycle_len = int(cycle_len)
    num_cycles = int(num_cycles)
    
    if cycle_len <= 0 or num_cycles <= 0:
        return None   
    
    wav_len = cycle_len * num_cycles
    
    phase = float(phase_degree) * numpy.pi / 180.0
    x = numpy.linspace(start=phase, stop=phase+2*numpy.pi, num=cycle_len, endpoint=False)
    
    zero_val = (low_level + high_level) / 2.0
    amplitude = (high_level - low_level) / 2.0
    y = numpy.sin(x)
    y = numpy.arcsin(y) * 2 * amplitude / numpy.pi + zero_val
    y = numpy.round(y)
    y = numpy.clip(y, dac_min, dac_max)    
    
    y = y.astype(numpy.uint16)
    
    wav = numpy.empty(wav_len, dtype=numpy.uint16)
    for n in range(num_cycles):
        wav[n * cycle_len : (n + 1) * cycle_len] = y
    
    return numpy.array(wav).astype('i1')

def build_square_wave(cycle_len, num_cycles=1, duty_cycle=50.0, phase_degree=0, low_level=0, high_level=2**16-1, dac_min=0, dac_max=2**16-1):
    '''Build Square Wave
    
    :param cycle_len: cycle length (in points).
    :param num_cycles: number of cycles.
    :param duty_cycle: duty-cycle (between 0% and 100%)
    :param phase_degree: starting-phase (in degrees)
    :param low_level: the square low level.
    :param high_level: the square high level.
    :param dac_min: DAC minimal value.
    :param dac_max: DAC maximal value.
    :returns: `numpy.array` with the wave data (DAC values)        
    '''        
    cycle_len = int(cycle_len)
    num_cycles = int(num_cycles)
    
    if cycle_len <= 0 or num_cycles <= 0:
        return None   
    
    wav_len = cycle_len * num_cycles
    
    duty_cycle = numpy.clip(duty_cycle, 0.0, 100.0)
    low_level = numpy.clip(low_level, dac_min, dac_max)
    high_level = numpy.clip(high_level, dac_min, dac_max)
    
    phase = int((float(phase_degree)/360.0)*cycle_len)
    x = numpy.linspace(start=0, stop=2*numpy.pi, num=cycle_len, endpoint=False)
    x = x <= 2 * numpy.pi * duty_cycle / 100.0
    y = numpy.full(x.shape, low_level)
    y[x] = high_level
    
    y = y.astype(numpy.uint16)
    
    wav = numpy.empty(wav_len, dtype=numpy.uint16)
    for n in range(num_cycles):
        wav[n * cycle_len : (n + 1) * cycle_len] = y
    wav = numpy.roll(wav, phase)
    return numpy.array(wav).astype('i1')

def Left10RelPhase():
    global AWGBLastWave

    ShiftVal = int((-2047/360)*10)
    AWGBNewWave = numpy.roll(AWGBLastWave, ShiftVal)
    AWGBSendWave(AWGBNewWave)

def Right10RelPhase():
    global AWGBLastWave

    ShiftVal = int((2047/360)*10)
    AWGBNewWave = numpy.roll(AWGBLastWave, ShiftVal)
    AWGBSendWave(AWGBNewWave)
    
def SetAwgRelPhase():
    global AWGRelPhaseEntry, AWGBLastWave

    ShiftVal = int((2047/360)*float(AWGRelPhaseEntry.get()))
    AWGBNewWave = numpy.roll(AWGBLastWave, ShiftVal)
    AWGBSendWave(AWGBNewWave)
#    
def SetAwgSymmetry():
    global V

    #send(":FUNCtion:RAMP:SYMMetry " + str(int(AWGASymmetryEntry.get())))
#
def SetAwgDutyCycle():
    global AWGADutyCycleEntry

    #send(":FUNCtion:PULSe:DTYCycle " + str(int(AWGADutyCycleEntry.get())))
#
def SetAwgWidth():
    global AWGAWidthEntry

    WidthNum = UnitConvert(AWGAWidthEntry.get())
    #send(":FUNCtion:PULSe:WIDTh " + str(WidthNum))
#
def AWGAMakeDC():
    global AWGAAmplvalue, AWGAOffsetvalue, AWGAAmplEntry, AWGAOffsetEntry
    global MaxSamples, AWGARecLength, AWGPeakToPeak, AWGBuffLen, AWGALength
    global AWGSampleRate
    
    try:
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    except:
        AWGBAmplvalue = 0.0
    try:
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    except:
        AWGAOffsetvalue = 1.0
    AWG3 = numpy.full(AWGBuffLen, 1.0)
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeSine():
    global AWGAAmplvalue, AWGAOffsetvalue, AWGAAmplEntry, AWGAOffsetEntry
    global AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength
    global AWGAShape

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    # print(AWGSampleRate, AWGAFreqvalue, MaxSamples)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #
    Cycles = numpy.floor(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    #Make Sine Wave
    # print("Cycles = ", Cycles)
    AWG3 = []
    if AWGAShape.get() == 1:
        AWG3 = numpy.sin(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    else:
        AWG3 = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeRampUp():
    global AWGAAmplvalue, AWGAOffsetvalue ,AWGAAmplEntry, AWGAOffsetEntry
    global AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    Cycles = numpy.ceil(AWGAFreqvalue/MaxRepRate)
    #Cycles = numpy.ceil(MaxSamples/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.linspace(-1.0, 1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
##
def AWGAMakeRampDn():
    global AWGAAmplvalue, AWGAOffsetvalue, AWGAAmplEntry, AWGAOffsetEntry
    global AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #Cycles = numpy.ceil(MaxSamples/AWGAperiodvalue)
    Cycles = numpy.ceil(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.linspace(1.0, -1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeTriangle():
    global AWGAFreqvalue, AWGAFreqEntry
    global AWGAAmplEntry, AWGAAmplvalue, AWGAOffsetvalue, AWGAOffsetEntry
    global AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    DutyCycle = AWGADutyCyclevalue / 100.0
    #Cycles = int(MaxSamples/AWGAperiodvalue)
    Cycles = numpy.ceil(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    PulseWidth = int(CycleLen * DutyCycle)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(CycleLen - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    #
    # Make Wave
    AWG0 = numpy.concatenate((numpy.linspace(-1.0, 1.0, PulseWidth), numpy.linspace(1.0, -1.0, Remainder)))
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeSquare():
    global ser, SAMPLErate, AWGAFreqvalue, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAAmplEntry, AWGAAmplvalue, AWGAOffsetvalue, AWGAOffsetEntry
    global AWGARecLength, AWGPeakToPeak, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    DutyCycle = AWGADutyCyclevalue / 100.0
    # Cycles = int(MaxSamples/AWGAperiodvalue)
    Cycles = numpy.ceil(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    PulseWidth = int(CycleLen * DutyCycle)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(CycleLen - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    #
    #Make Wave
    #
    AWG0 = numpy.concatenate((numpy.full(PulseWidth, 1.0), numpy.full(Remainder, -1.0)))
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeSinc():
    global ser, SAMPLErate, AWGAFreqvalue, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAAmplEntry, AWGAAmplvalue, AWGAOffsetvalue, AWGAOffsetEntry
    global AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    #Cycles = int(MaxSamples/AWGAperiodvalue)
    Cycles = numpy.floor(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    # Make Sinc Wave
    NumCy = AWGADutyCyclevalue
    MNumCy = 0 - NumCy
    # numpy.sinc(numpy.linspace(-4, 4, 400))
    # will product 4 “cycles” 400 samples long. 
    AWG0 = numpy.sinc(numpy.linspace(MNumCy, NumCy, CycleLen))
    AWG3 = AWG0
    index = 1
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
        index = index + 1
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeStair():
    global ser, SAMPLErate, AWGAFreqvalue, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAAmplEntry, AWGAAmplvalue, AWGAOffsetvalue, AWGAOffsetEntry
    global AWGPeakToPeak, AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    MaxV = 1.0 # AWGAOffsetvalue
    MinV = -1.0 # AWGAAmplvalue
    AWG0 = []
    AWG3 = []
    Treads = int(AWGADutyCyclevalue) # *100.0)
    if Treads < 2:
        Treads = 2
    TreadWidth = int(AWGAperiodvalue / Treads)
    TreadHight = (MaxV-MinV)/(Treads-1)
    Cycles = numpy.floor(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    # print("Treads = ", Treads, "TreadHight = ", TreadHight)
    # make one cycle
    for i in range(Treads):
        for j in range(TreadWidth):
            AWG0.append(MinV)
        MinV = MinV + TreadHight
    #
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Steps")
    AWGASendWave(AWG3)
##
def AWGAMakeFullWaveSine():
    global ser, SAMPLErate, AWGAFreqvalue, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAAmplEntry, AWGAAmplvalue, AWGAOffsetvalue, AWGAOffsetEntry
    global AWGPeakToPeak, AWGARecLength, AWGSampleRate, MaxSamples, duty1lab
    global AwgString9, AWGALength, AWGBuffLen
#
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    # print(AWGSampleRate, AWGAFreqvalue, MaxSamples)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #
    Cycles = numpy.floor(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    AWG3 = numpy.sin(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    AWG3 = numpy.absolute(AWG3) # * -1.0
    AWG3 = AWG3 - 0.5
    AWG3 = AWG3 * 2.0
#
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
# 
def AWGAMakeHalfWaveSine():
    global ser, SAMPLErate, AWGAFreqvalue, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAAmplEntry, AWGAAmplvalue, AWGAOffsetvalue, AWGAOffsetEntry
    global AWGPeakToPeak, AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength
# 
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    # print(AWGSampleRate, AWGAFreqvalue, MaxSamples)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #
    Cycles = numpy.floor(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    AWG3 = numpy.sin(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    AWG3 = numpy.maximum(AWG3, numpy.zeros(RecLength))
    #AWG3 = numpy.minimum(AWG3, numpy.zeros(RecLength))
    AWG3 = AWG3 - 0.5
    AWG3 = AWG3 * 2.0
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeFourier():
    global ser, SAMPLErate, AWGAFreqvalue, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAAmplEntry, AWGAAmplvalue, AWGAOffsetvalue, AWGAOffsetEntry
    global AWGPeakToPeak, AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength
# 
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    Max_term = int(AWGADutyCyclevalue)
    #
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    # print(AWGSampleRate, AWGAFreqvalue, MaxSamples)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #
    Cycles = numpy.floor(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    AWG3 = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength)) # the fundamental
    k = 3
    while k <= Max_term:
        # Add odd harmonics up to max_term
        Harmonic = (math.sin(k*numpy.pi/2.0)/k)*(numpy.cos(numpy.linspace(0, k*2*Cycles*numpy.pi, RecLength)))
        AWG3 = AWG3 + Harmonic
        k = k + 2 # skip even numbers
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Harmonics")
    AWGASendWave(AWG3)
#
def AWGAMakeUUNoise():
    global AWGAAmplvalue, AWGAOffsetvalue, AWGAAmplEntry, AWGAOffsetEntry
    global AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #Cycles = numpy.ceil(MaxSamples/AWGAperiodvalue)
    Cycles = numpy.ceil(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.random.uniform(1.0, -1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, numpy.random.uniform(1.0, -1.0, CycleLen)))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
def AWGAMakeUGNoise():
    global AWGAAmplvalue, AWGAOffsetvalue, AWGAAmplEntry, AWGAOffsetEntry
    global AWGARecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGALength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGAFreqvalue = UnitConvert(AWGAFreqEntry.get())
    if AWGAFreqvalue == 0.0:
        AWGAFreqvalue = 10.0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,AWGAFreqvalue)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #Cycles = numpy.ceil(MaxSamples/AWGAperiodvalue)
    Cycles = numpy.ceil(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.random.normal(0.0, 1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, numpy.random.normal(0.0, 1.0, CycleLen)))
    #
    AWGALength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty1lab.config(text="Percent")
    AWGASendWave(AWG3)
#
#
# Start AWG B here
#
def AWGBMakeDC():
    global AWGBAmplvalue, AWGBOffsetvalue ,AWGBAmplEntry, AWGBOffsetEntry
    global MaxSamples, AWGBRecLength, AWGPeakToPeak, AWGBuffLen, AWGBLength
    global AWGSampleRate
    
    try:
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    except:
        AWGBAmplvalue = 0.0
    try:
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    except:
        AWGBOffsetvalue = 1.0
    #
    AWG3 = numpy.full(AWGBuffLen, 1.0)
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
#
def AWGBMakeSine():
    global AWGBAmplvalue, AWGBOffsetvalue, AWGBAmplEntry, AWGBOffsetEntry
    global AWGBRecLength, AWGSampleRate, AWGBuffLen, MaxSamples, AWGBLength
    global AWGBShape

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    #
    Cycles = numpy.floor(AWGBFreqvalue/MaxRepRate)
    #Cycles = int(MaxSamples/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    #Make Sine Wave
    AWG3 = []
    if AWGBShape.get() == 1:
        AWG3 = numpy.sin(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    else:
        AWG3 = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
#
def AWGBMakeRampUp():
    global AWGBAmplvalue, AWGBOffsetvalue ,AWGBAmplEntry, AWGBOffsetEntry
    global AWGBRecLength, AWGBuffLen, MaxSamples, AWGSampleRate, AWGBLength
    
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    # Cycles = int(MaxSamples/AWGBperiodvalue)
    Cycles = numpy.ceil(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.linspace(-1.0, 1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
##
def AWGBMakeRampDn():
    global AWGBAmplvalue, AWGBOffsetvalue ,AWGBAmplEntry, AWGBOffsetEntry
    global AWGBRecLength, MaxSamples, AWGSampleRate, AWGBuffLen, AWGBLength
    
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    #Cycles = int(MaxSamples/AWGBperiodvalue)
    Cycles = numpy.ceil(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.linspace(1.0, -1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
#
def AWGBMakeTriangle():
    global ser, SAMPLErate, AWGBFreqvalue, AWGBFreqEntry
    global AWGBRecLength, MaxSamples, AWGSampleRate, AWGBLength, AWGBuffLen
    global AWGBAmplEntry, AWGBAmplvalue, AWGBOffsetvalue, AWGBOffsetEntry

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))
    DutyCycle = AWGBDutyCyclevalue / 100.0
    #Cycles = int(MaxSamples/AWGBperiodvalue)
    Cycles = int(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    PulseWidth = int(CycleLen * DutyCycle)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(CycleLen - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    #
    # Make Wave
    AWG0 = []
    AWG3 = []
    AWG0 = numpy.concatenate((numpy.linspace(-1.0, 1.0, PulseWidth), numpy.linspace(1.0, -1.0, Remainder)))
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
#
def AWGBMakeSquare():
    global ser, SAMPLErate, AWGBFreqvalue, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBAmplEntry, AWGBAmplvalue, AWGBOffsetvalue, AWGBOffsetEntry
    global AWGBRecLength, MaxSamples, AWGSampleRate, AWGBLength, AWGBuffLen
    
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))
    DutyCycle = AWGBDutyCyclevalue / 100.0
    # Cycles = int(MaxSamples/AWGBperiodvalue)
    Cycles = numpy.ceil(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    PulseWidth = int(CycleLen * DutyCycle)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(CycleLen - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    #
    #Make Wave
    # AWG3 = numpy.full(MaxSamples, DCValue)
    AWG0 = []
    AWG3 = []
    AWG0 = numpy.concatenate((numpy.full(PulseWidth, 1.0), numpy.full(Remainder, -1.0)))
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
#
def AWGBMakeSinc():
    global ser, SAMPLErate, AWGBFreqvalue, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBAmplEntry, AWGBAmplvalue, AWGBOffsetvalue, AWGBOffsetEntry
    global AWGBRecLength, AWGSampleRate, MaxSamples, AWGBLength

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))
    # Cycles = int(MaxSamples/AWGBperiodvalue)
    Cycles = numpy.floor(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    NumCy = AWGBDutyCyclevalue
    MNumCy = 0 - NumCy
    # numpy.sinc(numpy.linspace(-4, 4, 400))
    # will produce 4 “cycles” 400 samples long. 
    AWG0 = numpy.sinc(numpy.linspace(MNumCy, NumCy, RecLength))
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
##
def AWGBMakeStair():
    global ser, SAMPLErate, AWGBFreqvalue, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBAmplEntry, AWGBAmplvalue, AWGBOffsetvalue, AWGBOffsetEntry
    global AWGBRecLength, AWGPeakToPeak, AWGSampleRate, MaxSamples, AWGBLength, AWGBuffLen

    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))

    MaxV = 1.0 # AWGBOffsetvalue
    MinV = -1.0 # AWGBAmplvalue
    AWG0 = []
    AWG3 = []
    Treads = int(AWGBDutyCyclevalue) # *100.0)
    if Treads < 2:
        Treads = 2
    TreadWidth = int(AWGBperiodvalue / Treads)
    TreadHight = (MaxV-MinV)/(Treads-1)
    Cycles = numpy.floor(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    # print("Treads = ", Treads, "TreadHight = ", TreadHight)
    # make one cycle
    for i in range(Treads):
        for j in range(TreadWidth):
            AWG0.append(MinV)
        MinV = MinV + TreadHight
    #
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, AWG0))
    #
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Steps")
    AWGBSendWave(AWG3)
##
def AWGBMakeFullWaveSine():
    global ser, SAMPLErate, AWGBFreqvalue, AWGbFreqEntry, AWGbDutyCycleEntry
    global AWGBAmplEntry, AWGBAmplvalue, AWGBOffsetvalue, AWGBOffsetEntry
    global AWGPeakToPeak, AWGBRecLength, AWGSampleRate, MaxSamples, AWGBLength
# 
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    # print(AWGSampleRate, AWGAFreqvalue, MaxSamples)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    #
    Cycles = numpy.floor(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    
    AWG3 = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    AWG3 = numpy.absolute(AWG3) # * -1.0
    AWG3 = AWG3 - 0.5
    AWG3 = AWG3 * 2.0
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
# 
def AWGBMakeHalfWaveSine():
    global ser, SAMPLErate, AWGBFreqvalue, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBAmplEntry, AWGBAmplvalue, AWGBOffsetvalue, AWGBOffsetEntry
    global AWGPeakToPeak, AWGBRecLength, AWGSampleRate, MaxSamples, AWGBLength
# 
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    # print(AWGSampleRate, AWGAFreqvalue, MaxSamples)
    AWGAperiodvalue = AWGSampleRate/AWGAFreqvalue
    #
    Cycles = numpy.floor(AWGAFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGAperiodvalue)
    AWG3 = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    AWG3 = numpy.maximum(AWG3, numpy.zeros(RecLength))
    AWG3 = AWG3 - 0.5
    AWG3 = AWG3 * 2.0
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    # duty2lab.config(text="%")
    AWGBSendWave(AWG3)
##
def AWGBMakeFourier():
    global ser, SAMPLErate, AWGBFreqvalue, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBAmplEntry, AWGBAmplvalue, AWGBOffsetvalue, AWGBOffsetEntry
    global AWGPeakToPeak, AWGbRecLength, AWGSampleRate, MaxSamples, AWGBLength, AWGBuffLen
# 
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(MaxSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))
    Max_term = int(AWGBDutyCyclevalue)
    #
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    # print(AWGSampleRate, AWGAFreqvalue, MaxSamples)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    #
    Cycles = numpy.floor(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    AWG3 = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength)) # the fundamental
    k = 3
    while k <= Max_term:
        # Add odd harmonics up to max_term
        Harmonic = (math.sin(k*numpy.pi/2.0)/k)*(numpy.cos(numpy.linspace(0, k*2*Cycles*numpy.pi, RecLength)))
        AWG3 = AWG3 + Harmonic
        k = k + 2 # skip even numbers
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Harmonics")
    AWGBSendWave(AWG3)
##
def AWGBMakeUUNoise():
    global AWGBAmplvalue, AWGBOffsetvalue ,AWGBAmplEntry, AWGBOffsetEntry
    global AWGBRecLength, AWGBuffLen, MaxSamples, AWGSampleRate, AWGBLength
    
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    # Cycles = int(MaxSamples/AWGBperiodvalue)
    Cycles = numpy.ceil(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.random.uniform(-1.0, 1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, numpy.random.uniform(-1.0, 1.0, CycleLen)))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
##
def AWGBMakeUGNoise():
    global AWGBAmplvalue, AWGBOffsetvalue ,AWGBAmplEntry, AWGBOffsetEntry
    global AWGBRecLength, AWGBuffLen, MaxSamples, AWGSampleRate, AWGBLength
    
    SetAwgSampleRate()
    MaxRepRate = numpy.ceil(AWGSampleRate / AWGBuffLen)
    AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    AWGBFreqvalue = UnitConvert(AWGBFreqEntry.get())
    if AWGBFreqvalue == 0.0:
        AWGBFreqvalue = 10.0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,AWGBFreqvalue)
    AWGBperiodvalue = AWGSampleRate/AWGBFreqvalue
    # Cycles = int(MaxSamples/AWGBperiodvalue)
    Cycles = numpy.ceil(AWGBFreqvalue/MaxRepRate)
    if Cycles < 1:
        Cycles = 1
    RecLength = int(Cycles * AWGBperiodvalue)
    CycleLen = int(RecLength / Cycles)
    #
    #Make Wave
    AWG0 = numpy.random.normal(0.0, 1.0, CycleLen)
    AWG3 = AWG0
    # print( index , len(AWG3) )
    while len(AWG3) < AWGBuffLen-CycleLen:
        AWG3 = numpy.concatenate((AWG3, numpy.random.normal(0.0, 1.0, CycleLen)))
    #
    AWGBLength.config(text = "L = " + str(int(len(AWG3)))) # change displayed value
    duty2lab.config(text="Percent")
    AWGBSendWave(AWG3)
##
def AWGAOutToggle():
    global AwgAOnOffBt

    if AwgAOnOffBt.config('text')[-1] == 'ON':
        AwgAOnOffBt.config(text='OFF', style="Stop.TButton")
        SetAwgA_Ampl(0)
    else:
        AwgAOnOffBt.config(text='ON', style="Run.TButton")
        SetAwgA_Ampl(255)

#
def AWGBOutToggle():
    global AwgBOnOffBt

    if AwgBOnOffBt.config('text')[-1] == 'ON':
        AwgBOnOffBt.config(text='OFF', style="Stop.TButton")
        SetAwgB_Ampl(0)
    else:
        AwgBOnOffBt.config(text='ON', style="Run.TButton")
        SetAwgB_Ampl(255)
#
# Load configuration from IA window button
def BLoadConfigIA():
    global iawindow

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=iawindow)
    BLoadConfig(filename)
## Load configuration from SA window button
def BLoadConfigSA():
    global freqwindow

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=freqwindow)
    BLoadConfig(filename)
## Load configuration from Bode window button
def BLoadConfigBP():
    global bodewindow

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=bodewindow)
    BLoadConfig(filename)
## Load configuration from Scope window button
def BLoadConfigTime():
    global root

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=root)
    BLoadConfig(filename)
    UpdateTimeTrace()
## Run a script file
def RunScript():
    global VBuffA, VBuffB, VBuffC, VBuffD, NoiseCH1, NoiseCH2, VFilterA, VFilterB
    global VmemoryA, VmemoryB, VmemoryC, VmemoryD, AWGAwaveform, AWGBwaveform
    global VUnAvgA, VUnAvgB, IUnAvgA, IUnAvgB, UnAvgSav
    global TgInput, TgEdge, SingleShot, AutoLevel, SingleShotSA, ManualTrigger
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, AutoCenterA, AutoCenterB
    global YsignalVA, YsignalVB, YsignalM, YsignalMX, YsignalMY
    global CHAsb, CHBsb, CHMsb, HScale, FreqTraceMode
    global CHAsbxy, CHBsbxy, CHANNELS
    global CHAVPosEntryxy, CHBVPosEntryxy
    global ShowC1_V, ShowC4_V, ShowC2_V, ShowC3_V, MathTrace, MathXUnits, MathYUnits
    global CHAVPosEntry, CHMPosEntry, CHBVPosEntry, HozPossentry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGATerm, AWGAMode, AWGARepeatFlag, AWGBRepeatFlag
    global AWGSync, AWGAIOMode
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1, MeasDCI1, MeasMinI1
    global MeasMaxI1, MeasMidI1, MeasPPI1, MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2
    global MeasPPV2, MeasDCI2, MeasMinI2, MeasMaxI2, MeasMidI2, MeasPPI2, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasRMSI1, MeasRMSI2, MeasPhase, MeasDelay
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ, IASource, DisplaySeries
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC, AWG_Amp_Mode
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, AWGAPhaseDelay, AWGBPhaseDelay
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global MathAxis, MathXAxis, MathYAxis, Show_MathX, Show_MathY, MathScreenStatus, MathWindow
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2, CHAI_RC_HP, CHBI_RC_HP
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2, RelPhaseCenter, ImpedanceCenter
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global Show_Rseries, Show_Xseries, Show_Magnitude, Show_Angle
    global AWGABurstFlag, AWGACycles, AWGABurstDelay, AWGAwaveform, AWGAcsvFile, AWGBcsvFile
    global AWGBBurstFlag, AWGBCycles, AWGBBurstDelay, AWGBwaveform, AWGAwavFile, AWGBwavFile
    global SCLKPort, SDATAPort, SLATCHPort, FminEntry, HtMulEntry
    global phawindow, PhAca, PhAScreenStatus, PhADisp
    global GRWPhA, X0LPhA, GRHPhA, Y0TPhA, EnableScopeOnly
    global VScale, IScale, RefphEntry, BoardStatus, boardwindow, BrdSel
    global vat_btn, vbt_btn, iat_btn, ibt_btn, vabt_btn, RollBt, Roll_Mode
    global ScreenWidth, ScreenHeight
    global TRACEwidth, ColorMode, ca, COLORcanvas, COLORtrace4, COLORtraceR4, COLORtext
    global AWGANoiseEntry, AWGBNoiseEntry, AWGAsbnoise, AWGBsbnoise
    global AWGFiltA, AWGALenEntry, AWGFiltABoxCar, AWGFiltALength, digfltwindow
    global AWGFiltB, AWGBLenEntry, AWGFiltBBoxCar, AWGFiltBLength
    global DFiltACoef, DFiltBCoef, AWGACoef, AWGBCoef

    filename = askopenfilename(defaultextension = ".txt", filetypes=[("Script files", "*.txt")], parent=root)
    # Read Script commands from file
    try:
        ConfgFile = open(filename)
        for line in ConfgFile:
            try:
                exec( line.rstrip(), globals(), globals())
                # exec( line.rstrip() )
            except:
                print( "Skipping " + line.rstrip())
                showwarning("Syntax Error!",("Syntax Error found in line:\n " + line.rstrip()))
        ConfgFile.close()
    except:
        print( "Config File Not Found.")
        showwarning("Warning!","Script File Not Found.")
        
## Toggle the Background and text colors based on ColorMode
def BgColor():
    global COLORtext, COLORcanvas, ColorMode, Bodeca, BodeScreenStatus, PhAca, PhAScreenStatus
    global ca, Freqca, SpectrumScreenStatus, XYca, XYScreenStatus, IAca, IAScreenStatus
    global COLORtrace4, COLORtraceR4, TRACEwidth

    if ColorMode.get() > 0: # White background
        if TRACEwidth.get() < 2:
            TRACEwidth.set(2)
        COLORtext = "#000000"   # 100% black
        COLORtrace4 = "#a0a000" # 50% yellow
        COLORtraceR4 = "#606000"   # 25% yellow
        COLORcanvas = "#ffffff"     # 100% white
    else:
        COLORcanvas = "#000000"   # 100% black
        COLORtrace4 = "#ffff00" # 100% yellow
        COLORtraceR4 = "#808000"   # 50% yellow
        COLORtext = "#ffffff"     # 100% white
    ca.config(background=COLORcanvas)
    UpdateTimeScreen()
    if SpectrumScreenStatus.get() > 0:
        Freqca.config(background=COLORcanvas)
        UpdateFreqScreen()
    if XYScreenStatus.get() > 0:
        XYca.config(background=COLORcanvas)
        UpdateXYScreen()
    if PhAScreenStatus.get() > 0:
        PhAca.config(background=COLORcanvas)
        UpdatePhAScreen()
    if IAScreenStatus.get() > 0:
        IAca.config(background=COLORcanvas)
        UpdateIAScreen()
    if BodeScreenStatus.get() > 0:
        Bodeca.config(background=COLORcanvas)
        UpdateBodeScreen()
## Color Selector / Editor
def ColorSelector():
    global ColorScreenStatus, FrameBG, SWRev, RevDate, ColorWindow
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8

    if ColorScreenStatus.get() == 0:
        ColorScreenStatus.set(1)
        #
        ColorWindow = Toplevel()
        ColorWindow.title("Color Selector " + SWRev + RevDate)
        ColorWindow.resizable(FALSE,FALSE)
        ColorWindow.protocol("WM_DELETE_WINDOW", DestroyColorScreen)
        ColorWindow.configure(background=FrameBG)
        
        Colorframe1 = LabelFrame(ColorWindow, text="Trace Colors", style="A10R1.TLabelframe") #"A10T5.TLabelframe")
        Colorframe1.pack(side=TOP, expand=1, fill=Y)
    # Color value = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
        trace1bt = Button(Colorframe1, text="COLORtrace1", style="T1W16.TButton", command=SetColorT1 ) #COLORtrace1 = "#00ff00"   # 100% green
        trace1bt.grid(row=0, column=0, columnspan=1, sticky=W)
        #
        trace2bt = Button(Colorframe1, text="COLORtrace2", style="T2W16.TButton", command=SetColorT2 ) #COLORtrace2 = "#ff8000"   # 100% orange
        trace2bt.grid(row=0, column=1, columnspan=1, sticky=W)
        #
        trace3bt = Button(Colorframe1, text="COLORtrace3", style="T3W16.TButton", command=SetColorT3 ) #COLORtrace3 = "#00ffff"   # 100% cyan
        trace3bt.grid(row=0, column=2, columnspan=1, sticky=W)
        #
        trace4bt = Button(Colorframe1, text="COLORtrace4", style="T4W16.TButton", command=SetColorT4 ) #COLORtrace4 = "#ffff00"   # 100% yellow
        trace4bt.grid(row=0, column=3, columnspan=1, sticky=W)
        #
        trace5bt = Button(Colorframe1, text="COLORtrace5", style="T5W16.TButton", command=SetColorT5 ) #COLORtrace5 = "#ff00ff"   # 100% magenta
        trace5bt.grid(row=1, column=0, columnspan=1, sticky=W)
        #
        trace6bt = Button(Colorframe1, text="COLORtrace6", style="T6W16.TButton", command=SetColorT6 ) #COLORtrace6 = "#C80000"   # 90% red
        trace6bt.grid(row=1, column=1, columnspan=1, sticky=W)
        #
        trace7bt = Button(Colorframe1, text="COLORtrace7", style="T7W16.TButton", command=SetColorT7 ) #COLORtrace7 = "#8080ff"   # 100% purple
        trace7bt.grid(row=1, column=2, columnspan=1, sticky=W)
        #
        tracer1bt = Button(Colorframe1, text="COLORtraceR1", style="TR1W16.TButton", command=SetColorTR1 ) #COLORtraceR1 = "#008000"   # 50% green
        tracer1bt.grid(row=2, column=0, columnspan=1, sticky=W)
        #
        tracer2rbt = Button(Colorframe1, text="COLORtraceR2", style="TR2W16.TButton", command=SetColorTR2 ) #COLORtraceR2 = "#905000"   # 50% orange
        tracer2rbt.grid(row=2, column=1, columnspan=1, sticky=W)
        #
        tracer3bt = Button(Colorframe1, text="COLORtraceR3", style="TR3W16.TButton", command=SetColorTR3 ) #COLORtraceR3 = "#008080"   # 50% cyan
        tracer3bt.grid(row=2, column=2, columnspan=1, sticky=W)
        #
        tracer4bt = Button(Colorframe1, text="COLORtraceR4", style="TR4W16.TButton", command=SetColorTR4 ) #COLORtraceR4 = "#808000"   # 50% yellow
        tracer4bt.grid(row=2, column=3, columnspan=1, sticky=W)
        #
        tracer5bt = Button(Colorframe1, text="COLORtraceR5", style="TR5W16.TButton", command=SetColorTR5 ) #COLORtraceR5 = "#800080"   # 50% magenta
        tracer5bt.grid(row=3, column=0, columnspan=1, sticky=W)
        #
        tracer6bt = Button(Colorframe1, text="COLORtraceR6", style="TR6W16.TButton", command=SetColorTR6 ) #COLORtraceR6 = "#800000"   # 80% red
        tracer6bt.grid(row=3, column=1, columnspan=1, sticky=W)
        #
        tracer7bt = Button(Colorframe1, text="COLORtraceR7", style="TR7W16.TButton", command=SetColorTR7 ) #COLORtraceR7 = "#4040a0"  # 80% purple
        tracer7bt.grid(row=3, column=2, columnspan=1, sticky=W)
        #
        gridbt = Button(Colorframe1, text="COLORgrid", style="W16.TButton", command=SetColorGrid ) #COLORgrid = "#808080"     # 50% Gray
        gridbt.grid(row=4, column=0, columnspan=1, sticky=W)
        zerolinebt = Button(Colorframe1, text="COLORzeroline", style="ZLW16.TButton", command=SetColorZLine ) #COLORzeroline = "#0000ff" # 100% blue
        zerolinebt.grid(row=4, column=1, columnspan=1, sticky=W)
        ctriggerbt = Button(Colorframe1, text="COLORtrigger", style="TGW16.TButton", command=SetColorTrig ) #COLORtrigger = "#ff0000"  # 100% red
        ctriggerbt.grid(row=4, column=2, columnspan=1, sticky=W)
    #
        ctextbt = Button(Colorframe1, text="COLORtext", style="W16.TButton", command=SetColorText ) #COLORtext = "#ffffff"     # 100% white
        ctextbt.grid(row=4, column=3, columnspan=1, sticky=W)
    #
        cdismissbt = Button(Colorframe1, text="Dismiss", style="W16.TButton", command=DestroyColorScreen )
        cdismissbt.grid(row=5, column=0, columnspan=1, sticky=W)
        cresetbt = Button(Colorframe1, text="Reset Colors", style="W16.TButton", command=ResetAllColors )
        cresetbt.grid(row=5, column=1, columnspan=1, sticky=W)
##
def DestroyColorScreen():
    global ColorScreenStatus, ColorWindow
    
    if ColorScreenStatus.get() == 1:
        ColorScreenStatus.set(0)
        ColorWindow.destroy()
##
def ResetAllColors():
    global COLORtext, COLORcanvas, COLORtrigger, COLORsignalband, COLORframes, COLORgrid, COLORzeroline
    global COLORtrace1, COLORtraceR1, COLORtrace2, COLORtraceR2, COLORtrace3, COLORtraceR3, COLORtrace4, COLORtraceR4
    global COLORtrace5, COLORtraceR5, COLORtrace6, COLORtraceR6, COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8
    
    ResetColors()
    root.style.configure("T1W16.TButton", background=COLORtrace1)
    root.style.configure("Rtrace1.TButton", background=COLORtrace1)
    root.style.configure("Strace1.TButton", background=COLORtrace1)
    root.style.configure("Ctrace1.TButton", background=COLORtrace1)
    root.style.configure("Strace1.TCheckbutton", background=COLORtrace1)
    root.style.configure("T2W16.TButton", background=COLORtrace2)
    root.style.configure("Rtrace2.TButton", background=COLORtrace2)
    root.style.configure("Strace2.TButton", background=COLORtrace2)
    root.style.configure("Ctrace2.TButton", background=COLORtrace2)
    root.style.configure("Strace2.TCheckbutton", background=COLORtrace2)
    root.style.configure("T3W16.TButton", background=COLORtrace3)
    root.style.configure("Rtrace3.TButton", background=COLORtrace3)
    root.style.configure("Strace3.TButton", background=COLORtrace3)
    root.style.configure("Ctrace3.TButton", background=COLORtrace3)
    root.style.configure("Strace3.TCheckbutton", background=COLORtrace3)
    root.style.configure("T4W16.TButton", background=COLORtrace4)
    root.style.configure("Rtrace4.TButton", background=COLORtrace4)
    root.style.configure("Strace4.TButton", background=COLORtrace4)
    root.style.configure("Ctrace4.TButton", background=COLORtrace4)
    root.style.configure("Strace4.TCheckbutton", background=COLORtrace4)
    root.style.configure("T5W16.TButton", background=COLORtrace5)
    root.style.configure("T6W16.TButton", background=COLORtrace6)
    root.style.configure("Rtrace6.TButton", background=COLORtrace6)
    root.style.configure("Strace6.TButton", background=COLORtrace6)
    root.style.configure("Strace6.TCheckbutton", background=COLORtrace6)
    root.style.configure("T7W16.TButton", background=COLORtrace7)
    root.style.configure("Rtrace7.TButton", background=COLORtrace7)
    root.style.configure("Strace7.TButton", background=COLORtrace7)
    root.style.configure("Strace7.TCheckbutton", background=COLORtrace7)
    root.style.configure("TR1W16.TButton", background=COLORtraceR1)
    root.style.configure("TR2W16.TButton", background=COLORtraceR2)
    root.style.configure("TR3W16.TButton", background=COLORtraceR3)
    root.style.configure("TR4W16.TButton", background=COLORtraceR4)
    root.style.configure("TR5W16.TButton", background=COLORtraceR6)
    root.style.configure("TR6W16.TButton", background=COLORtraceR5)
    root.style.configure("TR5W16.TButton", background=COLORtraceR7)
    root.style.configure("TGW16.TButton", background=COLORtrigger)
##    
def SetColorT1():
    global COLORtrace1

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace1", initialcolor=(COLORtrace1))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace1 = str(hexcolor) # hexcolor
        root.style.configure("T1W16.TButton", background=COLORtrace1)
        root.style.configure("Rtrace1.TButton", background=COLORtrace1)
        root.style.configure("Strace1.TButton", background=COLORtrace1)
        root.style.configure("Ctrace1.TButton", background=COLORtrace1)
        root.style.configure("Strace1.TCheckbutton", background=COLORtrace1)
##
def SetColorT2():
    global COLORtrace2
    
    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace2", initialcolor=(COLORtrace2))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace2 = str(hexcolor) # hexcolor
        root.style.configure("T2W16.TButton", background=COLORtrace2)
        root.style.configure("Rtrace2.TButton", background=COLORtrace2)
        root.style.configure("Strace2.TButton", background=COLORtrace2)
        root.style.configure("Ctrace2.TButton", background=COLORtrace2)
        root.style.configure("Strace2.TCheckbutton", background=COLORtrace2)
##
def SetColorT3():
    global COLORtrace3

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace3", initialcolor=(COLORtrace3))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace3 = str(hexcolor) # hexcolor
        root.style.configure("T3W16.TButton", background=COLORtrace3)
        root.style.configure("Rtrace3.TButton", background=COLORtrace3)
        root.style.configure("Strace3.TButton", background=COLORtrace3)
        root.style.configure("Ctrace3.TButton", background=COLORtrace3)
        root.style.configure("Strace3.TCheckbutton", background=COLORtrace3)
##
def SetColorT4():
    global COLORtrace4

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace4", initialcolor=(COLORtrace4))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace4 = str(hexcolor) # hexcolor
        root.style.configure("T4W16.TButton", background=COLORtrace4)
        root.style.configure("Rtrace4.TButton", background=COLORtrace4)
        root.style.configure("Strace4.TButton", background=COLORtrace4)
        root.style.configure("Ctrace4.TButton", background=COLORtrace4)
        root.style.configure("Strace4.TCheckbutton", background=COLORtrace4)
##
def SetColorT5():
    global COLORtrace5

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace5", initialcolor=(COLORtrace5))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace5 = str(hexcolor) # hexcolor
        root.style.configure("T5W16.TButton", background=COLORtrace5)
##
def SetColorT6():
    global COLORtrace6

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace6", initialcolor=(COLORtrace6))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace6 = str(hexcolor) # hexcolor
        root.style.configure("T6W16.TButton", background=COLORtrace6)
        root.style.configure("Rtrace6.TButton", background=COLORtrace6)
        root.style.configure("Strace6.TButton", background=COLORtrace6)
        root.style.configure("Strace6.TCheckbutton", background=COLORtrace6)
##
def SetColorT7():
    global COLORtrace7

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace7", initialcolor=(COLORtrace7))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace7 = str(hexcolor) # hexcolor
        root.style.configure("T7W16.TButton", background=COLORtrace7)
        root.style.configure("Rtrace7.TButton", background=COLORtrace7)
        root.style.configure("Strace7.TButton", background=COLORtrace7)
        root.style.configure("Strace7.TCheckbutton", background=COLORtrace7)
##
def SetColorT8():
    global COLORtrace8

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrace8", initialcolor=(COLORtrace8))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrace7 = str(hexcolor) # hexcolor
##        root.style.configure("T7W16.TButton", background=COLORtrace7)
##        root.style.configure("Rtrace7.TButton", background=COLORtrace7)
##        root.style.configure("Strace7.TButton", background=COLORtrace7)
##        root.style.configure("Strace7.TCheckbutton", background=COLORtrace7)
##
def SetColorTR1():
    global COLORtraceR1

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR1", initialcolor=(COLORtraceR1))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR1 = str(hexcolor) # hexcolor
        root.style.configure("TR1W16.TButton", background=COLORtraceR1)
##
def SetColorTR2():
    global COLORtraceR2

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR2", initialcolor=(COLORtraceR2))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR2 = str(hexcolor) # hexcolor
        root.style.configure("TR2W16.TButton", background=COLORtraceR2)
##
def SetColorTR3():
    global COLORtraceR3

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR3", initialcolor=(COLORtraceR3))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR3 = str(hexcolor) # hexcolor
        root.style.configure("TR3W16.TButton", background=COLORtraceR3)
##
def SetColorTR4():
    global COLORtraceR4

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR4", initialcolor=(COLORtraceR4))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR4 = str(hexcolor) # hexcolor
        root.style.configure("TR4W16.TButton", background=COLORtraceR4)
##
def SetColorTR5():
    global COLORtraceR5

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR5", initialcolor=(COLORtraceR5))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR5 = str(hexcolor) # hexcolor
        root.style.configure("TR5W16.TButton", background=COLORtraceR5)
##
def SetColorTR6():
    global COLORtraceR6

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR6", initialcolor=(COLORtraceR6))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR6 = str(hexcolor) # hexcolor
        root.style.configure("TR6W16.TButton", background=COLORtraceR6)
##
def SetColorTR7():
    global COLORtraceR7

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR7", initialcolor=(COLORtraceR7))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR7 = str(hexcolor) # hexcolor
        root.style.configure("TR7W16.TButton", background=COLORtraceR7)
##
def SetColorTR8():
    global COLORtraceR8

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtraceR8", initialcolor=(COLORtraceR8))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtraceR8 = str(hexcolor) # hexcolor
        ## root.style.configure("TR7W16.TButton", background=COLORtraceR7)
##
def SetColorGrid():
    global COLORgrid

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORgrid", initialcolor=(COLORgrid))
    tempwindow.destroy()
    if hexcolor != None:
        COLORgrid = str(hexcolor) # hexcolor
##
def SetColorText():
    global COLORtext

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtext", initialcolor=(COLORtext))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtext = str(hexcolor) # hexcolor
##
def SetColorTrig():
    global COLORtrigger

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORtrigger", initialcolor=(COLORtrigger))
    tempwindow.destroy()
    if hexcolor != None:
        COLORtrigger = str(hexcolor) # hexcolor
        root.style.configure("TGW16.TButton", background=COLORtrigger)
##
def SetColorZLine():
    global COLORzeroline

    tempwindow = Tk()
    tempwindow.state("withdrawn")
    rgb,hexcolor = askcolor(parent=tempwindow, title="Choose color for COLORzeroline", initialcolor=(COLORzeroline))
    tempwindow.destroy()
    if hexcolor != None:
        COLORzeroline = str(hexcolor) # hexcolor
        root.style.configure("ZLW16.TButton", background=COLORzeroline)
#
## Save scope canvas as encapsulated postscript file
def BSaveScreen():
    global CANVASwidth, CANVASheight
    global COLORtext, MarkerNum, ColorMode
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")])
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n")
    if MarkerNum > 0 or ColorMode.get() > 0:
        ca.postscript(file=filename, height=CANVASheight, width=CANVASwidth, colormode='color', rotate=Orient)
    else:    # temp chnage text corlor to black
        COLORtext = "#000000"
        UpdateTimeScreen()
        # first save postscript file
        ca.postscript(file=filename, height=CANVASheight, width=CANVASwidth, colormode='color', rotate=Orient)
        # now convert to bit map
        # img = Image.open("screen_shot.eps")
        # img.save("screen_shot.gif", "gif")
        COLORtext = "#ffffff"
        UpdateTimeScreen()
## Save XY canvas as encapsulated postscript file
def BSaveScreenXY():
    global CANVASwidthXY, CANVASheightXY, xywindow
    global COLORtext, MarkerNum, ColorMode, XYca
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent=xywindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=xywindow)
    if MarkerNum > 0 or ColorMode.get() > 0:
        XYca.postscript(file=filename, height=CANVASheightXY, width=CANVASwidthXY, colormode='color', rotate=Orient)
    else:    # temp chnage text corlor to black
        COLORtext = "#000000"
        UpdateXYScreen()
        # first save postscript file
        XYca.postscript(file=filename, height=CANVASheightXY, width=CANVASwidthXY, colormode='color', rotate=Orient)
        # now convert to bit map
        # img = Image.open("screen_shot.eps")
        # img.save("screen_shot.gif", "gif")
        COLORtext = "#ffffff"
        UpdateXYScreen()
## Save IA canvas as encapsulated postscript file
def BSaveScreenIA():
    global CANVASwidthIA, CANVASheightIA
    global COLORtext, IAca, ColorMode, iawindow
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent=iawindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=iawindow)
    if ColorMode.get() > 0:
        IAca.postscript(file=filename, height=CANVASheightIA, width=CANVASwidthIA, colormode='color', rotate=Orient)
    else: # temp change text color to black for Black BG
        COLORtext = "#000000"
        UpdateIAScreen()
        # save postscript file
        IAca.postscript(file=filename, height=CANVASheightIA, width=CANVASwidthIA, colormode='color', rotate=Orient)
        # 
        COLORtext = "#ffffff"
        UpdateIAScreen()
## Save Bode canvas as encapsulated postscript file
def BSaveScreenBP():
    global CANVASwidthBP, CANVASheightBP
    global COLORtext, Bodeca, bodewindow
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent = bodewindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=bodewindow)
    if MarkerNum > 0 or ColorMode.get() > 0:
        Bodeca.postscript(file=filename, height=CANVASheightBP, width=CANVASwidthBP, colormode='color', rotate=Orient)
    else: # temp change text color to black
        COLORtext = "#000000"
        UpdateBodeScreen()
        # save postscript file
        Bodeca.postscript(file=filename, height=CANVASheightBP, width=CANVASwidthBP, colormode='color', rotate=Orient)
        # 
        COLORtext = "#ffffff"
        UpdateBodeScreen()
## Save scope all time array data to file
def BSaveData():
    global VBuffA, VBuffB, VBuffC, VBuffD, SAMPLErate, NoiseCH1, NoiseCH2

    # open file to save data
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(filename, 'w')
    DataFile.write( 'Sample-#, CA-V, CB-V \n' )
    for index in range(len(VBuffA)):
        if Roll_Mode.get() > 0:
            TimePnt = float(index+0.0)
        else:
            TimePnt = float((index+0.0)/SAMPLErate)
        DataFile.write(str(TimePnt) + ', ' + str(VBuffA[index]) + ', ' + str(VBuffB[index]) + '\n')
    DataFile.close()

## Save selected scope time array data to file
def BSaveChannelData():
    global SAMPLErate, VBuffA, VBuffB, VBuffC, VBuffD, NoiseCH1, NoiseCH2

    # ask user for channel to save
    Channel = askstring("Choose Channel", "CA-V, CB-V, CC-V, CD-V\n Channel:\n", initialvalue="CA-V")
    if (Channel == None):         # If Cancel pressed, then None
        return
    # open file to save data
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(filename, 'w')
    if Channel == "CA-V":
        DataFile.write( 'Sample-#, CA-V\n' )
        for index in range(len(VBuffA)):
            TimePnt = float((index+0.0)/SAMPLErate)
            DataFile.write( str(TimePnt) + ', ' + str(VBuffA[index]) + '\n')
    elif Channel == "CB-V":
        DataFile.write( 'Sample-#, CB-V\n' )
        for index in range(len(VBuffB)):
            TimePnt = float((index+0.0)/SAMPLErate)
            DataFile.write( str(TimePnt) + ', ' + str(VBuffB[index]) + '\n')
    elif Channel == "CC-V":
        DataFile.write( 'Sample-#, CC-V\n' )
        for index in range(len(VBuffC)):
            TimePnt = float((index+0.0)/SAMPLErate)
            DataFile.write( str(TimePnt) + ', ' + str(VBuffC[index]) + '\n')
    elif Channel == "CD-V":
        DataFile.write( 'Sample-#, CD-V\n' )
        for index in range(len(VBuffD)):
            TimePnt = float((index+0.0)/SAMPLErate)
            DataFile.write( str(TimePnt) + ', ' + str(VBuffD[index]) + '\n')
    DataFile.close()
#
# place text string on clipboard
def BSaveToClipBoard(TempBuffer):
    global VBuffA, VBuffB, VBuffC, VBuffD, SAMPLErate, NoiseCH1, NoiseCH2
    
    root.clipboard_clear()
    for index in range(len(TempBuffer)):
        root.clipboard_append(str(TempBuffer[index])+ '\n')
    root.update()
#
# Get text string from clipboard
def BReadFromClipboard():

    TempBuffer = []
    try:
        clip_text = root.clipboard_get()
        TempBuffer = numpy.fromstring( clip_text, dtype=float, sep='\n' )
        return(TempBuffer)
    except:
        return(TempBuffer)
#
def BLoadDFiltAClip():
    global DFiltACoef
    
    DFiltACoef = BReadFromClipboard()
    DifFiltALength.config(text = "Length = " + str(int(len(DFiltACoef)))) # change displayed length value
#
def BLoadDFiltBClip():
    global DFiltBCoef
    
    DFiltBCoef = BReadFromClipboard()
    DifFiltBLength.config(text = "Length = " + str(int(len(DFiltBCoef)))) # change displayed length value
#
## Read scope all time array data from saved file
def BReadData():
    global VBuffA, VBuffB, VBuffC, VBuffD, NoiseCH1, NoiseCH2, SHOWsamples

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")])
    try:
        CSVFile = open(filename)
        dialect = csv.Sniffer().sniff(CSVFile.read(2048))
        CSVFile.seek(0)
        csv_f = csv.reader(CSVFile, dialect)
        VBuffA = []
        VBuffB = []
        SHOWsamples = 0
        for row in csv_f:
            try:
                VBuffA.append(float(row[1]))
                VBuffB.append(float(row[2]))
                SHOWsamples = SHOWsamples + 1
            except:
                print( 'skipping non-numeric row')
        VBuffA = numpy.array(VBuffA)
        VBuffB = numpy.array(VBuffB)
        CSVFile.close()
        UpdateTimeTrace()
    except:
        showwarning("WARNING","No such file found or wrong format!")
## Open User Guide in Browser
# open a URL, in this case, the ALICE desk-top-users-guide
def BHelp():
    # need to cahnge this when new user guig is written!
    url = "https://wiki.analog.com/university/tools/m1k/alice/desk-top-users-guide"
    webbrowser.open(url,new=2)
## Show info on software / firmware / hardware
def BAbout():
    global RevDate, SWRev, FWRevOne, HWRevOne, DevID, Version_url
#Version_url = 'https://github.com/analogdevicesinc/alice/releases/download/1.3.8/alice-desktop-1.3-setup.exe'
    try:
        if sys.version_info[0] == 2:
            u = urllib2.urlopen(Version_url)
        if sys.version_info[0] == 3:
            u = urllib.request.urlopen(Version_url)
        meta = u.info()
        time_string = str(meta.getheaders("Last-Modified"))
    except:
        time_string = "Unavailable"
    showinfo("About ALICE", "ALICE Universal" + SWRev + RevDate + "\n" +
             "Last Released Version: " + time_string[7:18] + "\n" +
             "Software Rev " + str(FWRevOne) + "\n" +
             "Serial Number " + DevID + "\n" +
             "Software is provided as is without any Warranty")
#
## Take snap shot of displayed time waveforms
def BSnapShot():
    global T1Vline, T2Vline
    global Tmathline, TMRline, TXYRline
    global T1VRline, T2VRline, T3VRline, T4VRline, TMCVline, TMDVline
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V, ShowMath, MathTrace
    global TMAVline, TMBVline, TMCVline, TMDVline
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global ShowRMA, ShowRMB, ShowRMC, ShowRMD

    if ShowC1_V.get() == 1:
        T1VRline = T1Vline               # V reference Trace line channel A
    if ShowC2_V.get() == 1:
        T2VRline = T2Vline               # V reference Trace line channel B
    if ShowC3_V.get() == 1:
        T3VRline = T3Vline               # V reference Trace line channel A
    if ShowC4_V.get() == 1:
        T4VRline = T4Vline               # V reference Trace line channel B
    if MathTrace.get() > 0:
        TMRline = Tmathline              # Math reference Trace line
#
## Take snap shot of displayed XY Traces
def BSnapShotXY():
    global XYlineVA, XYlineVB, XYlineM, XYlineMX, XYlineMY
    global XYRlineVA, XYRlineVB, XYRlineM, XYRlineMX, XYRlineMY
    
    if len(XYlineVA) > 4:
        XYRlineVA = XYlineVA
    if len(XYlineVB) > 4:
        XYRlineVB = XYlineVB
    if len(XYlineM) > 4:
        XYRlineM = XYlineM
    if len(XYlineMX) > 4:
        XYRlineMX = XYlineMX
    if len(XYlineMY) > 4:
        XYRlineMY = XYlineMY
#
## Save gain, offset and filter variables for external dividers
def BSaveCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DevID
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry

    devidstr = DevID[17:31]
    filename = devidstr + "_O.cal"
    CalFile = open(filename, "w")
    #
    CalFile.write('CHAVGainEntry.delete(0,END)\n')
    CalFile.write('CHAVGainEntry.insert(4, ' + CHAVGainEntry.get() + ')\n')
    CalFile.write('CHBVGainEntry.delete(0,END)\n')
    CalFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
    CalFile.write('CHAVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAVOffsetEntry.insert(4, ' + CHAVOffsetEntry.get() + ')\n')
    CalFile.write('CHBVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')
    #
    # save channel AC frequency compensation settings
    try:
        CHA_TC1.set(float(cha_TC1Entry.get()))
        CHA_TC2.set(float(cha_TC2Entry.get()))
        CHB_TC1.set(float(chb_TC1Entry.get()))
        CHB_TC2.set(float(chb_TC2Entry.get()))
        CHA_A1.set(float(cha_A1Entry.get()))
        CHA_A2.set(float(cha_A2Entry.get()))
        CHB_A1.set(float(chb_A1Entry.get()))
        CHB_A2.set(float(chb_A2Entry.get()))
    except:
        donothing()   
    CalFile.write('CHA_RC_HP.set(' + str(CHA_RC_HP.get()) + ')\n')
    CalFile.write('CHB_RC_HP.set(' + str(CHB_RC_HP.get()) + ')\n')
    CalFile.write('CHA_TC1.set(' + str(CHA_TC1.get()) + ')\n')
    CalFile.write('CHA_TC2.set(' + str(CHA_TC2.get()) + ')\n')
    CalFile.write('CHB_TC1.set(' + str(CHB_TC1.get()) + ')\n')
    CalFile.write('CHB_TC2.set(' + str(CHB_TC2.get()) + ')\n')
    CalFile.write('CHA_A1.set(' + str(CHA_A1.get()) + ')\n')
    CalFile.write('CHA_A2.set(' + str(CHA_A2.get()) + ')\n')
    CalFile.write('CHB_A1.set(' + str(CHB_A1.get()) + ')\n')
    CalFile.write('CHB_A2.set(' + str(CHB_A2.get()) + ')\n')
    CalFile.write('cha_TC1Entry.delete(0,END)\n')
    CalFile.write('cha_TC1Entry.insert(4, ' + str(CHA_TC1.get()) + ')\n')
    CalFile.write('cha_TC2Entry.delete(0,END)\n')
    CalFile.write('cha_TC2Entry.insert(4, ' + str(CHA_TC2.get()) + ')\n')
    CalFile.write('chb_TC1Entry.delete(0,END)\n')
    CalFile.write('chb_TC1Entry.insert(4, ' + str(CHB_TC1.get()) + ')\n')
    CalFile.write('chb_TC2Entry.delete(0,END)\n')
    CalFile.write('chb_TC2Entry.insert(4, ' + str(CHB_TC2.get()) + ')\n')
    CalFile.write('cha_A1Entry.delete(0,END)\n')
    CalFile.write('cha_A1Entry.insert(4, ' + str(CHA_A1.get()) + ')\n')
    CalFile.write('cha_A2Entry.delete(0,END)\n')
    CalFile.write('cha_A2Entry.insert(4, ' + str(CHA_A2.get()) + ')\n')
    CalFile.write('chb_A1Entry.delete(0,END)\n')
    CalFile.write('chb_A1Entry.insert(4, ' + str(CHB_A1.get()) + ')\n')
    CalFile.write('chb_A2Entry.delete(0,END)\n')
    CalFile.write('chb_A2Entry.insert(4, ' + str(CHB_A2.get()) + ')\n')

    CalFile.close()
## Load gain, offset and filter variables for external dividers
def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DevID
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry

    devidstr = DevID[17:31]
    filename = devidstr + "_O.cal"
    try:
        CalFile = open(filename)
        for line in CalFile:
            exec( line.rstrip() )
        CalFile.close()
    except:
        print( "Cal file for this device not found")
## Ask user for channel A Measurement Label and Formula 
def BUserAMeas():
    global UserAString, UserALabel, MeasUserA

    TempString = UserALabel
    UserALabel = askstring("Measurement Label", "Current Label: " + UserALabel + "\n\nNew Label:\n", initialvalue=UserALabel)
    if (UserALabel == None):         # If Cancel pressed, then None
        MeasUserA.set(0)
        UserALabel = TempString
        return
    TempString = UserAString
    UserAString = askstring("Measurement Formula", "Current Formula: " + UserAString + "\n\nNew Formula:\n", initialvalue=UserAString)
    if (UserAString == None):         # If Cancel pressed, then None
        MeasUserA.set(0)
        UserAString = TempString
        return
    MeasUserA.set(1)
## Ask user for channel B Measurement Label and Formula
def BUserBMeas():
    global UserBString, UserBLabel, MeasUserB

    TempString = UserBLabel
    UserBLabel = askstring("Measurement Label", "Current Label: " + UserBLabel + "\n\nNew Label:\n", initialvalue=UserBLabel)
    if (UserBLabel == None):         # If Cancel pressed, then None
        MeasUserB.set(0)
        UserBLabel = TempString
        return
    TempString = UserBString
    UserBString = askstring("Measurement Formula", "Current Formula: " + UserBString + "\n\nNew Formula:\n", initialvalue=UserBString)
    if (UserBString == None):         # If Cancel pressed, then None
        MeasUserB.set(0)
        UserBString = TempString
        return
    MeasUserB.set(1)
#
## Ask user to enter custom plot label string
def BUserCustomPlotText():
    global LabelPlotText, PlotLabelText # = "Custom Plot Label"

    TempString = PlotLabelText
    PlotLabelText = askstring("Custom Label", "Current Plot Label: " + PlotLabelText + "\n\nNew Label:\n", initialvalue=PlotLabelText)
    if (PlotLabelText == None):         # If Cancel pressed, then None
        LabelPlotText.set(0)
        PlotLabelText = TempString
        return
    LabelPlotText.set(1)
## Make New Math waveform controls menu window
def NewEnterMathControls():
    global RUNstatus, MathScreenStatus, MathWindow, SWRev, RevDate
    global MathString, MathUnits, MathXString, MathXUnits, MathYString, MathYUnits
    global MathAxis, MathXAxis, MathYAxis, MathTrace
    global formentry, unitsentry, axisentry, xformentry, xunitsentry, xaxisentry, yformentry, yunitsentry, yaxisentry
    global formlab, xformlab, yformlab, FrameBG
    global Mframe1, Mframe2, Mframe3, Mframe4
    
    if MathScreenStatus.get() == 0:
        MathScreenStatus.set(1)
        #
        MathWindow = Toplevel()
        MathWindow.title("Math Formula " + SWRev + RevDate)
        MathWindow.resizable(FALSE,FALSE)
        MathWindow.protocol("WM_DELETE_WINDOW", DestroyMathScreen)
        MathWindow.configure(background=FrameBG)
        Mframe1 = LabelFrame(MathWindow, text="Built-in Exp", style="A10T5.TLabelframe") #"A10T5.TLabelframe")
        Mframe2 = LabelFrame(MathWindow, text="Math Trace", style="A10T5.TLabelframe")
        Mframe3 = LabelFrame(MathWindow, text="X Math Trace", style="A10T6.TLabelframe")
        Mframe4 = LabelFrame(MathWindow, text="Y Math Trace", style="A10T7.TLabelframe")
        # frame1.grid(row=0, column=0, sticky=W)
        #
        Mframe1.grid(row = 0, column=0, rowspan=3, sticky=W)
        Mframe2.grid(row = 0, column=1, sticky=W)
        Mframe3.grid(row = 1, column=1, sticky=W)
        Mframe4.grid(row = 2, column=1, sticky=W)
        #
        # Built in functions
        # 
        mrb1 = Radiobutton(Mframe1, text='none', variable=MathTrace, value=0, command=UpdateTimeTrace)
        mrb1.grid(row=0, column=0, sticky=W)
        mrb2 = Radiobutton(Mframe1, text='CAV+CBV', variable=MathTrace, value=1, command=UpdateTimeTrace)
        mrb2.grid(row=1, column=0, sticky=W)
        mrb3 = Radiobutton(Mframe1, text='CAV-CBV', variable=MathTrace, value=2, command=UpdateTimeTrace)
        mrb3.grid(row=2, column=0, sticky=W)
        mrb4 = Radiobutton(Mframe1, text='CBV-CAV', variable=MathTrace, value=3, command=UpdateTimeTrace)
        mrb4.grid(row=3, column=0, sticky=W)
        mrb5 = Radiobutton(Mframe1, text='CAV+CCV', variable=MathTrace, value=4, command=UpdateTimeTrace)
        mrb5.grid(row=4, column=0, sticky=W)
        mrb6 = Radiobutton(Mframe1, text='CAV-CCV', variable=MathTrace, value=5, command=UpdateTimeTrace)
        mrb6.grid(row=5, column=0, sticky=W)
        mrb7 = Radiobutton(Mframe1, text='CCV-CAV', variable=MathTrace, value=6, command=UpdateTimeTrace)
        mrb7.grid(row=6, column=0, sticky=W)
        mrb8 = Radiobutton(Mframe1, text='CBV+CCV', variable=MathTrace, value=7, command=UpdateTimeTrace)
        mrb8.grid(row=7, column=0, sticky=W)
        mrb9 = Radiobutton(Mframe1, text='CBV-CCV', variable=MathTrace, value=8, command=UpdateTimeTrace)
        mrb9.grid(row=8, column=0, sticky=W)
        mrb10 = Radiobutton(Mframe1, text='CCV-CBV', variable=MathTrace, value=9, command=UpdateTimeTrace)
        mrb10.grid(row=9, column=0, sticky=W)
        mrb11 = Radiobutton(Mframe1, text='CBV/CAV', variable=MathTrace, value=10, command=UpdateTimeTrace)
        mrb11.grid(row=10, column=0, sticky=W)
        mrb13 = Radiobutton(Mframe1, text='Formula', variable=MathTrace, value=12, command=UpdateTimeTrace)
        mrb13.grid(row=12, column=0, sticky=W)
        # 
        # Math trace formula sub Mframe2
        #
        sframe2a = Frame( Mframe2 )
        sframe2a.pack(side=TOP)
        formlab = Label(sframe2a, text="  Formula ", style= "A10B.TLabel")
        formlab.pack(side=LEFT)
        formentry = Entry(sframe2a, width=23)
        formentry.pack(side=LEFT)
        formentry.delete(0,"end")
        formentry.insert(0,MathString)
        sframe2b = Frame( Mframe2 )
        sframe2b.pack(side=TOP)
        unitslab = Label(sframe2b, text="Units ", style= "A10B.TLabel")
        unitslab.pack(side=LEFT)
        unitsentry = Entry(sframe2b, width=6)
        unitsentry.pack(side=LEFT)
        unitsentry.delete(0,"end")
        unitsentry.insert(0,MathUnits)
        checkbt = Button(sframe2b, text="Check", command=CheckMathString )
        checkbt.pack(side=LEFT)
        sframe2c = Frame( Mframe2 )
        sframe2c.pack(side=TOP)
        axislab = Label(sframe2c, text="Axis ", style= "A10B.TLabel")
        axislab.pack(side=LEFT)
        axisentry = Entry(sframe2c, width=4)
        axisentry.pack(side=LEFT)
        axisentry.delete(0,"end")
        axisentry.insert(0,MathAxis)
        applybt = Button(sframe2c, text="Apply", command=ApplyMathString )
        applybt.pack(side=LEFT)
        # 
        # X Math trace formula sub Mframe3
        #
        sframe3a = Frame( Mframe3 )
        sframe3a.pack(side=TOP)
        xformlab = Label(sframe3a, text="X Formula ", style= "A10B.TLabel")
        xformlab.pack(side=LEFT)
        xformentry = Entry(sframe3a, width=23)
        xformentry.pack(side=LEFT)
        xformentry.delete(0,"end")
        xformentry.insert(0, MathXString)
        sframe3b = Frame( Mframe3 )
        sframe3b.pack(side=TOP)
        xunitslab = Label(sframe3b, text="X Units ", style= "A10B.TLabel")
        xunitslab.pack(side=LEFT)
        xunitsentry = Entry(sframe3b, width=6)
        xunitsentry.pack(side=LEFT)
        xunitsentry.delete(0,"end")
        xunitsentry.insert(0, MathXUnits)
        xcheckbt = Button(sframe3b, text="Check", command=CheckMathXString )
        xcheckbt.pack(side=LEFT)
        sframe3c = Frame( Mframe3 )
        sframe3c.pack(side=TOP)
        xaxislab = Label(sframe3c, text="X Axis ", style= "A10B.TLabel")
        xaxislab.pack(side=LEFT)
        xaxisentry = Entry(sframe3c, width=4)
        xaxisentry.pack(side=LEFT)
        xaxisentry.delete(0,"end")
        xaxisentry.insert(0, MathXAxis)
        xapplybt = Button(sframe3c, text="Apply", command=ApplyMathXString )
        xapplybt.pack(side=LEFT)
        # 
        # Math trace formula sub Mframe4
        #
        sframe4a = Frame( Mframe4 )
        sframe4a.pack(side=TOP)
        yformlab = Label(sframe4a, text="Y Formula ", style= "A10B.TLabel")
        yformlab.pack(side=LEFT)
        yformentry = Entry(sframe4a, width=23)
        yformentry.pack(side=LEFT)
        yformentry.delete(0,"end")
        yformentry.insert(0,MathYString)
        sframe4b = Frame( Mframe4 )
        sframe4b.pack(side=TOP)
        yunitslab = Label(sframe4b, text="Y Units ", style= "A10B.TLabel")
        yunitslab.pack(side=LEFT)
        yunitsentry = Entry(sframe4b, width=6)
        yunitsentry.pack(side=LEFT)
        yunitsentry.delete(0,"end")
        yunitsentry.insert(0,MathYUnits)
        ycheckbt = Button(sframe4b, text="Check", command=CheckMathYString )
        ycheckbt.pack(side=LEFT)
        sframe4c = Frame( Mframe4 )
        sframe4c.pack(side=TOP)
        yaxislab = Label(sframe4c, text="Y Axis ", style= "A10B.TLabel")
        yaxislab.pack(side=LEFT)
        yaxisentry = Entry(sframe4c, width=4)
        yaxisentry.pack(side=LEFT)
        yaxisentry.delete(0,"end")
        yaxisentry.insert(0,MathYAxis)
        yapplybt = Button(sframe4c, text="Apply", command=ApplyMathYString )
        yapplybt.pack(side=LEFT)

        dismissbutton = Button(MathWindow, text="Dismiss", command=DestroyMathScreen)
        dismissbutton.grid(row=3, column=0, sticky=W)
        
    if RUNstatus.get() > 0:
        UpdateTimeTrace()
## Destroy New Math waveform controls menu window
def DestroyMathScreen():
    global MathScreenStatus, MathWindow
    
    if MathScreenStatus.get() == 1:
        MathScreenStatus.set(0)
        MathWindow.destroy()
## Check Math String for syntac errors
def CheckMathString():
    global MathString, formentry, MathUnits, unitsentry, MathAxis, axisentry, formlab
    global VBuffA, VBuffB, NoiseCH1, NoiseCH2
    global VmemoryA, VmemoryB
    global VUnAvgA, VUnAvgB, UnAvgSav
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global AWGAwaveform, AWGBwaveform
    global Show_MathX, Show_MathY
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2

    t = 0
    TempString = formentry.get()
    try:
        MathResult = eval(TempString)
        formlab.configure(text="Formula ", style= "A10G.TLabel")
    except:
        formlab.configure(text="Formula ", style= "A10R.TLabel")
## Check X Math String for syntac errors
def CheckMathXString():
    global MathXString, xformentry, MathXUnits, xunitsentry, MathXAxis, xaxisentry, xformlab
    global VBuffA, VBuffB, VBuffC, VBuffD, NoiseCH1, NoiseCH2
    global VmemoryA, VmemoryB, VmemoryC, VmemoryD
    global VUnAvgA, VUnAvgB, UnAvgSav
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global AWGAwaveform, AWGBwaveform
    global Show_MathX, Show_MathY
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCV3, DCV4, MinV3, MaxV3, MinV4, MaxV4

    t = 0
    TempString = xformentry.get()
    # print(TempString)
    MathResult = eval(TempString)
    try:
        MathResult = eval(TempString)
        xformlab.configure(text="X Formula ", style= "A10G.TLabel")
    except:
        xformlab.configure(text="X Formula ", style= "A10R.TLabel")
## Check Y Math String for syntac errors
def CheckMathYString():
    global MathYString, yformentry, MathYUnits, yunitsentry, MathYAxis, yaxisentry, yformlab
    global VBuffA, VBuffB, VBuffC, VBuffD, NoiseCH1, NoiseCH2
    global VmemoryA, VmemoryB, VmemoryC, VmemoryD
    global VUnAvgA, VUnAvgB, UnAvgSav
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global AWGAwaveform, AWGBwaveform
    global Show_MathX, Show_MathY
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCV3, DCV4, MinV3, MaxV3, MinV4, MaxV4

    t = 0
    TempString = yformentry.get()
    try:
        MathResult = eval(TempString)
        yformlab.configure(text="Y Formula ", style= "A10G.TLabel")
    except:
        yformlab.configure(text="Y Formula ", style= "A10R.TLabel")
## Apply Math string from entry widget
def ApplyMathString():
    global MathString, formentry, MathUnits, unitsentry, MathAxis, axisentry

    MathString = formentry.get()
    MathUnits = unitsentry.get()
    MathAxis = axisentry.get()
## Apply X Math string from entry widget
def ApplyMathXString():
    global MathXString, xformentry, MathXUnits, xunitsentry, MathXAxis, xaxisentry

    MathXString = xformentry.get()
    MathXUnits = xunitsentry.get()
    MathXAxis = xaxisentry.get()
## Apply Y Math string from entry widget
def ApplyMathYString():
    global MathYString, yformentry, MathYUnits, yunitsentry, MathYAxis, yaxisentry

    MathYString = yformentry.get()
    MathYUnits = yunitsentry.get()
    MathYAxis = yaxisentry.get()
## Ask user for new Marker text location on screen
def BSetMarkerLocation():
    global MarkerLoc, RUNstatus

    TempString = MarkerLoc
    MarkerLoc = askstring("Marker Text Location", "Current Marker Text Location: " + MarkerLoc + "\n\nNew Location: (UL, UR, LL, LR)\n", initialvalue=MarkerLoc)
    if (MarkerLoc == None):         # If Cancel pressed, then None
        MarkerLoc = TempString
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
## Nop
def donothing():
    global RUNstatus
## Another Nop
def DoNothing(event):
    global RUNstatus
## Set to display all time waveforms
def BShowCurvesAll():
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC3_V, RUNstatus, CHANNELS
    
    if CHANNELS >= 1:
        ShowC1_V.set(1)
    if CHANNELS >= 2:
        ShowC2_V.set(1)
    if CHANNELS >= 3:
        ShowC3_V.set(1)
    if CHANNELS >= 4:
        ShowC4_V.set(1)
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
## Turn off display of all time waveforms
def BShowCurvesNone():
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC3_V, RUNstatus, CHANNELS
    
    if CHANNELS >= 1:
        ShowC1_V.set(0)
    if CHANNELS >= 2:
        ShowC2_V.set(0)
    if CHANNELS >= 3:
        ShowC3_V.set(0)
    if CHANNELS >= 4:
        ShowC4_V.set(0)
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
#
## Set Trigger level to 50% (mid) point of current waveform
def BTrigger50p():
    global TgInput, TRIGGERlevel, TRIGGERentry, RUNstatus
    global MaxV1, MinV1, MaxV2, MinV2, MaxV3, MinV3, MaxV4, MinV4
    
    # set new trigger level to mid point of waveform    
    MidV1 = (MaxV1+MinV1)/2
    MidV2 = (MaxV2+MinV2)/2
    MidV3 = (MaxV3+MinV3)/2
    MidV4 = (MaxV4+MinV4)/2
    DCString = "0.0"
    try:
        if (TgInput.get() == 0):
            DCString = "0.0"
        elif (TgInput.get() == 1 ):
            DCString = ' {0:.2f} '.format(MidV1)
        elif (TgInput.get() == 2 ):
            DCString = ' {0:.2f} '.format(MidV2)
        elif (TgInput.get() == 3 ):
            DCString = ' {0:.2f} '.format(MidV3)
        elif (TgInput.get() == 4 ):
            DCString = ' {0:.2f} '.format(MidV4)
        else:
            DCString = ' {0:.2f} '.format(0.5)
    except:
        pass
#
    TRIGGERlevel = eval(DCString)
    TRIGGERentry.delete(0,END)
    TRIGGERentry.insert(4, DCString)
    BTriglevel()
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
        
## place holder for hardware triggering if implemented
## evalute trigger level entry string to a numerical value and set new trigger level     
def BTriglevel():
    global TRIGGERlevel, TRIGGERentry, RUNstatus
    global InGainA, InGainB, InOffA, InOffB
    global TgInput, TrigSource

    ## evalute entry string to a numerical value
    TRIGGERlevel = float(TRIGGERentry.get())
#
    if TgInput.get() == 1:
        # adjust for divider if any Channel A
        TRIGGERlevel = (TRIGGERlevel / InGainA) + (InOffA / InGainA)
    if TgInput.get() == 2:
        # adjust for divider if any Channel B
        TRIGGERlevel = (TRIGGERlevel / InGainB) + (InOffB / InGainB)
    if TgInput.get() == 3:
        # adjust for divider if any Channel C
        TRIGGERlevel = (TRIGGERlevel / InGainC) + (InOffC / InGainC)
    if TgInput.get() == 4:
        # adjust for divider if any Channel D
        TRIGGERlevel = (TRIGGERlevel / InGainD) + (InOffD / InGainD)
    if TgInput.get() >= 5:
        # adjust for divider if any Channel D
        TRIGGERlevel = 0.5
#
    SendTriggerLevel()
#
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb, TimeDiv

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    HozOffset = int(TimeDiv/HorzValue)
    # prevent divide by zero error
    
def SetVAPoss():
    global CHAVPosEntry, DCV1
    
    CHAVPosEntry.delete(0,"end")
    CHAVPosEntry.insert(0, ' {0:.2f} '.format(DCV1))
#
def SetVBPoss():
    global CHBVPosEntry, DCV2
    
    CHBVPosEntry.delete(0,"end")
    CHBVPosEntry.insert(0, ' {0:.2f} '.format(DCV2))
#
def SetVCPoss():
    global CHCVPosEntry, DCV3
    
    CHCVPosEntry.delete(0,"end")
    CHCVPosEntry.insert(0, ' {0:.2f} '.format(DCV3))
#
def SetVDPoss():
    global CHDVPosEntry, DCV4
    
    CHDVPosEntry.delete(0,"end")
    CHDVPosEntry.insert(0, ' {0:.2f} '.format(DCV4))
#
def SetXYVAPoss():
    global CHAVPosEntryxy, DCV1
    
    CHAVPosEntryxy.delete(0,"end")
    CHAVPosEntryxy.insert(0, ' {0:.2f} '.format(DCV1))
#
def SetXYVBPoss():
    global CHBVPosEntryxy, DCV2
    
    CHBVPosEntryxy.delete(0,"end")
    CHBVPosEntryxy.insert(0, ' {0:.2f} '.format(DCV2))
#
def SetXYVCPoss():
    global CHCVPosEntryxy, DCV3
    
    CHCVPosEntryxy.delete(0,"end")
    CHCVPosEntryxy.insert(0, ' {0:.2f} '.format(DCV3))
#
def SetXYVDPoss():
    global CHDVPosEntryxy, DCV4
    
    CHDVPosEntryxy.delete(0,"end")
    CHDVPosEntryxy.insert(0, ' {0:.2f} '.format(DCV4))
#    
def BHozPoss(event):
    global HozPoss, HozPossentry, RUNstatus

    # get time scale
    HorzValue = UnitConvert(HozPossentry.get())
    # HozOffset = int(TimeDiv/HorzValue)
    SetHorzPoss()
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update#
#
## Start aquaring scope time data
def BStart():
    global RUNstatus, devx, PwrBt, DevID, FWRevOne, session, AWGSync
    global contloop, discontloop, TimeDiv, First_Slow_sweep, OhmDisp, DMMDisp
    global TimeDisp, XYDisp, PhADisp, FreqDisp, BodeDisp, IADisp
    global Dlog_open, dlog, Ztime

    # Check if User wants data loging on or off
    if Dlog_open.get() == 1 and dlog.get() > 0:
        Ztime = time.time()
    elif Dlog_open.get() == 0 and dlog.get() > 0:
        DlogerOpen_out()
        Ztime = time.time()
    else:
        Dlog_open.set(0)
    #
    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    elif TimeDisp.get() == 0 and XYDisp.get() == 0 and PhADisp.get() == 0 and FreqDisp.get() == 0 and BodeDisp.get() == 0 and IADisp.get() == 0 and OhmDisp.get() == 0 and DMMDisp.get() == 0:
        showwarning("WARNING","Enable at least one Instrument!")
    else:
        temp = 0
        #
        if (RUNstatus.get() == 0):
            RUNstatus.set(1)
        #
                    
    # UpdateTimeScreen()          # Always Update
# Start running Ohmmeter tool

## Start Impedance Tool               
def BStartIA():
    global AWGAFreqEntry, AWGAFreqvalue, FWRevOne, NetworkScreenStatus, BodeDisp

    IASourceSet()
    if NetworkScreenStatus.get() > 0 and BodeDisp.get() > 0:
        BStartBP()
    else:
        BStart()
    
## Set up IA AWG sources
def IASourceSet():
    global  IASource

    if IASource.get() == 0:
        donothing()
    else:
        AWGAShape.set(1) # Set Sine
        MakeAWGwaves()

## Stop (pause) scope tool
def BStop():
    global RUNstatus, TimeDisp, XYDisp, FreqDisp, IADisp, session, AWGSync
    global CHA, CHB, contloop, discontloop
    
    if (RUNstatus.get() == 1):
        try:
            HardwareStop()
        except:
            pass
        # print("Stoping")
        RUNstatus.set(0)
#
    if TimeDisp.get() > 0:
        UpdateTimeScreen()          # Always Update screens as necessary
    if XYDisp.get() > 0:
        UpdateXYScreen()
    if FreqDisp.get() > 0:
        UpdateFreqScreen()
    if IADisp.get() > 0:
        UpdateIAScreen()

## Toggel on/off Roll Sweep Mode
def BRoll():
    global Roll_Mode, RollBt

    if Roll_Mode.get() == 1:
        Roll_Mode.set(0)
        RollBt.config(style="RollOff.TButton",text="Roll-Off")
    else:
        Roll_Mode.set(1)
        RollBt.config(style="Roll.TButton",text="Roll-On")

## Set Hor time scale from entry widget
def BTime():
    global TimeDiv, TMsb, RUNstatus, SHOWsamples, Power2, MaxSampleRate
    global ShowC1_V, ShowC2_V, TimeSpan, SAMPLErate, SHOWsamples
    
    TimeDiv = UnitConvert(TMsb.get())
    SetSampleRate()
    #
    if RUNstatus.get() == 0:      # if not running
        UpdateTimeTrace()           # Update
    
def BCHAlevel():
    global CHAsb, RUNstatus, CH1vpdvLevel
    
    CH1vpdvLevel = UnitConvert(CHAsb.get())
    try:
        HCHAlevel()
    except:
        donothing()
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update

def BCHBlevel():
    global CHBsb, RUNstatus, CH2vpdvLevel
    
    CH2vpdvLevel = UnitConvert(CHBsb.get())
    try:
        HCHBlevel()
    except:
        donothing()
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update   
#
def BCHClevel():
    global CHCsb, RUNstatus, CHCvpdvLevel
    
    CHCvpdvLevel = UnitConvert(CHCsb.get())
    try:
        HCHClevel()
    except:
        donothing()
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update

def BCHDlevel():
    global CHDsb, RUNstatus, CHDvpdvLevel
    
    CHDvpdvLevel = UnitConvert(CHDsb.get())
    try:
        HCHDlevel()
    except:
        donothing()
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update
#
def BOffsetA(event):
    global CHAOffset, CHAVPosEntry, CH1vpdvLevel, RUNstatus

    try:
        CHAOffset = float(eval(CHAVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    NumberOfDiv = int(CHAOffset/CH1vpdvLevel)
    try:
        HOffsetA()
    except:
        donothing()
    # set new offset level
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update

def BOffsetB(event):
    global CHBOffset, CHBVPosEntry, CH2vpdvLevel, RUNstatus

    try:
        CHBOffset = float(eval(CHBVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    NumberOfDiv = int(CHBOffset/CH2vpdvLevel)
    try:
        HOffsetB()
    except:
        donothing()
    # set new offset level
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update
#
def BOffsetC(event):
    global CHCOffset, CHCVPosEntry, CHCvpdvLevel, RUNstatus

    try:
        CHCOffset = float(eval(CHCVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHCVPosEntry.delete(0,END)
        CHCVPosEntry.insert(0, CHCOffset)
    NumberOfDiv = int(CHCOffset/CHCvpdvLevel)
    # set new offset level
    try:
        HOffsetC()
    except:
        donothing()
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update

def BOffsetD(event):
    global CHDOffset, CHDVPosEntry, CHDvpdvLevel, RUNstatus

    try:
        CHDOffset = float(eval(CHDVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHDVPosEntry.delete(0,END)
        CHDVPosEntry.insert(0, CHDOffset)
    NumberOfDiv = int(CHDOffset/CHDvpdvLevel)
    # set new offset level
    try:
        HOffsetD()
    except:
        donothing()
    if RUNstatus.get() == 0:
        UpdateTimeTrace()           # if not running Update
#
# set check box colors
def TimeCheckBox():
    global TimeDisp, ckb1
    if TimeDisp.get() == 1:
        ckb1.config(style="Enab.TCheckbutton")
    else:
        ckb1.config(style="Disab.TCheckbutton")
#
def XYCheckBox():
    global XYDisp, ckb2
    if XYDisp.get() == 1:
        ckb2.config(style="Enab.TCheckbutton")
    else:
        ckb2.config(style="Disab.TCheckbutton")
#
def FreqCheckBox():
    global FreqDisp, ckb3, OOTckb3, OOTScreenStatus
    if FreqDisp.get() == 1:
        if OOTScreenStatus.get() == 0:
            ckb3.config(style="Enab.TCheckbutton")
        else:
            OOTckb3.config(style="Enab.TCheckbutton")
    else:
        if OOTScreenStatus.get() == 0:
            ckb3.config(style="Disab.TCheckbutton")
        else:
            OOTckb3.config(style="Disab.TCheckbutton")
#
def BodeCheckBox():
    global BodeDisp, ckb5, OOTckb5, OOTScreenStatus
    if BodeDisp.get() == 1:
        if OOTScreenStatus.get() == 0:
            ckb5.config(style="Enab.TCheckbutton")
        else:
            OOTckb5.config(style="Enab.TCheckbutton")
    else:
        if OOTScreenStatus.get() == 0:
            ckb5.config(style="Disab.TCheckbutton")
        else:
            OOTckb5.config(style="Disab.TCheckbutton")
#
def IACheckBox():
    global IADisp, ckb4, OOTckb4, OOTScreenStatus
    if IADisp.get() == 1:
        if OOTScreenStatus.get() == 0:
            ckb4.config(style="Enab.TCheckbutton")
        else:
            OOTckb4.config(style="Enab.TCheckbutton")
    else:
        if OOTScreenStatus.get() == 0:
            ckb4.config(style="Disab.TCheckbutton")
        else:
            OOTckb4.config(style="Disab.TCheckbutton")
#
def PhACheckBox():
    global PhADisp, Phckb, OOTphckb, OOTScreenStatus 
    if PhADisp.get() == 1:
        if OOTScreenStatus.get() == 0:
            phckb.config(style="Enab.TCheckbutton")
        else:
            OOTphckb.config(style="Enab.TCheckbutton")
    else:
        if OOTScreenStatus.get() == 0:
            phckb.config(style="Disab.TCheckbutton")
        else:
            OOTphckb.config(style="Disab.TCheckbutton")
#
def OhmCheckBox():
    global OhmDisp, ckb6, OOTckb6, OOTScreenStatus 
    if OhmDisp.get() == 1:
        if OOTScreenStatus.get() == 0:
            ckb6.config(style="Enab.TCheckbutton")
        else:
            OOTckb6.config(style="Enab.TCheckbutton")
    else:
        if OOTScreenStatus.get() == 0:
            ckb6.config(style="Disab.TCheckbutton")
        else:
            OOTckb6.config(style="Disab.TCheckbutton")
#
def DMMCheckBox():
    global DMMDisp, ckb7, OOTckb7, OOTScreenStatus 
    if DMMDisp.get() == 1:
        if OOTScreenStatus.get() == 0:
            ckb7.config(style="Enab.TCheckbutton")
        else:
            OOTckb7.config(style="Enab.TCheckbutton")
    else:
        if OOTScreenStatus.get() == 0:
            ckb7.config(style="Disab.TCheckbutton")
        else:
            OOTckb7.config(style="Disab.TCheckbutton")
#
def LbCheckBox():
    global LoopBack, lbckb

    if LoopBack.get() > 0:
        lbckb.config(style="Enab.TCheckbutton")
    else:
        lbckb.config(style="Disab.TCheckbutton")
#
# ========================= Main routine ====================================
## Main Loop
#
def Analog_In():
    global RUNstatus, OhmRunStatus, OhmDisp, DMMRunStatus, DMMDisp
    global SingleShot, ManualTrigger, TimeDisp, XYDisp, FreqDisp, SpectrumScreenStatus, HWRevOne
    global PhADisp, IADisp, IAScreenStatus, CutDC, DevOne, BodeScreenStatus, BodeDisp
    global MuxScreenStatus, VBuffA, VBuffB, NoiseCH1, NoiseCH2
    global CHANNELS, ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global InGainA, InGainB, InOffA, InOffB, InGainC, InGainD, InOffC, InOffD
    global CHAVGainEntry, CHAVOffsetEntry, CHBVGainEntry, CHBVOffsetEntry
    global CHCVGainEntry, CHCVOffsetEntry, CHDVGainEntry, CHDVOffsetEntry
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global SV1, SV2, SVA_B, Closed, SingleShot, ManualTrigger
    global FregPoint, FStep, TRACEaverage
    # Analog Mux channel measurement variables
    global TRACEresetTime, TRACEmodeTime, TgInput, SettingsStatus, TRIGGERsample
    
    while (Closed == 0):       # Main loop
        # Do input probe Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
        if CHANNELS >= 1:
            try:
                InOffA = float(eval(CHAVOffsetEntry.get()))
            except:
                CHAVOffsetEntry.delete(0,END)
                CHAVOffsetEntry.insert(0, InOffA)
            try:
                InGainA = float(eval(CHAVGainEntry.get()))
            except:
                CHAVGainEntry.delete(0,END)
                CHAVGainEntry.insert(0, InGainA)
        if CHANNELS >= 2:
            try:
                InGainB = float(eval(CHBVGainEntry.get()))
            except:
                CHBVGainEntry.delete(0,END)
                CHBVGainEntry.insert(0, InGainB)
            try:
                InOffB = float(eval(CHBVOffsetEntry.get()))
            except:
                CHBVOffsetEntry.delete(0,END)
                CHBVOffsetEntry.insert(0, InOffB)
        if CHANNELS >= 3:
            try:
                InGainC = float(eval(CHCVGainEntry.get()))
            except:
                CHCVGainEntry.delete(0,END)
                CHCVGainEntry.insert(0, InGainC)
            try:
                InOffC = float(eval(CHCVOffsetEntry.get()))
            except:
                CHCVOffsetEntry.delete(0,END)
                CHCVOffsetEntry.insert(0, InOffC)
        if CHANNELS >= 4:
            try:
                InGainD = float(eval(CHDVGainEntry.get()))
            except:
                CHDVGainEntry.delete(0,END)
                CHDVGainEntry.insert(0, InGainD)
            try:
                InOffD = float(eval(CHDVOffsetEntry.get()))
            except:
                CHDVOffsetEntry.delete(0,END)
                CHDVOffsetEntry.insert(0, InOffD)
        # RUNstatus = 1 : Open Acquisition
        if (RUNstatus.get() == 1) or (RUNstatus.get() == 2):
            if SettingsStatus.get() == 1:
                SettingsUpdate() # Make sure current entries in Settings controls are up to date
            # if TimeDisp.get() > 0 or XYDisp.get() > 0 or PhADisp.get() > 0:
            Analog_Time_In()
            if TimeDisp.get() > 0: #
                UpdateTimeAll() # Update Data, trace and time screen
                if SingleShot.get() > 0 and Is_Triggered == 1: # Singel Shot trigger is on
                    BStop() # 
                    SingleShot.set(0)
                if ManualTrigger.get() == 1: # Manual trigger is on
                    BStop() # 
            if XYDisp.get() > 0 and XYScreenStatus.get() > 0:
                UpdateXYAll() # Update Data, trace and XY screen
                if SingleShot.get() > 0 and Is_Triggered == 1: # Singel Shot trigger is on
                    BStop() # 
                    SingleShot.set(0)
                if ManualTrigger.get() == 1: # Manual trigger is on
                    BStop() # 
            if MeasureStatus.get() > 0:
                UpdateMeasureScreen()
            if (FreqDisp.get() > 0 and SpectrumScreenStatus.get() == 1) or (IADisp.get() > 0 and IAScreenStatus.get() == 1) or (BodeDisp.get() > 0 and BodeScreenStatus.get() == 1):
                if IADisp.get() > 0 or BodeDisp.get() > 0:
                    CutDC.set(1) # remove DC portion of waveform  
                Analog_Freq_In()
            if OhmRunStatus.get() == 1 and OhmDisp.get() == 1:
                Ohm_Analog_In()
            if DMMRunStatus.get() == 1 and DMMDisp.get() == 1:
                DMM_Analog_In()
        else:
            time.sleep(0.01) # slow down loop while not running to reduce CPU usage
        root.update_idletasks()
        root.update()
##
def DMM_Analog_In():
    global VBuffA, VBuffB, VBuffC, VBuffD, MBuff, MBuffX, MBuffY
    global DmmLabel1, DmmLabel2, DmmLabel3, DmmLabel4
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V, CHANNELS
    global MathTrace, Show_MathX, Show_MathY, YsignalMX, YsignalMY
    global Ztime, dlog
    #
    DCVA0 = DCVB0 = DCVC0 = DCVD0 = DCMath = DCMathX = DCMathY = 0.0 # initalize measurment variable
    RIN = 1000000 # nominal
    # Get_Data()
    #
    DmmLabel1.config(text = " " ) # Reset display
    DmmLabel2.config(text = " " ) # Reset display
    DmmLabel3.config(text = " " ) # Reset display
    DmmLabel4.config(text = " " ) # Reset display
    VString1 = "A = "
    VString2 = "C = "
    VString3 = "Math = "
    VString4 = "MathX = "
    if ShowC1_V.get() > 0 and CHANNELS >= 1:
        DCVA0 = numpy.mean(VBuffA) # calculate average
        VString1 = VString1 + ' {0:.4f} '.format(DCVA0) # format with 4 decimal places
        DmmLabel1.config(text = VString1) # change displayed values
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        DCVB0 = numpy.mean(VBuffB) # calculate average
        VString1 = VString1 + " B = " + ' {0:.4f} '.format(DCVB0) # format with 4 decimal places
        DmmLabel1.config(text = VString1) # change displayed values
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        DCVC0 = numpy.mean(VBuffC) # calculate average
        VString2 = VString2 + ' {0:.4f} '.format(DCVC0) # format with 4 decimal places
        DmmLabel2.config(text = VString2) # change displayed values
    if ShowC4_V.get() > 0 and CHANNELS >= 4:
        DCVD0 = numpy.mean(VBuffD) # calculate average
        VString2 = VString2 + " D = " + ' {0:.4f} '.format(DCVD0) # format with 4 decimal places
        DmmLabel2.config(text = VString2) # change displayed values
    if MathTrace.get() > 0:
        DCMath = numpy.mean(MBuff) # calculate average
        VString3 = VString3 + ' {0:.4f} '.format(DCMath) # format with 4 decimal places
        DmmLabel3.config(text = VString3) # change displayed values
    if Show_MathX.get() > 0 or YsignalMX.get() == 1:
        DCMathX = numpy.mean(MBuffX) # calculate average
        VString4 = VString4 + ' {0:.4f} '.format(DCMathX) # format with 4 decimal places
        DmmLabel4.config(text = VString4) # change displayed values
    if Show_MathY.get() > 0 or YsignalMY.get() == 1:
        DCMathY = numpy.mean(MBuffY) # calculate average
        VString4 = VString4 + " MathY = " + ' {0:.4f} '.format(DCMathY) # format with 4 decimal places
        DmmLabel4.config(text = VString4) # change displayed values
    # print VString
    Update_Analog_Meter(DCVA0, DCVB0, DCVC0, DCVD0, DCMath, DCMathX, DCMathY)
    if dlog.get() > 0: # Check to see if Data Logging is On
        tstr1 = time.time()-Ztime
        DlogString = '{0:.3f}, '.format(tstr1)
        if ShowC1_V.get() > 0 and CHANNELS >= 1:
            DlogString = DlogString + ' {0:.4f} '.format(DCVA0) # format with 4 decimal
        if ShowC2_V.get() > 0 and CHANNELS >= 2:
            DlogString = DlogString + ' {0:.4f} '.format(DCVB0) # format with 4
        if ShowC3_V.get() > 0 and CHANNELS >= 3:
            DlogString = DlogString + ' {0:.4f} '.format(DCVC0) # format with 4 decimal
        if ShowC4_V.get() > 0 and CHANNELS >= 4:
            DlogString = DlogString + ' {0:.4f} '.format(DCVD0) # format with 4
        if MathTrace.get() > 0:
            DlogString = DlogString + ' {0:.4f} '.format(DCMath) # format with 4
        if Show_MathX.get() > 0 or YsignalMX.get() == 1:
            DlogString = DlogString + ' {0:.4f} '.format(DCMathX) # format with 4
        if Show_MathY.get() > 0 or YsignalMY.get() == 1:
            DlogString = DlogString + ' {0:.4f} '.format(DCMathY) # format with 4
        DlogString = DlogString + " \n"
        DlogFile.write( DlogString )
#
# Toggle Dlogger flag
def Dloger_on_off(): 
    global DlogFile, Dlog_open, dlog

    if dlog.get() == 1:
        DlogerOpen_out()
        #print("Opening Dlog file")
    else:
        DlogerClose_out()
        #print("Closing Dlog file")
#
# Close file for data logging
def DlogerClose_out():
    global DlogFile, Dlog_open, dlog

    if Dlog_open.get() == 1:
        try:
            DlogFile.close()
            #print("Closing Dlog file")
        except:
            Dlog_open.set(0)
    else:
        Dlog_open.set(0)
#
# Open file for data logging
def DlogerOpen_out():
    global DlogFile, Dlog_open, dlog
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V, CHANNELS
    global MathTrace, Show_MathX, Show_MathY, YsignalMX, YsignalMY
    
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
    filename = "DataLogger-" + tme
    filename = filename + ".csv"
    try:
        DlogFile = open(filename, 'a')
    except:
        filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
        DlogFile = open(filename, 'a')
    #
    DlogString = 'Time, '
    if ShowC1_V.get() > 0 and CHANNELS >= 1:
        DlogString = DlogString + 'CH-A V, ' 
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        DlogString = DlogString + 'CH-B V, ' 
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        DlogString = DlogString + 'CH-C V, '
    if ShowC4_V.get() > 0 and CHANNELS >= 4:
        DlogString = DlogString + 'CH-D V, '
    if MathTrace.get() > 0:
        DlogString = DlogString + 'Math, '
    if Show_MathX.get() > 0 or YsignalMX.get() == 1:
        DlogString = DlogString + 'MathX, '
    if Show_MathY.get() > 0 or YsignalMY.get() == 1:
        DlogString = DlogString + 'MathY '
    DlogString = DlogString + " \n"
    DlogFile.write( DlogString )
    Dlog_open.set(1)
#    
## Ohmmeter loop
def Ohm_Analog_In():
    global RMode, CHATestVEntry, CHATestREntry, CHA, CHB, OhmA0, OhmA1
    global Rint, AWGAShape, CHBIntREntry, VBuffA, VBuffB, CHANNELS

    if CHANNELS < 2:
        return
    try:
        chatestv = float(eval(CHATestVEntry.get()))
        if chatestv > 4.0:
            chatestv = 4.0
            CHATestVEntry.delete(0,END)
            CHATestVEntry.insert(0, chatestv)
    except:
        CHATestVEntry.delete(0,END)
        CHATestVEntry.insert(0, chatestv)
    try:
        chatestr = float(eval(CHATestREntry.get()))
    except:
        CHATestREntry.delete(0,END)
        CHATestREntry.insert(0, chatestr)
    try:
        Rint = float(eval(CHBIntREntry.get()))
    except:
        CHBIntREntry.delete(0,END)
        CHBIntREntry.insert(0, 10000000)
    # 
    # RIN = 2000000 # nominal
    # Get_Data()
    #
    DCVA0 = numpy.mean(VBuffA) # calculate average
    DCVB0 = numpy.mean(VBuffB) # calculate average
    #DCVA0 = (DCVA0 - InOffA) * InGainA
    #DCVB0 = (DCVB0 - InOffB) * InGainB
    # external resistor
    DCM = chatestr * (DCVB0/(DCVA0-DCVB0))
    if (Rint - DCM) > 0: # trying to measure a resistor > RIN?
        DCR = (DCM * Rint) / (Rint - DCM) # correct for channel B input resistance
    else:
        DCR = DCM
    if DCR < 1000:
        OhmString = '{0:.2f} '.format(DCR) + "Ohms "# format with 2 decimal places
    else:
        OhmString = '{0:.3f} '.format(DCR/1000) + "KOhms " # divide by 1000 and format with 3 decimal places
    IAString = "Meas " + ' {0:.4f} '.format(DCVB0) + " V"
    OhmA0.config(text = OhmString) # change displayed value
    OhmA1.config(text = IAString) # change displayed value
    CHATestVEntry.delete(0,END)
    CHATestVEntry.insert(0, DCVA0)
#
    time.sleep(0.1)
#
## Scope time main loop
# Read the analog data and store the data into the arrays
def Analog_Time_In():
    global TimeDiv, TMsb, TRACEmodeTime, TRACEresetTime, TRACEaverage
    global CHAVOffsetEntry, CHAVGainEntry, CHBVOffsetEntry, CHBVGainEntry
    global InOffA, InGainA, InOffB, InGainB
    global PhADisp, PhAScreenStatus
    global First_Slow_sweep, Roll_Mode

    # get time scale
    TimeDiv = UnitConvert(TMsb.get())
    #

# Decide which Fast or Slow sweep routine to call
    if Roll_Mode.get() > 0: # 200:
        Analog_Roll_time() # rolling trace
    else:
        First_Slow_sweep = 0
        Analog_Fast_time()
        #
#
        if PhADisp.get() > 0 and PhAScreenStatus.get() == 1:
            Analog_Phase_In()
#
## Process captured time dmain signals to extract magnitude and phase data
def Analog_Phase_In():
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global DCV1, DCV2, DCV3, DCV4, MinV1, MaxV1, MinV2, MaxV2
    global FFTwindowshape, ZEROstuffing, CHANNELS, SMPfft
    global VBuffA, VBuffB, VBuffC, VBuffD, SHOWsamples, SAMPLErate
    global VAresult, VBresult, VABresult, VCresult, VDresult
    global PhaseVA, PhaseVB, PhaseVAB, PhaseVC, PhaseVD
    global vat_btn, vbt_btn, vct_btn, vdt_btn, vabt_btn

    fs = SAMPLErate
    freq_min = 10.0
    freq_max = fs/2.0
    
    if SHOWsamples >= 400:
        CALCFFTwindowshape(SMPfft) # (SHOWsamples)
    else:
        return
    num_bins = SMPfft + 1
    RMScorr = 7.07106 / SMPfft # (SHOWsamples) RMS For VOLTAGE!
    #
    if ShowC1_V.get() > 0 and CHANNELS >= 1:
        if vat_btn.config('text')[-1] == 'ON':
            if len(VBuffA) >= SMPfft:
                WData = VBuffA[0:SMPfft] - DCV1
            else:
                WData = VBuffA - DCV1
            if len(WData) != len(FFTwindowshape):
                CALCFFTwindowshape(len(WData))
            WData = WData * FFTwindowshape # 
            WData = WData / 5.0
            # VA array
            fft = czt_range(WData, num_bins, freq_min, freq_max, fs)
            PhaseVA = numpy.angle(fft, deg=True)     # calculate angle
            VAresult = numpy.absolute(fft)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
            VAresult = VAresult * RMScorr
    #
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        if vbt_btn.config('text')[-1] == 'ON':
            if len(VBuffB) >= SMPfft:
                WData = VBuffB[0:SMPfft] - DCV2
            else:
                WData = VBuffB - DCV2
            if len(WData) != len(FFTwindowshape):
                CALCFFTwindowshape(len(WData))
            WData = WData * FFTwindowshape # 
            WData = WData / 5.0
            # VB array
            fft = czt_range(WData, num_bins, freq_min, freq_max, fs)
            PhaseVB = numpy.angle(fft, deg=True)     # calculate angle
            VBresult = numpy.absolute(fft)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
            VBresult = VBresult * RMScorr
    #
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        if vct_btn.config('text')[-1] == 'ON':
            if len(VBuffC) >= SMPfft:
                WData = VBuffC[0:SMPfft] - DCV3
            else:
                WData = VBuffC - DCV3
            if len(WData) != len(FFTwindowshape):
                CALCFFTwindowshape(len(WData))
            WData = WData * FFTwindowshape # 
            WData = WData / 5.0
            # VB array
            fft = czt_range(WData, num_bins, freq_min, freq_max, fs)
            PhaseVC = numpy.angle(fft, deg=True)     # calculate angle
            VCresult = numpy.absolute(fft)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
            VCresult = VCresult * RMScorr
    #
    if ShowC4_V.get() > 0 and CHANNELS >= 4:
        if vdt_btn.config('text')[-1] == 'ON':
            if len(VBuffD) >= SMPfft:
                WData = VBuffD[0:SMPfft] - DCV4
            else:
                WData = VBuffD - DCV4
            if len(WData) != len(FFTwindowshape):
                CALCFFTwindowshape(len(WData))
            WData = WData * FFTwindowshape # 
            WData = WData / 5.0
            # VB array
            fft = czt_range(WData, num_bins, freq_min, freq_max, fs)
            PhaseVD = numpy.angle(fft, deg=True)     # calculate angle
            VDresult = numpy.absolute(fft)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
            VDresult = VDresult * RMScorr
    #
    if ShowC1_V.get() > 0 and ShowC2_V.get() > 0 and CHANNELS >= 2:
        if vabt_btn.config('text')[-1] == 'ON':
            if len(VBuffA) >= SMPfft:
                WData = (VBuffA[0:SMPfft]-VBuffB[0:SMPfft]) * FFTwindowshape # numpy.kaiser(SHOWsamples, 14) * 3
            else:
                WData = (VBuffA-VBuffB) * FFTwindowshape
            WData = WData / 5.0
            # VA-VB array
            fft = czt_range(WData, num_bins, freq_min, freq_max, fs)
            PhaseVAB = numpy.angle(fft, deg=True)     # calculate angle
            VABresult = numpy.absolute(fft)       # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
            VABresult = VABresult * RMScorr
#
    UpdatePhAAll()
#
## Right now this is a limited attempt to plot rolling sweep.
def Analog_Roll_time():
    global VBuffA, VBuffB, VFilterA, VFilterB, LSBsizeA, LSBsizeB
    global VmemoryA, VmemoryB, NoiseCH1, NoiseCH2
    global VUnAvgA, VUnAvgB, UnAvgSav
    global AWGSync, AWGAMode, AWGBMode, TMsb, HoldOff, HozPoss, HozPossentry
    global AWGAIOMode, AWGBIOMode, DecimateOption, DualMuxMode, MuxChan
    global TRACEresetTime, TRACEmodeTime, TRACEaverage, TRIGGERsample, TgInput, LShift
    global CHA, CHB, contloop
    global CHANNELS, TRACESread, TRACEsize, First_Slow_sweep, Roll_Mode # , ShiftPointer
    global RUNstatus, SingleShot, ManualTrigger, TimeDisp, XYDisp, FreqDisp
    global TimeDiv, hldn, Is_Triggered, GRW
    global SAMPLErate, SHOWsamples, MinSamples, MaxSamples, AWGSAMPLErate
    global TRACErefresh, AWGScreenStatus, XYScreenStatus, MeasureStatus
    global SCREENrefresh, DCrefresh
    global DCV1, DCV2, DCV3, DCV4, MinV1, MaxV1, MinV2, MaxV2
    global SV1, SV2, SVA_B
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHBVPosEntry
    global CHCVGainEntry, CHDVGainEntry, CHCVOffsetEntry, CHDVOffsetEntry
    global InOffA, InGainA, InOffB, InGainB
    global DigFiltA, DigFiltB, DFiltACoef, DFiltBCoef
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global VAets, VBets, Samples_Cycle, MulX, ETSDisp, ETSDir, ETSts, Fmin, FminE, eqivsamplerate
    global DivXEntry, FOffEntry, FminDisp, FOff, DivX, FMulXEntry, FBase, MaxETSrecord
    global cal, ADC_Mux_Mode, Alternate_Sweep_Mode, Last_ADC_Mux_Mode
    global MeasGateLeft, MeasGateRight, MeasGateNum, MeasGateStatus

    # Starting acquisition
    DCVA0 = DCVB0 = DCIA0 = DCIB0 = 0.0 # initalize measurment variable
    #
    NumSamples = 10 # int(SAMPLErate/TimeDiv)
    if First_Slow_sweep == 0:
        VBuffA = numpy.ones(GRW)       
        VBuffB = numpy.ones(GRW)
        First_Slow_sweep = 1
    if len(VBuffA) != GRW:
        VBuffA = numpy.ones(GRW)       
        VBuffB = numpy.ones(GRW)
    #
        Get_Data()
        #
    # get_samples returns a list of values for voltage
    for index in range(NumSamples): # calculate average
        DCVA0 += VBuffA[index] # Sum for average CA voltage 
        DCVB0 += VBuffB[index] # Sum for average CB voltage
    DCVA0 = DCVA0/(NumSamples) # calculate V average
    DCVB0 = DCVB0/(NumSamples) # calculate V average
    # Adjust for gain and offset
    DCVA0 = (DCVA0 - InOffA) * InGainA
    DCVB0 = (DCVB0 - InOffB) * InGainB
# next new sample
    VBuffA = shift_buffer(VBuffA, -1, DCVA0)
    VBuffB = shift_buffer(VBuffB, -1, DCVB0)
# Calculate measurement values
    SampleEnd = len(VBuffA)
    Cal_trace_scalars(10, SampleEnd-10)
#
    if TimeDisp.get() > 0:
        MakeTimeTrace()         # Update the traces
        UpdateTimeScreen()      # Update the screen 
    if XYDisp.get() > 0 and XYScreenStatus.get() > 0:
        UpdateXYAll()         # Update Data, trace and XY screen
    if MeasureStatus.get() > 0:
        UpdateMeasureScreen()
    # update screens
#
## routine for time scales faster than Slow_Sweep_Limit mSec/Div
def Analog_Fast_time():
    global VBuffA, VBuffB, VBuffC, VBuffD, VFilterA, VFilterB, VmemoryA, VmemoryB
    global VmemoryC, VmemoryD, VUnAvgA, VUnAvgB, UnAvgSav, NoiseCH1, NoiseCH2
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on, SaveDig
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on, COLORtrace8
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global AWGSync, TMsb, HoldOff, HozPoss, HozPossentry
    global DecimateOption, divfactor, UseSoftwareTrigger
    global TRACEresetTime, TRACEmodeTime, TRACEaverage, TRIGGERsample, TgInput, LShift, TgLabel
    global discontloop, contloop, DeBugMode, TRIGGERentry, TRIGGERlevel
    global CHANNELS, TRACESread, TRACEsize
    global RUNstatus, SingleShot, ManualTrigger, TimeDisp, XYDisp, FreqDisp
    global TimeDiv, hldn, Is_Triggered, Trigger_LPF_length, LPFTrigger
    global SAMPLErate, SHOWsamples, MinSamples, MaxSamples, AWGSAMPLErate
    global TRACErefresh, AWGScreenStatus, XYScreenStatus, MeasureStatus
    global SCREENrefresh, DCrefresh
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCV3, DCV4, MinV3, MaxV3, MinV4, MaxV4
    global SV1, SV2, SV3, SV4, SVA_B
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHBVPosEntry
    global CHCVGainEntry, CHDVGainEntry, CHCVOffsetEntry, CHDVOffsetEntry
    global CHCVPosEntry, CHDVPosEntry
    global InOffA, InGainA, InOffB, InGainB, InOffC, InGainC, InOffD, InGainD
    global DigFiltA, DigFiltB, DFiltACoef, DFiltBCoef, DigBuffA, DigBuffB
    global MeasGateLeft, MeasGateRight, MeasGateNum, MeasGateStatus
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V, Interp4Filter
    global CH1vpdvLevel, CH2vpdvLevel, CHAOffset, CHBOffset
    global CHCvpdvLevel, CHDvpdvLevel, CHCOffset, CHDOffset
    global BCVASkewEntry, BCVBSkewEntry, BCVCSkewEntry, BCVDSkewEntry
    global DigDeSkewVA, DigDeSkewVB, DigDeSkewVC, DigDeSkewVD
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2, CHC_RC_HP, CHD_RC_HP
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global CHC_TC1, CHC_TC2, CHD_TC1, CHD_TC2
    global CHC_A1, CHC_A2, CHD_A1, CHD_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global chc_TC1Entry, chc_TC2Entry, chd_TC1Entry, chd_TC2Entry
    global chc_A1Entry, chc_A2Entry, chd_A1Entry, chd_A2Entry
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global LSBsizeA, LSBsizeB, LSBsizeC, LSBsizeD
    global vat_btn, vbt_btn, vct_btn, vdt_btn, PhAScreenStatus
    
    if TRACEmodeTime.get() == 0 and TRACEresetTime == False:
        TRACEresetTime = True
        if len(VBuffA) != len(VmemoryA):
            VmemoryA = VBuffA # Clear the memory for averaging
            VmemoryB = VBuffB
            VmemoryC = VBuffC
            VmemoryD = VBuffD
    elif TRACEmodeTime.get() == 1:
        if TRACEresetTime == True:
            TRACEresetTime = False
        # Save previous trace in memory for average trace
        #if len(VBuffA) == len(VmemoryA):
        VmemoryA = VBuffA
        #if len(VBuffB) == len(VmemoryB):
        VmemoryB = VBuffB
        #if len(VBuffC) == len(VmemoryC):
        VmemoryC = VBuffC
        #if len(VBuffD) == len(VmemoryD):
        VmemoryD = VBuffD
#
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
    # hozpos = int(HozPoss * SAMPLErate/1000 )
    hozpos = 0
    # number of samples to acquire, 2 screen widths
    onescreen = 1024
#
# Starting acquisition
# Triggering handeled in Get_Data if softwhere or hardware
#
    TRACESread = 1
    Get_Data()
    #
    
# print("in Fast Time:", len(VBuffA), len(VBuffB))
    # SHOWsamples = len(VBuffA)
# Check if Input channel RC high pass compensation checked
    if CHA_RC_HP.get() == 1 and ShowC1_V.get() > 0:
        try:
            TC1A = float(cha_TC1Entry.get())
            if TC1A < 0:
                TC1A = 0
                cha_TC1Entry.delete(0,END)
                cha_TC1Entry.insert(0, TC1A)
        except:
            TC1A = CHA_TC1.get()
        try:
            TC2A = float(cha_TC2Entry.get())
            if TC2A < 0:
                TC2A = 0
                cha_TC2Entry.delete(0,END)
                cha_TC2Entry.insert(0, TC2A)
        except:
            TC2A = CHA_TC2.get()
        #
        try:
            Gain1A = float(cha_A1Entry.get())
        except:
            Gain1A = CHA_A1.get()
        try:
            Gain2A = float(cha_A2Entry.get())
        except:
            Gain2A = CHA_A2.get()
        #
        if len(VBuffA) > 4:
            VBuffA = Digital_RC_High_Pass( VBuffA, TC1A, Gain1A )
            VBuffA = Digital_RC_High_Pass( VBuffA, TC2A, Gain2A )
    if CHB_RC_HP.get() == 1 and ShowC2_V.get() > 0:
        try:
            TC1B = float(chb_TC1Entry.get())
            if TC1B < 0:
                TC1B = 0
                chb_TC1Entry.delete(0, END)
                chb_TC1Entry.insert(0, TC1B)
        except:
            TC1B = CHB_TC1.get()
        try:
            TC2B = float(chb_TC2Entry.get())
            if TC2B < 0:
                TC2B = 0
                chb_TC2Entry.delete(0, END)
                chb_TC2Entry.insert(0, TC2B)
        except:
            TC2B = CHB_TC2.get()
        #
        try:
            Gain1B = float(chb_A1Entry.get())
        except:
            Gain1B = CHB_A1.get()
        try:
            Gain2B = float(chb_A2Entry.get())
        except:
            Gain2B = CHB_A2.get()
        #
        if len(VBuffB) > 4:
            VBuffB = Digital_RC_High_Pass( VBuffB, TC1B, Gain1B )
            VBuffB = Digital_RC_High_Pass( VBuffB, TC2B, Gain2B )
#
    if CHC_RC_HP.get() == 1 and ShowC3_V.get() > 0:
        try:
            TC1C = float(chc_TC1Entry.get())
            if TC1C < 0:
                TC1C = 0
                chc_TC1Entry.delete(0,END)
                chc_TC1Entry.insert(0, TC1C)
        except:
            TC1C = CHC_TC1.get()
        try:
            TC2C = float(chc_TC2Entry.get())
            if TC2C < 0:
                TC2C = 0
                chc_TC2Entry.delete(0,END)
                chc_TC2Entry.insert(0, TC2C)
        except:
            TC2C = CHC_TC2.get()
        #
        try:
            Gain1C = float(chc_A1Entry.get())
        except:
            Gain1C = CHC_A1.get()
        try:
            Gain2C = float(chc_A2Entry.get())
        except:
            Gain2C = CHC_A2.get()
        #
        if len(VBuffC) > 4:
            VBuffC = Digital_RC_High_Pass( VBuffC, TC1C, Gain1C )
            VBuffC = Digital_RC_High_Pass( VBuffC, TC2C, Gain2C )
    if CHD_RC_HP.get() == 1 and ShowC4_V.get() > 0:
        try:
            TC1D = float(chd_TC1Entry.get())
            if TC1D < 0:
                TC1D = 0
                chd_TC1Entry.delete(0, END)
                chd_TC1Entry.insert(0, TC1D)
        except:
            TC1D = CHD_TC1.get()
        try:
            TC2D = float(chd_TC2Entry.get())
            if TC2D < 0:
                TC2D = 0
                chd_TC2Entry.delete(0, END)
                chd_TC2Entry.insert(0, TC2D)
        except:
            TC2D = CHD_TC2.get()
        #
        try:
            Gain1D = float(chd_A1Entry.get())
        except:
            Gain1D = CHD_A1.get()
        try:
            Gain2D = float(chd_A2Entry.get())
        except:
            Gain2D = CHD_A2.get()
        #
        if len(VBuffD) > 4:
            VBuffD = Digital_RC_High_Pass( VBuffD, TC1D, Gain1D )
            VBuffD = Digital_RC_High_Pass( VBuffD, TC2D, Gain2D )
# Check if need to DeSkew waveform data
    if DigDeSkewVA.get() > 0 and ShowC1_V.get() > 0:
        try:
            Shift = int(BCVASkewEntry.get())
        except:
            Shift = 0
            DigDeSkewVA.set(0)
        if Shift != 0:
            VBuffA = numpy.roll(VBuffA, Shift)
    if DigDeSkewVB.get() > 0 and ShowC2_V.get() > 0:
        try:
            Shift = int(BCVBSkewEntry.get())
        except:
            Shift = 0
            DigDeSkewVB.set(0)
        if Shift != 0:
            VBuffB = numpy.roll(VBuffB, Shift)
    if DigDeSkewVC.get() > 0 and ShowC3_V.get() > 0:
        try:
            Shift = int(BCVCSkewEntry.get())
        except:
            Shift = 0
            DigDeSkewVC.set(0)
        if Shift != 0:
            VBuffC = numpy.roll(VBuffC, Shift)
    if DigDeSkewVD.get() > 0 and ShowC4_V.get() > 0:
        try:
            Shift = int(BCVDSkewEntry.get())
        except:
            Shift = 0
            DigDeSkewVD.set(0)
        if Shift != 0:
            VBuffD = numpy.roll(VBuffD, Shift)
# check if digital filter box checked
    if DigFiltA.get() == 1 and ShowC1_V.get() > 0:
        if len(DFiltACoef) > 1:
            VBuffA = numpy.convolve(VBuffA, DFiltACoef)
    if DigFiltB.get() == 1 and ShowC2_V.get() > 0:
        if len(DFiltBCoef) > 1:
            VBuffB = numpy.convolve(VBuffB, DFiltBCoef)
# Check if we ned to do Software triggering
    if UseSoftwareTrigger > 0:
        # Find trigger sample point if necessary
        # print("Array Len ",len(VBuffA), "SHOWsamples ", SHOWsamples)
        LShift = 0
        if TgInput.get() == 1 and ShowC1_V.get() > 0:
            FindTriggerSample(VBuffA)
        if TgInput.get() == 2 and ShowC2_V.get() > 0:
            FindTriggerSample(VBuffB)
        if TgInput.get() == 3 and ShowC3_V.get() > 0:
            FindTriggerSample(VBuffC)
        if TgInput.get() == 4 and ShowC4_V.get() > 0:
            FindTriggerSample(VBuffD)
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
        if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
            LShift = 0 - TRIGGERsample
            if ShowC1_V.get() > 0:
                VBuffA = numpy.roll(VBuffA, LShift)
            if ShowC2_V.get() > 0:
                VBuffB = numpy.roll(VBuffB, LShift+2)
            if ShowC3_V.get() > 0:
                VBuffC = numpy.roll(VBuffC, LShift+2)
            if ShowC4_V.get() > 0:
                VBuffD = numpy.roll(VBuffD, LShift+3)
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
    else:
        # VBuffA = numpy.roll(VBuffA, -2)
        VBuffA = numpy.roll(VBuffA, -4)
        VBuffB = numpy.roll(VBuffB, -2)
        VBuffC = numpy.roll(VBuffC, -1)
        VBuffD = numpy.roll(VBuffD, -1)
#
    Endsample = SHOWsamples - 1
    if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
        if len(VBuffA) == len(VmemoryA):
            VBuffA = VmemoryA + (VBuffA - VmemoryA) / TRACEaverage.get()
        if len(VBuffB) == len(VmemoryB):
            VBuffB = VmemoryB + (VBuffB - VmemoryB) / TRACEaverage.get()
        if len(VBuffC) == len(VmemoryC):
            VBuffC = VmemoryC + (VBuffC - VmemoryC) / TRACEaverage.get()
        if len(VBuffD) == len(VmemoryD):
            VBuffD = VmemoryD + (VBuffD - VmemoryD) / TRACEaverage.get()
# DC value = average of the data record
    if MeasGateStatus.get() == 1:
        if (MeasGateRight-MeasGateLeft) > 0:
            hldn = int(MeasGateLeft * SAMPLErate/1000) + TRIGGERsample
            Endsample = int(MeasGateRight * SAMPLErate/1000) + TRIGGERsample
            if Endsample <= hldn:
                Endsample = hldn + 2
# Calculate Math Waveforms
    MakeMathWaves()
# Calculate scalar values
    if (len(VBuffA) > 1000) or (len(VBuffB) > 1000) or (len(VBuffC) > 1000) or (len(VBuffD) > 1000):
        Endsample = len(VBuffA) - 5
        Cal_trace_scalars(1, Endsample)
#
    # update screens
##    if TimeDisp.get() > 0: #
##        UpdateTimeAll() # Update Data, trace and time screen
##    if XYDisp.get() > 0 and XYScreenStatus.get() > 0:
##        UpdateXYAll() # Update Data, trace and XY screen
##    if MeasureStatus.get() > 0:
##        UpdateMeasureScreen()
###
# Calculate waveform scalar values
def Cal_trace_scalars(SampleStart, SampleEnd):
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V, MathTrace
    global VBuffA, VBuffB, VBuffC, VBuffD, MBuff, MBuffX, MBuffY
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCV3, DCV4, MinV3, MaxV3, MinV4, MaxV4
    global SV1, SV2, SVA_B, SV3, SV4
    global DCM, DCMX, DCMY, MinM, MinMX, MinMY, MaxM, MaxMX, MaxMY

    # RMS value = square root of average of the data record squared
    if ShowC1_V.get() > 0 and len(VBuffA) > 0:
        DCV1 = numpy.mean(VBuffA[SampleStart:SampleEnd])
        MinV1 = numpy.amin(VBuffA[SampleStart:SampleEnd])
        MaxV1 = numpy.amax(VBuffA[SampleStart:SampleEnd])
        SV1 = numpy.sqrt(numpy.mean(numpy.square(VBuffA[SampleStart:SampleEnd])))
    if ShowC2_V.get() > 0 and len(VBuffB) > 0:
        DCV2 = numpy.mean(VBuffB[SampleStart:SampleEnd])
        MinV2 = numpy.amin(VBuffB[SampleStart:SampleEnd])
        MaxV2 = numpy.amax(VBuffB[SampleStart:SampleEnd])
        SV2 = numpy.sqrt(numpy.mean(numpy.square(VBuffB[SampleStart:SampleEnd])))
    if ShowC3_V.get() > 0 and len(VBuffC) > 0:
        DCV3 = numpy.mean(VBuffC[SampleStart:SampleEnd])
        MinV3 = numpy.amin(VBuffC[SampleStart:SampleEnd])
        MaxV3 = numpy.amax(VBuffC[SampleStart:SampleEnd])
        SV3 = numpy.sqrt(numpy.mean(numpy.square(VBuffC[SampleStart:SampleEnd])))
    if ShowC4_V.get() > 0 and len(VBuffD) > 0:
        DCV4 = numpy.mean(VBuffD[SampleStart:SampleEnd])
        MinV4 = numpy.amin(VBuffD[SampleStart:SampleEnd])
        MaxV4 = numpy.amax(VBuffD[SampleStart:SampleEnd])
        SV4 = numpy.sqrt(numpy.mean(numpy.square(VBuffD[SampleStart:SampleEnd])))
    if (len(VBuffA) == len(VBuffB)) and len(VBuffA) > 0:
        SVA_B = numpy.sqrt(numpy.mean(numpy.square(VBuffA[SampleStart:SampleEnd]-VBuffB[SampleStart:SampleEnd])))
    if MathTrace.get() > 0 and len(MBuff) > 0:
        DCM = numpy.mean(MBuff[SampleStart:SampleEnd])
        MinM = numpy.amin(MBuff[SampleStart:SampleEnd])
        MaxM = numpy.amax(MBuff[SampleStart:SampleEnd])
    if Show_MathX.get() > 0 or YsignalMX.get():
        DCMX = numpy.mean(MBuffX[SampleStart:SampleEnd])
        MinMX = numpy.amin(MBuffX[SampleStart:SampleEnd])
        MaxMX = numpy.amax(MBuffX[SampleStart:SampleEnd])
    if Show_MathY.get() > 0 or YsignalMY.get():
        DCMY = numpy.mean(MBuffY[SampleStart:SampleEnd])
        MinMY = numpy.amin(MBuffY[SampleStart:SampleEnd])
        MaxMY = numpy.amax(MBuffY[SampleStart:SampleEnd])
#
# Function to calculate relative phase angle between two sine waves of the same frequency
# Removes any DC content
def Sine_Phase():
    global DCV1, DCV2, VBuffA, VBuffB, NoiseCH1, NoiseCH2

    sum1 = 0.0
    sum2 = 0.0
    sum12 = 0.0
    i = 0
    n = len(VBuffA)
    while i < n:
       sum1 += (VBuffA[i]-DCV1)*(VBuffA[i]-DCV1)
       sum2 += (VBuffB[i]-DCV2)*(VBuffB[i]-DCV2)
       sum12 += (VBuffA[i]-DCV1)*(VBuffB[i]-DCV2)
       i += 1
    return math.acos(sum12/math.sqrt(sum1*sum2))*180.0/numpy.pi 
#
#  High Pass y[n] = alpha * (y[n-1] + x[n] - x[n-1])
#  Low Pass y[n] = y[n-1] + (alpha * ((x[n] - x[n-1]))
#  All Pass y[n] = alpha * y[n-1] - alpha * (x[n] + x[n-1])
#  All Pass y[n] = alpha * (y[n-1] - x[n] - x[n-1])

## Digital RC filter function for input divider frequency compensation
# TC1 is in micro seconds
def Digital_RC_High_Pass( InBuff, TC1, Gain ): 
    global SAMPLErate
    
    OutBuff = []
    n = len(InBuff)
    Delta = 0.88/SAMPLErate
    TC = TC1 * 1.0E-6
    Alpha = TC / (TC + Delta)
    OutBuff.append(0.0) # initialize first output sample
    i = 1
    while i < n:
        OutBuff.append( Alpha * (OutBuff[i-1] + InBuff[i] - InBuff[i-1]) )
        i += 1
    OutBuff = numpy.array(OutBuff)
    OutBuff = InBuff + (OutBuff * Gain)
    return OutBuff
## Digital filter function for input divider frequency compensation
# TC1 is in micro seconds
def Digital_RC_Low_Pass( InBuff, TC1, Gain ): # TC1 is in micro seconds
    global SAMPLErate
    
    OutBuff = []
    n = len(InBuff)
    Delta = 1.0/SAMPLErate
    TC = TC1 * 1.0E-6
    Alpha = Delta / (TC + Delta)
    i = 1
    OutBuff.append(Alpha*InBuff[0])
    while i < n:
        OutBuff.append( OutBuff[i-1] + (Alpha * (InBuff[i] - InBuff[i-1])) )
        i += 1
    OutBuff = numpy.array(OutBuff)
    OutBuff = (OutBuff * Gain)
    return OutBuff
##
# Function to left (-num) or right (+num) shift buffer and fill with a value
# returns same length buffer
# preallocate empty array and assign slice
def shift_buffer(arr, num, fill_value=numpy.nan):
    result = numpy.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result[:] = arr
    return result
#
## Main SA and Bode loop
# Read from the stream and store the data into the arrays
def Analog_Freq_In():   
    global VBuffA, VBuffB, VBuffC, VBuffD
    global AWGAShape, AWGAIOMode, AWGBIOMode
    global AWGAFreqvalue, FStepSync, FSweepSync
    global NSteps, LoopNum, FSweepMode, FStep
    global StartFreqEntry, StopFreqEntry
    global MaxSamples, discontloop, TMsb
    global RUNstatus, SingleShotSA, FSweepCont
    global AWGSAMPLErate, IAScreenStatus, SpectrumScreenStatus, BodeScreenStatus
    global NiCScreenStatus, NiCDisp, NqPScreenStatus, NqPDisp
    global OverRangeFlagA, OverRangeFlagB, BodeDisp, FreqDisp, IADisp
    global DCA, DCB, InOffA, InGainA, InOffB, InGainB
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DigFiltA, DFiltACoef, DigFiltB, DFiltBCoef
    global BDSweepFile, FileSweepFreq, FileSweepAmpl
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global Reset_Freq, AWGAFreqEntry, AWGBFreqEntry, IASource, IA_Ext_Conf
    
    HalfSAMPLErate = SAMPLErate/2
    #
    if len(VBuffA) < 1000:
        return
    INITIALIZEstart()
    # Starting acquisition This is a HACK to get around non-continous AWG mode!
    # restart AWGs if indicated
    if FSweepMode.get() > 0 and BodeDisp.get() > 0: # Run Sweep Gen only if sleceted and Bode display is active
        if BDSweepFile.get() == 0:
            if LoopNum.get() <= len(FStep):
                FregPoint = FStep[LoopNum.get()-1] # look up next frequency from list of Freq Steps
            else:
                FregPoint = FStep[0]
        else:
            if LoopNum.get() <= len(FileSweepFreq): #
                FregPoint = FileSweepFreq[LoopNum.get()-1] # look up next frequency from list of bins
                VRMSAmpl = 10**(FileSweepAmpl[LoopNum.get()-1]/20) # convert to V RMS 0 dBV = 1V RMS
            else:
                FregPoint = FileSweepFreq[0]
                VRMSAmpl = 10**(FileSweepAmpl[0]/20) # convert to V RMS 0 dBV = 1V RMS
            VMax = 2.5 + (1.414*VRMSAmpl) # calculate positive peak assuming sine wave
            VMin = 2.5 - (1.414*VRMSAmpl) # calculate negative peak assuming sine wave
            if FSweepMode.get() == 1: # set new CH-A amplitude
                AWGAAmplEntry.delete(0,END)
                AWGAAmplEntry.insert(4, VMin)
                AWGAOffsetEntry.delete(0,END)
                AWGAOffsetEntry.insert(4, VMax)
        if FSweepMode.get() == 1: # set new CH-A frequency and adjust time base here
            AWGAFreqEntry.delete(0,END)
            AWGAFreqEntry.insert(4, FregPoint)
            ## Time list in s/div
            ##"5us", "10us", "20us", "50us", "100us", "200us", "500us", "1.0ms", "2.0ms", "5.0ms",
            ##"10ms", "20ms", "50ms", "100ms", "200ms", "500ms", "1.0s", "2.0s", "5.0s"
            if FregPoint <= 100 and FregPoint > 10:
                TMsb.set("20ms")
            elif FregPoint <= 1000 and FregPoint > 100:
                TMsb.set("2ms")
            elif FregPoint <= 10000 and FregPoint > 1000:
                TMsb.set("200us")
            elif FregPoint <= 100000 and FregPoint > 10000:
                TMsb.set("50us")
            else:
                TMsb.set("50ms")
            BTime()
            MakeAWGwaves()
    # 
    #if BodeDisp.get() > 0: # check if doing Bode Plot
        #Analog_Time_In() # donothing()
        # get samples
    OverRangeFlagA = OverRangeFlagB = 0 # Clear over range flags
    index = hldn # skip first hldn samples
    #
# check if digital filter box checked
    if DigFiltA.get() == 1:
        VBuffA = numpy.convolve(VBuffA, DFiltACoef)
    if DigFiltB.get() == 1:
        VBuffB = numpy.convolve(VBuffB, DFiltBCoef)
    DoFFT()
    if SpectrumScreenStatus.get() > 0 and FreqDisp.get() > 0:
        UpdateFreqAll()                         # Update spectrum Data, trace and screen
    if IAScreenStatus.get() > 0 and IADisp.get() > 0:
        #print("About to Update IA screen" )
        UpdateIAAll()
    if BodeScreenStatus.get() > 0 and BodeDisp.get() > 0:
        UpdateBodeAll()
    if NqPScreenStatus.get() > 0 and NqPDisp.get() > 0:
        UpdateNqPAll()
    if NiCScreenStatus.get() > 0 and NiCDisp.get() > 0:
        UpdateNiCAll()
    if SingleShotSA.get() == 1: # Single shot sweep is on
        RUNstatus.set(0)
# 
    if FSweepMode.get() > 0 and BodeDisp.get() > 0: # Increment loop counter only if sleceted and Bode display is active
        LoopNum.set(LoopNum.get() + 1)
        if LoopNum.get() > NSteps.get():
            if FSweepMode.get() == 1:
                AWGAFreqEntry.delete(0,"end")
                AWGAFreqEntry.insert(0, Reset_Freq)
            if FSweepMode.get() == 2:
                AWGBFreqEntry.delete(0,"end")
                AWGBFreqEntry.insert(0, Reset_Freq)
#
            LoopNum.set(1)
            if FSweepCont.get() == 0:
                RUNstatus.set(0)
#
## Make histogram of time signals
def MakeHistogram():
    global VBuffA, VBuffB, HBuffA, HBuffB, NoiseCH1, NoiseCH2
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global ShowC1_V, ShowC2_V, Xsignal
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global VABase, VATop, VBBase, VBTop

    if ShowC1_V.get() == 1 or Xsignal.get() == 6:
        CHAGridMax = (5 * CH1pdvRange ) + CHAOffset # Calculate CHA Grid Min and Max
        CHAGridMin = (-5 * CH1pdvRange ) + CHAOffset
        VAMid = (MinV1 + MaxV1)/2 # Find CHA mid value
        HBuffA = numpy.histogram(VBuffA, bins=5000, range=[CHAGridMin, CHAGridMax] )
        LowerPeak = 0
        UpperPeak = 0
        b = 0
        while (b < 4999):
            if HBuffA[0][b] > HBuffA[0][LowerPeak] and HBuffA[1][b] < VAMid:
                LowerPeak = b
                VABase = HBuffA[1][b]
            if HBuffA[0][b] > HBuffA[0][UpperPeak] and HBuffA[1][b] > VAMid:
                UpperPeak = b
                VATop = HBuffA[1][b]
            b = b + 1
    if ShowC2_V.get() == 1 or Xsignal.get() == 7:
        CHBGridMax = (5 * CH2pdvRange ) + CHBOffset # Calculate CHB Grid Min and Max
        CHBGridMin = (-5 * CH2pdvRange ) + CHBOffset
        VBMid = (MinV2 + MaxV2)/2 # Find CHB mid value
        HBuffB = numpy.histogram(VBuffB, bins=5000, range=[CHBGridMin, CHBGridMax] )
        LowerPeak = 0
        UpperPeak = 0
        b = 0
        while (b < 4999):
            if HBuffB[0][b] > HBuffB[0][LowerPeak] and HBuffB[1][b] < VBMid:
                LowerPeak = b
                VBBase = HBuffB[1][b]
            if HBuffB[0][b] > HBuffB[0][UpperPeak] and HBuffB[1][b] > VBMid:
                UpperPeak = b
                VBTop = HBuffB[1][b]
            b = b + 1
## Plot Histogram as Percent?
def BHistAsPercent():
    global HistAsPercent

    if askyesno("Plot as Percent", "Plot Histogram as Percent?", parent=xywindow):
        HistAsPercent = 1
    else:
        HistAsPercent = 0
#
## Software Routine to find rising edge of traces
def FindRisingEdge(Trace1, Trace2):
    global MinV1, MaxV1, MinV2, MaxV2, HoldOff, TRIGGERsample, TgInput, LShift
    global ETSrecord, DISsamples
    global SHOWsamples, SAMPLErate, CHAperiod, CHAfreq, CHBperiod, CHBfreq
    global CHAHW, CHALW, CHADCy, CHBHW, CHBLW, CHBDCy, ShowC1_V, ShowC2_V
    global CHABphase, CHBADelayR1, CHBADelayR2, CHBADelayF

    CHAHW = CHALW = CHADCy = CHBHW = CHBLW = CHBDCy = 0
    anr1 = bnr1 = 0
    anf1 = bnf1 = 1
    anr2 = bnr2 = 2
    hldn = int(HoldOff * SAMPLErate/1000)
    # print(DISsamples, len(Trace1))
    if TgInput.get() > 0: # if triggering right shift arrays to undo trigger left shift
        Trace1 = numpy.roll(Trace1, -LShift)
        Trace2 = numpy.roll(Trace2, -LShift)
    else:
        Trace1 = numpy.roll(Trace1, -hldn)
        Trace2 = numpy.roll(Trace2, -hldn)
    try:
        MidV1 = (numpy.amax(Trace1)+numpy.amin(Trace1))/2.0
        MidV2 = (numpy.amax(Trace2)+numpy.amin(Trace2))/2.0
    except:
        MidV1 = (MinV1+MaxV1)/2
        MidV2 = (MinV2+MaxV2)/2
#
    Arising = [i for (i, val) in enumerate(Trace1) if val >= MidV1 and Trace1[i-1] < MidV1]
    Afalling = [i for (i, val) in enumerate(Trace1) if val <= MidV1 and Trace1[i-1] > MidV1]
    AIrising = [i - (Trace1[i] - MidV1)/(Trace1[i] - Trace1[i-1]) for i in Arising]
    AIfalling = [i - (MidV1 - Trace1[i])/(Trace1[i-1] - Trace1[i]) for i in Afalling]
    
    CHAfreq = SAMPLErate / numpy.mean(numpy.diff(AIrising))
    CHAperiod = (numpy.mean(numpy.diff(AIrising)) * 1000.0) / SAMPLErate # time in mSec
# Catch zero length array?
    try:
        Dummy_read = Arising[0]
    except:
        pass
    # print(len(Arising), len(Afalling))
    if len(Arising) > 0 or len(Afalling) > 0:
        if Arising[0] > 0:
            try:
                anr1 = AIrising[0]
            except:
                anr1 = 0
            try:
                anr2 = AIrising[1]
            except:
                anr2 = SHOWsamples
            try:
                if AIfalling[0] < AIrising[0]:
                    anf1 = AIfalling[1]
                else:
                    anf1 = AIfalling[0]
            except:
                anf1 = 1
        else:
            try:
                anr1 = AIrising[1]
            except:
                anr1 = 0
            try:
                anr2 = AIrising[2]
            except:
                anr2 = SHOWsamples
            try:
                if AIfalling[1] < AIrising[1]:
                    anf1 = AIfalling[2]
                else:
                    anf1 = AIfalling[1]
            except:
                anf1 = 1
    CHAHW = float(((anf1 - anr1) * 1000.0) / SAMPLErate)
    CHALW = float(((anr2 - anf1) * 1000.0) / SAMPLErate)
    CHADCy = float(anf1 - anr1) / float(anr2 - anr1) * 100.0 # in percent
# search Trace 2
    Brising = [i for (i, val) in enumerate(Trace2) if val >= MidV2 and Trace2[i-1] < MidV2]
    Bfalling = [i for (i, val) in enumerate(Trace2) if val <= MidV2 and Trace2[i-1] > MidV2]
    BIrising = [i - (Trace2[i] - MidV2)/(Trace2[i] - Trace2[i-1]) for i in Brising]
    BIfalling = [i - (MidV2 - Trace2[i])/(Trace2[i-1] - Trace2[i]) for i in Bfalling]

    CHBfreq = SAMPLErate / numpy.mean(numpy.diff(BIrising))
    CHBperiod = (numpy.mean(numpy.diff(BIrising)) * 1000.0) / SAMPLErate # time in mSec
# Catch zero length array?
    try:
        Dummy_read = Brising[0]
    except:
        pass
    # print(len(Brising), len(Bfalling))
    if len(Brising) > 0 or len(Bfalling) > 0:
        if Brising[0] > 0:
            try:
                bnr1 = BIrising[0]
            except:
                bnr1 = 0
            try:
                bnr2 = BIrising[1]
            except:
                bnr2 = SHOWsamples
            try:
                if BIfalling[0] < BIrising[0]:
                    bnf1 = BIfalling[1]
                else:
                    bnf1 = BIfalling[0]
            except:
                bnf1 = 1
        else:
            try:
                bnr1 = BIrising[1]
            except:
                bnr1 = 0
            try:
                bnr2 = BIrising[2]
            except:
                bnr2 = SHOWsamples
            try:
                if BIfalling[1] < BIrising[1]:
                    bnf1 = BIfalling[2]
                else:
                    bnf1 = BIfalling[1]
            except:
                bnf1 = 1
    #
    CHBHW = float(((bnf1 - bnr1) * 1000.0) / SAMPLErate)
    CHBLW = float(((bnr2 - bnf1) * 1000.0) / SAMPLErate)
    CHBDCy = float(bnf1 - bnr1) / float(bnr2 - bnr1) * 100.0 # in percent
#
    if bnr1 > anr1:
        CHBADelayR1 = float((bnr1 - anr1) * 1000.0 / SAMPLErate)
    else:
        CHBADelayR1 = float((bnr2 - anr1) * 1000.0 / SAMPLErate)
    CHBADelayR2 = float((bnr2 - anr2) * 1000.0 / SAMPLErate)
    CHBADelayF = float((bnf1 - anf1) * 1000.0 / SAMPLErate)
    try:
        CHABphase = 360.0*(float((bnr1 - anr1) * 1000.0 / SAMPLErate))/CHAperiod
    except:
        CHABphase = 0.0
    if CHABphase < 0.0:
        CHABphase = CHABphase + 360.0
#
## Interpolate time between samples around trigger event
def ReInterploateTrigger(TrgBuff):
    global DX, TRIGGERsample, TRIGGERlevel

    DX = 0
    n = TRIGGERsample
    DY = TrgBuff[int(n)] - TrgBuff[int(n+1)]
    if DY != 0.0:
        DX = (TRIGGERlevel - TrgBuff[int(n+1)])/DY # calculate interpolated trigger point
    else:
        DX = 0
#
## Find the sample where trigger event happened 
def FindTriggerSample(TrgBuff): # find trigger time sample point of passed waveform array
    global AutoLevel, TgInput, TRIGGERlevel, TRIGGERentry, DX, SAMPLErate, Is_Triggered
    global HoldOffentry, HozPossentry, TRIGGERsample, TRACEsize, HozPoss, hozpos
    global Trigger_LPF_length, LPFTrigger, HoldOff
    
    # Set the TRACEsize variable
    if len(TrgBuff) < 128:
        return
    TRACEsize = len(TrgBuff)              # Set the trace length
    DX = 0
    Is_Triggered = 0
    if LPFTrigger.get() > 0:
        TFiltCoef = [] # empty coef array
        for n in range(Trigger_LPF_length.get()):
            TFiltCoef.append(float(1.0/Trigger_LPF_length.get()))
        TFiltCoef = numpy.array(TFiltCoef)
        TrgBuff = numpy.convolve(TrgBuff, TFiltCoef)
#
    try:
        TrgMin = numpy.amin(TrgBuff)
    except:
        TrgMin = 0.0
    try:
        TrgMax = numpy.amax(TrgBuff)
    except:
        TrgMax = 0.0
# Find trigger sample
    try:
        if AutoLevel.get() == 1:
            TRIGGERlevel = (TrgMin + TrgMax)/2
            TRIGGERentry.delete(0,"end")
            TRIGGERentry.insert(0, ' {0:.4f} '.format(TRIGGERlevel))
        else:
            TRIGGERlevel = eval(TRIGGERentry.get())
    except:
        TRIGGERentry.delete(0,END)
        TRIGGERentry.insert(0, TRIGGERlevel)
# Start from first sample after HoldOff
    # HoldOff = 0
# slide trace left right by HozPoss
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
        
    hldn = int(HoldOff * SAMPLErate/1000)
    hozpos = int(HozPoss * SAMPLErate/1000)
    if hozpos >= 0:
        TRIGGERsample = hldn
    else:
        TRIGGERsample = abs(hozpos)
#      
    Nmax = int(TRACEsize / 1.5) # first 2/3 of data set
    DX = 0
    n = HoldOff # TRIGGERsample
    TRIGGERlevel2 = 0.99 * TRIGGERlevel # Hysteresis to avoid triggering on noise
    if TRIGGERlevel2 < TrgMin:
        TRIGGERlevel2 = TrgMin
    if TRIGGERlevel2 > TrgMax:
        TRIGGERlevel2 = TrgMax
    ChInput = TrgBuff[int(n)]
    Prev = ChInput
    while ( ChInput >= TRIGGERlevel2) and n < Nmax:
        n = n + 1
        ChInput = TrgBuff[int(n)]
    while (ChInput <= TRIGGERlevel) and n < Nmax:
        Prev = ChInput
        n = n + 1
        ChInput = TrgBuff[int(n)]
    DY = ChInput - Prev
    if DY != 0.0:
        DX = (TRIGGERlevel - Prev)/DY # calculate interpolated trigger point
    else:
        DX = 0
    if TgEdge.get() == 1:
        TRIGGERlevel2 = 1.01 * TRIGGERlevel
        if TRIGGERlevel2 < TrgMin:
            TRIGGERlevel2 = TrgMin
        if TRIGGERlevel2 > TrgMax:
            TRIGGERlevel2 = TrgMax
        ChInput = TrgBuff[int(n)]
        Prev = ChInput
        while (ChInput <= TRIGGERlevel2) and n < Nmax:
            n = n + 1
            ChInput = TrgBuff[int(n)]
        while (ChInput >= TRIGGERlevel) and n < Nmax:
            Prev = ChInput
            n = n + 1
            ChInput = TrgBuff[int(n)]
        DY = Prev - ChInput
        try:
            DX = (Prev - TRIGGERlevel)/DY # calculate interpolated trigger point
        except:
            DX = 0
    
# check to insure trigger point is in bounds                
    if n < Nmax:
        TRIGGERsample = n - 1
        Is_Triggered = 1
    elif n > Nmax: # Didn't find edge in first 2/3 of data set
        TRIGGERsample = 1 + hldn # reset to begining
        Is_Triggered = 0
    if DX > 1:
        DX = 1 # never more than 100% of a sample period
    elif DX < 0:
        DX = 0 # never less than 0% of a sample period
    if math.isnan(DX):
        DX = 0
    TRIGGERsample = TRIGGERsample + hozpos
## Update Data, trace and time screen
def UpdateTimeAll():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    
    if len(VBuffA) < 100 and ShowC1_V.get() > 0:
        return
    if len(VBuffB) < 100 and ShowC2_V.get() > 0:
        return
    if len(VBuffC) < 100 and ShowC3_V.get() > 0:
        return
    if len(VBuffD) < 100 and ShowC4_V.get() > 0:
        return
    MakeTimeTrace()         # Update the traces
    UpdateTimeScreen()      # Update the screen 
## Update time trace and screen
def UpdateTimeTrace():
    global VBuffA, VBuffB, VBuffC, VBuffD
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    
    if len(VBuffA) < 100 and ShowC1_V.get() > 0:
        return
    if len(VBuffB) < 100 and ShowC2_V.get() > 0:
        return
    if len(VBuffC) < 100 and ShowC3_V.get() > 0:
        return
    if len(VBuffD) < 100 and ShowC4_V.get() > 0:
        return
    MakeTimeTrace()         # Update traces
    UpdateTimeScreen()      # Update the screen
## Update time screen with trace and text
def UpdateTimeScreen():     
    global VBuffA, VBuffB, VBuffC, VBuffD
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    
    if len(VBuffA) < 100 and ShowC1_V.get() > 0:
        return
    if len(VBuffB) < 100 and ShowC2_V.get() > 0:
        return
    if len(VBuffC) < 100 and ShowC3_V.get() > 0:
        return
    if len(VBuffD) < 100 and ShowC4_V.get() > 0:
        return
    
    MakeTimeScreen()        # Update the screen
    root.update()       # Activate updated screens    
## Update Data, trace and XY screen
def UpdateXYAll():
    global Xsignal, YsignalVA, YsignalVB, YsignalVC, YsignalVD
    
    if len(VBuffA) < 100 and (Xsignal.get() == 1 or YsignalVA.get() > 0):
        return
    if len(VBuffB) < 100 and (Xsignal.get() == 3 or YsignalVB.get() > 0):
        return
    if len(VBuffC) < 100 and (Xsignal.get() == 2 or YsignalVC.get() > 0):
        return
    if len(VBuffD) < 100 and (Xsignal.get() == 4 or YsignalVD.get() > 0):
        return
    
    MakeXYTrace()         # Update the traces
    UpdateXYScreen()      # Update the screen 
## Update XY trace and screen
def UpdateXYTrace():      
    global Xsignal, YsignalVA, YsignalVB, YsignalVC, YsignalVD
    
    if len(VBuffA) < 100 and (Xsignal.get() == 1 or YsignalVA.get() > 0):
        return
    if len(VBuffB) < 100 and (Xsignal.get() == 3 or YsignalVB.get() > 0):
        return
    if len(VBuffC) < 100 and (Xsignal.get() == 2 or YsignalVC.get() > 0):
        return
    if len(VBuffD) < 100 and (Xsignal.get() == 4 or YsignalVD.get() > 0):
        return
    
    MakeXYTrace()         # Update traces
    UpdateXYScreen()      # Update the screen
## Update XY screen with trace and text
def UpdateXYScreen():     
    global Xsignal, YsignalVA, YsignalVB, YsignalVC, YsignalVD
    
    if len(VBuffA) < 100 and (Xsignal.get() == 1 or YsignalVA.get() > 0):
        return
    if len(VBuffB) < 100 and (Xsignal.get() == 3 or YsignalVB.get() > 0):
        return
    if len(VBuffC) < 100 and (Xsignal.get() == 2 or YsignalVC.get() > 0):
        return
    if len(VBuffD) < 100 and (Xsignal.get() == 4 or YsignalVD.get() > 0):
        return
    
    MakeXYScreen()        # Update the screen
    root.update()       # Activate updated screens

def MakeMathWaves(): # calculate Math waveform arrays
    global VBuffA, VBuffB, VBuffC, VBuffD, MBuff, MBuffX, MBuffY
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global MathTrace, Show_MathX, Show_MathY, RUNstatus
    global MathString, MathXString, MathYString, YsignalMX, YsignalMY, Xsignal
    
    if MathTrace.get() > 0:
        if MathTrace.get() == 1: # plot sum of CA-V and CB-V
            MBuff = VBuffA + VBuffB
        elif MathTrace.get() == 2: # plot difference of CA-V and CB-V 
            MBuff = VBuffA - VBuffB
        elif MathTrace.get() == 3: # plot difference of CB-V and CA-V 
            MBuff = VBuffB - VBuffA
        elif MathTrace.get() == 4: # plot Sum of CA-V and CC-V 
            MBuff = VBuffA + VBuffC
        elif MathTrace.get() == 5: # plot difference of CA-V and CC-V 
            MBuff = VBuffA - VBuffC
        elif MathTrace.get() == 6: # plot difference of CC-V and CA-V 
            MBuff = VBuffC - VBuffA
        elif MathTrace.get() == 7: # plot Sum of CB-V and CC-V 
            MBuff = VBuffB + VBuffC
        elif MathTrace.get() == 8: # plot difference of CB-V and CC-V 
            MBuff = VBuffB - VBuffC
        elif MathTrace.get() == 9: # plot difference of CC-V and CB-V 
            MBuff = VBuffC - VBuffB
        elif MathTrace.get() == 10: # plot ratio of CB-V and CA-V
            try:
                VBuffB / VBuffA #  voltage gain A to B
            except:
                print("Math Error! 1")
                VBuffB / 0.000001
                RUNstatus.set(0)

        elif MathTrace.get() == 12: # plot from equation string
            # MathString = "(VBuffA[t]+ VBuffB[t] - CHAOffset)"
            try:
                MBuff = eval(MathString) 
            except:
                print("Math Error! 2")
                RUNstatus.set(0)
                
    if Show_MathX.get() > 0 or ((Xsignal.get() == 6 or YsignalMX.get() == 1) and XYDisp.get() == 1):
        try:
            MBuffX = eval(MathXString)
        except:
            print("Math Error! 3")
            RUNstatus.set(0)

    if Show_MathY.get() > 0 or (YsignalMY.get() == 1 and XYDisp.get() == 1):
        try:
            MBuffY = eval(MathYString)
        except:
            print("Math Error! 4")
            RUNstatus.set(0)
#
## Make the Digital scope time traces
def MakeDigitalTrace():
    global VBuffG
    global D0_is_on, D1_is_on, D2_is_on, D3_is_on
    global D4_is_on, D5_is_on, D6_is_on, D7_is_on
    global DBuff0, DBuff1, DBuff2, DBuff3, DBuff4, DBuff5, DBuff6, DBuff7
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    global X0L, Y0T, GRW, GRH, SHOWsamples, TgInput
    global TMpdiv       # Array with time / div values in ms
    global TMsb, Tdiv   # Time per div spin box variable
    global TimeDiv      # current spin box value
    global SAMPLErate, SCstart, DISsamples, RUNstatus, TRACEsize, TRIGGERsample
    
#
    TraceLength = len(VBuffG) #
    SCstart = 0
    ylo = 0.0
    xlo = 0.0
    Ymin = Y0T                  # Minimum position of time grid (top)
    Ymax = Y0T + GRH            # Maximum position of time grid (bottom)
    Xmin = X0L                  # Minimum position of time grid (left)
    Xmax = X0L + GRW            # Maximum position of time grid (right)

    Yconv = float(GRH/10.0) # pixels per vertical grid
    Xconv = float(GRW/Tdiv.get()) # pixels per horizontal grid

    c0 = GRH + Y0T    # vert possition fixed on grids
    c1 = c0 - Yconv
    c2 = c1 - Yconv
    c3 = c2 - Yconv
    c4 = c3 - Yconv
    c5 = c4 - Yconv
    c6 = c5 - Yconv
    c7 = c6 - Yconv
    
    D0line = []
    D1line = []
    D2line = []
    D3line = []
    D4line = []
    D5line = []
    D6line = []
    D7line = []
    # set and/or corrected for in range
    if TgInput.get() > 0:
        SCmin = int(-1 * TRIGGERsample)
        SCmax = int(TraceLength-4)
    else:
        SCmin = 0 # hldn
        SCmax = TraceLength - 1
    if SCstart < SCmin:             # No reading before start of array
        SCstart = SCmin
    if SCstart  > SCmax:            # No reading after end of array
        SCstart = SCmax
    #
    DISsamples = SAMPLErate * Tdiv.get() * TimeDiv # number of samples to display
    if DISsamples > TraceLength:
        DISsamples = TraceLength
    Xstep = GRW / DISsamples
    Xlimit = GRW+Xstep
    t = int(SCstart) # # t = Start sample in trace
    if t < 0:
        t = 0
    x = 0  
    if (DISsamples <= GRW):
        Xstep = GRW / DISsamples
        xa = 0 - int(Xstep*DX)       # adjust start pixel for interpolated trigger point
        x = 0 - int(Xstep*DX)
        Tstep = 1
        x1 = 0                      # x position of trace line
        xa1 = 0
        y1 = 0.0                    # y position of trace line
        while x <= Xlimit:
            if t < TraceLength:
                xa1 = xa + X0L
                x1 = x + X0L
                if D0_is_on :
                    y1 = int(c0 - (Yconv * DBuff0[t] * 0.75))
                    D0line.append(int(xa1))
                    D0line.append(int(y1))
                if D1_is_on :
                    y1 = int(c1 - (Yconv * DBuff1[t] * 0.75))
                    D1line.append(int(xa1))
                    D1line.append(int(y1))
                if D2_is_on :
                    y1 = int(c2 - (Yconv * DBuff2[t] * 0.75))
                    D2line.append(int(xa1))
                    D2line.append(int(y1))
                if D3_is_on :
                    y1 = int(c3 - (Yconv * DBuff3[t] * 0.75))
                    D3line.append(int(xa1))
                    D3line.append(int(y1))
                if D4_is_on :
                    y1 = int(c4 - (Yconv * DBuff4[t] * 0.75))
                    D4line.append(int(xa1))
                    D4line.append(int(y1))
                if D5_is_on :
                    y1 = int(c5 - (Yconv * DBuff5[t] * 0.75))
                    D5line.append(int(xa1))
                    D5line.append(int(y1))
                if D6_is_on :
                    y1 = int(c6 - (Yconv * DBuff6[t] * 0.75))
                    D6line.append(int(xa1))
                    D6line.append(int(y1))
                if D7_is_on :
                    y1 = int(c7 - (Yconv * DBuff7[t] * 0.75))
                    D7line.append(int(xa1))
                    D7line.append(int(y1))
            t = int(t + Tstep)
            x = x + Xstep
            xa = xa + Xstep
            
    else: #if (DISsamples > GRW): # if the number of samples is larger than the grid width need to ship over samples
        Xstep = 1
        Tstep = DISsamples / GRW      # number of samples to skip per grid pixel
        x1 = 0.0                          # x position of trace line
        ylo = 0.0                       # ymin position of trace 1 line
        yhi = 0.0                       # ymax position of trace 1 line

        t = int(SCstart) # + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
        if t > TraceLength-1:
            t = 0
        if t < 0:
            t = 0
        x = 0               # Horizontal screen pixel
        ft = t              # time point with fractions
        while (x <= GRW):
            if (t < TraceLength):
                if (t >= TraceLength):
                    t = TraceLength-2
                    x = GRW
                x1 = x + X0L
                #
                if D0_is_on :
                    ylo = DBuff0[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D0_is_on :
                            v = DBuff0[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c0 - Yconv * ylo)
                    yhi = int(c0 - Yconv * yhi)
                    D0line.append(int(x1))
                    D0line.append(int(ylo))        
                    D0line.append(int(x1))
                    D0line.append(int(yhi))
                    ypv1 = ylo
                #
                if D1_is_on :
                    ylo = DBuff1[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D1_is_on :
                            v = DBuff1[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c1 - Yconv * ylo)
                    yhi = int(c1 - Yconv * yhi)
                    D1line.append(int(x1))
                    D1line.append(int(ylo))        
                    D1line.append(int(x1))
                    D1line.append(int(yhi))
                    ypv1 = ylo
                #
                if D2_is_on :
                    ylo = DBuff2[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D2_is_on :
                            v = DBuff2[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c2 - Yconv * ylo)
                    yhi = int(c2 - Yconv * yhi)
                    D2line.append(int(x1))
                    D2line.append(int(ylo))        
                    D2line.append(int(x1))
                    D2line.append(int(yhi))
                    ypv1 = ylo
                #
                if D3_is_on :
                    ylo = DBuff3[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D3_is_on :
                            v = DBuff3[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c3 - Yconv * ylo)
                    yhi = int(c3 - Yconv * yhi)
                    D3line.append(int(x1))
                    D3line.append(int(ylo))        
                    D3line.append(int(x1))
                    D3line.append(int(yhi))
                    ypv1 = ylo
                #
                if D4_is_on :
                    ylo = DBuff4[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D4_is_on :
                            v = DBuff4[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c4 - Yconv * ylo)
                    yhi = int(c4 - Yconv * yhi)
                    D4line.append(int(x1))
                    D4line.append(int(ylo))        
                    D4line.append(int(x1))
                    D4line.append(int(yhi))
                    ypv1 = ylo
                #
                if D5_is_on :
                    ylo = DBuff5[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D5_is_on :
                            v = DBuff5[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c5 - Yconv * ylo)
                    yhi = int(c5 - Yconv * yhi)
                    D5line.append(int(x1))
                    D5line.append(int(ylo))        
                    D5line.append(int(x1))
                    D5line.append(int(yhi))
                    ypv1 = ylo
                #
                if D6_is_on :
                    ylo = DBuff6[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D6_is_on :
                            v = DBuff6[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c6 - Yconv * ylo)
                    yhi = int(c6 - Yconv * yhi)
                    D6line.append(int(x1))
                    D6line.append(int(ylo))        
                    D6line.append(int(x1))
                    D6line.append(int(yhi))
                    ypv1 = ylo
                #
                if D7_is_on :
                    ylo = DBuff7[t] * 0.75
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TraceLength:
                        if D7_is_on :
                            v = DBuff7[t] * 0.75
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    #
                    ylo = int(c7 - Yconv * ylo)
                    yhi = int(c7 - Yconv * yhi)
                    D7line.append(int(x1))
                    D7line.append(int(ylo))        
                    D7line.append(int(x1))
                    D7line.append(int(yhi))
                    ypv1 = ylo
                #
            ft = ft + Tstep
            t = int(ft)
            if (t > TraceLength):
                t = TraceLength-2
                x = GRW
            x = x + Xstep
#
## Make the Analog scope time traces
def MakeTimeTrace():
    global VBuffA, VBuffB, VBuffC, VBuffD, VBuffG, NoiseCH1, NoiseCH2
    global MBuff, MBuffX, MBuffY, CHANNELS
    global VmemoryA, VmemoryB, VmemoryC, VmemoryD
    global VUnAvgA, VUnAvgB, UnAvgSav
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global T1Vline, T2Vline, T3Vline, T4Vline
    global Tmathline, TMXline, TMYline
    global MathString, MathAxis, MathXString, MathYString, MathXAxis, MathYAxis
    global Triggerline, Triggersymbol, TgInput, TgEdge, HoldOff, HoldOffentry
    global X0L, Y0T, GRW, GRH, MouseX, MouseY, MouseCAV, MouseCBV, MouseCCV, MouseCDV
    global SHOWsamples, ZOHold, AWGBMode, Tdiv
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global Show_MathX, Show_MathY
    global TRACES, TRACESread
    global AutoCenterA, AutoCenterB
    global CHAsb, CHBsb, CHCsb, CHDsb, CHAOffset, CHBOffset, CHCOffset, CHDOffset
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TimeDiv      # current spin box value
    global SAMPLErate, SCstart, DISsamples, First_Slow_sweep
    global TRIGGERsample, TRACEsize, DX
    global TRIGGERlevel, TRIGGERentry, AutoLevel
    global InOffA, InGainA, InOffB, InGainB
    global CH1pdvRange, CH2pdvRange, CHCpdvRange, CHDpdvRange
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCV3, DCV4, MinV3, MaxV3, MinV4, MaxV4
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHBVPosEntry, CHCVPosEntry, CHDVPosEntry
    global CHMOffset, CHMVPosEntry, CHMpdvRange, CHMsb, CHCsb, CHDsb

    # Set the TRACEsize variable

    try:
        TimeDiv = UnitConvert(TMsb.get())
    except:
        pass

    TRACEsize = SHOWsamples #
    SCstart = 0
    ylo = 0.0
    xlo = 0.0
    Ymin = Y0T                  # Minimum position of time grid (top)
    Ymax = Y0T + GRH            # Maximum position of time grid (bottom)
    Xmin = X0L                  # Minimum position of time grid (left)
    Xmax = X0L + GRW            # Maximum position of time grid (right)

    # Check for Auto Centering
    if AutoCenterA.get() > 0:
        CHAOffset = DCV1
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, ' {0:.2f} '.format(CHAOffset))
    if AutoCenterB.get() > 0:
        CHBOffset = DCV2
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, ' {0:.2f} '.format(CHBOffset))
    if AutoCenterC.get() > 0:
        CHCOffset = DCV3
        CHCVPosEntry.delete(0,END)
        CHCVPosEntry.insert(0, ' {0:.2f} '.format(CHCOffset))
    if AutoCenterD.get() > 0:
        CHDOffset = DCV4
        CHDVPosEntry.delete(0,END)
        CHDVPosEntry.insert(0, ' {0:.2f} '.format(CHDOffset))
    # get the vertical ranges
    # get the vertical offsets
    # prevent divide by zero error
    if CHANNELS >= 1:
        CH1pdvRange = UnitConvert(CHAsb.get())
        try: # CHA
            CHAOffset = float(eval(CHAVPosEntry.get()))
        except:
            CHAVPosEntry.delete(0,END)
            CHAVPosEntry.insert(0, CHAOffset)
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
    if CHANNELS >= 2:
        CH2pdvRange = UnitConvert(CHBsb.get())
        try: # CHB
            CHBOffset = float(eval(CHBVPosEntry.get()))
        except:
            CHBVPosEntry.delete(0,END)
            CHBVPosEntry.insert(0, CHBOffset)
        if CH2pdvRange < 0.001:
            CH2pdvRange = 0.001
    if CHANNELS >= 3:
        CHCpdvRange = UnitConvert(CHCsb.get())
        try: # CHC
            CHCOffset = float(eval(CHCVPosEntry.get()))
        except:
            CHCVPosEntry.delete(0,END)
            CHCVPosEntry.insert(0, CHCOffset)
        if CHCpdvRange < 0.001:
            CHCpdvRange = 0.001
    if CHANNELS >= 4:
        CHDpdvRange = UnitConvert(CHDsb.get())
        try: # CHD
            CHDOffset = float(eval(CHDVPosEntry.get()))
        except:
            CHDVPosEntry.delete(0,END)
            CHDVPosEntry.insert(0, CHDOffset)
        if CHDpdvRange < 0.001:
            CHDpdvRange = 0.001
    CHMpdvRange = UnitConvert(CHMsb.get())
    try: # Math
        CHMOffset = float(eval(CHMVPosEntry.get()))
    except:
        CHMVPosEntry.delete(0,END)
        CHNVPosEntry.insert(0, CHMOffset)
    if CHMpdvRange < 0.001:
        CHMpdvRange = 0.001
    # X Y Math
    try:
        CHMXpdvRange = float(eval(CHMXsb.get()))
    except:
        CHMXpdvRange = 0.001
    try:
        CHMXOffset = float(eval(CHMXPosEntry.get()))
    except:
        CHMXOffset = 0.0
    try:
        CHMYpdvRange = float(eval(CHMYsb.get()))
    except:
        CHMYpdvRange = 0.001
    try:
        CHMYOffset = float(eval(CHMYPosEntry.get()))
    except:
        CHMYOffset = 0.0
    #
#
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
        HozPoss = 0.0
#
    hozpos = int(HozPoss * SAMPLErate/1000.0 )
    if hozpos < 0:
        hozpos = 0        
    #  drawing the traces 
    if TRACEsize == 0:      # If no trace, skip rest of this routine
        T1Vline = []        # Trace line channel A V
        T2Vline = []        # Trace line channel B V
        T3Vline = []                    # V Trace line channel C
        T4Vline = []                    # V Trace line channel D
        Tmathline = []                  # math trce line
        TMXline = []                    # X math Trace line
        TMYline = []                    # Y math Trace line
        return() 

    # set and/or corrected for in range
    if TgInput.get() > 0:
        SCmin = int(-1 * TRIGGERsample)
        SCmax = int(TRACEsize-4)
    else:
        SCmin = 0 # hldn
        SCmax = TRACEsize - 1
    if SCstart < SCmin:             # No reading before start of array
        SCstart = SCmin
    if SCstart  > SCmax:            # No reading after end of array
        SCstart = SCmax

    # Make Trace lines etc.
    mg_siz = float(GRH/10.0)
    if CHANNELS >= 1:
        Yconv1 = mg_siz / CH1pdvRange    # Vertical Conversion factors from samples to screen points
        Xconv1 = float(GRW/Tdiv.get()) / CH1pdvRange    # Horizontal Conversion factors from samples to screen points
    if CHANNELS >= 2:
        Yconv2 = mg_siz / CH2pdvRange
        Xconv2 = float(GRW/Tdiv.get()) / CH2pdvRange
    if CHANNELS >= 3:
        Yconv3 = mg_siz / CHCpdvRange
        Xconv3 = float(GRW/Tdiv.get()) / CHCpdvRange
    if CHANNELS >= 4:
        Yconv4 = mg_siz / CHDpdvRange
        Xconv4 = float(GRW/Tdiv.get()) / CHDpdvRange
    YconvM = mg_siz / CHMpdvRange
    XconvM = float(GRW/Tdiv.get()) / CHMpdvRange
# include ploting X and Y math formulas vs time for now
    YconvMx = mg_siz / CHMXpdvRange
    YconvMy = mg_siz / CHMYpdvRange
#
    c1 = GRH / 2.0 + Y0T    # fixed correction channel A
    c2 = GRH / 2.0 + Y0T    # fixed correction channel B
    c3 = GRH / 2.0 + Y0T    # fixed correction channel C
    c4 = GRH / 2.0 + Y0T    # fixed correction channel D

##    if First_Slow_sweep == 1:
##        TRACEsize = len(VBuffA)
##        DISsamples = GRW
##    else:
    DISsamples = SAMPLErate * Tdiv.get() * TimeDiv # number of samples to display
    # print("DISsamples = ",DISsamples, "SHOWsamples = ", SHOWsamples)
    #
    T1Vline = []                    # V Trace line channel A
    T2Vline = []                    # V Trace line channel B
    T3Vline = []                    # V Trace line channel C
    T4Vline = []                    # V Trace line channel D
    Tmathline = []                  # math trce line
    TMXline = []                    # X math Trace line
    TMYline = []                    # Y math Trace line
    if len(VBuffA) < 4 and len(VBuffB) < 4:
        return
    t = int(SCstart) # + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
    if t < 0:
        t = 0
    x = 0                           # Horizontal screen pixel
#
    if ShowC1_V.get() > 0 and CHANNELS >= 1:
        ypv1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        ypv2 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        ypv3 = int(c1 - Yconv3 * (VBuffC[t] - CHCOffset))
    if ShowC4_V.get() > 0 and CHANNELS >= 4:
        ypv4 = int(c2 - Yconv4 * (VBuffD[t] - CHDOffset))
    DvY1 = DvY2 = DvY3 = DvY4 = 0 
#
    if (DISsamples <= GRW):
        # print("DX = ", DX)
        Xstep = GRW / DISsamples
        xa = 0 # - int(Xstep*DX) # adjust start pixel for interpolated trigger point
        x = 0 # - int(Xstep*DX)
        Tstep = 1
        x1 = 0                      # x position of trace line
        xa1 = 0
        y1 = 0.0                    # y position of trace line
        if ShowC1_V.get() > 0 and CHANNELS >= 1:
            ypv1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
        if ShowC2_V.get() > 0 and CHANNELS >= 2:
            ypv2 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
        if ShowC3_V.get() > 0 and CHANNELS >= 3:
            ypv3 = int(c1 - Yconv3 * (VBuffC[t] - CHCOffset))
        if ShowC4_V.get() > 0 and CHANNELS >= 4:
            ypv4 = int(c2 - Yconv4 * (VBuffD[t] - CHDOffset))
        ypm = ypmx = ypmy = GRH / 2.0 + Y0T
        if TgInput.get() == 0:
            Xlimit = GRW
        else:
            Xlimit = GRW+Xstep
        while x <= Xlimit:
            if t < TRACEsize:
                xa1 = xa + X0L
                x1 = x + X0L
                if ShowC1_V.get() == 1 and CHANNELS >= 1:
                    y1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(ypv1))
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(y1))
                    else:    
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(y1))
                    DvY1 = ypv1 - y1
                    ypv1 = y1
                if ShowC2_V.get() == 1 and CHANNELS >= 2:
                    y1 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        T2Vline.append(int(x1))
                        T2Vline.append(int(ypv2))
                        T2Vline.append(int(x1))
                        T2Vline.append(int(y1))
                    else:
                        T2Vline.append(int(x1))
                        T2Vline.append(int(y1))
                    DvY2 = ypv2 - y1
                    ypv2 = y1
                if ShowC3_V.get() == 1 and CHANNELS >= 3:
                    y1 = int(c3 - Yconv3 * (VBuffC[t] - CHCOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        T3Vline.append(int(x1))
                        T3Vline.append(int(ypv3))
                        T3Vline.append(int(x1))
                        T3Vline.append(int(y1))
                    else:
                        T3Vline.append(int(x1))
                        T3Vline.append(int(y1))
                    DvY3 = ypv3 - y1
                    ypv3 = y1
                if ShowC4_V.get() == 1 and CHANNELS >= 4:
                    y1 = int(c4 - Yconv4 * (VBuffD[t] - CHDOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        T4Vline.append(int(x1))
                        T4Vline.append(int(ypv4))
                        T4Vline.append(int(x1))
                        T4Vline.append(int(y1))
                    else:
                        T4Vline.append(int(x1))
                        T4Vline.append(int(y1))
                    DvY4 = ypv4 - y1
                    ypv4 = y1
                if MathTrace.get() > 0:
                    y1 = int(c1 - YconvM * (MBuff[t] - CHMOffset))
                                    
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        Tmathline.append(int(x1))
                        Tmathline.append(int(ypm))
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    else:    # connet the dots with single line
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    ypm = y1
                if Show_MathX.get() > 0:
                    y1 = int(c1 - YconvMx * (MBuffX[t] - CHMXOffset))
                        
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMXline.append(int(x1))
                        TMXline.append(int(ypmx))
                        TMXline.append(int(x1))
                        TMXline.append(int(y1))
                    else:    # connet the dots with single line
                        TMXline.append(int(x1))
                        TMXline.append(int(y1))
                    ypmx = y1
                if Show_MathY.get() > 0:
                    y1 = int(c1 - YconvMy * (MBuffY[t]- CHMYOffset))
                        
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMYline.append(int(x1))
                        TMYline.append(int(ypmy))
                        TMYline.append(int(x1))
                        TMYline.append(int(y1))
                    else:    # connet the dots with single line
                        TMYline.append(int(x1))
                        TMYline.append(int(y1))
                    ypmy = y1
                        
            # remember trace verticle pixel at X mouse location
            if MouseX - X0L >= x and MouseX - X0L < (x + Xstep): # - Xstep
                Xfine = MouseX - X0L - x
                if ShowC1_V.get() > 0 and CHANNELS >= 1:
                    MouseCAV = ypv1 - (DvY1 * (Xfine/Xstep)) # interpolate along yaxis 
                if ShowC2_V.get() > 0 and CHANNELS >= 2:
                    MouseCBV = ypv2 - (DvY2 * (Xfine/Xstep))
                if ShowC3_V.get() > 0 and CHANNELS >= 3:
                    MouseCCV = ypv3 - (DvY3 * (Xfine/Xstep)) 
                if ShowC4_V.get() > 0 and CHANNELS >= 4:
                    MouseCDV = ypv4 - (DvY4 * (Xfine/Xstep))
 
            t = int(t + Tstep)
            x = x + Xstep
            xa = xa + Xstep
            
    else: #if (DISsamples > GRW): # if the number of samples is larger than the grid width need to ship over samples
        Xstep = 1
        Tstep = DISsamples / GRW      # number of samples to skip per grid pixel
        x1 = 0.0                          # x position of trace line
        ylo = 0.0                       # ymin position of trace 1 line
        yhi = 0.0                       # ymax position of trace 1 line

        t = int(SCstart) # + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
        if t > len(VBuffA)-1:
            t = 0
        if t < 0:
            t = 0
        x = 0               # Horizontal screen pixel
        ft = t              # time point with fractions
        while (x <= GRW):
            if (t < TRACEsize):
                # print( "t = ", t)
                if (t >= len(VBuffA)):
                    t = len(VBuffA)-2
                    x = GRW
                    
                x1 = x + X0L
                ylo = VBuffA[t] - CHAOffset
                yhi = ylo
                n = t
                while n < (t + Tstep) and n < TRACEsize:
                    if ( ShowC1_V.get() == 1 ):
                        v = VBuffA[t] - CHAOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                    n = n + 1
                #
                if ShowC1_V.get() == 1 and CHANNELS >= 1:
                    ylo = int(c1 - Yconv1 * ylo)
                    yhi = int(c1 - Yconv1 * yhi)
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax
                    if (yhi < Ymin):
                        yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    T1Vline.append(int(x1))
                    T1Vline.append(int(ylo))        
                    T1Vline.append(int(x1))
                    T1Vline.append(int(yhi))
                    ypv1 = ylo
                #
                if ShowC2_V.get() == 1 and CHANNELS >= 2:
                    ylo = VBuffB[t] - CHBOffset
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TRACEsize:
                        if ( ShowC2_V.get() == 1 ):
                            v = VBuffB[t] - CHBOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    if ShowC2_V.get() == 1 and CHANNELS >= 2:
                        ylo = int(c2 - Yconv2 * ylo)
                        yhi = int(c2 - Yconv2 * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax

                        if (yhi < Ymin):
                             yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        T2Vline.append(int(x1))
                        T2Vline.append(int(ylo))        
                        T2Vline.append(int(x1))
                        T2Vline.append(int(yhi))
                        ypv2 = ylo
                #
                if ShowC3_V.get() == 1 and CHANNELS >= 3:
                    ylo = VBuffC[t] - CHCOffset
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TRACEsize:
                        if ( ShowC3_V.get() == 1 ):
                            v = VBuffC[t] - CHCOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    if ShowC3_V.get() == 1 and CHANNELS >= 3:
                        ylo = int(c3 - Yconv3 * ylo)
                        yhi = int(c3 - Yconv3 * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax
                        if (yhi < Ymin):
                            yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        T3Vline.append(int(x1))
                        T3Vline.append(int(ylo))        
                        T3Vline.append(int(x1))
                        T3Vline.append(int(yhi))
                        ypv3 = ylo
                #
                if ShowC4_V.get() == 1 and CHANNELS >= 4:
                    ylo = VBuffD[t] - CHDOffset
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TRACEsize:
                        v = VBuffD[t] - CHDOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                        n = n + 1
                    #
                    if ShowC4_V.get() == 1 and CHANNELS >= 4:
                        ylo = int(c4 - Yconv4 * ylo)
                        yhi = int(c4 - Yconv4 * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax
                        if (yhi < Ymin):
                            yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        T4Vline.append(int(x1))
                        T4Vline.append(int(ylo))        
                        T4Vline.append(int(x1))
                        T4Vline.append(int(yhi))
                        ypv4 = ylo
                #
                if MathTrace.get() > 0:
                    ylo = MBuff[t] - CHMOffset
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TRACEsize:
                        v = MBuff[t] - CHMOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                        n = n + 1
                    #
                    ylo = int(c4 - YconvM * ylo)
                    yhi = int(c4 - YconvM * yhi)
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax
                    if (yhi < Ymin):
                        yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    Tmathline.append(int(x1))
                    Tmathline.append(int(ylo))        
                    Tmathline.append(int(x1))
                    Tmathline.append(int(yhi))
                    ypm = ylo
                #
                if Show_MathX.get() > 0:
                    ylo = MBuffX[t] - CHMXOffset
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TRACEsize:
                        v = MBuffX[t] - CHMXOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                        n = n + 1
                    #
                    ylo = int(c4 - YconvMx * ylo)
                    yhi = int(c4 - YconvMx * yhi)
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax
                    if (yhi < Ymin):
                        yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMXline.append(int(x1))
                        TMXline.append(int(ylo))        
                        TMXline.append(int(x1))
                        TMXline.append(int(yhi))
                    else:
                        TMXline.append(int(x1))
                        TMXline.append(int(yhi))
                    ypm = ylo
                #
                if Show_MathY.get() > 0:
                    ylo = MBuffY[t] - CHMYOffset
                    yhi = ylo
                    n = t
                    while n < (t + Tstep) and n < TRACEsize:
                        v = MBuffY[t] - CHMYOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                        n = n + 1
                    #
                    ylo = int(c4 - YconvMy * ylo)
                    yhi = int(c4 - YconvMy * yhi)
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax
                    if (yhi < Ymin):
                        yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMYline.append(int(x1))
                        TMYline.append(int(ylo))        
                        TMYline.append(int(x1))
                        TMYline.append(int(yhi))
                    else:
                        TMYline.append(int(x1))
                        TMYline.append(int(yhi))
                    ypm = ylo

            ft = ft + Tstep
            if (MouseX - X0L) == x: # > (x - 1) and (MouseX - X0L) < (x + 1):
                if ShowC1_V.get() > 0 and CHANNELS >= 1:
                    MouseCAV = ypv1
                if ShowC2_V.get() > 0 and CHANNELS >= 2:
                    MouseCBV = ypv2
                if ShowC3_V.get() > 0 and CHANNELS >= 3:
                    MouseCCV = ypv3
                if ShowC4_V.get() > 0 and CHANNELS >= 4:
                    MouseCDV = ypv4
            t = int(ft)
            if (t >= len(VBuffA)):
                t = len(VBuffA)-2
                x = GRW
            x = x + Xstep
    # Make trigger triangle pointer
    Triggerline = []    # Trigger pointer
    Triggersymbol = []  # Trigger symbol
    if TgInput.get() > 0:
        x1 = X0L
        if TgInput.get() == 1: # triggering on CA-V
            Yconv = mg_siz / CH1pdvRange
            ytemp = Yconv * (float(TRIGGERentry.get())-CHAOffset) #TRIGGERlevel 
            y1 = int(c1 - ytemp)
        elif TgInput.get() == 2:  # triggering on CB-V
            Yconv = mg_siz / CH2pdvRange
            ytemp = Yconv * (float(TRIGGERentry.get())-CHBOffset) #TRIGGERlevel
            y1 = int(c2 - ytemp)
        elif TgInput.get() == 3: # triggering on CC-V
            Yconv = mg_siz / CHCpdvRange
            ytemp = Yconv * (float(TRIGGERentry.get())-CHCOffset) #TRIGGERlevel 
            y1 = int(c3 - ytemp)
        elif TgInput.get() == 4:  # triggering on CD-V
            Yconv = mg_siz / CHDpdvRange
            ytemp = Yconv * (float(TRIGGERentry.get())-CHDOffset) #TRIGGERlevel
            y1 = int(c4 - ytemp)
        elif TgInput.get() >= 5:  # triggering on Digital ?
            y1 = int((GRH+Y0T) - (mg_siz * (TgInput.get() - 5)))
        #
        if (y1 < Ymin):
            y1 = Ymin
        if (y1 > Ymax):
            y1 = Ymax
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1+5))
        Triggerline.append(int(x1+5))
        Triggerline.append(int(y1))
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1-5))
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1+5))
        x1 = X0L + (GRW/2)
        if TgEdge.get() == 0: # draw rising edge symbol
            y1 = -3
            y2 = -13
        else:
            y1 = -13
            y2 = -3
        Triggersymbol.append(int(x1-10))
        Triggersymbol.append(int(Ymin+y1))
        Triggersymbol.append(int(x1))
        Triggersymbol.append(int(Ymin+y1))
        Triggersymbol.append(int(x1))
        Triggersymbol.append(int(Ymin+y2))
        Triggersymbol.append(int(x1+10))
        Triggersymbol.append(int(Ymin+y2))
    #
    try:
        MakeDigitalTrace()
    except:
        pass
    #
#
## Make the XY plot traces
def MakeXYTrace():    
    global VBuffA, VBuffB, VBuffC, VBuffD, NoiseCH1, NoiseCH2
    global MBuff, MBuffX, MBuffY, CHANNELS
    global VmemoryA, VmemoryB, VmemoryC, VmemoryD
    global VUnAvgA, VUnAvgB, UnAvgSav
    global XYlineVA, XYlineVB, XYlineVC, XYlineVD, XYlineM, XYlineMX, XYlineMY
    global MathXString, MathYString, MathAxis, MathXAxis, MathYAxis
    global HoldOff, HoldOffentry
    global X0LXY, Y0TXY, GRWXY, GRHXY
    global YminXY, YmaxXY, XminXY, XmaxXY
    global SHOWsamples, ZOHold, AWGBMode
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global TRACES, TRACESread, RUNstatus
    global Xsignal, YsignalVA, YsignalVB, YsignalVC, YsignalVD, YsignalM, YsignalMX, YsignalMY
    global CHAsbxy, CHBsbxy, CHAOffset, CHBOffset, CHCsbxy, CHDsbxy, CHCOffset, CHDOffset
    global CHAsbxy, CHBsbxy, CHCsbxy, CHDsbxy, CHAxylab, CHBxylab
    global CHAVPosEntryxy, CHBVPosEntryxy, CHCVPosEntryxy, CHDVPosEntryxy
    global CHMXsb, CHMYsb, CHMXPosEntry, CHMYPosEntry
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TimeDiv      # current spin box value
    global SAMPLErate
    global SCstart, MathString
    global TRIGGERsample, TRACEsize, DX
    global TRIGGERlevel, TRIGGERentry, AutoLevel
    global InOffA, InGainA, InOffB, InGainB
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCV3, DCV4
    global HozPoss, HozPossentry
    global CHMOffset, CHMVPosEntry, CHMpdvRange, CHMsb

    # Set the TRACEsize variable
    TRACEsize = int(SHOWsamples - TRIGGERsample) # Set the trace length Don't plot beyond trigger shift point
    SCstart = 0
    yloVA = yloVB = yloVC = yloVD = yloM = yloMX = yloMY = 0.0
    xlo = 0.0
    # get the vertical ranges
    # get the vertical offsets
    # prevent divide by zero error
    try:
        CH1pdvRange = float(eval(CHAsbxy.get()))
    except:
        CH1pdvRange = 0.001
    try:
        CHAOffset = float(eval(CHAVPosEntryxy.get()))
    except:
        CHAOffset = 0.0
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    try:
        CH2pdvRange = float(eval(CHBsbxy.get()))
    except:
        CH2pdvRange = 0.001
    try:
        CHBOffset = float(eval(CHBVPosEntryxy.get()))
    except:
        CHBOffset = 0.0
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    try:
        CH3pdvRange = float(eval(CHCsbxy.get()))
    except:
        CH3pdvRange = 0.001
    try:
        CHCOffset = float(eval(CHCVPosEntryxy.get()))
    except:
        CHCOffset = 0.0
    if CH3pdvRange < 0.001:
        CH3pdvRange = 0.001
    try:
        CH4pdvRange = float(eval(CHDsbxy.get()))
    except:
        CH4pdvRange = 0.001
    try:
        CHDOffset = float(eval(CHDVPosEntryxy.get()))
    except:
        CHDOffset = 0.0
    if CH4pdvRange < 0.001:
        CH4pdvRange = 0.001
    # Math
    CHMpdvRange = UnitConvert(CHMsb.get())
    try:
        CHMOffset = float(eval(CHMVPosEntry.get()))
    except:
        CHMVPosEntry.delete(0,END)
        CHNVPosEntry.insert(0, CHMOffset)
    if CHMpdvRange < 0.001:
        CHMpdvRange = 0.001
    #
    try:
        CHMXpdvRange = float(eval(CHMXsb.get()))
    except:
        CHMXpdvRange = 0.1
    try:
        CHMXOffset = float(eval(CHMXPosEntry.get()))
    except:
        CHMXOffset = 0.0
    try:
        CHMYpdvRange = float(eval(CHMYsb.get()))
    except:
        CHMYpdvRange = 0.1
    try:
        CHMYOffset = float(eval(CHMYPosEntry.get()))
    except:
        CHMYOffset = 0.0
    #
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if Xsignal.get() == 1:
        Xconv1 = float(GRWXY/10.0) / CH1pdvRange    # Horizontal Conversion factors from samples to screen points
    if Xsignal.get() == 3:
        Xconv2 = float(GRWXY/10.0) / CH2pdvRange
    if Xsignal.get() == 2:
        Xconv3 = float(GRWXY/10.0) / CH3pdvRange
    if Xsignal.get() == 4:
        Xconv4 = float(GRWXY/10.0) / CH4pdvRange
    if YsignalVA.get() == 1: # CAV
        Yconv1 = float(GRHXY/10.0) / CH1pdvRange    # Vertical Conversion factors from samples to screen points
    if YsignalVB.get() == 1: # CBV
        Yconv2 = float(GRHXY/10.0) / CH2pdvRange
    if YsignalVC.get() == 1: # CCV
        Yconv3 = float(GRHXY/10.0) / CH3pdvRange
    if YsignalVD.get() == 1: # CDV
        Yconv4 = float(GRHXY/10.0) / CH4pdvRange
    YconvM = float(GRHXY/10.0) / CHMpdvRange
    XconvM = float(GRWXY/10.0) / CHMpdvRange
    XconvMx = float(GRWXY/10.0) / CHMXpdvRange
    YconvMy = float(GRHXY/10.0) / CHMYpdvRange
    YconvMx = float(GRHXY/10.0) / CHMXpdvRange
    XconvMxy = XconvM
# draw an X/Y plot
    XYlineVA = []       # XY Trace lines
    XYlineVB = []
    XYlineVC = []
    XYlineVD = []
    XYlineM = []
    XYlineMX = []
    XYlineMY = []
    t = 0 # int(TRIGGERsample) # skip over sampled before hold off time and trigger point
    c1 = GRHXY / 2.0 + Y0TXY   # fixed correction channel A
    c2 = GRWXY / 2.0 + X0LXY   # Hor correction factor
    while (t < TRACEsize):
        # calculate X axis points
        if Xsignal.get() == 1: # CVA
            xlo = VBuffA[t] - CHAOffset
            xlo = int(c2 + Xconv1 * xlo)
        elif Xsignal.get() == 3: # CVB
            xlo = VBuffB[t] - CHBOffset
            xlo = int(c2 + Xconv2 * xlo)
        elif Xsignal.get() == 2: # CVC
            xlo = VBuffC[t] - CHCOffset
            xlo = int(c2 + Xconv3 * xlo)
        elif Xsignal.get() == 4: # CVD
            xlo = VBuffD[t] - CHCOffset
            xlo = int(c2 + Xconv4 * xlo)
        elif Xsignal.get() == 6: # X-Math
            xlo = MBuffX[t] - CHMXOffset
            xlo = int(c2 + XconvMx * xlo)
        if xlo < XminXY: # clip waveform if going off grid
            xlo  = XminXY
        if xlo > XmaxXY:
            xlo  = XmaxXY
        # calculate Y axis points
        if YsignalVA.get() == 1: # CAV
            yloVA = VBuffA[t] - CHAOffset
            yloVA = int(c1 - Yconv1 * yloVA)
            if yloVA < YminXY: # clip waveform if going off grid
                yloVA  = YminXY
            if yloVA > YmaxXY:
                yloVA  = YmaxXY
            XYlineVA.append(int(xlo))
            XYlineVA.append(int(yloVA))
        if YsignalVB.get() == 1: # CBV
            yloVB = VBuffB[t] - CHBOffset
            yloVB = int(c1 - Yconv2 * yloVB)
            if yloVB < YminXY: # clip waveform if going off grid
                yloVB  = YminXY
            if yloVB > YmaxXY:
                yloVB  = YmaxXY
            XYlineVB.append(int(xlo))
            XYlineVB.append(int(yloVB))
        if YsignalVC.get() == 1: # CCV
            yloVC = VBuffC[t] - CHCOffset
            yloVC = int(c1 - Yconv3 * yloVC)
            if yloVC < YminXY: # clip waveform if going off grid
                yloVC  = YminXY
            if yloVC > YmaxXY:
                yloVC  = YmaxXY
            XYlineVC.append(int(xlo))
            XYlineVC.append(int(yloVC))
        if YsignalVD.get() == 1: # CDV
            yloVD = VBuffB[t] - CHDOffset
            yloVD = int(c1 - Yconv4 * yloVD)
            if yloVD < YminXY: # clip waveform if going off grid
                yloVD  = YminXY
            if yloVD > YmaxXY:
                yloVD  = YmaxXY
            XYlineVD.append(int(xlo))
            XYlineVD.append(int(yloVD))
        if YsignalM.get() == 1: # Math
            yloM = MBuff[t] - CHMOffset
            try:
                yloM = int(c1 - YconvM * yloM)
            except:
                yloM = int(c1)
            if yloM < YminXY: # clip waveform if going off grid
                yloM = YminXY
            if yloM > YmaxXY:
                yloM  = YmaxXY
            XYlineM.append(int(xlo))
            XYlineM.append(int(yloM))
        if YsignalMX.get() == 1: # Math-X
            yloMX = MBuffX[t] - CHMXOffset
            try:
                yloMX = int(c1 - YconvMx * yloMX)
            except:
                yloMX = int(c1)
            if yloMX < YminXY: # clip waveform if going off grid
                yloMX  = YminXY
            if yloMX > YmaxXY:
                yloMX  = YmaxXY
            XYlineMX.append(int(xlo))
            XYlineMX.append(int(yloMX))
        if YsignalMY.get() == 1: # Math-Y
            yloMY = MBuffY[t] - CHMYOffset
            try:
                yloMY = int(c1 - YconvMy * yloMY)
            except:
                yloMY = int(c1)
            if yloMY < YminXY: # clip waveform if going off grid
                yloMY  = YminXY
            if yloMY > YmaxXY:
                yloMY  = YmaxXY
            XYlineMY.append(int(xlo))
            XYlineMY.append(int(yloMY))
        
        t = int(t + 1)
#
## Update the time screen with traces and text   
def MakeTimeScreen():     
    global T1Vline, T2Vline, T3Vline, T4Vline, TXYline # active trave lines
    global TMXline, TMYline, CHANNELS
    global T1VRline, T2VRline, T3VRline, T4VRline # reference trace lines
    global Triggerline, Triggersymbol, Tmathline, TMRline, TXYRline
    global D0line, D1line, D2line, D3line, D4line, D5line, D6line, D7line
    global VBuffA, VBuffB, VBuffC, VBuffD, NoiseCH1, NoiseCH2
    global VmemoryA, VmemoryB, VmemoryC, VmemoryD
    global VUnAvgA, VUnAvgB, UnAvgSav
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global FontSize, Tdiv, ZeroGrid
    global LabelPlotText, PlotLabelText # plot custom label text flag
    global MouseX, MouseY, MouseWidget, MouseCAV, MouseCBV
    global ShowXCur, ShowYCur, TCursor, VCursor
    global SHOWsamples  # Number of samples in data record
    global ShowC1_V, ShowC2_V, Show_MathX, Show_MathY
    global ShowRA_V, ShowRB_V, ShowRC_V, ShowRD_V, ShowMath
    global MathUnits, MathXUnits, MathYUnits
    global Xsignal, Ysignal, MathTrace, MathAxis, MathXAxis, MathYAxis
    global RUNstatus, SingleShot, ManualTrigger, session    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global CHAsb, CHCsb        # V range spinbox Index for channel 1
    global CHBsb, CHDsb        # V range spinbox Index for channel 2
    global CHAOffset, CHCOffset    # Position value for channel 1 V
    global CHBOffset, CHDOffset    # Position value for channel 2 V    
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TimeDiv, Mulx, DISsamples      # current spin box value
    global SAMPLErate, contloop, discontloop, HtMulEntry
    global TRIGGERsample, TRIGGERlevel, HoldOff, HoldOffentry, TgInput
    global COLORgrid, COLORzeroline, COLORtext, COLORtrigger  # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6
    global COLORtraceR1, COLORtraceR2, COLORtraceR3, COLORtraceR4, COLORtraceR5, COLORtraceR6
    global COLORtrace7, COLORtraceR7, COLORtrace8, COLORtraceR8
    global CANVASwidth, CANVASheight
    global TRACErefresh, TRACEmode, TRACEwidth, GridWidth
    global ScreenTrefresh, SmoothCurves, Is_Triggered, TgLabel
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCV3, DCV4, MinV3, MaxV3, MinV4, MaxV4
    global CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
    global SV1, SV2, SV3, SV4, CHABphase, SVA_B
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasDCV3, MeasMinV3, MeasMaxV3, MeasMidV3, MeasPPV3
    global MeasDCV4, MeasMinV4, MeasMaxV4, MeasMidV4, MeasPPV4
    global MeasRMSV1, MeasRMSV2, MeasRMSV3, MeasRMSV4, MeasPhase, MeasRMSVA_B
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global AWGAShape, AWGBShape, MeasDiffAB, MeasDiffBA 
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAVPosEntry, CHMpdvRange, CHMOffset
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global DevID, ser, MarkerNum, MarkerScale, MeasGateLeft, MeasGateRight, MeasGateStatus
    global HozPoss, HozPossentry, First_Slow_sweep, Roll_Mode
    global VABase, VATop, VBBase, VBTop, UserALabel, UserAString, UserBLabel, UserBString
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasUserA, MeasUserB
    global CHBADelayR1, CHBADelayR2, CHBADelayF, MeasDelay
    #
    Ymin = Y0T                  # Minimum position of time grid (top)
    Ymax = Y0T + GRH            # Maximum position of time grid (bottom)

    # DISsamples = (10.0 * TimeDiv) # grid width in time 
    Tstep = (TimeDiv * Tdiv.get()) / GRW # time per pixel
    # get the vertical ranges
    # get the vertical offsets
    # prevent divide by zero error
    if CHANNELS >= 1:
        CH1pdvRange = UnitConvert(CHAsb.get())
        try: # CHA
            CHAOffset = float(eval(CHAVPosEntry.get()))
        except:
            CHAVPosEntry.delete(0,END)
            CHAVPosEntry.insert(0, CHAOffset)
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
    if CHANNELS >= 2:
        CH2pdvRange = UnitConvert(CHBsb.get())
        try: # CHB
            CHBOffset = float(eval(CHBVPosEntry.get()))
        except:
            CHBVPosEntry.delete(0,END)
            CHBVPosEntry.insert(0, CHBOffset)
        if CH2pdvRange < 0.001:
            CH2pdvRange = 0.001
    if CHANNELS >= 3:
        CHCpdvRange = UnitConvert(CHCsb.get())
        try: # CHC
            CHCOffset = float(eval(CHCVPosEntry.get()))
        except:
            CHCVPosEntry.delete(0,END)
            CHCVPosEntry.insert(0, CHCOffset)
        if CHCpdvRange < 0.001:
            CHCpdvRange = 0.001
    if CHANNELS >= 4:
        CHDpdvRange = UnitConvert(CHDsb.get())
        try: # CHD
            CHDOffset = float(eval(CHDVPosEntry.get()))
        except:
            CHDVPosEntry.delete(0,END)
            CHDVPosEntry.insert(0, CHDOffset)
        if CHDpdvRange < 0.001:
            CHDpdvRange = 0.001
    try: # Math
        CHMOffset = float(eval(CHMVPosEntry.get()))
    except:
        CHMVPosEntry.delete(0,END)
        CHNVPosEntry.insert(0, CHMOffset)
    # slide trace left right by HozPoss
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
        HozPoss = 0.0
    vt = HozPoss # invert sign and scale to mSec
    if ScreenTrefresh.get() == 0:
        # Delete all items on the screen
        ca.delete(ALL) # remove all items
        MarkerNum = 0
        # Draw horizontal grid lines
        i = 0
        x1 = X0L
        x2 = X0L + GRW
        mg_siz = GRW/Tdiv.get()
        mg_inc = mg_siz/5.0
        MathFlag1 = (MathAxis == "V-A" and MathTrace.get() == 12) or (MathXAxis == "V-A" and Show_MathX.get() == 1) or (MathYAxis == "V-A" and Show_MathY.get() == 1)
        MathFlag2 = (MathAxis == "V-B" and MathTrace.get() == 12) or (MathXAxis == "V-B" and Show_MathX.get() == 1) or (MathYAxis == "V-B" and Show_MathY.get() == 1)
      # vertical scale text labels
        RightOffset = FontSize * 3
        LeftOffset = int(FontSize/2)
        if (ShowC1_V.get() == 1 or MathTrace.get() == 1 or MathTrace.get() == 2 or MathFlag1):
            ca.create_text(x1-LeftOffset+1, 12, text="CHA", fill=COLORtrace1, anchor="e", font=("arial", FontSize-1 ))
        if (ShowC2_V.get() == 1 or MathTrace.get() == 3 or MathTrace.get() == 10 or MathFlag2):
            ca.create_text(x1-RightOffset-2, 12, text="CHB", fill=COLORtrace2, anchor="e", font=("arial", FontSize-1 )) #26
        if ShowC3_V.get() == 1 and CHANNELS >= 3:
            ca.create_text(x2+LeftOffset, 12, text="CHC", fill=COLORtrace3, anchor="w", font=("arial", FontSize-1 ))
        if ShowC4_V.get() == 1 and CHANNELS >= 4:
            ca.create_text(x2+RightOffset+4, 12, text="CHD", fill=COLORtrace4, anchor="w", font=("arial", FontSize-1 )) #28
        elif MathTrace.get() > 0:
            ca.create_text(x2+RightOffset+20, 12, text="Math", fill=COLORtrace5, anchor="e", font=("arial", FontSize-1 )) #26
        #
        while (i < 11):
            y = Y0T + i * GRH/10.0
            Dline = [x1,y,x2,y]
            if i == 5:
                ca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue line at center of grid
                k = 0
                while (k < Tdiv.get()):
                    l = 1
                    while (l < 5):
                        Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                        ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
            else:
                ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())

            if (ShowC1_V.get() == 1 or MathTrace.get() == 1 or MathTrace.get() == 2 or MathFlag1):
                Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                # Vaxis_label = ' {0:.2f} '.format(Vaxis_value)
                Vaxis_label = str(round(Vaxis_value,3 ))
                ca.create_text(x1-LeftOffset, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
            if CHANNELS >= 2:
                if (ShowC2_V.get() == 1 or MathTrace.get() == 3 or MathTrace.get() == 10 or MathFlag2):
                    Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                    Vaxis_label = str(round(Vaxis_value, 3))
                    ca.create_text(x1-RightOffset-2, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", FontSize )) # 26
            if ShowC3_V.get() == 1 and CHANNELS >= 3:
                Iaxis_value = 1.0 * (((5-i) * CHCpdvRange ) + CHCOffset)
                Iaxis_label = str(round(Iaxis_value, 3))
                ca.create_text(x2+LeftOffset, y, text=Iaxis_label, fill=COLORtrace3, anchor="w", font=("arial", FontSize ))
            if ShowC4_V.get() == 1 and CHANNELS >= 4:
                Iaxis_value = 1.0 * (((5-i) * CHDpdvRange ) + CHDOffset)
                Iaxis_label = str(round(Iaxis_value, 3))
                ca.create_text(x2+RightOffset+4, y, text=Iaxis_label, fill=COLORtrace4, anchor="w", font=("arial", FontSize )) # 28
            if MathTrace.get() > 0:
                Vaxis_value = (((5-i) * CHMpdvRange ) + CHMOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                ca.create_text(x2+RightOffset+20, y, text=Vaxis_label, fill=COLORtrace5, anchor="e", font=("arial", FontSize )) # 26
    
            i = i + 1
        # Draw vertical grid lines
        i = 0
        y1 = Y0T
        y2 = Y0T + GRH
        mg_siz = GRH/10.0
        mg_inc = mg_siz/5.0
        vx = TimeDiv
        
        vt = vx * ZeroGrid.get() # (Tdiv.get()/-2)
        #
        NumLine = Tdiv.get() + 1
        while (i < NumLine):
            x = X0L + i * GRW/Tdiv.get()
            Dline = [x,y1,x,y2]
            if (i == Tdiv.get()/2 ):
                ca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue vertical line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5.0):
                        Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                        ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
    #
                if Roll_Mode.get() == 0: # should be same as First_Slow_sweep == 0
                    axis_value = ((i * vx)+ vt)
                    axis_label = ' {0:.1f} '.format(axis_value) + " nS"
                    if vx >= 1.0:
                        axis_value = ((i * vx)+ vt)
                        axis_label = ' {0:.1f} '.format(axis_value) + " S"
                    if vx < 1.0 and vx >= 0.001:
                        axis_value = ((i * vx) + vt) * 1000
                        axis_label = ' {0:.1f} '.format(axis_value) + " mS"
                    if vx < 0.001:
                        axis_value = ((i * vx) + vt) * 1000000
                        axis_label = ' {0:.1f} '.format(axis_value) + " uS"
                    ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
            else:
                ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                if Roll_Mode.get() == 0: # should be same as First_Slow_sweep == 0
                    axis_value = ((i * vx)+ vt)
                    axis_label = ' {0:.1f} '.format(axis_value) + " nS"
                    if vx >= 1.0:
                        axis_value = ((i * vx)+ vt)
                        axis_label = ' {0:.1f} '.format(axis_value) + " S"
                    if vx < 1.0 and vx >= 0.001:
                        axis_value = ((i * vx) + vt) * 1000
                        axis_label = ' {0:.1f} '.format(axis_value) + " mS"
                    if vx < 0.001:
                        axis_value = ((i * vx) + vt) * 1000000
                        axis_label = ' {0:.1f} '.format(axis_value) + " uS"
                    ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
                        
            i = i + 1
    # Write the trigger line if available
    if Roll_Mode.get() == 0: # Don't show trigger indicator when in Roll Mode
        if len(Triggerline) > 2:                    # Avoid writing lines with 1 coordinate
            ca.create_polygon(Triggerline, outline=COLORtrigger, fill=COLORtrigger, width=1)
            ca.create_line(Triggersymbol, fill=COLORtrigger, width=GridWidth.get())
            if TgInput.get() == 0:
                TgLabel = "None"
            if TgInput.get() == 1:
                TgLabel = "CA-V"
            if TgInput.get() == 2:
                TgLabel = "CB-V"
            if TgInput.get() == 3:
                TgLabel = "CC-V"
            if TgInput.get() == 4:
                TgLabel = "CD-V"
            if TgInput.get() >= 5:
                TgLabel = "Dx"
            if Is_Triggered == 1:
                TgLabel = TgLabel + " Triggered"
            else:
                TgLabel = TgLabel + " Not Triggered"
                if SingleShot.get() > 0:
                    TgLabel = TgLabel + " Armed"
            x = X0L + (GRW/2) + 12
            ca.create_text(x, Ymin-FontSize, text=TgLabel, fill=COLORtrigger, anchor="w", font=("arial", FontSize ))
    # Draw T - V Cursor lines if required
    if MarkerScale.get() == 0:
        Yconv1 = float(GRH/10.0) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORmarker = COLORtrace1
        Units = " V"
    if MarkerScale.get() == 1:
        MouseY = MouseCAV
        Yconv1 = float(GRH/10.0) / CH1pdvRange # CH1pdvRange
        Yoffset1 = CHAOffset
        COLORmarker = COLORtrace1
        Units = " V"
    if MarkerScale.get() == 2:
        MouseY = MouseCBV
        Yconv1 = float(GRH/10.0) / CH2pdvRange
        Yoffset1 = CHBOffset
        COLORmarker = COLORtrace2
        Units = " V"
    if MarkerScale.get() == 3:
        MouseY = MouseCCV
        Yconv1 = float(GRH/10.0) / CHCpdvRange
        Yoffset1 = CHCOffset
        COLORmarker = COLORtrace3
        Units = " V"
    if MarkerScale.get() == 4:
        MouseY = MouseCDV
        Yconv1 = float(GRH/10.0) / CHDpdvRange
        Yoffset1 = CHDOffset
        COLORmarker = COLORtrace4
        Units = " V"
#
    if ShowTCur.get() > 0:
        # vx = Tstep
        Dline = [TCursor, Y0T, TCursor, Y0T+GRH]
        ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
        vt = TimeDiv * ZeroGrid.get() # (Tdiv.get()/-2)
        Tpoint = ((TCursor - X0L) * Tstep) + vt # 
        V_label = ' {0:.1f} '.format(Tpoint) + " nS"
        if Tpoint >= 1.0:
            V_label = ' {0:.1f} '.format(Tpoint) + " S"
        if Tpoint < 1.0 and Tpoint >= 0.001:
            axis_value = Tpoint * 1000
            V_label = ' {0:.1f} '.format(axis_value) + " mS"
        if Tpoint < 0.001:
            axis_value = Tpoint * 1000000
            V_label = ' {0:.1f} '.format(axis_value) + " uS"
        if Roll_Mode.get() == 0: # should be same as First_Slow_sweep == 0
            ca.create_text(TCursor, Y0T+GRH+6, text=V_label, fill=COLORtext, anchor="n", font=("arial", FontSize ))
    if ShowVCur.get() > 0:
        Dline = [X0L, VCursor, X0L+GRW, VCursor]
        ca.create_line(Dline, dash=(4,3), fill=COLORmarker, width=GridWidth.get())
        c1 = GRH / 2 + Y0T    # fixed Y correction 
        yvolts = ((VCursor-c1)/Yconv1) - Yoffset1
        V1String = ' {0:.3f} '.format(-yvolts)
        V_label = V1String + Units
        ca.create_text(X0L+GRW+2, VCursor, text=V_label, fill=COLORmarker, anchor="w", font=("arial", FontSize ))
    if ShowTCur.get() == 0 and ShowVCur.get() == 0 and MouseWidget == ca:
        if MouseX > X0L and MouseX < X0L+GRW and MouseY > Y0T and MouseY < Y0T+GRH:
            Dline = [MouseX, Y0T, MouseX, Y0T+GRH]
            ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            ca.create_oval(MouseX-GridWidth.get(), MouseY-GridWidth.get(), MouseX+GridWidth.get(), MouseY+GridWidth.get(), outline=COLORtrigger, fill=COLORtrigger, width=GridWidth.get())
            # vx = Tstep
            vt = TimeDiv * ZeroGrid.get() # (Tdiv.get()/-2)
            Tpoint = ((MouseX - X0L) * Tstep) + vt #
            V_label = ' {0:.1f} '.format(Tpoint) + " nS"
            if Tpoint >= 1.0:
                V_label = ' {0:.1f} '.format(Tpoint) + " S"
            if Tpoint < 1.0 and Tpoint >= 0.001:
                axis_value = Tpoint * 1000
                V_label = ' {0:.1f} '.format(axis_value) + " mS"
            if Tpoint < 0.001:
                axis_value = Tpoint * 1000000
                V_label = ' {0:.1f} '.format(axis_value) + " uS"
            if Roll_Mode.get() == 0: # should be same as First_Slow_sweep == 0
                ca.create_text(MouseX, Y0T+GRH+6, text=V_label, fill=COLORtext, anchor="n", font=("arial", FontSize ))
            Dline = [X0L, MouseY, X0L+GRW, MouseY]
            ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            c1 = GRH / 2 + Y0T    # fixed Y correction 
            yvolts = ((MouseY-c1)/Yconv1) - Yoffset1
            V1String = ' {0:.3f} '.format(-yvolts)
            V_label = V1String + Units
            ca.create_text(X0L+GRW+2, MouseY, text=V_label, fill=COLORmarker, anchor="w", font=("arial", FontSize ))
#
    if MeasGateStatus.get() == 1:
        LeftGate = X0L + MeasGateLeft / Tstep
        RightGate = X0L + MeasGateRight / Tstep
        ca.create_line(LeftGate, Y0T, LeftGate, Y0T+GRH, dash=(5,3), width=GridWidth.get(), fill=COLORtrace5)
        ca.create_line(RightGate, Y0T, RightGate, Y0T+GRH, dash=(5,3), width=GridWidth.get(), fill=COLORtrace7)
        #
        # TString = ' {0:.2f} '.format(Tpoint)
        if Roll_Mode.get() == 0: # should be same as First_Slow_sweep == 0
            DeltaT = ' ? '
            DT = (MeasGateRight-MeasGateLeft)
            if DT == 0.0:
                DT = 1.0
            if DT >= 1:
                axis_value = DT
                DeltaT = ' {0:.2f} '.format(axis_value) + " S "
            if DT < 1.0 and DT >= 0.001:
                axis_value = DT * 1000.0
                DeltaT = ' {0:.2f} '.format(axis_value) + " mS "
            if DT < 0.001:
                axis_value = DT * 1000000.0
                DeltaT = ' {0:.2f} '.format(axis_value) + " uS "
            # DeltaT = ' {0:.3f} '.format(Tpoint-PrevT)
            DF = (1.0/DT)
            if DF < 1000:
                DFreq = ' {0:.2f} '.format(DF) + " Hz "
            if DF > 1000 and DF < 1000000:
                DFreq = ' {0:.1f} '.format(DF/1000) + " KHz "
            if DF > 1000000:
                DFreq = ' {0:.1f} '.format(DF/1000000) + " MHz "
            #
            V_label = " Delta T" + DeltaT
            V_label = V_label + ", Freq " + DFreq
        # place in upper left unless specified otherwise
        TxScale = FontSize + 2
        x = X0L + 5
        y = Y0T + 7
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0L + GRW - 5
            y = Y0T + 7
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0L + 5
            y = Y0T + GRH + 7 - (MarkerNum*TxScale)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0L + GRW - 5
            y = Y0T + GRH + 7
            Justify = 'e'
        ca.create_text(x, y, text=V_label, fill=COLORtrace5, anchor=Justify, font=("arial", FontSize ))
        #
#
    SmoothBool = SmoothCurves.get()
    # Write the traces if available
    if len(T1Vline) > 4: # Avoid writing lines with 1 coordinate    
        ca.create_line(T1Vline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())   # Write the voltage trace 1
    if len(T2Vline) > 4: # Write the trace 2 if active
        ca.create_line(T2Vline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(T3Vline) > 4: # Avoid writing lines with 1 coordinate    
        ca.create_line(T3Vline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())   # Write the voltage trace 1
    if len(T4Vline) > 4: # Write the trace 2 if active
        ca.create_line(T4Vline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(Tmathline) > 4 and MathTrace.get() > 0: # Write Math tace if active
        ca.create_line(Tmathline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TMXline) > 4 : # Write X Math tace if active
        ca.create_line(TMXline, fill=COLORtrace6, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TMYline) > 4 : # Write Y Math tace if active
        ca.create_line(TMYline, fill=COLORtrace7, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D0line) > 4 : # Write D0 tace if active
        ca.create_line(D0line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D1line) > 4 : # Write D1 tace if active
        ca.create_line(D1line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D2line) > 4 : # Write D2 tace if active
        ca.create_line(D2line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D3line) > 4 : # Write D3 tace if active
        ca.create_line(D3line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D4line) > 4 : # Write D4 tace if active
        ca.create_line(D4line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D5line) > 4 : # Write D5 tace if active
        ca.create_line(D5line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D6line) > 4 : # Write D6 tace if active
        ca.create_line(D6line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(D7line) > 4 : # Write D7 tace if active
        ca.create_line(D7line, fill=COLORtrace8, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRA_V.get() == 1 and len(T1VRline) > 4:
        ca.create_line(T1VRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRB_V.get() == 1 and len(T2VRline) > 4:
        ca.create_line(T2VRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRC_V.get() == 1 and len(T3VRline) > 4:
        ca.create_line(T3VRline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRD_V.get() == 1 and len(T4VRline) > 4:
        ca.create_line(T3VRline, fill=COLORtraceR4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMath.get() == 1 and len(TMRline) > 4:
        ca.create_line(TMRline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    # General information on top of the grid
    # Sweep information
    sttxt = " "
    if TRACEmodeTime.get() == 1:
        sttxt = sttxt + " Averaging"
    if ManualTrigger.get() == 1:
        sttxt = "Manual Trigger"
    if (RUNstatus.get() == 0) or (RUNstatus.get() == 3):
        sttxt = "Stopped"
    if ScreenTrefresh.get() == 1:
        sttxt = sttxt + " Persistance ON"
        # Delete text at bottom of screen
        de = ca.find_enclosed( X0L-1, Y0T+GRH+12, CANVASwidth, Y0T+GRH+100)
        for n in de: 
            ca.delete(n)
        # Delete text at top of screen
        de = ca.find_enclosed( X0L-1, -1, CANVASwidth, 20)
        for n in de: 
            ca.delete(n)
    if Roll_Mode.get() == 0:
        SR_label = ' {0:.1f} '.format(SAMPLErate)
        if LabelPlotText.get() > 0:
            txt = PlotLabelText + " Sample rate: " + SR_label + " " + sttxt
        else:
            txt = "Device ID " + DevID + " Sample rate: " + SR_label + " # Samples: " + str(SHOWsamples)+ " " + sttxt
    else:
        if LabelPlotText.get() > 0:
            txt = PlotLabelText + " Rolling Sweep " + sttxt
        else:
            txt = "Device ID " + DevID + " Rolling Sweep " + sttxt
    x = X0L+2
    y = 15
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    # digital I/O indicators
    x2 = X0L + GRW
    BoxColor = "#808080"   # gray
    # Time sweep information and view at information
    vx = TimeDiv
    if vx >= 1:
        txt = ' {0:.2f} '.format(vx) + " S/div"
    if vx < 1 and vx >= 0.001:
        txt = ' {0:.2f} '.format(vx * 1000.0) + " mS/div"
    if vx < 0.001:
        txt = ' {0:.2f} '.format(vx * 1000000.0) + " uS/div"

    txt = txt + "  "
    #
    txt = txt + "View at "
    if abs(vt) >= 1:
        txt = txt + ' {0:.2f} '.format(vt) + " S "
    if abs(vt) < 1 and abs(vt) >= 0.001:
        txt = txt + ' {0:.2f} '.format(vt * 1000) + " mS "
    if abs(vt) < 0.001:
        txt = txt + ' {0:.2f} '.format(vt * 1000000.0) + " uS "
    # print period and frequency of displayed channels
    if ShowC1_V.get() == 1 or ShowC2_V.get() == 1:
        if MeasGateStatus.get() == 1:
            if (MeasGateRight-MeasGateLeft) > 0:
                hldn = int(MeasGateLeft * SAMPLErate)
                Endsample = int(MeasGateRight * SAMPLErate)
                if Endsample <= hldn:
                    Endsample = hldn + 2
                FindRisingEdge(VBuffA[hldn:Endsample],VBuffB[hldn:Endsample])
        else:
            FindRisingEdge(VBuffA,VBuffB)
        if ShowC1_V.get() == 1 and CHANNELS >= 1:
            if MeasAHW.get() == 1:
                txt = txt + " CA Hi Width = " + ' {0:.3f} '.format(CHAHW) + " mS "
            if MeasALW.get() == 1:
                txt = txt + " CA Lo Width = " + ' {0:.3f} '.format(CHALW) + " mS "
            if MeasADCy.get() == 1:
                txt = txt + " CA DutyCycle = " + ' {0:.1f} '.format(CHADCy) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " CA Period = " + ' {0:.3f} '.format(CHAperiod) + " mS "
            if MeasAFREQ.get() == 1:
                txt = txt + " CA Freq = "
                ChaF = CHAfreq
                if ChaF < 1000:
                    V1String = ' {0:.1f} '.format(ChaF)
                    txt = txt + str(V1String) + " Hz "
                if ChaF > 1000 and ChaF < 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000)
                    txt = txt + str(V1String) + " KHz "
                if ChaF > 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000000)
                    txt = txt + str(V1String) + " MHz "
                #
        if ShowC2_V.get() == 1 and CHANNELS >= 2:
            if MeasBHW.get() == 1:
                txt = txt + " CB Hi Width = " + ' {0:.3f} '.format(CHBHW) + " mS "
            if MeasBLW.get() == 1:
                txt = txt + " CB Lo Width = " + ' {0:.3f} '.format(CHBLW) + " mS "
            if MeasBDCy.get() == 1:
                txt = txt + " CB DutyCycle = " + ' {0:.1f} '.format(CHBDCy) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " CB Period = " + ' {0:.3f} '.format(CHBperiod) + " mS "
            if MeasBFREQ.get() == 1:
                txt = txt + " CB Freq = "
                ChaF = CHBfreq
                if ChaF < 1000:
                    V1String = ' {0:.1f} '.format(ChaF)
                    txt = txt + str(V1String) + " Hz "
                if ChaF > 1000 and ChaF < 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000)
                    txt = txt + str(V1String) + " KHz "
                if ChaF > 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000000)
                    txt = txt + str(V1String) + " MHz "
                #

    x = X0L
    y = Y0T+GRH+int(2.5 *FontSize) # 20
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    if MeasTopV1.get() == 1 or MeasBaseV1.get() == 1 or MeasTopV2.get() == 1 or MeasBaseV2.get() == 1:
        MakeHistogram()
    txt = " "
    if ShowC1_V.get() == 1 and CHANNELS >= 1:
    # Channel A information
        txt = "CHA: "
        txt = txt + str(CH1pdvRange) + " V/div"
        if MeasDCV1.get() == 1: 
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV1)
        if MeasMaxV1.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV1)
        if MeasTopV1.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VATop)
        if MeasMinV1.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV1)
        if MeasBaseV1.get() == 1:
            txt = txt +  " Base = " + ' {0:.4f} '.format(VABase)
        if MeasMidV1.get() == 1:
            MidV1 = (MaxV1+MinV1)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV1)
        if MeasPPV1.get() == 1:
            PPV1 = MaxV1-MinV1
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV1)
        if MeasRMSV1.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV1)
        if MeasRMSVA_B.get() == 1:
            txt = txt +  " A-B RMS = " + ' {0:.4f} '.format(SVA_B)
        if MeasDiffAB.get() == 1:
            txt = txt +  " A-B = " + ' {0:.4f} '.format(DCV1-DCV2)
        if MeasUserA.get() == 1:
            try:
                TempValue = eval(UserAString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserALabel + " = " + V1String
    if ShowC3_V.get() == 1 and CHANNELS >= 3:
        txt = txt + "CHC: "
        txt = txt + str(CHCpdvRange) + " V/div"
        if MeasDCV3.get() == 1: 
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV3)
        if MeasMaxV3.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV3)
        if MeasMinV3.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV3)
        if MeasMidV3.get() == 1:
            MidV3 = (MaxV3+MinV3)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV3)
        if MeasPPV3.get() == 1:
            PPV3 = MaxV3-MinV3
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV3)
        if MeasRMSV3.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV3)
    x = X0L
    y = Y0T+GRH+(4*FontSize) # 32
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    txt= " "
    # Channel B information
    if ShowC2_V.get() == 1 and CHANNELS >= 2:
        txt = "CHB: "
        txt = txt + str(CH2pdvRange) + " V/div"
        if MeasDCV2.get() == 1:
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV2)
        if MeasMaxV2.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV2)
        if MeasTopV2.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VBTop)
        if MeasMinV2.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV2)
        if MeasBaseV2.get() == 1:
            txt = txt +  " Base = " + ' {0:.4f} '.format(VBBase)
        if MeasMidV2.get() == 1:
            MidV2 = (MaxV2+MinV2)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV2)
        if MeasPPV2.get() == 1:
            PPV2 = MaxV2-MinV2
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV2)
        if MeasRMSV2.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV2)
        if MeasDiffBA.get() == 1:
            txt = txt +  " B-A = " + ' {0:.4f} '.format(DCV2-DCV1)
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String
    if ShowC4_V.get() == 1 and CHANNELS >= 4:
        txt = txt + "CHD: "
        txt = txt + str(CHDpdvRange) + " V/div"
        if MeasDCV4.get() == 1: 
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV4)
        if MeasMaxV4.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV4)
        if MeasMinV4.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV4)
        if MeasMidV4.get() == 1:
            MidV4 = (MaxV4+MinV4)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV4)
        if MeasPPV4.get() == 1:
            PPV4 = MaxV4-MinV4
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV4)
        if MeasRMSV4.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV4)       
    x = X0L
    y = Y0T+GRH+int(5.5*FontSize) # 44
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
#
## Update the XY screen traces and text
def MakeXYScreen():
    global XYlineVA, XYlineVB, XYlineVC, XYlineVD, XYlineM, XYlineMX, XYlineMY # active trave lines
    global Tmathline, TMRline, XYRlineVA, XYRlineVB, XYRlineM, XYRlineMX, XYRlineMY
    global X0LXY         # Left top X value
    global Y0TXY          # Left top Y value
    global GRWXY          # Screenwidth
    global GRHXY          # Screenheight
    global FontSize, LabelPlotText, PlotLabelText
    global XYca, MouseX, MouseY, MouseWidget
    global ShowXCur, ShowYCur, XCursor, YCursor, CHANNELS
    global SHOWsamples  # Number of samples in data record
    global ShowMath, MathUnits, MathXUnits, MathYUnits
    global Xsignal, MathAxis, MathXAxis, MathYAxis
    global YsignalVA, YsignalVC, YsignalVB, YsignalVD, YsignalM, YsignalMY, YsignalMX
    global XYRefAV, XYRefC, XYRefBV, XYRefD, XYRefM, XYRefMX, XYRefMY
    global RUNstatus, SingleShot, ManualTrigger    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global CHAsbxy, CHBsbxy, CHCsbxy, CHDsbxy      # spinbox Index 
    global CHAOffset, CHBOffset, CHCOffset, CHDOffset    # Offset values     
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TimeDiv      # current spin box value
    global SAMPLErate
    global TRIGGERsample, TRIGGERlevel
    global COLORgrid, COLORzeroline, COLORtext, COLORtrigger, COLORtrace6, COLORtrace7 # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5
    global COLORtraceR1, COLORtraceR2, COLORtraceR3, COLORtraceR4, COLORtraceR5, COLORtraceR6, COLORtraceR7
    global CANVASwidthXY, CANVASheightXY, COLORXmarker, COLORYmarker
    global TRACErefresh, TRACEmode, TRACEwidth, GridWidth
    global ScreenXYrefresh, SmoothCurves
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2, CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
    global SV1, SI1, SV2, SI2, CHABphase
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasRMSV1, MeasRMSV2, MeasPhase
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global AWGAShape
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAVPosEntry
    global CHMsb, CHMXsb, CHMYsb, CHMVPosEntry, CHMXPosEntry, CHMYPosEntry
    global XY1pdvRange, XYAOffset, XY2pdvRange, XYBOffset
    global CHMpdvRange, CHMOffset
    global DevID, MarkerNum, MarkerScale
    global HozPoss, HozPossentry
    global HistAsPercent, VBuffA, VBuffB, HBuffA, HBuffB, NoiseCH1, NoiseCH2
    global VABase, VATop, VBBase, VBTop, UserALabel, UserAString, UserBLabel, UserBString
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasUserA, MeasUserB
    #
    Ymin = Y0TXY                # Minimum position of screen grid (top)
    Ymax = Y0TXY + GRHXY        # Maximum position of screen grid (bottom)
    RightOffset = FontSize * 3
    LeftOffset = int(FontSize/2)
#
    MXOffset = MYOffset = 0
    MXpdvRange = MYpdvRange = 0.5
    if CHANNELS >= 1:
        try:
            XY1pdvRange = float(eval(CHAsbxy.get()))
        except:
            CHAsbxy.delete(0,END)
            CHAsbxy.insert(0, XY1pdvRange)
        # get the vertical offsets
        try:
            XYAOffset = float(eval(CHAVPosEntryxy.get()))
        except:
            CHAVPosEntryxy.delete(0,END)
            CHAVPosEntryxy.insert(0, XYAOffset)
    if CHANNELS >= 2:
        try:
            XY2pdvRange = float(eval(CHBsbxy.get()))
        except:
            CHBsbxy.delete(0,END)
            CHBsbxy.insert(0, XY2pdvRange)
        try:
            XYBOffset = float(eval(CHBVPosEntryxy.get()))
        except:
            CHBVPosEntry.delete(0,END)
            CHBVPosEntry.insert(0, XYBOffset)
    if CHANNELS >= 3:
        try:
            XY3pdvRange = float(eval(CHCsbxy.get()))
        except:
            CHCsbxy.delete(0,END)
            CHCsbxy.insert(0, XY3pdvRange)
        try:
            XYCOffset = float(eval(CHCVPosEntryxy.get()))
        except:
            CHCVPosEntry.delete(0,END)
            CHCVPosEntry.insert(0, XYCOffset)
    if CHANNELS >= 4:
        try:
            XY4pdvRange = float(eval(CHDsbxy.get()))
        except:
            CHDsbxy.delete(0,END)
            CHDsbxy.insert(0, XY4pdvRange)
        try:
            XYDOffset = float(eval(CHDVPosEntryxy.get()))
        except:
            CHDVPosEntry.delete(0,END)
            CHDVPosEntry.insert(0, XYDOffset)
# Math
    CHMpdvRange = UnitConvert(CHMsb.get())
    try:
        CHMOffset = float(eval(CHMVPosEntry.get()))
    except:
        CHMVPosEntry.delete(0,END)
        CHNVPosEntry.insert(0, CHMOffset)
    if CHMpdvRange < 0.001:
        CHMpdvRange = 0.001
    #
    try:
        MXpdvRange = float(eval(CHMXsb.get()))
    except:
        CHMXsb.delete(0,END)
        CHMXsb.insert(0, MMpdvRange)
    try:
        MYpdvRange = float(eval(CHMYsb.get()))
    except:
        CHMYsb.delete(0,END)
        CHMYsb.insert(0, MYpdvRange)
    try:
        MXOffset = float(eval(CHMXPosEntry.get()))
    except:
        CHMXPosEntry.delete(0,END)
        CHMXPosEntry.insert(0, MXOffset)
    try:
        MYOffset = float(eval(CHMYPosEntry.get()))
    except:
        CHMYPosEntry.delete(0,END)
        CHMYPosEntry.insert(0, MYOffset)
    #
    # prevent divide by zero error
    if XY1pdvRange < 0.001:
        XY1pdvRange = 0.001
    if XY2pdvRange < 0.001:
        XY2pdvRange = 0.001
    if MXpdvRange < 0.001:
        MXpdvRange = 0.001
    if MYpdvRange < 0.001:
        MYpdvRange = 0.001
    # If drawing histograms adjust offset based on range such that bottom grid is zero
    if ScreenXYrefresh.get() == 0:
        # Delete all items on the screen
        MarkerNum = 0
        XYca.delete(ALL) # remove all items
        # Draw horizontal grid lines
        i = 0
        x1 = X0LXY
        x2 = X0LXY + GRWXY
        mg_siz = GRWXY/10.0
        mg_inc = mg_siz/5.0
        while (i < 11):
            y = Y0TXY + i * GRHXY/10.0
            Dline = [x1,y,x2,y]
            if i == 5:
                XYca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5):
                        Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                        XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
            else:
                XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            if YsignalVA.get() == 1:
                Vaxis_value = (((5-i) * XY1pdvRange ) + XYAOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                XYca.create_text(x1-LeftOffset, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
            if YsignalVB.get() == 1:
                Vaxis_value = (((5-i) * XY2pdvRange ) + XYBOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                XYca.create_text(x1-RightOffset, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", FontSize ))
            if YsignalVC.get() == 1:
                Vaxis_value = (((5-i) * XY3pdvRange ) + XYCOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                XYca.create_text(x2+LeftOffset, y, text=Vaxis_label, fill=COLORtrace3, anchor="w", font=("arial", FontSize ))
            if YsignalM.get() == 1:
                TempCOLOR = COLORtrace5
                if MathTrace.get() == 2:
                    Vaxis_value = (((5-i) * CHMpdvRange ) + CHMOffset)
                else:
                    Vaxis_value = (((5-i) * CHMpdvRange ) + CHMOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                XYca.create_text(x1-LeftOffset, y, text=Vaxis_label, fill=TempCOLOR, anchor="e", font=("arial", FontSize ))
            if YsignalMX.get() == 1:
                TempCOLOR = COLORtrace6
                Vaxis_value = (((5-i) * MXpdvRange ) + MXOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                XYca.create_text(x2+LeftOffset, y, text=Vaxis_label, fill=TempCOLOR, anchor="w", font=("arial", FontSize )) 
            if YsignalMY.get() == 1:
                TempCOLOR = COLORtrace7
                Vaxis_value = (((5-i) * MYpdvRange ) + MYOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                XYca.create_text(x2+RightOffset, y, text=Vaxis_label, fill=TempCOLOR, anchor="w", font=("arial", FontSize ))
            i = i + 1
        # Draw vertical grid lines
        i = 0
        y1 = Y0TXY
        y2 = Y0TXY + GRHXY
        mg_siz = GRHXY/10.0
        mg_inc = mg_siz/5.0
        # 
        while (i < 11):
            x = X0LXY + i * GRWXY/10.0
            Dline = [x,y1,x,y2]
            if (i == 5):
                XYca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue vertical line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5):
                        Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                        XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
                if Xsignal.get() == 1: # 
                    Vaxis_value = (((i-5) * XY1pdvRange ) + XYAOffset)
                    Vaxis_label = str(round(Vaxis_value, 3))
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", FontSize ))
                elif Xsignal.get() == 3:
                    Vaxis_value = (((i-5) * XY2pdvRange ) + XYBOffset)
                    Vaxis_label = str(round(Vaxis_value, 3))
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", FontSize ))
                elif Xsignal.get() == 6:
                    TempCOLOR = COLORtrace6
                    if MathTrace.get() == 2:
                        Vaxis_value = (((i-5) * XY1pdvRange ) + XYAOffset)
                    elif MathTrace.get() == 3:
                        Vaxis_value = (((i-5) * XY2pdvRange ) + XYBOffset)
                    else:
                        if MathXAxis == "V-A":
                            Vaxis_value = (((i-5) * XY1pdvRange ) + XYAOffset)
                            TempCOLOR = COLORtrace1
                        elif MathXAxis == "V-B":
                            Vaxis_value = (((i-5) * XY2pdvRange ) + XYBOffset)
                            TempCOLOR = COLORtrace2
                        else:
                            Vaxis_value = (((i-5) * MXpdvRange ) + MXOffset) # XY1pdvRange XYAOffset)
                            TempCOLOR = COLORtrace6
                    Vaxis_label = str(round(Vaxis_value, 3))
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=TempCOLOR, anchor="n", font=("arial", FontSize ))
            else:
                XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                if Xsignal.get() == 1:
                    Vaxis_value = (((i-5) * XY1pdvRange ) + XYAOffset)
                    Vaxis_label = str(round(Vaxis_value, 3))
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", FontSize ))
                elif Xsignal.get() == 3:
                    Vaxis_value = (((i-5) * XY2pdvRange ) + XYBOffset)
                    Vaxis_label = str(round(Vaxis_value, 3))
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", FontSize ))
                elif Xsignal.get() == 6:
                    TempCOLOR = COLORtrace6
                    if MathTrace.get() == 2:
                        Vaxis_value = (((i-5) * XY1pdvRange ) + XYAOffset)
                    elif MathTrace.get() == 3:
                        Vaxis_value = (((i-5) * XY2pdvRange ) + XYBOffset)
                    else:
                        if MathXAxis == "V-A":
                            Vaxis_value = (((i-5) * XY1pdvRange ) + XYAOffset)
                            TempCOLOR = COLORtrace1
                        elif MathXAxis == "V-B":
                            Vaxis_value = (((i-5) * XY2pdvRange ) + XYBOffset)
                            TempCOLOR = COLORtrace2
                        else:
                            Vaxis_value = (((i-5) * MXpdvRange ) + MXOffset) # CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(round(Vaxis_value, 3))
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=TempCOLOR, anchor="n", font=("arial", FontSize ))
            i = i + 1
# Draw traces
# Avoid writing lines with 1 coordinate
    if YsignalVA.get() == 1:
        if len(XYlineVA) > 4:
            XYca.create_line(XYlineVA, fill=COLORtrace1, width=TRACEwidth.get())
    if YsignalVB.get() == 1:
        if len(XYlineVB) > 4:
            XYca.create_line(XYlineVB, fill=COLORtrace2, width=TRACEwidth.get())
    if YsignalVC.get() == 1:
        if len(XYlineVC) > 4:
            XYca.create_line(XYlineVC, fill=COLORtrace3, width=TRACEwidth.get())
    if YsignalVD.get() == 1:
        if len(XYlineVD) > 4:
            XYca.create_line(XYlineVD, fill=COLORtrace4, width=TRACEwidth.get())
    if YsignalM.get() == 1: #  or Ysignal.get() == 5:
        if len(XYlineM) > 4:
            XYca.create_line(XYlineM, fill=COLORtrace5, width=TRACEwidth.get())
    if YsignalMX.get() == 1:
        if len(XYlineMX) > 4:
            XYca.create_line(XYlineMX, fill=COLORtrace6, width=TRACEwidth.get())
    if YsignalMY.get() == 1:
        if len(XYlineMY) > 4:
            XYca.create_line(XYlineMY, fill=COLORtrace7, width=TRACEwidth.get())
    if len(XYRlineVA) > 4 and XYRefAV.get() == 1:
        XYca.create_line(XYRlineVA, fill=COLORtraceR1, width=TRACEwidth.get())
    if len(XYRlineVB) > 4 and XYRefBV.get() == 1:
        XYca.create_line(XYRlineVB, fill=COLORtraceR2, width=TRACEwidth.get())
    if len(XYRlineM) > 4 and XYRefM.get() == 1:
        XYca.create_line(XYRlineM, fill=COLORtraceR5, width=TRACEwidth.get())
    if len(XYRlineMX) > 4 and XYRefMX.get() == 1:
        XYca.create_line(XYRlineMX, fill=COLORtraceR6, width=TRACEwidth.get())
    if len(XYRlineMY) > 4 and XYRefMY.get() == 1:
        XYca.create_line(XYRlineMY, fill=COLORtraceR7, width=TRACEwidth.get())
# Draw Histogram Traces
    if  Xsignal.get() == 8:
        MakeHistogram()
        b = 0
        Yconv1 = float(GRHXY/10.0) / XY2pdvRange
        Xconv1 = float(GRWXY/10.0) / XY1pdvRange
        y1 = Y0TXY + GRHXY
        c2 = GRWXY / 2.0 + X0LXY   # Hor correction factor
        while b < 4999: #
            if HistAsPercent == 1: # convert to percent of total sample count
                ylo = float(HBuffA[0][b]) / len(VBuffA)
                ylo = ylo * 100.0
            else:
                ylo = HBuffA[0][b] #
            ylo = int(y1 - (Yconv1 * ylo))
            if ylo >  Ymax:
                ylo = Ymax
            if ylo < Ymin:
                ylo = Ymin
            xlo = HBuffA[1][b] - CHAOffset
            xlo = int(c2 + Xconv1 * xlo)
            Dline = [xlo,y1,xlo,ylo]
            XYca.create_line(Dline, fill=COLORtrace1, width=TRACEwidth.get())
            b = b + 1
    if  Xsignal.get() == 9:
        MakeHistogram()
        b = 0
        Yconv1 = float(GRHXY/10.0) / XY1pdvRange
        Xconv1 = float(GRWXY/10.0) / XY2pdvRange
        y1 = Y0TXY + GRHXY
        c2 = GRWXY / 2.0 + X0LXY   # Hor correction factor
        while b < 4999: #
            if HistAsPercent == 1: # convert to percent
                ylo = float(HBuffB[0][b]) / len(VBuffB)
                ylo = ylo * 100.0
            else:
                ylo = HBuffB[0][b]
            ylo = int(y1 - Yconv1 * ylo)
            if ylo >  Ymax:
                ylo = Ymax
            if ylo < Ymin:
                ylo = Ymin
            xlo = HBuffB[1][b] - CHBOffset
            xlo = int(c2 + Xconv1 * xlo)
            Dline = [xlo,y1,xlo,ylo]
            XYca.create_line(Dline, fill=COLORtrace2, width=TRACEwidth.get())
            b = b + 1
# Draw X - Y Cursor lines if required
    COLORXmarker = COLORtrace1
    COLORYmarker = COLORtrace2
    Xconv1 = float(GRWXY/10) / XY1pdvRange
    Xoffset1 = CHAOffset
    X_label = " V"
    if Xsignal.get() == 1 or Xsignal.get() == 6:
        Xconv1 = float(GRWXY/10) / XY1pdvRange
        Xoffset1 = CHAOffset
        COLORXmarker = COLORtrace1
        X_label = " V"
    if Xsignal.get() == 3 or Xsignal.get() == 7:
        Xconv1 = float(GRWXY/10) / XY2pdvRange
        Xoffset1 = CHBOffset
        COLORXmarker = COLORtrace2
        X_label = " V"
    if Xsignal.get() == 5:
        X_label = MathXUnits
        if MathXAxis == "V-A":
            Xconv1 = float(GRWXY/10) / XY1pdvRange
            Xoffset1 = CHAOffset
            COLORXmarker = COLORtrace1
        elif MathXAxis == "V-B":
            Xconv1 = float(GRWXY/10) / XY2pdvRange
            Xoffset1 = CHBOffset
            COLORXmarker = COLORtrace2
        else:
            Xconv1 = float(GRWXY/10) / XY1pdvRange
            Xoffset1 = CHAOffset
            COLORXmarker = COLORtrace1
# Set variables just incase
    Yconv1 = float(GRHXY/10.0) / XY1pdvRange
    Yoffset1 = CHAOffset
    Y_label = " V"
    if YsignalVA.get() == 1 or YsignalM.get() == 1:
        Yconv1 = float(GRHXY/10.0) / XY1pdvRange
        Yoffset1 = CHAOffset
        COLORYmarker = COLORtrace1
        Y_label = " V"
    if YsignalVB.get() == 1 or YsignalM.get() == 1:
        Yconv1 = float(GRHXY/10.0) / XY2pdvRange
        Yoffset1 = CHBOffset
        COLORYmarker = COLORtrace2
        Y_label = " V"
    if YsignalM.get() == 1 or YsignalMX.get() == 1 or YsignalMY.get() == 1:
        Y_label = MathYUnits
        if MathYAxis == "V-A":
            Yconv1 = float(GRHXY/10.0) / XY1pdvRange
            Yoffset1 = CHAOffset
            COLORYmarker = COLORtrace1
        elif MathYAxis == "V-B":
            Yconv1 = float(GRHXY/10.0) / XY2pdvRange
            Yoffset1 = CHBOffset
            COLORYmarker = COLORtrace2
        else:
            Yconv1 = float(GRHXY/10.0) / XY1pdvRange
            Yoffset1 = CHAOffset
            COLORYmarker = COLORtrace1
    if ShowXCur.get() > 0:
        Dline = [XCursor, Y0TXY, XCursor, Y0TXY+GRHXY]
        XYca.create_line(Dline, dash=(4,3), fill=COLORXmarker, width=GridWidth.get())
        c1 = GRWXY / 2.0 + X0LXY    # fixed X correction 
        xvolts = Xoffset1 - ((c1-XCursor)/Xconv1)
        XString = ' {0:.3f} '.format(xvolts)
        V_label = XString + X_label
        XYca.create_text(XCursor+1, YCursor-5, text=V_label, fill=COLORXmarker, anchor="w", font=("arial", FontSize ))
    if ShowYCur.get() > 0:
        Dline = [X0LXY, YCursor, X0LXY+GRWXY, YCursor]
        XYca.create_line(Dline, dash=(4,3), fill=COLORYmarker, width=GridWidth.get())
        c1 = GRHXY / 2.0 + Y0TXY    # fixed Y correction 
        yvolts = ((YCursor-c1)/Yconv1) - Yoffset1
        V1String = ' {0:.3f} '.format(-yvolts)
        V_label = V1String + Y_label
        XYca.create_text(XCursor+1, YCursor+5, text=V_label, fill=COLORYmarker, anchor="w", font=("arial", FontSize ))
    if ShowXCur.get() == 0 and ShowYCur.get() == 0 and MouseWidget == XYca:
        if MouseX > X0LXY and MouseX < X0LXY+GRWXY and MouseY > Y0TXY and MouseY < Y0TXY+GRHXY:
            Dline = [MouseX, Y0TXY, MouseX, Y0TXY+GRHXY]
            XYca.create_line(Dline, dash=(4,3), fill=COLORXmarker, width=GridWidth.get())
            c1 = GRWXY / 2.0 + X0LXY    # fixed X correction 
            xvolts = Xoffset1 - ((c1-MouseX)/Xconv1) # XCursor
            XString = ' {0:.3f} '.format(xvolts)
            V_label = XString + X_label
            XYca.create_text(MouseX+1, MouseY-5, text=V_label, fill=COLORXmarker, anchor="w", font=("arial", FontSize ))
            Dline = [X0LXY, MouseY, X0LXY+GRWXY, MouseY]
            XYca.create_line(Dline, dash=(4,3), fill=COLORYmarker, width=GridWidth.get())
            c1 = GRHXY / 2 + Y0TXY    # fixed Y correction 
            yvolts = ((MouseY-c1)/Yconv1) - Yoffset1
            V1String = ' {0:.3f} '.format(-yvolts)
            V_label = V1String + Y_label
            XYca.create_text(MouseX+1, MouseY+5, text=V_label, fill=COLORYmarker, anchor="w", font=("arial", FontSize ))
#
# General information on top of the grid
# Sweep information
    sttxt = "Running"
    if TRACEmodeTime.get() == 1:
        sttxt = sttxt + " Averaging"
    if ManualTrigger.get() == 1:
        sttxt = "Manual Trigger"
    if (RUNstatus.get() == 0) or (RUNstatus.get() == 3):
        sttxt = "Stopped"
    if ScreenXYrefresh.get() == 1:
        sttxt = sttxt + " Persistance ON"
        # Delete text at bottom of screen
        de = XYca.find_enclosed( X0LXY-1, Y0TXY+GRHXY+19, CANVASwidthXY, Y0TXY+GRHXY+100)
        for n in de: 
            XYca.delete(n)
        # Delete text at top of screen
        de = XYca.find_enclosed( X0LXY-1, -1, CANVASwidthXY, 20)
        for n in de: 
            XYca.delete(n)
    SR_label = ' {0:.1f} '.format(SAMPLErate)
    if LabelPlotText.get() > 0:
        txt = PlotLabelText + " Sample rate: " + SR_label + " " + sttxt
    else:
        txt = "Device ID " + DevID + " Sample rate: " + SR_label + " " + sttxt
    x = X0LXY
    y = 12
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    # digital I/O indicators
    x2 = X0LXY + GRWXY
    # print period and frequency of displayed channels
    txt = " "
    if Xsignal.get() == 1 or Xsignal.get() == 3:
        FindRisingEdge(VBuffA, VBuffB)
        if Xsignal.get() == 1:
            if MeasAHW.get() == 1:
                txt = txt + " CA Hi Width = " + ' {0:.2f} '.format(CHAHW) + " mS "
            if MeasALW.get() == 1:
                txt = txt + " CA Lo Width = " + ' {0:.2f} '.format(CHALW) + " mS "
            if MeasADCy.get() == 1:
                txt = txt + " CA DutyCycle = " + ' {0:.1f} '.format(CHADCy) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " CA Period = " + ' {0:.2f} '.format(CHAperiod) + " mS "
            if MeasAFREQ.get() == 1:
                txt = txt + " CA Freq = " + ' {0:.1f} '.format(CHAfreq) + " Hz "
        if Xsignal.get() == 3:
            if MeasBHW.get() == 1:
                txt = txt + " CB Hi Width = " + ' {0:.2f} '.format(CHBHW) + " mS "
            if MeasBLW.get() == 1:
                txt = txt + " CB Lo Width = " + ' {0:.2f} '.format(CHBLW) + " mS "
            if MeasBDCy.get() == 1:
                txt = txt + " CB DutyCycle = " + ' {0:.1f} '.format(CHBDCy) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " CB Period = " + ' {0:.2f} '.format(CHBperiod) + " mS "
            if MeasBFREQ.get() == 1:
                txt = txt + " CB Freq = " + ' {0:.1f} '.format(CHBfreq) + " Hz "
        if MeasPhase.get() == 1:
            txt = txt + " A-B Phase = " + ' {0:.1f} '.format(CHABphase) + " deg "
            
    x = X0LXY
    y = Y0TXY+GRHXY+int(2.5*FontSize) # 20
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    txt = " "
    if Xsignal.get() == 1 or YsignalVA.get() == 1 or Xsignal.get() == 6:
    # Channel A information
        txt = "CHA: "
        txt = txt + str(XY1pdvRange) + " V/div"
        if MeasDCV1.get() == 1:
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV1)
        if MeasMaxV1.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV1)
        if MeasTopV1.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VATop)
        if MeasMinV1.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV1)
        if MeasBaseV1.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VABase)
        if MeasMidV1.get() == 1:
            MidV1 = (MaxV1+MinV1)/2
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV1)
        if MeasPPV1.get() == 1:
            PPV1 = MaxV1-MinV1
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV1)
        if MeasRMSV1.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV1)
        if MeasUserA.get() == 1:
            try:
                TempValue = eval(UserAString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserALabel + " = " + V1String

    x = X0LXY
    y = Y0TXY+GRHXY+int(4*FontSize) # 32
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    txt= " "
    # Channel B information
    if Xsignal.get() == 3 or YsignalVB.get() == 1 or Xsignal.get() == 7:
        txt = "CHB: "
        txt = txt + str(XY2pdvRange) + " V/div"
        if MeasDCV2.get() == 1:
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV2)
        if MeasMaxV2.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV2)
        if MeasTopV2.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VBTop)
        if MeasMinV2.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV2)
        if MeasBaseV2.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VBBase)
        if MeasMidV2.get() == 1:
            MidV2 = (MaxV2+MinV2)/2
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV2)
        if MeasPPV2.get() == 1:
            PPV2 = MaxV2-MinV2
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV2)
        if MeasRMSV2.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV2)
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String

    x = X0LXY
    y = Y0TXY+GRHXY+int(5.5 * FontSize) # 44
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
#
def SelectChannels():
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V

    try:
        HardwareSelectChannels()
    except:
        pass
#    
def SetScaleA():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 1:
        MarkerScale.set(1)
        CHAlab.config(style="Rtrace1.TButton")
        CHBlab.config(style="Strace2.TButton")
    else:
        MarkerScale.set(0)

def SetScaleB():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 2:
        MarkerScale.set(2)
        CHAlab.config(style="Strace1.TButton")
        CHBlab.config(style="Rtrace2.TButton")
    else:
        MarkerScale.set(0)
#
def SetScaleC():
    global MarkerScale, CHClab, CHDlab

    if MarkerScale.get() != 1:
        MarkerScale.set(3)
        CHClab.config(style="Rtrace3.TButton")
        CHDlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)

def SetScaleD():
    global MarkerScale, CHClab, CHDlab

    if MarkerScale.get() != 2:
        MarkerScale.set(3)
        CHClab.config(style="Strace3.TButton")
        CHDlab.config(style="Rtrace4.TButton")
    else:
        MarkerScale.set(0)
#
def SetXYScaleA():
    global MarkerXYScale, CHAxylab, CHBxylab

    MarkerXYScale.set(1)
    CHAxylab.config(style="Rtrace1.TButton")
    CHBxylab.config(style="Strace2.TButton")

def SetXYScaleB():
    global MarkerXYScale, CHAxylab, CHBxylab

    MarkerXYScale.set(2)
    CHBxylab.config(style="Rtrace2.TButton")
    CHAxylab.config(style="Strace1.TButton")       
#
def SetXYScaleC():
    global MarkerXYScale, CHCxylab, CHAxylab

    MarkerXYScale.set(3)
    CHCxylab.config(style="Rtrace2.TButton")
    CHAxylab.config(style="Strace1.TButton")
#
def SetXYScaleD():
    global MarkerXYScale, CHAxylab, CHDxylab

    MarkerXYScale.set(4)
    CHDxylab.config(style="Rtrace2.TButton")
    CHAxylab.config(style="Strace1.TButton")
#
def onCanvasClickRight(event):
    global ShowTCur, ShowVCur, TCursor, VCursor, RUNstatus, ca

    TCursor = event.x
    VCursor = event.y
    if RUNstatus.get() == 0:
        UpdateTimeScreen()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
## Shift Time or vertical cursors if on or shift gated measurement cursors if enabled
def onCanvasClickScroll(event):
    global ShowTCur, ShowVCur, TCursor, VCursor, RUNstatus, ca, MWcount
    global MeasGateStatus, MeasGateLeft, MeasGateRight, TimeDiv, GRW, Tdiv

    ShiftKeyDwn = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 or ShowVCur.get() > 0: # move cursors if shown
            if ShowTCur.get() > 0 and ShiftKeyDwn == 0:
            # respond to Linux or Windows wheel event
                if event.num == 5 or event.delta == -120:
                    TCursor -= 1
                if event.num == 4 or event.delta == 120:
                    TCursor += 1
            elif ShowVCur.get() > 0 or ShiftKeyDwn == 1:
            # respond to Linux or Windows wheel event
                if event.num == 5 or event.delta == -120:
                    VCursor += 1
                if event.num == 4 or event.delta == 120:
                    VCursor -= 1
##            if ShowTCur.get() > 0 and ShiftKeyDwn == 0:
##                TCursor = TCursor + event.delta/100
##            elif ShowVCur.get() > 0 or ShiftKeyDwn == 1:
##                VCursor = VCursor - event.delta/100
        else:
            if MeasGateStatus.get() == 1:
                Tstep = (TimeDiv / GRW) / Tdiv.get() # time in mS per pixel
                if ShiftKeyDwn == 0:
                    if event.num == 5 or event.delta == -120:
                        MeasGateLeft = MeasGateLeft + (-100 * Tstep)
                    if event.num == 4 or event.delta == 120:
                        MeasGateLeft = MeasGateLeft + (100 * Tstep)
                    # MeasGateLeft = MeasGateLeft + (event.delta * Tstep) #+ HoldOff
                if ShiftKeyDwn == 1:
                    if event.num == 5 or event.delta == -120:
                        MeasGateRight = MeasGateRight + (-100 * Tstep)
                    if event.num == 4 or event.delta == 120:
                        MeasGateRight = MeasGateRight + (100 * Tstep)
                    #MeasGateRight = MeasGateRight + (event.delta * Tstep) #+ HoldOff
            try:
                onSpinBoxScroll(event) # if cursor are not showing scroll the Horx time base
            except:
                donothing()
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
#
## Move Vertical cursors up 1 or 5
def onCanvasUpArrow(event):
    global ShowVCur, VCursor, YCursor, dBCursor, BdBCursor, RUNstatus, ca, XYca, Freqca, Bodeca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and shift_key == 0:
            VCursor = VCursor - 1
        elif ShowVCur.get() > 0 and shift_key == 1:
            VCursor = VCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowYCur.get() > 0 and shift_key == 0:
                YCursor = YCursor - 1
            elif ShowYCur.get() > 0 and shift_key == 1:
                YCursor = YCursor - 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowdBCur.get() > 0 and shift_key == 0:
                dBCursor = dBCursor - 1
            elif ShowdBCur.get() > 0 and shift_key == 1:
                dBCursor = dBCursor - 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBdBCur.get() > 0 and shift_key == 0:
                BdBCursor = BdBCursor - 1
            elif ShowBdBCur.get() > 0 and shift_key == 1:
                BdBCursor = BdBCursor - 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
## Move Vertical cursors down 1 or 5
def onCanvasDownArrow(event):
    global ShowVCur, VCursor, YCursor, dBCursor, BdBCursor, RUNstatus, ca, XYca, Freqca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and shift_key == 0:
            VCursor = VCursor + 1
        elif ShowVCur.get() > 0 and shift_key == 1:
            VCursor = VCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowYCur.get() > 0 and shift_key == 0:
                YCursor = YCursor + 1
            elif ShowYCur.get() > 0 and shift_key == 1:
                YCursor = YCursor + 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowdBCur.get() > 0 and shift_key == 0:
                dBCursor = dBCursor + 1
            elif ShowdBCur.get() > 0 and shift_key == 1:
                dBCursor = dBCursor + 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBdBCur.get() > 0 and shift_key == 0:
                BdBCursor = BdBCursor + 1
            elif ShowBdBCur.get() > 0 and shift_key == 1:
                BdBCursor = BdBCursor + 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
## Move Time curcors left 1 or 5
def onCanvasLeftArrow(event):
    global ShowTCur, TCursor, XCursor, FCursor, BPCursor, RUNstatus, ca, XYca, Freqca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and shift_key == 0:
            TCursor = TCursor - 1
        elif ShowTCur.get() > 0 and shift_key == 1:
            TCursor = TCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowXCur.get() > 0 and shift_key == 0:
                XCursor = XCursor - 1
            elif ShowXCur.get() > 0 and shift_key == 1:
                XCursor = XCursor - 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowFCur.get() > 0 and shift_key == 0:
                FCursor = FCursor - 1
            elif ShowFCur.get() > 0 and shift_key == 1:
                FCursor = FCursor - 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBPCur.get() > 0 and shift_key == 0:
                BPCursor = BPCursor - 1
            elif ShowBPCur.get() > 0 and shift_key == 1:
                BPCursor = BPCursor - 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
## Move Time curcors right 1 or 5
def onCanvasRightArrow(event):
    global ShowTCur, TCursor, XCursor, FCursor, BPCursor, RUNstatus, ca, XYca, Freqca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and shift_key == 0:
            TCursor = TCursor + 1
        elif ShowTCur.get() > 0 and shift_key == 1:
            TCursor = TCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowXCur.get() > 0 and shift_key == 0:
                XCursor = XCursor + 1
            elif ShowXCur.get() > 0 and shift_key == 1:
                XCursor = XCursor + 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowFCur.get() > 0 and shift_key == 0:
                FCursor = FCursor + 1
            elif ShowFCur.get() > 0 and shift_key == 1:
                FCursor = FCursor + 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBPCur.get() > 0 and shift_key == 0:
                BPCursor = BPCursor + 1
            elif ShowBPCur.get() > 0 and shift_key == 1:
                BPCursor = BPCursor + 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
## Pause / start on space bar
def onCanvasSpaceBar(event):
    global RUNstatus, ca, XYca, Freqca, Bodeca, IAca

    if event.widget == ca:
        if RUNstatus.get() == 0:
            BStart()
        elif RUNstatus.get() > 0:
            BStop()
    try:
        if event.widget == XYca:
            if RUNstatus.get() == 0:
                BStart()
            elif RUNstatus.get() > 0:
                BStop()
    except:
        donothing()
    try:
        if event.widget == IAca:
            if RUNstatus.get() == 0:
                BStart()
            elif RUNstatus.get() > 0:
                BStop()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if RUNstatus.get() == 0:
                BStartSA()
            elif RUNstatus.get() > 0:
                BStopSA()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if RUNstatus.get() == 0:
                BStartBP()
            elif RUNstatus.get() > 0:
                BStopBP()
    except:
        donothing()
#
def onCanvasClickLeft(event):
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global FontSize, Tdiv, CHANNELS
    global ca, MarkerLoc, Roll_Mode, TimeDiv, ZeroGrid
    global HoldOffentry, Xsignal, Ysignal, COLORgrid, COLORtext
    global TMsb, CHAsb, CHBsb, CHAIsb, CHBIsb, MarkerScale
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry
    global SAMPLErate, RUNstatus, MarkerNum, PrevV, PrevT
    global COLORtrace1, COLORtrace2, MathUnits, MathXUnits, MathYUnits
    global CH1pdvRange, CH2pdvRange, CHCpdvRange, CHDpdvRange
    global CHAOffset, CHAIOffset, CHBOffset, CHBIOffset
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global MeasGateLeft, MeasGateRight, MeasGateStatus, MeasGateNum, TMsb, SAMPLErate
    
    # get time scale
    TimeDiv = UnitConvert(TMsb.get())

    # 
    # add markers only if stopped
    if (RUNstatus.get() == 0):
        MarkerNum = MarkerNum + 1
        # get the vertical ranges
        CH1pdvRange = UnitConvert(CHAsb.get())
        if CHANNELS >= 2:
            CH2pdvRange = UnitConvert(CHBsb.get())
        # get the vertical offsets
        try:
            CHAOffset = float(eval(CHAVPosEntry.get()))
        except:
            CHAVPosEntry.delete(0,END)
            CHAVPosEntry.insert(0, CHAOffset)
        if CHANNELS >= 2:
            try:
                CHBOffset = float(eval(CHBVPosEntry.get()))
            except:
                CHBVPosEntry.delete(0,END)
                CHBVPosEntry.insert(0, CHBOffset)
        # prevent divide by zero error
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
        if CHANNELS >= 2:
            if CH2pdvRange < 0.001:
                CH2pdvRange = 0.001
#
        Yoffset1 = CHAOffset
        if MarkerScale.get() == 1:
            Yconv1 = float(GRH/10.0) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORmarker = COLORtrace1
            Units = " V"
        elif MarkerScale.get() == 2:
            Yconv1 = float(GRH/10.0) / CH2pdvRange
            Yoffset1 = CHBOffset
            COLORmarker = COLORtrace2
            Units = " V"
        else:
            Yconv1 = float(GRH/10.0) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORmarker = COLORtrace1
            Units = " V"
    #
        c1 = GRH / 2.0 + Y0T    # fixed correction channel A
        xc1 = GRW / 2.0 + X0L
        c2 = GRH / 2.0 + Y0T    # fixed correction channel B
        # draw X at marker point and number
        ca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORtext)
        ca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORtext)
        #
        Tstep = (Tdiv.get() * TimeDiv) / GRW # time in mS per pixel
        vt = TimeDiv * ZeroGrid.get() # (Tdiv.get()/-2)
        Tpoint = ((event.x-X0L) * Tstep) + vt
        #
        TString = ' {0:.3f} '.format(Tpoint) + " nS"
        if Tpoint >= 1.0:
            TString = ' {0:.3f} '.format(Tpoint) + " S"
        if Tpoint < 1.0 and Tpoint >= 0.001:
            axis_value = Tpoint * 1000
            TString = ' {0:.3f} '.format(axis_value) + " mS"
        if Tpoint < 0.001:
            axis_value = Tpoint * 1000000
            TString = ' {0:.3f} '.format(axis_value) + " uS"
        #
        yvolts = ((event.y-c1)/Yconv1) - Yoffset1
        if MarkerScale.get() == 1 or MarkerScale.get() == 2:
            V1String = ' {0:.3f} '.format(-yvolts)
        else:
            V1String = ' {0:.1f} '.format(-yvolts)
        V_label = str(MarkerNum) + " " + TString + V1String
        V_label = V_label + Units
        if MarkerNum > 1:
            if MarkerScale.get() == 1 or MarkerScale.get() == 2:
                DeltaV = ' {0:.3f} '.format(PrevV-yvolts)
            else:
                DeltaV = ' {0:.1f} '.format(PrevV-yvolts)
            if Roll_Mode.get() == 0: # should be same as First_Slow_sweep == 0
                DT = (Tpoint-PrevT)
                #
                DeltaT = ' {0:.3f} '.format(DT) + " nS"
                if Tpoint >= 1.0:
                    DeltaT = ' {0:.3f} '.format(DT) + " S"
                if Tpoint < 1.0 and Tpoint >= 0.001:
                    axis_value = DT * 1000
                    DeltaT = ' {0:.3f} '.format(axis_value) + " mS"
                if Tpoint < 0.001:
                    axis_value = DT * 1000000
                    DeltaT = ' {0:.3f} '.format(axis_value) + " uS"
                #
                DeltaFreq = 1.0/(Tpoint-PrevT)
                
                V_label = V_label + " Delta " + DeltaT + DeltaV
                V_label = V_label + Units
                if DeltaFreq >= 1000:
                    DFreq = ' {0:.3f} '.format(DeltaFreq/1000.0)
                    V_label = V_label + ", Freq " + DFreq + " KHz"
                else:
                    DFreq = ' {0:.3f} '.format(DeltaFreq)
                    V_label = V_label + ", Freq " + DFreq + " Hz"
            else:
                V_label = V_label  + " Delta " + DeltaV + Units
        # place in upper left unless specified otherwise
        TxScale = FontSize + 2
        x = X0L + 5
        y = Y0T + 3 + (MarkerNum*TxScale)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0L + GRW - 5
            y = Y0T + 3 + (MarkerNum*TxScale)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0L + 5
            y = Y0T + GRH + 3 - (MarkerNum*TxScale)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0L + GRW - 5
            y = Y0T + GRH + 3 - (MarkerNum*TxScale)
            Justify = 'e'
        ca.create_text(event.x+4, event.y, text=str(MarkerNum), fill=COLORtext, anchor=Justify, font=("arial", FontSize ))
        ca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", FontSize ))
        PrevV = yvolts
        PrevT = Tpoint
    else:
        if MeasGateStatus.get() == 1:
            #
            Tstep = (Tdiv.get() * TimeDiv) / GRW # time in mS per pixel
            if MeasGateNum == 0:
                MeasGateLeft = ((event.x-X0L) * Tstep) #+ HoldOff
                MeasGateNum = 1
            else:
                MeasGateRight = ((event.x-X0L) * Tstep) #+ HoldOff
                MeasGateNum = 0
            LeftGate = X0L + MeasGateLeft / Tstep
            RightGate = X0L + MeasGateRight / Tstep
            ca.create_line(LeftGate, Y0T, LeftGate, Y0T+GRH, fill=COLORtext)
            ca.create_line(RightGate, Y0T, RightGate, Y0T+GRH, fill=COLORtext)
#
def onCanvasOne(event):
    global ShowC1_V

    if ShowC1_V.get() == 0:
        ShowC1_V.set(1)
    else:
        ShowC1_V.set(0)
#
def onCanvasTwo(event):
    global ShowC2_V, CHANNELS

    if CHANNELS >= 2:
        if ShowC2_V.get() == 0:
            ShowC2_V.set(1)
        else:
            ShowC2_V.set(0)
#
def onCanvasThree(event):
    global ShowC3_V, CHANNELS

    if CHANNELS >= 3:
        if ShowC3_V.get() == 0:
            ShowC3_V.set(1)
        else:
            ShowC3_V.set(0)
#
def onCanvasFour(event):
    global ShowC4_V, CHANNELS

    if CHANNELS >= 4:
        if ShowC4_V.get() == 0:
            ShowC4_V.set(1)
        else:
            ShowC4_V.set(0)
# 
def onCanvasFive(event):
    global MathTrace

    MathTrace.set(1)
#
def onCanvasSix(event):
    global MathTrace

    MathTrace.set(2)
# 
def onCanvasSeven(event):
    global MathTrace

    MathTrace.set(3)
#
def onCanvasEight(event):
    global MathTrace

    MathTrace.set(10)
#
def onCanvasNine(event):
    global MathTrace

    MathTrace.set(12)
#
def onCanvasZero(event):
    global MathTrace

    MathTrace.set(0)
#
def onCanvasTrising(event):
    global TgEdge

    TgEdge.set(0)
#
def onCanvasTfalling(event):
    global TgEdge

    TgEdge.set(1)
#
def onCanvasSnap(event):

    BSnapShot()
#
def onCanvasAverage(event):
    global TRACEmodeTime

    if TRACEmodeTime.get() == 0:
        TRACEmodeTime.set(1)
    else:
        TRACEmodeTime.set(0)
#
def onCanvasInterp(event):
    global EnableInterpFilter

    if EnableInterpFilter.get() == 0:
        EnableInterpFilter.set(1)
    else:
        EnableInterpFilter.set(0)
#
def onCanvasShowTcur(event):
    global ShowTCur

    if ShowTCur.get() == 0:
        ShowTCur.set(1)
    else:
        ShowTCur.set(0)
#
def onCanvasShowVcur(event):
    global ShowVCur

    if ShowVCur.get() == 0:
        ShowVCur.set(1)
    else:
        ShowVCur.set(0)
#
def onCanvasXYRightClick(event):
    global ShowXCur, ShowYCur, XCursor, YCursor, RUNstatus, XYca

    XCursor = event.x
    YCursor = event.y
    if RUNstatus.get() == 0:
        UpdateXYScreen()
    XYca.bind_all('<MouseWheel>', onCanvasXYScrollClick)
#
def onCanvasXYScrollClick(event):
    global ShowXCur, ShowYCur, XCursor, YCursor, RUNstatus
    if event.widget == XYca:
        if ShowXCur.get() > 0 or ShowYCur.get() > 0: # move cursors if shown
            ShiftKeyDwn = event.state & 1
            if ShowXCur.get() > 0 and ShiftKeyDwn == 0:
                # respond to Linux or Windows wheel event
                if event.num == 5 or event.delta == -120:
                    XCursor -= 1
                if event.num == 4 or event.delta == 120:
                    XCursor += 1
                # XCursor = XCursor + event.delta/100
            elif ShowYCur.get() > 0 or ShiftKeyDwn == 1:
                # respond to Linux or Windows wheel event
                if event.num == 5 or event.delta == -120:
                    YCursor += 1
                if event.num == 4 or event.delta == 120:
                    YCursor -= 1
                #YCursor = YCursor - event.delta/100
        if RUNstatus.get() == 0:
            UpdateXYScreen()
#
def onCanvasXYLeftClick(event):
    global X0LXY          # Left top X value
    global Y0TXY          # Left top Y value
    global GRWXY          # Screenwidth
    global GRHXY          # Screenheight
    global FontSize
    global XYca, CHANNELS
    global HoldOffentry, Xsignal, YsignalVA, YsignalVB, COLORgrid, COLORtext
    global TMsb, CHAsbxy, CHBsbxy, CHCsbxy, CHDsbxy, MarkerScale
    global CHAVPosEntryxy, CHBVPosEntryxy
    global SAMPLErate, RUNstatus, MarkerNum, PrevX, PrevY
    global COLORtrace1, COLORtrace2, MathUnits, MathXUnits, MathYUnits
    global CH1pdvRange, CH2pdvRange
    global CHAOffset, CHBOffset
    # add markers only if stopped
    # 
    if (RUNstatus.get() == 0):
        MarkerNum = MarkerNum + 1
        try:
            XY1pdvRange = float(eval(CHAsbxy.get()))
        except:
            CHAsbxy.delete(0,END)
            CHAsbxy.insert(0, XY1pdvRange)
        if CHANNELS >= 2:
            try:
                XY2pdvRange = float(eval(CHBsbxy.get()))
            except:
                CHBsbxy.delete(0,END)
                CHBsbxy.insert(0, XY2pdvRange)
        # get the vertical offsets
        try:
            CHAOffset = float(eval(CHAVPosEntryxy.get()))
        except:
            CHAVPosEntryxy.delete(0,END)
            CHAVPosEntryxy.insert(0, CHAOffset)
        if CHANNELS >= 2:
            try:
                CHBOffset = float(eval(CHBVPosEntryxy.get()))
            except:
                CHBVPosEntryxy.delete(0,END)
                CHBVPosEntryxy.insert(0, CHBOffset)
        # prevent divide by zero error
        if XY1pdvRange < 0.001:
            XY1pdvRange = 0.001
        if XY2pdvRange < 0.001:
            XY2pdvRange = 0.001
    #
        Yconv1 = float(GRHXY/10) / XY1pdvRange    # Conversion factors from samples to screen points
        Xconv1 = float(GRWXY/10) / XY1pdvRange
        if CHANNELS >= 2:
            Yconv2 = float(GRHXY/10) / XY2pdvRange
            Xconv2 = float(GRWXY/10) / XY2pdvRange
        COLORmarker = COLORtext
        Yoffset1 = CHAOffset
        c1 = GRHXY / 2 + Y0TXY    # fixed correction channel A
        xc1 = GRWXY / 2 + X0LXY
        c2 = GRHXY / 2 + Y0TXY    # fixed correction channel B
        # draw X at marker point and number
        XYca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORtext)
        XYca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORtext)
        XYca.create_text(event.x+4, event.y, text=str(MarkerNum), fill=COLORtext, anchor="w", font=("arial", FontSize ))
        V_label = str(MarkerNum) + " "
        x = X0LXY + 5
        y = Y0TXY + 3 + (MarkerNum*10)
        xvolts = ((xc1-event.x)/Xconv1) - CHAOffset # preset the variable
        if (Xsignal.get()==1 or Xsignal.get()==5) and (YsignalVA.get()==3 or YsignalVB.get()==5):
            yvolts = ((event.y-c2)/Yconv2) - CHBOffset
            xvolts = ((xc1-event.x)/Xconv1) - CHAOffset
            VyString = ' {0:.3f} '.format(-yvolts)
            VxString = ' {0:.3f} '.format(-xvolts)
            V_label = V_label + VxString + " V, " + VyString + " V"
            if MarkerNum > 1:
                DeltaY = ' {0:.3f} '.format(PrevY-yvolts)
                DeltaX = ' {0:.3f} '.format(PrevX-xvolts)
                V_label = V_label + " Delta " + DeltaX + " V, " + DeltaY + " V"
            PrevY = yvolts
        elif (Xsignal.get()==3 or Xsignal.get()==5) and (YsignalVA.get()==1 or YsignalVB.get()==5):
            yvolts = ((event.y-c1)/Yconv1) - CHAOffset
            xvolts = ((xc1-event.x)/Xconv2) - CHBOffset
            VyString = ' {0:.3f} '.format(-yvolts)
            VxString = ' {0:.3f} '.format(-xvolts)
            V_label = V_label + VxString + " V, " + VyString + " V"
            if MarkerNum > 1:
                DeltaY = ' {0:.3f} '.format(PrevY-yvolts)
                DeltaX = ' {0:.3f} '.format(PrevX-xvolts)
                V_label = V_label + " Delta " + DeltaX + " V, " + DeltaY + " V"
            PrevY = yvolts
        XYca.create_text(x, y, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
        PrevX = xvolts
#
# Some DSP functions
#
# Generate Time-series From Half-spectrum code block
# takes: a desired noise spectral density array (freq)
# the sample rate of the time series (fs),
# returns a time series of voltage samples that can be sent to the AWG
# 
# DC in first element.
# Output length is 2x input length
def time_points_from_freq(freq, fs=1, density=False):
    N=len(freq)
    rnd_ph_pos = (numpy.ones(N-1, dtype=numpy.complex)*
                  numpy.exp(1j*numpy.random.uniform
                         (0.0,2.0*numpy.pi, N-1)))
    rnd_ph_neg = numpy.flip(numpy.conjugate(rnd_ph_pos))
    rnd_ph_full = numpy.concatenate(([1],rnd_ph_pos,[1], rnd_ph_neg))
    r_s_full = numpy.concatenate((freq, numpy.roll(numpy.flip(freq), 1)))
    r_spectrum_rnd_ph = r_s_full * rnd_ph_full
    r_time_full = numpy.fft.ifft(r_spectrum_rnd_ph)
#    print("RMS imaginary component: ",
#          np.std(np.imag(r_time_full)),
#          " Should be close to nothing")
    if (density == True):
        #Note that this N is "predivided" by 2
        r_time_full *= N*numpy.sqrt(fs/(N))
    return(numpy.real(r_time_full))
#
def TimeSeriesNoise(n, Fsample, mag, b=4):
    # Build Noise Time-series
    # n = number of Freq Bins
    # b = number of noise bands
    # Fsample is Sample Rate
    # generates four "bands" of mag V/rootHz noise
    mag = mag * 0.707106 # scale by 1/sqrt 2 for RMS
    width = int(n/(4 * b))
    i = 1
    aband = numpy.ones(width)
    zband = numpy.zeros(width)
    bands = numpy.concatenate((aband, zband))
    while i < b:
        bands = numpy.concatenate((bands, aband, zband))
        i = i + 1
    bands = bands*mag
    bands[0] = 0.0 # Set DC bin content to zero
    return time_points_from_freq(bands, fs=Fsample, density=True)
#
# Generate Time samples for single frequency Bin
# Uses IFFT
#
def TimeSeriesSingleTone(n, BinNum, Fsample, mag):
    # Build Single tone Time-series
    # n = number of Freq Bins
    # BinNum = FFT Bin number
    # Fsample is Sample Rate
    # mag is tone amplitude
    bands = numpy.zeros(n)
    bands[BinNum] = 1
    bands = bands * (mag/2.0)
    return time_points_from_freq(bands, fs=Fsample, density=True)
#
def PinkNoise(N, mag):
    # Pink noise.
    # Pink noise has equal power in bands that are proportionally wide.
    # Power spectral density decreases with 3 dB per octave.
    # N Length of sample array, mag magnitude scaling factor
    
    x = numpy.random.normal(0.0, 1, N).astype(numpy.float32) # white Noise
    X = numpy.fft.rfft(x) / N
    S = numpy.sqrt(numpy.arange(X.size)+1.0)  # +1 to avoid divide by zero
    y = numpy.fft.irfft(X/S).real[:N] # extremely tiny value 1e-9 without normalization
    z = numpy.ndarray = mag
    y = y * numpy.sqrt((numpy.abs(z)**2).mean() / (numpy.abs(y)**2).mean())

    return y 
#
def BlueNoise(N, mag):
    # Blue noise.
    # Power increases with 6 dB per octave.
    # Power spectral density increases with 3 dB per octave.
    # N Length of sample array, mag magnitude scaling factor
    
    # x = numpy.random.randn(N).astype(numpy.float32) # white Noise
    x = numpy.random.normal(0.0, 1, N).astype(numpy.float32) # white Noise
    X = numpy.fft.rfft(x) / N
    S = numpy.sqrt(numpy.arange(X.size))  # Filter
    y = numpy.fft.irfft(X*S).real[:N]
    z = numpy.ndarray = mag
    y = y * numpy.sqrt((numpy.abs(z)**2).mean() / (numpy.abs(y)**2).mean())
    
    return y
#
def BrownNoise(N, mag):
    # Brown noise.
    # Power decreases with -3 dB per octave.
    # Power spectral density decreases with 6 dB per octave.
    # N Length of sample array, mag magnitude scaling factor
    
    # x = numpy.random.randn(N).astype(numpy.float32) # white Noise
    x = numpy.random.normal(0.0, 1, N).astype(numpy.float32) # white Noise
    X = numpy.fft.rfft(x) / N
    S = numpy.arange(X.size)+1  # Filter
    y = numpy.fft.irfft(X/S).real[:N]
    z = numpy.ndarray = mag
    y = y * numpy.sqrt((numpy.abs(z)**2).mean() / (numpy.abs(y)**2).mean())
    
    return y
#
def VioletNoise(N, mag):
    # Violet noise.
    # Power increases with +9 dB per octave.
    # Power density increases with +6 dB per octave.
    # N Length of sample array, mag magnitude scaling factor

    # x = numpy.random.randn(N).astype(numpy.float32) # white Noise
    x = numpy.random.normal(0.0, 1, N).astype(numpy.float32) # white Noise
    X = numpy.fft.rfft(x) / N
    S = numpy.arange(X.size)  # Filter
    y = numpy.fft.irfft(X*S).real[0:N]
    z = numpy.ndarray = mag
    y = y * numpy.sqrt((numpy.abs(z)**2).mean() / (numpy.abs(y)**2).mean())
    
    return y
#
def SchroederPhase(Length, NrTones, Ampl):
    # Generate a Schroeder Phase (Chirp) of Length samples and having NrTones
    OutArray = []
    OutArray = Ampl*numpy.cos(numpy.linspace(0, 2*numpy.pi, Length)) # the fundamental
    k = 2
    while k <= NrTones:
        # Add all harmonics up to NrTones
        Harmonic = Ampl*numpy.cos(numpy.linspace(0, k*2*numpy.pi, Length)+(numpy.pi*k*k/NrTones))
        OutArray = OutArray + Harmonic
        k = k + 1
    # OutArray = OutArray + 2.5 # Center wavefrom on 2.5 V
    return(OutArray)
#
def SinePower(Length, Power, Phase, Ampl):
    # Generate a Sine Power Pulse waveform of length samples with Symmetry, Phase and Ampl
    OutArray = []
    t = 1.0E-5 # 10 uSec
    frequency = 1.0/(t*Length) # Freq of one cycle
    exponent_setting = numpy.clip(Power, -99.999999999, 100.000) / 100.0
    if exponent_setting >= 0:
        exponent = (1.0 - exponent_setting)
    else:
        exponent = 1.0 / (1.0 + exponent_setting)
    #
    Len = 0
    while Len < Length:
        x = t * Len * frequency + Phase / 360.0
        plain_old_sine = numpy.sin(x * 2 * numpy.pi)
        # In the SinePower wave function, the 'Power' value is used
        # to indicate and exponent between 1.0 and 0.0.
        y = numpy.copysign(numpy.abs(plain_old_sine) ** exponent, plain_old_sine)
        OutArray.append(Ampl * y)
        Len = Len + 1
    #
    # OutArray = numpy.array(OutArray) + 2.5 # Center wavefrom on 2.5 V
    return(OutArray)
#
def Wrap(InArray, WrFactor):
    # Build new array by skipping WrFactor samples and wrapping back around
    # [1,2,3,4,5,6} becomes [1,3,5,2,4,6]
    # effectively multiplies the frequency content by WrFactor
    OutArray = []
    OutArray = numpy.array(OutArray)
    InArray = numpy.array(InArray)
    EndIndex = len(InArray)
    StartIndex = 0
    while StartIndex < WrFactor:
        OutArray = numpy.concatenate((OutArray, InArray[StartIndex:EndIndex:WrFactor]), axis=0)
        StartIndex = StartIndex + 1
    return OutArray
#
def UnWrap(InArray, WrFactor):
    # Build new array by splitting arrray into WrFactor sections and interleaving samples from each section
    # [1,2,3,4,5,6} becomes [1,4,2,5,3,6]
    # effectively divided the frequency content by WrFactor
    OutArray = []
    InArray = numpy.array(InArray)
    EndIndex = int(len(InArray)/WrFactor)
    StartIndex = 0
    while StartIndex < EndIndex:
        LoopIndex = 0
        while LoopIndex < WrFactor:
            OutArray.append(InArray[StartIndex+LoopIndex])
            LoopIndex = LoopIndex + 1
        StartIndex = StartIndex + 1
    OutArray = numpy.array(OutArray)
    return OutArray
#
def Write_WAV(data, repeat, filename):
    global SAMPLErate
    # write data array to mono .wav file 100KSPS
    # copy buffer repeat times in output file
    # Use : Write_WAV(VBuffB, 2, "write_wave_1.wav")
    wavfile = wave.open(filename, "w")
    nchannels = 1
    sampwidth = 2
    framerate = SAMPLErate
    amplitude = 32766
    nframes = len(data)
    comptype = "NONE"
    compname = "not compressed"
    wavfile.setparams((nchannels,
                        sampwidth,
                        framerate,
                        nframes,
                        comptype,
                        compname))
    # Normalize data
    ArrN = numpy.array(data)
    ArrN /= numpy.max(numpy.abs(data))
    frames = []
    for s in ArrN:
        mul = int(s * amplitude)
        # print "s: %f mul: %d" % (s, mul)
        frames.append(struct.pack('h', mul))
    print( len(frames))
    frames = ''.join(frames)
    print( len(frames))
    for x in xrange(0, repeat):
        print( x )
        wavfile.writeframes(frames)
    wavfile.close()
#   
## ======= Spectrum Analyzer functions ===========
#
def BSaveScreenSA():
    global CANVASwidthF, CANVASheightF, freqwindow
    global COLORtext
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent=freqwindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=freqwindow)
    if MarkerNum > 0 or ColorMode.get() > 0:
        Freqca.postscript(file=filename, height=CANVASheightF, width=CANVASwidthF, colormode='color', rotate=Orient)
    else: # temp change text color to black
        COLORtext = "#000000"
        UpdateFreqScreen()
        # save postscript file
        Freqca.postscript(file=filename, height=CANVASheightF, width=CANVASwidthF, colormode='color', rotate=Orient)
        # 
        COLORtext = "#ffffff"
        UpdateFreqScreen()
#
def Bnot():
    print( "Routine not made yet")

def BShowCurvesAllSA():
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P
    ShowC1_VdB.set(1)
    ShowC1_P.set(1)
    ShowC2_VdB.set(1)
    ShowC2_P.set(1)

def BShowCurvesNoneSA():
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P
    ShowC1_VdB.set(0)
    ShowC1_P.set(0)
    ShowC2_VdB.set(0)
    ShowC2_P.set(0)
    
def BNormalmode():
    global RUNstatus
    global FreqTraceMode

    FreqTraceMode.set(1)
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)
    
def BPeakholdmode():
    global RUNstatus
    global FreqTraceMode

    FreqTraceMode.set(2)
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)
    
def BAveragemode():
    global RUNstatus, TRACEaverage, FreqTraceMode, freqwindow

    FreqTraceMode.set(3)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)

def BResetFreqAvg():
    global FreqTraceMode, TRACEresetFreq

    if FreqTraceMode.get()==3:
        TRACEresetFreq = True
        
def BSTOREtraceSA():
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMathSA
    global T1Fline, T2Fline, T1FRline, T2FRline, TFRMline, TFMline
    global T1Pline, T2Pline, T1PRline, T2PRline
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    
    if ShowC1_VdB.get() == 1:
        T1FRline = T1Fline
        PeakxRA = PeakxA
        PeakyRA = PeakyA
        PeakdbRA = PeakdbA
        PeakfreqRA = PeakfreqA
    if ShowC2_VdB.get() == 1:
        T2FRline = T2Fline
        PeakxRB = PeakxB
        PeakyRB = PeakyB
        PeakdbRB = PeakdbB
        PeakfreqRB = PeakfreqB
    if ShowC1_P.get() == 1:
        T1PRline = T1Pline
    if ShowC2_P.get() == 1:
        T2PRline = T2Pline
    if ShowMathSA.get() > 0:
        TFRMline = TFMline
        PeakxRM = PeakxM
        PeakyRM = PeakyM
        PeakRMdb = PeakMdb
        PeakfreqRM = PeakfreqM

    UpdateFreqTrace()           # Always Update
#
##
def BSTOREtraceBP():
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMathBP
    global Show_Rseries, Show_Xseries, Show_Magnitude, Show_Angle
    global TAFline, TBFline, TAFRline, TBFRline, TBPRMline, TBPMline
    global TAPline, TBPline, TAPRline, TBPRline
    global TIARline, TIAXline, TIAMagline, TIAAngline
    global RefIARline, RefIAXline, RefIAMagline, RefIAAngline
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    
    if ShowCA_VdB.get() == 1:
        TAFRline = TAFline
        PeakxRA = PeakxA
        PeakyRA = PeakyA
        PeakdbRA = PeakdbA
        PeakfreqRA = PeakfreqA
    if ShowCB_VdB.get() == 1:
        TBFRline = TBFline
        PeakxRB = PeakxB
        PeakyRB = PeakyB
        PeakdbRB = PeakdbB
        PeakfreqRB = PeakfreqB
    if ShowCA_P.get() == 1:
        TAPRline = TAPline
    if ShowCB_P.get() == 1:
        TBPRline = TBPline
    if ShowMathBP.get() > 0:
        TBPRMline = TBPMline
        PeakxRM = PeakxM
        PeakyRM = PeakyM
        PeakRMdb = PeakMdb
        PeakfreqRM = PeakfreqM
    if Show_Rseries.get() > 0:
        RefIARline = TIARline
    if Show_Xseries.get() > 0:
        RefIAXline = TIAXline
    if Show_Magnitude.get() > 0:
        RefIAMagline = TIAMagline
    if Show_Angle.get() > 0:
        RefIAAngline = TIAAngline
    UpdateBodeTrace()           # Always Update
#
## Store the trace as CSV file [frequency, magnitude or dB value]
def BCSVfile():
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep, bodewindow
    global SAMPLErate, ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, TRACEsize
    
    # Set the TRACEsize variable
    if ShowCA_VdB.get() == 1:
        TRACEsize = len(FSweepAdB)     # Set the trace length
    elif ShowCA_VdB.get() == 1:
        TRACEsize = len(FSweepBdB)
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        return()
# ask if save as magnitude or dB
    dB = askyesno("Mag or dB: ","Save amplidude data as dB (Yes) or Mag (No):\n", parent=bodewindow)
# Yes 1 = dB, No 0 = Mag
    # Make the file name and open it
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
    filename = "Bode-" + tme
    filename = filename + ".csv"
    # open file to save data
    filename = asksaveasfilename(initialfile = filename, defaultextension = ".csv",
                                 filetypes=[("Comma Separated Values", "*.csv")], parent=bodewindow)
    DataFile = open(filename,'a')  # Open output file
    HeaderString = 'Frequency-#, '
    if ShowCA_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'CA-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CA-Mag, '
    if ShowCB_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'CB-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CB-Mag, '
    if ShowCA_P.get() == 1:
        HeaderString = HeaderString + 'Phase A-B, '
    if ShowCB_P.get() == 1:
        HeaderString = HeaderString + 'Phase B-A, '
    HeaderString = HeaderString + '\n'
    DataFile.write( HeaderString )   

    n = 0
    while n < len(FSweepAdB):
        F = FStep[n] # look up frequency bin in list of bins
        txt = str(F)
        if ShowCA_VdB.get() == 1:
            V = 10 * math.log10(float(FSweepAdB[n]))  
            if dB == 0:
                V = 10.0**(V/20.0)
            txt = txt + "," + str(V) 
        if ShowCB_VdB.get() == 1:
            V = 10 * math.log10(float(FSweepBdB[n])) 
            if dB == 0:
                V = 10.0**(V/20.0)
            txt = txt  + "," + str(V)
        if ShowCA_P.get() == 1:
            RelPhase = FSweepAPh[n]#-FSweepBPh[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        if ShowCB_P.get() == 1:
            RelPhase = FSweepBPh[n]#-FSweepAPh[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        txt = txt + "\n"
        DataFile.write(txt)
        n = n + 1    

    DataFile.close()    # Close the file

def BSaveDataIA():
    global iawindow, FStep
    global NetworkScreenStatus, NSweepSeriesR, NSweepSeriesX, NSweepSeriesMag, NSweepSeriesAng
    
    if NetworkScreenStatus.get() > 0:
        tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
        filename = "Impedance-" + tme
        filename = filename + ".csv"
        # open file to save data
        filename = asksaveasfilename(initialfile = filename, defaultextension = ".csv",
                                     filetypes=[("Comma Separated Values", "*.csv")], parent=iawindow)
        DataFile = open(filename,'a')  # Open output file
        HeaderString = 'Frequency, Series R, Series X, Series Z, Series Angle'
        HeaderString = HeaderString + '\n'
        DataFile.write( HeaderString )

        n = 0
        while n < len(NSweepSeriesR):
            F = FStep[n] # look up frequency bin in list of bins
            txt = str(F) + "," + str(NSweepSeriesR[n]) + "," + str(NSweepSeriesX[n]) + "," + str(NSweepSeriesMag[n]) + "," + str(NSweepSeriesAng[n])
            txt = txt + "\n"
            DataFile.write(txt)
            n = n + 1
        DataFile.close()    # Close the file
    else:
        return
#
def BStartSA():
    global RUNstatus, freqwindow, session, AWGSync, contloop, discontloop
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMathSA, DevID, StopFreqEntry

    #AWGSync.set(0) # always run in continuous mode
    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    else:
        if (ShowC1_VdB.get() == 0 and
        ShowC2_VdB.get() == 0 and
        ShowMathSA.get() == 0 and
        ShowC1_P.get() == 0 and
        ShowC2_P.get() == 0):
            showwarning("WARNING","Select at least one trace first",  parent=freqwindow)
            return()
        try:
            StopFrequency = float(StopFreqEntry.get())
        except:
            StopFreqEntry.delete(0,"end")
            StopFreqEntry.insert(0,50000)
            StopFrequency = 50000
        #
        BStart()
#
    UpdateFreqAll()          # Always Update

def BStopSA():
    global RUNstatus, session, AWGSync

    if (RUNstatus.get() == 1):
        contloop = 0
        discontloop = 1
        RUNstatus.set(0)
    else:
        RUNstatus.set(0)
    UpdateFreqAll()          # Always Update
    
def Blevel1():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() - 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def Blevel2():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() + 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def Blevel3():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() - 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def Blevel4():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() + 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()
#
def BDBdiv1():
    global DBdivindex
    global RUNstatus
    
    if (DBdivindex.get() >= 1):
        DBdivindex.set(DBdivindex.get() - 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def BDBdiv2():
    global DBdivindex
    global DBdivlist
    global RUNstatus
    
    if (DBdivindex.get() < len(DBdivlist) - 1):
        DBdivindex.set(DBdivindex.get() + 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()
#
##----- Bode Plot controls
def BStartBP():
    global RUNstatus, LoopNum, devx, PwrBt, bodewindow, session, AWGSync
    global ShowCA_VdB, ShowCB_P, ShowCB_VdB, ShowCB_P, ShowMathBP, contloop, discontloop
    global FStep, NSteps, FSweepMode, HScaleBP, CutDC
    global AWGAMode, AWGAShape, AWGBMode, AWGBShape
    global StartBodeEntry, StopBodeEntry, SweepStepBodeEntry, DevID
    global AWGAFreqEntry, Reset_Freq
    global ZEROstuffing, SAMPLErate
    global BeginIndex, EndIndex

    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    else:
        if ShowCA_VdB.get() == 0 and ShowCB_VdB.get() == 0 and ShowMathBP.get() == 0:
            showwarning("WARNING","Select at least one trace first",  parent=bodewindow)
            return()
        #
        if ZEROstuffing.get() < 3:
            ZEROstuffing.set(3)
        CutDC.set(1) # set to remove DC
        try:
            EndFreq = float(StopBodeEntry.get())
        except:
            StopBodeEntry.delete(0,"end")
            StopBodeEntry.insert(0,10000)
            EndFreq = 10000
        try:
            BeginFreq = float(StartBodeEntry.get())
        except:
            StartBodeEntry.delete(0,"end")
            StartBodeEntry.insert(0,100)
            BeginFreq = 100
        #
        if FSweepMode.get() == 1:
            AWGAShape.set(1) # Set Shape to Sine
            Reset_Freq = AWGAFreqEntry.get()
            
        try:
            NSteps.set(float(SweepStepBodeEntry.get()))
        except:
            SweepStepBodeEntry.delete(0,"end")
            SweepStepBodeEntry.insert(0, NSteps.get())
        #
        if FSweepMode.get() > 0:
            LoopNum.set(1)
            if NSteps.get() < 5:
                NSteps.set(5)
            if HScaleBP.get() == 1:
                LogFStop = math.log10(EndFreq)
                try:
                    LogFStart = math.log10(BeginFreq)
                except:
                    LogFStart = 0.1
                FStep = numpy.logspace(LogFStart, LogFStop, num=NSteps.get(), base=10.0)
            else:
                FStep = numpy.linspace(BeginFreq, EndFreq, num=NSteps.get())
            
        BStart()
        # UpdateBodeAll()          # Always Update
#
def BStopBP():
    global RUNstatus, AWGSync, FSweepMode, AWGAFreqEntry, AWGBFreqEntry, Reset_Freq
    
    if FSweepMode.get() == 1:
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, Reset_Freq)
    if FSweepMode.get() == 2:
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, Reset_Freq)
#
    if (RUNstatus.get() == 1):
        RUNstatus.set(0)
    elif (RUNstatus.get() == 2):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 3):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 4):
        RUNstatus.set(3)
    UpdateBodeAll()          # Always Update
# 
def Blevel1BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() - 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def Blevel2BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() + 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def Blevel3BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() - 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def Blevel4BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() + 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def BDBdiv1BP():
    global DBdivindexBP
    global RUNstatus
    
    if (DBdivindexBP.get() >= 1):
        DBdivindexBP.set(DBdivindexBP.get() - 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def BDBdiv2BP():
    global DBdivindexBP
    global DBdivlist
    global RUNstatus
    
    if (DBdivindexBP.get() < len(DBdivlist) - 1):
        DBdivindexBP.set(DBdivindexBP.get() + 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()
#
def BShowCurvesAllBP():
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P
    ShowCA_VdB.set(1)
    ShowCA_P.set(1)
    ShowCB_VdB.set(1)
    ShowCB_P.set(1)

def BShowCurvesNoneBP():
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P
    ShowCA_VdB.set(0)
    ShowCA_P.set(0)
    ShowCB_VdB.set(0)
    ShowCB_P.set(0)
# Bode Plot refresh
def UpdateBodeAll():        # Update Data, trace and screen
    global FFTBuffA, FFTBuffB
    
    # DoFFT()             # Fast Fourier transformation
    MakeBodeTrace()         # Update the traces
    UpdateBodeScreen()      # Update the screen 

def UpdateBodeTrace():      # Update trace and screen
    MakeBodeTrace()         # Update traces
    UpdateBodeScreen()      # Update the screen

def UpdateBodeScreen():     # Update screen with trace and text
    MakeBodeScreen()        # Update the screen    
#    
## ============================================ Freq Main routine ====================================================
#
def UpdateFreqAll():        # Update Data, trace and screen
    global VBuffA, VBuffB
    global SHOWsamples

    if len(VBuffA) < SHOWsamples and len(VBuffB) < SHOWsamples:
        return
    
    # DoFFT()             # Fast Fourier transformation
    #print("about to make Freq Trace")
    MakeFreqTrace()         # Update the traces
    #print("about to update Freq screen")
    UpdateFreqScreen()      # Update the screen 

def UpdateFreqTrace():      # Update trace and screen
    MakeFreqTrace()         # Update traces
    UpdateFreqScreen()      # Update the screen

def UpdateFreqScreen():     # Update screen with trace and text
    #print("about to make Freq screen")
    MakeFreqScreen()        # Update the screen    
#
## Chirp-Z transform.
#
def czt(x, m = None, w = None, a = None):
    """Calculate the Chirp-Z transform of an input vector x.
    Parameters:
        x: time domain samples.
        m: The number of frequency domain samples in the result.
        a: The complex starting point (normally, a point on the complex unit circle).
        w: The complex ratio between points (normally, a point on the complex unix circle). Determines the frequency resolution.
    """

    n = len(x)
    if m is None: m = n
    if w is None: w = numpy.exp(-2j * numpy.pi / m)
    if a is None: a = 1.

    w_exponents_1 = numpy.arange(0, n)**2 / 2.0    # n elements [ 0 .. (n - 1) ]
    w_exponents_2 = - numpy.arange(-(n - 1), m)**2 / 2.0 # m + n - 1 elements [ -(n - 1) .. +(m - 1) ]
    w_exponents_3 = numpy.arange(0, m)**2 / 2.0    # m elements [ 0 ..  (m - 1) ]

    xx = x * a ** -numpy.arange(n) * w ** w_exponents_1

    # Determine next-biggest FFT of power-of-two.

    nfft = 1
    while nfft < (m + n - 1):
        nfft += nfft

    # Perform CZT.
    fxx = numpy.fft.fft(xx, nfft)
    ww = w ** w_exponents_2
    fww = numpy.fft.fft(ww, nfft)
    fyy = fxx * fww
    yy = numpy.fft.ifft(fyy, nfft)

    # Select output.
    yy = yy[n - 1 : m + n - 1]
    y = yy * w ** w_exponents_3

    return y
#
## Part of Chirp Z transform
def czt_range(x, m, fmin, fmax, fs=None):
    """Calculate frequency domain samples for a frequency range [fmin .. fmax].
    This function provides an interface to the CZT functionality that covers most use cases.
    Parameters:
        x: time domain samples.
        m: The number of frequency domain samples in the result.
        fmin: The minimum frequency for which to calculate the frequency response;
        fmax: The maximum frequency for which to calculate the frequency response;
        fs: The sampling frequency of the time domain samples in x.
            If not specified, it is assumed that the fmin and fmax values are already scaled to fs.
    """
    if fs is not None:
        fmin /= fs
        fmax /= fs
    a = numpy.exp(fmin * 2 * numpy.pi * 1j)  # first frequency
    w = numpy.exp(-(fmax - fmin) / (m - 1) * 2 * numpy.pi * 1j)  # frequency step
    return czt(x, m, w, a)
#
## Do Chirp Z trnasform FFT
def DoCZT():
    global VBuffA, VBuffB, SHOWsamples, xscale
    global VAresult, VBresult, VABresult, SAMPLErate
    global PhaseVA, PhaseVB, PhaseVAB, FFTwindowshape

    PhaseA = []
    PhaseB = []
    fs = SAMPLErate
    freq_min = 50.0
    freq_max = fs/2.0
    num_bins = SHOWsamples + 1
    if len(VBuffA) != len(FFTwindowshape):
        CALCFFTwindowshape(len(VBuffA))
    #CALCFFTwindowshape(SHOWsamples)
    WData1 = VBuffA * FFTwindowshape # numpy.kaiser(SHOWsamples, 14) * 3
    WData2 = VBuffB * FFTwindowshape # numpy.kaiser(SHOWsamples, 14) * 3
    WData3 = (VBuffA-VBuffB) * FFTwindowshape # numpy.kaiser(SHOWsamples, 14) * 3
    
    WData1 = WData1 / 5.0
    WData2 = WData2 / 5.0
    WData3 = WData3 / 5.0
    RMScorr = 7.07106 / SHOWsamples # RMS For VOLTAGE!
    # VA array
    fft_1 = czt_range(WData1, num_bins, freq_min, freq_max, fs)
    PhaseVA = numpy.angle(fft_1, deg=True)     # calculate angle
    VAresult = numpy.absolute(fft_1)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    VAresult = VAresult * RMScorr
    # VB array
    fft_2 = czt_range(WData2, num_bins, freq_min, freq_max, fs)
    PhaseVB = numpy.angle(fft_2, deg=True)     # calculate angle
    VBresult = numpy.absolute(fft_2)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    VBresult = VBresult * RMScorr
    # VA-VB array
    fft_3 = czt_range(WData3, num_bins, freq_min, freq_max, fs)
    PhaseVAB = numpy.angle(fft_3, deg=True)     # calculate angle
    VABresult = numpy.absolute(fft_3)       # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    VABresult = VABresult * RMScorr
#
## calculate some FFTs
def DoFFT():
    global VBuffA, VBuffB, SHOWsamples, xscalem, SMPfft
    global TRACEresetFreq, TRACEaverage, FreqTraceMode
    global FFTmemoryA, FFTresultA, FFTresultAB, PhaseAB
    global FFTmemoryB, FFTresultB, FFTwindowshape, StopFreqEntry, StartFreqEntry
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, DCV1, DCV2
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global SAfreq_max, SAfreq_min, SAMPLErate, SAnum_bins
    
    PhaseA = []
    PhaseB = []
    fs = SAMPLErate
    SAfreq_max = fs/2.0
    if len(VBuffA) != len(VBuffB):
        return
    FFTsamples = SMPfft # len(VBuffA)
    try:
        if float(StopFreqEntry.get()) <= SAfreq_max:
            SAfreq_max = float(StopFreqEntry.get())
    except:
        SAfreq_max = fs/2.0
    SAfreq_min = fs / FFTsamples
    try:
        if float(StartFreqEntry.get()) >= SAfreq_min:
            SAfreq_min = float(StartFreqEntry.get())
    except:
        SAfreq_min = fs / FFTsamples
    SAnum_bins = FFTsamples + 1
    RMScorr = 1.0 / FFTsamples # For VOLTAGE!
    Powcorr = 50*(RMScorr **2) # vpktage squared For POWER!
    #
    CALCFFTwindowshape(SMPfft)
    if len(VBuffA) >= SMPfft:
        WData1 = VBuffA[0:SMPfft] - DCV1
    else:
        WData1 = VBuffA - DCV1
        CALCFFTwindowshape(len(VBuffA))
    if len(VBuffB) >= SMPfft:
        WData2 = VBuffB[0:SMPfft] - DCV2
    else:
        WData2 = VBuffB - DCV2
        CALCFFTwindowshape(len(VBuffB))
    WData3 = (WData1-WData2) * FFTwindowshape # numpy.kaiser(SHOWsamples, 14) * 3
    WData1 = WData1 * FFTwindowshape # numpy.kaiser(SHOWsamples, 14) * 3
    WData2 = WData2 * FFTwindowshape # numpy.kaiser(SHOWsamples, 14) * 3
#
    WData1 = WData1 / 5.0
    WData2 = WData2 / 5.0
    WData3 = WData3 / 5.0

    # Save previous trace in memory for max or average trace
    FFTmemoryA = FFTresultA
    FFTmemoryB = FFTresultB
    if FreqTraceMode.get() == 3:
        PhaseMemoryA = PhaseA
        PhaseMemoryB = PhaseB
    
    # VA array
    fft_1 = czt_range(WData1, SAnum_bins, SAfreq_min, SAfreq_max, fs)
    PhaseA = numpy.angle(fft_1, deg=True)     # calculate angle
    FFTresultA = numpy.absolute(fft_1)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    FFTresultA = FFTresultA * FFTresultA
    FFTresultA = FFTresultA * Powcorr
    # VB array
    fft_2 = czt_range(WData2, SAnum_bins, SAfreq_min, SAfreq_max, fs)
    PhaseB = numpy.angle(fft_2, deg=True)     # calculate angle
    FFTresultB = numpy.absolute(fft_2)        # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    FFTresultB = FFTresultB * FFTresultB
    FFTresultB = FFTresultB * Powcorr
    # VA-VB array
    fft_3 = czt_range(WData3, SAnum_bins, SAfreq_min, SAfreq_max, fs)
    PhaseAB = numpy.angle(fft_3, deg=True)     # calculate angle
    FFTresultAB = numpy.absolute(fft_3)       # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    FFTresultAB = FFTresultAB * FFTresultAB
    FFTresultAB = FFTresultAB * Powcorr
#
    TRACEsize = int(len(FFTresultB))
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)
    if SpectrumScreenStatus.get() > 0:
        try:
            StartFrequency = float(StartFreqEntry.get())
        except:
            StartFreqEntry.delete(0,"end")
            StartFreqEntry.insert(0,100)
            StartFrequency = 100
        STARTsample = int(StartFrequency / Fsample)
    else:
        STARTsample = 0
    if LoopNum.get() == 1:
        PhaseMemoryB = PhaseB
        FSweepAdB = []
        FSweepBdB = []
        FSweepAPh = []
        FSweepBPh = []
        if NetworkScreenStatus.get() > 0:
            NSweepSeriesR = []
            NSweepSeriesX = []
            NSweepSeriesMag = [] # in ohms 
            NSweepSeriesAng = [] # in degrees
            NSweepParallelR = []
            NSweepParallelC = []
            NSweepParallelL = []
            NSweepSeriesC = []
            NSweepSeriesL = []
    if FreqTraceMode.get() == 1:      # Normal mode 1, do not change
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1

    if FreqTraceMode.get() == 2 and TRACEresetFreq == False:  # Peak hold mode 2, change v to peak value
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if len(FFTresultB) == len(FFTmemoryB):
            FFTresultB = numpy.maximum(FFTresultB, FFTmemoryB)#
    if FreqTraceMode.get() == 3 and TRACEresetFreq == False:  # Average mode 3, add difference / TRACEaverage to v
        try:
            FFTresultB = FFTmemoryB + (FFTresultB - FFTmemoryB) / TRACEaverage.get()
            PhaseB = PhaseMemoryB +(PhaseB - PhaseMemoryB) / TRACEaverage.get()
        except:
            FFTmemoryB = FFTresultB
            PhaseMemoryB = PhaseB
# 
    TRACEsize = int(len(FFTresultA))
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)
    if SpectrumScreenStatus.get() > 0:
        STARTsample = int(StartFrequency / Fsample)
    else:
        STARTsample = 0
    if LoopNum.get() == 1:
        PhaseMemoryA = PhaseA
    if FreqTraceMode.get() == 1:      # Normal mode 1, do not change
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1

    if FreqTraceMode.get() == 2 and TRACEresetFreq == False:  # Peak hold mode 2, change v to peak value
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
#
        if len(FFTresultA) == len(FFTmemoryA):
            FFTresultA = numpy.maximum(FFTresultA, FFTmemoryA)
    if FreqTraceMode.get() == 3 and TRACEresetFreq == False:  # Average mode 3, add difference / TRACEaverage to v
        try:
            FFTresultA = FFTmemoryA + (FFTresultA - FFTmemoryA) / TRACEaverage.get()
            PhaseA = PhaseMemoryA +(PhaseA - PhaseMemoryA) / TRACEaverage.get()
        except:
            FFTmemoryA = FFTresultA
            PhaseMemoryA = PhaseA
#
    if FSweepMode.get() > 0 and BodeScreenStatus.get() > 0:
        FSweepAdB.append(numpy.amax(FFTresultA))
        FSweepBdB.append(numpy.amax(FFTresultB))
        FSweepAPh.append(PhaseA[numpy.argmax(FFTresultA)])
        FSweepBPh.append(PhaseB[numpy.argmax(FFTresultB)]) 

    TRACEresetFreq = False          # Trace reset done
#
## Original FFT routime
def Old_DoFFT():            # Fast Fourier transformation
    global FFTBuffA, FFTBuffB, AWGAwaveform, AWGBwaveform
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P
    global FFTmemoryA, FFTresultA, FFTresultAB, PhaseAB
    global FFTmemoryB, FFTresultB
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global FFTwindowshape, FFTbandwidth, SMPfft
    global AWGSAMPLErate, StartFreqEntry, StopFreqEntry, StartBodeEntry
    global LoopNum, IA_Ext_Conf
    global STARTsample, STOPsample, CutDC, SHOWsamples
    global TRACEaverage, FreqTraceMode, FSweepMode
    global TRACEresetFreq, ZEROstuffing
    global SpectrumScreenStatus, IAScreenStatus, BodeScreenStatus
    global NetworkScreenStatus, NSweepSeriesR, NSweepSeriesX, NSweepSeriesMag, NSweepSeriesAng
    global NSweepParallelR, NSweepParallelC, NSweepParallelL, NSweepSeriesC, NSweepSeriesL

    # T1 = time.time()              # For time measurement of FFT routine
    REX = []
    PhaseA = []
    PhaseB = []
    # Convert list to numpy array REX for faster Numpy calculations
    # Take the first fft samples
    REX = numpy.array(FFTBuffA[0:SHOWsamples])    # Make a numpy arry of the list

    # Set Analog level display value MAX value is 5 volts for ALM1000
    REX = REX / 5.0

    # Do the FFT window function 
    REX = REX * FFTwindowshape[0:len(REX)]      # The windowing shape function only over the samples

    # Zero stuffing of array for better interpolation of peak level of signals
    ZEROstuffingvalue = int(2 ** ZEROstuffing.get())
    fftsamples = ZEROstuffingvalue * SHOWsamples      # Add zero's to the arrays

    # Save previous trace in memory for max or average trace
    FFTmemoryA = FFTresultA
    if FreqTraceMode.get() == 3:
        PhaseMemoryA = PhaseA

    # FFT with numpy 
    ALL = numpy.fft.fft(REX, n=fftsamples)  # Do FFT + zerostuffing till n=fftsamples with NUMPY  ALL = Real + Imaginary part
    PhaseA = numpy.angle(ALL, deg=True)     # calculate angle
    ALL = numpy.absolute(ALL)               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    ALL = ALL * ALL                         # Convert from Voltage to Power (P = (V*V) / R; R = 1)

    le = int(len(ALL) / 2)                  # Only half is used, other half is mirror
    # ALL = ALL[0:le]                       # So take only first half of the array
    FFTresultA = ALL[0:le]
    PhaseA = PhaseA[0:le]
    RMScorr = 1.0 / SHOWsamples # For VOLTAGE!
    Powcorr = 50*(RMScorr **2) # vpktage squared For POWER!
    FFTresultA = FFTresultA * Powcorr
#
    REX = []
    # Convert list to numpy array REX for faster Numpy calculations
    # Take the first fft samples
    REX = numpy.array(FFTBuffB[0:SHOWsamples])    # Make a numpy arry of the list

    # Set level display value MAX value is 5 volts for ALM1000
    REX = REX / 5.0

    # Do the FFT window function
    try:
        REX = REX * FFTwindowshape      # The windowing shape function only over the samples
    except:
        return
    # Zero stuffing of array for better interpolation of peak level of signals
    ZEROstuffingvalue = int(2 ** ZEROstuffing.get())
    fftsamples = ZEROstuffingvalue * SHOWsamples      # Add zero's to the arrays

    # Save previous trace in memory for max or average trace
    FFTmemoryB = FFTresultB
    if FreqTraceMode.get() == 3:
        PhaseMemoryB = PhaseB
    # FFT with numpy 
    ALL = numpy.fft.fft(REX, n=fftsamples)  # Do FFT + zerostuffing till n=fftsamples with NUMPY  ALL = Real + Imaginary part
    PhaseB = numpy.angle(ALL, deg=True)     # calculate angle
    ALL = numpy.absolute(ALL)               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    ALL = ALL * ALL                         # Convert from Voltage to Power (P = (U*U) / R; R = 1)

    le = int(len(ALL) / 2 )                 # Only half is used, other half is mirror
    # ALL = ALL[0:le]                       # So take only first half of the array
    FFTresultB = ALL[0:le]
    PhaseB = PhaseB[0:le]
    FFTresultB = FFTresultB * Powcorr
#
    if IA_Ext_Conf.get() == 1: # calculate fft for voltage A-B for use if IA set to config 2
        REX = []
        PhaseAB = []
        # Convert list to numpy array REX for faster Numpy calculations
        # Take the first fft samples
        REX = numpy.array(FFTBuffA[0:SMPfft]-FFTBuffB[0:SHOWsamples])    # Make a numpy arry of the VA-VB list

        # Set level display value MAX value is 5 volts for ALM1000
        REX = REX / 5.0

        # Do the FFT window function
        REX = REX * FFTwindowshape      # The windowing shape function only over the samples

        # Zero stuffing of array for better interpolation of peak level of signals
        ZEROstuffingvalue = int(2 ** ZEROstuffing.get())
        fftsamples = ZEROstuffingvalue * SHOWsamples      # Add zero's to the arrays

        # Save previous trace in memory for max or average trace
        # FFTmemoryB = FFTresultB
        # if FreqTraceMode.get() == 3:
            # PhaseMemoryB = PhaseB
        # FFT with numpy 
        ALL = numpy.fft.fft(REX, n=fftsamples)  # Do FFT + zerostuffing till n=fftsamples with NUMPY  ALL = Real + Imaginary part
        PhaseAB = numpy.angle(ALL, deg=True)     # calculate angle
        ALL = numpy.absolute(ALL)               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
        ALL = ALL * ALL                         # Convert from Voltage to Power (P = (U*U) / R; R = 1)

        le = len(ALL) / 2                       # Only half is used, other half is mirror
        #ALL = ALL[:le]                          # So take only first half of the array
        FFTresultAB = ALL[:le]
        PhaseAB = PhaseAB[:le]
        FFTresultAB = FFTresultAB * Powcorr
#
    if ShowAWGASA.get() > 0:
        FFTAWGA = AWGAwaveform
        DCA = 0.0
        if CutDC.get() == 1:
            DCA = numpy.average(FFTAWGA)
            FFTAWGA = FFTAWGA - DCA
        if len(AWGAwaveform) < SHOWsamples:
            Repeats = math.ceil(SMPfft/len(AWGAwaveform))
            i = 0
            while i < Repeats:
                FFTAWGA = numpy.concatenate((FFTAWGA, AWGAwaveform-DCA))
                i = i + 1
        REX = []
        # Convert list to numpy array REX for faster Numpy calculations
        # Take the first fft samples
        REX = numpy.array(FFTAWGA[0:SHOWsamples])    # Make a numpy arry of the list

        # Set level display value MAX value is 5 volts for ALM1000
        REX = REX / 5.0

        # Do the FFT window function
        try:
            REX = REX * FFTwindowshape      # The windowing shape function only over the samples
        except:
            return
        # Zero stuffing of array for better interpolation of peak level of signals
        ZEROstuffingvalue = int(2 ** ZEROstuffing.get())
        fftsamples = ZEROstuffingvalue * SHOWsamples      # Add zero's to the arrays
        # FFT with numpy 
        ALL = numpy.fft.fft(REX, n=fftsamples)  # Do FFT + zerostuffing till n=fftsamples with NUMPY  ALL = Real + Imaginary part
        #PhaseB = numpy.angle(ALL, deg=True)     # calculate angle
        ALL = numpy.absolute(ALL)               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
        ALL = ALL * ALL                         # Convert from Voltage to Power (P = (U*U) / R; R = 1)

        le = int(len(ALL) / 2 )                 # Only half is used, other half is mirror
        # ALL = ALL[0:le]                         # So take only first half of the array
        FFTresultAWGA = ALL[0:le]
        #PhaseB = PhaseB[0:le]
        FFTresultAWGA = FFTresultAWGA * Powcorr
#

#
    TRACEsize = int(len(FFTresultB))
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)
    if SpectrumScreenStatus.get() > 0:
        try:
            StartFrequency = float(StartFreqEntry.get())
        except:
            StartFreqEntry.delete(0,"end")
            StartFreqEntry.insert(0,100)
            StartFrequency = 100
        STARTsample = int(StartFrequency / Fsample)
    else:
        STARTsample = 0
    if LoopNum.get() == 1:
        PhaseMemoryB = PhaseB
        FSweepAdB = []
        FSweepBdB = []
        FSweepAPh = []
        FSweepBPh = []
        if NetworkScreenStatus.get() > 0:
            NSweepSeriesR = []
            NSweepSeriesX = []
            NSweepSeriesMag = [] # in ohms 
            NSweepSeriesAng = [] # in degrees
            NSweepParallelR = []
            NSweepParallelC = []
            NSweepParallelL = []
            NSweepSeriesC = []
            NSweepSeriesL = []
    if FreqTraceMode.get() == 1:      # Normal mode 1, do not change
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1

    if FreqTraceMode.get() == 2 and TRACEresetFreq == False:  # Peak hold mode 2, change v to peak value
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if len(FFTresultB) == len(FFTmemoryB):
            FFTresultB = numpy.maximum(FFTresultB, FFTmemoryB)#
    if FreqTraceMode.get() == 3 and TRACEresetFreq == False:  # Average mode 3, add difference / TRACEaverage to v
        try:
            FFTresultB = FFTmemoryB + (FFTresultB - FFTmemoryB) / TRACEaverage.get()
            PhaseB = PhaseMemoryB +(PhaseB - PhaseMemoryB) / TRACEaverage.get()
        except:
            FFTmemoryB = FFTresultB
            PhaseMemoryB = PhaseB
# 
    TRACEsize = int(len(FFTresultA))
    Fsample = float(AWGSAMPLErate / 2) / (TRACEsize - 1)
    if SpectrumScreenStatus.get() > 0:
        STARTsample = int(StartFrequency / Fsample)
    else:
        STARTsample = 0
    if LoopNum.get() == 1:
        PhaseMemoryA = PhaseA
    if FreqTraceMode.get() == 1:      # Normal mode 1, do not change
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1

    if FreqTraceMode.get() == 2 and TRACEresetFreq == False:  # Peak hold mode 2, change v to peak value
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample:TRACEsize])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
#
        if len(FFTresultA) == len(FFTmemoryA):
            FFTresultA = numpy.maximum(FFTresultA, FFTmemoryA)
    if FreqTraceMode.get() == 3 and TRACEresetFreq == False:  # Average mode 3, add difference / TRACEaverage to v
        try:
            FFTresultA = FFTmemoryA + (FFTresultA - FFTmemoryA) / TRACEaverage.get()
            PhaseA = PhaseMemoryA +(PhaseA - PhaseMemoryA) / TRACEaverage.get()
        except:
            FFTmemoryA = FFTresultA
            PhaseMemoryA = PhaseA
#
    if FSweepMode.get() > 0 and BodeScreenStatus.get() > 0:
        FSweepAdB.append(numpy.amax(FFTresultA))
        FSweepBdB.append(numpy.amax(FFTresultB))
        FSweepAPh.append(PhaseA[numpy.argmax(FFTresultA)])
        FSweepBPh.append(PhaseB[numpy.argmax(FFTresultB)]) 

    TRACEresetFreq = False          # Trace reset done
#
## calculate Spectrum traces
def MakeFreqTrace():        # Update the grid and trace
    global FFTmemoryA, FFTresultA
    global FFTmemoryB, FFTresultB
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMathSA
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM, PeakIndexA, PeakIndexB
    global PeakfreqA, PeakfreqB
    global DBdivindex   # Index value
    global DBdivlist    # dB per division list
    global DBlevel      # Reference level
    global GRHF,GRWF    # Screenheight, Screenwidth
    global AWGSAMPLErate, HScale, Fsample, SAMPLErate
    global StartFreqEntry, StopFreqEntry, PhCenFreqEntry, RelPhaseCenter
    global STARTsample, STOPsample, LoopNum, FSweepMode, FreqTraceMode
    global SAVScale, SAVPSD, SAvertmaxEntry, SAvertminEntry, SAvertmax, SAvertmin
    global T1Fline, T2Fline, TFMline, T1Pline, T2Pline, TAFline, TBFline
    global Vdiv         # Number of vertical divisions
    global X0LF, Y0TF   # Left top X value, Left top Y value
    global SAfreq_max, SAfreq_min, SAnum_bins, FBinWidth

    # Set the TRACEsize variable
    FFTsamples = len(FFTresultA)
    TRACEsize = 0
    try:
        StartFrequency = float(StartFreqEntry.get())
    except:
        StartFreqEntry.delete(0,"end")
        StartFreqEntry.insert(0,100)
        StartFrequency = 100
    try:
        StopFrequency = float(StopFreqEntry.get())
    except:
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,50000)
        StopFrequency = 50000
    if StartFrequency > StopFrequency :
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,50000)
        StopFrequency = 50000
    if StopFrequency < StartFrequency :
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,50000)
        StopFrequency = 50000
    try:
        Phasecenter = int(PhCenFreqEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenFreqEntry.delete(0,"end")
        PhCenFreqEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
    try: # from list ("10.0", "1.0" , "0.1", "10mV", "1mV", "100uV", "10uV", "1uV", "100nV" , "10nV")
        if SAvertmaxEntry.get() == "10.0":
            SAvertmax = 10.0
        elif SAvertmaxEntry.get() == "1.0":
            SAvertmax = 1.0
        elif SAvertmaxEntry.get() == "0.1":
            SAvertmax = 0.1
        elif SAvertmaxEntry.get() == "10mV":
            SAvertmax = 1.0E-2
        elif SAvertmaxEntry.get() == "1mV":
            SAvertmax = 1.0E-3
        elif SAvertmaxEntry.get() == "100uV":
            SAvertmax = 1.0E-4
        elif SAvertmaxEntry.get() == "10uV":
            SAvertmax = 1.0E-5
        elif SAvertmaxEntry.get() == "1uV":
            SAvertmax = 1.0E-6
        elif SAvertmaxEntry.get() == "100nV":
            SAvertmax = 1.0E-7
        elif SAvertmaxEntry.get() == "10nV":
            SAvertmax = 1.0E-8
        else:
            SAvertmax = float(SAvertmaxEntry.get())
        if SAvertmax < 0.0: # negative values not allowed
            SAvertmaxEntry.delete(0,"end")
            SAvertmaxEntry.insert(0, "1mV")
            SAvertmax = 1.0E-3
    except:
        SAvertmaxEntry.delete(0,"end")
        SAvertmaxEntry.insert(0, "1mV")
        SAvertmax = 1.0E-3
    try: # from list ("10.0", "1.0" , "0.1", "10mV", "1mV", "100uV", "10uV", "1uV", "100nV" , "10nV")
        if SAvertminEntry.get() == "10.0":
            SAvertmin = 10.0
        elif SAvertminEntry.get() == "1.0":
            SAvertmin = 1.0
        elif SAvertminEntry.get() == "0.1":
            SAvertmin = 0.1
        elif SAvertminEntry.get() == "10mV":
            SAvertmin = 1.0E-2
        elif SAvertminEntry.get() == "1mV":
            SAvertmin = 1.0E-3
        elif SAvertminEntry.get() == "100uV":
            SAvertmin = 1.0E-4
        elif SAvertminEntry.get() == "10uV":
            SAvertmin = 1.0E-5
        elif SAvertminEntry.get() == "1uV":
            SAvertmin = 1.0E-6
        elif SAvertminEntry.get() == "100nV":
            SAvertmin = 1.0E-7
        elif SAvertminEntry.get() == "10nV":
            SAvertmin = 1.0E-8
        else:
            SAvertmin = float(SAvertminEntry.get())
        if SAvertmin < 0.0: # negative values not allowed
            SAvertminEntry.delete(0,"end")
            SAvertminEntry.insert(0, "1uV")
            SAvertmin = 1.0E-6
    except:
        SAvertminEntry.delete(0,"end")
        SAvertminEntry.insert(0, "1uV")
        SAvertmin = 1.0E-6
    if ShowC1_VdB.get() == 1 or ShowMathSA.get() > 0:
        TRACEsize = len(FFTresultA)     # Set the trace length
    elif ShowC2_VdB.get() == 1 or ShowMathSA.get() > 0:
        TRACEsize = len(FFTresultB)
    #print(TRACEsize)
    if TRACEsize == 0:  # If no trace, skip rest of this routine
        return()
    if FSweepMode.get() > 0 and LoopNum.get() == NSteps.get():
        PhaseA = PhaseMemoryA
        PhaseB = PhaseMemoryB
    #
    FBinWidth = (SAfreq_max - SAfreq_min) / SAnum_bins # CZT done from start to stop
    # Vertical conversion factors (level dBs) and border limits
    Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()])     # Conversion factors, Yconv is the number of screenpoints per dB
    YVconv = float(GRHF) / (SAvertmax - SAvertmin) # * Vdiv.get()
    Yc = float(Y0TF) + Yconv * (DBlevel.get())  # Yc is the 0 dBm position, can be outside the screen!
    YVc = float(Y0TF) + YVconv * SAvertmax
    Ymin = Y0TF                  # Minimum position of screen grid (top)
    Ymax = Y0TF + GRHF            # Maximum position of screen grid (bottom)
    Yphconv = float(GRHF) / 360
    Yp = float(Y0TF) + Yphconv + 180
    # Horizontal conversion factors (frequency Hz) and border limits
    Fpixel = (SAfreq_max - SAfreq_min) / GRWF    # Frequency step per screen pixel
    Fsample = (SAfreq_max - SAfreq_min) / SAnum_bins  # CZT done from start to stop
    #
    try:
        LogFStop = math.log10(SAfreq_max)
    except:
        LogFStop = 0.0
    try:
        LogFStart = math.log10(SAfreq_min)
    except:
        LogFStart = 0.0
    LogFpixel = (LogFStop - LogFStart) / GRWF
    #
    try:
        LogVStop = math.log10(SAvertmax)
    except:
        LogVStop = 0.0
    try:
        LogVStart = math.log10(SAvertmin)
    except:
        LogVStart = -10
    LogVpixel = (LogVStop - LogVStart) / GRHF
    ## CZT done from start to stop
    STARTsample = int(SAfreq_min / Fsample)   # First sample in FFTresult[] that is used
    # print("SAfreq_min = ", SAfreq_min, "Fsample = ", Fsample )
    #print("Start Sample: ", STARTsample)
    STARTsample = 1   # First within screen range
    STOPsample = SAnum_bins - 1 #
    #print("Stop Sample: ", STOPsample)
    MAXsample = SAnum_bins - 1                      # Just an out of range check
    if STARTsample > (MAXsample - 1):
        STARTsample = MAXsample - 1

    if STOPsample > MAXsample:
        STOPsample = MAXsample

    T1Fline = []
    T2Fline = []
    TAFline = []
    TBFline = []
    T1Pline = []
    T2Pline = []
    TFMline = []
    #print("Start Sample: ", STARTsample)
    #print("Start Freq: ", STARTsample * Fsample)
    n = STARTsample
    PeakIndexA = PeakIndexB = n
    PeakdbA = PeakdbB = PeakMdb = -200 # PeakdbB
    while n < STOPsample:
        F = (n * Fsample) + SAfreq_min
        if HScale.get() == 1:
            try:
                LogF = math.log10(F) # convet to log Freq
                x = X0LF + (LogF - LogFStart)/LogFpixel
            except:
                x = X0LF
        else:
            x = X0LF + (F / Fpixel ) # - SAfreq_min
        if x < X0LF:
            x = X0LF
        if ShowC1_VdB.get() == 1: 
            T1Fline.append(int(x + 0.5))
            try:
                if SAVScale.get() == 0:
                    if SAVPSD.get() == 1:
                        dbA = 10 * math.log10(float(FFTresultA[n])/math.sqrt(FBinWidth))   
                    else:
                        dbA = 10 * math.log10(float(FFTresultA[n])) # Convert power to DBs                 
                    ya = Yc - Yconv * dbA
                else:
                    dbA = 10 * math.log10(float(FFTresultA[n]))   # Convert power to DBs
                    V = 10.0**(dbA/20.0)# convert back to RMS Volts
                    if SAVPSD.get() == 1:
                        V = V/math.sqrt(FBinWidth) # per root Hz
                    if SAVScale.get() == 2:
                        try:
                            LogV = math.log10(V) # convet to log Volts
                            ya = YVc - (LogV - LogVStart)/LogVpixel
                        except:
                            ya = YVc - YVconv * V
                    else:
                        ya = YVc - YVconv * V
            except:
                ya = Ymax
            if (ya < Ymin):
                ya = Ymin
            if (ya > Ymax):
                ya = Ymax
            if dbA > PeakdbA:
                PeakdbA = dbA
                PeakyA = int(ya + 0.5)
                PeakxA = int(x + 0.5)
                PeakfreqA = F
                PeakIndexA = n
            T1Fline.append(int(ya + 0.5))
        if ShowC2_VdB.get() == 1:
            T2Fline.append(int(x + 0.5))
            try:
                if SAVScale.get() == 0:
                    if SAVPSD.get() == 1:
                        dbB = 10 * math.log10(float(FFTresultB[n])/math.sqrt(FBinWidth))   
                    else:
                        dbB = 10 * math.log10(float(FFTresultB[n])) # Convert power to DBs 
                    yb = Yc - Yconv * dbB
                else:
                    dbB = 10 * math.log10(float(FFTresultB[n]))   # Convert power to DBs
                    V = 10.0**(dbB/20.0)# RMS Volts
                    if SAVPSD.get() == 1:
                        V = V/math.sqrt(FBinWidth) # per root Hz
                    if SAVScale.get() == 2:
                        try:
                            LogV = math.log10(V) # convet to log Volts
                            yb = YVc - (LogV - LogVStart)/LogVpixel
                        except:
                            yb = YVc - YVconv * V
                    else:
                        yb = YVc - YVconv * V
            except:
                yb = Ymax
            if (yb < Ymin):
                yb = Ymin
            if (yb > Ymax):
                yb = Ymax
            if dbB > PeakdbB:
                PeakdbB = dbB
                PeakyB = int(yb + 0.5)
                PeakxB = int(x + 0.5)
                PeakfreqB = F
                PeakIndexB = n
            T2Fline.append(int(yb + 0.5))
        
        if ShowC1_P.get() == 1:
            T1Pline.append(int(x + 0.5))
            if FSweepMode.get() > 0:
                RelPhase = PhaseMemoryA[n]-PhaseMemoryB[n]
            else:
                RelPhase = PhaseA[n]-PhaseB[n]
            RelPhase = RelPhase - Phasecenter
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            RelPhase = RelPhase - 20.0
            ya = Yp - Yphconv * RelPhase
            T1Pline.append(int(ya + 0.5))
        if ShowC2_P.get() == 1:
            T2Pline.append(int(x + 0.5))
            if FSweepMode.get() > 0:
                RelPhase = PhaseMemoryB[n]-PhaseMemoryA[n]
            else:
                RelPhase = PhaseB[n]-PhaseA[n]
            RelPhase = RelPhase - Phasecenter
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            RelPhase = RelPhase - 20.0
            ya = Yp - Yphconv * RelPhase
            T2Pline.append(int(ya + 0.5))
        if ShowMathSA.get() > 0:
            TFMline.append(int(x + 0.5))
            if SAVPSD.get() == 1:
                dbA = 10 * math.log10(float(FFTresultA[n])/math.sqrt(FBinWidth)) # Convert power to DBs 
                dbB = 10 * math.log10(float(FFTresultB[n])/math.sqrt(FBinWidth))
            else: 
                dbA = 10 * math.log10(float(FFTresultA[n])) # Convert power to DBs
                dbB = 10 * math.log10(float(FFTresultB[n]))
            if ShowMathSA.get() == 1:
                MdB = dbA - dbB
            elif ShowMathSA.get() == 2:
                MdB = dbB - dbA
            yb = Yc - Yconv * MdB
            if (yb < Ymin):
                yb = Ymin
            if (yb > Ymax):
                yb = Ymax
            if MdB > PeakMdb:
                PeakMdb = MdB
                PeakyM = int(yb + 0.5)
                PeakxM = int(x + 0.5)
                PeakfreqM = F
            TFMline.append(int(yb + 0.5))
        n = n + 1
#
## make Bode Plot Traces
def MakeBodeTrace():        # Update the grid and trace
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMathBP
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB
    global DBdivindexBP   # Index value
    global DBdivlist    # dB per division list
    global DBlevelBP      # Reference level
    global GRHBP          # Screenheight
    global GRWBP          # Screenwidth
    global AWGSAMPLErate, HScaleBP, RUNstatus, SAMPLErate, MaxSampleRate
    global StartBodeEntry, StopBodeEntry, SMPfft
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global FreqTraceMode, RelPhaseCenter, PhCenBodeEntry, ImCenBodeEntry, ImpedanceCenter, Impedcenter
    global TAFline, TBFline, TBPMline, TAPline, TBPline
    global Vdiv         # Number of vertical divisions
    global X0LBP        # Left top X value
    global Y0TBP        # Left top Y value
    global ResScale, NetworkScreenStatus, Show_Rseries, NSweepSeriesR, Show_Xseries, NSweepSeriesX
    global Show_Magnitude, NSweepSeriesMag, Show_Angle, NSweepSeriesAng
    global TIARline, TIAXline, TIAMagline, TIAAngline, CurrentFreqX

    # Set the TRACEsize variable
    TRACEsize = 0
    if ShowCA_VdB.get() == 1 or ShowMathBP.get() > 0:
        TRACEsize = len(FStep)     # Set the trace length
    elif ShowCB_VdB.get() == 1 or ShowMathBP.get() > 0:
        TRACEsize = len(FStep)
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        return()
    #
    try:
        EndFreq = float(StopBodeEntry.get())
    except:
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,10000)
        EndFreq = 10000
    try:
        BeginFreq = float(StartBodeEntry.get())
    except:
        StartBodeEntry.delete(0,"end")
        StartBodeEntry.insert(0,100)
        BeginFreq = 100
    try:
        Phasecenter = float(PhCenBodeEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenBodeEntry.delete(0,"end")
        PhCenBodeEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
    try:
        Impedcenter = float(ImCenBodeEntry.get())
        ImpedanceCenter.set(Impedcenter)
    except:
        ImCenBodeEntry.delete(0,"end")
        ImCenBodeEntry.insert(0,0)
        ImpedanceCenter.set(0)
        Impedcenter = 0
    #
    HalfSAMPLErate = SAMPLErate/2
    BeginIndex = int((BeginFreq/HalfSAMPLErate)*16384)
    EndIndex = int((EndFreq/HalfSAMPLErate)*16384)
    CurrentFreqX = X0LBP + 14
    if FSweepMode.get() > 0 and len(FSweepAdB) > 4:
        # Vertical conversion factors (level dBs) and border limits
        Yconv = float(GRHBP) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()])     # Conversion factors, Yconv is the number of screenpoints per dB
        Yc = float(Y0TBP) + Yconv * (DBlevelBP.get())  # Yc is the 0 dBm position, can be outside the screen!
        Ymin = Y0TBP                  # Minimum position of screen grid (top)
        Ymax = Y0TBP + GRHBP            # Maximum position of screen grid (bottom)
        Yphconv = float(GRHBP) / 360 # degrees per pixel
        Yp = float(Y0TBP) + Yphconv + 180
        x1 = X0LBP + 14
        # Horizontal conversion factors (frequency Hz) and border limits
        Fpixel = (EndFreq - BeginFreq) / GRWBP    # Frequency step per screen pixel   
        LogFStop = math.log10(EndFreq)
        try:
            LogFStart = math.log10(BeginFreq)
        except:
            LogFStart = 0.0
        LogFpixel = (LogFStop - LogFStart) / GRWBP
        TAFline = []
        TBFline = []
        TAPline = []
        TBPline = []
        TIARline = []
        TIAXline = []
        TIAMagline = []
        TIAAngline = []
        TBPMline = []
        PeakdbA = -200
        PeakdbB = -200
        PeakMdb = -200
        n = 0
        for n in range(len(FSweepAdB)): # while n < len(FStep):
            if n < len(FStep): # check if n has gone out off bounds because user did something dumb
                F = FStep[n] # look up frequency bin in list of bins
            else:
                F = FStep[0]
            if F >= BeginFreq and F <= EndFreq:
                if HScaleBP.get() == 1:
                    try:
                        LogF = math.log10(F) # convet to log Freq
                        x = x1 + (LogF - LogFStart)/LogFpixel
                    except:
                        x = x1
                else:
                    x = x1 + (F - BeginFreq)  / Fpixel
                CurrentFreqX = x
                if ShowCA_VdB.get() == 1: 
                    TAFline.append(int(x + 0.5))
                    try:
                        dbA = 10 * math.log10(float(FSweepAdB[n]))   # Convert power to DBs, except for log(0) error
                        ya = Yc - Yconv * dbA  
                    except:
                        ya = Ymax
                    if (ya < Ymin):
                        ya = Ymin
                    if (ya > Ymax):
                        ya = Ymax
                    if dbA > PeakdbA:
                        PeakdbA = dbA
                        PeakyA = int(ya + 0.5)
                        PeakxA = int(x + 0.5)
                        PeakfreqA = F
                    TAFline.append(int(ya + 0.5))
                if ShowCB_VdB.get() == 1:
                    TBFline.append(int(x + 0.5))
                    try:
                        dbB = 10 * math.log10(float(FSweepBdB[n]))
                        yb = Yc - Yconv * dbB 
                    except:
                        yb = Ymax
                    if (yb < Ymin):
                        yb = Ymin
                    if (yb > Ymax):
                        yb = Ymax
                    if dbB > PeakdbB:
                        PeakdbB = dbB
                        PeakyB = int(yb + 0.5)
                        PeakxB = int(x + 0.5)
                        PeakfreqB = F
                    TBFline.append(int(yb + 0.5))
                if ShowCA_P.get() == 1:
                    TAPline.append(int(x + 0.5))
                    RelPhase = FSweepAPh[n] - FSweepBPh[n]
                    RelPhase = RelPhase - Phasecenter
                    if RelPhase > 180:
                        RelPhase = RelPhase - 360
                    elif RelPhase < -180:
                        RelPhase = RelPhase + 360
                    ya = Yp - Yphconv * RelPhase
                    TAPline.append(int(ya + 0.5))
                if ShowCB_P.get() == 1:
                    TBPline.append(int(x + 0.5))
                    RelPhase = FSweepBPh[n] - FSweepAPh[n]
                    RelPhase = RelPhase - Phasecenter
                    if RelPhase > 180:
                        RelPhase = RelPhase - 360
                    elif RelPhase < -180:
                        RelPhase = RelPhase + 360
                    ya = Yp - Yphconv * RelPhase
                    TBPline.append(int(ya + 0.5))
                if ShowMathBP.get() > 0:
                    TBPMline.append(int(x + 0.5))
                    dbA = 10 * math.log10(float(FSweepAdB[n])) # Convert power to DBs, except for log(0) error
                    dbB = 10 * math.log10(float(FSweepBdB[n])) 
                    if ShowMathBP.get() == 1:
                        MdB = dbA - dbB
                    elif ShowMathBP.get() == 2:
                        MdB = dbB - dbA
                    yb = Yc - Yconv * MdB
                    if (yb < Ymin):
                        yb = Ymin
                    if (yb > Ymax):
                        yb = Ymax
                    if MdB > PeakMdb:
                        PeakMdb = MdB
                        PeakyM = int(yb + 0.5)
                        PeakxM = int(x + 0.5)
                        PeakfreqM = F
                    TBPMline.append(int(yb + 0.5))
# draw impedance trace if necessary
        if NetworkScreenStatus.get() > 0:
            ycenter = Y0TBP + (GRHBP/2)
            OhmsperPixel = float(ResScale.get())*Vdiv.get()/GRHBP
            n = 0
            for n in range(len(NSweepSeriesR)): # while n < len(FStep):
                if n < len(FStep): # check if n has gone out off bounds because user did something dumb
                    F = FStep[n] # look up frequency bin in list of bins
                else:
                    F = FStep[0]
                if F >= BeginFreq and F <= EndFreq:
                    if HScaleBP.get() == 1:
                        try:
                            LogF = math.log10(F) # convet to log Freq
                            x = x1 + (LogF - LogFStart)/LogFpixel
                        except:
                            x = x1 
                    else:
                        x = x1 + (F - BeginFreq)  / Fpixel
                    if Show_Rseries.get() == 1:
                        TIARline.append(int(x + 0.5))
                        y1 = ycenter - ((NSweepSeriesR[n]-Impedcenter) / OhmsperPixel)
                        if (y1 < Ymin):
                            y1 = Ymin
                        if (y1 > Ymax):
                            y1 = Ymax
                        TIARline.append(y1)
                    if Show_Xseries.get() == 1:
                        TIAXline.append(int(x + 0.5))
                        y1 = ycenter - ((NSweepSeriesX[n]-Impedcenter) / OhmsperPixel)
                        if (y1 < Ymin):
                            y1 = Ymin
                        if (y1 > Ymax):
                            y1 = Ymax
                        TIAXline.append(y1)
                    if Show_Magnitude.get() == 1:
                        TIAMagline.append(int(x + 0.5))
                        y1 = ycenter - ((NSweepSeriesMag[n]-Impedcenter) / OhmsperPixel)
                        if (y1 < Ymin):
                            y1 = Ymin
                        if (y1 > Ymax):
                            y1 = Ymax
                        TIAMagline.append(y1)
                    if Show_Angle.get() == 1:
                        TIAAngline.append(int(x + 0.5))
                        y1 = ycenter - Yphconv * (NSweepSeriesAng[n]-Phasecenter)
                        if (y1 < Ymin):
                            y1 = Ymin
                        if (y1 > Ymax):
                            y1 = Ymax
                        TIAAngline.append(y1)                            
#
## Draw Bode plot screen
def MakeBodeScreen():       # Update the screen with traces and text
    global CANVASheightBP, CANVASwidthBP, SmoothCurvesBP
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    global COLORgrid    # The colors
    global COLORsignalband, COLORtext
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6, COLORtrace7
    global FSweepMode, LoopNum, MarkerFreqNum, TRACEwidth, GridWidth
    global DBdivindexBP   # Index value
    global DBdivlist    # dB per division list
    global DBlevelBP      # Reference level
    global FFTwindow, FFTbandwidth, ZEROstuffing, FFTwindowname
    global X0LBP          # Left top X value
    global Y0TBP          # Left top Y value
    global GRWBP          # Screenwidth
    global GRHBP          # Screenheight
    global FontSize
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global AWGSAMPLErate, HScaleBP, SAMPLErate, MaxSampleRate
    global SHOWsamples      # number of FFT samples
    global StartBodeEntry, StopBodeEntry
    global ShowCA_P, ShowCB_P, ShowRA_VdB, ShowRB_VdB, ShowMarkerBP
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP
    global ShowMathBP, BodeDisp, RelPhaseCenter, PhCenBodeEntry, ImCenBodeEntry, ImpedanceCenter, Impedcenter
    global ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global Show_Rseries, Show_Xseries, Show_Magnitude, Show_Angle, NetworkScreenStatus
    global Show_RseriesRef, Show_XseriesRef, Show_MagnitudeRef, Show_AngleRef
    global TAFline, TBFline, TAPline, TAFRline, TBFRline, TBPMline, TBPRMline
    global TAPRline, TBPRline
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv, ResScale # Number of vertical divisions
    global TIARline, TIAXline, TIAMagline, TIAAngline, CurrentFreqX
    global RefIARline, RefIAXline, RefIAMagline, RefIAAngline

    # Delete all items on the screen
    MarkerFreqNum = 0
    Bodeca.delete(ALL) # remove all items

    try:
        EndFreq = float(StopBodeEntry.get())
    except:
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,10000)
        EndFreq = 10000
    try:
        BeginFreq = float(StartBodeEntry.get())
    except:
        StartBodeEntry.delete(0,"end")
        StartBodeEntry.insert(0,100)
        BeginFreq = 100
    try:
        Phasecenter = float(PhCenBodeEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenBodeEntry.delete(0,"end")
        PhCenBodeEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
    try:
        Impedcenter = float(ImCenBodeEntry.get())
        ImpedanceCenter.set(Impedcenter)
    except:
        ImCenBodeEntry.delete(0,"end")
        ImCenBodeEntry.insert(0,0)
        ImpedanceCenter.set(0)
        Impedcenter = 0
    #
    # Draw horizontal grid lines
    i = 0
    x1 = X0LBP + 14
    x2 = x1 + GRWBP
    while (i <= Vdiv.get()):
        y = Y0TBP + i * GRHBP/Vdiv.get()
        Dline = [x1,y,x2,y]
        if i == 0 or i == Vdiv.get():
            Bodeca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
        else:
            Bodeca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
        Vaxis_value = (DBlevelBP.get() - (i * DBdivlist[DBdivindexBP.get()]))
        Vaxis_label = str(Vaxis_value)
        Bodeca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
        if ShowCA_P.get() == 1 or ShowCB_P.get() == 1 or Show_Angle.get() == 1:
            Vaxis_value = ( 180 - ( i * (360 / Vdiv.get()))) + Phasecenter
            Vaxis_label = str(Vaxis_value)
            Bodeca.create_text(x2+3, y, text=Vaxis_label, fill=COLORtrace3, anchor="w", font=("arial", FontSize ))
        if NetworkScreenStatus.get() > 0:
            if Show_Rseries.get() == 1 or Show_Xseries.get() == 1 or Show_Magnitude.get() == 1:
                RperDiv = float(ResScale.get())
                Vaxis_value = ( (RperDiv * Vdiv.get()/2) - (i * RperDiv) ) + Impedcenter
                if Vaxis_value > 500 or Vaxis_value < -500:
                    Vaxis_value = Vaxis_value/1000.0
                    if Vaxis_value > 5 or Vaxis_value < -5:
                        Vaxis_label = ' {0:.0f}'.format(Vaxis_value) + 'K'
                    else:
                        Vaxis_label = ' {0:.1f}'.format(Vaxis_value) + 'K'
                elif Vaxis_value > 50 or Vaxis_value < -50:
                    Vaxis_label = ' {0:.1f} '.format(Vaxis_value)
                elif Vaxis_value > 5 or Vaxis_value < -55:
                    Vaxis_label = ' {0:.2f} '.format(Vaxis_value)
                else:
                    Vaxis_label = ' {0:.3f} '.format(Vaxis_value)
                Bodeca.create_text(x1-23, y, text=Vaxis_label, fill=COLORtrace5, anchor="e", font=("arial", FontSize ))
        i = i + 1
    # Draw vertical grid lines
    i = 0
    y1 = Y0TBP
    y2 = Y0TBP + GRHBP
    if HScaleBP.get() == 1:
        F = 1.0
        LogFStop = math.log10(EndFreq)
        try:
            LogFStart = math.log10(BeginFreq)
        except:
            LogFStart = 0.0
        LogFpixel = (LogFStop - LogFStart) / GRWBP
        # draw left and right edges
        while F <= EndFreq:
            if F >= BeginFreq:
                try:
                    LogF = math.log10(F) # convet to log Freq
                    x = x1 + (LogF - LogFStart)/LogFpixel
                except:
                    x = x1
                Dline = [x,y1,x,y2]
                if F == 1 or F == 10 or F == 100 or F == 1000 or F == 10000 or F == 100000:
                    Bodeca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    axis_label = str(F)
                    Bodeca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
                else:
                    Bodeca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
                
            if F < 10:
                F = F + 1
            elif F < 100:
                F = F + 10
            elif F < 1000:
                F = F + 100
            elif F < 1000:
                F = F + 100
            elif F < 10000:
                F = F + 1000
            elif F < 100000:
                F = F + 10000
            elif F < 200000:
                F = F + 10000
    else:
        Freqdiv = (EndFreq - BeginFreq) / 10
        while (i < 11):
            x = x1 + i * GRWBP/10
            Dline = [x,y1,x,y2]
            if i == 0 or i == 10:
                Bodeca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                Bodeca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            axis_value = BeginFreq + (i * Freqdiv)
            axis_label = str(axis_value)
            Bodeca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
            i = i + 1
    # Draw X - Y cursors if needed
    Fpixel = (EndFreq - BeginFreq) / GRWBP # Frequency step per screen pixel
    LogFStop = math.log10(EndFreq)
    try:
        LogFStart = math.log10(BeginFreq)
    except:
        LogFStart = 0.0
    LogFpixel = (LogFStop - LogFStart) / GRWBP
    if ShowBPCur.get() > 0:
        Dline = [BPCursor, Y0TBP, BPCursor, Y0TBP+GRHBP]
        Bodeca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScaleBP.get() == 1:
            xfreq = 10**(((BPCursor-x1)*LogFpixel) + LogFStart)
        else:
            xfreq = ((BPCursor-x1)*Fpixel)+BeginFreq
        XFString = ' {0:.2f} '.format(xfreq)
        V_label = XFString + " Hz"
        Bodeca.create_text(BPCursor, Y0TBP+GRHBP+6, text=V_label, fill=COLORtext, anchor="n", font=("arial", FontSize ))
        #Bodeca.create_text(BPCursor+1, BdBCursor-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
#
    if ShowBdBCur.get() > 0:
        Dline = [x1, BdBCursor, x1+GRWBP, BdBCursor]
        Bodeca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        if ShowBdBCur.get() == 1:
            # Vertical conversion factors (level dBs) and border limits
            Yconv = float(GRHBP) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
            Yc = float(Y0TBP) + Yconv * (DBlevelBP.get()) # Yc is the 0 dBm position, can be outside the screen!
            yvdB = ((Yc-BdBCursor)/Yconv)
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " dBV"
        else:
            # Vertical conversion factors (level degrees) and border limits
            Yconv = float(GRHBP) / 360.0 # Conversion factors, Yconv is the number of screenpoints per degree
            Yc = float(Y0TBP)  # Yc is the 180 degree position
            yvdB = 180 + ((Yc-BdBCursor)/Yconv) + Phasecenter
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " Deg"
        Bodeca.create_text(x1+GRWBP+1, BdBCursor, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
        #Bodeca.create_text(BPCursor+1, BdBCursor+5, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
    #
    SmoothBool = SmoothCurvesBP.get()
    # Draw traces
    if len(TAFline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHA
        if OverRangeFlagA == 1:
            Bodeca.create_line(TAFline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Bodeca.create_line(TAFline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbA) + ',' + ' {0:.1f} '.format(PeakfreqA)
            Bodeca.create_text(PeakxA, PeakyA, text=Peak_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
    if len(TBFline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHB
        if OverRangeFlagB == 1:
            Bodeca.create_line(TBFline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Bodeca.create_line(TBFline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbB) + ',' + ' {0:.1f} '.format(PeakfreqB)
            Bodeca.create_text(PeakxB, PeakyB, text=Peak_label, fill=COLORtrace2, anchor="w", font=("arial", FontSize ))
    if len(TAPline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Bodeca.create_line(TAPline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TBPline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Bodeca.create_line(TBPline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowCA_RdB.get() == 1 and len(TAFRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TAFRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRA) + ',' + ' {0:.1f} '.format(PeakfreqRA)
            Bodeca.create_text(PeakxRA, PeakyRA, text=Peak_label, fill=COLORtraceR1, anchor="e", font=("arial", FontSize ))
    if ShowCB_RdB.get() == 1 and len(TBFRline) > 4:   # Write the ref trace B if active
        Bodeca.create_line(TBFRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRB) + ',' + ' {0:.1f} '.format(PeakfreqRB)
            Freqca.create_text(PeakxRB, PeakyRB, text=Peak_label, fill=COLORtraceR2, anchor="w", font=("arial", FontSize ))
    if ShowCA_RP.get() == 1 and len(TAPRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TAPRline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowCB_RP.get() == 1 and len(TBPRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TBPRline, fill=COLORtraceR4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMathBP.get() > 0 and len(TBPMline) > 4:   # Write the Math trace if active
        Bodeca.create_line(TBPMline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakMdb) + ',' + ' {0:.1f} '.format(PeakfreqM)
            Bodeca.create_text(PeakxM, PeakyM, text=Peak_label, fill=COLORtrace5, anchor="w", font=("arial", FontSize ))
    if ShowRMathBP.get() == 1 and len(TBPRMline) > 4:   # Write the ref math trace if active
        Bodeca.create_line(TBPRMline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakRMdb) + ',' + ' {0:.1f} '.format(PeakfreqRM)
            Bodeca.create_text(PeakxRM, PeakyRM, text=Peak_label, fill=COLORtraceR5, anchor="w", font=("arial", FontSize ))
    if Show_Rseries.get() == 1 and len(TIARline) > 4:
        Bodeca.create_line(TIARline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if Show_Xseries.get() == 1 and len(TIAXline) > 4:
        Bodeca.create_line(TIAXline, fill=COLORtrace6, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if Show_Magnitude.get() == 1 and len(TIAMagline) > 4:
        Bodeca.create_line(TIAMagline, fill=COLORtrace7, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if Show_Angle.get() == 1 and len(TIAAngline) > 4:
        Bodeca.create_line(TIAAngline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if Show_RseriesRef.get() == 1 and len(RefIARline) > 4:
        Bodeca.create_line(RefIARline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if Show_XseriesRef.get() == 1 and len(RefIAXline) > 4:
        Bodeca.create_line(RefIAXline, fill=COLORtraceR6, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if Show_MagnitudeRef.get() == 1 and len(RefIAMagline) > 4:
        Bodeca.create_line(RefIAMagline, fill=COLORtraceR7, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if Show_AngleRef.get() == 1 and len(RefIAAngline) > 4:
        Bodeca.create_line(RefIAAngline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())

    Dline = [CurrentFreqX, Y0TBP, CurrentFreqX, Y0TBP+GRHBP]
    Bodeca.create_line(Dline, dash=(2,2), fill=COLORgrid, width=GridWidth.get())
    if HScaleBP.get() == 1:
        xfreq = 10**(((CurrentFreqX-x1)*LogFpixel) + LogFStart)
    else:
        xfreq = ((CurrentFreqX-x1)*Fpixel)+BeginFreq
    XFString = ' {0:.0f} '.format(xfreq)
    V_label = XFString + " Hz"
    Bodeca.create_text(CurrentFreqX, Y0TBP+GRHBP+1, text=V_label, fill=COLORtext, anchor="n", font=("arial", FontSize ))
    # General information on top of the grid
    SR_label = ' {0:.1f} '.format(SAMPLErate)
    txt = " Sample rate: " + SR_label
    txt = txt + " FFT samples: " + str(SHOWsamples)

    txt = txt + " " + FFTwindowname
        
    x = X0LBP
    y = 12
    idTXT = Bodeca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))

    # Start and stop frequency and dB/div and trace mode
    txt = str(BeginFreq) + " to " + str(EndFreq) + " Hz"
    txt = txt + " " + str(DBdivlist[DBdivindexBP.get()]) + " dB/div"
    txt = txt + " Level: " + str(DBlevelBP.get()) + " dB "
    txt = txt + " FFT Bandwidth = " + ' {0:.2f} '.format(FFTbandwidth)
    
    x = X0LBP
    y = Y0TBP+GRHBP+23
    idTXT = Bodeca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    
    if FreqTraceMode.get() == 1:
        txt ="Normal mode "

    if FreqTraceMode.get() == 2:
        txt = "Peak hold mode "
    
    if FreqTraceMode.get() == 3:
        txt = "Power average  mode (" + str(TRACEaverage.get()) + ") " 

    if ZEROstuffing.get() > 0:
        txt = txt + " Zero Stuffing = " + str(ZEROstuffing.get())
    # Runstatus and level information
    if (RUNstatus.get() == 0):
        txt = txt + " Stopped "
    else:
        if BodeDisp.get() == 1:
            txt = txt + " Running "
        else:
            txt = txt + " Display off "
    if FSweepMode.get() > 0:
        txt = txt + " Freq Step = " + str(LoopNum.get())
    x = X0LBP
    y = Y0TBP+GRHBP+34
    IDtxt  = Bodeca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
#
## Impedance analyzer routines -----
def UpdateIAAll():        # Update Data, trace and screen
    global FFTresultA, FFTresultB
    global SHOWsamples
    
    if len(FFTresultA) < SHOWsamples and len(FFTresultB) < SHOWsamples:
        return
    MakeIATrace()         # Update the traces
    UpdateIAScreen()      # Update the screen 

def UpdateIATrace():      # Update trace and screen
    MakeIATrace()         # Update traces
    UpdateIAScreen()      # Update the screen

def UpdateIAScreen():     # Update screen with trace and text
    MakeIAScreen()        # Update the screen
    root.update()       # Activate updated screens    
#
## Calculate Impedance from relative amplitude and phase
def DoImpedance():
# Input Variables
    global PeakdbA, PeakdbB, PeakRelPhase, PeakdbAB
    global SAfreq_max, SAfreq_min, SAnum_bins, FBinWidth # number of FFT samples
    #(VZ/VA)from vector voltmeter 
    # global VVangle # angle in degrees between VZ and VA 
    global RsystemEntry # resistance of series resistor or power divider  
# Computed outputs 
    # global VVangleCosine # cosine of vector voltmeter angle 
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries, ImpedanceXseries # in ohms 
    global IA_Ext_Conf, IA_Mode
    
    DEG2RAD = (math.pi / 180.0)
    SMALL = 1E-20
    try:
        ResValue = float(RsystemEntry.get())
    except:
        ResValue = 1000.0
        
    VA = math.pow(10,(PeakdbA/20))
    VB = math.pow(10,(PeakdbB/20))
    VVangleCosine = math.cos(math.radians(PeakRelPhase))
    if IA_Mode.get() == 0:
        if IA_Ext_Conf.get() == 1:
            VAB = math.pow(10,(PeakdbAB/20))
            VZ = VAB # VZ=VA-VB
            # VI = VB
        else:
            VZ = VB # VZ=VB
        VI = math.sqrt(VA**2 + VZ**2 - 2*VA*VZ*VVangleCosine)
        costheta = (VA**2 + VI**2 - VZ**2)/(2 * VA * VI) 
        Za = ResValue * VA / VI
        ImpedanceRseries = Za * costheta - ResValue
        ImpedanceMagnitude = ResValue * VZ / VI
    else:
        # VI=VB
        VZ = math.sqrt(VA**2 + VB**2 - 2*VA*VB*VVangleCosine)
        costheta = (VA**2 + VB**2 - VZ**2)/(2 * VA * VB) 
        Za = ResValue * VA / VB
        ImpedanceRseries = Za * costheta - ResValue
        ImpedanceMagnitude = ResValue * VZ / VB
        # invert relative phase
        PeakRelPhase = 0.0 - PeakRelPhase
        
    # don't try to take square root of a negative number)
    ImpedanceXseries = math.sqrt(abs(ImpedanceMagnitude**2 - ImpedanceRseries**2))
    if(PeakRelPhase < 0.0):
        ImpedanceXseries = -ImpedanceXseries
        if IA_Ext_Conf.get() == 1:
            ImpedanceRseries = -ImpedanceRseries
    ImpedanceAngle = math.atan2(ImpedanceXseries, ImpedanceRseries) / DEG2RAD
#
## Calculate Impedance traces
def MakeIATrace():        # Update the grid and trace
    global FFTmemoryA, FFTresultA, FFTresultAB, PhaseAB
    global FFTmemoryB, FFTresultB
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB, PeakRelPhase, PeakdbAB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM, PeakphaseA, PeakphaseB 
    global PeakfreqA, PeakfreqB, GainCorEntry, PhaseCorEntry, PhaseCorrection
    global DBdivindex   # Index value
    global DBdivlist    # dB per division list
    global DBlevel      # Reference level
    global GRHIA          # Screenheight
    global GRWIA          # Screenwidth
    global AWGSAMPLErate, SAMPLErate, SHOWsamples
    global SAfreq_max, SAfreq_min, SAnum_bins, FBinWidth       # number of FFT samples
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global TRACEmode, IA_Ext_Conf
    global T1Vline, T2Vline, TMline, T1Pline, T2Pline
    global Vdiv         # Number of vertical divisions
    global X0LIA          # Left top X value
    global Y0TIA          # Left top Y value 
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries, ImpedanceXseries # in ohms 

    # Set the TRACEsize variable
    TRACEsize = len(FFTresultA)     # Set the trace length
    
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)
    # Horizontal conversion factors (frequency Hz) and border limits
    STARTsample = 0     # First sample in FFTresult[] that is used
    STARTsample = int(math.ceil(STARTsample))               # First within screen range
    STOPsample = SAnum_bins # (SAMPLErate * 0.45) / Fsample
    STOPsample = int(math.floor(STOPsample))    # Last within screen range, math.floor actually not necessary, part of int
#
    RMScorr = 1.0 / SHOWsamples # For VOLTAGE!
    Powcorr = RMScorr **2 # vpktage squared For POWER!
    try:
        GainCorrection = float(eval(GainCorEntry.get()))
    except:
        GainCorEntry.delete(0,END)
        GainCorEntry.insert(0, GainCorrection)
        
    try:
        PhaseCorrection = float(eval(PhaseCorEntry.get()))
    except:
        PhaseCorEntry.delete(0,END)
        PhaseCorEntry.insert(0, PhaseCorrection)
        
    MAXsample = SAnum_bins      # Just an out of range check
    if STARTsample > (MAXsample - 1):
        STARTsample = MAXsample - 1

    if STOPsample > MAXsample:
        STOPsample = MAXsample - 1
    
    n = STARTsample
    PeakfreqA = PeakfreqB = PeakfreqM = F = Fsample
    PeakphaseA = PhaseA[n]
    PeakphaseB = PhaseB[n]
    PeakphaseAB = PhaseAB[n]
    PeakSample = n

    PeakdbA = 10 * math.log10(float(FFTresultA[n]))
    PeakdbB = 10 * math.log10(float(FFTresultB[n]))
    PeakMdb = PeakdbA - PeakdbB
    if IA_Ext_Conf.get() == 1:
        PeakdbAB = 10 * math.log10(float(FFTresultAB[n]))
    while n < STOPsample:
        F = n * Fsample
        try:
            dbA = 10 * math.log10(float(FFTresultA[n]))   # Convert power to DBs, except for log(0) error
        except:
            dbA = -200
        if dbA > PeakdbA:
            PeakdbA = dbA
            PeakfreqA = F
            PeakphaseA = PhaseA[n]
            PeakSample = n

        try:
            dbB = 10 * math.log10(float(FFTresultB[n]))  
        except:
            dbB = -200
        if dbB > PeakdbB:
            PeakdbB = dbB
            PeakfreqB = F
            PeakphaseB = PhaseB[n]
        
        if IA_Ext_Conf.get() == 1:
            try:
                dbAB = 10 * math.log10(float(FFTresultAB[n])) 
            except:
                dbAB = -200
            if dbAB > PeakdbAB:
                PeakdbAB = dbAB
                PeakphaseAB = PhaseAB[n]
        RelPhase = PhaseA[n]-PhaseB[n]
        if RelPhase > 180:
            RelPhase = RelPhase - 360
        elif RelPhase < -180:
            RelPhase = RelPhase + 360
        n = n + 1
    if IA_Ext_Conf.get() == 1:
        PeakRelPhase = PeakphaseAB-PeakphaseA
    else:
        PeakRelPhase = PeakphaseB-PeakphaseA
#
    if PeakRelPhase > 180:
        PeakRelPhase = PeakRelPhase - 360
    elif PeakRelPhase < -180:
        PeakRelPhase = PeakRelPhase + 360
    PeakRelPhase = PeakRelPhase + PhaseCorrection
    PeakdbB = PeakdbB + GainCorrection
    DoImpedance()
#
## Draw the impedance Analyzer screen
def MakeIAScreen():       # Update the screen with traces and text
    global CANVASheightIA, CANVASwidthIA, IAca, TIAMline, TIAMRline
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    global PeakphaseA, PeakphaseB, PeakRelPhase, PhaseCalEntry, CapZeroEntry
    global SmoothCurvesBP, TRACEwidth, GridWidth    # The colors
    global COLORsignalband, COLORtext, COLORgrid, IASweepSaved
    global COLORtrace1, COLORtrace2, COLORtrace5, COLORtrace6
    global ResScale, DisplaySeries   # Ohms per div
    global SAfreq_max, SAfreq_min, SAnum_bins, FBinWidth       # number of FFT samples
    global FFTwindow, FFTbandwidth, ZEROstuffing, FFTwindowname
    global X0LIA          # Left top X value
    global Y0TIA          # Left top Y value
    global GRWIA          # Screenwidth
    global GRHIA          # Screenheight
    global FontSize, IAGridType
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global AWGSAMPLErate, SAMPLErate, MaxSampleRate, OverRangeFlagA, OverRangeFlagB
    global SMPfft       # number of FFT samples
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv         # Number of vertical divisions
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries, ImpedanceXseries, Cseries # in ohms / uF
    global LoopNum, NetworkScreenStatus, NSweepSeriesR, NSweepSeriesX, NSweepSeriesMag, NSweepSeriesAng
    global NSweepParallelR, NSweepParallelC, NSweepParallelL, NSweepSeriesC, NSweepSeriesC

    # Delete all items on the screen
    IAca.delete(ALL) # remove all items
    SmoothBool = SmoothCurvesBP.get()
    Cparallel = 0.0
    Rparallel = 0.0
    Lparallel = 0.0
    Radius = (GRWIA-X0LIA)/(1 + Vdiv.get()*2) # 11
    xright = 10 + GRWIA/2 + ( Vdiv.get() * Radius ) # 5
    OhmsperPixel = float(ResScale.get())/Radius
    TRadius = Radius * Vdiv.get() # 5
    xcenter = GRWIA/2
    ycenter = GRHIA/2
    if IAGridType.get() == 0:
        # Draw circular grid lines
        i = 1
        xcenter = GRWIA/2
        ycenter = GRHIA/2 
        Radius = (GRWIA-X0LIA)/(1 + Vdiv.get()*2) # 11
        OhmsperPixel = float(ResScale.get())/Radius
        TRadius = Radius * Vdiv.get() # 5
        xright = 10 + xcenter + ( Vdiv.get() * Radius ) # 5
        while (i <= Vdiv.get()):
            x0 = xcenter - ( i * Radius )
            x1 = xcenter + ( i * Radius )
            y0 = ycenter - ( i * Radius )
            y1 = ycenter + ( i * Radius )
            axisvalue = float(ResScale.get()) * i
            if axisvalue >= 1000.0 or axisvalue <= -1000.0:
                axisvalue = axisvalue / 1000
                ResTxt = '{0:.1f}'.format(axisvalue)
                axis_label = str(ResTxt) + "K"
            elif axisvalue >= 100.0 or axisvalue <= -100.0:
                ResTxt = '{0:.1f}'.format(axisvalue)
                axis_label = str(ResTxt)
            elif axisvalue >= 10.0 or axisvalue <= -10.0:
                ResTxt = '{0:.2f}'.format(axisvalue)
                axis_label = str(ResTxt)
            else:
                ResTxt = '{0:.3f}'.format(axisvalue)
                axis_label = str(ResTxt)
            IAca.create_oval( x0, y0, x1, y1, outline=COLORgrid, width=GridWidth.get())
            IAca.create_line(xcenter, y0, xright, y0, fill=COLORgrid, width=GridWidth.get(), dash=(4,3))
            IAca.create_text(xright, y0, text=axis_label, fill=COLORgrid, anchor="w", font=("arial", FontSize+2 ))
            # 
            i = i + 1
        IAca.create_line(xcenter, y0, xcenter, y1, fill=COLORgrid, width=GridWidth.get())
        IAca.create_line(x0, ycenter, x1, ycenter, fill=COLORgrid, width=GridWidth.get())
        RAngle = math.radians(45)
        y = TRadius*math.sin(RAngle)
        x = TRadius*math.cos(RAngle)
        IAca.create_line(xcenter-x, ycenter-y, xcenter+x, ycenter+y, fill=COLORgrid, width=GridWidth.get())
        IAca.create_line(xcenter+x, ycenter-y, xcenter-x, ycenter+y, fill=COLORgrid, width=GridWidth.get())
        IAca.create_text(x0, ycenter, text="180", fill=COLORgrid, anchor="e", font=("arial", FontSize+2 ))
        IAca.create_text(x1, ycenter, text="0.0", fill=COLORgrid, anchor="w", font=("arial", FontSize+2 ))
        IAca.create_text(xcenter, y0, text="90", fill=COLORgrid, anchor="s", font=("arial", FontSize+2 ))
        IAca.create_text(xcenter, y1, text="-90", fill=COLORgrid, anchor="n", font=("arial", FontSize+2 ))
    else:
        # Draw horizontal grid lines
        i = 0 - Vdiv.get()
        j = 0
        x1 = X0LIA
        x2 = X0LIA + TRadius * 2
        xcenter = x1 + (TRadius)
        OhmsperPixel = float(ResScale.get())/Radius
        while (i <= Vdiv.get()):
            y = Y0TIA + j * (TRadius/Vdiv.get())
            Dline = [x1,y,x2,y]
            if i == 0 or i == Vdiv.get() or i == -Vdiv.get():
                IAca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                IAca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            axisvalue = float(ResScale.get()) * -i
            if axisvalue >= 1000.0 or axisvalue <= -1000.0:
                axisvalue = axisvalue / 1000
                ResTxt = '{0:.1f}'.format(axisvalue)
                axis_label = str(ResTxt) + "K"
            else:
                ResTxt = '{0:.0f}'.format(axisvalue)
                axis_label = str(ResTxt)
            IAca.create_text(x1-3, y, text=axis_label, fill=COLORtrace6, anchor="e", font=("arial", FontSize ))
            i = i + 1
            j = j + 1
        # Draw vertical grid lines
        i = 0 - Vdiv.get()
        j = 0
        y1 = Y0TIA
        y2 = Y0TIA + TRadius * 2
        ycenter = y1 + (TRadius)
        #    "\n".join(axis_label)
        while (i <= Vdiv.get()): #
            x = x1 + j * (TRadius/Vdiv.get())
            Dline = [x,y1,x,y2]
            if i == 0 or i == Vdiv.get() or i == -Vdiv.get():
                IAca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                IAca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            axisvalue = float(ResScale.get()) * i
            if axisvalue >= 1000.0 or axisvalue <= -1000.0:
                axisvalue = axisvalue / 1000
                ResTxt = '{0:.1f}'.format(axisvalue)
                axis_label = str(ResTxt) + "K"
            else:
                ResTxt = '{0:.0f}'.format(axisvalue)
                axis_label = str(ResTxt)
            IAca.create_text(x, y2+3, text=axis_label, fill=COLORtrace1, anchor="n", font=("arial", FontSize ))
            i = i + 1
            j = j + 1 
# Draw traces
    # Add saved line if there
    if IASweepSaved.get() > 0:
        if len(TIAMRline) > 4:
            IAca.create_line(TIAMRline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
#
    x1 = xcenter + ( ImpedanceRseries / OhmsperPixel )
    if x1 > 1500:
        x1 = xright
    elif x1 < -500:
        x1 = xcenter - xright
    IAca.create_line(xcenter, ycenter, x1, ycenter, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
    y1 = ycenter - ( ImpedanceXseries / OhmsperPixel )
    if y1 > 1500:
        y1 = xright
    elif y1 < -500:
        y1 = ycenter - xright
    xmag = x1
    ymag = y1
    IAca.create_line(xcenter, ycenter, xcenter, y1, fill=COLORtrace6, arrow="last", width=TRACEwidth.get())
    MagRadius = ImpedanceMagnitude / OhmsperPixel
    y1 = ycenter - MagRadius*math.sin(math.radians(ImpedanceAngle))
    if y1 > 1500:
        y1 = xright
    elif y1 < -500:
        y1 = ycenter - xright
    x1 = xcenter + MagRadius*math.cos(math.radians(ImpedanceAngle))
    if x1 > 1500:
        x1 = xright
    elif x1 < -500:
        x1 = xcenter - xright
    IAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace2, arrow="last", width=TRACEwidth.get())
#
    TIAMline = []
    if len(NSweepSeriesMag) > 2:
        index = 0
        while index < len(NSweepSeriesMag):
            MagRadius = NSweepSeriesMag[index] / OhmsperPixel
            y1 = ycenter - MagRadius*math.sin(math.radians(NSweepSeriesAng[index]))
            if y1 > 1500:
                y1 = xright
            elif y1 < -500:
                y1 = ycenter - xright
            x1 = xcenter + MagRadius*math.cos(math.radians(NSweepSeriesAng[index]))
            if x1 > 1500:
                x1 = xright
            elif x1 < -500:
                x1 = xcenter - xright
            TIAMline.append(x1)
            TIAMline.append(y1)
            index = index + 1
        IAca.create_line(TIAMline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())        
# display warning if input out of range
    if OverRangeFlagA == 1:
        x = X0LIA+GRWIA+10
        y = Y0TIA+GRHIA-40
        IAca.create_rectangle(x-6, y-6, x+6, y+6, fill="#ff0000")
        IAca.create_text (x+12, y, text="CH1 Over Range", anchor=W, fill="#ff0000", font=("arial", FontSize+4 ))
    if OverRangeFlagB == 1:
        x = X0LIA+GRWIA+10
        y = Y0TIA+GRHIA-10
        IAca.create_rectangle(x-6, y-6, x+6, y+6, fill="#ff0000")
        IAca.create_text (x+12, y, text="CH2 Over Range", anchor=W, fill="#ff0000", font=("arial", FontSize+4 ))
    # General information on top of the grid
    SR_label = ' {0:.1f} '.format(SAMPLErate)
    txt = " Sample rate: " + SR_label
    txt = txt + " FFT samples: " + str(SAnum_bins)

    txt = txt + " " + FFTwindowname
    if NetworkScreenStatus.get() > 0:
        txt = txt + " Sweep ON"
    else:
        txt = txt + " Sweep OFF"
    x = X0LIA
    y = 12
    idTXT = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    #
    x = X0LIA + GRWIA + 4
    y = 24
    txt = "Gain " + ' {0:.2f} '.format(PeakdbB-PeakdbA) + " dB" 
    TXT9  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    txt = "Phase " + ' {0:.2f} '.format(PeakRelPhase) + " Degrees"
    TXT10  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    txt = "Freq " + ' {0:.1f} '.format(PeakfreqA) + " Hertz"
    TXT11  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    txt = "Impedance Magnitude"
    TXT1 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    if ImpedanceMagnitude >= 1000.0 or ImpedanceMagnitude <= -1000.0:
        txt = '{0:.2f}'.format(ImpedanceMagnitude/1000.0)
        txt = str(txt) + "K"
    elif ImpedanceMagnitude >= 100.0 or ImpedanceMagnitude <= -100.0:
        txt = ' {0:.1f} '.format(ImpedanceMagnitude)
    elif ImpedanceMagnitude >= 10.0 or ImpedanceMagnitude <= -10.0:
        txt = ' {0:.2f} '.format(ImpedanceMagnitude)
    else:
        txt = ' {0:.3f} '.format(ImpedanceMagnitude)
    TXT2 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    txt = "Impedance Angle" 
    TXT3 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    txt = ' {0:.1f} '.format(ImpedanceAngle)
    TXT4 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    txt = "Impedance R series"
    TXT5 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    if ImpedanceRseries >= 1000.0 or ImpedanceRseries <= -1000.0:
        txt = '{0:.2f}'.format(ImpedanceRseries/1000.0)
        txt = str(txt) + "K"
    elif ImpedanceRseries >= 100.0 or ImpedanceRseries <= -100.0:
        txt = ' {0:.1f} '.format(ImpedanceRseries)
    elif ImpedanceRseries >= 10.0 or ImpedanceRseries <= -10.0:
        txt = ' {0:.2f} '.format(ImpedanceRseries)
    else:
        txt = ' {0:.3f} '.format(ImpedanceRseries)
    TXT6 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    txt = "Impedance X series"
    TXT7 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
    y = y + 24
    if ImpedanceXseries >= 1000.0 or ImpedanceXseries <= -1000.0:
        txt = '{0:.2f}'.format(ImpedanceXseries/1000.0)
        txt = str(txt) + "K"
    elif ImpedanceXseries >= 100.0 or ImpedanceXseries <= -100.0:
        txt = ' {0:.1f} '.format(ImpedanceXseries)
    elif ImpedanceXseries >= 10.0 or ImpedanceXseries <= -10.0:
        txt = ' {0:.2f} '.format(ImpedanceXseries)
    else:
        txt = ' {0:.3f} '.format(ImpedanceXseries)
    TXT8 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+6 ))
#
    Cseries = 0.0
    Cparallel = 0.0
    Lseries = 0.0
    Lparallel = 0.0
    Rparallel = 0.0
    if ImpedanceXseries < 0: # calculate series capacitance
        y = y + 24
        try:
            Cseries = -1 / ( 2 * math.pi * PeakfreqA * ImpedanceXseries ) # in farads
        except:
            Cseries = 0
        Qseries = 1/(2*math.pi*PeakfreqA*Cseries*ImpedanceRseries)
        Cparallel = Cseries * (Qseries**2 / (1+Qseries**2))
        Cparallel = Cparallel * 1E6 # convert to micro Farads
        Rparallel = ImpedanceRseries * (1+Qseries**2)
        Cseries = Cseries * 1E6 # convert to micro Farads
        if DisplaySeries.get() == 0:
            txt = "Series Capacitance"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
            y = y + 20
            if Cseries < 1:
                Ctext = Cseries * 1E3
                if Ctext < 1:
                    Ctext = Ctext * 1E3
                    CtextDis = Ctext + float(CapZeroEntry.get())
                    txt = ' {0:.1f} '.format(CtextDis) + "pF"
                else:
                    txt = ' {0:.3f} '.format(Ctext) + "nF"
            else:
                txt = ' {0:.3f} '.format(Cseries) + "uF"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
        else:
            txt = "Parallel"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
            y = y + 20
            if Cparallel < 1:
                Ctext = Cparallel * 1E3
                if Ctext < 1:
                    Ctext = Ctext * 1E3
                    txt = "Capacitance " + ' {0:.1f} '.format(Ctext) + "pF"
                else:
                    txt = "Capacitance " + ' {0:.3f} '.format(Ctext) + "nF"
            else:
                txt = "Capacitance " + ' {0:.3f} '.format(Cparallel) + "uF"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
            y = y + 20
            txt = "Resistance" + ' {0:.1f} '.format(Rparallel) + "ohms"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
        y = y + 20
        dissp = abs(ImpedanceRseries/ImpedanceXseries) * 100 # Dissipation factor is ratio of XR to XC in percent
        txt = 'D =  {0:.2f} '.format(dissp) + " %"
        IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
        
    elif ImpedanceXseries > 0: # calculate series inductance
        y = y + 24
        try:
            Lseries = ImpedanceXseries / ( 2 * 3.14159 * PeakfreqA ) # in henry
        except:
            Lseries = 0
        Qseries = (2*math.pi*PeakfreqA*Lseries)/ImpedanceRseries
        if Qseries == 0.0: # Check if divide by zero
            Qseries = 0.00001
        Lparallel = Lseries * ((1+Qseries**2) / Qseries**2)
        Lparallel = Lparallel * 1E3 # convert to millihenry
        Rparallel = ImpedanceRseries * (1+Qseries**2)
        Lseries = Lseries * 1E3 # in millihenry
        if DisplaySeries.get() == 0:
            txt = "Series Inductance"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
            y = y + 22
            if Lseries < 1:
                Ltext = Lseries * 1E3
                txt = ' {0:.2f} '.format(Ltext) + "uH"
            else:
                txt = ' {0:.2f} '.format(Lseries) + "mH"
            IAca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
        else:
            txt = "Parallel"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
            y = y + 20
            if Lparallel < 1:
                Ltext = Lparallel * 1E3
                txt = "Inductance " + ' {0:.2f} '.format(Ltext) + "uH"
            else:
                txt = "Inductance " + ' {0:.2f} '.format(Lparallel) + "mH"
            IAca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
            y = y + 20
            txt = "Resistance" + ' {0:.1f} '.format(Rparallel) + "ohms"
            IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
        y = y + 20
        qf = abs(ImpedanceXseries/ImpedanceRseries) * 100 # Quality Factor is ratio of XL to XR
        txt = 'Q =  {0:.2f} '.format(qf)
        IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
    #
    if LoopNum.get() > 1:
        if NetworkScreenStatus.get() > 0:
            NSweepSeriesR.append(ImpedanceRseries)
            NSweepSeriesX.append(ImpedanceXseries)
            NSweepSeriesMag.append(ImpedanceMagnitude) # in ohms 
            NSweepSeriesAng.append(ImpedanceAngle) # in degrees
            NSweepParallelR.append(Rparallel)
            NSweepParallelC.append(Cparallel) # in uF
            NSweepParallelL.append(Lparallel) # in mH
            NSweepSeriesC.append(Cseries) # in uF
            NSweepSeriesL.append(Lseries) # in mH
    # Start and stop frequency and trace mode
    Fmax = int(SAMPLErate * 0.45)
    txt = "0.0 to " + str(Fmax) + " Hz"

    txt = txt + "  FFT Bandwidth =" + ' {0:.2f} '.format(FFTbandwidth)
        
    x = X0LIA
    y = Y0TIA+GRHIA-13
    idTXT = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    txt = " "
    if FreqTraceMode.get() == 1:
        txt ="Normal mode "

    if FreqTraceMode.get() == 2:
        txt = "Peak hold mode "
    
    if FreqTraceMode.get() == 3:
        txt = "Power average  mode (" + str(TRACEaverage.get()) + ") " 

    if ZEROstuffing.get() > 0:
        txt = txt + "Zero Stuffing = " + str(ZEROstuffing.get())
    # Runstatus and level information
    if (RUNstatus.get() == 0):
        txt = txt + "  Stopped "
    else:
        txt = txt + "  Running "
    y = Y0TIA+GRHIA
    IDtxt  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
#
def IACaresize(event):
    global IAca, GRWIA, XOLIA, GRHIA, Y0TIA, CANVASwidthIA, CANVASheightIA, FontSize
     
    CANVASwidthIA = event.width - 4
    CANVASheightIA = event.height - 4
    GRWIA = CANVASwidthIA - (2 * X0LIA) - int(21.25 * FontSize) # 170 new grid width
    GRHIA = CANVASheightIA - Y0TIA - int(2.25 * FontSize) # 10 new grid height
    UpdateIAAll()
#
## ================ Make IA Window ==========================
def MakeIAWindow():
    global iawindow, IAca, logo, IAScreenStatus, RsystemEntry, IADisp, AWGSync, IASource
    global COLORcanvas, CANVASwidthIA, CANVASheightIA, RevDate, AWGAMode, AWGAShape, AWGBMode
    global FFTwindow, CutDC, ColorMode, ResScale, GainCorEntry, PhaseCorEntry, DisplaySeries
    global GRWIA, X0LIA, GRHIA, Y0TIA, IA_Ext_Conf, DeBugMode, SWRev, CapZeroEntry
    global NetworkScreenStatus, IASweepSaved, IAGridType
    global FrameRelief, BorderSize, IAconschem

    if IAScreenStatus.get() == 0:
        IAScreenStatus.set(1)
        IADisp.set(1)
        IACheckBox()
        CutDC.set(1) # set to remove DC
        CANVASwidthIA = GRWIA + 2 * X0LIA + int(21.25 * FontSize)     # The canvas width
        CANVASheightIA = GRHIA + Y0TIA + int(2.25 * FontSize)         # The canvas height
        
        iawindow = Toplevel()
        iawindow.title("Impedance Analyzer " + SWRev + RevDate)
        iawindow.protocol("WM_DELETE_WINDOW", DestroyIAScreen)
        frame2iar = Frame(iawindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2iar.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2ia = Frame(iawindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2ia.pack(side=TOP, expand=YES, fill=BOTH)

        IAca = Canvas(frame2ia, width=CANVASwidthIA, height=CANVASheightIA, background=COLORcanvas, cursor='cross')
        IAca.bind("<Configure>", IACaresize)
        IAca.bind("<Return>", DoNothing)
        IAca.bind("<space>", onCanvasSpaceBar)
        IAca.pack(side=TOP, expand=YES, fill=BOTH)

        # menu buttons
        # right side drop down menu buttons
        dropmenu = Frame( frame2iar )
        dropmenu.pack(side=TOP)
        # File menu 
        IAFilemenu = Menubutton(dropmenu, text="File", style="W5.TButton")
        IAFilemenu.menu = Menu(IAFilemenu, tearoff = 0 )
        IAFilemenu["menu"] = IAFilemenu.menu
        IAFilemenu.menu.add_command(label="Save Config", command=BSaveConfigIA)
        IAFilemenu.menu.add_command(label="Load Config", command=BLoadConfigIA)
        IAFilemenu.menu.add_command(label="Run Script", command=RunScript)
        IAFilemenu.menu.add_command(label="Save V Cal", command=BSaveCal)
        IAFilemenu.menu.add_command(label="Load V Cal", command=BLoadCal)
        IAFilemenu.menu.add_command(label="Save Data", command=BSaveDataIA)
        IAFilemenu.menu.add_command(label="Save Screen", command=BSaveScreenIA)
        IAFilemenu.menu.add_command(label="Help", command=BHelp)
        IAFilemenu.pack(side=LEFT, anchor=W)
        #
        IAOptionmenu = Menubutton(dropmenu, text="Options", style="W8.TButton")
        IAOptionmenu.menu = Menu(IAOptionmenu, tearoff = 0 )
        IAOptionmenu["menu"]  = IAOptionmenu.menu
        IAOptionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
        IAOptionmenu.menu.add_checkbutton(label='Cut-DC', variable=CutDC)
        #IAOptionmenu.menu.add_checkbutton(label='Sweep-on', variable=NetworkScreenStatus)
        #IAOptionmenu.menu.add_checkbutton(label='Save Sweep', variable=IASweepSaved, command=BSaveIASweep)
        if DeBugMode == 1:
            IAOptionmenu.menu.add_command(label="-Ext Config-", command=donothing)
            IAOptionmenu.menu.add_radiobutton(label='1', variable=IA_Ext_Conf, value=0)
            IAOptionmenu.menu.add_radiobutton(label='2', variable=IA_Ext_Conf, value=1)
        IAOptionmenu.menu.add_command(label="-Meas As-", command=donothing)
        IAOptionmenu.menu.add_radiobutton(label='Series', variable=DisplaySeries, value=0)
        IAOptionmenu.menu.add_radiobutton(label='Parallel', variable=DisplaySeries, value=1)
        IAOptionmenu.menu.add_command(label="-Background-", command=donothing)
        IAOptionmenu.menu.add_radiobutton(label='Black', variable=ColorMode, value=0, command=BgColor)
        IAOptionmenu.menu.add_radiobutton(label='White', variable=ColorMode, value=1, command=BgColor)
        IAOptionmenu.pack(side=LEFT, anchor=W)
        #
        rsemenu = Frame( frame2iar )
        rsemenu.pack(side=TOP)
        rseb2 = Button(rsemenu, text="Stop", style="Stop.TButton", command=BStop)
        rseb2.pack(side=RIGHT)
        rseb3 = Button(rsemenu, text="Run", style="Run.TButton", command=BStartIA)
        rseb3.pack(side=RIGHT)
        #
        IAFFTwindmenu = Menubutton(frame2iar, text="FFTwindow", style="W11.TButton")
        IAFFTwindmenu.menu = Menu(IAFFTwindmenu, tearoff = 0 )
        IAFFTwindmenu["menu"]  = IAFFTwindmenu.menu
        IAFFTwindmenu.menu.add_radiobutton(label='Rectangular window (B=1)', variable=FFTwindow, value=0)
        IAFFTwindmenu.menu.add_radiobutton(label='Cosine window (B=1.24)', variable=FFTwindow, value=1)
        IAFFTwindmenu.menu.add_radiobutton(label='Triangular window (B=1.33)', variable=FFTwindow, value=2)
        IAFFTwindmenu.menu.add_radiobutton(label='Hann window (B=1.5)', variable=FFTwindow, value=3)
        IAFFTwindmenu.menu.add_radiobutton(label='Blackman window (B=1.73)', variable=FFTwindow, value=4)
        IAFFTwindmenu.menu.add_radiobutton(label='Nuttall window (B=2.02)', variable=FFTwindow, value=5)
        IAFFTwindmenu.menu.add_radiobutton(label='Flat top window (B=3.77)', variable=FFTwindow, value=6)
        IAFFTwindmenu.pack(side=TOP)
        #
        # Temp set source resistance to 1000
        rsystem = Frame( frame2iar )
        rsystem.pack(side=TOP)
        rsystemlab = Label(rsystem, text="Ext Res")
        rsystemlab.pack(side=LEFT, anchor=W)
        RsystemEntry = Entry(rsystem, width=7, cursor='double_arrow')
        RsystemEntry.bind('<Return>', onTextKey)
        RsystemEntry.bind('<MouseWheel>', onTextScroll)
        RsystemEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        RsystemEntry.bind("<Button-5>", onTextScroll)
        RsystemEntry.bind('<Key>', onTextKey)
        RsystemEntry.pack(side=LEFT, anchor=W)
        RsystemEntry.delete(0,"end")
        RsystemEntry.insert(4,1000)
        # Res Scale Spinbox
        ressb = Frame( frame2iar )
        ressb.pack(side=TOP)
        reslab = Label(ressb, text="Ohms/div ")
        reslab.pack(side=LEFT)
        ResScale = Spinbox(ressb, width=7, cursor='double_arrow', values=ResScalediv)
        ResScale.bind('<MouseWheel>', onSpinBoxScroll)
        ResScale.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
        ResScale.bind("<Button-5>", onSpinBoxScroll)
        ResScale.pack(side=LEFT)
        ResScale.delete(0,"end")
        ResScale.insert(0,500)
        #
        GainCor = Frame( frame2iar )
        GainCor.pack(side=TOP)
        GainCorlab = Label(GainCor, text="Gain Cor dB")
        GainCorlab.pack(side=LEFT, anchor=W)
        GainCorEntry = Entry(GainCor, width=7, cursor='double_arrow')
        GainCorEntry.bind('<Return>', onTextKey)
        GainCorEntry.bind('<MouseWheel>', onTextScroll)
        GainCorEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        GainCorEntry.bind("<Button-5>", onTextScroll)
        GainCorEntry.bind('<Key>', onTextKey)
        GainCorEntry.pack(side=LEFT, anchor=W)
        GainCorEntry.delete(0,"end")
        GainCorEntry.insert(4,0.0)
        #
        PhaseCor = Frame( frame2iar )
        PhaseCor.pack(side=TOP)
        PhaseCorlab = Label(PhaseCor, text="Phase Cor")
        PhaseCorlab.pack(side=LEFT, anchor=W)
        PhaseCorEntry = Entry(PhaseCor, width=7, cursor='double_arrow')
        PhaseCorEntry.bind('<Return>', onTextKey)
        PhaseCorEntry.bind('<MouseWheel>', onTextScroll)
        PhaseCorEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        PhaseCorEntry.bind("<Button-5>", onTextScroll)
        PhaseCorEntry.bind('<Key>', onTextKey)
        PhaseCorEntry.pack(side=LEFT, anchor=W)
        PhaseCorEntry.delete(0,"end")
        PhaseCorEntry.insert(4,0.0)
        #
        capofflab = Label(frame2iar, text="Capacitance Offset")
        capofflab.pack(side=TOP)
        CapZero = Frame( frame2iar )
        CapZero.pack(side=TOP)
        CapZerobutton = Button(CapZero, text="Zero", style="W4.TButton", command=IACapZero)
        CapZerobutton.pack(side=LEFT, anchor=W)
        CapResetbutton = Button(CapZero, text="Reset", style="W5.TButton", command=IACapReset)
        CapResetbutton.pack(side=LEFT, anchor=W)
        CapZeroEntry = Entry(CapZero, width=6, cursor='double_arrow')
        CapZeroEntry.bind('<Return>', onTextKey)
        CapZeroEntry.bind('<MouseWheel>', onTextScroll)
        CapZeroEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        CapZeroEntry.bind("<Button-5>", onTextScroll)
        CapZeroEntry.bind('<Key>', onTextKey)
        CapZeroEntry.pack(side=LEFT, anchor=W)
        CapZeroEntry.delete(0,"end")
        CapZeroEntry.insert(4,0.0)
        #
        srclab = Label(frame2iar, text="Source")
        srclab.pack(side=TOP)
        extsrc1 = Radiobutton(frame2iar, text="Internal", variable=IASource, value=0, command=IASourceSet)
        extsrc1.pack(side=TOP)
        extsrc2 = Radiobutton(frame2iar, text="External", variable=IASource, value=1, command=IASourceSet)
        extsrc2.pack(side=TOP)
        #
        gridmenu = Frame( frame2iar )
        gridmenu.pack(side=TOP)
        iagrid1= Radiobutton(frame2iar, text="Polar Grid", variable=IAGridType, value=0) #, command=IAGridSet)
        iagrid1.pack(side=TOP)
        iagrid2 = Radiobutton(frame2iar, text="Rect Grid", variable=IAGridType, value=1) #, command=IAGridSet)
        iagrid2.pack(side=TOP)
        #
        dismiss1button = Button(frame2iar, text="Dismiss", style="W8.TButton", command=DestroyIAScreen)
        dismiss1button.pack(side=TOP)
        # Draw Connection schematic
        IAconschem = Canvas(frame2iar, width=130, height=75, background=COLORwhite) # , cursor='cross')
        IAconschem.pack(side=TOP)
        IAconschem.bind('<1>', onIAShemeClickLeft) # left mouse button toggles mode flag
        DrawIASchem()
        
        # add Alice logo 
        ADI1 = Label(frame2iar, image=logo, anchor= "sw", compound="top") #  height=49, width=116,
        ADI1.pack(side=TOP)
#
def onIAShemeClickLeft(event):
    global ID_Mode, IAconschem

    if event.widget == IAconschem: # left mouse button toggles mode flag
        if IA_Mode.get() == 0:
            IA_Mode.set(1)
            DrawIASchem()
        else:
            IA_Mode.set(0)
            DrawIASchem()
#
def DrawIASchem():
    global ID_Mode, IAconschem, IACMString
    
    IAconschem.delete(ALL) # remove all drawing items
    ResW = 6
    X = 32
    Y = 14
    if IA_Mode.get() == 0:
        IAconschem.create_line(X, Y, X+17, Y, fill=COLORblack, width=3)
        IAconschem.create_line(X+17, Y, X+20, Y+ResW, fill=COLORblack, width=3)
        IAconschem.create_line(X+20, Y+ResW, X+26, Y-ResW, fill=COLORblack, width=3)
        IAconschem.create_line(X+26, Y-ResW, X+31, Y+ResW, fill=COLORblack, width=3)
        IAconschem.create_line(X+31, Y+ResW, X+37, Y-ResW, fill=COLORblack, width=3)
        IAconschem.create_line(X+37, Y-ResW, X+40, Y, fill=COLORblack, width=3)
        IAconschem.create_line(X+40, Y, X+65, Y, fill=COLORblack, width=3)
        IAconschem.create_line(X+55, Y, X+55, Y+20, fill=COLORblack, width=3)
        IAconschem.create_rectangle(X+50, Y+20, X+60, Y+40, fill=COLORwhite, width=3)
        IAconschem.create_line(X+55, Y+40, X+55, Y+50, fill=COLORblack, width=3)
        IAconschem.create_line(X, Y+50, X+57, Y+50, fill=COLORblack, width=3)
        IAconschem.create_text(X+6, Y-6, text="AWG A", fill=COLORblack, anchor="e", font=("arial", FontSize ))
        IAconschem.create_text(X-2, Y+9, text="CH A", fill=COLORblack, anchor="e", font=("arial", FontSize+1 ))
        IAconschem.create_text(X-1, Y+50, text=IACMString, fill=COLORblack, anchor="e", font=("arial", FontSize+1 ))
        IAconschem.create_text(X+67, Y, text="CH B", fill=COLORblack, anchor="w", font=("arial", FontSize+1 ))
        IAconschem.create_text(X+19, Y+12, text="Rext", fill=COLORblack, anchor="w", font=("arial", FontSize+1 ))
        IAconschem.create_text(X+45, Y+30, text="Zut", fill=COLORblack, anchor="e", font=("arial", FontSize+1 ))
    else:
        IAconschem.create_line(X, Y, X+17, Y, fill=COLORblack, width=3)
        IAconschem.create_rectangle(X+17, Y+ResW, X+40, Y-ResW, fill=COLORwhite, width=3)
        IAconschem.create_line(X+40, Y, X+65, Y, fill=COLORblack, width=3)
        #
        IAconschem.create_line(X+55, Y, X+55, Y+20, fill=COLORblack, width=3)
        IAconschem.create_line(X+55, Y+19, X+49, Y+23, fill=COLORblack, width=3)
        IAconschem.create_line(X+49, Y+23, X+61, Y+26, fill=COLORblack, width=3)
        IAconschem.create_line(X+61, Y+26, X+49, Y+32, fill=COLORblack, width=3)
        IAconschem.create_line(X+49, Y+32, X+61, Y+38, fill=COLORblack, width=3)
        IAconschem.create_line(X+61, Y+38, X+55, Y+41, fill=COLORblack, width=3)
        #
        IAconschem.create_line(X+55, Y+40, X+55, Y+50, fill=COLORblack, width=3)
        IAconschem.create_line(X, Y+50, X+57, Y+50, fill=COLORblack, width=3)
        IAconschem.create_text(X+6, Y-6, text="AWG A", fill=COLORblack, anchor="e", font=("arial", FontSize ))
        IAconschem.create_text(X-2, Y+9, text="CH A", fill=COLORblack, anchor="e", font=("arial", FontSize+1 ))
        IAconschem.create_text(X-1, Y+50, text=IACMString, fill=COLORblack, anchor="e", font=("arial", FontSize+1 ))
        IAconschem.create_text(X+67, Y, text="CH B", fill=COLORblack, anchor="w", font=("arial", FontSize+1 ))
        IAconschem.create_text(X+19, Y+14, text="Zut", fill=COLORblack, anchor="w", font=("arial", FontSize+1 ))
        IAconschem.create_text(X+45, Y+30, text="Rext", fill=COLORblack, anchor="e", font=("arial", FontSize+1 ))
#
def DestroyIAScreen():
    global iawindow, IAScreenStatus, IAca, IADisp
    
    IAScreenStatus.set(0)
    IADisp.set(0)
    IACheckBox()
    iawindow.destroy()
#
def BSaveIASweep():
    global TIAMline, TIAMRline, IASweepSaved

    if IASweepSaved.get() > 0:
        TIAMRline = TIAMline
#
def IACapZero():
    global Cseries, CapZeroEntry

    Ctext = ' {0:.1f} '.format(-Cseries * 1E6)
    CapZeroEntry.delete(0,"end")
    CapZeroEntry.insert(6,Ctext)
#
def IACapReset():
    global CapZeroEntry

    CapZeroEntry.delete(0,"end")
    CapZeroEntry.insert(4,0.0)
#
def MakeNyquistPlot():
    global nqpwindow, NqPca, logo, NqPScreenStatus, NqPDisp
    global COLORcanvas, CANVASwidthNqP, CANVASheightNqP, RevDate
    global GRWNqP, X0LNqP, GRHNqP, Y0TNqP, DeBugMode, SWRev
    global NetworkScreenStatus, NqPSweepSaved
    global FrameRelief, BorderSize

    if NqPScreenStatus.get() == 0:
        NqPScreenStatus.set(1)
        NqPDisp.set(1)
        CANVASwidthNqP = GRWNqP + (2 * X0LNqP)     # The canvas width
        CANVASheightNqP = GRHNqP + Y0TNqP + 10  # The canvas height
        nqpwindow = Toplevel()
        nqpwindow.title("Nyquist Plot " + SWRev + RevDate)
        nqpwindow.protocol("WM_DELETE_WINDOW", DestroyNqPScreen)

        frame2nqp = Frame(nqpwindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2nqp.pack(side=TOP, expand=YES, fill=BOTH)

        NqPca = Canvas(frame2nqp, width=CANVASwidthNqP, height=CANVASheightNqP, background=COLORcanvas, cursor='cross')
        NqPca.bind("<Configure>", NqPCaresize)
        NqPca.bind("<Return>", DoNothing)
        NqPca.bind("<space>", onCanvasSpaceBar)
        NqPca.pack(side=TOP, expand=YES, fill=BOTH)
#
def DestroyNqPScreen():
    global nqpwindow, NqPScreenStatus, NqPca, NqPDisp
    
    NqPScreenStatus.set(0)
    NqPDisp.set(0)
    nqpwindow.destroy()
#
def NqPCaresize(event):
    global NqPca, GRWNqP, XOLNqP, GRHNqP, Y0TNqP, CANVASwidthNqP, CANVASheightNqP, FontSize
    
    CANVASwidthNqP = event.width - 4
    CANVASheightNqP = event.height - 4
    GRWNqP = CANVASwidthNqP - (2 * X0LNqP) # new grid width
    GRHNqP = CANVASheightNqP - Y0TNqP - int(1.25 * FontSize)  # 10 new grid height
    UpdateNqPAll()
#
## Draw the Nyquist plot screen
def MakeNqPScreen():
    global NqPca, GRWNqP, XOLNqP, GRHNqP, Y0TNqP, CANVASwidthNqP, CANVASheightNqP, COLORtrace1
    global COLORgrid, GridWidth, SmoothCurvesBP, SmoothBool, DBlevelBP, DBdivlist, DBdivindexBP
    global FSweepAdB, FSweepBdB, FSweepBPh, FSweepAPh, ShowMathBP, NqPline, TRACEwidth
    global Vdiv, FStep
    global FontSize
    
    # Delete all items on the canvas
    NqPca.delete(ALL) # remove all items
    SmoothBool = SmoothCurvesBP.get()
    # Draw circular grid lines
    i = 1
    xcenter = GRWNqP/2
    ycenter = GRHNqP/2 
    Radius = (GRWNqP-X0LNqP)/(1 + Vdiv.get() * 2) # 11
    dBperPixel = float(DBdivlist[DBdivindexBP.get()])/Radius
    TRadius = Radius * Vdiv.get() # 5
    x1 = X0LNqP
    x2 = X0LNqP + GRWNqP
    xright = 10 + xcenter + ( Vdiv.get() * Radius ) # 5
    while (i <= Vdiv.get()):
        x0 = xcenter - ( i * Radius )
        x1 = xcenter + ( i * Radius )
        y0 = ycenter - ( i * Radius )
        y1 = ycenter + ( i * Radius )
        dBaxis_value = (DBlevelBP.get() - (i * DBdivlist[DBdivindexBP.get()]))
        NqPca.create_oval( x0, y0, x1, y1, outline=COLORgrid, width=GridWidth.get())
        NqPca.create_line(xcenter, y0, xright, y0, fill=COLORgrid, width=GridWidth.get(), dash=(4,3))
        NqPca.create_text(xright, y0, text=str(dBaxis_value), fill=COLORgrid, anchor="w", font=("arial", FontSize+2 ))
        # 
        i = i + 1
    NqPca.create_line(xcenter, y0, xcenter, y1, fill=COLORgrid, width=GridWidth.get())
    NqPca.create_line(x0, ycenter, x1, ycenter, fill=COLORgrid, width=GridWidth.get())
    RAngle = math.radians(45)
    y = TRadius*math.sin(RAngle)
    x = TRadius*math.cos(RAngle)
    NqPca.create_line(xcenter-x, ycenter-y, xcenter+x, ycenter+y, fill=COLORgrid, width=GridWidth.get())
    NqPca.create_line(xcenter+x, ycenter-y, xcenter-x, ycenter+y, fill=COLORgrid, width=GridWidth.get())
    NqPca.create_text(x0, ycenter, text="180", fill=COLORgrid, anchor="e", font=("arial", FontSize+2 ))
    NqPca.create_text(x1, ycenter, text="0.0", fill=COLORgrid, anchor="w", font=("arial", FontSize+2 ))
    NqPca.create_text(xcenter, y0, text="90", fill=COLORgrid, anchor="s", font=("arial", FontSize+2 ))
    NqPca.create_text(xcenter, y1, text="-90", fill=COLORgrid, anchor="n", font=("arial", FontSize+2 ))
    # xcenter = xcenter + (DBlevelBP.get()/dBperPixel)
# Draw traces
    NqPline = []
    if len(FSweepAdB) > 4:
        for index in range(len(FSweepAdB)): # while n < len(FStep):
            if index < len(FStep): # check if n has gone out off bounds because user did something dumb
                F = FStep[index] # look up frequency bin in list of bins
            else:
                F = FStep[0]
            # Mag value
            dbA = 10 * math.log10(float(FSweepAdB[index])) # Convert power to DBs, except for log(0) error
            dbB = 10 * math.log10(float(FSweepBdB[index])) 
            if ShowMathBP.get() == 1:
                MdB = dbA - dbB
            elif ShowMathBP.get() == 2:
                MdB = dbB - dbA
            MagRadius = (-MdB / dBperPixel) + (DBlevelBP.get()/dBperPixel)
            # Phase Value
            RelPhase = FSweepBPh[index] - FSweepAPh[index]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            RelPhase = RelPhase # - 9.0
            y1 = ycenter - MagRadius*math.sin(math.radians(RelPhase))
            if y1 > 1500:
                y1 = xright
            elif y1 < -500:
                y1 = ycenter - xright
            x1 = xcenter + MagRadius*math.cos(math.radians(RelPhase ))
            if x1 > 1500:
                x1 = xright
            elif x1 < -500:
                x1 = xcenter - xright
            NqPline.append(x1)
            NqPline.append(y1)
        NqPca.create_line(NqPline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())        
#
# Make the Nichols Plot
def MakeNicPlot():
    global NiCScreenStatus, NiCDisp
    global nicwindow, NiCca, logo, SWRev
    global COLORcanvas, CANVASwidthNic, CANVASheightNic, RevDate
    global GRWNiC, X0LNiC, GRHNiC, Y0TNiC, DeBugMode
    global NetworkScreenStatus, NiCSweepSaved
    global FrameRelief, BorderSize

    if NiCScreenStatus.get() == 0:
        NiCScreenStatus.set(1)
        NiCDisp.set(1)
        CANVASwidthNic = GRWNiC + 18 + X0LNiC     # The canvas width
        CANVASheightNic = GRHNiC + 60  # The canvas height
        nicwindow = Toplevel()
        nicwindow.title("Nichols Plot " + SWRev + RevDate)
        nicwindow.protocol("WM_DELETE_WINDOW", DestroyNiCScreen)

        frame2nic = Frame(nicwindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2nic.pack(side=TOP, expand=YES, fill=BOTH)

        NiCca = Canvas(frame2nic, width=CANVASwidthNic, height=CANVASheightNic, background=COLORcanvas, cursor='cross')
        NiCca.bind("<Configure>", NiCCaresize)
        NiCca.bind("<Return>", DoNothing)
        NiCca.bind("<space>", onCanvasSpaceBar)
        NiCca.pack(side=TOP, expand=YES, fill=BOTH)
#
def DestroyNiCScreen():
    global nicwindow, NiCScreenStatus, NiCca, NiCDisp
    
    NiCScreenStatus.set(0)
    NiCDisp.set(0)
    nicwindow.destroy()
#
def NiCCaresize(event):
    global NiCca, GRWNiC, XOLNiC, GRHNiC, Y0TNiC, CANVASwidthNic, CANVASheightNic, FontSize
    
    CANVASwidthNic = event.width - 4
    CANVASheightNic = event.height - 4
    GRWNiC = CANVASwidthNic - int(2.25 * FontSize) - X0LNiC # 18 new grid width
    GRHNiC = CANVASheightNic - int(7.5 * FontSize) # 60 new grid height
    UpdateNiCAll()
#
## Make the Nichols Plot screen
def MakeNiCScreen():
    global NiCline, NiCca, CANVASwidthNic, CANVASheightNic, X0LNiC, GRWNiC, Y0TNiC, GRHNiC, X0TNiC
    global COLORzeroline, GridWidth, COLORgrid, FSweepAdB, FSweepBdB, ShowMathBP
    global FSweepBPh, FSweepAPh, SmoothCurvesBP, SmoothBool, DBlevelBP, DBdivlist, DBdivindexBP
    global Vdiv, FStep, PhCenBodeEntry, RelPhaseCenter
    global FontSize
    
    Ymin = Y0TNiC                  # Minimum position of XY grid (top)
    Ymax = Y0TNiC + GRHNiC            # Maximum position of XY grid (bottom)
    Xmin = X0LNiC                  # Minimum position of XY grid (left)
    Xmax = X0LNiC + GRWNiC            # Maximum position of XY grid (right)
    try:
        Phasecenter = int(PhCenBodeEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenBodeEntry.delete(0,"end")
        PhCenBodeEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
    # Delete all items on the screen
    MarkerNum = 0
    SmoothBool = SmoothCurvesBP.get()
    NiCca.delete(ALL) # remove all items
    # Draw horizontal grid lines Rel Gain Magnitude
    i = 0
    x1 = X0LNiC
    x2 = X0TNiC = X0LNiC + GRWNiC
    mg_siz = GRWNiC/10.0
    mg_inc = mg_siz/5.0
    DegPerDiv = 360 / 10
    while (i < Vdiv.get()+1):
        dBaxis_value = (DBlevelBP.get() - (i * DBdivlist[DBdivindexBP.get()]))
        y = Y0TNiC + i * GRHNiC/Vdiv.get()
        Dline = [x1,y,x2,y]
        if dBaxis_value == 0:
            NiCca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue line at center of grid
            k = 0
            while (k < 10):
                l = 1
                while (l < 5): # add tick marks
                    Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                    NiCca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    l = l + 1
                k = k + 1
        else:
            NiCca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
        dBaxis_label = str(dBaxis_value)
        NiCca.create_text(x1-3, y, text=dBaxis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
        
        i = i + 1
    # Draw vertical grid lines (phase -180 to 180 10 div)
    i = 0
    y1 = Y0TNiC
    y2 = Y0TNiC + GRHNiC
    mg_siz = GRHNiC/10.0
    mg_inc = mg_siz/5.0
    # 
    while (i < 11):
        x = X0LNiC + i * GRWNiC/10.0
        Dline = [x,y1,x,y2]
        axis_value = Phasecenter - 180 + (i * DegPerDiv)
        axis_label = str(axis_value)
        if ( axis_value == 0):
            NiCca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue vertical line at center of grid
            k = 0
            while (k < 10):
                l = 1
                while (l < 5): # add tick marks
                    Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                    NiCca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    l = l + 1
                k = k + 1
        else:
            NiCca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
        NiCca.create_text(x, y2+3, text=axis_label, fill=COLORtrace3, anchor="n", font=("arial", FontSize ))
        i = i + 1
    # Draw traces
    # Vertical conversion factors (level dBs) and border limits
    Yconv = float(GRHNiC) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()])     # Conversion factors, Yconv is the number of screenpoints per dB
    Yc = float(Y0TNiC) + Yconv * (DBlevelBP.get())  # Yc is the 0 dBm position, can be outside the screen!
    Xphconv = float(GRWNiC / 360.0) # degrees per pixel
    Xp = float(X0LNiC) + Xphconv * 180.0
    x1 = X0LNiC + 14
    # Horizontal conversion factors (phase deg) and border limits
    NiCline = []
    if len(FSweepAdB) > 4:
        index = 0
        for index in range(len(FSweepAdB)): # while n < len(FStep):
            if index < len(FStep): # check if n has gone out off bounds because user did something dumb
                F = FStep[index] # look up frequency bin in list of bins
            else:
                F = FStep[0]
            # Mag value
            dbA = 10 * math.log10(float(FSweepAdB[index])) # Convert power to DBs, except for log(0) error
            dbB = 10 * math.log10(float(FSweepBdB[index]))
            if ShowMathBP.get() == 1:
                MdB = dbA - dbB
            elif ShowMathBP.get() == 2:
                MdB = dbB - dbA
            yb = Yc - Yconv * MdB
            if (yb < Ymin):
                yb = Ymin
            if (yb > Ymax):
                yb = Ymax
            # Phase Value
            RelPhase = FSweepBPh[index] - FSweepAPh[index]
            RelPhase = RelPhase - Phasecenter
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            xa = Xp + Xphconv * RelPhase
            if (xa < Xmin):
                xa = Ymin
            if (xa > Xmax):
                xa = Xmax
            NiCline.append(int(xa + 0.5))
            NiCline.append(int(yb + 0.5))
        NiCca.create_line(NiCline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
##
def UpdateNqPAll():        # Update Data, trace and screen
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep
    global SMPfft

    if len(FSweepAdB) < 2:
        return
    #MakeNqPTrace()         # Update the traces
    UpdateNqPScreen()      # Update the screen 
##
def UpdateNqPTrace():      # Update trace and screen
    
    #MakeNqPTrace()         # Update traces
    UpdateNqPScreen()      # Update the screen
##
def UpdateNqPScreen():     # Update screen with trace and text
    
    MakeNqPScreen()     # Update the screen
    root.update()       # Activate updated screens    
##
def UpdateNiCAll():        # Update Data, trace and screen
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep
    global SMPfft

    if len(FSweepAdB) < 2:
        return
    #MakeNiCTrace()         # Update the traces
    UpdateNiCScreen()      # Update the screen 
##
def UpdateNiCTrace():      # Update trace and screen
    
    #MakeNiCTrace()         # Update traces
    UpdateNiCScreen()      # Update the screen
##
def UpdateNiCScreen():     # Update screen with trace and text
    
    MakeNiCScreen()     # Update the screen
    root.update()       # Activate updated screens    
#
##
def VAtoggle():
    global vat_btn

    if vat_btn.config('text')[-1] == 'ON':
        vat_btn.config(text='OFF', style="Stop.TButton")
    else:
        vat_btn.config(text='ON', style="Run.TButton")
#
def VABtoggle():
    global vabt_btn

    if vabt_btn.config('text')[-1] == 'ON':
        vabt_btn.config(text='OFF', style="Stop.TButton")
    else:
        vabt_btn.config(text='ON', style="Run.TButton")
##
def VBtoggle():
    global vbt_btn

    if vbt_btn.config('text')[-1] == 'ON':
        vbt_btn.config(text='OFF', style="Stop.TButton")
    else:
        vbt_btn.config(text='ON', style="Run.TButton")
##
def VCtoggle():
    global vct_btn

    if vct_btn.config('text')[-1] == 'ON':
        vct_btn.config(text='OFF', style="Stop.TButton")
    else:
        vct_btn.config(text='ON', style="Run.TButton")
##
def VDtoggle():
    global vdt_btn

    if vdt_btn.config('text')[-1] == 'ON':
        vdt_btn.config(text='OFF', style="Stop.TButton")
    else:
        vdt_btn.config(text='ON', style="Run.TButton")
##
def IApBtoggle():
    global iapbt_btn

    if iapbt_btn.config('text')[-1] == 'ON':
        iapbt_btn.config(text='OFF', style="Stop.TButton")
    else:
        iapbt_btn.config(text='ON', style="Run.TButton")
#
## ================ Make Phase Analyzer Window ==========================
def MakePhAWindow():
    global phawindow, PhAca, logo, PhAScreenStatus, PhADisp, AWGSync
    global COLORcanvas, CANVASwidthPhA, CANVASheightPhA, RevDate, AWGAMode, AWGAShape, AWGBMode
    global FFTwindow, CutDC, ColorMode, RefPhase, XYvpdiv
    global GRWPhA, X0LPhA, GRHPhA, Y0TPhA, DeBugMode, SWRev, PhAPlotMode
    global VScale, IScale, RefphEntry, AppendPhAData
    global vat_btn, vbt_btn, vct_btn, vabt_btn, vdt_btn
    global FrameRelief, BorderSize, CHANNELS

    if PhAScreenStatus.get() == 0:
        PhAScreenStatus.set(1)
        PhADisp.set(1)
        PhACheckBox()
        CutDC.set(1) # set to remove DC
        CANVASwidthPhA = GRWPhA + 2 * X0LPhA + int(21.25 * FontSize)    # The canvas width
        CANVASheightPhA = GRHPhA + Y0TPhA + int(2.25 * FontSize)         # The canvas height
        phawindow = Toplevel()
        phawindow.title("Phase Analyzer " + SWRev + RevDate)
        phawindow.protocol("WM_DELETE_WINDOW", DestroyPhAScreen)
        frame2phar = Frame(phawindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2phar.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2pha = Frame(phawindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2pha.pack(side=TOP, expand=YES, fill=BOTH)

        PhAca = Canvas(frame2pha, width=CANVASwidthPhA, height=CANVASheightPhA, background=COLORcanvas, cursor='cross')
        PhAca.bind("<Configure>", PhACaresize)
        PhAca.bind("<Return>", DoNothing)
        PhAca.bind("<space>", onCanvasSpaceBar)
        PhAca.pack(side=TOP, expand=YES, fill=BOTH)
        
        # menu buttons
        # right side drop down menu buttons
        dropmenu = Frame( frame2phar )
        dropmenu.pack(side=TOP)
        # File menu 
        PhAFilemenu = Menubutton(dropmenu, text="File", style="W5.TButton")
        PhAFilemenu.menu = Menu(PhAFilemenu, tearoff = 0 )
        PhAFilemenu["menu"] = PhAFilemenu.menu
        PhAFilemenu.menu.add_command(label="Save Config", command=BSaveConfigIA)
        PhAFilemenu.menu.add_command(label="Load Config", command=BLoadConfigIA)
        PhAFilemenu.menu.add_command(label="Run Script", command=RunScript)
        PhAFilemenu.menu.add_command(label="Save Data", command=BSavePhAData)
        PhAFilemenu.menu.add_checkbutton(label=' - Append', variable=AppendPhAData)
        PhAFilemenu.menu.add_command(label="Plot From File", command=PlotPhAFromFile)
        PhAFilemenu.menu.add_radiobutton(label=' - Vectors', variable=PhAPlotMode, value=0)
        PhAFilemenu.menu.add_radiobutton(label=' - Outline', variable=PhAPlotMode, value=1)
        PhAFilemenu.menu.add_command(label="Help", command=BHelp)
        PhAFilemenu.pack(side=LEFT, anchor=W)
        #
        PhAOptionmenu = Menubutton(dropmenu, text="Options", style="W8.TButton")
        PhAOptionmenu.menu = Menu(PhAOptionmenu, tearoff = 0 )
        PhAOptionmenu["menu"]  = PhAOptionmenu.menu
        PhAOptionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
        PhAOptionmenu.menu.add_checkbutton(label='Cut-DC', variable=CutDC)
        
        PhAOptionmenu.menu.add_command(label="-Background-", command=donothing)
        PhAOptionmenu.menu.add_radiobutton(label='Black', variable=ColorMode, value=0, command=BgColor)
        PhAOptionmenu.menu.add_radiobutton(label='White', variable=ColorMode, value=1, command=BgColor)
        PhAOptionmenu.pack(side=LEFT, anchor=W)
        #
        rsphmenu = Frame( frame2phar )
        rsphmenu.pack(side=TOP)
        rsphb2 = Button(rsphmenu, text="Stop", style="Stop.TButton", command=BStop)
        rsphb2.pack(side=RIGHT)
        rsphb3 = Button(rsphmenu, text="Run", style="Run.TButton", command=BStart)
        rsphb3.pack(side=RIGHT)
        #
        PhAFFTwindmenu = Menubutton(frame2phar, text="FFTwindow", style="W11.TButton")
        PhAFFTwindmenu.menu = Menu(PhAFFTwindmenu, tearoff = 0 )
        PhAFFTwindmenu["menu"]  = PhAFFTwindmenu.menu
        PhAFFTwindmenu.menu.add_radiobutton(label='Rectangular window (B=1)', variable=FFTwindow, value=0)
        PhAFFTwindmenu.menu.add_radiobutton(label='Cosine window (B=1.24)', variable=FFTwindow, value=1)
        PhAFFTwindmenu.menu.add_radiobutton(label='Triangular window (B=1.33)', variable=FFTwindow, value=2)
        PhAFFTwindmenu.menu.add_radiobutton(label='Hann window (B=1.5)', variable=FFTwindow, value=3)
        PhAFFTwindmenu.menu.add_radiobutton(label='Blackman window (B=1.73)', variable=FFTwindow, value=4)
        PhAFFTwindmenu.menu.add_radiobutton(label='Nuttall window (B=2.02)', variable=FFTwindow, value=5)
        PhAFFTwindmenu.menu.add_radiobutton(label='Flat top window (B=3.77)', variable=FFTwindow, value=6)
        PhAFFTwindmenu.pack(side=TOP)
        #
        FFTwindow.set(5) # default to Nuttall window (6)
        # 
        refph = Frame( frame2phar )
        refph.pack(side=TOP)
        refphlab = Label(refph, text="Ref Phase")
        refphlab.pack(side=LEFT, anchor=W)
        RefphEntry = Spinbox(refph, width=5, cursor='double_arrow', values=RefPhase)
        RefphEntry.bind('<MouseWheel>', onSpinBoxScroll)
        RefphEntry.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
        RefphEntry.bind("<Button-5>", onSpinBoxScroll)
        RefphEntry.pack(side=LEFT, anchor=W)
        RefphEntry.delete(0,"end")
        RefphEntry.insert(0,"CH-A")
        #
        if CHANNELS >= 1:
            vatb = Frame( frame2phar )
            vatb.pack(side=TOP)
            vatblab = Label(vatb, text="CH-A ")
            vatblab.pack(side=LEFT)
            vat_btn = Button(vatb, text="OFF", style="Stop.TButton", width=4, command=VAtoggle)
            vat_btn.pack(side=LEFT)
        if CHANNELS >= 2:
            vbtb = Frame( frame2phar )
            vbtb.pack(side=TOP)
            vbtblab = Label(vbtb, text="CH-B ")
            vbtblab.pack(side=LEFT)
            vbt_btn = Button(vbtb, text="OFF", style="Stop.TButton", width=4, command=VBtoggle)
            vbt_btn.pack(side=LEFT)
        #
        if CHANNELS >= 3:
            vctb = Frame( frame2phar )
            vctb.pack(side=TOP)
            vctblab = Label(vctb, text="CH-C ")
            vctblab.pack(side=LEFT)
            vct_btn = Button(vctb, text="OFF", style="Stop.TButton", width=4, command=VCtoggle)
            vct_btn.pack(side=LEFT)
        if CHANNELS >= 4:
            vdtb = Frame( frame2phar )
            vdtb.pack(side=TOP)
            vdtblab = Label(vdtb, text="CH-D ")
            vdtblab.pack(side=LEFT)
            vdt_btn = Button(vdtb, text="OFF", style="Stop.TButton", width=4, command=VDtoggle)
            vdt_btn.pack(side=LEFT)
        #
        if CHANNELS >= 2:
            vabtb = Frame( frame2phar )
            vabtb.pack(side=TOP)
            vabtblab = Label(vabtb, text="CA-CB ")
            vabtblab.pack(side=LEFT)
            vabt_btn = Button(vabtb, text="OFF", style="Stop.TButton", width=4, command=VABtoggle)
            vabt_btn.pack(side=LEFT)
        # Voltage Scale Spinbox
        vssb = Frame( frame2phar )
        vssb.pack(side=TOP)
        vslab = Label(vssb, text="Volts/div ")
        vslab.pack(side=LEFT)
        VScale = Spinbox(vssb, width=7, cursor='double_arrow', values=XYvpdiv)
        VScale.bind('<MouseWheel>', onSpinBoxScroll)
        VScale.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
        VScale.bind("<Button-5>", onSpinBoxScroll)
        VScale.pack(side=LEFT)
        VScale.delete(0,"end")
        VScale.insert(0,0.5)
        #
        dismiss1button = Button(frame2phar, text="Dismiss", style="W8.TButton", command=DestroyPhAScreen)
        dismiss1button.pack(side=TOP)
        # add Alice logo 
        ADI1 = Label(frame2phar, image=logo, anchor= "sw", compound="top") #  height=49, width=116,
        ADI1.pack(side=TOP)
#
## Destroy Phase Analizer window
def DestroyPhAScreen():
    global phawindow, PhAScreenStatus, PhAca, PhADisp
    
    PhAScreenStatus.set(0)
    PhADisp.set(0)
    PhACheckBox()
    phawindow.destroy()
#
## Resize Phase Analizer window
def PhACaresize(event):
    global PhAca, GRWPhA, XOLPhA, GRHPhA, Y0TPhA, CANVASwidthPhA, CANVASheightPhA, FontSize
     
    CANVASwidthPhA = event.width - 4
    CANVASheightPhA = event.height - 4
    GRWPhA = CANVASwidthPhA - (2 * X0LPhA) - int(21.25 * FontSize) # 170 new grid width
    GRHPhA = CANVASheightPhA - Y0TPhA - int(2.25 * FontSize) # 10 new grid height
    UpdatePhAAll()
#
def UpdatePhAAll():        # Update Data, trace and screen
    
    MakePhATrace()         # Update the traces
    UpdatePhAScreen()      # Update the screen

def UpdatePhATrace():      # Update trace and screen
    MakePhATrace()         # Update traces
    UpdatePhAScreen()      # Update the screen

def UpdatePhAScreen():     # Update screen with trace and text
    MakePhAScreen()        # Update the screen
    root.update()       # Activate updated screens    
#
## Find amplitude peaks and Phase
def MakePhATrace():        # Update the grid and trace
    global VAresult, VBresult, VABresult, PhaseVA, PhaseVB, PhaseVAB
    global PeakVA, PeakVB, PeakVAB
    global VCresult, VDresult, PhaseVC, PhaseVD
    global PeakVC, PeakVD
    global PeakfreqVA, PeakfreqVB, PeakfreqVC, PeakfreqVD
    global PeakphaseVA, PeakphaseVB, PeakphaseVC, PeakphaseVD, PeakphaseVAB
    global GRHPhA          # Screenheight
    global GRWPhA          # Screenwidth
    global SAMPLErate
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global TRACEmode, CHANNELS
    global Vdiv         # Number of vertical divisions
    global X0LPhA          # Left top X value
    global Y0TPhA          # Left top Y value  

    # Set the TRACEsize variable
    if len(VAresult) < 32 or len(VBresult) < 32:
        return
    TRACEsize = len(VAresult)     # Set the trace length
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)
    # print(TRACEsize, Fsample)
    # Horizontal conversion factors (frequency Hz) and border limits
    STARTsample = 0     # First sample in FFTresult[] that is used
    STARTsample = int(math.ceil(STARTsample))               # First within screen range
    STOPsample = 90000 / Fsample
    STOPsample = int(math.floor(STOPsample))                # Last within screen range, math.floor actually not necessary, part of int
#
    MAXsample = TRACEsize                                   # Just an out of range check
    if STARTsample > (MAXsample - 1):
        STARTsample = MAXsample - 1

    if STOPsample > MAXsample:
        STOPsample = MAXsample

    n = STARTsample +1
    PeakVA = PeakVB = PeakVC = PeakVD = PeakVAB = 0.0
    PeakfreqVA = PeakfreqVB = F = n * Fsample
    PeakphaseVA = PhaseVA[n]
    PeakphaseVB = PhaseVB[n]
    PeakSampleVB = PeakSampleVA = n

    while n <= STOPsample: # search for peaks
        F = n * Fsample
        try:
            VA = float(VAresult[n])   #
        except:
            VA = 0.0
        if VA > PeakVA:
            PeakVA = VA
            PeakfreqVA = F
            PeakphaseVA = PhaseVA[n]
            PeakSampleVA = n
            
        try:
            VB = float(VBresult[n]) #  
        except:
            VB = 0.0
        if VB > PeakVB:
            PeakVB = VB
            PeakfreqVB = F
            PeakphaseVB = PhaseVB[n]
            PeakSampleVB = n

        try:
            VC = float(VCresult[n])   #
        except:
            VC = 0.0
        if VC > PeakVC:
            PeakVC = VC
            PeakfreqVC = F
            PeakphaseVC = PhaseVC[n]
            PeakSampleVC = n
            
        try:
            VD = float(VDresult[n]) #  
        except:
            VD = 0.0
        if VD > PeakVD:
            PeakVD = VD
            PeakfreqVD = F
            PeakphaseVD = PhaseVD[n]
            PeakSampleVD = n

        try:
            VAB = float(VABresult[n])   #
        except:
            VAB = 0.0
        if VAB > PeakVAB:
            PeakVAB = VAB
            PeakfreqVAB = F
            PeakphaseVAB = PhaseVAB[n]
            PeakSampleVAB = n
        n = n + 1
#
## Draw the Phase Analyzer screen
def MakePhAScreen():       # Update the screen with traces and text
    global PeakVA, PeakVB, PeakVAB, PeakfreqVA, PeakfreqVB
    global PeakVC, PeakVD, PeakfreqVC, PeakfreqVD
    global PeakphaseVA, PeakphaseVB, PeakphaseVC, PeakphaseVD, PeakphaseVAB
    global CAVphase, CBVphase, CABVphase, CCVphase, CDVphase
    global CANVASheightPhA, CANVASwidthPhA, PhAca, TRACEwidth, GridWidth
    global COLORsignalband, COLORtext, COLORgrid  # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6, COLORtrace7
    global FFTwindow, FFTbandwidth, ZEROstuffing, FFTwindowname
    global X0LPhA          # Left top X value
    global Y0TPhA          # Left top Y value
    global GRWPhA          # Screenwidth
    global GRHPhA          # Screenheight
    global FontSize, Mulx, CHANNELS
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global AWGSAMPLErate, SAMPLErate, SHOWsamples, OverRangeFlagA, OverRangeFlagB
    global SMPfft       # number of FFT samples
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv, VScale        # Number of vertical divisions
    global vat_btn, vbt_btn, vct_btn, vdt_btn, vabt_btn, RefphEntry
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V, CHA_RC_HP, CHB_RC_HP
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2, CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global InOffA, InGainA, InOffB, InGainB
    global SV1, SV2, CHABphase, SVA_B
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasRMSV1, MeasRMSV2, MeasPhase, MeasRMSVA_B
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ

    # Delete all items on the screen
    PhAca.delete(ALL) # remove all items
    # SmoothBool = SmoothCurvesBP.get()
    # Draw circular grid lines
    i = 1
    xcenter = GRWPhA/2
    ycenter = (GRHPhA/2) + 14
    Radius = (GRWPhA-X0LPhA)/(1 + Vdiv.get()*2) # 11
    VoltsperPixel = float(VScale.get())/Radius
    TRadius = Radius * Vdiv.get() # 5
    x1 = X0LPhA
    x2 = X0LPhA + GRWPhA
    xright = 10 + xcenter + ( Vdiv.get() * Radius ) # 5
    while (i <= Vdiv.get()):
        x0 = xcenter - ( i * Radius )
        x1 = xcenter + ( i * Radius )
        y0 = ycenter - ( i * Radius )
        y1 = ycenter + ( i * Radius )
        VTxt = '{0:.2f}'.format(float(VScale.get()) * i)
        TOffset = xright+(4*FontSize)
        PhAca.create_oval( x0, y0, x1, y1, outline=COLORgrid, width=GridWidth.get())
        PhAca.create_line(xcenter, y0, xright, y0, fill=COLORgrid, width=GridWidth.get(), dash=(4,3))
        PhAca.create_text(xright, y0, text=str(VTxt), fill=COLORtrace1, anchor="w", font=("arial", FontSize+2 ))
        # 
        i = i + 1
    PhAca.create_line(xcenter, y0, xcenter, y1, fill=COLORgrid, width=GridWidth.get())
    PhAca.create_line(x0, ycenter, x1, ycenter, fill=COLORgrid, width=GridWidth.get())
    RAngle = math.radians(45)
    y = TRadius*math.sin(RAngle)
    x = TRadius*math.cos(RAngle)
    PhAca.create_line(xcenter-x, ycenter-y, xcenter+x, ycenter+y, fill=COLORgrid, width=GridWidth.get())
    PhAca.create_line(xcenter+x, ycenter-y, xcenter-x, ycenter+y, fill=COLORgrid, width=GridWidth.get())
    PhAca.create_text(x0, ycenter, text="180", fill=COLORgrid, anchor="e", font=("arial", FontSize+2 ))
    PhAca.create_text(x1, ycenter, text="0.0", fill=COLORgrid, anchor="w", font=("arial", FontSize+2 ))
    PhAca.create_text(xcenter, y0, text="90", fill=COLORgrid, anchor="s", font=("arial", FontSize+2 ))
    PhAca.create_text(xcenter, y1, text="-90", fill=COLORgrid, anchor="n", font=("arial", FontSize+2 ))
    YBot = y1
    # calculate phase error due half sample period offset 0.0018
    PhErr = 0.0

# Draw traces
#
    if RefphEntry.get() == "CH-A":
        CAVphase = 0.0
        CBVphase = PeakphaseVA - PeakphaseVB + PhErr
        if CHANNELS >= 3:
            CCVphase = PeakphaseVA - PeakphaseVC + PhErr
        if CHANNELS >= 4:
            CDVphase = PeakphaseVA - PeakphaseVD + PhErr
        CABVphase = PeakphaseVA - PeakphaseVAB
    elif RefphEntry.get() == "CH-B":
        CBVphase = 0.0
        CAVphase = PeakphaseVB - PeakphaseVA - PhErr
        if CHANNELS >= 3:
            CCVphase = PeakphaseVB - PeakphaseVC + PhErr
        if CHANNELS >= 4:
            CDVphase = PeakphaseVB - PeakphaseVD + PhErr
        CABVphase = PeakphaseVB - PeakphaseVAB
    elif RefphEntry.get() == "CH-C" and CHANNELS >= 3:
        CCVphase = 0.0
        CAVphase = PeakphaseVC - PeakphaseVA - PhErr
        CBVphase = PeakphaseVC - PeakphaseVB + PhErr
        if CHANNELS >= 4:
            CDVphase = PeakphaseVC - PeakphaseVD + PhErr
        CABVphase = PeakphaseVC - PeakphaseVAB
    elif RefphEntry.get() == "CH-D" and CHANNELS >= 4:
        CDVphase = 0.0
        CAVphase = PeakphaseVD - PeakphaseVA - PhErr
        CBVphase = PeakphaseVD - PeakphaseVB + PhErr
        CCVphase = PeakphaseVD - PeakphaseVC + PhErr
        CABVphase = PeakphaseVD - PeakphaseVAB
    #
    if CHANNELS >= 1:
        if CAVphase > 180:
            CAVphase = CAVphase - 360
        elif CAVphase < -180:
            CAVphase = CAVphase + 360
    if CHANNELS >= 2:
        if CBVphase > 180:
            CBVphase = CBVphase - 360
        elif CBVphase < -180:
            CBVphase = CBVphase + 360
    if CHANNELS >= 3:
        if CCVphase > 180:
            CCVphase = CCVphase - 360
        elif CCVphase < -180:
            CCVphase = CCVphase + 360
    if CHANNELS >= 4:
        if CDVphase > 180:
            CDVphase = CDVphase - 360
        elif CDVphase < -180:
            CDVphase = CDVphase + 360
    if CABVphase > 180:
        CABVphase = CABVphase - 360
    elif CABVphase < -180:
        CABVphase = CABVphase + 360    
    #
    if CHANNELS >= 1:
        if vat_btn.config('text')[-1] == 'ON':
            MagRadius = PeakVA / VoltsperPixel
            y1 = ycenter - MagRadius*math.sin(math.radians(CAVphase))
            if y1 > 1500:
                y1 = xright
            elif y1 < -500:
                y1 = ycenter - xright
            x1 = xcenter + MagRadius*math.cos(math.radians(CAVphase))
            if x1 > 1500:
                x1 = xright
            elif x1 < -500:
                x1 = xcenter - xright
            PhAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
    if CHANNELS >= 2:
        if vbt_btn.config('text')[-1] == 'ON':
            MagRadius = PeakVB / VoltsperPixel
            y1 = ycenter - MagRadius*math.sin(math.radians(CBVphase))
            if y1 > 1500:
                y1 = xright
            elif y1 < -500:
                y1 = ycenter - xright
            x1 = xcenter + MagRadius*math.cos(math.radians(CBVphase))
            if x1 > 1500:
                x1 = xright
            elif x1 < -500:
                x1 = xcenter - xright
            PhAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace2, arrow="last", width=TRACEwidth.get())
    if CHANNELS >= 3:
        #
        if vct_btn.config('text')[-1] == 'ON':
            MagRadius = PeakVC / VoltsperPixel
            y1 = ycenter - MagRadius*math.sin(math.radians(CCVphase))
            if y1 > 1500:
                y1 = xright
            elif y1 < -500:
                y1 = ycenter - xright
            x1 = xcenter + MagRadius*math.cos(math.radians(CCVphase))
            if x1 > 1500:
                x1 = xright
            elif x1 < -500:
                x1 = xcenter - xright
            PhAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace3, arrow="last", width=TRACEwidth.get())
    if CHANNELS >= 4:
        if vdt_btn.config('text')[-1] == 'ON':
            MagRadius = PeakVD / VoltsperPixel
            y1 = ycenter - MagRadius*math.sin(math.radians(CDVphase))
            if y1 > 1500:
                y1 = xright
            elif y1 < -500:
                y1 = ycenter - xright
            x1 = xcenter + MagRadius*math.cos(math.radians(CDVphase))
            if x1 > 1500:
                x1 = xright
            elif x1 < -500:
                x1 = xcenter - xright
            PhAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace4, arrow="last", width=TRACEwidth.get())
    
    # plot VA - VB vector
    if CHANNELS >= 2:
        if vabt_btn.config('text')[-1] == 'ON':
            MagRadius = PeakVAB / VoltsperPixel
            
            y1 = ycenter - MagRadius*math.sin(math.radians(CABVphase))
            if y1 > 1500:
                y1 = xright
            elif y1 < -500:
                y1 = ycenter - xright
            x1 = xcenter + MagRadius*math.cos(math.radians(CABVphase))
            if x1 > 1500:
                x1 = xright
            elif x1 < -500:
                x1 = xcenter - xright
            PhAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace5, arrow="last", width=TRACEwidth.get())
# display warning if input out of range
    if OverRangeFlagA == 1:
        x = X0LPhA+GRWPhA+10
        y = Y0TPhA+GRHPhA-40
        PhAca.create_rectangle(x-6, y-6, x+6, y+6, fill="#ff0000")
        PhAca.create_text (x+12, y, text="CHA Over Range", anchor=W, fill="#ff0000", font=("arial", FontSize+4 ))
    if OverRangeFlagB == 1:
        x = X0LPhA+GRWPhA+10
        y = Y0TPhA+GRHPhA-10
        PhAca.create_rectangle(x-6, y-6, x+6, y+6, fill="#ff0000")
        PhAca.create_text (x+12, y, text="CHB Over Range", anchor=W, fill="#ff0000", font=("arial", FontSize+4 ))
# General information on top of the grid
    SR_label = ' {0:.1f} '.format(SAMPLErate)
    txt = "    Sample rate: " + SR_label
    txt = txt + "    FFT samples: " + str(SHOWsamples)
    txt = txt + "   " + FFTwindowname
        
    x = X0LPhA
    y = 12
    idTXT = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    #
    x = X0LPhA + GRWPhA + 4
    y = 24
    if CHANNELS >= 1:
        if vat_btn.config('text')[-1] == 'ON':
            txt = "A Mag " + ' {0:.3f} '.format(PeakVA) + " RMS V" 
            TXT9  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace1, font=("arial", FontSize+4 ))
            y = y + 24
        #
            txt = "A Phase " + ' {0:.1f} '.format(CAVphase) + " Degrees"
            TXT14  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace1, font=("arial", FontSize+4 ))
            y = y + 24
    if CHANNELS >= 2:
        if vbt_btn.config('text')[-1] == 'ON':
            txt = "B Mag " + ' {0:.3f} '.format(PeakVB) + " RMS V" 
            TXT10  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace2, font=("arial", FontSize+4 ))
            y = y + 24
        #
            txt = "B Phase " + ' {0:.1f} '.format(CBVphase) + " Degrees"
            TXT15  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace2, font=("arial", FontSize+4 ))
            y = y + 24
    if CHANNELS >= 3:
        if vct_btn.config('text')[-1] == 'ON':
            txt = "C Mag " + ' {0:.3f} '.format(PeakVC) + " RMS V" 
            TXT11  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace3, font=("arial", FontSize+4 ))
            y = y + 24
        #
            txt = "C Phase " + ' {0:.1f} '.format(CCVphase) + " Degrees"
            TXT16  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace3, font=("arial", FontSize+4 ))
            y = y + 24
    if CHANNELS >= 4:
        if vdt_btn.config('text')[-1] == 'ON':
            txt = "D Mag " + ' {0:.3f} '.format(PeakVD) + " RMS V" 
            TXT12  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace4, font=("arial", FontSize+4 ))
            y = y + 24
        #
            txt = "D Phase " + ' {0:.1f} '.format(CDVphase) + " Degrees"
            TXT17  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace4, font=("arial", FontSize+4 ))
            y = y + 24
    if CHANNELS >= 2:
        if vabt_btn.config('text')[-1] == 'ON':
            txt = "A-B Mag " + ' {0:.3f} '.format(PeakVAB) + " RMS V" 
            TXT13  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace5, font=("arial", FontSize+4 ))
            y = y + 24
        #
            txt = "A-B Phase " + ' {0:.1f} '.format(CABVphase) + " Degrees"
            TXT18  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtrace5, font=("arial", FontSize+4 ))
            y = y + 24
    #
    txt = "A Freq " + ' {0:.1f} '.format(PeakfreqVA) + " Hertz"
    TXT19  = PhAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize+4 ))
    y = y + 24
#
    txt = " "
# print time domin measured period and frequency of displayed channels
    if ShowC1_V.get() == 1 or ShowC2_V.get() == 1:
        FindRisingEdge(VBuffA,VBuffB)
        if ShowC1_V.get() == 1:
            if MeasAHW.get() == 1:
                txt = txt + " CA Hi Width = " + ' {0:.3f} '.format(CHAHW/Mulx) + " mS "
            if MeasALW.get() == 1:
                txt = txt + " CA Lo Width = " + ' {0:.3f} '.format(CHALW/Mulx) + " mS "
            if MeasADCy.get() == 1:
                txt = txt + " CA DutyCycle = " + ' {0:.1f} '.format(CHADCy) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " CA Period = " + ' {0:.3f} '.format(CHAperiod/Mulx) + " mS "
            if MeasAFREQ.get() == 1:
                txt = txt + " CA Freq = "
                ChaF = float(CHAfreq)
                if ChaF < 1000:
                    V1String = ' {0:.2f} '.format(ChaF)
                    txt = txt + str(V1String) + " Hz "
                if ChaF > 1000 and ChaF < 1000000:
                    V1String = ' {0:.2f} '.format(ChaF/1000)
                    txt = txt + str(V1String) + " KHz "
                if ChaF > 1000000:
                    V1String = ' {0:.2f} '.format(ChaF/1000000)
                    txt = txt + str(V1String) + " MHz "
                #txt = txt + " CA Freq = " + ' {0:.1f} '.format(CHAfreq) + " Hz "
        if ShowC2_V.get() == 1:
            if MeasBHW.get() == 1:
                txt = txt + " CB Hi Width = " + ' {0:.3f} '.format(CHBHW/Mulx) + " mS "
            if MeasBLW.get() == 1:
                txt = txt + " CB Lo Width = " + ' {0:.3f} '.format(CHBLW/Mulx) + " mS "
            if MeasBDCy.get() == 1:
                txt = txt + " CB DutyCycle = " + ' {0:.1f} '.format(CHBDCy) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " CB Period = " + ' {0:.3f} '.format(CHBperiod/Mulx) + " mS "
            if MeasBFREQ.get() == 1:
                txt = txt + " CB Freq = "
                ChaF = float(CHBfreq)
                if ChaF < 1000:
                    V1String = ' {0:.2f} '.format(ChaF)
                    txt = txt + str(V1String) + " Hz "
                if ChaF > 1000 and ChaF < 1000000:
                    V1String = ' {0:.2f} '.format(ChaF/1000)
                    txt = txt + str(V1String) + " KHz "
                if ChaF > 1000000:
                    V1String = ' {0:.2f} '.format(ChaF/1000000)
                    txt = txt + str(V1String) + " MHz "
                #txt = txt + " CB Freq = " + ' {0:.1f} '.format(CHBfreq) + " Hz "

        if MeasPhase.get() == 1:
            txt = txt + " CA-B Phase = " + ' {0:.1f} '.format(CHABphase) + " deg "
        if MeasDelay.get() == 1:
            txt = txt + " CB-A Delay = " + ' {0:.3f} '.format(CHBADelayR1) + " mS "    
     
    x = X0LPhA
    y = YBot + int(2.5 *FontSize) #
    TXT18 = PhAca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    txt = " "
    if ShowC1_V.get() == 1:
    # Channel A information
        txt = "CHA: "
        if MeasDCV1.get() == 1: 
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV1)
        if MeasMaxV1.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV1)
        if MeasTopV1.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VATop)
        if MeasMinV1.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV1)
        if MeasBaseV1.get() == 1:
            txt = txt +  " Base = " + ' {0:.4f} '.format(VABase)
        if MeasMidV1.get() == 1:
            MidV1 = (MaxV1+MinV1)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV1)
        if MeasPPV1.get() == 1:
            PPV1 = MaxV1-MinV1
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV1)
        if MeasRMSV1.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV1)
        if MeasRMSVA_B.get() == 1:
            txt = txt +  " A-B RMS = " + ' {0:.4f} '.format(SVA_B)
        if MeasDiffAB.get() == 1:
            txt = txt +  " CA-CB = " + ' {0:.4f} '.format(DCV1-DCV2)
        if MeasUserA.get() == 1:
            try:
                TempValue = eval(UserAString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserALabel + " = " + V1String
        
    x = X0LPhA
    y = YBot + int(4*FontSize) # 
    TXT19 = PhAca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    txt= " "
    # Channel B information
    if ShowC2_V.get() == 1:
        txt = "CHB: "
        if MeasDCV2.get() == 1:
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV2)
        if MeasMaxV2.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV2)
        if MeasTopV2.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VBTop)
        if MeasMinV2.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV2)
        if MeasBaseV2.get() == 1:
            txt = txt +  " Base = " + ' {0:.4f} '.format(VBBase)
        if MeasMidV2.get() == 1:
            MidV2 = (MaxV2+MinV2)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV2)
        if MeasPPV2.get() == 1:
            PPV2 = MaxV2-MinV2
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV2)
        if MeasRMSV2.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV2)
        if MeasDiffBA.get() == 1:
            txt = txt +  " CB-CA = " + ' {0:.4f} '.format(DCV2-DCV1)
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String

    x = X0LPhA
    y = YBot + int(5.5 *FontSize) # 
    TXT20 = PhAca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
#
def BSavePhAData():
    global PeakVA, PeakVB, PeakVC, PeakVD
    global PeakfreqVA, PeakfreqVB
    global CAVphase, CBVphase, CABVphase
    global CCVphase, CDVphase, CHANNELS
    global MuxScreenStatus, AppendPhAData, PhADatafilename
    global vat_btn, vbt_btn, vct_btn, vdt_btn, vabt_btn

    # open file to save data
    if AppendPhAData.get() == 0:
        PhADatafilename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(PhADatafilename, 'a')
    DataFile.write( 'Amplitude, Phase, @ ' + str(PeakfreqVA) + ' Hertz\n')
    if CHANNELS >= 1:
        if vat_btn.config('text')[-1] == 'ON':
            DataFile.write( str(PeakVA) + ', ' + str(CAVphase) + ', CH A\n')
    if CHANNELS >= 2:
        if vbt_btn.config('text')[-1] == 'ON':
            DataFile.write( str(PeakVB) + ', ' + str(CBVphase) + ', CH B\n')
    if CHANNELS >= 3:
        if vct_btn.config('text')[-1] == 'ON':
            DataFile.write( str(PeakVA) + ', ' + str(CCVphase) + ', CH C\n')
    if CHANNELS >= 4:
        if vdt_btn.config('text')[-1] == 'ON':
            DataFile.write( str(PeakVB) + ', ' + str(CDVphase) + ', CH D\n')
    DataFile.close()
#
def PlotPhAFromFile():
    global CANVASheightPhA, CANVASwidthPhA, PhAca, TRACEwidth, GridWidth, PhAPlotMode
    global COLORsignalband, COLORtext, COLORgrid, SmoothCurves  # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6, COLORtrace7
    global GRWPhA, GRHPhA, X0LPhA, Vdiv, VScale, IScale 
# open file to read data from
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    i = 1
    xcenter = GRWPhA/2
    ycenter = (GRHPhA/2) + 14
    Radius = (GRWPhA-X0LPhA)/(1 + Vdiv.get()*2) # 11
    VoltsperPixel = float(VScale.get())/Radius
    mAperPixel = float(IScale.get())/Radius
    TRadius = Radius * Vdiv.get() # 5
    x1 = X0LPhA
    x2 = X0LPhA + GRWPhA
    PhATrace = []
# Read values from CVS file
    try:
        CSVFile = open(filename)
        dialect = csv.Sniffer().sniff(CSVFile.read(2048))
        CSVFile.seek(0)
        csv_f = csv.reader(CSVFile, dialect)
        for row in csv_f:
            try:
                PeakMag = float(row[0])
                PeakPhase = float(row[1])
                if row[2] == "CA-I" or row[2] == "CB-I":
                    MagRadius = PeakMag / mAperPixel
                else:
                    MagRadius = PeakMag / VoltsperPixel
            
                y1 = ycenter - MagRadius*math.sin(math.radians(PeakPhase))
                if y1 > 1500:
                    y1 = xright
                elif y1 < -500:
                    y1 = ycenter - xright
                x1 = xcenter + MagRadius*math.cos(math.radians(PeakPhase))
                if x1 > 1500:
                    x1 = xright
                elif x1 < -500:
                    x1 = xcenter - xright
                if PhAPlotMode.get() == 0:
                    PhAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace5, arrow="last", width=TRACEwidth.get())
                else:
                    PhATrace.append(x1)
                    PhATrace.append(y1)
            except:
                print( 'skipping non-numeric row')
        if PhAPlotMode.get() == 1:
            PhAca.create_line(PhATrace, fill=COLORtrace5, smooth=SmoothCurves.get(), splinestep=5, width=TRACEwidth.get())
        CSVFile.close()
    except:
        showwarning("WARNING","No such file found or wrong format!")
#
#
def STOREcsvfile():     # Store the trace as CSV file [frequency, magnitude or dB value]
    global FFTmemoryA, FFTresultA, SMPfft
    global FFTmemoryB, FFTresultB
    global PhaseA, PhaseB, freqwindow
    global AWGSAMPLErate, SAMPLErate, MaxSampleRate, ShowC1_VdB, ShowC2_VdB
    
    # Set the TRACEsize variable
    if ShowC1_VdB.get() == 1:
        TRACEsize = len(FFTresultA)     # Set the trace length
    elif ShowC2_VdB.get() == 1:
        TRACEsize = len(FFTresultB)
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        return()
# ask if save as magnitude or dB
    dB = askyesno("Mag or dB: ","Save amplidude data as dB (Yes) or Mag (No):\n", parent=freqwindow)
    # Make the file name and open it
    if dB == 0:
        PSD = askyesno("Mag/Root Hz? ","Save Mag in V/sqrt Hz? (yes) or (No):\n", parent=freqwindow)
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
    filename = "Spectrum-" + tme
    filename = filename + ".csv"
    # open file to save data
    filename = asksaveasfilename(initialfile = filename, defaultextension = ".csv",
                                 filetypes=[("Comma Separated Values", "*.csv")], parent=freqwindow)
    DataFile = open(filename,'a')  # Open output file
    HeaderString = 'Frequency-#, '
    if ShowC1_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'CA-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CA-Mag, '
    if ShowC2_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'CB-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CB-Mag, '
    if ShowC1_P.get() == 1:
        HeaderString = HeaderString + 'Phase A-B, '
    if ShowC2_P.get() == 1:
        HeaderString = HeaderString + 'Phase B-A, '
    HeaderString = HeaderString + '\n'
    DataFile.write( HeaderString )

    FBinWidth = float(SAMPLErate / 2.0) / (TRACEsize - 1)   # Frequency step per sample   
    n = 0
    
    while n < TRACEsize:
        F = n * FBinWidth
        txt = str(F)
        if ShowC1_VdB.get() == 1:
            V = 10 * math.log10(float(FFTresultA[n]))  # 
            if dB == 0:
                V = 10.0**(V/20.0) # RMS Volts
                if PSD == 1:
                    V = V/math.sqrt(FBinWidth) # per root Hz
            txt = txt + "," + str(V) 
        if ShowC2_VdB.get() == 1:
            V = 10 * math.log10(float(FFTresultB[n]))  #
            if dB == 0:
                V = 10.0**(V/20.0)# RMS Volts
                if PSD == 1:
                    V = V/math.sqrt(FBinWidth) # per root Hz
            txt = txt  + "," + str(V)
        if ShowC1_P.get() == 1:
            RelPhase = PhaseA[n]-PhaseB[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        if ShowC2_P.get() == 1:
            RelPhase = PhaseB[n]-PhaseA[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        txt = txt + "\n"
        DataFile.write(txt)
        n = n + 1    

    DataFile.close()                           # Close the file
##
# Make Spectrum Analyzer Screen
def MakeFreqScreen():       # Update the screen with traces and text
    global CANVASheightF, CANVASwidthF, SmoothCurvesSA
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM, PeakIndexA, PeakIndexB, Fsample
    global COLORgrid    # The colors
    global COLORsignalband, COLORtext
    global COLORtrace1, COLORtrace2
    global FSweepMode, LoopNum, MarkerFreqNum, TRACEwidth, GridWidth
    global DBdivindex   # Index value
    global DBdivlist    # dB per division list
    global DBlevel      # Reference level
    global FFTwindow, FFTbandwidth, ZEROstuffing, FFTwindowname
    global X0LF          # Left top X value
    global Y0TF          # Left top Y value
    global GRWF          # Screenwidth
    global GRHF          # Screenheight
    global FontSize, DevID
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global AWGSAMPLErate, SAMPLErate, MaxSampleRate, SingleShotSA, HScale, HarmonicMarkers
    global SAfreq_max, SAfreq_min, SAnum_bins, FBinWidth, SHOWsamples       # number of FFT samples
    global SAVScale, SAVPSD, SAvertmaxEntry, SAvertminEntry, SAvertmax, SAvertmin
    global StartFreqEntry, StopFreqEntry, PhCenFreqEntry, RelPhaseCenter
    global ShowC1_P, ShowC2_P, ShowRA_VdB, ShowRB_VdB, ShowMarker
    global ShowRA_P, ShowRB_P, ShowMathSA, FreqDisp
    global ShowFCur, ShowdBCur, FCursor, dBCursor
    global T1Fline, T2Fline, T1Pline, T1FRline, T2FRline, TFMline, TFRMline
    global T1PRline, T2PRline, TAFline, TBFline
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv         # Number of vertical divisions
    global SAfreq_max, SAfreq_min, SAnum_bins, FBinWidth

    # Delete all items on the screen
    MarkerFreqNum = 0
    FBinWidth = float(SAMPLErate / 2.0) / (SHOWsamples - 1)   # Frequency step per sample
    Freqca.delete(ALL) # remove all items
    try:
        StartFrequency = float(StartFreqEntry.get())
    except:
        StartFreqEntry.delete(0,"end")
        StartFreqEntry.insert(0,100)
        StartFrequency = 100
    try:
        StopFrequency = float(StopFreqEntry.get())
    except:
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,10000)
        StopFrequency = 10000
    try:
        Phasecenter = int(PhCenFreqEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenFreqEntry.delete(0,"end")
        PhCenFreqEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
    StopFrequency = SAfreq_max
    StartFrequency = SAfreq_min # SAnum_bins, FBinWidth
    # Draw horizontal grid lines
    i = 0
    x1 = X0LF
    x2 = X0LF + GRWF
    if SAVScale.get() == 0: # In dB
        while (i <= Vdiv.get()):
            y = Y0TF + i * GRHF/Vdiv.get()
            Dline = [x1,y,x2,y]
            if i == 0 or i == Vdiv.get():
                Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            Vaxis_value = (DBlevel.get() - (i * DBdivlist[DBdivindex.get()]))
            Vaxis_label = str(Vaxis_value)
            Freqca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
            if ShowC1_P.get() == 1 or ShowC2_P.get() == 1:
                Vaxis_value = ( 180 - ( i * (360 / Vdiv.get())))
                Vaxis_value = Vaxis_value + Phasecenter
                Vaxis_label = str(Vaxis_value)
                Freqca.create_text(x2+3, y, text=Vaxis_label, fill=COLORtrace3, anchor="w", font=("arial", FontSize ))
            i = i + 1
    else: # In rms V
        if SAVScale.get() == 2: # Log Scale
            try:
                LogVStop = math.log10(SAvertmax)
            except:
                LogVStop = 0.0
            try:
                LogVStart = math.log10(SAvertmin)
            except:
                LogVStart = -10
            LogVpixel = (LogVStart - LogVStop) / GRHF
            NumDec = LogVStart - LogVStop # number of major grids
            Gridpixel = GRHF/NumDec # number of pixels per major grid
            V = NumDec
            while V <= 0: # Major Grid lines
                try:
                    LogV = math.log10(10**V) # convet to log Volts
                    y = Y0TF + (LogV/LogVpixel)
                except:
                    y = Y0TF
                Dline = [x1,y,x2,y]
                Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                LNum = LogVStop + V
                if LNum == 1.0:
                    axis_label = "10.0"
                elif LNum == 0:
                    axis_label = "1.0"
                elif LNum == -1:
                    axis_label = "100mV"
                elif LNum == -2:
                    axis_label = "10mV"
                elif LNum == -3:
                    axis_label = "1mV"
                elif LNum == -4:
                    axis_label = "100uV"
                elif LNum == -5:
                    axis_label = "10uV"
                elif LNum == -6:
                    axis_label = "1uV"
                elif LNum == -7:
                    axis_label = "100nV"
                elif LNum == -8:
                    axis_label = "10nV"
                else:
                    axis_label = str(LogVStart+V)
                    print(LNum)
                Freqca.create_text(x1-3, y, text=axis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
                J = 2
                while J < 10: # Minor Grid lines
                    ym = y + (Gridpixel*math.log10(J))
                    Dline = [x1,ym,x2,ym]
                    Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
                    J = J + 1
                V = V + 1
        else: # Linear Scale
            i = 0
            Vper = (SAvertmax - SAvertmin) / Vdiv.get()
            while (i < Vdiv.get()+1):
                y = Y0TF + i * GRHF/Vdiv.get()
                Dline = [x1,y,x2,y]
                if i == 0 or i == Vdiv.get():
                    Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                else:
                    Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
                axis_value = (SAvertmax - (i * Vper))
                axis_label = ' {0:.3f} '.format(axis_value) # str(axis_value)
                Freqca.create_text(x1-3, y, text=axis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
                i = i + 1
    # Draw vertical grid lines 
    i = 0
    y1 = Y0TF
    y2 = Y0TF + GRHF
    if HScale.get() == 1:
        F = 1.0
        LogFStop = math.log10(StopFrequency)
        try:
            LogFStart = math.log10(StartFrequency)
        except:
            LogFStart = 0.0
        LogFpixel = (LogFStop - LogFStart) / GRWF
        # draw left and right edges
        while F <= StopFrequency:
            if F >= StartFrequency:
                try:
                    LogF = math.log10(F) # convet to log Freq
                    x = X0LF + (LogF - LogFStart)/LogFpixel
                except:
                    x = X0LF
                Dline = [x,y1,x,y2]
                if F == 1 or F == 10 or F == 100 or F == 1000 or F == 10000 or F == 100000:
                    Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    axis_label = str(F)
                    Freqca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
                else:
                    Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
                
            if F < 10:
                F = F + 1
            elif F < 100:
                F = F + 10
            elif F < 1000:
                F = F + 100
            elif F < 1000:
                F = F + 100
            elif F < 10000:
                F = F + 1000
            elif F < 100000:
                F = F + 10000
            elif F < 200000:
                F = F + 10000
    else:
        Freqdiv = (StopFrequency - StartFrequency) / 10
        while (i < 11):
            x = X0LF + i * GRWF/10.0
            Dline = [x,y1,x,y2]
            if i == 0 or i == 10:
                Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            axis_value = (StartFrequency + (i * Freqdiv))
            axis_label = ' {0:.0f} '.format(axis_value) # str(axis_value)
            Freqca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
            i = i + 1
    # Draw X - Y cursors if needed
    Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
    Yc = float(Y0TF) + Yconv * (DBlevel.get()) # Yc is the 0 dBm position, can be outside the screen!
    # Vertical conversion factors (level dBs) and border limits
    YVconv = float(GRHF) / (SAvertmax - SAvertmin) # 
    YVc = float(Y0TF) + YVconv * SAvertmax
    Fpixel = (StopFrequency - StartFrequency) / GRWF # Frequency step per screen pixel
    if ShowFCur.get() > 0:
        Dline = [FCursor, Y0TF, FCursor, Y0TF+GRHF]
        Freqca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScale.get() == 1:
            LogFStop = math.log10(StopFrequency)
            try:
                LogFStart = math.log10(StartFrequency)
            except:
                LogFStart = 0.0
            LogFpixel = (LogFStop - LogFStart) / GRWF
            xfreq = 10**(((FCursor-X0LF)*LogFpixel) + LogFStart)
        else:
            Fpixel = (StopFrequency - StartFrequency) / GRWF # Frequency step per screen pixel
            xfreq = ((FCursor-X0LF)*Fpixel)+StartFrequency
        XFString = ' {0:.2f} '.format(xfreq)
        V_label = XFString + " Hz"
        Freqca.create_text(FCursor+1, Y0TF+GRHF+6, text=V_label, fill=COLORtext, anchor="n", font=("arial", FontSize ))
        #Freqca.create_text(FCursor+1, dBCursor-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
#
    if ShowdBCur.get() > 0:
        Dline = [X0LF, dBCursor, X0LF+GRWF, dBCursor]
        Freqca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        if SAVScale.get() == 0: # In dB
            yvdB = ((Yc-dBCursor)/Yconv)
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " dBV"
        elif SAVScale.get() == 1: # Lin Scale
            yvdB = ((YVc-dBCursor)/YVconv)
            VdBString = ' {0:.3f} '.format(yvdB)
            V_label = VdBString + " Vrms"
        else: # Log Scale
            LogVpixel = (LogVStop - LogVStart) / GRHF
            Vlog = ((YVc - dBCursor) * LogVpixel) + LogVStart
            yvdB = 10**Vlog
            VdBString = ' {:.2e} '.format(yvdB)
            V_label = VdBString + " Vrms"
                
        Freqca.create_text(X0LF+GRWF-5, dBCursor, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
    #
    SmoothBool = SmoothCurvesSA.get()
    # Draw traces
    if len(T1Fline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHA
        if OverRangeFlagA == 1:
            Freqca.create_line(T1Fline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Freqca.create_line(T1Fline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() > 0:
            k = 1
            while k <= HarmonicMarkers.get():
                FreqA = k*PeakfreqA # * PeakIndexA*Fsample
                #
                if SAVScale.get() == 0: # In dB
                    if SAVPSD.get() == 1:
                        try:
                            dbA = 10 * math.log10(float(FFTresultA[PeakIndexA*k])/math.sqrt(FBinWidth))
                        except:
                            dbA = -100
                    else:
                        try:
                            dbA = 10 * math.log10(float(FFTresultA[PeakIndexA*k]))
                        except:
                            dbA = -100
                    if ShowMarker.get() == 2 and k > 1:
                        Peak_label = ' {0:.2f} '.format(dbA - PeakdbA) + ',' + ' {0:.1f} '.format(FreqA - PeakfreqA)
                    else:
                        Peak_label = ' {0:.2f} '.format(dbA) + ',' + ' {0:.1f} '.format(FreqA)
                    yA = Yc - Yconv * dbA
                else: # Volts Scale
                    try:
                        dbA = 10 * math.log10(float(FFTresultA[PeakIndexA*k]))   # Convert power to DBs
                    except:
                        dbA = -100
                    V = 10.0**(dbA/20.0)# convert back to RMS Volts
                    PeakV = 10.0**(PeakdbA/20.0)# convert back to RMS Volts
                    if SAVPSD.get() == 1: # per root Hz
                        V = V/math.sqrt(FBinWidth) 
                        PeakV = PeakV/math.sqrt(FBinWidth) # per root Hz
                    if SAVScale.get() == 2: # Log Scale
                        LogVpixel = (LogVStop - LogVStart) / GRHF
                        try:
                            LogV = math.log10(V) # convet to log Volts
                            yA = YVc - (LogV - LogVStart)/LogVpixel
                        except:
                            yA = YVc - YVconv * V
                        if ShowMarker.get() == 2 and k > 1:
                            Peak_label = ' {0:.2e} '.format(V - PeakV) + ',' + ' {0:.1f} '.format(FreqA - PeakfreqA)
                        else:
                            Peak_label = ' {0:.2e} '.format(V) + ',' + ' {0:.1f} '.format(FreqA)
                    else: # Lin Scale
                        if ShowMarker.get() == 2 and k > 1:
                            Peak_label = ' {0:.2f} '.format(V - PeakV) + ',' + ' {0:.1f} '.format(FreqA - PeakfreqA)
                        else:
                            Peak_label = ' {0:.2f} '.format(V) + ',' + ' {0:.1f} '.format(FreqA)
                        yA = YVc - YVconv * V
                #   
                if HScale.get() == 1:
                    try:
                        LogF = math.log10(FreqA) # convet to log Freq
                        xA = X0LF + int((LogF - LogFStart)/LogFpixel)
                    except:
                        xA = X0LF
                else:
                    xA = X0LF+int((FreqA - StartFrequency)/Fpixel)# +StartFrequency
                
                Freqca.create_text(xA, yA, text=Peak_label, fill=COLORtrace1, anchor="s", font=("arial", FontSize ))
                k = k + 1

    if len(T2Fline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHB
        if OverRangeFlagB == 1:
            Freqca.create_line(T2Fline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Freqca.create_line(T2Fline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() > 0:
            k = 1
            while k <= HarmonicMarkers.get():
                FreqB = k*PeakfreqB # PeakIndexB*Fsample
                #
                if SAVScale.get() == 0: # In dB
                    if SAVPSD.get() == 1:
                        try:
                            dbB = 10 * math.log10(float(FFTresultB[PeakIndexB*k])/math.sqrt(FBinWidth))
                        except:
                            dbB = -100
                    else:
                        try:
                            dbB = 10 * math.log10(float(FFTresultB[PeakIndexB*k]))
                        except:
                            dbb = -100
                    if ShowMarker.get() == 2 and k > 1:
                        Peak_label = ' {0:.2f} '.format(dbB - PeakdbB) + ',' + ' {0:.1f} '.format(FreqB - PeakfreqB)
                    else:
                        Peak_label = ' {0:.2f} '.format(dbB) + ',' + ' {0:.1f} '.format(FreqB)
                    yB = Yc - Yconv * dbB
                else: # Volts Scale
                    try:
                        dbB = 10 * math.log10(float(FFTresultB[PeakIndexB*k]))   # Convert power to DBs
                    except:
                        dbB = -100
                    V = 10.0**(dbB/20.0)# convert back to RMS Volts
                    PeakV = 10.0**(PeakdbB/20.0)# convert back to RMS Volts
                    if SAVPSD.get() == 1: # per root Hz
                        V = V/math.sqrt(FBinWidth) 
                        PeakV = PeakV/math.sqrt(FBinWidth) # per root Hz
                    if SAVScale.get() == 2: # Log Scale
                        LogVpixel = (LogVStop - LogVStart) / GRHF
                        try:
                            LogV = math.log10(V) # convet to log Volts
                            yB = YVc - (LogV - LogVStart)/LogVpixel
                        except:
                            yB = YVc - YVconv * V
                        if ShowMarker.get() == 2 and k > 1:
                            Peak_label = ' {0:.2e} '.format(V - PeakV) + ',' + ' {0:.1f} '.format(FreqB - PeakfreqB)
                        else:
                            Peak_label = ' {0:.2e} '.format(V) + ',' + ' {0:.1f} '.format(FreqB)
                    else: # Lin Scale
                        if ShowMarker.get() == 2 and k > 1:
                            Peak_label = ' {0:.2f} '.format(V - PeakV) + ',' + ' {0:.1f} '.format(FreqB - PeakfreqB)
                        else:
                            Peak_label = ' {0:.2f} '.format(V) + ',' + ' {0:.1f} '.format(FreqB)
                        yB = YVc - YVconv * V
                #   
                if HScale.get() == 1:
                    try:
                        LogF = math.log10(FreqB) # convet to log Freq
                        xB = X0LF + int((LogF - LogFStart)/LogFpixel)
                    except:
                        xB = X0LF
                else:
                    xB = X0LF+int((FreqB - StartFrequency)/Fpixel)# +StartFrequency
                
                Freqca.create_text(xB, yB, text=Peak_label, fill=COLORtrace2, anchor="s", font=("arial", FontSize ))
                k = k + 1
#
    if len(T1Pline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Freqca.create_line(T1Pline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(T2Pline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Freqca.create_line(T2Pline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRA_VdB.get() == 1 and len(T1FRline) > 4:   # Write the ref trace A if active
        Freqca.create_line(T1FRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRA) + ',' + ' {0:.1f} '.format(PeakfreqRA)
            Freqca.create_text(PeakxRA, PeakyRA, text=Peak_label, fill=COLORtraceR1, anchor="s", font=("arial", FontSize ))
    if ShowRB_VdB.get() == 1 and len(T2FRline) > 4:   # Write the ref trace B if active
        Freqca.create_line(T2FRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRB) + ',' + ' {0:.1f} '.format(PeakfreqRB)
            Freqca.create_text(PeakxRB, PeakyRB, text=Peak_label, fill=COLORtraceR2, anchor="s", font=("arial", FontSize ))
    if ShowRA_P.get() == 1 and len(T1PRline) > 4:   # Write the ref trace A if active
        Freqca.create_line(T1PRline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRB_P.get() == 1 and len(T2PRline) > 4:   # Write the ref trace A if active
        Freqca.create_line(T2PRline, fill=COLORtraceR4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMathSA.get() > 0 and len(TFMline) > 4:   # Write the Math trace if active
        Freqca.create_line(TFMline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() ==1:
            Peak_label = ' {0:.2f} '.format(PeakMdb) + ',' + ' {0:.1f} '.format(PeakfreqM)
            Freqca.create_text(PeakxM, PeakyM, text=Peak_label, fill=COLORtrace5, anchor="s", font=("arial", FontSize ))
    if ShowRMath.get() == 1 and len(TFRMline) > 4:   # Write the ref math trace if active
        Freqca.create_line(TFRMline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() ==1:
            Peak_label = ' {0:.2f} '.format(PeakRMdb) + ',' + ' {0:.1f} '.format(PeakfreqRM)
            Freqca.create_text(PeakxRM, PeakyRM, text=Peak_label, fill=COLORtraceR5, anchor="s", font=("arial", FontSize ))
    # General information on top of the grid
    SR_label = ' {0:.1f} '.format(SAMPLErate)
    txt = "Device ID " + DevID + " Sample rate: " + SR_label

    txt = txt + " " + FFTwindowname
        
    x = X0LF
    y = 12
    idTXT = Freqca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))

    # Start and stop frequency and dB/div and trace mode
    SR_label = ' {0:.1f} '.format(StartFrequency)
    SF_label = ' {0:.1f} '.format(StopFrequency)
    txt = SR_label + " to " + SF_label + " Hz"
    txt = txt + " " + str(DBdivlist[DBdivindex.get()]) + " dB/div"
    txt = txt + " Level: " + str(DBlevel.get()) + " dB "
    if FFTwindow.get() < 7:
        txt = txt + " FFT Bandwidth = " + ' {0:.2f} '.format(FBinWidth)
    else:
        txt = txt + " FFT Bandwidth = ???" 
    
    x = X0LF
    y = Y0TF+GRHF+23
    idTXT = Freqca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))
    
    if FreqTraceMode.get() == 1:
        txt ="Normal mode "

    if FreqTraceMode.get() == 2:
        txt = "Peak hold mode "
    
    if FreqTraceMode.get() == 3:
        txt = "Power average mode (" + str(TRACEaverage.get()) + ") " 

    if ZEROstuffing.get() > 0:
        txt = txt + "Zero Stuffing = " + str(ZEROstuffing.get())
    # Runstatus and level information
    if (RUNstatus.get() == 0) and (SingleShotSA.get() == 0):
        txt = txt + " Stopped "
    elif SingleShotSA.get() == 1:
        txt = txt + " Single Shot Trace "
    else:
        if FreqDisp.get() == 1:
            txt = txt + " Running "
        else:
            txt = txt + " Display off "
    x = X0LF
    y = Y0TF+GRHF+34
    IDtxt  = Freqca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", FontSize ))

def INITIALIZEstart():
    global SMPfft, FFTwindow, SHOWsamples, VBuffA, VBuffB
    global SMPfftpwrTwo, BodeDisp, FFTwindowshape
    global TRACEresetFreq, FreqTraceMode, LoopNum, FSweepMode, FSweepCont

    # First some subroutines to set specific variables
    #print("Buffer Length: ", len(VBuffA), "FFT Window Length: ", len(FFTwindowshape))
    #if len(VBuffA) != len(FFTwindowshape):
        #print("Requested to set FFT Window.")
    #CALCFFTwindowshape(len(VBuffA))
    CALCFFTwindowshape(SHOWsamples)
    if FreqTraceMode.get() == 1 and TRACEresetFreq == False:
        TRACEresetFreq = True               # Clear the memory for averaging or peak
    if FreqTraceMode.get() == 2 and LoopNum.get() == 1 and FSweepMode.get() > 0 and FSweepCont.get() == 0 and BodeDisp.get() >0:
        TRACEresetFreq = True               # Clear the memory for peak hold when using sweep generator
#
def CALCFFTwindowshape(WinLength):           # Make the FFTwindowshape for the windowing function
    global FFTbandwidth, FFTbw             # The FFT bandwidth
    global FFTwindow                # Which FFT window number is selected
    global FFTwindowname            # The name of the FFT window function
    global FFTwindowshape           # The window shape
    global AWGSAMPLErate, SAMPLErate, MaxSampleRate # The sample rate
    # Number of FFT samples is passed to function
    if WinLength < 128:
        print("Requested Window less then 128 samples?")
        return
    # FFTname and FFTbandwidth in milliHz
    FFTwindowname = "No such window"
    FFTbw = 0
    
    if FFTwindow.get() == 0:
        FFTwindowname = " Rectangular (no) window (B=1) "
        FFTbw = 1.0

    if FFTwindow.get() == 1:
        FFTwindowname = " Cosine window (B=1.24) "
        FFTbw = 1.24

    if FFTwindow.get() == 2:
        FFTwindowname = " Triangular window (B=1.33) "
        FFTbw = 1.33

    if FFTwindow.get() == 3:
        FFTwindowname = " Hann window (B=1.5) "
        FFTbw = 1.5

    if FFTwindow.get() == 4:
        FFTwindowname = " Blackman window (B=1.73) "
        FFTbw = 1.73

    if FFTwindow.get() == 5:
        FFTwindowname = " Nuttall window (B=2.02) "
        FFTbw = 2.02

    if FFTwindow.get() == 6:
        FFTwindowname = " Flat top window (B=3.77) "
        FFTbw = 3.77
        
    if FFTwindow.get() == 7:
        FFTwindowname = FFTUserWindowString
        FFTbw = 0.0
        try:
            FFTwindowshape = eval(FFTUserWindowString)
        except:
            FFTwindowshape = numpy.ones(1024)         # Initialize with ones
            print( "Filling FFT window with Ones")
    elif FFTwindow.get() == 8: # window shape array read from csv file
        FFTwindowname = "Window Shape From file"
        FFTbw = 0.0
    else:
        FFTbandwidth = int(FFTbw * (SAMPLErate/2.0) / float(WinLength)) 
        # Calculate the shape
        FFTwindowshape = numpy.ones(WinLength)         # Initialize with ones
        n = 0
        while n < WinLength:
            # Cosine window function - medium-dynamic range B=1.24
            if FFTwindow.get() == 1:
                w = math.sin(math.pi * n / (WinLength - 1))
                FFTwindowshape[n] = w * 1.571
            # Triangular non-zero endpoints - medium-dynamic range B=1.33
            if FFTwindow.get() == 2:
                w = (2.0 / WinLength) * ((WinLength/ 2.0) - abs(n - (WinLength - 1) / 2.0))
                FFTwindowshape[n] = w * 2.0
            # Hann window function - medium-dynamic range B=1.5
            if FFTwindow.get() == 3:
                w = 0.5 - 0.5 * math.cos(2 * math.pi * n / (WinLength - 1))
                FFTwindowshape[n] = w * 2.000
            # Blackman window, continuous first derivate function - medium-dynamic range B=1.73
            if FFTwindow.get() == 4:
                w = 0.42 - 0.5 * math.cos(2 * math.pi * n / (WinLength - 1)) + 0.08 * math.cos(4 * math.pi * n / (WinLength - 1))
                FFTwindowshape[n] = w * 2.381
            # Nuttall window, continuous first derivate function - high-dynamic range B=2.02
            if FFTwindow.get() == 5:
                w = 0.355768 - 0.487396 * math.cos(2 * math.pi * n / (WinLength - 1)) + 0.144232 * math.cos(4 * math.pi * n / (WinLength - 1))- 0.012604 * math.cos(6 * math.pi * n / (WinLength - 1))
                FFTwindowshape[n] = w * 2.811
            # Flat top window, medium-dynamic range, extra wide bandwidth B=3.77
            if FFTwindow.get() == 6:
                w = 1.0 - 1.93 * math.cos(2 * math.pi * n / (WinLength - 1)) + 1.29 * math.cos(4 * math.pi * n / (WinLength - 1))- 0.388 * math.cos(6 * math.pi * n / (WinLength - 1)) + 0.032 * math.cos(8 * math.pi * n / (WinLength - 1))
                FFTwindowshape[n] = w * 1.000
            n = n + 1
    #print("Length of Window: ", len(FFTwindowshape)) 
def BUserFFTwindow():
    global FFTUserWindowString, freqwindow, bodewindow, SpectrumScreenStatus, BodeScreenStatus

    TempString = FFTUserWindowString
    if BodeScreenStatus.get() > 0:
        FFTUserWindowString = askstring("User FFT Window", "Current User Window: " + FFTUserWindowString + "\n\nNew Window:\n", initialvalue=FFTUserWindowString, parent=bodewindow)
    elif SpectrumScreenStatus.get() > 0:
        FFTUserWindowString = askstring("User FFT Window", "Current User Window: " + FFTUserWindowString + "\n\nNew Window:\n", initialvalue=FFTUserWindowString, parent=freqwindow)
    else:
        FFTUserWindowString = askstring("User FFT Window", "Current User Window: " + FFTUserWindowString + "\n\nNew Window:\n", initialvalue=FFTUserWindowString)
    if (FFTUserWindowString == None):         # If Cancel pressed, then None
        FFTUserWindowString = TempString

def BFileFFTwindow():
    global FFTwindowshape, FFTwindow

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=freqwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
        FFTwindowshape = []
        for row in csv_f:
            try:
                FFTwindowshape.append(float(row[0]))
            except:
                print( 'skipping non-numeric row')
        FFTwindowshape = numpy.array(FFTwindowshape)
        CSVFile.close()
        if len(FFTwindowshape) < 1024:
            extra = int((1024 - len(FFTwindowshape)) / 2)
            FFTwindowshape = numpy.pad(FFTwindowshape,(extra, extra), 'edge')
    except:
        showwarning("WARNING","No such file found or wrong format!")
#
def onCanvasFreqRightClick(event):
    global ShowFCur, ShowdBCur, FCursor, dBCursor, RUNstatus, Freqca

    FCursor = event.x
    dBCursor = event.y
    if RUNstatus.get() == 0:
        UpdateFreqScreen()
    Freqca.bind('<MouseWheel>', onCanvasFreqClickScroll)
    Freqca.bind("<Button-4>", onCanvasFreqClickScroll)# with Linux OS
    Freqca.bind("<Button-5>", onCanvasFreqClickScroll)
#
def onCanvasFreqClickScroll(event):
    global ShowFCur, ShowdBCur, FCursor, dBCursor, RUNstatus, Freqca
    
    if event.widget == Freqca:
        ShiftKeyDwn = event.state & 1
        if ShowFCur.get() > 0 and ShiftKeyDwn == 0:
            # respond to Linux or Windows wheel event
            if event.num == 5 or event.delta == -120:
                FCursor -= 1
            if event.num == 4 or event.delta == 120:
                FCursor += 1
        elif ShowdBCur.get() > 0 or ShiftKeyDwn == 1:
            # respond to Linux or Windows wheel event
            if event.num == 5 or event.delta == -120:
                dBCursor += 1
            if event.num == 4 or event.delta == 120:
                dBCursor -= 1
        if RUNstatus.get() == 0:
            UpdateFreqScreen()
# 
def onCanvasFreqLeftClick(event):
    global X0LF          # Left top X value 
    global Y0TF          # Left top Y value
    global GRWF          # Screenwidth
    global GRHF          # Screenheight
    global FontSize
    global Freqca, MarkerLoc, SAMPLErate, MaxSampleRate
    global COLORgrid, COLORtext, HScale, ShowC1_VdB, ShowC2_VdB
    global COLORtrace1, COLORtrace2, StartFreqEntry, StopFreqEntry
    global AWGSAMPLErate, RUNstatus, COLORtext, MarkerFreqNum, PrevdBV, PrevF
    global SAVScale, SAVPSD, SAvertmaxEntry, SAvertminEntry, SAvertmax, SAvertmin

    if (RUNstatus.get() == 0):
        MarkerFreqNum = MarkerFreqNum + 1
        COLORmarker = COLORgrid
        if ShowC1_VdB.get() == 1:
            COLORmarker = COLORtrace1
        elif ShowC2_VdB.get() == 1:
            COLORmarker = COLORtrace2
        try:
            StartFrequency = float(StartFreqEntry.get())
        except:
            StartFreqEntry.delete(0,"end")
            StartFreqEntry.insert(0,100)
            StartFrequency = 100
        try:
            StopFrequency = float(StopFreqEntry.get())
        except:
            StopFreqEntry.delete(0,"end")
            StopFreqEntry.insert(0,100)
            StopFrequency = 100
        # draw X at marker point and number
        Freqca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORmarker)
        Freqca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORmarker)
        Freqca.create_text(event.x+4, event.y, text=str(MarkerFreqNum), fill=COLORmarker, anchor="w", font=("arial", FontSize ))
        # Vertical conversion factors (level dBs) and border limits
        Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
        YVconv = float(GRHF) / (SAvertmax - SAvertmin) # * Vdiv.get()
        Yc = float(Y0TF) + Yconv * (DBlevel.get())  # Yc is the 0 dBm position, can be outside the screen!
        YVc = float(Y0TF) + YVconv * SAvertmax
        Yphconv = float(GRHF) / 360
        Yp = float(Y0TF) + Yphconv + 180
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScale.get() == 1:
            LogFStop = math.log10(StopFrequency)
            try:
                LogFStart = math.log10(StartFrequency)
            except:
                LogFStart = 0.0
            LogFpixel = (LogFStop - LogFStart) / GRWF
            xfreq = 10**(((event.x-X0LF)*LogFpixel) + LogFStart)
        else:
            Fpixel = (StopFrequency - StartFrequency) / GRWF # Frequency step per screen pixel
            xfreq = ((event.x-X0LF)*Fpixel)+StartFrequency
        #
        try:
            LogVStop = math.log10(SAvertmax)
        except:
            LogVStop = 0.0
        try:
            LogVStart = math.log10(SAvertmin)
        except:
            LogVStart = -10
        LogVpixel = (LogVStop - LogVStart) / GRHF
        #
        XFString = ' {0:.2f} '.format(xfreq)
        if SAVScale.get() == 0:
            yvdB = ((Yc-event.y)/Yconv)
            VdBString = ' {0:.3f} '.format(yvdB)
            V_label = str(MarkerFreqNum) + " " + XFString + " Hz, " + VdBString + " dBV"
        else:
            if SAVScale.get() == 1:
                yvdB = ((YVc-event.y)/YVconv)
                VdBString = ' {0:.3f} '.format(yvdB)
            else:
                Vlog = ((YVc - event.y) * LogVpixel) + LogVStart
                yvdB = 10**Vlog
                VdBString = ' {:.2e} '.format(yvdB)
            V_label = str(MarkerFreqNum) + " " + XFString + " Hz, " + VdBString + " Vrms"
        
        if MarkerFreqNum > 1:
            DeltaV = ' {0:.3f} '.format(yvdB-PrevdBV)
            DeltaF = ' {0:.2f} '.format(xfreq-PrevF)
            if SAVScale.get() == 0:
                DeltaV = ' {0:.3f} '.format(yvdB-PrevdBV)
                V_label = V_label + " Delta " + DeltaF + " Hz, " + DeltaV + " dBV"
            else:
                if SAVScale.get() == 1:
                    DeltaV = ' {0:.3f} '.format(yvdB-PrevdBV)
                else:
                    DeltaV = ' {0:.2e} '.format(yvdB-PrevdBV)
                V_label = V_label + " Delta " + DeltaF + " Hz, " + DeltaV + " Vrms"
        x = X0LF + 5
        y = Y0TF + 3 + (MarkerFreqNum*10)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0LF + GRWF - 5
            y = Y0TF + 3 + (MarkerFreqNum*10)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0LF + 5
            y = Y0TF + GRHF + 3 - (MarkerFreqNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0LF + GRWF - 5
            y = Y0TF + GRHF + 3 - (MarkerFreqNum*10)
            Justify = 'e'
        Freqca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", FontSize ))
        PrevdBV = yvdB
        PrevF = xfreq
#
def onCanvasSAOne(event):
    global ShowC1_VdB
    if ShowC1_VdB.get() == 0:
        ShowC1_VdB.set(1)
    else:
        ShowC1_VdB.set(0)
#
def onCanvasSATwo(event):
    global ShowC2_VdB
    if ShowC2_VdB.get() == 0:
        ShowC2_VdB.set(1)
    else:
        ShowC2_VdB.set(0)
# 
def onCanvasSAThree(event):
    global ShowC1_P
    if ShowC1_P.get() == 0:
        ShowC1_P.set(1)
    else:
        ShowC1_P.set(0)
#
def onCanvasSAFour(event):
    global ShowC2_P
    if ShowC2_P.get() == 0:
        ShowC2_P.set(1)
    else:
        ShowC2_P.set(0)
#
def onCanvasSAFive(event):
    global ShowMarker
    if ShowMarker.get() == 0:
        ShowMarker.set(1)
    else:
        ShowMarker.set(0)
#
def onCanvasSASix(event):
    global ShowRA_VdB
    if ShowRA_VdB.get() == 0:
        ShowRA_VdB.set(1)
    else:
        ShowRA_VdB.set(0)
# 
def onCanvasSASeven(event):
    global ShowRB_VdB
    if ShowRB_VdB.get() == 0:
        ShowRB_VdB.set(1)
    else:
        ShowRB_VdB.set(0)
#
def onCanvasSAEight(event):
    global ShowMathSA
    ShowMathSA.set(2)
#
def onCanvasSANine(event):
    global ShowMathSA
    ShowMathSA.set(1)
#
def onCanvasSAZero(event):
    global ShowMathSA
    ShowMathSA.set(0)
#
def onCanvasSASnap(event):
    BSTOREtraceSA()
#
def onCanvasSANormal(event):
    BNormalmode()
#
def onCanvasSAPeak(event):
    BPeakholdmode()

def onCanvasSAReset(event):
    BResetFreqAvg()
#
def onCanvasSAAverage(event):
    BAveragemode()
#
def onCanvasShowFcur(event):
    global ShowFCur
    if ShowFCur.get() == 0:
        ShowFCur.set(1)
    else:
        ShowFCur.set(0)
#
def onCanvasShowdBcur(event):
    global ShowdBCur
    if ShowdBCur.get() == 1:
        ShowdBCur.set(0)
    else:
        ShowdBCur.set(1)
#
def onCanvasShowPcur(event):
    global ShowdBCur
    if ShowdBCur.get() == 2:
        ShowdBCur.set(0)
    else:
        ShowdBCur.set(2)
#
def onCanvasBodeRightClick(event):
    global ShowBPCur, ShowBdBCur, BPCursor, BdBCursor, RUNstatus, Bodeca

    BPCursor = event.x
    BdBCursor = event.y
    if RUNstatus.get() == 0:
        UpdateBodeScreen()
    #Bodeca.bind_all('<MouseWheel>', onCanvasBodeClickScroll)
    Bodeca.bind('<MouseWheel>', onCanvasBodeClickScroll)
    Bodeca.bind("<Button-4>", onCanvasBodeClickScroll)# with Linux OS
    Bodeca.bind("<Button-5>", onCanvasBodeClickScroll)
#
def onCanvasBodeClickScroll(event):
    global ShowBPCur, ShowBdBCur, BPCursor, BdBCursor, RUNstatus

    # print event.state
    shift_key = event.state & 1
    if ShowBPCur.get() > 0 and shift_key == 0:
    # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            BPCursor -= 1
        if event.num == 4 or event.delta == 120:
            BPCursor += 1
    elif ShowBdBCur.get() > 0 or shift_key == 1:
    # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            BdBCursor += 1
        if event.num == 4 or event.delta == 120:
            BdBCursor -= 1
    if RUNstatus.get() == 0:
        UpdateBodeScreen()
# 
def onCanvasBodeLeftClick(event):
    global X0LBP          # Left top X value 
    global Y0TBP         # Left top Y value
    global GRWBP          # Screenwidth
    global GRHBP          # Screenheight
    global FontSize
    global Bodeca, MarkerLoc, SAMPLErate
    global COLORgrid, COLORtext, HScaleBP, ShowCA_VdB, ShowCB_VdB, DBdivindexBP
    global COLORtrace1, COLORtrace2, COLORtrace6, StartBodeEntry, StopBodeEntry, DBlevelBP
    global AWGSAMPLErate, RUNstatus, COLORtext, MarkerFreqNum, PrevdBV, PrevF, Vdiv

    if (RUNstatus.get() == 0):
        MarkerFreqNum = MarkerFreqNum + 1
        COLORmarker = COLORtrace6 # COLORgrid
        if ShowCA_VdB.get() == 1:
            COLORmarker = COLORtrace1
        elif ShowCB_VdB.get() == 1:
            COLORmarker = COLORtrace2
        try:
            EndFreq = float(StopBodeEntry.get())
        except:
            StopBodeEntry.delete(0,"end")
            StopBodeEntry.insert(0,10000)
            EndFreq = 10000
        try:
            BeginFreq = float(StartBodeEntry.get())
        except:
            StartBodeEntry.delete(0,"end")
            StartBodeEntry.insert(0,100)
            BeginFreq = 100
        # draw X at marker point and number
        Bodeca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORmarker)
        Bodeca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORmarker)
        Bodeca.create_text(event.x+4, event.y, text=str(MarkerFreqNum), fill=COLORmarker, anchor="w", font=("arial", FontSize ))
        # Vertical conversion factors (level dBs) and border limits
        Yconv = float(GRHBP) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
        Yc = float(Y0TBP) + Yconv * (DBlevelBP.get()) # Yc is the 0 dBm position, can be outside the screen!
        Yphconv = float(GRHBP) / 360
        Yp = float(Y0TBP) + Yphconv + 180
        x1 = X0LBP + 14
        x2 = x1 + GRWBP
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScaleBP.get() == 1:
            LogFStop = math.log10(EndFreq)
            try:
                LogFStart = math.log10(BeginFreq)
            except:
                LogFStart = 0.0
            LogFpixel = (LogFStop - LogFStart) / GRWBP
            xfreq = 10**(((event.x-x1)*LogFpixel) + LogFStart)
        else:
            Fpixel = (EndFreq - BeginFreq) / GRWBP # Frequency step per screen pixel
            xfreq = ((event.x-x1)*Fpixel)+BeginFreq

        yvdB = ((Yc-event.y)/Yconv)
        VdBString = ' {0:.1f} '.format(yvdB)
        XFString = ' {0:.2f} '.format(xfreq)
        V_label = str(MarkerFreqNum) + " " + XFString + " Hz, " + VdBString + " dBV"
        if MarkerFreqNum > 1:
            DeltaV = ' {0:.3f} '.format(yvdB-PrevdBV)
            DeltaF = ' {0:.2f} '.format(xfreq-PrevF)
            V_label = V_label + " Delta " + DeltaF + " Hz, " + DeltaV + " dBV"
        x = x1 + 5
        y = Y0TBP + 3 + (MarkerFreqNum*10)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = x2 - 5
            y = Y0TBP + 3 + (MarkerFreqNum*10)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = x1 + 5
            y = Y0TBP + GRHBP + 3 - (MarkerFreqNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = x2 - 5
            y = Y0TBP + GRHBP + 3 - (MarkerFreqNum*10)
            Justify = 'e'
        Bodeca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", FontSize ))
        PrevdBV = yvdB
        PrevF = xfreq
#
def onCanvasBdOne(event):
    global ShowCA_VdB
    if ShowCA_VdB.get() == 0:
        ShowCA_VdB.set(1)
    else:
        ShowCA_VdB.set(0)
#
def onCanvasBdTwo(event):
    global ShowCB_VdB
    if ShowCB_VdB.get() == 0:
        ShowCB_VdB.set(1)
    else:
        ShowCB_VdB.set(0)
# 
def onCanvasBdThree(event):
    global ShowCA_P
    if ShowCA_P.get() == 0:
        ShowCA_P.set(1)
    else:
        ShowCA_P.set(0)
#
def onCanvasBdFour(event):
    global ShowCB_P
    if ShowCB_P.get() == 0:
        ShowCB_P.set(1)
    else:
        ShowCB_P.set(0)
#
def onCanvasBdFive(event):
    global ShowMarkerBP
    if ShowMarkerBP.get() == 0:
        ShowMarkerBP.set(1)
    else:
        ShowMarkerBP.set(0)
#
def onCanvasBdSix(event):
    global ShowRA_VdB
    if ShowRA_VdB.get() == 0:
        ShowRA_VdB.set(1)
    else:
        ShowRA_VdB.set(0)
# 
def onCanvasBdSeven(event):
    global ShowRB_VdB
    if ShowRB_VdB.get() == 0:
        ShowRB_VdB.set(1)
    else:
        ShowRB_VdB.set(0)
#
def onCanvasBdEight(event):
    global ShowMathBP
    ShowMathBP.set(2)
#
def onCanvasBdNine(event):
    global ShowMathBP
    ShowMathBP.set(1)
#
def onCanvasBdZero(event):
    global ShowMathBP
    ShowMathBP.set(0)
#
def onCanvasBdSnap(event):
    BSTOREtraceBP()
#
def onCanvasShowBPcur(event):
    global ShowBPCur
    if ShowBPCur.get() == 0:
        ShowBPCur.set(1)
    else:
        ShowBPCur.set(0)
#
def onCanvasShowBdBcur(event):
    global ShowBdBCur
    if ShowBdBCur.get() == 1:
        ShowBdBCur.set(0)
    else:
        ShowBdBCur.set(1)
#
def onCanvasShowPdBcur(event):
    global ShowBdBCur
    if ShowBdBCur.get() == 2:
        ShowBdBCur.set(0)
    else:
        ShowBdBCur.set(2)
#
def onAWGAscroll(event):
    global AWGAShape
    
    onTextScroll(event)
    time.sleep(0.05)
    MakeAWGwaves()
    time.sleep(0.05)
#
def onAWGBscroll(event):
    global AWGBShape
    
    onTextScroll(event)
    time.sleep(0.05)
    MakeAWGwaves()
    time.sleep(0.05)
#
def onHzPosScroll(event):

    onTextScroll(event)
    SetHorzPoss()
#
def onTrigLevelScroll(event):

    onTextScroll(event)
    BTriglevel()
#
def onTextScroll(event):   # Use mouse wheel to scroll entry values, august 7
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    NewVal = OldValfl
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta == -120:
        NewVal = OldValfl - Step
    if event.num == 4 or event.delta == 120:
        NewVal = OldValfl + Step
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor
#
def onAWGAkey(event):
    global AWGAShape
    
    onTextKey(event)
    MakeAWGwaves()
#
def onAWGBkey(event):
    global AWGBShape
    
    onTextKey(event)
    MakeAWGwaves()
#
def onTextKeyAWG(event):
    onTextKey(event)
    MakeAWGwaves()
#
# Use Arriw keys to inc dec entry values
def onTextKey(event):
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    if platform.system() == "Windows":
        if event.keycode == 38: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 40: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Linux":
        if event.keycode == 111: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 116: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Darwin":
        if event.keycode == 0x7D: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 0x7E: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    else:
        return
#
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor
#
def onSpinBoxScroll(event):
    spbox = event.widget
    if sys.version_info[0] == 3 and sys.version_info[1] > 6: # Spin Boxes do this automatically in Python > 3.6 apparently
        return
    if event.num == 4 or event.delta > 0: # if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    if event.num == 5 or event.delta < 0:
        spbox.invoke('buttondown')
#
# ================ Make awg sub window ==========================
def MakeAWGWindow():
    global AWGAShape, AWGBShape, awgwindow, AWGChannels, FrameBG, BorderSize
    global AWGScreenStatus, AWGAShapeLabel, AwgAOnOffBt
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGBShapeLabel, AwgBOnOffBt, AuxDACEntry, awgbph, AWGBPhaseEntry
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global RevDate, phaseblab, duty1lab, duty2lab, AwgaOnOffLb, AwgbOnOffLb
    global AwgANoiseBt, PWMDivEntry, PWMWidthEntry, AWGALength, AWGBLength
    global AwgLayout, AWG_Amp_Mode, SWRev, BisCompA, LockFreq, bcompa # 0 = Min/Max mode, 1 = Amp/Offset
    global AwgString1, AwgString2, AwgString3, AwgString4, AwgString5, AwgString6
    global AwgString7, AwgString8, AwgString9, AwgString10, AwgString11, AwgString12
    global AwgString13, AwgString14, AwgString15, AwgString16
    
    if AWGScreenStatus.get() == 0:
        AWGScreenStatus.set(1)
        
        awgwindow = Toplevel()
        awgwindow.title("AWG Controls " + SWRev + RevDate)
        awgwindow.resizable(FALSE,FALSE)
        awgwindow.geometry('+0+100')
        awgwindow.configure(background=FrameBG, borderwidth=BorderSize)
        awgwindow.protocol("WM_DELETE_WINDOW", DestroyAWGScreen)
        #
        frame2 = LabelFrame(awgwindow, text="AWG CH A", style="A10R1.TLabelframe")
        frame3 = LabelFrame(awgwindow, text="AWG CH B", style="A10R2.TLabelframe")
        frame4 = LabelFrame(awgwindow, text="AUX DAC Voltage", style="A10R6.TLabelframe")
        #
        if AwgLayout == "Horz":
            frame4.pack(side=BOTTOM, expand=1, fill=Y)
            frame2.pack(side=LEFT, expand=1, fill=X)
            frame3.pack(side=LEFT, expand=1, fill=X)
             
        else:
            frame4.pack(side=BOTTOM, expand=1, fill=Y)
            frame2.pack(side=TOP, expand=1, fill=Y)
            frame3.pack(side=TOP, expand=1, fill=Y)
        #
        if AWGChannels >= 1:
            # now AWG A
            # AWG enable sub frame
            # On / Off button
            awgaOnOff = Frame( frame2 )
            awgaOnOff.pack(side=TOP)
            AwgaOnOffLb = Label(awgaOnOff, text="AWG A Output ")
            AwgaOnOffLb.pack(side=LEFT)
            AwgAOnOffBt = Button(awgaOnOff, text="OFF", style="Stop.TButton", width=4, command=AWGAOutToggle)
            AwgAOnOffBt.pack(side=LEFT)
    #
            awg1eb = Frame( frame2 )
            awg1eb.pack(side=TOP)
            ShapeAMenu = Menubutton(awg1eb, text="Shape", style="W6.TButton")
            ShapeAMenu.menu = Menu(ShapeAMenu, tearoff = 0 )
            ShapeAMenu["menu"] = ShapeAMenu.menu
            ShapeAMenu.menu.add_command(label="-Basic-", foreground="blue", command=donothing)
            ShapeAMenu.menu.add_radiobutton(label="DC", variable=AWGAShape, value=0, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString1, variable=AWGAShape, value=1, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString2, variable=AWGAShape, value=2, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString3, variable=AWGAShape, value=3, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString4, variable=AWGAShape, value=4, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString5, variable=AWGAShape, value=5, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString6, variable=AWGAShape, value=6, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString7, variable=AWGAShape, value=7, command=MakeAWGwaves)
            ShapeAMenu.menu.add_radiobutton(label=AwgString8, variable=AWGAShape, value=8, command=MakeAWGwaves)
            if AWGShowAdvanced.get() > 0:
                ShapeAMenu.menu.add_command(label="-Advanced-", foreground="blue", command=donothing)
                ShapeAMenu.menu.add_radiobutton(label=AwgString9, variable=AWGAShape, value=9, command=MakeAWGwaves)
                ShapeAMenu.menu.add_radiobutton(label=AwgString10, variable=AWGAShape, value=10, command=MakeAWGwaves)
                ShapeAMenu.menu.add_radiobutton(label=AwgString11, variable=AWGAShape, value=11, command=MakeAWGwaves)
                ShapeAMenu.menu.add_radiobutton(label=AwgString12, variable=AWGAShape, value=12, command=MakeAWGwaves)
                ShapeAMenu.menu.add_radiobutton(label=AwgString13, variable=AWGAShape, value=13, command=MakeAWGwaves)
                ShapeAMenu.menu.add_radiobutton(label=AwgString14, variable=AWGAShape, value=14, command=MakeAWGwaves)
                ShapeAMenu.menu.add_radiobutton(label=AwgString15, variable=AWGAShape, value=15, command=MakeAWGwaves)
                ShapeAMenu.menu.add_radiobutton(label=AwgString16, variable=AWGAShape, value=16, command=MakeAWGwaves)
            ShapeAMenu.pack(side=TOP) # , anchor=W)
            #
            AWGAShapeLabel = Label(frame2, text="AWG A Wave Shape")
            AWGAShapeLabel.pack(side=TOP)
            #
            awg1ampl = Frame( frame2 )
            awg1ampl.pack(side=TOP)
            #awgampset = Button(awg1ampl, text="Min V", style="W5.TButton")#, command=SetAwgAmpl)
            #awgampset.pack(side=LEFT, anchor=W)
            AWGAAmplEntry = Entry(awg1ampl, width=6, cursor='double_arrow')
            AWGAAmplEntry.bind("<Return>", UpdateAwgContRet)
            AWGAAmplEntry.bind('<MouseWheel>', onAWGAscroll)
            AWGAAmplEntry.bind("<Button-4>", onAWGAscroll)# with Linux OS
            AWGAAmplEntry.bind("<Button-5>", onAWGAscroll)
            AWGAAmplEntry.bind('<Key>', onTextKeyAWG)
            AWGAAmplEntry.pack(side=LEFT, anchor=W)
            AWGAAmplEntry.delete(0,"end")
            AWGAAmplEntry.insert(0, 0.2)
            amp1lab = Label(awg1ampl) #, text="Min Ch A")
            amp1lab.pack(side=LEFT, anchor=W)
            #
            awg1off = Frame( frame2 )
            awg1off.pack(side=TOP)
            #awgoffset = Button(awg1off, text="Max V", style="W5.TButton") # , command=SetAwgOffset)
            #awgoffset.pack(side=LEFT, anchor=W)
            AWGAOffsetEntry = Entry(awg1off, width=6, cursor='double_arrow')
            AWGAOffsetEntry.bind("<Return>", UpdateAwgContRet)
            AWGAOffsetEntry.bind('<MouseWheel>', onAWGAscroll)
            AWGAOffsetEntry.bind("<Button-4>", onAWGAscroll)# with Linux OS
            AWGAOffsetEntry.bind("<Button-5>", onAWGAscroll)
            AWGAOffsetEntry.bind('<Key>', onTextKeyAWG)
            AWGAOffsetEntry.pack(side=LEFT, anchor=W)
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0,3.0)
            off1lab = Label(awg1off) #, text="Max Ch A")
            off1lab.pack(side=LEFT, anchor=W)
            if AWG_Amp_Mode.get() == 0:
                amp1lab.config(text = "Low V" ) # change displayed value
                off1lab.config(text = "High V" ) # change displayed value
            else:
                amp1lab.config(text = "Amp (PK-PK)" )
                off1lab.config(text = "Offset" )
            # AWG Frequency sub frame
            awg1freq = Frame( frame2 )
            awg1freq.pack(side=TOP)
            #awgfreqset = Button(awg1freq, text="", style="W5.TButton") #, command=SetAwgFrequency)
            #awgfreqset.pack(side=LEFT, anchor=W)
            AWGAFreqEntry = Entry(awg1freq, width=7, cursor='double_arrow')
            AWGAFreqEntry.bind("<Return>", UpdateAwgContRet)
            AWGAFreqEntry.bind('<MouseWheel>', onAWGAscroll)
            AWGAFreqEntry.bind("<Button-4>", onAWGAscroll)# with Linux OS
            AWGAFreqEntry.bind("<Button-5>", onAWGAscroll)
            AWGAFreqEntry.bind('<Key>', onTextKeyAWG)
            AWGAFreqEntry.pack(side=LEFT, anchor=W)
            AWGAFreqEntry.delete(0,"end")
            AWGAFreqEntry.insert(0,1000.0)
            freq1lab = Label(awg1freq, text="Freq")
            freq1lab.pack(side=LEFT, anchor=W)
            #
##            awg1width = Frame( frame2 )
##            awg1width.pack(side=TOP)
##            awgawd = Button(awg1width, text="Width", style="W8.TButton") #, command=SetAwgWidth)
##            awgawd.pack(side=LEFT, anchor=W)
##            AWGAWidthEntry = Entry(awg1width, width=6, cursor='double_arrow')
##            AWGAWidthEntry.bind("<Return>", UpdateAwgContRet)
##            AWGAWidthEntry.bind('<MouseWheel>', onAWGAscroll)
##            AWGAWidthEntry.bind("<Button-4>", onAWGAscroll)# with Linux OS
##            AWGAWidthEntry.bind("<Button-5>", onAWGAscroll)
##            AWGAWidthEntry.bind('<Key>', onTextKeyAWG)
##            AWGAWidthEntry.pack(side=LEFT, anchor=W)
##            AWGAWidthEntry.delete(0,"end")
##            AWGAWidthEntry.insert(0,"0.5m")
##            widthalab = Label(awg1width, text="Sec")
##            widthalab.pack(side=LEFT, anchor=W)
            # AWG duty cycle frame
            awg1dc = Frame( frame2 )
            awg1dc.pack(side=TOP)
            awgadc = Button(awg1dc, text="Duty Cycle", style="W8.TButton") #, command=SetAwgDutyCycle)
            awgadc.pack(side=LEFT, anchor=W)
            AWGADutyCycleEntry = Entry(awg1dc, width=6, cursor='double_arrow')
            AWGADutyCycleEntry.bind("<Return>", UpdateAwgContRet)
            AWGADutyCycleEntry.bind('<MouseWheel>', onAWGAscroll)
            AWGADutyCycleEntry.bind("<Button-4>", onAWGAscroll)# with Linux OS
            AWGADutyCycleEntry.bind("<Button-5>", onAWGAscroll)
            AWGADutyCycleEntry.bind('<Key>', onTextKeyAWG)
            AWGADutyCycleEntry.pack(side=LEFT, anchor=W)
            AWGADutyCycleEntry.delete(0,"end")
            AWGADutyCycleEntry.insert(0,50)
            duty1lab = Label(awg1dc, text="Percent")
            duty1lab.pack(side=LEFT, anchor=W)
            #
            AWGALength = Label(frame2, text="Length")
            AWGALength.pack(side=TOP)
            #
            try:
                awgsync = Checkbutton(frame2, text="Sync AWG", variable=AWGSync, command=BAWGSync)
                awgsync.pack(side=TOP)
            except:
                pass
        #
        if EnableAWGNoise == 1:
            awgaNoise = Frame( frame2 )
            awgaNoise.pack(side=TOP)
            AwgANoiseLb = Label(awgaNoise, text="Noise")
            AwgANoiseLb.pack(side=LEFT)
            AwgANoiseBt = Button(awgaNoise, text="OFF", style="Stop.TButton", width=4, command=AWGANoiseToggle)
            AwgANoiseBt.pack(side=LEFT)
        #
        if AWGChannels >= 2:
            freqlock = Checkbutton(frame2, text="Lock Freq", variable=LockFreq) # , command=)
            freqlock.pack(side=TOP)
        # now AWG B controls
            awgbOnOff = Frame( frame3 )
            awgbOnOff.pack(side=TOP)
            AwgbOnOffLb = Label(awgbOnOff, text="AWG B Output ")
            AwgbOnOffLb.pack(side=LEFT)
            AwgBOnOffBt = Button(awgbOnOff, text="OFF", style="Stop.TButton", width=4, command=AWGBOutToggle)
            AwgBOnOffBt.pack(side=LEFT)
    #
            awg2eb = Frame( frame3 )
            awg2eb.pack(side=TOP)
            ShapeBMenu = Menubutton(awg2eb, text="Shape", style="W6.TButton")
            ShapeBMenu.menu = Menu(ShapeBMenu, tearoff = 0 )
            ShapeBMenu["menu"] = ShapeBMenu.menu
            ShapeBMenu.menu.add_command(label="-Basic-", foreground="blue", command=donothing)
            ShapeBMenu.menu.add_radiobutton(label="DC", variable=AWGBShape, value=0, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString1, variable=AWGBShape, value=1, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString2, variable=AWGBShape, value=2, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString3, variable=AWGBShape, value=3, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString4, variable=AWGBShape, value=4, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString5, variable=AWGBShape, value=5, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString6, variable=AWGBShape, value=6, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString7, variable=AWGBShape, value=7, command=MakeAWGwaves)
            ShapeBMenu.menu.add_radiobutton(label=AwgString8, variable=AWGBShape, value=8, command=MakeAWGwaves)
            if AWGShowAdvanced.get() > 0:
                ShapeBMenu.menu.add_command(label="-Advanced-", foreground="blue", command=donothing)
                ShapeBMenu.menu.add_radiobutton(label=AwgString9, variable=AWGBShape, value=9, command=MakeAWGwaves)
                ShapeBMenu.menu.add_radiobutton(label=AwgString10, variable=AWGBShape, value=10, command=MakeAWGwaves)
                ShapeBMenu.menu.add_radiobutton(label=AwgString11, variable=AWGBShape, value=11, command=MakeAWGwaves)
                ShapeBMenu.menu.add_radiobutton(label=AwgString12, variable=AWGBShape, value=12, command=MakeAWGwaves)
                ShapeBMenu.menu.add_radiobutton(label=AwgString13, variable=AWGBShape, value=13, command=MakeAWGwaves)
                ShapeBMenu.menu.add_radiobutton(label=AwgString14, variable=AWGBShape, value=14, command=MakeAWGwaves)
                ShapeBMenu.menu.add_radiobutton(label=AwgString15, variable=AWGBShape, value=15, command=MakeAWGwaves)
                ShapeBMenu.menu.add_radiobutton(label=AwgString16, variable=AWGBShape, value=16, command=MakeAWGwaves)
            ShapeBMenu.pack(side=TOP) # , anchor=W)
            #
            AWGBShapeLabel = Label(frame3, text="AWG B Wave Shape")
            AWGBShapeLabel.pack(side=TOP)
            #
            awg2ampl = Frame( frame3 )
            awg2ampl.pack(side=TOP)
            #AWGBmpset = Button(awg2ampl, text="Min V", style="W5.TButton")#, command=SetAWGBmpl)
            #awgampset.pack(side=LEFT, anchor=W)
            AWGBAmplEntry = Entry(awg2ampl, width=6, cursor='double_arrow')
            AWGBAmplEntry.bind("<Return>", UpdateAwgContRet)
            AWGBAmplEntry.bind('<MouseWheel>', onAWGBscroll)
            AWGBAmplEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
            AWGBAmplEntry.bind("<Button-5>", onAWGBscroll)
            AWGBAmplEntry.bind('<Key>', onTextKeyAWG)
            AWGBAmplEntry.pack(side=LEFT, anchor=W)
            AWGBAmplEntry.delete(0,"end")
            AWGBAmplEntry.insert(0, 0.2)
            amp2lab = Label(awg2ampl) #, text="Min Ch A")
            amp2lab.pack(side=LEFT, anchor=W)
            #
            awg2off = Frame( frame3 )
            awg2off.pack(side=TOP)
            #awgoffset = Button(awg2off, text="Max V", style="W5.TButton") # , command=SetAwgOffset)
            #awgoffset.pack(side=LEFT, anchor=W)
            AWGBOffsetEntry = Entry(awg2off, width=6, cursor='double_arrow')
            AWGBOffsetEntry.bind("<Return>", UpdateAwgContRet)
            AWGBOffsetEntry.bind('<MouseWheel>', onAWGBscroll)
            AWGBOffsetEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
            AWGBOffsetEntry.bind("<Button-5>", onAWGBscroll)
            AWGBOffsetEntry.bind('<Key>', onTextKeyAWG)
            AWGBOffsetEntry.pack(side=LEFT, anchor=W)
            AWGBOffsetEntry.delete(0,"end")
            AWGBOffsetEntry.insert(0, 3.0)
            off2lab = Label(awg2off) #, text="Max Ch A")
            off2lab.pack(side=LEFT, anchor=W)
            if AWG_Amp_Mode.get() == 0:
                amp2lab.config(text = "Low V" ) # change displayed value
                off2lab.config(text = "High V" ) # change displayed value
            else:
                amp2lab.config(text = "Amp (PK-PK)" )
                off2lab.config(text = "Offset" )
            # AWG Frequency sub frame
            awg2freq = Frame( frame3 )
            awg2freq.pack(side=TOP)
            #awgfreqset = Button(awg2freq, text="", style="W5.TButton") #, command=SetAwgFrequency)
            #awgfreqset.pack(side=LEFT, anchor=W)
            AWGBFreqEntry = Entry(awg2freq, width=7, cursor='double_arrow')
            AWGBFreqEntry.bind("<Return>", UpdateAwgContRet)
            AWGBFreqEntry.bind('<MouseWheel>', onAWGBscroll)
            AWGBFreqEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
            AWGBFreqEntry.bind("<Button-5>", onAWGBscroll)
            AWGBFreqEntry.bind('<Key>', onTextKeyAWG)
            AWGBFreqEntry.pack(side=LEFT, anchor=W)
            AWGBFreqEntry.delete(0,"end")
            AWGBFreqEntry.insert(0,1000.0)
            freq2lab = Label(awg2freq, text="Freq")
            freq2lab.pack(side=LEFT, anchor=W)
            #
            # AWG Phase or delay select sub frame
            # AWG Phase sub frame
            awg2phase = Frame( frame3 )
            awg2phase.pack(side=TOP)
            awgbph = Button(awg2phase, text="Phase", style="W5.TButton", command=ToggleAWGBPhaseDelay)
            awgbph.pack(side=LEFT, anchor=W)
            AWGBPhaseEntry = Entry(awg2phase, width=4, cursor='double_arrow')
            AWGBPhaseEntry.bind("<Return>", UpdateAwgContRet)
            AWGBPhaseEntry.bind('<MouseWheel>', onAWGBscroll)
            AWGBPhaseEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
            AWGBPhaseEntry.bind("<Button-5>", onAWGBscroll)
            AWGBPhaseEntry.bind('<Key>', onTextKeyAWG)
            AWGBPhaseEntry.pack(side=LEFT, anchor=W)
            AWGBPhaseEntry.delete(0,"end")
            AWGBPhaseEntry.insert(0,0)
            phaseblab = Label(awg2phase, text="Deg")
            phaseblab.pack(side=LEFT, anchor=W)
##            awg2width = Frame( frame3 )
##            awg2width.pack(side=TOP)
##            AWGBwd = Button(awg2width, text="Width", style="W8.TButton") #, command=SetAwgWidth)
##            AWGBwd.pack(side=LEFT, anchor=W)
##            AWGBWidthEntry = Entry(awg2width, width=6, cursor='double_arrow')
##            AWGBWidthEntry.bind("<Return>", UpdateAwgContRet)
##            AWGBWidthEntry.bind('<MouseWheel>', onAWGBscroll)
##            AWGBWidthEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
##            AWGBWidthEntry.bind("<Button-5>", onAWGBscroll)
##            AWGBWidthEntry.bind('<Key>', onTextKeyAWG)
##            AWGBWidthEntry.pack(side=LEFT, anchor=W)
##            AWGBWidthEntry.delete(0,"end")
##            AWGBWidthEntry.insert(0,"0.5m")
##            widthblab = Label(awg2width, text="Sec")
##            widthblab.pack(side=LEFT, anchor=W)
            # AWG duty cycle frame
            awg2dc = Frame( frame3 )
            awg2dc.pack(side=TOP)
            AWGBdc = Button(awg2dc, text="Duty Cycle", style="W8.TButton") #, command=SetAwgDutyCycle)
            AWGBdc.pack(side=LEFT, anchor=W)
            AWGBDutyCycleEntry = Entry(awg2dc, width=6, cursor='double_arrow')
            AWGBDutyCycleEntry.bind("<Return>", UpdateAwgContRet)
            AWGBDutyCycleEntry.bind('<MouseWheel>', onAWGBscroll)
            AWGBDutyCycleEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
            AWGBDutyCycleEntry.bind("<Button-5>", onAWGBscroll)
            AWGBDutyCycleEntry.bind('<Key>', onTextKeyAWG)
            AWGBDutyCycleEntry.pack(side=LEFT, anchor=W)
            AWGBDutyCycleEntry.delete(0,"end")
            AWGBDutyCycleEntry.insert(0,50)
            duty2lab = Label(awg2dc, text="Percent")
            duty2lab.pack(side=LEFT, anchor=W)
            #
            AWGBLength = Label(frame3, text="Length")
            AWGBLength.pack(side=TOP)
            # Shift relative phase when channels are same frequency?
##            awg2shift = Frame( frame3 )
##            awg2shift.pack(side=TOP)
##            left10 = Button(awg2shift, style='Left2.TButton', text='-10', command=Left10RelPhase)
##            left10.pack(side=LEFT, anchor=W)
##            right10 = Button(awg2shift, style='Right2.TButton', text='10', command=Right10RelPhase)
##            right10.pack(side=LEFT, anchor=W)
##            awg2phase = Frame( frame3 )
##            awg2phase.pack(side=TOP)
##            AWGRelPh = Button(awg2phase, text="Rel Phase", style="W8.TButton", command=SetAwgRelPhase)
##            AWGRelPh.pack(side=LEFT, anchor=W)
##            AWGRelPhaseEntry = Entry(awg2phase, width=6, cursor='double_arrow')
            # AWGRelPhaseEntry.bind("<Return>", UpdateAwContRet)
##            AWGRelPhaseEntry.bind('<MouseWheel>', onTextScroll)
##            AWGRelPhaseEntry.bind("<Button-4>", onTextScroll)# with Linux OS
##            AWGRelPhaseEntry.bind("<Button-5>", onTextScroll)
            # AWGRelPhaseEntry.bind('<Key>', onTextKeyAWG)
##            AWGRelPhaseEntry.pack(side=LEFT, anchor=W)
##            AWGRelPhaseEntry.delete(0,"end")
##            AWGRelPhaseEntry.insert(0,"0")
##            widthblab = Label(awg2width, text="Sec")
            #
            bcompa = Checkbutton(frame3, text="B = Comp A", variable=BisCompA, command=MakeAWGwaves)#SetBCompA)
            bcompa.pack(side=TOP)
        #
        #
        dismissbutton = Button(frame2, text="Minimize", style="W8.TButton", command=DestroyAWGScreen)
        dismissbutton.pack(side=TOP)
        # Now Aux DAC entry:
        #
        if AWGChannels >= 3:
            auxval = Frame( frame4 )
            auxval.pack(side=LEFT)
            AUXDACLabel = Label(auxval, text="AUX DAC Voltage")
            AUXDACLabel.pack(side=TOP)
            AuxDACEntry = Entry(auxval, width=6, cursor='double_arrow')
            AuxDACEntry.bind("<Return>", UpdateAuxDAC)
            AuxDACEntry.bind('<MouseWheel>', onAuxScroll)
            AuxDACEntry.bind("<Button-4>", onAuxScroll)# with Linux OS
            AuxDACEntry.bind("<Button-5>", onAuxScroll)
            AuxDACEntry.bind('<Key>', onTextKeyAux)
            AuxDACEntry.pack(side=TOP, anchor=W)
            AuxDACEntry.delete(0,"end")
            AuxDACEntry.insert(0,2.5)
            auxlab = Label(auxval, text="Aux DAC V")
            auxlab.pack(side=TOP, anchor=W)
        
        if ShowBallonHelp > 0:
            # BuildAWGAPhase_tip = CreateToolTip(awgaph, 'Toggle between degrees and time')
            try:
                BuildShapeAMenu_tip = CreateToolTip(ShapeAMenu, 'Set channel waveform shape')
            except:
                pass
        awgwindow.deiconify()
#
def ToggleAWGBPhaseDelay():
    global AWGBPhaseDelay, phaseblab, awgbph, awgbdel

    if AWGBPhaseDelay.get() == 1:
        AWGBPhaseDelay.set(0)
        awgbph.configure(text="Phase")
        phaseblab.configure(text="Deg")
    elif AWGBPhaseDelay.get() == 0:
        AWGBPhaseDelay.set(1)
        awgbph.configure(text="Delay")
        phaseblab.configure(text="mSec")
#
def AlignPhase():
    global AWGRelPhaseEntry

    PhaseOffset = Sine_Phase()
    SetAwgRelPhase()
#
def onAuxScroll(event):

    onTextScroll(event)
    UpdateAuxDAC()
#
def onTextKeyAux(event):

    UpdateAuxDAC()
#
def onPWMFScroll(event):

    onTextScroll(event)
    UpdatePWM()
#
def onPWMWScroll(event):

    onTextScroll(event)
    UpdatePWM()
#
#
def DestroyAWGScreen():
    global awgwindow, AWGScreenStatus
    
    # AWGScreenStatus.set(0)
    awgwindow.iconify()
#
def SyncImage():
    global MuxSync, hipulseimg, lowpulseimg, SyncButton

    if MuxSync.get() == 0:
        SyncButton.config(image=hipulseimg)
    else:
        SyncButton.config(image=lowpulseimg)
#
def BodeCaresize(event):
    global Bodeca, GRWBP, XOLBP, GRHBP, Y0TBP, CANVASwidthBP, CANVASheightBP, FontSize
    
    CANVASwidthBP = event.width - 4
    CANVASheightBP = event.height - 4 
    GRWBP = CANVASwidthBP - (2 * X0LBP) # new grid width
    GRHBP = CANVASheightBP - int(10 * FontSize)     # new grid height
    UpdateBodeAll()
#
def BSweepSync(): # Place holder function to pulse digital output during frequency sweeps
    global FSweepSync

    if FSweepSync.get() == 0:
        donothing()
    elif FSweepSync.get() == 1:
        donothing()
    elif FSweepSync.get() == 2:
        donothing()
#
def BStepSync(): # Place holder function to pulse digital output during frequency sweeps
    global FStepSync

    if FStepSync.get() == 0:
        donothing()
    elif FStepSync.get() == 1:
        donothing()
    elif FStepSync.get() == 2:
        donothing()
#
def BDSweepFromFile():
    global BDSweepFile, FileSweepFreq, FileSweepAmpl

    if BDSweepFile.get() > 0:
       # Read values from CVS file
        filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent = bodewindow)
        try:
            CSVFile = open(filename)
            csv_f = csv.reader(CSVFile)
            FileSweepFreq = []
            FileSweepAmpl = []
            for row in csv_f:
                try:
                    FileSweepFreq.append(float(row[0]))
                    FileSweepAmpl.append(float(row[1]))
                except:
                    print( 'skipping non-numeric row')
            FileSweepFreq = numpy.array(FileSweepFreq)
            FileSweepAmpl = numpy.array(FileSweepAmpl)
            MaxAmpl = numpy.amax(FileSweepAmpl)
            NormAmpl = MaxAmpl
            s = askstring("Normalize Max Amplitude", "Max Amplitude = " + str(MaxAmpl) + "\n\n Enter New Max value:\n in dB", parent = bodewindow)
            if (s == None):         # If Cancel pressed, then None
                return()
            try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
                v = int(s)
            except:
                s = "error"

            if s != "error":
                NormAmpl = MaxAmpl - v
            else:
                NormAmpl = MaxAmpl
            FileSweepAmpl = FileSweepAmpl - NormAmpl # normalize max amplitude to requested dBV
            CSVFile.close()
            StopBodeEntry.delete(0,"end")
            StopBodeEntry.insert(0,FileSweepFreq[len(FileSweepFreq)-1])
            StartBodeEntry.delete(0,"end")
            StartBodeEntry.insert(0,FileSweepFreq[0])
            SweepStepBodeEntry.delete(0,"end")
            SweepStepBodeEntry.insert(0,len(FileSweepFreq))
        except:
            showwarning("WARNING","No such file found or wrong format!", parent = bodewindow)
#
# ========== Make Bode Plot Window =============
def MakeBodeWindow():
    global logo, SmoothCurvesBP, CutDC, bodewindow, SWRev
    global CANVASwidthBP, CANVASheightBP, FFTwindow, CutDC, AWGAShape
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMarkerBP, BodeDisp, RelPhaseCenter
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP, ShowMathBP, ShowRMathBP, PhCenBodeEntry
    global BPSweepMode, BPSweepCont, Bodeca, BodeScreenStatus, RevDate, SweepStepBodeEntry
    global HScaleBP, StopBodeEntry, StartBodeEntry, ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global GRWBP, GRHBP, X0LBP, FStepSync, FSweepSync, BDSweepFile, MinigenScreenStatus
    global Show_Rseries, Show_Xseries, Show_Magnitude, Show_Angle, ImpedanceCenter, ImCenBodeEntry
    global Show_RseriesRef, Show_XseriesRef, Show_MagnitudeRef, Show_AngleRef
    global FrameRelief, BorderSize, LocalLanguage
    global sbode_tip, rbode_tip, bd3_tip, bd4_tip, bd5_tip, bd6_tip, bd7_tip, bd8_tip, bodismiss1button_tip
    global bstopfreqlab, bstartfreqlab, ImCenlab, BPhCenlab
    
    if BodeScreenStatus.get() == 0:
        BodeScreenStatus.set(1)
        BodeDisp.set(1)
        BodeCheckBox()
        CANVASwidthBP = GRWBP + 2 * X0LBP    # The Bode canvas width
        CANVASheightBP = GRHBP + int(10 * FontSize) # The bode canvas height
        CutDC.set(1) # set to remove DC
        AWGAShape.set(1) # Set Shape to Sine
        bodewindow = Toplevel()
        bodewindow.title("Bode Plotter " + SWRev + RevDate)
        bodewindow.protocol("WM_DELETE_WINDOW", DestroyBodeScreen)
        frame2bp = Frame(bodewindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2bp.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2b = Frame(bodewindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2b.pack(side=TOP, expand=YES, fill=BOTH)

        Bodeca = Canvas(frame2b, width=CANVASwidthBP, height=CANVASheightBP, background=COLORcanvas, cursor='cross')
        Bodeca.bind('<Configure>', BodeCaresize)
        Bodeca.bind('<1>', onCanvasBodeLeftClick)
        Bodeca.bind('<3>', onCanvasBodeRightClick)
        Bodeca.bind("<Up>", onCanvasUpArrow)
        Bodeca.bind("<Down>", onCanvasDownArrow)
        Bodeca.bind("<Left>", onCanvasLeftArrow)
        Bodeca.bind("<Right>", onCanvasRightArrow)
        Bodeca.bind("<space>", onCanvasSpaceBar)
        Bodeca.bind("1", onCanvasBdOne)
        Bodeca.bind("2", onCanvasBdTwo)
        Bodeca.bind("3", onCanvasBdThree)
        Bodeca.bind("4", onCanvasBdFour)
        Bodeca.bind("5", onCanvasBdFive)
        Bodeca.bind("6", onCanvasBdSix)
        Bodeca.bind("7", onCanvasBdSeven)
        Bodeca.bind("8", onCanvasBdEight)
        Bodeca.bind("9", onCanvasBdNine)
        Bodeca.bind("0", onCanvasBdZero)
        Bodeca.bind("f", onCanvasShowBPcur)
        Bodeca.bind("d", onCanvasShowBdBcur)
        Bodeca.bind("h", onCanvasShowPdBcur)
        Bodeca.bind("s", onCanvasBdSnap)
        Bodeca.pack(side=TOP, expand=YES, fill=BOTH)

        # right side drop down menu buttons
        dropmenu = Frame( frame2bp )
        dropmenu.pack(side=TOP)
        # File menu
        BodeFilemenu = Menubutton(dropmenu, text="File", style="W5.TButton")
        BodeFilemenu.menu = Menu(BodeFilemenu, tearoff = 0 )
        BodeFilemenu["menu"] = BodeFilemenu.menu
        BodeFilemenu.menu.add_command(label="Save Config", command=BSaveConfigBP)
        BodeFilemenu.menu.add_command(label="Load Config", command=BLoadConfigBP)
        BodeFilemenu.menu.add_command(label="Run Script", command=RunScript)
        BodeFilemenu.menu.add_command(label="Save Screen", command=BSaveScreenBP)
        BodeFilemenu.menu.add_command(label="Save Data", command=BCSVfile)
        BodeFilemenu.pack(side=LEFT, anchor=W)
        #
        BodeOptionmenu = Menubutton(dropmenu, text="Options", style="W8.TButton")
        BodeOptionmenu.menu = Menu(BodeOptionmenu, tearoff = 0 )
        BodeOptionmenu["menu"]  = BodeOptionmenu.menu
        BodeOptionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
        BodeOptionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurvesBP)
        BodeOptionmenu.menu.add_checkbutton(label='Cut-DC', variable=CutDC)
        BodeOptionmenu.menu.add_command(label="Store trace (s)", command=BSTOREtraceBP)
        BodeOptionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
        BodeOptionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
        BodeOptionmenu.menu.add_command(label="-Step Sync Pulse-", command=donothing)
        BodeOptionmenu.menu.add_radiobutton(label='None', variable=FStepSync, value=0, command=BStepSync)
        BodeOptionmenu.menu.add_radiobutton(label='Rising', variable=FStepSync, value=1, command=BStepSync)
        BodeOptionmenu.menu.add_radiobutton(label='Falling', variable=FStepSync, value=2, command=BStepSync)
        BodeOptionmenu.menu.add_command(label="-Sweep Sync Pulse-", command=donothing)
        BodeOptionmenu.menu.add_radiobutton(label='None', variable=FSweepSync, value=0, command=BSweepSync)
        BodeOptionmenu.menu.add_radiobutton(label='Rising', variable=FSweepSync, value=1, command=BSweepSync)
        BodeOptionmenu.menu.add_radiobutton(label='Falling', variable=FSweepSync, value=2, command=BSweepSync)
        BodeOptionmenu.pack(side=LEFT, anchor=W)
        #
        RUNframe = Frame( frame2bp )
        RUNframe.pack(side=TOP)
        rbode = Button(RUNframe, text="Run", style="Run.TButton", command=BStartBP)
        rbode.pack(side=LEFT)
        sbode = Button(RUNframe, text="Stop", style="Stop.TButton", command=BStopBP)
        sbode.pack(side=LEFT)
        #
        BodeFFTwindmenu = Menubutton(frame2bp, text="FFTwindow", style="W11.TButton")
        BodeFFTwindmenu.menu = Menu(BodeFFTwindmenu, tearoff = 0 )
        BodeFFTwindmenu["menu"]  = BodeFFTwindmenu.menu
        BodeFFTwindmenu.menu.add_radiobutton(label='Rectangular window (B=1)', variable=FFTwindow, value=0)
        BodeFFTwindmenu.menu.add_radiobutton(label='Cosine window (B=1.24)', variable=FFTwindow, value=1)
        BodeFFTwindmenu.menu.add_radiobutton(label='Triangular window (B=1.33)', variable=FFTwindow, value=2)
        BodeFFTwindmenu.menu.add_radiobutton(label='Hann window (B=1.5)', variable=FFTwindow, value=3)
        BodeFFTwindmenu.menu.add_radiobutton(label='Blackman window (B=1.73)', variable=FFTwindow, value=4)
        BodeFFTwindmenu.menu.add_radiobutton(label='Nuttall window (B=2.02)', variable=FFTwindow, value=5)
        BodeFFTwindmenu.menu.add_radiobutton(label='Flat top window (B=3.77)', variable=FFTwindow, value=6)
        BodeFFTwindmenu.menu.add_radiobutton(label='User Defined window', variable=FFTwindow, value=7)
        BodeFFTwindmenu.menu.add_command(label="Enter User function", command=BUserFFTwindow)
        BodeFFTwindmenu.menu.add_radiobutton(label='FFT Window from file', variable=FFTwindow, value=8, command=BFileFFTwindow)
        BodeFFTwindmenu.pack(side=TOP)
        #
        tracemenu = Frame( frame2bp )
        tracemenu.pack(side=TOP)
        # Curves menu
        # Show channels menu
        BodeShowmenu = Menubutton(tracemenu, text="Curves", style="W7.TButton")
        BodeShowmenu.menu = Menu(BodeShowmenu, tearoff = 0 )
        BodeShowmenu["menu"] = BodeShowmenu.menu
        BodeShowmenu.menu.add_command(label="-Show-", command=donothing)
        BodeShowmenu.menu.add_command(label="All", command=BShowCurvesAllBP)
        BodeShowmenu.menu.add_command(label="None", command=BShowCurvesNoneBP)
        BodeShowmenu.menu.add_checkbutton(label='CA-dBV   (1)', variable=ShowCA_VdB, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='CB-dBV   (2)', variable=ShowCB_VdB, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Phase A-B (3)', variable=ShowCA_P, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Phase B-A (4)', variable=ShowCB_P, command=UpdateBodeAll)
        BodeShowmenu.menu.add_command(label="-Math-", command=donothing)
        BodeShowmenu.menu.add_radiobutton(label='None (0)', variable=ShowMathBP, value=0, command=UpdateBodeAll)
        BodeShowmenu.menu.add_radiobutton(label='CA-dB - CB-dB (9)', variable=ShowMathBP, value=1, command=UpdateBodeAll)
        BodeShowmenu.menu.add_radiobutton(label='CB-dB - CA-dB (8)', variable=ShowMathBP, value=2, command=UpdateBodeAll)
        BodeShowmenu.menu.add_command(label="-Impedance-", command=donothing)
        BodeShowmenu.menu.add_checkbutton(label='Series R', variable=Show_Rseries, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Series X', variable=Show_Xseries, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Series Mag', variable= Show_Magnitude, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Series Ang', variable=Show_Angle, command=UpdateBodeAll)
        BodeShowmenu.menu.add_separator() 
        BodeShowmenu.menu.add_checkbutton(label='RA-dBV (6)', variable=ShowCA_RdB, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='RB-dBV (7)', variable=ShowCB_RdB, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='RPhase A-B', variable=ShowCA_RP, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='RPhase B-A', variable=ShowCB_RP, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Math', variable=ShowRMathBP, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Ref Series R', variable=Show_RseriesRef, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Ref Series X', variable=Show_XseriesRef, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Ref Series Mag', variable=Show_MagnitudeRef, command=UpdateBodeAll)
        BodeShowmenu.menu.add_checkbutton(label='Ref Series Ang', variable=Show_AngleRef, command=UpdateBodeAll)
        BodeShowmenu.pack(side=LEFT, anchor=W)
        #
        BodeMarkmenu = Menubutton(tracemenu, text="Cursors", style="W7.TButton")
        BodeMarkmenu.menu = Menu(BodeMarkmenu, tearoff = 0 )
        BodeMarkmenu["menu"] = BodeMarkmenu.menu
        BodeMarkmenu.menu.add_command(label="-Cursors&Markers-", command=donothing)
        BodeMarkmenu.menu.add_checkbutton(label='Marker   (5)', variable=ShowMarkerBP, command=UpdateBodeAll)
        BodeMarkmenu.menu.add_checkbutton(label='Freq Cursor', variable=ShowBPCur)
        BodeMarkmenu.menu.add_checkbutton(label='dB Cursor', variable=ShowBdBCur)
        BodeMarkmenu.menu.add_radiobutton(label='Cursor Off', variable=ShowBdBCur, value=0)
        BodeMarkmenu.menu.add_radiobutton(label='dB Cursor (d)', variable=ShowBdBCur, value=1)
        BodeMarkmenu.menu.add_radiobutton(label='Phase Cursor (h)', variable=ShowBdBCur, value=2)
        BodeMarkmenu.menu.add_checkbutton(label='Freq Cursor (f)', variable=ShowBPCur)
        BodeMarkmenu.pack(side=LEFT, anchor=W)
        #
        # Horz Scale        
        HzScale = Frame( frame2bp )
        HzScale.pack(side=TOP)
        brb1 = Radiobutton(HzScale, text="Lin F", variable=HScaleBP, value=0, command=UpdateBodeTrace )
        brb1.pack(side=LEFT)
        brb2 = Radiobutton(HzScale, text="Log F", variable=HScaleBP, value=1, command=UpdateBodeTrace )
        brb2.pack(side=LEFT)
        
        DBrange = Frame( frame2bp )
        DBrange.pack(side=TOP)
        bd3 = Button(DBrange, text="+dB/div", style="W8.TButton", command=BDBdiv2BP)
        bd3.pack(side=LEFT)
        bd4 = Button(DBrange, text="-dB/div", style="W8.TButton", command=BDBdiv1BP)
        bd4.pack(side=LEFT)

        LVBrange = Frame( frame2bp )
        LVBrange.pack(side=TOP)
        bd5 = Button(LVBrange, text="LVL+10", style="W8.TButton", command=Blevel4BP)
        bd5.pack(side=LEFT)
        bd6 = Button(LVBrange, text="LVL-10", style="W8.TButton", command=Blevel3BP)
        bd6.pack(side=LEFT)

        LVSrange = Frame( frame2bp )
        LVSrange.pack(side=TOP)
        bd7 = Button(LVSrange, text="LVL+1", style="W8.TButton", command=Blevel2BP)
        bd7.pack(side=LEFT)
        bd8 = Button(LVSrange, text="LVL-1", style="W8.TButton", command=Blevel1BP)
        bd8.pack(side=LEFT)

        PhaseCenter = Frame( frame2bp )
        PhaseCenter.pack(side=TOP)
        BPhCenlab = Label(PhaseCenter, text="Center Phase on")
        BPhCenlab.pack(side=LEFT)
        PhCenBodeEntry = Entry(PhaseCenter, width=5, cursor='double_arrow')
        PhCenBodeEntry.bind('<Return>', onTextKey)
        PhCenBodeEntry.bind('<MouseWheel>', onTextScroll)
        PhCenBodeEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        PhCenBodeEntry.bind("<Button-5>", onTextScroll)
        PhCenBodeEntry.bind('<Key>', onTextKey)
        PhCenBodeEntry.pack(side=LEFT)
        PhCenBodeEntry.delete(0,"end")
        PhCenBodeEntry.insert(0,RelPhaseCenter.get())
        #
        ImpedCenter = Frame( frame2bp )
        ImpedCenter.pack(side=TOP)
        ImCenlab = Label(ImpedCenter, text="Center Imped on")
        ImCenlab.pack(side=LEFT)
        ImCenBodeEntry = Entry(ImpedCenter, width=5, cursor='double_arrow')
        ImCenBodeEntry.bind('<Return>', onTextKey)
        ImCenBodeEntry.bind('<MouseWheel>', onTextScroll)
        ImCenBodeEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        ImCenBodeEntry.bind("<Button-5>", onTextScroll)
        ImCenBodeEntry.bind('<Key>', onTextKey)
        ImCenBodeEntry.pack(side=LEFT)
        ImCenBodeEntry.delete(0,"end")
        ImCenBodeEntry.insert(0,ImpedanceCenter.get())
        # sweep generator mode menu buttons
        FSweepmenu = Label(frame2bp, text="-Sweep Gen-", style="A10B.TLabel")
        FSweepmenu.pack(side=TOP)
        
        Frange1 = Frame( frame2bp )
        Frange1.pack(side=TOP)
        bstartfreqlab = Label(Frange1, text="Start Freq")
        bstartfreqlab.pack(side=LEFT)
        StartBodeEntry = Entry(Frange1, width=7, cursor='double_arrow')
        StartBodeEntry.bind('<Return>', onTextKey)
        StartBodeEntry.bind('<MouseWheel>', onTextScroll)
        StartBodeEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        StartBodeEntry.bind("<Button-5>", onTextScroll)
        StartBodeEntry.bind('<Key>', onTextKey)
        StartBodeEntry.pack(side=LEFT)
        StartBodeEntry.delete(0,"end")
        StartBodeEntry.insert(0,10)

        Frange2 = Frame( frame2bp )
        Frange2.pack(side=TOP)
        bstopfreqlab = Label(Frange2, text="Stop Freq")
        bstopfreqlab.pack(side=LEFT)
        StopBodeEntry = Entry(Frange2, width=7, cursor='double_arrow')
        StopBodeEntry.bind('<Return>', onTextKey)
        StopBodeEntry.bind('<MouseWheel>', onStopBodeScroll)
        StopBodeEntry.bind("<Button-4>", onStopBodeScroll)# with Linux OS
        StopBodeEntry.bind("<Button-5>", onStopBodeScroll)
        StopBodeEntry.bind('<Key>', onTextKey)
        StopBodeEntry.pack(side=LEFT)
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,10000)
        FSweepMode.set(1)
        #
        ffcb = Checkbutton(frame2bp, text='Sweep From File', variable=BDSweepFile, command=BDSweepFromFile)
        ffcb.pack(side=TOP)
        Frange3 = Frame( frame2bp )
        Frange3.pack(side=TOP)
        sweepsteplab = Label(Frange3, text="Sweep Steps")
        sweepsteplab.pack(side=LEFT)
        SweepStepBodeEntry = Entry(Frange3, width=5, cursor='double_arrow')
        SweepStepBodeEntry.bind('<Return>', onTextKey)
        SweepStepBodeEntry.bind('<MouseWheel>', onTextScroll)
        SweepStepBodeEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        SweepStepBodeEntry.bind("<Button-5>", onTextScroll)
        SweepStepBodeEntry.bind('<Key>', onTextKey)
        SweepStepBodeEntry.pack(side=LEFT)
        SweepStepBodeEntry.delete(0,"end")
        SweepStepBodeEntry.insert(0,100)
        
        sgrb5 = Radiobutton(frame2bp, text='Single', variable=FSweepCont, value=0)
        sgrb5.pack(side=TOP)
        sgrb6 = Radiobutton(frame2bp, text='Continuous', variable=FSweepCont, value=1)
        sgrb6.pack(side=TOP)
        Plotsframe = Frame( frame2bp )
        Plotsframe.pack(side=TOP)
        nyquistplotbutton = Button(Plotsframe, text="Polar Plot", style="W9.TButton", command=MakeNyquistPlot)
        nyquistplotbutton.pack(side=LEFT)
        nicholsplotbutton = Button(Plotsframe, text="Rect Plot", style="W8.TButton", command=MakeNicPlot)
        nicholsplotbutton.pack(side=LEFT)
        bodismiss1button = Button(frame2bp, text="Dismiss", style="W8.TButton", command=DestroyBodeScreen)
        bodismiss1button.pack(side=TOP)
        
        ADI2 = Label(frame2bp, image=logo, anchor= "sw", compound="top") #, height=49, width=116
        ADI2.pack(side=TOP)
        if ShowBallonHelp > 0:
            sbode_tip = CreateToolTip(sbode, 'Stop acquiring data')
            rbode_tip = CreateToolTip(rbode, 'Start acquiring data')
            bd3_tip = CreateToolTip(bd3, 'Increase number of dB/Div')
            bd4_tip = CreateToolTip(bd4, 'Decrease number of dB/Div')
            bd5_tip = CreateToolTip(bd5, 'Increase Ref Level by 10 dB')
            bd6_tip = CreateToolTip(bd6, 'Decrease Ref Level by 10 dB')
            bd7_tip = CreateToolTip(bd7, 'Increase Ref Level by 1 dB')
            bd8_tip = CreateToolTip(bd8, 'Decrease Ref Level by 1 dB')
            bodismiss1button_tip = CreateToolTip(bodismiss1button, 'Dismiss Bode Plot window')
            if LocalLanguage != "English":
                BLoadConfig(LocalLanguage) # load local language configuration
#
def DestroyBodeScreen():
    global bodewindow, BodeScreenStatus, ca, FSweepMode
    
    BodeScreenStatus.set(0)
    FSweepMode.set(0)
    BodeDisp.set(0)
    BodeCheckBox()
    bodewindow.destroy()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
def FreqCaresize(event):
    global Freqca, GRWF, XOLF, GRHF, Y0TF, CANVASwidthF, CANVASheightF, FontSize
    
    CANVASwidthF = event.width - 4
    CANVASheightF = event.height - 4
    GRWF = CANVASwidthF - 10 - (2 * X0LF) # new grid width
    GRHF = CANVASheightF - int(10 * FontSize)     # new grid height
    UpdateFreqAll()
#
# ================ Make spectrum sub window ==========================
def MakeSpectrumWindow():
    global logo, SmoothCurvesSA, CutDC, SingleShotSA, FFTwindow, freqwindow, SmoothCurvesSA
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMarker, FreqDisp
    global ShowRA_VdB, ShowRA_P, ShowRB_VdB, ShowRB_P, ShowMathSA, SWRev, SingleShotSA
    global ShowRMath, FSweepMode, FSweepCont, Freqca, SpectrumScreenStatus, RevDate, AWGShowAdvanced
    global HScale, StopFreqEntry, StartFreqEntry, ShowFCur, ShowdBCur, FCursor, dBCursor
    global CANVASwidthF, GRWF, X0LF, CANVASheightF, GRHF, FontSize, PhCenFreqEntry, RelPhaseCenter
    global FrameRelief, BorderSize, LocalLanguage, SAVScale, SAVPSD, SAvertmaxEntry, SAvertminEntry
    global sb_tip, rb_tip, bless_tip, bmore_tip, b3_tip, b4_tip, b5_tip, b6_tip, b7_tip, b8_tip, sadismiss1button_tip
    global SAMagdiv, SAVScale, SAvertmaxEntry, SAvertminEntry, SAVPSD
    
    if SpectrumScreenStatus.get() == 0:
        SpectrumScreenStatus.set(1)
        FreqDisp.set(1)
        FreqCheckBox()
        CANVASwidthF = GRWF + 10 + 2 * X0LF     # The spectrum canvas width
        CANVASheightF = GRHF + int(10 * FontSize) # 80 The spectrum canvas height
        freqwindow = Toplevel()
        freqwindow.title("Spectrum Analyzer " + SWRev + RevDate)
        freqwindow.protocol("WM_DELETE_WINDOW", DestroySpectrumScreen)
        frame2fr = Frame(freqwindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2fr.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2f = Frame(freqwindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2f.pack(side=TOP, expand=YES, fill=BOTH)

        Freqca = Canvas(frame2f, width=CANVASwidthF, height=CANVASheightF, background=COLORcanvas, cursor='cross')
        Freqca.bind('<Configure>', FreqCaresize)
        Freqca.bind('<1>', onCanvasFreqLeftClick)
        Freqca.bind('<3>', onCanvasFreqRightClick)
        Freqca.bind("<Up>", onCanvasUpArrow)
        Freqca.bind("<Down>", onCanvasDownArrow)
        Freqca.bind("<Left>", onCanvasLeftArrow)
        Freqca.bind("<Right>", onCanvasRightArrow)
        Freqca.bind("<space>", onCanvasSpaceBar)
        Freqca.bind("1", onCanvasSAOne)
        Freqca.bind("2", onCanvasSATwo)
        Freqca.bind("3", onCanvasSAThree)
        Freqca.bind("4", onCanvasSAFour)
        Freqca.bind("5", onCanvasSAFive)
        Freqca.bind("6", onCanvasSASix)
        Freqca.bind("7", onCanvasSASeven)
        Freqca.bind("8", onCanvasSAEight)
        Freqca.bind("9", onCanvasSANine)
        Freqca.bind("0", onCanvasSAZero)
        Freqca.bind("a", onCanvasSAAverage)
        Freqca.bind("n", onCanvasSANormal)
        Freqca.bind("p", onCanvasSAPeak)
        Freqca.bind("r", onCanvasSAReset)
        Freqca.bind("f", onCanvasShowFcur)
        Freqca.bind("d", onCanvasShowdBcur)
        Freqca.bind("h", onCanvasShowPcur)
        Freqca.bind("s", onCanvasSASnap)
        Freqca.pack(side=TOP, expand=YES, fill=BOTH)
        # right side drop down menu buttons
        dropmenu = Frame( frame2fr )
        dropmenu.pack(side=TOP)
        # File menu
        SAFilemenu = Menubutton(dropmenu, text="File", style="W5.TButton")
        SAFilemenu.menu = Menu(SAFilemenu, tearoff = 0 )
        SAFilemenu["menu"] = SAFilemenu.menu
        SAFilemenu.menu.add_command(label="Save Config", command=BSaveConfigSA)
        SAFilemenu.menu.add_command(label="Load Config", command=BLoadConfigSA)
        SAFilemenu.menu.add_command(label="Run Script", command=RunScript)
        SAFilemenu.menu.add_command(label="Save Screen", command=BSaveScreenSA)
        SAFilemenu.menu.add_command(label="Save Data", command=STOREcsvfile)
        SAFilemenu.pack(side=LEFT, anchor=W)
        #
        SAOptionmenu = Menubutton(dropmenu, text="Options", style="W8.TButton")
        SAOptionmenu.menu = Menu(SAOptionmenu, tearoff = 0 )
        SAOptionmenu["menu"]  = SAOptionmenu.menu
        SAOptionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
        SAOptionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurvesSA)
        SAOptionmenu.menu.add_checkbutton(label='Cut-DC', variable=CutDC)
        SAOptionmenu.menu.add_command(label="Store trace [s]", command=BSTOREtraceSA)
        SAOptionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
        SAOptionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
        SAOptionmenu.pack(side=LEFT, anchor=W)
        #
        RUNframe = Frame( frame2fr )
        RUNframe.pack(side=TOP)
        sarb = Button(RUNframe, text="Run", style="Run.TButton", command=BStartSA)
        sarb.pack(side=LEFT)
        sasb = Button(RUNframe, text="Stop", style="Stop.TButton", command=BStopSA)
        sasb.pack(side=LEFT)
        #
        Modeframe = Frame( frame2fr )
        Modeframe.pack(side=TOP)
        Modemenu = Menubutton(Modeframe, text="Mode", style="W5.TButton")
        Modemenu.menu = Menu(Modemenu, tearoff = 0 )
        Modemenu["menu"]  = Modemenu.menu
        Modemenu.menu.add_command(label="Normal mode [n]", command=BNormalmode)
        Modemenu.menu.add_command(label="Peak hold   [p]", command=BPeakholdmode)
        Modemenu.menu.add_command(label="Average     [a]", command=BAveragemode)
        Modemenu.menu.add_command(label="Reset Average [r]", command=BResetFreqAvg)
        Modemenu.menu.add_checkbutton(label='SingleShot', variable=SingleShotSA)
        Modemenu.pack(side=LEFT)
        #
        SAFFTwindmenu = Menubutton(Modeframe, text="FFTwindow", style="W11.TButton")
        SAFFTwindmenu.menu = Menu(SAFFTwindmenu, tearoff = 0 )
        SAFFTwindmenu["menu"]  = SAFFTwindmenu.menu
        SAFFTwindmenu.menu.add_radiobutton(label='Rectangular window (B=1)', variable=FFTwindow, value=0)
        SAFFTwindmenu.menu.add_radiobutton(label='Cosine window (B=1.24)', variable=FFTwindow, value=1)
        SAFFTwindmenu.menu.add_radiobutton(label='Triangular window (B=1.33)', variable=FFTwindow, value=2)
        SAFFTwindmenu.menu.add_radiobutton(label='Hann window (B=1.5)', variable=FFTwindow, value=3)
        SAFFTwindmenu.menu.add_radiobutton(label='Blackman window (B=1.73)', variable=FFTwindow, value=4)
        SAFFTwindmenu.menu.add_radiobutton(label='Nuttall window (B=2.02)', variable=FFTwindow, value=5)
        SAFFTwindmenu.menu.add_radiobutton(label='Flat top window (B=3.77)', variable=FFTwindow, value=6)
        SAFFTwindmenu.menu.add_radiobutton(label='User Defined window', variable=FFTwindow, value=7)
        SAFFTwindmenu.menu.add_command(label="Enter User function", command=BUserFFTwindow)
        SAFFTwindmenu.menu.add_radiobutton(label='FFT Window from file', variable=FFTwindow, value=8, command=BFileFFTwindow)
        SAFFTwindmenu.pack(side=LEFT)
        #
        # Show channels menu
        #
        MarkersMenu = Frame( frame2fr )
        MarkersMenu.pack(side=TOP)
        SAShowmenu = Menubutton(MarkersMenu, text="Curves", style="W7.TButton")
        SAShowmenu.menu = Menu(SAShowmenu, tearoff = 0 )
        SAShowmenu["menu"] = SAShowmenu.menu
        SAShowmenu.menu.add_command(label="-Show-", command=donothing)
        SAShowmenu.menu.add_command(label="All", command=BShowCurvesAllSA)
        SAShowmenu.menu.add_command(label="None", command=BShowCurvesNoneSA)
        SAShowmenu.menu.add_checkbutton(label='A-dBV   [1]', variable=ShowC1_VdB, command=UpdateFreqAll)
        SAShowmenu.menu.add_checkbutton(label='B-dBV   [2]', variable=ShowC2_VdB, command=UpdateFreqAll)
        SAShowmenu.menu.add_checkbutton(label='Phase A-B [3]', variable=ShowC1_P, command=UpdateFreqAll)
        SAShowmenu.menu.add_checkbutton(label='Phase B-A [4]', variable=ShowC2_P, command=UpdateFreqAll)
        SAShowmenu.menu.add_command(label="-Math-", command=donothing)
        SAShowmenu.menu.add_radiobutton(label='None  [0]', variable=ShowMathSA, value=0, command=UpdateFreqAll)
        SAShowmenu.menu.add_radiobutton(label='A-dB - B-dB [9]', variable=ShowMathSA, value=1, command=UpdateFreqAll)
        SAShowmenu.menu.add_radiobutton(label='B-dB - A-dB [8]', variable=ShowMathSA, value=2, command=UpdateFreqAll)
        SAShowmenu.menu.add_command(label="-Ref Trace-", command=donothing)
        SAShowmenu.menu.add_checkbutton(label='RA-dBV  [6]', variable=ShowRA_VdB, command=UpdateFreqAll)
        SAShowmenu.menu.add_checkbutton(label='RB-dBV  [7]', variable=ShowRB_VdB, command=UpdateFreqAll)
        SAShowmenu.menu.add_checkbutton(label='RPhase A-B', variable=ShowRA_P, command=UpdateFreqAll)
        SAShowmenu.menu.add_checkbutton(label='RPhase B-A', variable=ShowRB_P, command=UpdateFreqAll)
        SAShowmenu.menu.add_checkbutton(label='Ref Math', variable=ShowRMath, command=UpdateFreqAll)
        SAShowmenu.pack(side=LEFT)
        SACursormenu = Menubutton(MarkersMenu, text="Cursors", style="W7.TButton")
        SACursormenu.menu = Menu(SACursormenu, tearoff = 0 )
        SACursormenu["menu"] = SACursormenu.menu
        SACursormenu.menu.add_command(label="-Marker-", command=donothing)
        SACursormenu.menu.add_radiobutton(label='Markers  Off', variable=ShowMarker, value=0, command=UpdateFreqAll)
        SACursormenu.menu.add_radiobutton(label='Markers  [5]', variable=ShowMarker, value=1, command=UpdateFreqAll)
        SACursormenu.menu.add_radiobutton(label='Delta Markers', variable=ShowMarker, value=2, command=UpdateFreqAll)
        SACursormenu.menu.add_command(label="-Cursors-", command=donothing)
        SACursormenu.menu.add_radiobutton(label='Cursor Off', variable=ShowdBCur, value=0)
        SACursormenu.menu.add_radiobutton(label='dB Cursor   [d]', variable=ShowdBCur, value=1)
        #SACursormenu.menu.add_radiobutton(label='Phase Cursor [h]', variable=ShowdBCur, value=2)
        SACursormenu.menu.add_checkbutton(label='Freq Cursor [f]', variable=ShowFCur)
        SACursormenu.pack(side=LEFT)
        # HScale
        Frange1 = Frame( frame2fr )
        Frange1.pack(side=TOP)
        startfreqlab = Label(Frange1, text="Startfreq")
        startfreqlab.pack(side=LEFT)
        StartFreqEntry = Entry(Frange1, width=5, cursor='double_arrow')
        StartFreqEntry.bind('<Return>', onTextKey)
        StartFreqEntry.bind('<MouseWheel>', onTextScroll)
        StartFreqEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        StartFreqEntry.bind("<Button-5>", onTextScroll)
        StartFreqEntry.bind('<Key>', onTextKey)
        StartFreqEntry.pack(side=LEFT)
        StartFreqEntry.delete(0,"end")
        StartFreqEntry.insert(0,10)

        Frange2 = Frame( frame2fr )
        Frange2.pack(side=TOP)
        stopfreqlab = Label(Frange2, text="Stopfreq")
        stopfreqlab.pack(side=LEFT)
        StopFreqEntry = Entry(Frange2, width=7, cursor='double_arrow')
        StopFreqEntry.bind('<Return>', onTextKey)
        StopFreqEntry.bind('<MouseWheel>', onStopfreqScroll)
        StopFreqEntry.bind("<Button-4>", onStopfreqScroll)# with Linux OS
        StopFreqEntry.bind("<Button-5>", onStopfreqScroll)
        StopFreqEntry.bind('<Key>', onTextKey)
        StopFreqEntry.pack(side=LEFT)
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,10000)
        
        HzScale = Frame( frame2fr )
        HzScale.pack(side=TOP)
        sarb1 = Radiobutton(HzScale, text="Lin F", variable=HScale, value=0, command=UpdateFreqTrace )
        sarb1.pack(side=LEFT)
        sarb2 = Radiobutton(HzScale, text="Log F", variable=HScale, value=1, command=UpdateFreqTrace )
        sarb2.pack(side=LEFT)
        #
        PhaseCenter = Frame( frame2fr )
        PhaseCenter.pack(side=TOP)
        PhCenlab = Label(PhaseCenter, text="Center Phase on")
        PhCenlab.pack(side=LEFT)
        PhCenFreqEntry = Entry(PhaseCenter, width=5, cursor='double_arrow')
        PhCenFreqEntry.bind('<Return>', onTextKey)
        PhCenFreqEntry.bind('<MouseWheel>', onTextScroll)
        PhCenFreqEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        PhCenFreqEntry.bind("<Button-5>", onTextScroll)
        PhCenFreqEntry.bind('<Key>', onTextKey)
        PhCenFreqEntry.pack(side=LEFT)
        PhCenFreqEntry.delete(0,"end")
        PhCenFreqEntry.insert(0,RelPhaseCenter.get())
        #
        vertlabel = Label( frame2fr, text="Vertical Scale" )
        vertlabel.pack(side=TOP)
        savrb0 = Radiobutton(frame2fr, text="In dB", variable=SAVScale, value=0, command=UpdateFreqTrace )
        savrb0.pack(side=TOP)
        #
        DBrange = Frame( frame2fr )
        DBrange.pack(side=TOP)
        sab3 = Button(DBrange, text="+dB/div", style="W8.TButton", command=BDBdiv2)
        sab3.pack(side=LEFT)
        sab4 = Button(DBrange, text="-dB/div", style="W8.TButton", command=BDBdiv1)
        sab4.pack(side=LEFT)

        LVBrange = Frame( frame2fr )
        LVBrange.pack(side=TOP)
        sab5 = Button(LVBrange, text="LVL+10", style="W8.TButton", command=Blevel4)
        sab5.pack(side=LEFT)
        sab6 = Button(LVBrange, text="LVL-10", style="W8.TButton", command=Blevel3)
        sab6.pack(side=LEFT)

        LVSrange = Frame( frame2fr )
        LVSrange.pack(side=TOP)
        sab7 = Button(LVSrange, text="LVL+1", style="W8.TButton", command=Blevel2)
        sab7.pack(side=LEFT)
        sab8 = Button(LVSrange, text="LVL-1", style="W8.TButton", command=Blevel1)
        sab8.pack(side=LEFT)
        # Add RMS V controls
        vertscale = Frame( frame2fr )
        vertscale.pack(side=TOP)
        savlab1 = Label(vertscale, text="V RMS")
        savlab1.pack(side=LEFT)
        savrb1 = Radiobutton(vertscale, text="Lin", variable=SAVScale, value=1, command=UpdateFreqTrace )
        savrb1.pack(side=LEFT)
        savrb2 = Radiobutton(vertscale, text="Log", variable=SAVScale, value=2, command=UpdateFreqTrace )
        savrb2.pack(side=LEFT)
        sapsdcb = Checkbutton(frame2fr, text="PSD (sqrt Hz)", variable=SAVPSD)
        sapsdcb.pack(side=TOP)
        #
        vertmax = Frame( frame2fr )
        vertmax.pack(side=TOP)
        vertmaxlab = Label(vertmax, text="VRMS Max")
        vertmaxlab.pack(side=LEFT)
        SAvertmaxEntry = Spinbox(vertmax, width=6, cursor='double_arrow', values=SAMagdiv, command=BCHBlevel)
        SAvertmaxEntry.bind('<MouseWheel>', onSpinBoxScroll)
        SAvertmaxEntry.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
        SAvertmaxEntry.bind("<Button-5>", onSpinBoxScroll)
        SAvertmaxEntry.delete(0,"end")
        SAvertmaxEntry.insert(0,"1.0")
        SAvertmaxEntry.pack(side=LEFT)
##        SAvertmaxEntry = Entry(vertmax, width=7, cursor='double_arrow')
##        SAvertmaxEntry.bind('<Return>', onTextKey)
##        SAvertmaxEntry.bind('<MouseWheel>', onTextScroll)
##        SAvertmaxEntry.bind("<Button-4>", onTextScroll)# with Linux OS
##        SAvertmaxEntry.bind("<Button-5>", onTextScroll)
##        SAvertmaxEntry.bind('<Key>', onTextKey)
##        SAvertmaxEntry.pack(side=LEFT)
##        SAvertmaxEntry.delete(0,"end")
##        SAvertmaxEntry.insert(0,1.0)
        #
        vertmin = Frame( frame2fr )
        vertmin.pack(side=TOP)
        vertminlab = Label(vertmin, text="VRMS Min")
        vertminlab.pack(side=LEFT)
        SAvertminEntry = Spinbox(vertmin, width=6, cursor='double_arrow', values=SAMagdiv, command=BCHBlevel)
        SAvertminEntry.bind('<MouseWheel>', onSpinBoxScroll)
        SAvertminEntry.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
        SAvertminEntry.bind("<Button-5>", onSpinBoxScroll)
        SAvertminEntry.pack(side=LEFT)
        SAvertminEntry.delete(0,"end")
        SAvertminEntry.insert(0,"100uV")
##        SAvertminEntry = Entry(vertmin, width=7, cursor='double_arrow')
##        SAvertminEntry.bind('<Return>', onTextKey)
##        SAvertminEntry.bind('<MouseWheel>', onTextScroll)
##        SAvertminEntry.bind("<Button-4>", onTextScroll)# with Linux OS
##        SAvertminEntry.bind("<Button-5>", onTextScroll)
##        SAvertminEntry.bind('<Key>', onTextKey)
##        SAvertminEntry.pack(side=LEFT)
##        SAvertminEntry.delete(0,"end")
##        SAvertminEntry.insert(0,0.0001)
        #
        sadismiss1button = Button(frame2fr, text="Dismiss", style="W8.TButton", command=DestroySpectrumScreen)
        sadismiss1button.pack(side=TOP)
        
        ADI2 = Label(frame2fr, image=logo, anchor= "sw", compound="top") #, height=49, width=116
        ADI2.pack(side=TOP)
        if ShowBallonHelp > 0:
            sb_tip = CreateToolTip(sasb, 'Stop acquiring data')
            rb_tip = CreateToolTip(sarb, 'Start acquiring data')
            b3_tip = CreateToolTip(sab3, 'Increase number of dB/Div')
            b4_tip = CreateToolTip(sab4, 'Decrease number of dB/Div')
            b5_tip = CreateToolTip(sab5, 'Increase Ref Level by 10 dB')
            b6_tip = CreateToolTip(sab6, 'Decrease Ref Level by 10 dB')
            b7_tip = CreateToolTip(sab7, 'Increase Ref Level by 1 dB')
            b8_tip = CreateToolTip(sab8, 'Decrease Ref Level by 1 dB')
            sadismiss1button_tip = CreateToolTip(sadismiss1button, 'Dismiss Spectrum Analyzer window')
            if LocalLanguage != "English":
                BLoadConfig(LocalLanguage) # load local language configuration

def DestroySpectrumScreen():
    global freqwindow, SpectrumScreenStatus, ca
    
    SpectrumScreenStatus.set(0)
    FreqDisp.set(0)
    FreqCheckBox()
    freqwindow.destroy()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
def XYcaresize(event):
    global XYca, GRWXY, XOLXY, GRHXY, Y0TXY, CANVASwidthXY, CANVASheightXY, FontSize
    global YminXY, YmaxXY, XminXY, XmaxXY

    XOLXY = FontSize * 7
    CANVASwidthXY = event.width - 4
    CANVASheightXY = event.height - 4
    GRWXY = CANVASwidthXY - (2*X0LXY) # 18 new grid width
    GRHXY = CANVASheightXY - int(10 * FontSize)     # new grid height
    YminXY = Y0TXY                  # Minimum position of time grid (top)
    YmaxXY = Y0TXY + GRHXY            # Maximum position of time grid (bottom)
    XminXY = X0LXY                  # Minimum position of time grid (left)
    XmaxXY = X0LXY + GRWXY            # Maximum position of time grid (right)
    UpdateXYAll()
#    
# ================ Make XY Plot sub window ==========================
def MakeXYWindow():
    global logo, CANVASwidthXY, CANVASheightXY, Xsignal, EnableUserEntries
    global YsignalVA, YsignalVB, YsignalVC, YsignalVD, YsignalM, YsignalMX, YsignalMY
    global XYRefAV, XYRefAI, XYRefBV, XYRefBI, XYRefM, XYRefMX, XYRefMY
    global XYScreenStatus, MarkerXYScale, XYca, xywindow, RevDate, SWRev, XYDisp
    global CHAsbxy, CHBsbxy, CHCsbxy, CHDsbxy, CHAxylab, CHBxylab
    global CHAVPosEntryxy, CHBVPosEntryxy, CHCVPosEntryxy, CHDVPosEntryxy
    global CHMXsb, CHMYsb, CHMXPosEntry, CHMYPosEntry
    global XYvpdiv, ScreenXYrefresh, CHANNELS
    global YminXY, Y0TXY, YmaxXY, GRHXY, XminXY, X0LXY, XmaxXY, X0LXY, GRWXY, CANVASwidthXY, CANVASheightXY
    global FrameRelief, BorderSize, LocalLanguage, User3Entry, User4Entry
    global math_tip, bsxy_tip, brxy_tip, snapbutton_tip, savebutton_tip, dismissxybutton_tip, CHAxylab_tip
    global CHBxylab_tip, CHAxyofflab_tip, CHBxyofflab_tip, CHAIxyofflab_tip, CHBIxyofflab_tip
    
    if XYScreenStatus.get() == 0:
        XYScreenStatus.set(1)
        XYDisp.set(1)
        XYCheckBox()
        YminXY = Y0TXY                  # Minimum position of XY grid (top)
        YmaxXY = Y0TXY + GRHXY            # Maximum position of XY grid (bottom)
        XminXY = X0LXY                  # Minimum position of XY grid (left)
        XmaxXY = X0LXY + GRWXY            # Maximum position of XY grid (right)
        CANVASwidthXY = GRWXY + (2*X0LXY)     # The XY canvas width
        CANVASheightXY = GRHXY + 80         # The XY canvas height
        xywindow = Toplevel()
        xywindow.title("X-Y Plot " + SWRev + RevDate)
        xywindow.protocol("WM_DELETE_WINDOW", DestroyXYScreen)
        frame2xyr = Frame(xywindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2xyr.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2xy = Frame(xywindow, borderwidth=BorderSize, relief=FrameRelief)
        frame2xy.pack(side=TOP, expand=YES, fill=BOTH)

        frame3xy = Frame(xywindow, borderwidth=BorderSize, relief=FrameRelief)
        frame3xy.pack(side=TOP, expand=NO, fill=BOTH)

        frame4xy = Frame(xywindow, borderwidth=BorderSize, relief=FrameRelief)
        frame4xy.pack(side=TOP, expand=NO, fill=BOTH)

        frame5xy = Frame(xywindow, borderwidth=BorderSize, relief=FrameRelief)
        frame5xy.pack(side=TOP, expand=NO, fill=BOTH)

        XYca = Canvas(frame2xy, width=CANVASwidthXY, height=CANVASheightXY, background=COLORcanvas, cursor='cross')
        XYca.bind('<Configure>', XYcaresize)
        XYca.bind('<1>', onCanvasXYLeftClick)
        XYca.bind('<3>', onCanvasXYRightClick)
        XYca.bind("<Motion>",onCanvasMouse_xy)
        XYca.bind('<MouseWheel>', onCanvasXYScrollClick)
        XYca.bind("<Button-4>", onCanvasXYScrollClick)# with Linux OS
        XYca.bind("<Button-5>", onCanvasXYScrollClick)
        XYca.bind("<Up>", onCanvasUpArrow)
        XYca.bind("<Down>", onCanvasDownArrow)
        XYca.bind("<Left>", onCanvasLeftArrow)
        XYca.bind("<Right>", onCanvasRightArrow)
        XYca.bind("<space>", onCanvasSpaceBar)
        XYca.bind("a", onCanvasAverage)
        XYca.pack(side=TOP, fill=BOTH, expand=YES)
        #
        RUNframe = Frame( frame2xyr )
        RUNframe.pack(side=TOP)
        rbxy = Button(RUNframe, text="Run", style="Run.TButton", command=BStart)
        rbxy.pack(side=LEFT)
        sbxy = Button(RUNframe, text="Stop", style="Stop.TButton", command=BStop)
        sbxy.pack(side=LEFT)
        # Open Math trace menu
        mathbt = Button(frame2xyr, text="Math", style="W5.TButton", command = NewEnterMathControls)
        mathbt.pack(side=TOP) #, anchor=W)
        # Disply mode menu
        # X - Y mode signal select
        AxisLabX = Label(frame2xyr, text ="-X Axis-", style="A10R1.TLabelframe.Label")
        AxisLabX.pack(side=TOP)
        chaxmenu = Frame( frame2xyr )
        chaxmenu.pack(side=TOP)
        if CHANNELS >= 1:
            rbx1 = Radiobutton(chaxmenu, text='Ch A', style="Strace1.TCheckbutton", variable=Xsignal, value=1, command=UpdateXYTrace)
            rbx1.pack(side=LEFT, anchor=W)
        if CHANNELS >= 2:
            rbx2 = Radiobutton(chaxmenu, text='Ch B', style="Strace2.TCheckbutton", variable=Xsignal, value=3, command=UpdateXYTrace)
            rbx2.pack(side=LEFT, anchor=W)
        chcxmenu = Frame( frame2xyr )
        chcxmenu.pack(side=TOP)
        if CHANNELS >= 3:
            rbx3 = Radiobutton(chcxmenu, text='Ch C', style="Strace3.TCheckbutton", variable=Xsignal, value=2, command=UpdateXYTrace)
            rbx3.pack(side=LEFT, anchor=W)
        if CHANNELS >= 4:
            rbx4 = Radiobutton(chcxmenu, text='Ch D', style="Strace4.TCheckbutton", variable=Xsignal, value=4, command=UpdateXYTrace)
            rbx4.pack(side=LEFT, anchor=W)
        rbx6 = Radiobutton(frame2xyr, text='Math-X', style="Strace6.TCheckbutton", variable=Xsignal, value=6, command=UpdateXYTrace)
        rbx6.pack(side=TOP)
        if CHANNELS >= 1:
            rbx7 = Radiobutton(frame2xyr, text='Histogram Ch A', variable=Xsignal, value=8, command=BHistAsPercent)
            rbx7.pack(side=TOP)
        if CHANNELS >= 2:
            rbx8 = Radiobutton(frame2xyr, text='Histogram Ch B', variable=Xsignal, value=9, command=BHistAsPercent)
            rbx8.pack(side=TOP)
        #
        AxisLabY = Label(frame2xyr, text ="-Y Axis-", style="A10R2.TLabelframe.Label")
        AxisLabY.pack(side=TOP)
        chaymenu = Frame( frame2xyr )
        chaymenu.pack(side=TOP)
        if CHANNELS >= 1:
            rby1 = Checkbutton(chaymenu, text='Ch A', style="Strace1.TCheckbutton", variable=YsignalVA, command=UpdateXYTrace)
            rby1.pack(side=LEFT, anchor=W)
        if CHANNELS >= 2:
            rby2 = Checkbutton(chaymenu, text='Ch B', style="Strace2.TCheckbutton", variable=YsignalVB, command=UpdateXYTrace)
            rby2.pack(side=LEFT, anchor=W)
        chcymenu = Frame( frame2xyr )
        chcymenu.pack(side=TOP)
        if CHANNELS >= 3:
            rby3 = Checkbutton(chcymenu, text='Ch C', style="Strace3.TCheckbutton", variable=YsignalVC, command=UpdateXYTrace)
            rby3.pack(side=LEFT, anchor=W)
        if CHANNELS >= 4:
            rby4 = Checkbutton(chcymenu, text='Ch D', style="Strace4.TCheckbutton", variable=YsignalVD, command=UpdateXYTrace)
            rby4.pack(side=LEFT, anchor=W)
        rby7 = Checkbutton(frame2xyr, text='Math', style="Strace5.TCheckbutton", variable=YsignalM, command=UpdateXYTrace)
        rby7.pack(side=TOP)
        mymenu = Frame( frame2xyr )
        mymenu.pack(side=TOP)
        rby7 = Checkbutton(mymenu, text='Math-X', style="Strace6.TCheckbutton", variable=YsignalMX, command=UpdateXYTrace)
        rby7.pack(side=LEFT, anchor=W)
        rby8 = Checkbutton(mymenu, text='Math-Y', style="Strace7.TCheckbutton", variable=YsignalMY, command=UpdateXYTrace)
        rby8.pack(side=LEFT, anchor=W)
        # show cursor menu buttons
        cursormenu = Frame( frame2xyr )
        cursormenu.pack(side=TOP)
        cb1 = Checkbutton(cursormenu, text='X-Cur', variable=ShowXCur)
        cb1.pack(side=LEFT, anchor=W)
        cb2 = Checkbutton(cursormenu, text='Y-Cur', variable=ShowYCur)
        cb2.pack(side=LEFT, anchor=W)
        cb4 = Checkbutton(frame2xyr, text='Persistance', variable=ScreenXYrefresh, command=UpdateXYTrace)
        cb4.pack(side=TOP)
        #
        # Reference trace menu
        XYrefmenu = Menubutton(frame2xyr, text="Ref Traces", style="W11.TButton")
        XYrefmenu.menu = Menu(XYrefmenu, tearoff = 0 )
        XYrefmenu["menu"] = XYrefmenu.menu
        XYrefmenu.menu.add_command(label="Save SnapShot", command=BSnapShotXY)
        XYrefmenu.menu.add_checkbutton(label="Ch A", variable=XYRefAV, command=UpdateXYTrace)
        XYrefmenu.menu.add_checkbutton(label="Ch B", variable=XYRefBV, command=UpdateXYTrace)
        XYrefmenu.menu.add_checkbutton(label="Math", variable=XYRefM, command=UpdateXYTrace)
        XYrefmenu.menu.add_checkbutton(label="Math-X", variable=XYRefMX, command=UpdateXYTrace)
        XYrefmenu.menu.add_checkbutton(label="Math-Y", variable=XYRefMY, command=UpdateXYTrace)
        XYrefmenu.pack(side=TOP) # , anchor=W)
##
        dismissxybutton = Button(frame2xyr, style="W7.TButton", text="Dismiss", command=DestroyXYScreen)
        dismissxybutton.pack(side=TOP)
        # Add a pair of user entry wigets
        if EnableUserEntries > 0:
            UserEnt = Frame( frame2xyr )
            UserEnt.pack(side=TOP)
            userentlab = Button(UserEnt, text="User", width=4, style="W4.TButton")
            userentlab.pack(side=LEFT,fill=X)
            User3Entry = Entry(UserEnt, width=5, cursor='double_arrow')
            User3Entry.bind('<Return>', onTextKey)
            User3Entry.bind('<MouseWheel>', onTextScroll)
            User3Entry.bind("<Button-4>", onTextScroll)# with Linux OS
            User3Entry.bind("<Button-5>", onTextScroll)
            User3Entry.bind('<Key>', onTextKey)
            User3Entry.pack(side=LEFT)
            User3Entry.delete(0,"end")
            User3Entry.insert(0,1.0)
            User4Entry = Entry(UserEnt, width=5, cursor='double_arrow')
            User4Entry.bind('<Return>', onTextKey)
            User4Entry.bind('<MouseWheel>', onTextScroll)
            User4Entry.bind("<Button-4>", onTextScroll)# with Linux OS
            User4Entry.bind("<Button-5>", onTextScroll)
            User4Entry.bind('<Key>', onTextKey)
            User4Entry.pack(side=LEFT)
            User4Entry.delete(0,"end")
            User4Entry.insert(0,0.0)
        #
        ADI1xy = Label(frame2xyr, image=logo, anchor= "sw", compound="top") # , height=49, width=116
        ADI1xy.pack(side=TOP)
        # Bottom Buttons
        MarkerXYScale = IntVar()
        MarkerXYScale.set(1)
        # Voltage channel A
        if CHANNELS >= 1:
            CHAsbxy = Spinbox(frame3xy, width=5, cursor='double_arrow', values=XYvpdiv)
            CHAsbxy.bind('<MouseWheel>', onSpinBoxScroll)
            CHAsbxy.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
            CHAsbxy.bind("<Button-5>", onSpinBoxScroll)
            CHAsbxy.pack(side=LEFT)
            CHAsbxy.delete(0,"end")
            CHAsbxy.insert(0,0.5)
            CHAxylab = Button(frame3xy, text="A V/Div", style="Rtrace1.TButton", command=SetXYScaleA)
            CHAxylab.pack(side=LEFT)

            CHAVPosEntryxy = Entry(frame3xy, width=5, cursor='double_arrow')
            CHAVPosEntryxy.bind('<Return>', onTextKey)
            CHAVPosEntryxy.bind('<MouseWheel>', onTextScroll)
            CHAVPosEntryxy.bind("<Button-4>", onTextScroll)# with Linux OS
            CHAVPosEntryxy.bind("<Button-5>", onTextScroll)
            CHAVPosEntryxy.bind('<Key>', onTextKey)
            CHAVPosEntryxy.pack(side=LEFT)
            CHAVPosEntryxy.delete(0,"end")
            CHAVPosEntryxy.insert(0, 2.5)
            CHAofflabxy = Button(frame3xy, text="A Pos", style="Rtrace1.TButton", command=SetXYVAPoss)
            CHAofflabxy.pack(side=LEFT)
        # Voltage channel B
        if CHANNELS >= 2:
            CHBsbxy = Spinbox(frame3xy, width=5, cursor='double_arrow', values=XYvpdiv)
            CHBsbxy.bind('<MouseWheel>', onSpinBoxScroll)
            CHBsbxy.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
            CHBsbxy.bind("<Button-5>", onSpinBoxScroll)
            CHBsbxy.pack(side=LEFT)
            CHBsbxy.delete(0,"end")
            CHBsbxy.insert(0,0.5)
            #
            CHBxylab = Button(frame3xy, text="B V/Div", style="Rtrace2.TButton", command=SetXYScaleB)
            CHBxylab.pack(side=LEFT)

            CHBVPosEntryxy = Entry(frame3xy, width=5, cursor='double_arrow')
            CHBVPosEntryxy.bind('<Return>', onTextKey)
            CHBVPosEntryxy.bind('<MouseWheel>', onTextScroll)
            CHBVPosEntryxy.bind("<Button-4>", onTextScroll)# with Linux OS
            CHBVPosEntryxy.bind("<Button-5>", onTextScroll)
            CHBVPosEntryxy.bind('<Key>', onTextKey)
            CHBVPosEntryxy.pack(side=LEFT)
            CHBVPosEntryxy.delete(0,"end")
            CHBVPosEntryxy.insert(0, 2.5)
            CHBofflabxy = Button(frame3xy, text="B Pos", style="Rtrace2.TButton", command=SetXYVBPoss)
            CHBofflabxy.pack(side=LEFT)
# Voltage channel C
        if CHANNELS >= 3:
            CHCsbxy = Spinbox(frame4xy, width=5, cursor='double_arrow', values=XYvpdiv)
            CHCsbxy.bind('<MouseWheel>', onSpinBoxScroll)
            CHCsbxy.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
            CHCsbxy.bind("<Button-5>", onSpinBoxScroll)
            CHCsbxy.pack(side=LEFT)
            CHCsbxy.delete(0,"end")
            CHCsbxy.insert(0,0.5)
            CHCxylab = Button(frame4xy, text="C V/Div", style="Rtrace3.TButton", command=SetXYScaleC)
            CHCxylab.pack(side=LEFT)

            CHCVPosEntryxy = Entry(frame4xy, width=5, cursor='double_arrow')
            CHCVPosEntryxy.bind('<Return>', onTextKey)
            CHCVPosEntryxy.bind('<MouseWheel>', onTextScroll)
            CHCVPosEntryxy.bind("<Button-4>", onTextScroll)# with Linux OS
            CHCVPosEntryxy.bind("<Button-5>", onTextScroll)
            CHCVPosEntryxy.bind('<Key>', onTextKey)
            CHCVPosEntryxy.pack(side=LEFT)
            CHCVPosEntryxy.delete(0,"end")
            CHCVPosEntryxy.insert(0, 2.5)
            CHCofflabxy = Button(frame4xy, text="C Pos", style="Rtrace3.TButton", command=SetXYVCPoss)
            CHCofflabxy.pack(side=LEFT)
        # Voltage channel D
        if CHANNELS >= 4:
            CHDsbxy = Spinbox(frame4xy, width=5, cursor='double_arrow', values=XYvpdiv)
            CHDsbxy.bind('<MouseWheel>', onSpinBoxScroll)
            CHDsbxy.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
            CHDsbxy.bind("<Button-5>", onSpinBoxScroll)
            CHDsbxy.pack(side=LEFT)
            CHDsbxy.delete(0,"end")
            CHDsbxy.insert(0,0.5)
            #
            CHDxylab = Button(frame4xy, text="D V/Div", style="Rtrace4.TButton", command=SetXYScaleD)
            CHDxylab.pack(side=LEFT)

            CHDVPosEntryxy = Entry(frame4xy, width=5, cursor='double_arrow')
            CHDVPosEntryxy.bind('<Return>', onTextKey)
            CHDVPosEntryxy.bind('<MouseWheel>', onTextScroll)
            CHDVPosEntryxy.bind("<Button-4>", onTextScroll)# with Linux OS
            CHDVPosEntryxy.bind("<Button-5>", onTextScroll)
            CHDVPosEntryxy.bind('<Key>', onTextKey)
            CHDVPosEntryxy.pack(side=LEFT)
            CHDVPosEntryxy.delete(0,"end")
            CHDVPosEntryxy.insert(0, 2.5)
            CHDofflabxy = Button(frame4xy, text="D Pos", style="Rtrace4.TButton", command=SetXYVDPoss)
            CHDofflabxy.pack(side=LEFT)
        
        # Math X controls
        CHMXsb = Spinbox(frame5xy, width=5, cursor='double_arrow', values=XYvpdiv) #
        CHMXsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHMXsb.bind('<Button-4>', onSpinBoxScroll)
        CHMXsb.bind('<Button-4>', onSpinBoxScroll)
        CHMXsb.pack(side=LEFT)
        CHMXsb.delete(0,"end")
        CHMXsb.insert(0,0.5)
        CHMXlab = Button(frame5xy, text="MX V/Div", style="Rtrace6.TButton") #, command=SetScaleB)
        CHMXlab.pack(side=LEFT)

        CHMXPosEntry = Entry(frame5xy, width=5, cursor='double_arrow')
        CHMXPosEntry.bind("<Return>", BOffsetB)
        CHMXPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
        CHMXPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        CHMXPosEntry.bind("<Button-5>", onTextScroll)
        CHMXPosEntry.bind('<Key>', onTextKey)
        CHMXPosEntry.pack(side=LEFT)
        CHMXPosEntry.delete(0,"end")
        CHMXPosEntry.insert(0,2.5)
        CHMXofflab = Button(frame5xy, text="MX Pos", style="Rtrace6.TButton") #, command=SetVBPoss)
        CHMXofflab.pack(side=LEFT)

        # Math Y controls
        CHMYsb = Spinbox(frame5xy, width=5, cursor='double_arrow', values=XYvpdiv) #, command=BCHBlevel)
        CHMYsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHMYsb.bind('<Button-4>', onSpinBoxScroll)
        CHMYsb.bind('<Button-4>', onSpinBoxScroll)
        CHMYsb.pack(side=LEFT)
        CHMYsb.delete(0,"end")
        CHMYsb.insert(0,0.5)
        CHBxylab = Button(frame5xy, text="MY V/Div", style="Rtrace7.TButton", command=SetXYScaleB)
        CHBxylab.pack(side=LEFT)
                
        CHMYPosEntry = Entry(frame5xy, width=5, cursor='double_arrow')
        CHMYPosEntry.bind("<Return>", BOffsetB)
        CHMYPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
        CHMYPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        CHMYPosEntry.bind("<Button-5>", onTextScroll)
        CHMYPosEntry.bind('<Key>', onTextKey)
        CHMYPosEntry.pack(side=LEFT)
        CHMYPosEntry.delete(0,"end")
        CHMYPosEntry.insert(0,0.0)
        CHMYofflab = Button(frame5xy, text="MY Pos", style="Rtrace7.TButton")#, command=SetVBPoss)
        CHMYofflab.pack(side=LEFT)
        #
        if ShowBallonHelp > 0:
            math_tip = CreateToolTip(mathbt, 'Open Math window')
            bsxy_tip = CreateToolTip(sbxy, 'Stop acquiring data')
            brxy_tip = CreateToolTip(rbxy, 'Start acquiring data')
            dismissxybutton_tip = CreateToolTip(dismissxybutton, 'Diamiss X-Y plot window')
            CHAxylab_tip = CreateToolTip(CHAxylab, 'Select CHA-V vertical range/position axis to be used for markers and drawn color')
            CHBxylab_tip = CreateToolTip(CHBxylab, 'Select CHB-V vertical range/position axis to be used for markers and drawn color')
            CHAxyofflab_tip = CreateToolTip(CHAofflabxy, 'Set CHA-V position to DC average of signal')
            CHBxyofflab_tip = CreateToolTip(CHBofflabxy, 'Set CHB-V position to DC average of signal')
            if LocalLanguage != "English":
                BLoadConfig(LocalLanguage)

def DestroyXYScreen():
    global xywindow, XYScreenStatus, ca, XYDisp
    
    XYScreenStatus.set(0)
    XYDisp.set(0)
    XYCheckBox()
    xywindow.destroy()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
# Optional Calibration procedure routine
#
##
# Make screen for applying digital filters
def MakeDigFiltWindow():
    global digfltwindow, DigFiltStatus, RevDate, SWRev, DeBugMode
    global DigFiltA, DigFiltB, DifFiltALength, DifFiltBLength, DifFiltAFile, DifFiltBFile
    global DigFiltABoxCar, DigFiltBBoxCar, BCALenEntry, BCBLenEntry
    global BCVASkewEntry, BCVBSkewEntry, DigDeSkewVA, DigDeSkewVB
    global BCVCSkewEntry, BCVDSkewEntry, DigDeSkewVC, DigDeSkewVD
    global AWGFiltA, AWGALenEntry, AWGFiltABoxCar, AWGFiltALength, AWGFiltAFile
    global AWGFiltB, AWGBLenEntry, AWGFiltBBoxCar, AWGFiltBLength, AWGFiltBFile

    if DigFiltStatus.get() == 0:
        DigFiltStatus.set(1)
        digfltwindow = Toplevel()
        digfltwindow.title("Digital Filter " + SWRev + RevDate)
        digfltwindow.resizable(FALSE,FALSE)
        digfltwindow.protocol("WM_DELETE_WINDOW", DestroyDigFiltScreen)
        #
        scriptbutton = Button(digfltwindow, text="Run Script", style="W11.TButton", command=RunScript)
        scriptbutton.grid(row=0, column=0, columnspan=1, sticky=W)
        dismissdfbutton = Button(digfltwindow, text="Dismiss", style="W8.TButton", command=DestroyDigFiltScreen)
        dismissdfbutton.grid(row=0, column=1, columnspan=1, sticky=W)
        frame2 = LabelFrame(digfltwindow, text="CH A Filter", style="A10R1.TLabelframe")
        frame3 = LabelFrame(digfltwindow, text="CH B Filter", style="A10R2.TLabelframe")
        #
        frame2.grid(row=1, column=0, sticky=W)
        frame3.grid(row=1, column=1, sticky=W)
        frame4 = LabelFrame(digfltwindow, text="AWG A Filter", style="A10R1.TLabelframe")
        frame5 = LabelFrame(digfltwindow, text="AWG B Filter", style="A10R2.TLabelframe")
        frame4.grid(row=2, column=0, sticky=W)
        frame5.grid(row=2, column=1, sticky=W)
        #
        digfilta = Frame( frame2 )
        digfilta.pack(side=LEFT)
        #
        lab1 = Checkbutton(digfilta,text="Filter CH A", variable=DigFiltA)
        lab1.grid(row=0, column=0, columnspan=2, sticky=W)
        lab3 = Checkbutton(digfilta,text="Box Car", variable=DigFiltABoxCar, command=BuildBoxCarA)
        lab3.grid(row=1, column=0, sticky=W)
        BCALenEntry = Entry(digfilta, width=3, cursor='double_arrow')
        BCALenEntry.bind("<Return>", onRetDigFiltA)
        BCALenEntry.bind('<MouseWheel>', onDigFiltAScroll)
        BCALenEntry.bind("<Button-4>", onDigFiltAScroll)# with Linux OS
        BCALenEntry.bind("<Button-5>", onDigFiltAScroll)
        # BCALenEntry.bind('<Key>', onTextKey)
        BCALenEntry.grid(row=1, column=1, sticky=W)
        BCALenEntry.delete(0,"end")
        BCALenEntry.insert(0,2)
        bcalab = Label(digfilta, text="Length")
        bcalab.grid(row=1, column=2, sticky=W)
        DifFiltALength = Label(digfilta, text="Length = 0 ")
        DifFiltALength.grid(row=2, column=0, sticky=W)
        DifFiltAFile = Label(digfilta, text="File Name, none ")
        DifFiltAFile.grid(row=3, column=0, columnspan=3, sticky=W)
        cald = Button(digfilta, text='Load From File', command=BLoadDFiltA)
        cald.grid(row=4, column=0, columnspan=3, sticky=W)
        cacb = Button(digfilta, text='Load From Clip Board', command=BLoadDFiltAClip)
        cacb.grid(row=5, column=0, columnspan=3, sticky=W)
        camath = Button(digfilta, text='CH A Filter formula', command=BDFiltAMath)
        camath.grid(row=6, column=0, columnspan=3, sticky=W)
        
        # Deskew controls
        lab5 = Checkbutton(digfilta, text="DeSkew VA", variable=DigDeSkewVA)# , command=BuildBoxCarA)
        lab5.grid(row=7, column=0, sticky=W)
        BCVASkewEntry = Entry(digfilta, width=3, cursor='double_arrow')
        BCVASkewEntry.bind('<MouseWheel>', onTextScroll)
        BCVASkewEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        BCVASkewEntry.bind("<Button-5>", onTextScroll)
        BCVASkewEntry.grid(row=7, column=1, sticky=W)
        BCVASkewEntry.delete(0,"end")
        BCVASkewEntry.insert(0,0)
        bcasklab = Label(digfilta, text="# Samples")
        bcasklab.grid(row=7, column=2, sticky=W)
        #
        lab5i = Checkbutton(digfilta, text="DeSkew VC", variable=DigDeSkewVC)# , command=BuildBoxCarA)
        lab5i.grid(row=8, column=0, sticky=W)
        BCVCSkewEntry = Entry(digfilta, width=3, cursor='double_arrow')
        BCVCSkewEntry.bind('<MouseWheel>', onTextScroll)
        BCVCSkewEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        BCVCSkewEntry.bind("<Button-5>", onTextScroll)
        BCVCSkewEntry.grid(row=8, column=1, sticky=W)
        BCVCSkewEntry.delete(0,"end")
        BCVCSkewEntry.insert(0,0)
        bcaisklab = Label(digfilta, text="# Samples")
        bcaisklab.grid(row=8, column=2, sticky=W)
        #
        #dismissdfbutton = Button(digfilta, text="Dismiss", style="W8.TButton", command=DestroyDigFiltScreen)
        #dismissdfbutton.grid(row=7, column=0, columnspan=1, sticky=W)
        #
        digfiltb = Frame( frame3 )
        digfiltb.pack(side=RIGHT)
        lab2 = Checkbutton(digfiltb,text="Filter CH B", variable=DigFiltB)
        lab2.grid(row=0, column=0, columnspan=2, sticky=W)
        lab4 = Checkbutton(digfiltb,text="Box Car", variable=DigFiltBBoxCar, command=BuildBoxCarB)
        lab4.grid(row=1, column=0, sticky=W)
        BCBLenEntry = Entry(digfiltb, width=3, cursor='double_arrow')
        BCBLenEntry.bind("<Return>", onRetDigFiltB)
        BCBLenEntry.bind('<MouseWheel>', onDigFiltBScroll)
        BCBLenEntry.bind("<Button-4>", onDigFiltBScroll)# with Linux OS
        BCBLenEntry.bind("<Button-5>", onDigFiltBScroll)
        # BCALenEntry.bind('<Key>', onTextKey)
        BCBLenEntry.grid(row=1, column=1, sticky=W)
        BCBLenEntry.delete(0,"end")
        BCBLenEntry.insert(0,2)
        bcblab = Label(digfiltb, text="Length")
        bcblab.grid(row=1, column=2, sticky=W)
        DifFiltBLength = Label(digfiltb,text="Length = 0 ")
        DifFiltBLength.grid(row=2, column=0, sticky=W)
        DifFiltBFile = Label(digfiltb,text="File Name, none ")
        DifFiltBFile.grid(row=3, column=0, columnspan=3, sticky=W)
        cbld = Button(digfiltb, text='Load From File', command=BLoadDFiltB)
        cbld.grid(row=4, column=0, columnspan=3, sticky=W)
        cacb = Button(digfiltb, text='Load From Clip Board', command=BLoadDFiltBClip)
        cacb.grid(row=5, column=0, columnspan=3, sticky=W)
        cbmath = Button(digfiltb, text='CH B Filter formula', command=BDFiltBMath)
        cbmath.grid(row=6, column=0, columnspan=3, sticky=W)
        # Deskew controls
        lab6 = Checkbutton(digfiltb,text="DeSkew VB", variable=DigDeSkewVB)# , command=BuildBoxCarA)
        lab6.grid(row=7, column=0, sticky=W)
        BCVBSkewEntry = Entry(digfiltb, width=3, cursor='double_arrow')
        BCVBSkewEntry.bind('<MouseWheel>', onTextScroll)
        BCVBSkewEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        BCVBSkewEntry.bind("<Button-5>", onTextScroll)
        BCVBSkewEntry.grid(row=7, column=1, sticky=W)
        BCVBSkewEntry.delete(0,"end")
        BCVBSkewEntry.insert(0,0)
        bcbsklab = Label(digfiltb, text="# Samples")
        bcbsklab.grid(row=7, column=2, sticky=W)
        #
        lab6i = Checkbutton(digfiltb,text="DeSkew VD", variable=DigDeSkewVD)# , command=BuildBoxCarA)
        lab6i.grid(row=8, column=0, sticky=W)
        BCVDSkewEntry = Entry(digfiltb, width=3, cursor='double_arrow')
        BCVDSkewEntry.bind('<MouseWheel>', onTextScroll)
        BCVDSkewEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        BCVDSkewEntry.bind("<Button-5>", onTextScroll)
        BCVDSkewEntry.grid(row=8, column=1, sticky=W)
        BCVDSkewEntry.delete(0,"end")
        BCVDSkewEntry.insert(0,0)
        bcbisklab = Label(digfiltb, text="# Samples")
        bcbisklab.grid(row=8, column=2, sticky=W)
##        # AWG A controls
##        awgfilta = Frame( frame4 )
##        awgfilta.pack(side=LEFT)
##        lab7 = Checkbutton(awgfilta,text="Filter AWG A", variable=AWGFiltA, command=MakeAWGwaves)
##        lab7.grid(row=0, column=0, columnspan=2, sticky=W)
##        lab8 = Checkbutton(awgfilta,text="Box Car", variable=AWGFiltABoxCar, command=BuildAWGBoxCarA)
##        lab8.grid(row=1, column=0, sticky=W)
##        AWGALenEntry = Entry(awgfilta, width=3, cursor='double_arrow')
##        AWGALenEntry.bind("<Return>", onRetAWGFiltA)
##        AWGALenEntry.bind('<MouseWheel>', onAWGFiltAScroll)
##        AWGALenEntry.bind("<Button-4>", onAWGFiltAScroll)# with Linux OS
##        AWGALenEntry.bind("<Button-5>", onAWGFiltAScroll)
##        # BCALenEntry.bind('<Key>', onTextKey)
##        AWGALenEntry.grid(row=1, column=1, sticky=W)
##        AWGALenEntry.delete(0,"end")
##        AWGALenEntry.insert(0,2)
##        awgalab = Label(awgfilta, text="Length")
##        awgalab.grid(row=1, column=2, sticky=W)
##        AWGFiltALength = Label(awgfilta, text="Length = 0 ")
##        AWGFiltALength.grid(row=2, column=0, sticky=W)
##        AWGFiltAFile = Label(awgfilta, text="File Name, none ")
##        AWGFiltAFile.grid(row=3, column=0, columnspan=3, sticky=W)
##        awgaload = Button(awgfilta, text='Load From File', command=BLoadAWGFiltA)
##        awgaload.grid(row=4, column=0, columnspan=3, sticky=W)
##        awgacb = Button(awgfilta, text='Load From Clip Board', command=BLoadAWGAFiltClip)
##        awgacb.grid(row=5, column=0, columnspan=3, sticky=W)
##        awgamath = Button(awgfilta, text='AWG A Filter formula', command=BAWGFiltAMath)
##        awgamath.grid(row=6, column=0, columnspan=3, sticky=W)
        #
        #
def onRetDigFiltA(event):
    BuildBoxCarA()

def onDigFiltAScroll(event):
    onTextScroll(event)
    BuildBoxCarA()
    
def BuildBoxCarA():
    global BCALenEntry, DFiltACoef, DigFiltABoxCar, DifFiltALength

    if DigFiltABoxCar.get() == 0:
        return

    FLength = int(BCALenEntry.get())
    if FLength < 2:
        return

    DFiltACoef = [] # empty coef array

    for n in range(FLength):
        DFiltACoef.append(float(1.0/FLength))

    DFiltACoef = numpy.array(DFiltACoef)
    DifFiltALength.config(text = "Length = " + str(int(len(DFiltACoef)))) # change displayed length value

def onRetDigFiltB(event):
    BuildBoxCarB()

def onDigFiltBScroll(event):
    onTextScroll(event)
    BuildBoxCarB()
    
def BuildBoxCarB():
    global BCBLenEntry, DFiltBCoef, DigFiltBBoxCar, DifFiltBLength

    if DigFiltBBoxCar.get() == 0:
        return

    FLength = int(BCBLenEntry.get())
    if FLength < 2:
        return
    
    DFiltBCoef = [] # empty coef array

    for n in range(FLength):
        DFiltBCoef.append(float(1.0/FLength))

    DFiltBCoef = numpy.array(DFiltBCoef)
    DifFiltBLength.config(text = "Length = " + str(int(len(DFiltBCoef)))) # change displayed length value

def DestroyDigFiltScreen():
    global digfltwindow, DigFiltStatus
    
    DigFiltStatus.set(0)
    digfltwindow.destroy()

def BLoadDFiltA():
    global DFiltACoef, digfltwindow, DifFiltALength, DifFiltAFile

# Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=digfltwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=digfltwindow)
        return
    DFiltACoef = []

    for row in csv_f:
        try:
            DFiltACoef.append(float(row[0]))
        except:
            print( 'skipping non-numeric row')
    DFiltACoef = numpy.array(DFiltACoef)
    DifFiltALength.config(text = "Length = " + str(int(len(DFiltACoef)))) # change displayed length value
    DifFiltAFile.config(text = "File Name, " + os.path.basename(filename)) # change displayed file name
    CSVFile.close()
#
def BDFiltAMath():
    global DFiltACoef, digfltwindow, DifFiltALength, DifFiltAFile, DigFilterAString
    
    TempString = DigFilterAString
    DigFilterAString = askstring("CH A Filter Math Formula", "Current Formula: " + DigFilterAString + "\n\nNew Formula:\n", initialvalue=DigFilterAString, parent=digfltwindow)
    if (DigFilterAString == None):         # If Cancel pressed, then None
        DigFilterAString = TempString
        return
    DFiltACoef = eval(DigFilterAString)
    DFiltACoef = numpy.array(DFiltACoef)
    coefsum = numpy.sum(DFiltACoef)
    DFiltACoef = DFiltACoef / coefsum # always normalize to a gain of one
    DifFiltALength.config(text = "Length = " + str(int(len(DFiltACoef)))) # change displayed length value
    DifFiltAFile.config(text = "Using Filter A formula" ) # change displayed file name
    
def BLoadDFiltB():
    global DFiltBCoef, digfltwindow, DifFiltBLength, DifFiltBFile

# Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=digfltwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=digfltwindow)
        return
    DFiltBCoef = []

    for row in csv_f:
        try:
            DFiltBCoef.append(float(row[0]))
        except:
            print( 'skipping non-numeric row')
    DFiltBCoef = numpy.array(DFiltBCoef)
    DifFiltBLength.config(text = "Length = " + str(int(len(DFiltBCoef)))) # change displayed length value
    DifFiltBFile.config(text = "File Name, " + os.path.basename(filename)) # change displayed file name
    CSVFile.close()
#
def BDFiltBMath():
    global DFiltBCoef, digfltwindow, DifFiltBLength, DifFiltBFile, DigFilterBString
    
    TempString = DigFilterBString
    DigFilterBString = askstring("CH B Filter Math Formula", "Current Formula: " + DigFilterBString + "\n\nNew Formula:\n", initialvalue=DigFilterBString, parent=digfltwindow)
    if (DigFilterBString == None):         # If Cancel pressed, then None
        DigFilterBString = TempString
        return
    DFiltBCoef = eval(DigFilterBString)
    DFiltBCoef = numpy.array(DFiltBCoef)
    coefsum = numpy.sum(DFiltBCoef)
    DFiltBCoef = DFiltBCoef / coefsum
    DifFiltBLength.config(text = "Length = " + str(int(len(DFiltBCoef)))) # change displayed length value
    DifFiltBFile.config(text = "Using Filter B formula" ) # change displayed file name
#
def onRetAWGFiltA(event):
    BuildAWGBoxCarA()

def onAWGFiltAScroll(event):
    onTextScroll(event)
    BuildAWGBoxCarA()
    
def BuildAWGBoxCarA():
    global AWGALenEntry, AWGFiltACoef, AWGFiltABoxCar, AWGFiltALength

    if AWGFiltABoxCar.get() == 0:
        return

    FLength = int(AWGALenEntry.get())
    if FLength < 2:
        return

    AWGFiltACoef = [] # empty coef array

    for n in range(FLength):
        AWGFiltACoef.append(float(1.0/FLength))

    AWGFiltACoef = numpy.array(AWGFiltACoef)
    AWGFiltALength.config(text = "Length = " + str(int(len(AWGFiltACoef)))) # change displayed length value
    MakeAWGwaves()
#
def onRetAWGFiltB(event):
    BuildAWGBoxCarb()

def onAWGFiltBScroll(event):
    onTextScroll(event)
    BuildAWGBoxCarB()
    
def BuildAWGBoxCarB():
    global AWGBLenEntry, AWGFiltBCoef, AWGFiltBBoxCar, AWGFiltBLength

    if AWGFiltBBoxCar.get() == 0:
        return

    FLength = int(AWGBLenEntry.get())
    if FLength < 2:
        return

    AWGFiltBCoef = [] # empty coef array

    for n in range(FLength):
        AWGFiltBCoef.append(float(1.0/FLength))

    AWGFiltBCoef = numpy.array(AWGFiltBCoef)
    AWGFiltBLength.config(text = "Length = " + str(int(len(AWGFiltBCoef)))) # change displayed length value
    MakeAWGwaves()
#    
def BLoadAWGFiltA():
    global AWGFiltACoef, digfltwindow, AWGFiltALength, AWGFiltAFile

# Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=digfltwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=digfltwindow)
        return
    AWGFiltACoef = []

    for row in csv_f:
        try:
            AWGFiltACoef.append(float(row[0]))
        except:
            print( 'skipping non-numeric row')
    AWGFiltACoef = numpy.array(AWGFiltACoef)
    AWGFiltALength.config(text = "Length = " + str(int(len(AWGFiltACoef)))) # change displayed length value
    AWGFiltAFile.config(text = "File Name, " + os.path.basename(filename)) # change displayed file name
    CSVFile.close()
    MakeAWGwaves()
#
def BAWGFiltAMath():
    global AWGFiltACoef, digfltwindow, AWGFiltALength, AWGFiltAFile, AWGFilterAString
    
    TempString = AWGFilterAString
    AWGFilterAString = askstring("AWG A Filter Math Formula", "Current Formula: " + DigFilterAString + "\n\nNew Formula:\n", initialvalue=AWGFilterAString, parent=digfltwindow)
    if (AWGFilterAString == None):         # If Cancel pressed, then None
        AWGFilterAString = TempString
        return
    AWGFiltACoef = eval(AWGFilterAString)
    AWGFiltACoef = numpy.array(AWGFiltACoef)
    coefsum = numpy.sum(AWGFiltACoef)
    AWGFiltACoef = AWGFiltACoef / coefsum
    AWGFiltALength.config(text = "Length = " + str(int(len(AWGFiltACoef)))) # change displayed length value
    AWGFiltAFile.config(text = "AWG A Filter formula" ) # change displayed file name
    MakeAWGwaves()
#
#
def BLoadAWGFiltB():
    global AWGFiltBCoef, digfltwindow, AWGFiltbLength, AWGFiltBFile

# Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=digfltwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=digfltwindow)
        return
    AWGFiltBCoef = []

    for row in csv_f:
        try:
            AWGFiltBCoef.append(float(row[0]))
        except:
            print( 'skipping non-numeric row')
    AWGFiltBCoef = numpy.array(AWGFiltBCoef)
    AWGFiltBLength.config(text = "Length = " + str(int(len(AWGFiltBCoef)))) # change displayed length value
    AWGFiltBFile.config(text = "File Name, " + os.path.basename(filename)) # change displayed file name
    CSVFile.close()
    MakeAWGwaves()
#
def BAWGFiltBMath():
    global AWGFiltBCoef, digfltwindow, AWGFiltBLength, AWGFiltBFile, AWGFilterBString
    
    TempString = AWGFilterBString
    AWGFilterBString = askstring("AWG B Filter Math Formula", "Current Formula: " + DigFilterBString + "\n\nNew Formula:\n", initialvalue=AWGFilterBString, parent=digfltwindow)
    if (AWGFilterBString == None):         # If Cancel pressed, then None
        AWGFilterBString = TempString
        return
    AWGFiltBCoef = eval(AWGFilterBString)
    AWGFiltBCoef = numpy.array(AWGFiltBCoef)
    coefsum = numpy.sum(AWGFiltBCoef)
    AWGFiltBCoef = AWGFiltBCoef / coefsum
    AWGFiltBLength.config(text = "Length = " + str(int(len(AWGFiltBCoef)))) # change displayed length value
    AWGFiltBFile.config(text = "AWG B Filter formula" ) # change displayed file name
    MakeAWGwaves()
#
# Higher order SINC filters can be generated by convolving first order Box Car filters
def BuildRejectFilter(Order, Freject, Fsample):
    # Order can be 1, 2, 3 or 4
    # Fsample = 100000
    # Calculate SINC1 oversample ratios for Freject
    osr = int(Fsample/Freject) # 
    # osr60 = int(Fsample/60) # 60 Hz example
    # Create "boxcar" SINC1 filter
    sinc1 = numpy.ones(osr)
    # sinc1_60 = np.ones(osr60)
    # Calculate higher order filters
    sinc2 = numpy.convolve(sinc1, sinc1)
    sinc3 = numpy.convolve(sinc2, sinc1)
    sinc4 = numpy.convolve(sinc2, sinc2)
    fosr = float(Fsample/Freject)
    if Order == 1:
        return sinc1/fosr
    elif Order == 2:
        return sinc2/fosr
    elif Order == 3:
        return sinc3/fosr
    elif Order == 4:
        return sinc4/fosr
    else:
        return sinc1/fosr
    # Here's the SINC4-ish filter
    # with three zeros at 50Hz, one at 60Hz.
    # filt_50_60_rej = np.convolve(sinc3_50, sinc1_60)

# Fit the function y = A * exp(B * x) to the data arrays xs and ys
# returns (A, B)
# From: https://mathworld.wolfram.com/LeastSquaresFittingExponential.html
def fit_exp(xs, ys):
    S_x2_y = 0.0
    S_y_lny = 0.0
    S_x_y = 0.0
    S_x_y_lny = 0.0
    S_y = 0.0
    for (x,y) in zip(xs, ys):
        S_x2_y += x * x * y
        S_y_lny += y * numpy.log(y)
        S_x_y += x * y
        S_x_y_lny += x * y * numpy.log(y)
        S_y += y
    #end
    a = (S_x2_y * S_y_lny - S_x_y * S_x_y_lny) / (S_y * S_x2_y - S_x_y * S_x_y)
    b = (S_y * S_x_y_lny - S_x_y * S_y_lny) / (S_y * S_x2_y - S_x_y * S_x_y)
    return (numpy.exp(a), b)
#
def MakeCommandScreen():
    global commandwindow, CommandStatus, ExecString, LastCommand, RevDate, SWRev
    
    if CommandStatus.get() == 0:
        CommandStatus.set(1)
        commandwindow = Toplevel()
        commandwindow.title("Command Line " + SWRev + RevDate)
        commandwindow.resizable(FALSE,FALSE)
        commandwindow.protocol("WM_DELETE_WINDOW", DestroyCommandScreen)
        toplab = Label(commandwindow,text="Command Line Interface ", style="A12B.TLabel")
        toplab.grid(row=0, column=0, columnspan=4, sticky=W)
        cl1 = Label(commandwindow,text="Last command:")
        cl1.grid(row=1, column=0, sticky=W)
        LastCommand = Label(commandwindow,text=" ")
        LastCommand.grid(row=2, column=0, columnspan=4, sticky=W)
        ExecString = Entry(commandwindow, width=40)
        ExecString.bind("<Return>", RExecuteFromString)
        ExecString.grid(row=3, column=0, columnspan=4, sticky=W)
        ExecString.delete(0,"end")
        ExecString.insert(0,"")
        executeclbutton = Button(commandwindow, text="Execute", style="W8.TButton", command=BExecuteFromString)
        executeclbutton.grid(row=4, column=0, sticky=W, pady=8)
        scriptbutton = Button(commandwindow, text="Run Script", style="W10.TButton", command=RunScript)
        scriptbutton.grid(row=4, column=1, sticky=W, pady=8)
        # 
        dismissclbutton = Button(commandwindow, text="Dismiss", style="W8.TButton", command=DestroyCommandScreen)
        dismissclbutton.grid(row=4, column=2, sticky=W, pady=7)
        
def DestroyCommandScreen():
    global commandwindow, CommandStatus
    
    CommandStatus.set(0)
    commandwindow.destroy()

def RExecuteFromString(temp):

    BExecuteFromString()
    
def BExecuteFromString(): # global VBuffA,AWGAwaveform;VBuffA=AWGAwaveform
    global ExecString, LastCommand
    global VBuffA, VBuffB, NoiseCH1, NoiseCH2, VFilterA, VFilterB
    global VmemoryA, VmemoryB, AWGAwaveform, AWGBwaveform
    global VUnAvgA, VUnAvgB, IUnAvgA, IUnAvgB, UnAvgSav
    global TgInput, TgEdge, SingleShot, AutoLevel, SingleShotSA, ManualTrigger
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, Ysignal, AutoCenterA, AutoCenterB
    global CHAsb, CHBsb, HScale, FreqTraceMode
    global CHAsbxy, CHBsbxy, CHMXPosEntry, CHMYPosEntry
    global CHAVPosEntryxy, CHBVPosEntryxy
    global ShowC1_V, ShowC2_V, MathTrace, MathXUnits, MathYUnits
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry, HozPossentry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGATerm, AWGAMode, AWGARepeatFlag, AWGBRepeatFlag
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBPhaseEntry, AWGBShape, AWGBTerm, AWGBMode, AWGSync, AWGAIOMode, AWGBIOMode
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1, MeasDCI1, MeasMinI1
    global MeasMaxI1, MeasMidI1, MeasPPI1, MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2
    global MeasPPV2, MeasDCI2, MeasMinI2, MeasMaxI2, MeasMidI2, MeasPPI2, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasRMSI1, MeasRMSI2, MeasPhase, MeasDelay
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ, IASource, DisplaySeries
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC, AWG_Amp_Mode
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, AWGAPhaseDelay, AWGBPhaseDelay
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global MathAxis, MathXAxis, MathYAxis, Show_MathX, Show_MathY, MathScreenStatus, MathWindow
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2, CHAI_RC_HP, CHBI_RC_HP
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2, RelPhaseCenter, ImpedanceCenter
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global Show_Rseries, Show_Xseries, Show_Magnitude, Show_Angle
    global AWGABurstFlag, AWGACycles, AWGABurstDelay, AWGAwaveform, AWGAcsvFile, AWGBcsvFile
    global AWGBBurstFlag, AWGBCycles, AWGBBurstDelay, AWGBwaveform, AWGAwavFile, AWGBwavFile
    global SCLKPort, SDATAPort, SLATCHPort, FminEntry, HtMulEntry
    global phawindow, PhAca, PhAScreenStatus, PhADisp
    global GRWPhA, X0LPhA, GRHPhA, Y0TPhA, EnableScopeOnly
    global VScale, IScale, RefphEntry, BoardStatus, boardwindow, BrdSel
    global vat_btn, vbt_btn, iat_btn, ibt_btn, vabt_btn, RollBt, Roll_Mode
    global ScreenWidth, ScreenHeight
    global TRACEwidth, ColorMode, ca, COLORcanvas, COLORtrace4, COLORtraceR4, COLORtext
    global AWGANoiseEntry, AWGBNoiseEntry, AWGAsbnoise, AWGBsbnoise
    global AWGFiltA, AWGALenEntry, AWGFiltABoxCar, AWGFiltALength, digfltwindow
    global DFiltACoef, DFiltBCoef, AWGACoef, AWGBCoef

    try:
        exec( ExecString.get(), globals(), globals())
        # exec( ExecString.get() )
        LastCommand.config(text = ExecString.get() ) # change displayed last command
    except:
        LastCommand.config(text = "Syntax Error Encountered" ) # change displayed last command
        return()
#
def CAresize(event):
    global ca, GRW, XOL, GRH, Y0T, CANVASwidth, CANVASheight, FontSize
    
    XOL = FontSize * 7
    CANVASwidth = event.width - 4
    CANVASheight = event.height - 4
    GRW = CANVASwidth - (2 * X0L) # new grid width
    GRH = CANVASheight - (Y0T + (FontSize * 7))   # new grid height
    UpdateTimeAll()
#
def UpdateMeasureScreen():
    global ChaLab1, ChaLab12, ChaLab3, ChaLab4, ChaLab5, ChaLab6
    global ChaValue1, ChaValue2, ChaValue3, ChaValue4, ChaValue5, ChaValue6
    global ChbLab1, ChbLab12, ChbLab3, ChbLab4, ChbLab5, ChbLab6
    global ChbValue1, ChbValue2, ChbValue3, ChbValue4, ChbValue5, ChbValue6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString1))
    ChaValue1.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString2))
    ChaValue2.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString3))
    ChaValue3.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString4))
    ChaValue4.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString5))
    ChaValue5.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString6))
    ChaValue6.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString1))
    ChbValue1.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString2))
    ChbValue2.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString3))
    ChbValue3.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString4))
    ChbValue4.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString5))
    ChbValue5.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString6))
    ChbValue6.config(text = ValueText)
#
def MakeMeasureScreen():
    global measurewindow, MeasureStatus, RevDate, SWRev
    global ChaLab1, ChaLab12, ChaLab3, ChaLab4, ChaLab5, ChaLab6
    global ChaValue1, ChaValue2, ChaValue3, ChaValue4, ChaValue5, ChaValue6
    global ChbLab1, ChbLab12, ChbLab3, ChbLab4, ChbLab5, ChbLab6
    global ChbValue1, ChbValue2, ChbValue3, ChbValue4, ChbValue5, ChbValue6
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    
    if MeasureStatus.get() == 0:
        MeasureStatus.set(1)
        measurewindow = Toplevel()
        measurewindow.title("Measurements " + SWRev + RevDate)
        measurewindow.resizable(FALSE,FALSE)
        measurewindow.protocol("WM_DELETE_WINDOW", DestroyMeasureScreen)
        toplab = Label(measurewindow,text="Measurements ", style="A12B.TLabel")
        toplab.grid(row=0, column=0, columnspan=2, sticky=W)
        ChaLab1 = Label(measurewindow,text=ChaLableSrring1, style="A10B.TLabel")
        ChaLab1.grid(row=1, column=0, columnspan=1, sticky=W)
        ChaValue1 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue1.grid(row=1, column=1, columnspan=1, sticky=W)
        ChaLab2 = Label(measurewindow,text=ChaLableSrring2, style="A10B.TLabel")
        ChaLab2.grid(row=1, column=2, columnspan=1, sticky=W)
        ChaValue2 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue2.grid(row=1, column=3, columnspan=1, sticky=W)
        ChaLab3 = Label(measurewindow,text=ChaLableSrring3, style="A10B.TLabel")
        ChaLab3.grid(row=2, column=0, columnspan=1, sticky=W)
        ChaValue3 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue3.grid(row=2, column=1, columnspan=1, sticky=W)
        ChaLab4 = Label(measurewindow,text=ChaLableSrring4, style="A10B.TLabel")
        ChaLab4.grid(row=2, column=2, columnspan=1, sticky=W)
        ChaValue4 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue4.grid(row=2, column=3, columnspan=1, sticky=W)
        ChaLab5 = Label(measurewindow,text=ChaLableSrring5, style="A10B.TLabel")
        ChaLab5.grid(row=3, column=0, columnspan=1, sticky=W)
        ChaValue5 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue5.grid(row=3, column=1, columnspan=1, sticky=W)
        ChaLab6 = Label(measurewindow,text=ChaLableSrring6, style="A10B.TLabel")
        ChaLab6.grid(row=3, column=2, columnspan=1, sticky=W)
        ChaValue6 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue6.grid(row=3, column=3, columnspan=1, sticky=W)
        #
        ChbLab1 = Label(measurewindow,text=ChbLableSrring1, style="A10B.TLabel")
        ChbLab1.grid(row=4, column=0, columnspan=1, sticky=W)
        ChbValue1 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue1.grid(row=4, column=1, columnspan=1, sticky=W)
        ChbLab2 = Label(measurewindow,text=ChbLableSrring2, style="A10B.TLabel")
        ChbLab2.grid(row=4, column=2, columnspan=1, sticky=W)
        ChbValue2 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue2.grid(row=4, column=3, columnspan=1, sticky=W)
        ChbLab3 = Label(measurewindow,text=ChbLableSrring3, style="A10B.TLabel")
        ChbLab3.grid(row=5, column=0, columnspan=1, sticky=W)
        ChbValue3 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue3.grid(row=5, column=1, columnspan=1, sticky=W)
        ChbLab4 = Label(measurewindow,text=ChbLableSrring4, style="A10B.TLabel")
        ChbLab4.grid(row=5, column=2, columnspan=1, sticky=W)
        ChbValue4 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue4.grid(row=5, column=3, columnspan=1, sticky=W)
        ChbLab5 = Label(measurewindow,text=ChbLableSrring5, style="A10B.TLabel")
        ChbLab5.grid(row=6, column=0, columnspan=1, sticky=W)
        ChbValue5 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue5.grid(row=6, column=1, columnspan=1, sticky=W)
        ChbLab6 = Label(measurewindow,text=ChbLableSrring6, style="A10B.TLabel")
        ChbLab6.grid(row=6, column=2, columnspan=1, sticky=W)
        ChbValue6 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue6.grid(row=6, column=3, columnspan=1, sticky=W)
#
def DestroyMeasureScreen():
    global measurewindow, MeasureStatus
    
    MeasureStatus.set(0)
    measurewindow.destroy()
#
## Make the Digital I/O screen
def MakeDigScreen():
    global D0_in_on, D1_in_on, D2_in_on, D3_in_on, D4_in_on, D5_in_on, D6_in_on, D7_in_on
    global digin0, digin1, digin2, digin3, digin4, digin5, digin6, digin7
    global DigScreenStatus, win2, PWMDivEntry, PWMWidthEntry, PWMChannels
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn, DigChannels, LogicChannels
    global d0btn, d1btn, d2btn, d3btn, d4btn, d5btn, d6btn, d7btn, TgInput
    global pwmbtn, PWMLabel, FrameBG, BorderSize
    
    # setup Dig output window
    if DigScreenStatus.get() == 0:
        DigScreenStatus.set(1)
        win2 = Toplevel()
        win2.title("Digital Controls")
        win2.resizable(FALSE,FALSE)
        win2.protocol("WM_DELETE_WINDOW", DestroyDigScreen)
        win2.configure(background=FrameBG, borderwidth=BorderSize)
        RowNum = 1
        d7lab = Label(win2, text="  D7  ", background = "#8080ff")
        d7lab.grid(row=RowNum, column=1, sticky=W)
        d6lab = Label(win2, text="  D6  ", background = "#8080ff")
        d6lab.grid(row=RowNum, column=2, sticky=W)
        d5lab = Label(win2, text="  D5  ", background = "#8080ff")
        d5lab.grid(row=RowNum, column=3, sticky=W)
        d4lab = Label(win2, text="  D4  ", background = "#8080ff")
        d4lab.grid(row=RowNum, column=4, sticky=W)
        d3lab = Label(win2, text="  D3  ", background = "#8080ff")
        d3lab.grid(row=RowNum, column=5, sticky=W)
        d2lab = Label(win2, text="  D2  ", background = "#8080ff")
        d2lab.grid(row=RowNum, column=6, sticky=W)
        d1lab = Label(win2, text="  D1  ", background = "#8080ff")
        d1lab.grid(row=RowNum, column=7, sticky=W)
        d0lab = Label(win2, text="  D0  ", background = "#8080ff")
        d0lab.grid(row=RowNum, column=8, sticky=W)
        RowNum = RowNum + 1
        d7btn = Button(win2, image=RoundRedBtn, command=DigBtn7)
        d7btn.grid(row=RowNum, column=1, sticky=W)
        d6btn = Button(win2, image=RoundRedBtn, command=DigBtn6)
        d6btn.grid(row=RowNum, column=2, sticky=W)
        d5btn = Button(win2, image=RoundRedBtn, command=DigBtn5)
        d5btn.grid(row=RowNum, column=3, sticky=W)
        d4btn = Button(win2, image=RoundRedBtn, command=DigBtn4)
        d4btn.grid(row=RowNum, column=4, sticky=W)
        d3btn = Button(win2, image=RoundRedBtn, command=DigBtn3)
        d3btn.grid(row=RowNum, column=5, sticky=W)
        d2btn = Button(win2, image=RoundRedBtn, command=DigBtn2)
        d2btn.grid(row=RowNum, column=6, sticky=W)
        d1btn = Button(win2, image=RoundRedBtn, command=DigBtn1)
        d1btn.grid(row=RowNum, column=7, sticky=W)
        d0btn = Button(win2, image=RoundRedBtn, command=DigBtn0)
        d0btn.grid(row=RowNum, column=8, sticky=W)
        RowNum = RowNum + 1
        if LogicChannels > 0:
            TriggerOnLab = Label(win2, text="Trigger on:") # , background = "#8080ff")
            TriggerOnLab.grid(row=RowNum, column=1, columnspan=4, sticky=W)
            RowNum = RowNum + 1
            LogTrigrb1 = Radiobutton(win2, text="D7", variable=TgInput, value=12) #, command=)
            LogTrigrb1.grid(row=RowNum, column=1, sticky=W)
            LogTrigrb2 = Radiobutton(win2, text="D6", variable=TgInput, value=11) #, command=)
            LogTrigrb2.grid(row=RowNum, column=2, sticky=W)
            LogTrigrb3 = Radiobutton(win2, text="D5", variable=TgInput, value=10) #, command=)
            LogTrigrb3.grid(row=RowNum, column=3, sticky=W)
            LogTrigrb4 = Radiobutton(win2, text="D4", variable=TgInput, value=9) #, command=)
            LogTrigrb4.grid(row=RowNum, column=4, sticky=W)
            LogTrigrb5 = Radiobutton(win2, text="D3", variable=TgInput, value=8) #, command=)
            LogTrigrb5.grid(row=RowNum, column=5, sticky=W)
            LogTrigrb6 = Radiobutton(win2, text="D2", variable=TgInput, value=7) #, command=)
            LogTrigrb6.grid(row=RowNum, column=6, sticky=W)
            LogTrigrb7 = Radiobutton(win2, text="D1", variable=TgInput, value=6) #, command=)
            LogTrigrb7.grid(row=RowNum, column=7, sticky=W)
            LogTrigrb8 = Radiobutton(win2, text="D0", variable=TgInput, value=5) #, command=)
            LogTrigrb8.grid(row=RowNum, column=8, sticky=W)
            #Disable un used Trigger buttons
            if LogicChannels < 8:
                LogTrigrb1.config(state=DISABLED)
            if LogicChannels < 7:
                LogTrigrb2.config(state=DISABLED)
            if LogicChannels < 6:
                LogTrigrb3.config(state=DISABLED)
            if LogicChannels < 5:
                LogTrigrb4.config(state=DISABLED)
            if LogicChannels < 4:
                LogTrigrb5.config(state=DISABLED)
            if LogicChannels < 3:
                LogTrigrb6.config(state=DISABLED)
            if LogicChannels < 2:
                LogTrigrb7.config(state=DISABLED)
            if LogicChannels < 1:
                LogTrigrb8.config(state=DISABLED)
            RowNum = RowNum + 1
#
        if PWMChannels >= 1:
            pwmlab = Label(win2, text="On/Off", background = "#8080ff")
            pwmlab.grid(row=RowNum, column=1, sticky=W)
            pwmbtn = Button(win2, image=RoundRedBtn, command=TogglePWM)
            pwmbtn.grid(row=RowNum, column=2, sticky=W)
            RowNum = RowNum + 1
            PWMLabel = Label(win2, text="PWM Freq Divider")
            PWMLabel.grid(row=RowNum, column=1, columnspan=3, sticky=W)
            PWMDivEntry = Entry(win2, width=6, cursor='double_arrow')
            PWMDivEntry.bind("<Return>", UpdatePWM)
            PWMDivEntry.bind('<MouseWheel>', onPWMFScroll)
            PWMDivEntry.bind("<Button-4>", onPWMFScroll)# with Linux OS
            PWMDivEntry.bind("<Button-5>", onPWMFScroll)
            #PWMDivEntry.bind('<Key>', onTextKeyPWMF)
            PWMDivEntry.grid(row=RowNum, column=5, columnspan=2, sticky=W)
            PWMDivEntry.delete(0,"end")
            PWMDivEntry.insert(0,500)
            #
            RowNum = RowNum + 1
            pwmwlab = Label(win2, text="PWM Width")
            pwmwlab.grid(row=RowNum, column=1, columnspan=3, sticky=W)
            PWMWidthEntry = Entry(win2, width=6, cursor='double_arrow')
            PWMWidthEntry.bind("<Return>", UpdatePWM)
            PWMWidthEntry.bind('<MouseWheel>', onPWMWScroll)
            PWMWidthEntry.bind("<Button-4>", onPWMWScroll)# with Linux OS
            PWMWidthEntry.bind("<Button-5>", onPWMWScroll)
            #PWMWidthEntry.bind('<Key>', onTextKeyPWMW)
            PWMWidthEntry.grid(row=RowNum, column=5, columnspan=2, sticky=W)
            PWMWidthEntry.delete(0,"end")
            PWMWidthEntry.insert(0,50)
            RowNum = RowNum + 1
        #
        digdismissbutton = Button(win2, text="Dismiss", command=DestroyDigScreen)
        digdismissbutton.grid(row=RowNum, column=1, columnspan=2, sticky=W)
        #Disable un used Digital buttons
        if DigChannels < 8:
            d7btn.config(state=DISABLED)
        if DigChannels < 7:
            d6btn.config(state=DISABLED)
        if DigChannels < 6:
            d5btn.config(state=DISABLED)
        if DigChannels < 5:
            d4btn.config(state=DISABLED)
        if DigChannels < 4:
            d3btn.config(state=DISABLED)
        if DigChannels < 3:
            d2btn.config(state=DISABLED)
        if DigChannels < 2:
            d1btn.config(state=DISABLED)
        if DigChannels < 1:
            d1btn.config(state=DISABLED)
#
## Define digital button switch functions
def TogglePWM():
    global PWM_is_on, pwmbtn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if PWM_is_on:
        pwmbtn.config(image = RoundRedBtn)
        PWM_is_on = False
    else:
        pwmbtn.config(image = RoundGrnBtn)
        PWM_is_on = True
    try:
        PWM_On_Off()
    except:
        pass
#
def DigBtn0():
    global D0_is_on, d0btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D0_is_on:
        d0btn.config(image = RoundRedBtn)
        D0_is_on = False
    else:
        d0btn.config(image = RoundGrnBtn)
        D0_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
def DigBtn1():
    global D1_is_on, d1btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D1_is_on:
        d1btn.config(image = RoundRedBtn)
        D1_is_on = False
    else:
        d1btn.config(image = RoundGrnBtn)
        D1_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
def DigBtn2():
    global D2_is_on, d2btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D2_is_on:
        d2btn.config(image = RoundRedBtn)
        D2_is_on = False
    else:
        d2btn.config(image = RoundGrnBtn)
        D2_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
def DigBtn3():
    global D3_is_on, d3btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D3_is_on:
        d3btn.config(image = RoundRedBtn)
        D3_is_on = False
    else:
        d3btn.config(image = RoundGrnBtn)
        D3_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
def DigBtn4():
    global D4_is_on, d4btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D4_is_on:
        d4btn.config(image = RoundRedBtn)
        D4_is_on = False
    else:
        d4btn.config(image = RoundGrnBtn)
        D4_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
def DigBtn5():
    global D5_is_on, d5btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D5_is_on:
        d5btn.config(image = RoundRedBtn)
        D5_is_on = False
    else:
        d5btn.config(image = RoundGrnBtn)
        D5_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
def DigBtn6():
    global D6_is_on, d6btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D6_is_on:
        d6btn.config(image = RoundRedBtn)
        D6_is_on = False
    else:
        d6btn.config(image = RoundGrnBtn)
        D6_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
def DigBtn7():
    global D7_is_on, d7btn
    global RoundRedBtn, RoundGrnBtn, RoundOrBtn
	
    # Determine is on or off
    if D7_is_on:
        d7btn.config(image = RoundRedBtn)
        D7_is_on = False
    else:
        d7btn.config(image = RoundGrnBtn)
        D7_is_on = True
    try:
        SetDigPin()
    except:
        pass
#
## Destroy the Digtal controls Screen
def DestroyDigScreen():
    global win2, DigScreenStatus
    
    DigScreenStatus.set(0)
    win2.destroy()
#
def onStopfreqScroll(event):
    global StopFreqEntry, ADC_Mux_Mode, FWRevOne

    onTextScroll(event)
    try:
        StopFrequency = float(StopFreqEntry.get())
    except:
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,100000)
        StopFrequency = 100000
#
def onStopBodeScroll(event):
    global StopBodeEntry, ADC_Mux_Mode, FWRevOne

    onTextScroll(event)
    try:
        StopFrequency = float(StopBodeEntry.get())
    except:
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,100000)
        StopFrequency = 100000
#
# Draw analog meter face
def Build_meter():
    global MXcenter, MYcenter, MRadius, MGRW, MGRH, MAScreenStatus, MeterMaxEntry
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6, COLORtrace7
    global COLORtext, TRACEwidth, GridWidth, FontSize
    global COLORcanvas, COLORgrid, COLORdial, SWRev, RevDate, MAca, mawindow
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel
    global IndicatorA, IndicatorB, IndicatorC, IndicatorD
    global IndicatorM, IndicatorMX, IndicatorMY
    global ValueDisA, ValueDisB, ValueDisC, ValueDisD, DialSpan, CHANNELS
    global ValueDisM, ValueDisMX, ValueDisMY

    if MAScreenStatus.get() == 0:
        MAScreenStatus.set(1)
        mawindow = Toplevel()
        mawindow.title("Analog Meter " + SWRev + RevDate)
        mawindow.protocol("WM_DELETE_WINDOW", DestroyMAScreen)
    
        MAca = Canvas(mawindow, width=MGRW, height=MGRH, background=COLORcanvas)
        MAca.bind("<Configure>", MACaresize)
        MAca.pack(side=TOP, expand=YES, fill=BOTH)
# MAca.bind("<Return>", DoNothing)
        MAca.bind("<space>", onCanvasSpaceBar)
        if DialSpan > 359:
            DialSpan = 355
        DialStart = 360 - ((DialSpan-180)/2)
        DialCenter = 0.15 * MRadius
        MAca.create_arc(MXcenter-MRadius, MYcenter+MRadius, MXcenter+MRadius, MYcenter-MRadius, start=DialStart, extent=DialSpan, outline=COLORgrid, fill=COLORdial, width=GridWidth.get())
        MAca.create_arc(MXcenter-DialCenter, MYcenter+DialCenter, MXcenter+DialCenter, MYcenter-DialCenter, start=DialStart, extent=DialSpan, outline="blue", fill="blue", width=GridWidth.get())
        if Mmin >= Mmax:
            Mmax = Mmin + 0.1
            MeterMaxEntry.delete(0,END)
            MeterMaxEntry.insert(0, Mmax)
        MScale = Mmax - Mmin
        DialStart = 90 + (DialSpan/2)
        for tick in range(MajorDiv+1):
            TIradius = 1.1 * MRadius
            TOradius = 1.2 * MRadius
            Angle = DialStart - ((DialSpan*tick)/MajorDiv)
            NextAngle = DialStart - ((DialSpan*(tick+1))/MajorDiv)
            MinorTickStep = (Angle - NextAngle)/5.0
            RAngle = math.radians(Angle)
            y = MRadius*math.sin(RAngle)
            x = MRadius*math.cos(RAngle)
            yi = TIradius*math.sin(RAngle)
            xi = TIradius*math.cos(RAngle) 
            yt = TOradius*math.sin(RAngle)
            xt = TOradius*math.cos(RAngle)
            if Angle > 270:
                y = 0 - y
                yi = 0 - yi
                yt = 0 - yt
            #Draw Major Tick
            MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
            # Add Text Label
            Increment = MajorDiv/MScale
            axis_value = float((tick/Increment)+Mmin)
            # axis_label = '{0:.2f}'.format(axis_value)
            axis_label = str(round(axis_value,2 ))
            # axis_label = str(axis_value)
            MAca.create_text(MXcenter+xt, MYcenter-yt, text = axis_label, fill=COLORtext, font=("arial", FontSize ))
            # Add minor Ticks
            TIradius = 1.05 * MRadius
            if tick < MajorDiv:
                for minor in range(MinorDiv-1):
                    MinorAngle = Angle-((minor+1)*MinorTickStep)
                    RAngle = math.radians(MinorAngle)
                    y = MRadius*math.sin(RAngle)
                    x = MRadius*math.cos(RAngle)
                    yi = TIradius*math.sin(RAngle)
                    xi = TIradius*math.cos(RAngle)
                    if MinorAngle > 270:
                        y = 0 - y
                        yi = 0 - yi
                    #Draw Minor Tick
                    MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())

        MeterLabel = MAca.create_text(MXcenter-MRadius/2,MYcenter+MRadius/2, text = MeterLabelText, fill=COLORtext, font=("arial", FontSize+4 ))
        
        IndicatorA = MAca.create_line(MXcenter, MYcenter, MXcenter+x, MYcenter-y, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
        IndicatorB = IndicatorC = IndicatorD = IndicatorM = IndicatorMX = IndicatorMY = IndicatorA
        VString = ' {0:.4f} '.format(0.0) # format with 4 decimal places
        TextX = MXcenter - MRadius
        TextY = MYcenter + MRadius
        if CHANNELS >= 1:
            ValueDisA = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace1, font=("arial", FontSize+4 ))
        if CHANNELS >= 2:
            TextY = TextY + FontSize + 5
            ValueDisB = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace2, font=("arial", FontSize+4 ))
        if CHANNELS >= 3:
            TextY = TextY + FontSize + 5
            ValueDisC = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace3, font=("arial", FontSize+4 ))
        if CHANNELS >= 4:
            TextY = TextY + FontSize + 5
            ValueDisD = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace4, font=("arial", FontSize+4 ))
        TextX = TextX + 7 * FontSize
        TextY = MYcenter + MRadius
        ValueDisM = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace5, font=("arial", FontSize+4 ))
        TextY = TextY + FontSize + 5
        ValueDisMX = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace6, font=("arial", FontSize+4 ))
        TextY = TextY + FontSize + 5
        ValueDisMXY = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace7, font=("arial", FontSize+4 ))
#
def DestroyMAScreen():
    global mawindow, MAScreenStatus #, MAca, MADisp

    MAScreenStatus.set(0)
    mawindow.destroy()
#
def Update_Analog_Meter(ValueA, ValueB, ValueC, ValueD, ValueM, ValueMX, ValueMY):
    global MXcenter, MYcenter, MRadius, MAca, MGRW, MGRH
    global ShowC1_V, ShowC2_V, ShowC3_V, ShowC4_V
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, TRACEwidth, GridWidth, FontSize
    global Mmin, Mmax, MajorDiv, DialSpan, MeterMaxEntry
    global IndicatorA, IndicatorB, ValueDisA, ValueDisB, CHANNELS
    global IndicatorC, IndicatorD, ValueDisC, ValueDisD
    global IndicatorM, IndicatorMX, IndicatorMY
    global ValueDisM, ValueDisMX, ValueDisMY
    global MathTrace, Show_MathX, Show_MathY, YsignalMX, YsignalMY
    
    if Mmin >= Mmax:
        Mmax = Mmin + 0.1
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    MScale = Mmax - Mmin
    DialStart = 90 + (DialSpan/2)
    Tradius = 1.0 * MRadius
    try:
        MAca.delete(IndicatorA) # remove old lines
        MAca.delete(ValueDisA)# remove old text
    except:
        pass
    try:
        MAca.delete(IndicatorB)
        MAca.delete(ValueDisB)
    except:
        pass
    try:
        MAca.delete(IndicatorC)
        MAca.delete(ValueDisC)
    except:
        pass
    try:
        MAca.delete(IndicatorD)
        MAca.delete(ValueDisD)
    except:
        pass
    try:
        MAca.delete(IndicatorM)
        MAca.delete(ValueDisM)
    except:
        pass
    try:
        MAca.delete(IndicatorMX)
        MAca.delete(ValueDisMX)
    except:
        pass
    try:
        MAca.delete(IndicatorMY)
        MAca.delete(ValueDisMY)
    except:
        pass
    TextX = MXcenter - MRadius
    TextY = MYcenter + MRadius
    if ShowC1_V.get() > 0 and CHANNELS >= 1:
        Angle = DialStart - ((DialSpan*(ValueA-Mmin))/MScale) # calculate angle of CHA indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        ya = Tradius*math.sin(RAngle) # convert angle to x y position
        xa = Tradius*math.cos(RAngle)
        if Angle > 270:
            ya = 0 - ya
        IndicatorA = MAca.create_line(MXcenter, MYcenter, MXcenter+xa, MYcenter-ya, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueA) # format with 4 decimal places
        ValueDisA = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace1, font=("arial", FontSize+4 ))
    if ShowC2_V.get() > 0 and CHANNELS >= 2:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueB-Mmin))/MScale) # calculate angle of CHB indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yb = Tradius*math.sin(RAngle) # convert angle to x y position
        xb = Tradius*math.cos(RAngle)
        if Angle > 270:
            yb = 0 - yb
        IndicatorB = MAca.create_line(MXcenter, MYcenter, MXcenter+xb, MYcenter-yb, fill=COLORtrace2, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueB) # format with 4 decimal places
        ValueDisB = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace2, font=("arial", FontSize+4 ))
    if ShowC3_V.get() > 0 and CHANNELS >= 3:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueC-Mmin))/MScale) # calculate angle of CHC indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yc = Tradius*math.sin(RAngle) # convert angle to x y position
        xc = Tradius*math.cos(RAngle)
        if Angle > 270:
            yc = 0 - yc
        IndicatorC = MAca.create_line(MXcenter, MYcenter, MXcenter+xc, MYcenter-yc, fill=COLORtrace3, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueC) # format with 4 decimal places
        ValueDisC = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace3, font=("arial", FontSize+4 ))
    if ShowC4_V.get() > 0 and CHANNELS >= 4:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueD-Mmin))/MScale) # calculate angle of CHD indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorD = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace4, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueD) # format with 4 decimal places
        ValueDisD = MAca.create_text(TextX, TextY , text = VString, fill=COLORtrace4, font=("arial", FontSize+4 ))
    TextX = TextX + 7 * FontSize
    TextY = MYcenter + MRadius
    if MathTrace.get() > 0:
        Angle = DialStart - ((DialSpan*(ValueM-Mmin))/MScale) # calculate angle of Math indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorM = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace5, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueM) # format with 4 decimal places
        ValueDisM = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace5, font=("arial", FontSize+4 ))
    if Show_MathX.get() > 0 or YsignalMX.get() == 1:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueMX-Mmin))/MScale) # calculate angle of Math indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorMX = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace6, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueMX) # format with 4 decimal places
        ValueDisMX = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace6, font=("arial", FontSize+4 ))
    if Show_MathY.get() > 0 or YsignalMY.get() == 1:
        TextY = TextY + FontSize + 5
        Angle = DialStart - ((DialSpan*(ValueMY-Mmin))/MScale) # calculate angle of Math indicator
        if Angle < 0.0:
            Angle = 360 - Angle
        RAngle = math.radians(Angle)
        yd = Tradius*math.sin(RAngle) # convert angle to x y position
        xd = Tradius*math.cos(RAngle)
        if Angle > 270:
            yd = 0 - yd
        IndicatorMY = MAca.create_line(MXcenter, MYcenter, MXcenter+xd, MYcenter-yd, fill=COLORtrace7, arrow="last", width=TRACEwidth.get())
        VString = ' {0:.4f} '.format(ValueMY) # format with 4 decimal places
        ValueDisMY = MAca.create_text(TextX, TextY, text = VString, fill=COLORtrace7, font=("arial", FontSize+4 ))
#
# Resize Analog Meter window
def MACaresize(event):
    global MAca, MGRW, MGRH, CANVASwidthMA, CANVASheightMA, FontSize
    global MXcenter, MYcenter, MRadius, COLORdial, MeterMinEntry, MeterMaxEntry
    global IndicatorA, IndicatorB, COLORtrace1, COLORtrace2, COLORtext, TRACEwidth, GridWidth
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel 
     
    CANVASwidthMA = event.width - 4
    CANVASheightMA = event.height - 4
    MGRW = CANVASwidthMA # 170 new grid width
    MGRH = CANVASheightMA  # 10 new grid height
    MXcenter = int(MGRW/2.0)   # Meter Center
    MYcenter = int(MGRH/2.0)
    MRadius = MXcenter - 50    # Meter Radius
    MakeMeterDial()
#
def MakeMeterDial():
    global MAca, MGRW, MGRH, CANVASwidthMA, CANVASheightMA, FontSize
    global MXcenter, MYcenter, MRadius, COLORdial, MeterMinEntry, MeterMaxEntry
    global IndicatorA, IndicatorB, COLORtrace1, COLORtrace2, COLORtext, TRACEwidth, GridWidth
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel, DialSpan
    
    # Re make meter dial
    MAca.delete(ALL) # remove all items
    if DialSpan > 359:
        DialSpan = 355
    DialStart = 360 - ((DialSpan-180)/2)
    DialCenter = 0.15 * MRadius
    MAca.create_arc(MXcenter-MRadius, MYcenter+MRadius, MXcenter+MRadius, MYcenter-MRadius, start=DialStart, extent=DialSpan, outline=COLORgrid, fill=COLORdial, width=GridWidth.get())
    MAca.create_arc(MXcenter-DialCenter, MYcenter+DialCenter, MXcenter+DialCenter, MYcenter-DialCenter, start=DialStart, extent=DialSpan, outline="blue", fill="blue", width=GridWidth.get())
#
    try:
        Mmin = float(eval(MeterMinEntry.get()))
    except:
        MeterMinEntry.delete(0,END)
        MeterMinEntry.insert(0, Mmin)
    try:
        Mmax = float(eval(MeterMaxEntry.get()))
    except:
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    if Mmin >= Mmax:
        Mmax = Mmin + 0.1
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    MScale = Mmax - Mmin
    DialStart = 90.0 + (DialSpan/2.0)
    for tick in range(MajorDiv+1):
        TIradius = 1.1 * MRadius
        TOradius = 1.2 * MRadius
        Angle = DialStart - ((DialSpan*tick)/MajorDiv)
        NextAngle = DialStart - ((DialSpan*(tick+1))/MajorDiv)
        MinorTickStep = (Angle - NextAngle)/5.0
        RAngle = math.radians(Angle)
        y = MRadius*math.sin(RAngle)
        x = MRadius*math.cos(RAngle)
        yi = TIradius*math.sin(RAngle)
        xi = TIradius*math.cos(RAngle) 
        yt = TOradius*math.sin(RAngle)
        xt = TOradius*math.cos(RAngle)
        if Angle > 270:
            y = 0 - y
            yi = 0 - yi
            yt = 0 - yt
        #Draw Major Tick
        MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
        # Add Text Label
        Increment = MajorDiv/MScale
        axis_value = float((tick/Increment)+Mmin)
        axis_label = str(round(axis_value,2 ))
        # axis_label = str(axis_value)
        MAca.create_text(MXcenter+xt, MYcenter-yt, text = axis_label, fill=COLORtext, font=("arial", FontSize ))
        # Add minor Ticks
        TIradius = 1.05 * MRadius
        if tick < MajorDiv:
            for minor in range(MinorDiv-1):
                MinorAngle = Angle-((minor+1)*MinorTickStep)
                RAngle = math.radians(MinorAngle)
                y = MRadius*math.sin(RAngle)
                x = MRadius*math.cos(RAngle)
                yi = TIradius*math.sin(RAngle)
                xi = TIradius*math.cos(RAngle)
                if MinorAngle > 270:
                    y = 0 - y
                    yi = 0 - yi
                #Draw Minor Tick
                MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
        MeterLabel = MAca.create_text(MXcenter, MYcenter+MRadius/2, text = MeterLabelText, fill=COLORtext, font=("arial", FontSize+4 ))
#
def onMeterMinMax(event):
    onTextScroll(event)
    MakeMeterDial()
#
def onKeyMinMax(event):
    onTextKey(event)
    MakeMeterDial()
#
def ReSetAGO():
    global CHAVGainEntry, CHAVOffsetEntry

    CHAVGainEntry.delete(0,"end")
    CHAVGainEntry.insert(0,1.0)
    CHAVOffsetEntry.delete(0,"end")
    CHAVOffsetEntry.insert(0,0.0)
#
def ReSetBGO():
    global CHBVGainEntry, CHBVOffsetEntry

    CHBVGainEntry.delete(0,"end")
    CHBVGainEntry.insert(0,1.0)
    CHBVOffsetEntry.delete(0,"end")
    CHBVOffsetEntry.insert(0,0.0)
#
def ReSetCGO():
    global CHCVGainEntry, CHCVOffsetEntry

    CHCVGainEntry.delete(0,"end")
    CHCVGainEntry.insert(0,1.0)
    CHCVOffsetEntry.delete(0,"end")
    CHCVOffsetEntry.insert(0,0.0)
#
def ReSetDGO():
    global CHDVGainEntry, CHDVOffsetEntry

    CHDVGainEntry.delete(0,"end")
    CHDVGainEntry.insert(0,1.0)
    CHDVOffsetEntry.delete(0,"end")
    CHDVOffsetEntry.insert(0,0.0)
#
def MakeMeterWindow():
    global DMMStatus, DMMDisp, dmmwindow, DMMRunStatus, Mmax, Mmin, dlog
    global SWRev, RevDate, InGainA, InOffA, InGainB, InOffB, DmmLabel1
    global InGainC, InOffC, InGainD, InOffD, DmmLabel2, DmmLabel3, DmmLabel4
    global MeterMaxEntry, MeterMinEntry, MeterMinlab, MeterMaxlab, CHANNELS
    global MeterAGainEntry, MeterBGainEntry, MeterAOffsetEntry, MeterBOffsetEntry
    global MeterCGainEntry, MeterDGainEntry, MeterCOffsetEntry, MeterDOffsetEntry
#
    if DMMStatus.get() == 0:
        DMMStatus.set(1)
        DMMDisp.set(1)
        DMMCheckBox()
        dmmwindow = Toplevel()
        dmmwindow.title("Analog Meter " + SWRev + RevDate)
        framet = Frame(dmmwindow, borderwidth=BorderSize, relief=FrameRelief)
        framet.grid(row=0, column=0, sticky=W)
        Grow = 1
        DmmLabel1 = Label(framet, font = "Arial 16 bold")
        DmmLabel1.grid(row=Grow, columnspan=3, sticky=W)
        DmmLabel1.config(text = "A Volts B Volts")
        if CHANNELS >= 3:
            Grow = Grow + 1
            DmmLabel2 = Label(framet, font = "Arial 16 bold")
            DmmLabel2.grid(row=Grow, columnspan=3, sticky=W)
            DmmLabel2.config(text = "C Volts D Volts")
        Grow = Grow + 1
        DmmLabel3 = Label(framet, font = "Arial 16 bold")
        DmmLabel3.grid(row=Grow, columnspan=3, sticky=W)
        DmmLabel3.config(text = "Math")
        Grow = Grow + 1
        DmmLabel4 = Label(framet, font = "Arial 16 bold")
        DmmLabel4.grid(row=Grow, columnspan=3, sticky=W)
        DmmLabel4.config(text = "MathX MathY")
        Grow = Grow + 1
        frame0 = Frame( framet )
        frame0.grid(row=Grow, column=0, sticky=W)
        rb1 = Radiobutton(frame0, text="Stop", style="Stop.TRadiobutton", variable=DMMRunStatus, value=0, command=BStop )
        rb1.pack(side=LEFT)#.grid(row=2, column=0, sticky=W)
        rb2 = Radiobutton(frame0, text="Run", style="Run.TRadiobutton", variable=DMMRunStatus, value=1, command=BStart )
        rb2.pack(side=LEFT)#.grid(row=2, column=1, sticky=W)
        # Entry inputs for Meter Min and Max
        Grow = Grow + 1
        frame1 = Frame( framet )
        frame1.grid(row=Grow, column=0, sticky=W)
        MeterMinEntry = Entry(frame1, width=5, cursor='double_arrow')
        #MeterMinEntry.bind("<Return>", BOffsetA)
        MeterMinEntry.bind('<MouseWheel>', onMeterMinMax)# with Windows OS
        MeterMinEntry.bind("<Button-4>", onMeterMinMax)# with Linux OS
        MeterMinEntry.bind("<Button-5>", onMeterMinMax)
        MeterMinEntry.bind('<Key>', onKeyMinMax)
        MeterMinEntry.pack(side=LEFT)
        MeterMinEntry.delete(0,"end")
        MeterMinEntry.insert(0,Mmin)
        MeterMinlab = Button(frame1, text="Meter Min", style="W9.TButton", command=donothing)# SetVAPoss)
        MeterMinlab.pack(side=LEFT)
        #
        MeterMaxEntry = Entry(frame1, width=5, cursor='double_arrow')
        #MeterMaxEntry.bind("<Return>", BOffsetA)
        MeterMaxEntry.bind('<MouseWheel>', onMeterMinMax)# with Windows OS
        MeterMaxEntry.bind("<Button-4>", onMeterMinMax)# with Linux OS
        MeterMaxEntry.bind("<Button-5>", onMeterMinMax)
        MeterMaxEntry.bind('<Key>', onKeyMinMax)
        MeterMaxEntry.pack(side=LEFT)
        MeterMaxEntry.delete(0,"end")
        MeterMaxEntry.insert(0,Mmax)
        MeterMaxlab = Button(frame1, text="Meter Max", style="W9.TButton", command=donothing)# SetVAPoss)
        MeterMaxlab.pack(side=LEFT)
        #
        # Define Analog Meter display
        Build_meter()
        Grow = Grow + 1
        dlcheck = Checkbutton(framet, text="DLog to file", variable=dlog, command=Dloger_on_off)
        dlcheck.grid(row=Grow, column=0, sticky=W, pady=7)
        Grow = Grow + 1
        dmmdismissclbutton = Button(framet, text="Dismiss", style="W8.TButton", command=DestroyDMMScreen)
        dmmdismissclbutton.grid(row=Grow, column=0, sticky=W, pady=7)
#
def DestroyDMMScreen():
    global dmmwindow, DMMStatus, DMMDisp
    
    DMMStatus.set(0)
    DMMDisp.set(0)
    DMMCheckBox()
    DestroyMAScreen()
    dmmwindow.destroy()
#
#
def MakeOhmWindow():
    global OhmDisp, OhmStatus, ohmwindow, RevDate, RMode, OhmA0, OhmA1, OhmRunStatus
    global CHATestVEntry, CHATestREntry, SWRev, OnBoardRes
    global FrameRelief, BorderSize, OhmSche, Rint, CHBIntREntry
    
    if OhmStatus.get() == 0:
        OhmStatus.set(1)
        OhmDisp.set(1)
        RMode = IntVar()
        RMode.set(0)
        OhmCheckBox()
        ohmwindow = Toplevel()
        ohmwindow.title("DC Ohmmeter " + SWRev + RevDate)
        ohmwindow.resizable(FALSE,FALSE)
        ohmwindow.protocol("WM_DELETE_WINDOW", DestroyOhmScreen)
        frame1 = Frame(ohmwindow, borderwidth=BorderSize, relief=FrameRelief)
        frame1.grid(row=0, column=0, sticky=W)
        #
        buttons = Frame( frame1 )
        buttons.grid(row=0, column=0, sticky=W)
        omrb2 = Radiobutton(buttons, text="Run", style="Run.TRadiobutton", variable=OhmRunStatus, value=1, command=BStart )
        omrb2.pack(side=LEFT)
        omrb1 = Radiobutton(buttons, text="Stop", style="Stop.TRadiobutton", variable=OhmRunStatus, value=0, command=BStop )
        omrb1.pack(side=LEFT)
        #
        OhmA0 = Label(frame1, style="A16B.TLabel") # , font = "Arial 16 bold")
        OhmA0.grid(row=1, column=0, columnspan=2, sticky=W)
        OhmA0.config(text = "0.000 Ohms")

        OhmA1 = Label(frame1, style="A12B.TLabel") #, font = "Arial 12 bold")
        OhmA1.grid(row=2, column=0, columnspan=2, sticky=W)
        OhmA1.config(text = "Meas 0.000 V")
        #
        TestVA = Frame( frame1 )
        TestVA.grid(row=3, column=0, sticky=W)
        chatestvlab = Label(TestVA, text="Test Voltage", style="A10B.TLabel") #, font = "Arial 10 bold")
        chatestvlab.pack(side=LEFT)
        CHATestVEntry = Entry(TestVA, width=6, cursor='double_arrow') #
        CHATestVEntry.pack(side=LEFT)
        CHATestVEntry.bind('<MouseWheel>', onTextScroll)
        CHATestVEntry.bind("<Button-4>", onTextScroll)# with Linux OS
        CHATestVEntry.bind("<Button-5>", onTextScroll)
        CHATestVEntry.delete(0,"end")
        CHATestVEntry.insert(0,4.0)
        #
        TestRA = Frame( frame1 )
        TestRA.grid(row=5, column=0, sticky=W)
        chatestrlab = Label(TestRA, text="Known Res", style="A10B.TLabel") #, font = "Arial 10 bold")
        chatestrlab.pack(side=LEFT)
        CHATestREntry = Entry(TestRA, width=7, cursor='double_arrow') #
        CHATestREntry.pack(side=LEFT)
        CHATestREntry.bind('<MouseWheel>', onTextScroll)
        CHATestREntry.bind("<Button-4>", onTextScroll)# with Linux OS
        CHATestREntry.bind("<Button-5>", onTextScroll)
        CHATestREntry.delete(0,"end")
        CHATestREntry.insert(0,OnBoardRes)
        #
        #
        IntRB = Frame( frame1 )
        IntRB.grid(row=6, column=0, sticky=W)
        intrblab = Label(IntRB, text="CHB Int Res", style="A10B.TLabel") #, font = "Arial 10 bold")
        intrblab.pack(side=LEFT)
        CHBIntREntry = Entry(IntRB, width=8, cursor='double_arrow') #
        CHBIntREntry.pack(side=LEFT)
        CHBIntREntry.bind('<MouseWheel>', onTextScroll)
        CHBIntREntry.bind("<Button-4>", onTextScroll)# with Linux OS
        CHBIntREntry.bind("<Button-5>", onTextScroll)
        CHBIntREntry.delete(0,"end")
        CHBIntREntry.insert(0,Rint)
        #
        ohmdismissclbutton = Button(frame1, text="Dismiss", style="W8.TButton", command=DestroyOhmScreen)
        ohmdismissclbutton.grid(row=7, column=0, sticky=W, pady=7)
## Draw Schematic
        OhmSche = Canvas(frame1, width=210, height=220, background=COLORwhite)
        OhmSche.grid(row = 0, rowspan = 7, column = 2, sticky=W)
        #
        DrawOhmSchem()
#
def DrawOhmSchem():
    global RMode, OhmSche

    # Delete all items on the screen
    OhmSche.delete(ALL) # remove all items

    OhmSche.create_text(100, 9, text = "Connections", fill=COLORblack, font=("arial", FontSize+6 ))
    ResW = 10
    X = 40
    Y = 30
    DrawRes(X, Y, ResW, OhmSche)
    OhmSche.create_rectangle(X+38, Y-10, 122, Y+10, width=3) #
    OhmSche.create_line(X, Y, X+38, Y, fill=COLORblack, width=3)
    OhmSche.create_text(100, Y, text = "CH A", fill=COLORblack, font=("arial", FontSize+4 ))
    Y = 110
    OhmSche.create_line(X, Y, X+38, Y, fill=COLORblack, width=3)
    OhmSche.create_rectangle(X+38, Y-10, 122, Y+10, width=3) #
    OhmSche.create_text(100, Y, text = "CH B", fill=COLORblack, font=("arial", FontSize+4 ))
    Y = 190
    OhmSche.create_rectangle(X+38, Y-10, 122, Y+10, width=3) #
    OhmSche.create_text(100, Y, text = "GND", fill=COLORblack, font=("arial", FontSize+4 ))
    if RMode.get() == 0: # When using external known resistor
        #
        X = 40
        Y = 30
        OhmSche.create_text(X+15, Y+40, text = "Rknown", fill=COLORblack, anchor="w", font=("arial", FontSize+4 ))
        #
        Y = 110
        OhmSche.create_text(X+15, Y+40, text = "Rtest", fill=COLORblack, anchor="w", font=("arial", FontSize+4 ))
        DrawRes(X, Y, ResW, OhmSche)
        OhmSche.create_line(X, Y, X+38, Y, fill=COLORblack, width=3)
        Y = 190
        OhmSche.create_line(X, Y, X+38, Y, fill=COLORblack, width=3)
        #
    else: # When using int 50 ohm resistor
        X = 40
        Y = 30
        OhmSche.create_text(X+15, Y+40, text = "Rtest", fill=COLORblack, anchor="w", font=("arial", FontSize+4 ))
        Y = 110
        OhmSche.create_line(122, Y, 160, Y, fill=COLORblack, width=3)
        X = 160
        DrawRes(X, Y, ResW, OhmSche)
        #
        Y = 190
        OhmSche.create_line(122, Y, 160, Y, fill=COLORblack, width=3)
        #
        OhmSche.create_text(180, 140, text = "Rint", fill=COLORblack, anchor="w", font=("arial", FontSize+4 ))
        OhmSche.create_text(180, 160, text = "50", fill=COLORblack, anchor="w", font=("arial", FontSize+4 ))
#
def DestroyOhmScreen():
    global ohmwindow, OhmStatus, OhmDisp
    
    OhmStatus.set(0)
    OhmDisp.set(0)
    OhmCheckBox()
    ohmwindow.destroy()
#
def Settingsscroll(event):
    onTextScroll(event)
    SettingsUpdate()
#
def SettingsTextKey(event):
    onTextKey(event)
    SettingsUpdate()
#
def BuffSZscroll(event):
    onTextScroll(event)
    BuffSZUpdate()
#
def BuffSZTextKey(event):
    onTextKey(event)
    BuffSZUpdate()
#
def BuffSZUpdate():
    global BuffSZ
    
    try:
        NewLength = int(eval(BuffSZ.get()))
        if NewLength > HardwareBuffer:
            NewLength = HardwareBuffer
            BuffSZ.delete(0,END)
            BuffSZ.insert(0, int(NewLength))
        if NewLength <= 1:
            NewLength = HardwareBuffer
            BuffSZ.delete(0,END)
            BuffSZ.insert(0, int(NewLength))
        SetBufferLength(NewLength)
    except:
        pass
##
def MakeSettingsMenu():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon
    global AWG_Amp_Mode, SWRev, HardwareBuffer, BuffSZ
    global TrgLPFEntry, Trigger_LPF_length
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global CHC_RC_HP, CHD_RC_HP, CHC_TC1, CHC_TC2, CHD_TC1, CHD_TC2
    global CHC_A1, CHC_A2, CHD_A1, CHD_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global chc_TC1Entry, chc_TC2Entry, chd_TC1Entry, chd_TC2Entry
    global chc_A1Entry, chc_A2Entry, chd_A1Entry, chd_A2Entry
    global FrameRelief, BorderSize

    if SettingsStatus.get() == 0:
        SettingsStatus.set(1)
        Settingswindow = Toplevel()
        Settingswindow.title("Settings " + SWRev + RevDate)
        Settingswindow.resizable(FALSE,FALSE)
        Settingswindow.protocol("WM_DELETE_WINDOW", DestroySettings)
        frame1 = Frame(Settingswindow, borderwidth=BorderSize, relief=FrameRelief)
        frame1.grid(row=0, column=0, sticky=W)
        #
        Row = 0
        if HardwareBuffer > 0:
            bfszlab = Label(frame1, text="Capture Buffer Size", style= "A10B.TLabel")
            bfszlab.grid(row=Row, column=0, sticky=W)
            bfszMode = Frame( frame1 )
            bfszMode.grid(row=Row, column=1, sticky=W)
            BuffSZ = Entry(bfszMode, width=6, cursor='double_arrow')
            BuffSZ.bind("<Return>", BuffSZTextKey)
            BuffSZ.bind('<MouseWheel>', BuffSZscroll)
            BuffSZ.bind("<Button-4>", BuffSZscroll)# with Linux OS
            BuffSZ.bind("<Button-5>", BuffSZscroll)
            BuffSZ.bind('<Key>', BuffSZTextKey)
            BuffSZ.pack(side=RIGHT)
            BuffSZ.delete(0,"end")
            BuffSZ.insert(0,HardwareBuffer)
            #
            Row = Row + 1
        zstlab = Label(frame1, text="FFT Zero Stuffing", style= "A10B.TLabel")
        zstlab.grid(row=Row, column=0, sticky=W)
        zstMode = Frame( frame1 )
        zstMode.grid(row=Row, column=1, sticky=W)
        ZSTuff = Entry(zstMode, width=4, cursor='double_arrow')
        ZSTuff.bind("<Return>", SettingsTextKey)
        ZSTuff.bind('<MouseWheel>', Settingsscroll)
        ZSTuff.bind("<Button-4>", Settingsscroll)# with Linux OS
        ZSTuff.bind("<Button-5>", Settingsscroll)
        ZSTuff.bind('<Key>', SettingsTextKey)
        ZSTuff.pack(side=RIGHT)
        ZSTuff.delete(0,"end")
        ZSTuff.insert(0,ZEROstuffing.get())
        #
        Row = Row + 1
        Avglab = Label(frame1, text="Number Traces to Average", style= "A10B.TLabel")
        Avglab.grid(row=Row, column=0, sticky=W)
        AvgMode = Frame( frame1 )
        AvgMode.grid(row=Row, column=1, sticky=W)
        TAvg = Entry(AvgMode, width=4, cursor='double_arrow')
        TAvg.bind("<Return>", SettingsTextKey)
        TAvg.bind('<MouseWheel>', Settingsscroll)
        TAvg.bind("<Button-4>", Settingsscroll)# with Linux OS
        TAvg.bind("<Button-5>", Settingsscroll)
        TAvg.bind('<Key>', SettingsTextKey)
        TAvg.pack(side=RIGHT)
        TAvg.delete(0,"end")
        TAvg.insert(0,TRACEaverage.get())
        #
        Row = Row + 1
        HarMlab = Label(frame1, text="Number of Harmonic Markers", style= "A10B.TLabel")
        HarMlab.grid(row=Row, column=0, sticky=W)
        HarMMode = Frame( frame1 )
        HarMMode.grid(row=Row, column=1, sticky=W)
        HarMon = Entry(HarMMode, width=4, cursor='double_arrow')
        HarMon.bind("<Return>", SettingsTextKey)
        HarMon.bind('<MouseWheel>', Settingsscroll)
        HarMon.bind("<Button-4>", Settingsscroll)# with Linux OS
        HarMon.bind("<Button-5>", Settingsscroll)
        HarMon.bind('<Key>', SettingsTextKey)
        HarMon.pack(side=RIGHT)
        HarMon.delete(0,"end")
        HarMon.insert(0,HarmonicMarkers.get())
        #
        Row = Row + 1
        Vdivlab = Label(frame1, text="Number Vertical Div (SA, Bode)", style= "A10B.TLabel")
        Vdivlab.grid(row=Row, column=0, sticky=W)
        VdivMode = Frame( frame1 )
        VdivMode.grid(row=Row, column=1, sticky=W)
        VDivE = Entry(VdivMode, width=4, cursor='double_arrow')
        VDivE.bind("<Return>", SettingsTextKey)
        VDivE.bind('<MouseWheel>', Settingsscroll)
        VDivE.bind("<Button-4>", Settingsscroll)# with Linux OS
        VDivE.bind("<Button-5>", Settingsscroll)
        VDivE.bind('<Key>', SettingsTextKey)
        VDivE.pack(side=RIGHT)
        VDivE.delete(0,"end")
        VDivE.insert(0,Vdiv.get())
        #
        Row = Row + 1
        Twdthlab = Label(frame1, text="Trace Width in Pixels", style= "A10B.TLabel")
        Twdthlab.grid(row=Row, column=0, sticky=W)
        TwdthMode = Frame( frame1 )
        TwdthMode.grid(row=Row, column=1, sticky=W)
        TwdthE = Entry(TwdthMode, width=4, cursor='double_arrow')
        TwdthE.bind("<Return>", SettingsTextKey)
        TwdthE.bind('<MouseWheel>', Settingsscroll)
        TwdthE.bind("<Button-4>", Settingsscroll)# with Linux OS
        TwdthE.bind("<Button-5>", Settingsscroll)
        TwdthE.bind('<Key>', SettingsTextKey)
        TwdthE.pack(side=RIGHT)
        TwdthE.delete(0,"end")
        TwdthE.insert(0,TRACEwidth.get())
        #
        Row = Row + 1
        Gwdthlab = Label(frame1, text="Grid Width in Pixels", style= "A10B.TLabel")
        Gwdthlab.grid(row=Row, column=0, sticky=W)
        GwdthMode = Frame( frame1 )
        GwdthMode.grid(row=Row, column=1, sticky=W)
        GwdthE = Entry(GwdthMode, width=4, cursor='double_arrow')
        GwdthE.bind("<Return>", SettingsTextKey)
        GwdthE.bind('<MouseWheel>', Settingsscroll)
        GwdthE.bind("<Button-4>", Settingsscroll)# with Linux OS
        GwdthE.bind("<Button-5>", Settingsscroll)
        GwdthE.bind('<Key>', SettingsTextKey)
        GwdthE.pack(side=RIGHT)
        GwdthE.delete(0,"end")
        GwdthE.insert(0,GridWidth.get())
        #
        Row = Row + 1
        AwgAmplrb1 = Radiobutton(frame1, text="AWG Min/Max", variable=AWG_Amp_Mode, value=0, command=UpdateAWGWin)
        AwgAmplrb1.grid(row=Row, column=0, sticky=W)
        AwgAmplrb2 = Radiobutton(frame1, text="AWG Amp/Off ", variable=AWG_Amp_Mode, value=1, command=UpdateAWGWin)
        AwgAmplrb2.grid(row=Row, column=1, sticky=W)
        #
        if CHANNELS >= 1:
            Row = Row + 1
            cha_Rcomplab = Label(frame1, text="CHA Comp, TC1 (uSec), A1", style= "A10B.TLabel") # in micro seconds
            cha_Rcomplab.grid(row=Row, column=0, sticky=W)
            cha_RcomplabMode = Frame( frame1 )
            cha_RcomplabMode.grid(row=Row, column=1, sticky=W)
            cha_TC1Entry = Entry(cha_RcomplabMode, width=5, cursor='double_arrow')
            cha_TC1Entry.bind("<Return>", SettingsTextKey)
            cha_TC1Entry.bind('<MouseWheel>', Settingsscroll)
            cha_TC1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            cha_TC1Entry.bind("<Button-5>", Settingsscroll)
            cha_TC1Entry.bind('<Key>', SettingsTextKey)
            cha_TC1Entry.pack(side=LEFT)
            cha_TC1Entry.delete(0,"end")
            cha_TC1Entry.insert(0,CHA_TC1.get())
            cha_A1Entry = Entry(cha_RcomplabMode, width=5, cursor='double_arrow')
            cha_A1Entry.bind("<Return>", SettingsTextKey)
            cha_A1Entry.bind('<MouseWheel>', Settingsscroll)
            cha_A1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            cha_A1Entry.bind("<Button-5>", Settingsscroll)
            cha_A1Entry.bind('<Key>', SettingsTextKey)
            cha_A1Entry.pack(side=LEFT)
            cha_A1Entry.delete(0,"end")
            cha_A1Entry.insert(0,CHA_A1.get())
        #
            Row = Row + 1
            cha_Ccomplab = Label(frame1, text="CHA Comp, TC2 (uSec), A2", style= "A10B.TLabel") # in micro seconds
            cha_Ccomplab.grid(row=Row, column=0, sticky=W)
            cha_CcomplabMode = Frame( frame1 )
            cha_CcomplabMode.grid(row=Row, column=1, sticky=W)
            cha_TC2Entry = Entry(cha_CcomplabMode, width=5, cursor='double_arrow')
            cha_TC2Entry.bind("<Return>", SettingsTextKey)
            cha_TC2Entry.bind('<MouseWheel>', Settingsscroll)
            cha_TC2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            cha_TC2Entry.bind("<Button-5>", Settingsscroll)
            cha_TC2Entry.bind('<Key>', SettingsTextKey)
            cha_TC2Entry.pack(side=LEFT)
            cha_TC2Entry.delete(0,"end")
            cha_TC2Entry.insert(0,CHA_TC2.get())
            cha_A2Entry = Entry(cha_CcomplabMode, width=5, cursor='double_arrow')
            cha_A2Entry.bind("<Return>", SettingsTextKey)
            cha_A2Entry.bind('<MouseWheel>', Settingsscroll)
            cha_A2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            cha_A2Entry.bind("<Button-5>", Settingsscroll)
            cha_A2Entry.bind('<Key>', SettingsTextKey)
            cha_A2Entry.pack(side=LEFT)
            cha_A2Entry.delete(0,"end")
            cha_A2Entry.insert(0,CHA_A2.get())
        #
        if CHANNELS >= 2:
            Row = Row + 1
            chb_Rcomplab = Label(frame1, text="CHB Comp, TC1 (uSec), A1", style= "A10B.TLabel") # in micro seconds
            chb_Rcomplab.grid(row=Row, column=0, sticky=W)
            chb_RcomplabMode = Frame( frame1 )
            chb_RcomplabMode.grid(row=Row, column=1, sticky=W)
            chb_TC1Entry = Entry(chb_RcomplabMode, width=5, cursor='double_arrow')
            chb_TC1Entry.bind("<Return>", SettingsTextKey)
            chb_TC1Entry.bind('<MouseWheel>', Settingsscroll)
            chb_TC1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chb_TC1Entry.bind("<Button-5>", Settingsscroll)
            chb_TC1Entry.bind('<Key>', SettingsTextKey)
            chb_TC1Entry.pack(side=LEFT)
            chb_TC1Entry.delete(0,"end")
            chb_TC1Entry.insert(0,CHB_TC1.get())
            chb_A1Entry = Entry(chb_RcomplabMode, width=5, cursor='double_arrow')
            chb_A1Entry.bind("<Return>", SettingsTextKey)
            chb_A1Entry.bind('<MouseWheel>', Settingsscroll)
            chb_A1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chb_A1Entry.bind("<Button-5>", Settingsscroll)
            chb_A1Entry.bind('<Key>', SettingsTextKey)
            chb_A1Entry.pack(side=LEFT)
            chb_A1Entry.delete(0,"end")
            chb_A1Entry.insert(0,CHB_A1.get())
        #
            Row = Row + 1
            chb_Ccomplab = Label(frame1, text="CHB Comp, TC2 (uSec), A2", style= "A10B.TLabel") # in micro seconds
            chb_Ccomplab.grid(row=Row, column=0, sticky=W)
            chb_CcomplabMode = Frame( frame1 )
            chb_CcomplabMode.grid(row=Row, column=1, sticky=W)
            chb_TC2Entry = Entry(chb_CcomplabMode, width=5, cursor='double_arrow')
            chb_TC2Entry.bind("<Return>", SettingsTextKey)
            chb_TC2Entry.bind('<MouseWheel>', Settingsscroll)
            chb_TC2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chb_TC2Entry.bind("<Button-5>", Settingsscroll)
            chb_TC2Entry.bind('<Key>', SettingsTextKey)
            chb_TC2Entry.pack(side=LEFT)
            chb_TC2Entry.delete(0,"end")
            chb_TC2Entry.insert(0,CHB_TC2.get())
            chb_A2Entry = Entry(chb_CcomplabMode, width=5, cursor='double_arrow')
            chb_A2Entry.bind("<Return>", SettingsTextKey)
            chb_A2Entry.bind('<MouseWheel>', Settingsscroll)
            chb_A2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chb_A2Entry.bind("<Button-5>", Settingsscroll)
            chb_A2Entry.bind('<Key>', SettingsTextKey)
            chb_A2Entry.pack(side=LEFT)
            chb_A2Entry.delete(0,"end")
            chb_A2Entry.insert(0,CHB_A2.get())
        #
        if CHANNELS >= 3:
            Row = Row + 1
            chc_Rcomplab = Label(frame1, text="CHC Comp, TC1 (uSec), A1", style= "A10B.TLabel") # in micro seconds
            chc_Rcomplab.grid(row=Row, column=0, sticky=W)
            chc_RcomplabMode = Frame( frame1 )
            chc_RcomplabMode.grid(row=Row, column=1, sticky=W)
            chc_TC1Entry = Entry(chc_RcomplabMode, width=5, cursor='double_arrow')
            chc_TC1Entry.bind("<Return>", SettingsTextKey)
            chc_TC1Entry.bind('<MouseWheel>', Settingsscroll)
            chc_TC1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chc_TC1Entry.bind("<Button-5>", Settingsscroll)
            chc_TC1Entry.bind('<Key>', SettingsTextKey)
            chc_TC1Entry.pack(side=LEFT)
            chc_TC1Entry.delete(0,"end")
            chc_TC1Entry.insert(0,CHC_TC1.get())
            chc_A1Entry = Entry(chc_RcomplabMode, width=5, cursor='double_arrow')
            chc_A1Entry.bind("<Return>", SettingsTextKey)
            chc_A1Entry.bind('<MouseWheel>', Settingsscroll)
            chc_A1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chc_A1Entry.bind("<Button-5>", Settingsscroll)
            chc_A1Entry.bind('<Key>', SettingsTextKey)
            chc_A1Entry.pack(side=LEFT)
            chc_A1Entry.delete(0,"end")
            chc_A1Entry.insert(0,CHC_A1.get())
        #
            Row = Row + 1
            chc_Ccomplab = Label(frame1, text="CHC Comp, TC2 (uSec), A2", style= "A10B.TLabel") # in micro seconds
            chc_Ccomplab.grid(row=Row, column=0, sticky=W)
            chc_CcomplabMode = Frame( frame1 )
            chc_CcomplabMode.grid(row=Row, column=1, sticky=W)
            chc_TC2Entry = Entry(chc_CcomplabMode, width=5, cursor='double_arrow')
            chc_TC2Entry.bind("<Return>", SettingsTextKey)
            chc_TC2Entry.bind('<MouseWheel>', Settingsscroll)
            chc_TC2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chc_TC2Entry.bind("<Button-5>", Settingsscroll)
            chc_TC2Entry.bind('<Key>', SettingsTextKey)
            chc_TC2Entry.pack(side=LEFT)
            chc_TC2Entry.delete(0,"end")
            chc_TC2Entry.insert(0,CHC_TC2.get())
            chc_A2Entry = Entry(chc_CcomplabMode, width=5, cursor='double_arrow')
            chc_A2Entry.bind("<Return>", SettingsTextKey)
            chc_A2Entry.bind('<MouseWheel>', Settingsscroll)
            chc_A2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chc_A2Entry.bind("<Button-5>", Settingsscroll)
            chc_A2Entry.bind('<Key>', SettingsTextKey)
            chc_A2Entry.pack(side=LEFT)
            chc_A2Entry.delete(0,"end")
            chc_A2Entry.insert(0,CHC_A2.get())
        #
        if CHANNELS >= 4:
            Row = Row + 1
            chd_Rcomplab = Label(frame1, text="CHD Comp, TC1 (uSec), A1", style= "A10B.TLabel") # in micro seconds
            chd_Rcomplab.grid(row=Row, column=0, sticky=W)
            chd_RcomplabMode = Frame( frame1 )
            chd_RcomplabMode.grid(row=Row, column=1, sticky=W)
            chd_TC1Entry = Entry(chd_RcomplabMode, width=5, cursor='double_arrow')
            chd_TC1Entry.bind("<Return>", SettingsTextKey)
            chd_TC1Entry.bind('<MouseWheel>', Settingsscroll)
            chd_TC1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chd_TC1Entry.bind("<Button-5>", Settingsscroll)
            chd_TC1Entry.bind('<Key>', SettingsTextKey)
            chd_TC1Entry.pack(side=LEFT)
            chd_TC1Entry.delete(0,"end")
            chd_TC1Entry.insert(0,CHD_TC1.get())
            chd_A1Entry = Entry(chd_RcomplabMode, width=5, cursor='double_arrow')
            chd_A1Entry.bind("<Return>", SettingsTextKey)
            chd_A1Entry.bind('<MouseWheel>', Settingsscroll)
            chd_A1Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chd_A1Entry.bind("<Button-5>", Settingsscroll)
            chd_A1Entry.bind('<Key>', SettingsTextKey)
            chd_A1Entry.pack(side=LEFT)
            chd_A1Entry.delete(0,"end")
            chd_A1Entry.insert(0,CHD_A1.get())
        #
            Row = Row + 1
            chd_Ccomplab = Label(frame1, text="CHD Comp, TC2 (uSec), A2", style= "A10B.TLabel") # in micro seconds
            chd_Ccomplab.grid(row=Row, column=0, sticky=W)
            chd_CcomplabMode = Frame( frame1 )
            chd_CcomplabMode.grid(row=Row, column=1, sticky=W)
            chd_TC2Entry = Entry(chd_CcomplabMode, width=5, cursor='double_arrow')
            chd_TC2Entry.bind("<Return>", SettingsTextKey)
            chd_TC2Entry.bind('<MouseWheel>', Settingsscroll)
            chd_TC2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chd_TC2Entry.bind("<Button-5>", Settingsscroll)
            chd_TC2Entry.bind('<Key>', SettingsTextKey)
            chd_TC2Entry.pack(side=LEFT)
            chd_TC2Entry.delete(0,"end")
            chd_TC2Entry.insert(0,CHD_TC2.get())
            chd_A2Entry = Entry(chd_CcomplabMode, width=5, cursor='double_arrow')
            chd_A2Entry.bind("<Return>", SettingsTextKey)
            chd_A2Entry.bind('<MouseWheel>', Settingsscroll)
            chd_A2Entry.bind("<Button-4>", Settingsscroll)# with Linux OS
            chd_A2Entry.bind("<Button-5>", Settingsscroll)
            chd_A2Entry.bind('<Key>', SettingsTextKey)
            chd_A2Entry.pack(side=LEFT)
            chd_A2Entry.delete(0,"end")
            chd_A2Entry.insert(0,CHD_A2.get())
def UpdateAWGWin():

    UpdateAWGA()
    UpdateAWGB()
    MakeAWGwaves()
    
def SettingsUpdate():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon
    global CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2, TrgLPFEntry, Trigger_LPF_length
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    
    try:
        GW = int(eval(GwdthE.get()))
        if GW < 1:
            GW = 1
            GwdthE.delete(0,END)
            GwdthE.insert(0, int(GW))
        if GW > 5:
            GW = 5
            GwdthE.delete(0,END)
            GwdthE.insert(0, int(GW))
    except:
        GwdthE.delete(0,END)
        GwdthE.insert(0, GridWidth.get())
    GridWidth.set(GW)
    #
    try:
        TW = int(eval(TwdthE.get()))
        if TW < 1:
            TW = 1
            TwdthE.delete(0,END)
            TwdthE.insert(0, int(TW))
        if TW > 5:
            TW = 5
            TwdthE.delete(0,END)
            TwdthE.insert(0, int(TW))
    except:
        TwdthE.delete(0,END)
        TwdthE.insert(0, TRACEwidth.get())
    TRACEwidth.set(TW)
 # Number of average sweeps for average mode
    try:
        TA = int(eval(TAvg.get()))
        if TA < 1:
            TA = 1
            TAvg.delete(0,END)
            TAvg.insert(0, int(TA))
        if TA > 16:
            TA = 16
            TAvg.delete(0,END)
            TAvg.insert(0, int(TA))
    except:
        TAvg.delete(0,END)
        TAvg.insert(0, TRACEaverage.get())
    TRACEaverage.set(TA)
    # Number of vertical divisions for spectrum / Bode
    try:
        VDv = int(eval(VDivE.get()))
        if VDv < 1:
            VDv = 1
            VDivE.delete(0,END)
            VDivE.insert(0, int(VDv))
        if VDv > 16:
            VDv = 16
            VDivE.delete(0,END)
            VDivE.insert(0, int(VDv))
    except:
        VDivE.delete(0,END)
        VDivE.insert(0, Vdiv.get())
    Vdiv.set(VDv)
    # number of Harmonic Markers in SA
    try:
        HM = int(eval(HarMon.get()))
        if HM < 1:
            HM = 1
            HarMon.delete(0,END)
            HarMon.insert(0, int(HM))
        if HM > 9:
            HM =9
            HarMon.delete(0,END)
            HarMon.insert(0, int(HM))
    except:
        HarMon.delete(0,END)
        HarMon.insert(0, HarmonicMarkers.get())
    HarmonicMarkers.set(HM)
 # The zero stuffing value is 2 ** ZERO stuffing, calculated on initialize
    try:
        ZST = int(eval(ZSTuff.get()))
        if ZST < 1:
            ZST = 1
            ZSTuff.delete(0,END)
            ZSTuff.insert(0, int(ZST))
        if ZST > 5:
            ZST = 5
            ZSTuff.delete(0,END)
            ZSTuff.insert(0, int(ZST))
    except:
        ZSTuff.delete(0,END)
        ZSTuff.insert(0, ZEROstuffing.get())
    ZEROstuffing.set(ZST)
#
#
def DestroySettings():
    global Settingswindow, SettingsStatus
    
    SettingsStatus.set(0)
    SettingsUpdate()
    Settingswindow.destroy()
#
def onCanvasMouse_xy(event):
    global MouseX, MouseY, MouseWidget

    MouseWidget = event.widget
    MouseX, MouseY = event.x, event.y
#
def BSetFmin():
    global FminEntry, CHAfreq
    
    if CHAfreq > 0:
        String = '{0:.3f}'.format(CHAfreq/1000)
        FminEntry.delete(0,"end")
        FminEntry.insert(0,String)
#
def ReSetAGO():
    global CHAVGainEntry, CHAVOffsetEntry

    CHAVGainEntry.delete(0,"end")
    CHAVGainEntry.insert(0,1.0)
    CHAVOffsetEntry.delete(0,"end")
    CHAVOffsetEntry.insert(0,0.0)
#
def ReSetBGO():
    global CHBVGainEntry, CHBVOffsetEntry

    CHBVGainEntry.delete(0,"end")
    CHBVGainEntry.insert(0,1.0)
    CHBVOffsetEntry.delete(0,"end")
    CHBVOffsetEntry.insert(0,0.0)
#
def OpenOtherTools():
    global EnablePhaseAnalizer, EnableSpectrumAnalizer, EnableBodePlotter, EnableImpedanceAnalizer
    global EnableOhmMeter, OOTphckb, OOTBuildPhAScreen, OOTckb3, OOTBuildSpectrumScreen, OOTckb5, ckb1
    global OOTBuildBodeScreen, OOTckb4, OOTBuildIAScreen, OOTckb6, OOTBuildOhmScreen, OOTScreenStatus
    global OOTwindow, SWRev, RevDate, BorderSize, FrameRelief, OOTdismissclbutton, EnableDigIO
    global EnablePIODACMode, EnableMuxMode, EnableMinigenMode, EnablePmodDA1Mode, EnableDigPotMode, EnableGenericSerialMode
    global EnableAD5626SerialMode, EnableDigitalFilter, EnableCommandInterface, EnableMeasureScreen, EnableETSScreen

    if OOTScreenStatus.get() == 0:
        OOTScreenStatus.set(1)
        OOTwindow = Toplevel()
        OOTwindow.title("Instruments " + SWRev + RevDate)
        OOTwindow.resizable(FALSE,FALSE)
        OOTwindow.protocol("WM_DELETE_WINDOW", DestroyOOTwindow)
        frame1 = Frame(OOTwindow, borderwidth=BorderSize, relief=FrameRelief)
        frame1.grid(row=0, column=0, sticky=W)
        #
        nextrow = 1
        timebtn = Frame( frame1 )
        timebtn.grid(row=nextrow, column=0, sticky=W)
        ckb1 = Checkbutton(timebtn, text="Enab", style="Disab.TCheckbutton", variable=TimeDisp, command=TimeCheckBox)
        ckb1.pack(side=LEFT)
        timelab = Label(timebtn, text="Time Plot")
        timelab.pack(side=LEFT)
        nextrow = nextrow + 1
        if EnablePhaseAnalizer > 0:
            phasebtn = Frame( frame1 )
            phasebtn.grid(row=nextrow, column=0, sticky=W)
            OOTphckb = Checkbutton(phasebtn, text="Enab", style="Disab.TCheckbutton", variable=PhADisp, command=PhACheckBox)
            OOTphckb.pack(side=LEFT)
            OOTBuildPhAScreen = Button(phasebtn, text="Phasor Plot", style="W11.TButton", command=MakePhAWindow)
            OOTBuildPhAScreen.pack(side=LEFT)
            nextrow = nextrow + 1
        #
        if EnableSpectrumAnalizer > 0:
            freqbtn = Frame( frame1 )
            freqbtn.grid(row=nextrow, column=0, sticky=W)
            OOTckb3 = Checkbutton(freqbtn, text="Enab", style="Disab.TCheckbutton", variable=FreqDisp, command=FreqCheckBox)
            OOTckb3.pack(side=LEFT)
            OOTBuildSpectrumScreen = Button(freqbtn, text="Spectrum Plot", style="W11.TButton", command=MakeSpectrumWindow)
            OOTBuildSpectrumScreen.pack(side=LEFT)
            nextrow = nextrow + 1
        #
        if EnableBodePlotter > 0:
            bodebtn = Frame( frame1 )
            bodebtn.grid(row=nextrow, column=0, sticky=W)
            OOTckb5 = Checkbutton(bodebtn, text="Enab", style="Disab.TCheckbutton", variable=BodeDisp, command=BodeCheckBox)
            OOTckb5.pack(side=LEFT)
            OOTBuildBodeScreen = Button(bodebtn, text="Bode Plot", style="W11.TButton", command=MakeBodeWindow)
            OOTBuildBodeScreen.pack(side=LEFT)
            nextrow = nextrow + 1
        #
        if EnableImpedanceAnalizer > 0:
            impdbtn = Frame( frame1 )
            impdbtn.grid(row=nextrow, column=0, sticky=W)
            OOTckb4 = Checkbutton(impdbtn, text="Enab", style="Disab.TCheckbutton", variable=IADisp, command=IACheckBox)
            OOTckb4.pack(side=LEFT)
            OOTBuildIAScreen = Button(impdbtn, text="Impedance", style="W11.TButton", command=MakeIAWindow)
            OOTBuildIAScreen.pack(side=LEFT)
            nextrow = nextrow + 1
        #
        if EnableOhmMeter > 0:
            dcohmbtn = Frame( frame1 )
            dcohmbtn.grid(row=nextrow, column=0, sticky=W)
            OOTckb6 = Checkbutton(dcohmbtn, text="Enab", style="Disab.TCheckbutton", variable=OhmDisp, command=OhmCheckBox)
            OOTckb6.pack(side=LEFT)
            OOTBuildOhmScreen = Button(dcohmbtn, text="Ohmmeter", style="W11.TButton", command=MakeOhmWindow)
            OOTBuildOhmScreen.pack(side=LEFT)
            nextrow = nextrow + 1
        ## Digital Input / Output Option screens
        if EnableDigitalFilter >0:
            OOTDigFiltScreen = Button(frame1, text="Digital Filter", style="W17.TButton", command=MakeDigFiltWindow)
            OOTDigFiltScreen.grid(row=nextrow, column=0, sticky=W)
            nextrow = nextrow + 1
        if EnableCommandInterface > 0:
            OOTCommandLineScreen = Button(frame1, text="Command Interface", style="W17.TButton", command=MakeCommandScreen)
            OOTCommandLineScreen.grid(row=nextrow, column=0, sticky=W)
            nextrow = nextrow + 1
        if EnableMeasureScreen > 0:
            OOTMeasureScreen = Button(frame1, text="Measure Screen", style="W17.TButton", command=MakeMeasureScreen)
            OOTMeasureScreen.grid(row=nextrow, column=0, sticky=W)
            nextrow = nextrow + 1
        #
        OOTdismissclbutton = Button(frame1, text="Dismiss", style="W8.TButton", command=DestroyOOTwindow)
        OOTdismissclbutton.grid(row=nextrow, column=0, sticky=W, pady=7)
#
def DestroyOOTwindow():
    global OOTwindow, OOTScreenStatus
    
    OOTScreenStatus.set(0)
    OOTwindow.destroy()
#
#
# Calculate resistor divider gain and offset voltage
def RDbutton(): 
    global Rint, RDX0L, display9, display8, Voff, R1, R2, resdivwindow
    global RDGain, RDOffset, RDeffective
    #
    try:
        X = UnitConvert(Voff.get())
        Y = UnitConvert(R1.get())
        Z = UnitConvert(R2.get())
        ZE = (Z * Rint) / (Z + Rint)
        YE = (Y * Rint) / (Y + Rint)
        RDGain =  (Y + ZE) / ZE
        RDOffset = (X * YE)/(YE + Z)
        RDeffective = (Y * ZE) / (Y + ZE)
    except:
        RDOffset = None
        RDGain = None
        X = None
        Y = None
        Z = None
    
    if ((RDOffset is None) or (X is None) or (Y is None) or (Z is None) or (RDGain is None)):
        display = Label(resdivwindow, text="Calculation Error", foreground = "Red").place(x = RDX0L+80, y = 260)
    else:
        display = Label(resdivwindow, text="Calculation Successful", foreground = "Dark Green").place(x = RDX0L+80, y = 260)
        display9.config(text="%f Offset" %RDOffset)
        display8.config(text="%f Gain" %RDGain)		
#
# Draw a resistor shape at location
def DrawRes(X, Y, ResW, SchCa): 
    global COLORblack

    SchCa.create_line(X, Y, X, Y+20, fill=COLORblack, width=3)
    SchCa.create_line(X, Y+20, X+ResW, Y+25, fill=COLORblack, width=3)
    SchCa.create_line(X+ResW, Y+25, X-ResW, Y+35, fill=COLORblack, width=3)
    SchCa.create_line(X-ResW, Y+35, X+ResW, Y+45, fill=COLORblack, width=3)
    SchCa.create_line(X+ResW, Y+45, X-ResW, Y+55, fill=COLORblack, width=3)
    SchCa.create_line(X-ResW, Y+55, X, Y+60, fill=COLORblack, width=3)
    SchCa.create_line(X, Y+60, X, Y+80, fill=COLORblack, width=3)
#
def RDSetAGO():
    global CHAVGainEntry, CHAVOffsetEntry
    global RDGain, RDOffset, CHAIleak, RDeffective

    DivOffset = RDOffset + (CHAIleak * RDeffective)
    Gain_str = '{0:.3f}'.format(RDGain)
    Voff_str = '{0:.3f}'.format(DivOffset)
    CHAVGainEntry.delete(0,"end")
    CHAVGainEntry.insert(0,Gain_str)
    CHAVOffsetEntry.delete(0,"end")
    CHAVOffsetEntry.insert(0,Voff_str)
#
def RDSetBGO():
    global CHBVGainEntry, CHBVOffsetEntry
    global RDGain, RDOffset, CHBIleak, RDeffective

    DivOffset = RDOffset + (CHBIleak * RDeffective)
    Gain_str = '{0:.3f}'.format(RDGain)
    Voff_str = '{0:.3f}'.format(DivOffset)
    CHBVGainEntry.delete(0,"end")
    CHBVGainEntry.insert(0,Gain_str)
    CHBVOffsetEntry.delete(0,"end")
    CHBVOffsetEntry.insert(0,Voff_str)
##
def RDSetCGO():
    global CHCVGainEntry, CHCVOffsetEntry
    global RDGain, RDOffset, CHBIleak, RDeffective

    DivOffset = RDOffset + (CHBIleak * RDeffective)
    Gain_str = '{0:.3f}'.format(RDGain)
    Voff_str = '{0:.3f}'.format(DivOffset)
    CHCVGainEntry.delete(0,"end")
    CHCVGainEntry.insert(0,Gain_str)
    CHCVOffsetEntry.delete(0,"end")
    CHCVOffsetEntry.insert(0,Voff_str)
##
def RDSetDGO():
    global CHDVGainEntry, CHDVOffsetEntry
    global RDGain, RDOffset, CHBIleak, RDeffective

    DivOffset = RDOffset + (CHBIleak * RDeffective)
    Gain_str = '{0:.3f}'.format(RDGain)
    Voff_str = '{0:.3f}'.format(DivOffset)
    CHDVGainEntry.delete(0,"end")
    CHDVGainEntry.insert(0,Gain_str)
    CHDVOffsetEntry.delete(0,"end")
    CHDVOffsetEntry.insert(0,Voff_str)
#
def MakeResDivWindow():
    global SWRev, RevDate, ResDivStatus, ResDivDisp, R1, R2, Voff, COLORblack, COLORwhite
    global SetResDivA, SetResDivB, SetResDivC, SetResDivB, CHANNELS, FrameBG, BorderSize
    global display8, display9, resdivwindow, RDGRW, RDGRH, RDY0T, RDX0L
    
    if ResDivStatus.get() == 0: #
        ResDivStatus.set(1)
        ResDivDisp.set(1)
        resdivwindow = Toplevel()
        resdivwindow.title("Scope Input Resistor Divider " + SWRev + RevDate)
        resdivwindow.resizable(FALSE,FALSE)
        resdivwindow.protocol("WM_DELETE_WINDOW", DestroyResDivScreen)
        resdivwindow.geometry("530x310")
        resdivwindow.configure(background=FrameBG, borderwidth=BorderSize)
# from here down we build GUI
        #framet = Frame(resdivwindow, borderwidth=BorderSize, relief=FrameRelief)
        #framet.place(x=530, y=310) # , sticky=W)
        Font_tuple = ("Comic Sans MS", 10, "bold")
        #
        display = Label(resdivwindow, text="Scope Input Resistor Divider", foreground= "Blue",font = Font_tuple)
        display.place(x = RDX0L, y = RDY0T)
        
        display1 = Label(resdivwindow, text="Resistor - R1")
        display1.place(x = RDX0L, y = 60)
        display2 = Entry(resdivwindow,textvariable=R1)
        display2.place(x = RDX0L+80, y = 60)
        
        display3 = Label(resdivwindow, text="Resistor - R2")
        display3.place(x = RDX0L, y = 100)
        display4 = Entry(resdivwindow,textvariable=R2)
        display4.place(x = RDX0L+80, y = 100)
        
        display5 = Label(resdivwindow, text="Offset Voltage")
        display5.place(x = RDX0L, y = 140)
        display6 = Entry(resdivwindow,textvariable=Voff)
        display6.place(x = RDX0L+80, y = 140)
        
        display7 = Label(resdivwindow, text="Divider Offset")
        display7.place(x = RDX0L, y = 180)
        
        display9 = Label(resdivwindow, text="To be calculated", foreground = "Blue")
        display9.place(x = RDX0L+80, y = 180)

        display10 = Label(resdivwindow, text="Divider Gain")
        display10.place(x = RDX0L, y = 220)
        
        display8 = Label(resdivwindow, text="To be calculated", foreground = "Blue")
        display8.place(x = RDX0L+80, y = 220)
        
        Calbutton = Button(resdivwindow, text = "Calculate", command=RDbutton)
        Calbutton.place(x = RDX0L, y = 260)
        
        ResDivdismissbutton = Button(resdivwindow, text="Dismiss", command=DestroyResDivScreen)
        ResDivdismissbutton.place(x = 230, y = 260)
        if CHANNELS >= 1:
            ResDivCHAsetbutton = Checkbutton(resdivwindow, text='Set Ch A', style="Strace1.TCheckbutton", variable=SetResDivA, command=RDSetAGO)#
            ResDivCHAsetbutton.place(x = 330, y = 260)
        if CHANNELS >= 2:
            ResDivCHBsetbutton = Checkbutton(resdivwindow, text='Set Ch B', style="Strace2.TCheckbutton", variable=SetResDivB, command=RDSetBGO)#
            ResDivCHBsetbutton.place(x = 430, y = 260)
        if CHANNELS >= 3:
            ResDivCHCsetbutton = Checkbutton(resdivwindow, text='Set Ch C', style="Strace3.TCheckbutton", variable=SetResDivC, command=RDSetCGO)#
            ResDivCHCsetbutton.place(x = 330, y = 280)
        if CHANNELS >= 4:
            ResDivCHDsetbutton = Checkbutton(resdivwindow, text='Set Ch D', style="Strace4.TCheckbutton", variable=SetResDivD, command=RDSetDGO)#
            ResDivCHDsetbutton.place(x = 430, y = 280)
        
        Sche = Canvas(resdivwindow, width=RDGRW, height=RDGRH, background=COLORwhite)
        Sche.place(x = 230, y = RDY0T) #
        
        # Draw Schematic
        DrawRes(115, 40, 10, Sche)
        Sche.create_text(140, 80, text = "R1", fill=COLORblack, font=("arial", FontSize+4 ))
        DrawRes(115, 120, 10, Sche)
        Sche.create_text(140, 160, text = "R2", fill=COLORblack, font=("arial", FontSize+4 ))
        DrawRes(190, 120, 10, Sche)
        Sche.create_text(220, 160, text = "Rint", fill=COLORblack, font=("arial", FontSize+4 ))
        # Sche.create_text(225, 180, text = "1 Meg", fill=COLORblack, font=("arial", FontSize+4 ))
        Sche.create_line(70, 40, 115, 40, fill=COLORblack, width=3)
        Sche.create_line(70, 200, 115, 200, fill=COLORblack, width=3)
        Sche.create_line(115, 120, 235, 120, fill=COLORblack, width=3)
        Sche.create_line(175, 200, 205, 200, fill=COLORblack, width=3)
        Sche.create_line(175, 200, 190, 220, fill=COLORblack, width=3)
        Sche.create_line(205, 200, 190, 220, fill=COLORblack, width=3)
        Sche.create_rectangle(40, 30, 70, 50, width=3) #
        Sche.create_text(45, 15, text = "V Input", fill=COLORblack, font=("arial", FontSize+4 ))
        Sche.create_rectangle(40, 190, 70, 210, width=3) #
        Sche.create_text(47, 175, text = "V Offset", fill=COLORblack, font=("arial", FontSize+4 ))
        Sche.create_rectangle(235, 110, 265, 130, width=3) #
        Sche.create_text(230, 95, text = "Scope Input", fill=COLORblack, font=("arial", FontSize+4 ))
#
def DestroyResDivScreen():
    global resdivwindow, ResDivStatus, ResDivDisp
    
    ResDivStatus.set(0)
    ResDivDisp.set(0)
    resdivwindow.destroy()
# Routine to calculate effective un buffered input resistance based on sample rate
def CalEqRint():
    global SAMPLErate, Rint, Cint, SetResDivA, SetResDivB
    
    Rint = 1.0/(Cint * SAMPLErate) # Cint = 1.456E-12
    # print("Calculated Rint: ", Rint)
    RDbutton()
    if SetResDivA.get() > 0:
        RDSetAGO()
    if SetResDivB.get() > 0:
        RDSetBGO()
#
def ReConnectDevice():
    global Sucess
    if not Sucess:
        Sucess = ConnectDevice()
    if Sucess:
        #
        bcon.configure(text="Conn", style="GConn.TButton")
        BTime() # initally set Sample Rate by Horz Time base
        BSetTrigEdge()
        BSetTriggerSource()
        BTriglevel() # set trigger level
        MakeAWGwaves()
#
# ================ Make main Screen ==========================
#
TgInput = IntVar()   # Trigger Input variable
TgSource = IntVar()   # Trigger Input variable
SingleShot = IntVar() # variable for single shot triger
ManualTrigger = IntVar() # variable for Manual trigger
AutoLevel = IntVar() # variable for Auto Level trigger at mid point
TgEdge = IntVar()   # Trigger edge variable
# Show channels variables
ShowC1_V = IntVar()   # curves to display variables
ShowC2_V = IntVar()
ShowC3_V = IntVar()   # curves to display variables
ShowC4_V = IntVar()
ShowRA_V = IntVar()
ShowRB_V = IntVar()
ShowRC_V = IntVar()
ShowRD_V = IntVar()
ShowMath = IntVar()
# Bode and SA variables
ShowC1_VdB = IntVar()   # curves to display variables
ShowC1_P = IntVar()
ShowC2_VdB = IntVar()
ShowC2_P = IntVar()
ShowMarker = IntVar()
ShowRA_VdB = IntVar()
ShowRA_P = IntVar()
ShowRB_VdB = IntVar()
ShowRB_P = IntVar()
ShowMathSA = IntVar()
ShowRMath = IntVar()
HScaleBP = IntVar()
HScaleBP.set(1)
#
Show_MathX = IntVar()
Show_MathY = IntVar()
AutoCenterA = IntVar()
AutoCenterB = IntVar()
AutoCenterC = IntVar()
AutoCenterD = IntVar()
SmoothCurves = IntVar()
ZOHold = IntVar()
TRACEmodeTime = IntVar()
TRACEmodeTime.set(0)
DecimateOption = IntVar()
MathTrace = IntVar()
# AWG variables
AWGAShape = IntVar()  # AWG A Wave shape variable
AWGAPhaseDelay = IntVar() #
AWGBShape = IntVar()  # AWG B Wave shape variable
AWGBPhaseDelay = IntVar() #
LockFreq = IntVar() # Flag to lock AWG A and AWG B to same frequency
LockFreq.set(0)
BisCompA = IntVar() # Make Channel B comp of channel A
BisCompA.set(0)
AWGSync = IntVar() # Sync start both AWG channels
AWGSync.set(0)
# define vertical measurment variables
MeasDCV1 = IntVar()
MeasMinV1 = IntVar()
MeasMaxV1 = IntVar()
MeasMidV1 = IntVar()
MeasPPV1 = IntVar()
MeasRMSV1 = IntVar()
MeasRMSVA_B = IntVar()

MeasDiffAB = IntVar()
MeasDCV2 = IntVar()
MeasMinV2 = IntVar()
MeasMaxV2 = IntVar()
MeasMidV2 = IntVar()
MeasPPV2 = IntVar()
MeasRMSV2 = IntVar()

MeasDCV3 = IntVar()
MeasMinV3 = IntVar()
MeasMaxV3 = IntVar()
MeasMidV3 = IntVar()
MeasPPV3 = IntVar()
MeasRMSV3 = IntVar()

MeasDCV4 = IntVar()
MeasMinV4 = IntVar()
MeasMaxV4 = IntVar()
MeasMidV4 = IntVar()
MeasPPV4 = IntVar()
MeasRMSV4 = IntVar()

MeasDiffBA = IntVar()
MeasUserA = IntVar()
MeasAHW = IntVar()
MeasALW = IntVar()
MeasADCy = IntVar()
MeasAPER = IntVar()
MeasAFREQ = IntVar()
MeasBHW = IntVar()
MeasBLW = IntVar()
MeasBDCy = IntVar()
MeasBPER = IntVar()
MeasBFREQ = IntVar()
MeasPhase = IntVar()
MeasTopV1 = IntVar()
MeasBaseV1 = IntVar()
MeasTopV2 = IntVar()
MeasBaseV2 = IntVar()
MeasUserB = IntVar()
MeasDelay = IntVar()
TimeDisp = IntVar()
TimeDisp.set(1)
XYDisp = IntVar()
FreqDisp = IntVar()
PhADisp = IntVar()
BodeDisp = IntVar()
IADisp = IntVar()
OhmDisp = IntVar()
OOTScreenStatus = IntVar()
OOTScreenStatus.set(0)
PhAScreenStatus = IntVar()
PhAScreenStatus.set(0)
AppendPhAData = IntVar()
AppendPhAData.set(0)
PhAPlotMode = IntVar()
PhADatafilename = "PhaseData.csv"
BodeScreenStatus = IntVar()
BodeScreenStatus.set(0)
MuxScreenStatus = IntVar()
MuxScreenStatus.set(0)
DigFiltStatus = IntVar()
DigFiltStatus.set(0)
CommandStatus = IntVar()
CommandStatus.set(0)
MeasureStatus = IntVar()
MeasureStatus.set(0)
MarkerScale = IntVar()
MarkerScale.set(1)
SettingsStatus = IntVar()
CHA_RC_HP = IntVar()
CHB_RC_HP = IntVar()
CHC_RC_HP = IntVar()
CHD_RC_HP = IntVar()
HScale = IntVar()
SAVScale = IntVar()
SAVPSD = IntVar()
SAvertmax = 1.0
SAvertmin = 1.0E-6
dlog = IntVar()
dlog.set(0)
Dlog_open = IntVar()
Dlog_open.set(0)
#
# CH1Probe
# CH2Probe
CH1VRange = "500mV"
CH2VRange = "500mV"
CH3VRange = "500mV"
CH4VRange = "500mV"
TimeDivStr = "200us"
TiggerLevel = 0.0
# Try to connect to hardware
Sucess = ConnectDevice()
#
#
if GUITheme == "Light": # Can be Light or Dark or Blue or LtBlue
    FrameBG = "#d7d7d7"
    ButtonText = "#000000"
    COLORwhite = "#ffffff" # 100% white
    COLORblack = "#000000" # 100% black
elif GUITheme == "Dark":
    FrameBG = "#484848"
    ButtonText = "#ffffff"
    COLORwhite = "#000000" # 100% black
    COLORblack = "#ffffff" # 100% white
elif GUITheme == "Blue":
    FrameBG = "#242468"
    ButtonText = "#d0d0ff"
elif GUITheme == "LtBlue":
    FrameBG = "#c0e8ff"
    ButtonText = "#000040"
EntryText = "#000000"
BoxColor = "#0000ff" # 100% blue
root.style.configure("TFrame", background=FrameBG, borderwidth=BorderSize)
root.style.configure("TLabelframe", background=FrameBG)
root.style.configure("TLabel", foreground=ButtonText, background=FrameBG, relief=LabRelief)
root.style.configure("TEntry", foreground=EntryText, background=FrameBG, relief=ButRelief) #cursor='sb_v_double_arrow'
root.style.configure("TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TRadiobutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TButton", foreground=ButtonText, background=FrameBG, highlightcolor=FrameBG, relief=ButRelief)
# define custom buttons and labels
root.style.configure("TSpinbox", arrowsize=SBoxarrow) # 11 only changes things in Python 3
root.style.configure("W3.TButton", width=3, relief=ButRelief)
root.style.configure("W4.TButton", width=4, relief=ButRelief)
root.style.configure("W5.TButton", width=5, relief=ButRelief)
root.style.configure("W6.TButton", width=6, relief=ButRelief)
root.style.configure("W7.TButton", width=7, relief=ButRelief)
root.style.configure("W8.TButton", width=8, relief=ButRelief)
root.style.configure("W9.TButton", width=9, relief=ButRelief)
root.style.configure("W10.TButton", width=10, relief=ButRelief)
root.style.configure("W11.TButton", width=11, relief=ButRelief)
root.style.configure("W16.TButton", width=16, relief=ButRelief)
root.style.configure("W17.TButton", width=17, relief=ButRelief)
root.style.configure("Stop.TButton", background=ButtonRed, foreground="#000000", width=4, relief=ButRelief)
root.style.configure("Run.TButton", background=ButtonGreen, foreground="#000000", width=4, relief=ButRelief)
root.style.configure("Pwr.TButton", background=ButtonGreen, foreground="#000000", width=8, relief=ButRelief)
root.style.configure("PwrOff.TButton", background=ButtonRed, foreground="#000000", width=8, relief=ButRelief)
root.style.configure("Roll.TButton", background=ButtonGreen, foreground="#000000", width=7, relief=ButRelief)
root.style.configure("RollOff.TButton", background=ButtonRed, foreground="#000000", width=8, relief=ButRelief)
root.style.configure("RConn.TButton", background=ButtonRed, foreground="#000000", width=5, relief=ButRelief)
root.style.configure("GConn.TButton", background=ButtonGreen, foreground="#000000", width=5, relief=ButRelief)
root.style.configure("Rtrace1.TButton", background=COLORtrace1, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace1.TButton", background=COLORtrace1, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace1.TButton", background=COLORtrace1, foreground="#000000", relief=ButRelief)
root.style.configure("Rtrace2.TButton", background=COLORtrace2, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace2.TButton", background=COLORtrace2, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace2.TButton", background=COLORtrace2, foreground="#000000", relief=ButRelief)
root.style.configure("Rtrace3.TButton", background=COLORtrace3, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace3.TButton", background=COLORtrace3, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace3.TButton", background=COLORtrace3, foreground="#000000", relief=ButRelief)
root.style.configure("Rtrace4.TButton", background=COLORtrace4, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace4.TButton", background=COLORtrace4, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace4.TButton", background=COLORtrace4, foreground="#000000", relief=ButRelief)
root.style.configure("Rtrace5.TButton", background=COLORtrace5, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Rtrace6.TButton", background=COLORtrace6, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Rtrace6.TButton", background=COLORtrace6, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Rtrace7.TButton", background=COLORtrace7, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace7.TButton", background=COLORtrace7, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("T1W16.TButton", background=COLORtrace1, width=16, relief=ButRelief)
root.style.configure("T2W16.TButton", background=COLORtrace2, width=16, relief=ButRelief)
root.style.configure("T3W16.TButton", background=COLORtrace3, width=16, relief=ButRelief)
root.style.configure("T4W16.TButton", background=COLORtrace4, width=16, relief=ButRelief)
root.style.configure("T5W16.TButton", background=COLORtrace5, width=16, relief=ButRelief)
root.style.configure("T6W16.TButton", background=COLORtrace6, width=16, relief=ButRelief)
root.style.configure("T7W16.TButton", background=COLORtrace7, width=16, relief=ButRelief)
root.style.configure("TR1W16.TButton", background=COLORtraceR1, width=16, relief=ButRelief)
root.style.configure("TR2W16.TButton", background=COLORtraceR2, width=16, relief=ButRelief)
root.style.configure("TR3W16.TButton", background=COLORtraceR3, width=16, relief=ButRelief)
root.style.configure("TR4W16.TButton", background=COLORtraceR4, width=16, relief=ButRelief)
root.style.configure("TR5W16.TButton", background=COLORtraceR5, width=16, relief=ButRelief)
root.style.configure("TR6W16.TButton", background=COLORtraceR6, width=16, relief=ButRelief)
root.style.configure("TR7W16.TButton", background=COLORtraceR7, width=16, relief=ButRelief)
root.style.configure("TGW16.TButton", background=COLORtrigger, width=16, relief=ButRelief)
root.style.configure("ZLW16.TButton", background=COLORzeroline, width=16, relief=ButRelief)
root.style.configure("RGray.TButton", background="#808080", width=7, relief=RAISED)
root.style.configure("SGray.TButton", background="#808080", width=7, relief=SUNKEN)
#
root.style.configure("A10T5.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR5, font=('Arial', 10, 'bold'))
root.style.configure("A10T5.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10T6.TLabelframe.Label", background=FrameBG, foreground=COLORtrace6, font=('Arial', 10, 'bold'))
root.style.configure("A10T6.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10T7.TLabelframe.Label", background=FrameBG, foreground=COLORtrace7, font=('Arial', 10, 'bold'))
root.style.configure("A10T7.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
#
root.style.configure("A10R1.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR1, font=('Arial', 10, 'bold'))
root.style.configure("A10R1.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10R2.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR2, font=('Arial', 10, 'bold'))
root.style.configure("A10R2.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10R6.TLabelframe.Label", background=FrameBG, foreground=COLORtraceR7, font=('Arial', 10, 'bold'))
root.style.configure("A10R6.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10.TLabelframe.Label", background=FrameBG, font=('Arial', 10, 'bold'))
root.style.configure("A10.TLabelframe", borderwidth=BorderSize, relief=FrameRelief)
root.style.configure("A10B.TLabel", foreground=ButtonText, font="Arial 10 bold") # Black text
root.style.configure("A10R.TLabel", foreground=ButtonRed, font="Arial 10 bold") # Red text
root.style.configure("A10G.TLabel", foreground=ButtonGreen, font="Arial 10 bold") # Red text
root.style.configure("A12B.TLabel", foreground=ButtonText, font="Arial 12 bold") # Black text
root.style.configure("A16B.TLabel", foreground=ButtonText, font="Arial 16 bold") # Black text
root.style.configure("Stop.TRadiobutton", background=ButtonRed, indicatorcolor=FrameBG)
root.style.configure("Run.TRadiobutton", background=ButtonGreen, indicatorcolor=FrameBG)
root.style.configure("Disab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonRed)
root.style.configure("Enab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonGreen)
root.style.configure("Strace1.TCheckbutton", background=COLORtrace1, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace2.TCheckbutton", background=COLORtrace2, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace3.TCheckbutton", background=COLORtrace3, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace4.TCheckbutton", background=COLORtrace4, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace5.TCheckbutton", background=COLORtrace5, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace6.TCheckbutton", background=COLORtrace6, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace7.TCheckbutton", background=COLORtrace7, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("WPhase.TRadiobutton", width=5, foreground="#000000", background="white", indicatorcolor=("red", "green"))
root.style.configure("GPhase.TRadiobutton", width=5, foreground="#000000", background="gray", indicatorcolor=("red", "green"))
# Custom left and right arrows
root.style.layout('Left1.TButton',[
                ('Button.focus', {'children': [
                    ('Button.leftarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.layout('Left2.TButton',[
                ('Button.focus', {'children': [
                    ('Button.leftarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.layout('Right1.TButton',[
                ('Button.focus', {'children': [
                    ('Button.rightarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.layout('Right2.TButton',[
                ('Button.focus', {'children': [
                    ('Button.rightarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]} )]} )] )

root.style.configure('Left1.TButton',font=('',FontSize,'bold'), width=7, arrowcolor='black', background='white', relief=LabRelief)
root.style.configure('Right1.TButton',font=('',FontSize,'bold'), width=7, arrowcolor='black', background='white', relief=LabRelief)
root.style.configure('Left2.TButton',font=('',FontSize,'bold'), width=6, arrowcolor='black')
root.style.configure('Right2.TButton',font=('',FontSize,'bold'), width=6, arrowcolor='black')
# Create frames
frame2r = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame2r.pack(side=RIGHT, fill=BOTH, expand=NO)

frame1 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame1.pack(side=TOP, fill=BOTH, expand=NO)

frame2 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame2.pack(side=TOP, fill=BOTH, expand=YES)

frame3 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame3.pack(side=TOP, fill=BOTH, expand=NO)

frame4 = Frame(root, borderwidth=BorderSize, relief=FrameRelief)
frame4.pack(side=TOP, fill=BOTH, expand=NO)
# create a pulldown menu
# Trigger signals
Triggermenu = Menubutton(frame1, text="Trigger", style="W7.TButton")
Triggermenu.menu = Menu(Triggermenu, tearoff = 0 )
Triggermenu["menu"]  = Triggermenu.menu
Triggermenu.menu.add_radiobutton(label='None', variable=TgInput, value=0)
if CHANNELS >= 1:
    Triggermenu.menu.add_radiobutton(label='CH A', background=COLORtrace1, variable=TgInput, value=1, command=BSetTriggerSource)
if CHANNELS >= 2:
    Triggermenu.menu.add_radiobutton(label='CH B', background=COLORtrace2, variable=TgInput, value=2, command=BSetTriggerSource)
if CHANNELS >= 3:
    Triggermenu.menu.add_radiobutton(label='CH C', background=COLORtrace3, variable=TgInput, value=3, command=BSetTriggerSource)
if CHANNELS >= 4:
    Triggermenu.menu.add_radiobutton(label='CH D', background=COLORtrace4, variable=TgInput, value=4, command=BSetTriggerSource)
Triggermenu.menu.add_radiobutton(label='Internal', variable=TgSource, value=0, command=BTrigIntExt)
Triggermenu.menu.add_radiobutton(label='External', variable=TgSource, value=1, command=BTrigIntExt)
Triggermenu.menu.add_checkbutton(label='Auto Level', variable=AutoLevel)
Triggermenu.menu.add_checkbutton(label='Manual Trgger', variable=ManualTrigger)
Triggermenu.menu.add_checkbutton(label='SingleShot', variable=SingleShot)
Triggermenu.pack(side=LEFT)
#
Edgemenu = Menubutton(frame1, text="Edge", style="W5.TButton")
Edgemenu.menu = Menu(Edgemenu, tearoff = 0 )
Edgemenu["menu"]  = Edgemenu.menu
Edgemenu.menu.add_radiobutton(label='Rising (+)', variable=TgEdge, value=0, command=BSetTrigEdge)
Edgemenu.menu.add_radiobutton(label='Falling (-)', variable=TgEdge, value=1, command=BSetTrigEdge)
Edgemenu.pack(side=LEFT)
#
tlab = Label(frame1, text="Trig Level")
tlab.pack(side=LEFT)
TRIGGERentry = Entry(frame1, width=5, cursor='double_arrow')
TRIGGERentry.bind('<MouseWheel>', onTrigLevelScroll)
TRIGGERentry.bind("<Button-4>", onTrigLevelScroll)# with Linux OS
TRIGGERentry.bind("<Button-5>", onTrigLevelScroll)
TRIGGERentry.bind("<Return>", BTriglevel)
TRIGGERentry.bind('<Key>', onTextKey)
TRIGGERentry.pack(side=LEFT)
TRIGGERentry.delete(0,"end")
TRIGGERentry.insert(0,TRIGGERlevel)
#
tgb = Button(frame1, text="50%", style="W4.TButton", command=BTrigger50p)
tgb.pack(side=LEFT)
#
hozlab = Button(frame1, text="Horz Pos", style="W8.TButton", command=SetHorzPoss)
hozlab.pack(side=LEFT)
HozPossentry = Entry(frame1, width=6, cursor='double_arrow')
HozPossentry.bind('<MouseWheel>', onHzPosScroll)
HozPossentry.bind("<Button-4>", onHzPosScroll)# with Linux OS
HozPossentry.bind("<Button-5>", onHzPosScroll)
HozPossentry.bind("<Return>", BHozPoss)
HozPossentry.bind('<Key>', onTextKey)
HozPossentry.pack(side=LEFT)
HozPossentry.delete(0,"end")
HozPossentry.insert(0,508)
#
bexit = Button(frame1, text="Exit", style="W4.TButton", command=Bcloseexit)
bexit.pack(side=RIGHT)
bstop = Button(frame1, text="Stop", style="Stop.TButton", command=BStop)
bstop.pack(side=RIGHT)
brun = Button(frame1, text="Run", style="Run.TButton", command=BStart)
brun.pack(side=RIGHT)
# Curves Menu
if EnableScopeOnly == 0:
    Showmenu = Menubutton(frame1, text="Curves", style="W7.TButton")
else:
    Showmenu = Menubutton(frame1, text="Traces", style="W7.TButton")
Showmenu.menu = Menu(Showmenu, tearoff = 0 )
Showmenu["menu"] = Showmenu.menu
Showmenu.menu.add_command(label="-Show Traces-", foreground="blue", command=donothing)
Showmenu.menu.add_command(label="All", command=BShowCurvesAll)
Showmenu.menu.add_command(label="None", command=BShowCurvesNone)
if CHANNELS >= 1:
    Showmenu.menu.add_checkbutton(label='CH A (1)', background=COLORtrace1, variable=ShowC1_V, command=SelectChannels)#
if CHANNELS >= 2:
    Showmenu.menu.add_checkbutton(label='CH B (2)', background=COLORtrace2, variable=ShowC2_V, command=SelectChannels)#
if CHANNELS >= 3:
    Showmenu.menu.add_checkbutton(label='CH C (3)', background=COLORtrace3, variable=ShowC3_V, command=SelectChannels)#
if CHANNELS >= 4:
    Showmenu.menu.add_checkbutton(label='CH D (4)', background=COLORtrace4, variable=ShowC4_V, command=SelectChannels)#
Showmenu.menu.add_checkbutton(label='Math-X', background=COLORtrace6, variable=Show_MathX, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='Math-Y', background=COLORtrace7, variable=Show_MathY, command=UpdateTimeTrace)
Showmenu.menu.add_command(label="-Auto Vert Center-", foreground="blue", command=donothing)
if CHANNELS >= 1:
    Showmenu.menu.add_checkbutton(label='Center CA', variable=AutoCenterA)
if CHANNELS >= 2:
    Showmenu.menu.add_checkbutton(label='Center CB', variable=AutoCenterB)
if CHANNELS >= 3:
    Showmenu.menu.add_checkbutton(label='Center CC', variable=AutoCenterC)
if CHANNELS >= 4:
    Showmenu.menu.add_checkbutton(label='Center CD', variable=AutoCenterD)
Showmenu.menu.add_command(label="-Input HP Comp-", foreground="blue", command=donothing)
if CHANNELS >= 1:
    Showmenu.menu.add_checkbutton(label='Comp CH A', variable=CHA_RC_HP)
if CHANNELS >= 2:
    Showmenu.menu.add_checkbutton(label='Comp CH B', variable=CHB_RC_HP)
if CHANNELS >= 3:
    Showmenu.menu.add_checkbutton(label='Comp CH C', variable=CHC_RC_HP)
if CHANNELS >= 4:
    Showmenu.menu.add_checkbutton(label='Comp CH D', variable=CHC_RC_HP)
Showmenu.menu.add_separator()
if CHANNELS >= 1:
    Showmenu.menu.add_checkbutton(label='RA', background=COLORtraceR1, variable=ShowRA_V, command=UpdateTimeTrace)
if CHANNELS >= 2:
    Showmenu.menu.add_checkbutton(label='RB', background=COLORtraceR2, variable=ShowRB_V, command=UpdateTimeTrace)
if CHANNELS >= 3:
    Showmenu.menu.add_checkbutton(label='RC', background=COLORtraceR3, variable=ShowRC_V, command=UpdateTimeTrace)
if CHANNELS >= 4:
    Showmenu.menu.add_checkbutton(label='RD', background=COLORtraceR4, variable=ShowRD_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='RMath', background=COLORtraceR5, variable=ShowMath, command=UpdateTimeTrace)
Showmenu.menu.add_separator()
Showmenu.menu.add_checkbutton(label='T Cursor (t)', variable=ShowTCur, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='V Cursor (v)', variable=ShowVCur, command=UpdateTimeTrace)
Showmenu.pack(side=RIGHT)
#
if ShowBallonHelp > 0:
    Triggermenu_tip = CreateToolTip(Triggermenu, 'Select trigger signal')
    Edgemenu_tip = CreateToolTip(Edgemenu, 'Select trigger edge')
    tgb_tip = CreateToolTip(tgb, 'Set trigger level to waveform mid point')
    hozlab_tip = CreateToolTip(hozlab, 'When triggering, set trigger point to center of screen')
    bexit_tip = CreateToolTip(bexit, 'Exit ALICE Desktop')
    bstop_tip = CreateToolTip(bstop, 'Stop acquiring data')
    brun_tip = CreateToolTip(brun, 'Start acquiring data')
    Showmenu_tip = CreateToolTip(Showmenu, 'Select which traces to display')

# Sampling controls Widgets
#RollBt = Button(frame1, text="Roll-Off", style="RollOff.TButton", command=BRoll)
# RollBt.pack(side=RIGHT) 
#
# Time per Div
TMsb = Spinbox(frame1, width=7, values= TMpdiv, cursor='double_arrow', command=BTime)
TMsb.bind('<MouseWheel>', onSpinBoxScroll)
TMsb.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
TMsb.bind("<Button-5>", onSpinBoxScroll)
TMsb.pack(side=RIGHT)
TMsb.delete(0,"end")
TMsb.insert(0,TimeDivStr) # "200us"
TMlab = Label(frame1, text="Time S/Div")
TMlab.pack(side=RIGHT)
#
ca = Canvas(frame2, width=CANVASwidth, height=CANVASheight, background=COLORcanvas, cursor='cross')
# add mouse left and right button click to canvas
ca.bind('<Configure>', CAresize)
ca.bind('<1>', onCanvasClickLeft)
ca.bind('<3>', onCanvasClickRight)
ca.bind("<Motion>",onCanvasMouse_xy)
ca.bind("<Up>", onCanvasUpArrow) # DoNothing)
ca.bind("<Down>", onCanvasDownArrow)
ca.bind("<Left>", onCanvasLeftArrow)
ca.bind("<Right>", onCanvasRightArrow)
ca.bind("<space>", onCanvasSpaceBar)
ca.bind("1", onCanvasOne)
ca.bind("2", onCanvasTwo)
ca.bind("3", onCanvasThree)
ca.bind("4", onCanvasFour)
ca.bind("5", onCanvasFive)
ca.bind("6", onCanvasSix)
ca.bind("7", onCanvasSeven)
ca.bind("8", onCanvasEight)
ca.bind("9", onCanvasNine)
ca.bind("0", onCanvasZero)
ca.bind("a", onCanvasAverage)
ca.bind("i", onCanvasInterp)
ca.bind("t", onCanvasShowTcur)
ca.bind("v", onCanvasShowVcur)
ca.bind("s", onCanvasSnap)
ca.bind("+", onCanvasTrising)
ca.bind("-", onCanvasTfalling)
ca.bind('<MouseWheel>', onCanvasClickScroll)
ca.bind("<Button-4>", onCanvasClickScroll)# with Linux OS
ca.bind("<Button-5>", onCanvasClickScroll)
ca.pack(side=TOP, fill=BOTH, expand=YES)
MouseWidget = ca
# right side menu buttons
dropmenu = Frame( frame2r )
dropmenu.pack(side=TOP)
bcon = Button(dropmenu, text="Recon", style="RConn.TButton", command=ReConnectDevice)
bcon.pack(side=LEFT, anchor=W)
# File menu
Filemenu = Menubutton(dropmenu, text="File", style="W4.TButton")
Filemenu.menu = Menu(Filemenu, tearoff = 0 )
Filemenu["menu"] = Filemenu.menu
Filemenu.menu.add_command(label="Save Config", command=BSaveConfigTime)
Filemenu.menu.add_command(label="Load Config", command=BLoadConfigTime)
Filemenu.menu.add_command(label="Run Script", command=RunScript)
Filemenu.menu.add_command(label="Save Adj", command=BSaveCal)
Filemenu.menu.add_command(label="Load Adj", command=BLoadCal)
Filemenu.menu.add_command(label="Save Screen", command=BSaveScreen)
Filemenu.menu.add_command(label="Save To CSV", command=BSaveData)
Filemenu.menu.add_command(label="Load From CSV", command=BReadData)
Filemenu.menu.add_command(label="Save PWL Data", command=BSaveChannelData)
Filemenu.menu.add_checkbutton(label="DLog to file", variable=dlog, command=Dloger_on_off)
Filemenu.menu.add_command(label="Help", command=BHelp)
Filemenu.menu.add_command(label="About", command=BAbout)
Filemenu.pack(side=LEFT, anchor=W)
# Options Menu
Optionmenu = Menubutton(dropmenu, text="Options", style="W7.TButton")
Optionmenu.menu = Menu(Optionmenu, tearoff = 0 )
Optionmenu["menu"]  = Optionmenu.menu
Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
Optionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurves, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Z-O-Hold', variable=ZOHold, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Iterpolate (i)', variable=EnableInterpFilter)
Optionmenu.menu.add_checkbutton(label='Trace Avg (a)', variable=TRACEmodeTime)
Optionmenu.menu.add_checkbutton(label='Dual Time Cursors', variable=MeasGateStatus)
Optionmenu.menu.add_checkbutton(label='Persistance', variable=ScreenTrefresh)
Optionmenu.menu.add_command(label='Set Marker Location', command=BSetMarkerLocation)
Optionmenu.menu.add_command(label='Change Plot Label', command=BUserCustomPlotText)
Optionmenu.menu.add_command(label="SnapShot (s)", command=BSnapShot)
Optionmenu.menu.add_command(label="Color Selector", command=ColorSelector)
Optionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
Optionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
if AllowFlashFirmware == 1:
    Optionmenu.menu.add_command(label="Update Firmware", command=UpdateFirmware)

if EnableScopeOnly != 0:
    Optionmenu.menu.add_command(label="Open Instruments", command=OpenOtherTools)
Optionmenu.pack(side=LEFT, anchor=W)
#
dropmenu2 = Frame( frame2r )
dropmenu2.pack(side=TOP)
# Open Math trace menu
mathbt = Button(dropmenu2, text="Math", style="W4.TButton", command = NewEnterMathControls)
mathbt.pack(side=RIGHT, anchor=W)
# Measurments menu
measlab = Label(dropmenu2, text="Meas")
measlab.pack(side=LEFT, anchor=W)
MeasmenuA = Menubutton(dropmenu2, text="CA", style="W3.TButton")
MeasmenuA.menu = Menu(MeasmenuA, tearoff = 0 )
MeasmenuA["menu"]  = MeasmenuA.menu
MeasmenuA.menu.add_command(label="-CA-V-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=MeasDCV1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=MeasMinV1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=MeasMaxV1)
MeasmenuA.menu.add_checkbutton(label='Base', variable=MeasBaseV1)
MeasmenuA.menu.add_checkbutton(label='Top', variable=MeasTopV1)
MeasmenuA.menu.add_checkbutton(label='Mid', variable=MeasMidV1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=MeasPPV1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=MeasRMSV1)
MeasmenuA.menu.add_checkbutton(label='A-B', variable=MeasDiffAB)
MeasmenuA.menu.add_checkbutton(label='A-B RMS', variable=MeasRMSVA_B)
MeasmenuA.menu.add_checkbutton(label='User', variable=MeasUserA, command=BUserAMeas)
#MeasmenuA.menu.add_separator()
MeasmenuA.menu.add_command(label="-CA-Time-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='H-Width', variable=MeasAHW)
MeasmenuA.menu.add_checkbutton(label='L-Width', variable=MeasALW)
MeasmenuA.menu.add_checkbutton(label='DutyCyle', variable=MeasADCy)
MeasmenuA.menu.add_checkbutton(label='Period', variable=MeasAPER)
MeasmenuA.menu.add_checkbutton(label='Freq', variable=MeasAFREQ)
MeasmenuA.menu.add_checkbutton(label='A-B Phase', variable=MeasPhase)
if CHANNELS >= 3:
    MeasmenuA.menu.add_separator()
    MeasmenuA.menu.add_command(label="-CC-V-", foreground="blue", command=donothing)
    MeasmenuA.menu.add_checkbutton(label='Avg', variable=MeasDCV3)
    MeasmenuA.menu.add_checkbutton(label='Min', variable=MeasMinV3)
    MeasmenuA.menu.add_checkbutton(label='Max', variable=MeasMaxV3)
    MeasmenuA.menu.add_checkbutton(label='Mid', variable=MeasMidV3)
    MeasmenuA.menu.add_checkbutton(label='P-P', variable=MeasPPV3)
    MeasmenuA.menu.add_checkbutton(label='RMS', variable=MeasRMSV3)
#
MeasmenuA.pack(side=LEFT)
#
MeasmenuB = Menubutton(dropmenu2, text="CB", style="W3.TButton")
MeasmenuB.menu = Menu(MeasmenuB, tearoff = 0 )
MeasmenuB["menu"]  = MeasmenuB.menu
MeasmenuB.menu.add_command(label="-CB-V-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=MeasDCV2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=MeasMinV2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=MeasMaxV2)
MeasmenuB.menu.add_checkbutton(label='Base', variable=MeasBaseV2)
MeasmenuB.menu.add_checkbutton(label='Top', variable=MeasTopV2)
MeasmenuB.menu.add_checkbutton(label='Mid', variable=MeasMidV2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=MeasPPV2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=MeasRMSV2)
MeasmenuB.menu.add_checkbutton(label='B-A', variable=MeasDiffBA)
MeasmenuB.menu.add_checkbutton(label='User', variable=MeasUserB, command=BUserBMeas)
#MeasmenuB.menu.add_separator()
MeasmenuB.menu.add_command(label="-CB-Time-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='H-Width', variable=MeasBHW)
MeasmenuB.menu.add_checkbutton(label='L-Width', variable=MeasBLW)
MeasmenuB.menu.add_checkbutton(label='DutyCyle', variable=MeasBDCy)
MeasmenuB.menu.add_checkbutton(label='Period', variable=MeasBPER)
MeasmenuB.menu.add_checkbutton(label='Freq', variable=MeasBFREQ)
MeasmenuB.menu.add_checkbutton(label='B-A Delay', variable=MeasDelay)
if CHANNELS >= 4:
    MeasmenuB.menu.add_separator()
    MeasmenuB.menu.add_command(label="-CD-V-", foreground="blue", command=donothing)
    MeasmenuB.menu.add_checkbutton(label='Avg', variable=MeasDCV4)
    MeasmenuB.menu.add_checkbutton(label='Min', variable=MeasMinV4)
    MeasmenuB.menu.add_checkbutton(label='Max', variable=MeasMaxV4)
    MeasmenuB.menu.add_checkbutton(label='Mid', variable=MeasMidV4)
    MeasmenuB.menu.add_checkbutton(label='P-P', variable=MeasPPV4)
    MeasmenuB.menu.add_checkbutton(label='RMS', variable=MeasRMSV4)
MeasmenuB.pack(side=LEFT)
if ShowBallonHelp > 0:
    math_tip = CreateToolTip(mathbt, 'Open Math window')
    options_tip = CreateToolTip(Optionmenu, 'Select Optional Settings')
    file_tip = CreateToolTip(Filemenu, 'Select File operations')
#
DigScreenStatus = IntVar()
DigScreenStatus.set(0)
#
if AWGChannels > 0:
    BuildAWGScreen = Button(frame2r, text="AWG Window", style="W16.TButton", command=MakeAWGWindow)
    BuildAWGScreen.pack(side=TOP)
# Mode selector
timebtn = Frame( frame2r )
timebtn.pack(side=TOP)
ckb1 = Checkbutton(timebtn, text="Enab", style="Disab.TCheckbutton", variable=TimeDisp, command=TimeCheckBox)
ckb1.pack(side=LEFT)
timelab = Label(timebtn, text="Time Plot")
timelab.pack(side=LEFT)
if EnableXYPlotter > 0:
    xybtn = Frame( frame2r )
    xybtn.pack(side=TOP)
    ckb2 = Checkbutton(xybtn, text="Enab", style="Disab.TCheckbutton", variable=XYDisp, command=XYCheckBox)
    ckb2.pack(side=LEFT)
    BuildXYScreen = Button(xybtn, text="X-Y Plot", style="W11.TButton", command=MakeXYWindow)
    BuildXYScreen.pack(side=TOP)
#
if EnablePhaseAnalizer > 0:
    phasebtn = Frame( frame2r )
    phasebtn.pack(side=TOP)
    phckb = Checkbutton(phasebtn, text="Enab", style="Disab.TCheckbutton", variable=PhADisp, command=PhACheckBox)
    phckb.pack(side=LEFT)
    BuildPhAScreen = Button(phasebtn, text="Phasor Plot", style="W11.TButton", command=MakePhAWindow)
    BuildPhAScreen.pack(side=LEFT)
#
if EnableSpectrumAnalizer > 0:
    freqbtn = Frame( frame2r )
    freqbtn.pack(side=TOP)
    ckb3 = Checkbutton(freqbtn, text="Enab", style="Disab.TCheckbutton", variable=FreqDisp, command=FreqCheckBox)
    ckb3.pack(side=LEFT)
    BuildSpectrumScreen = Button(freqbtn, text="Spectrum Plot", style="W11.TButton", command=MakeSpectrumWindow)
    BuildSpectrumScreen.pack(side=LEFT)
#
if EnableBodePlotter > 0:
    bodebtn = Frame( frame2r )
    bodebtn.pack(side=TOP)
    ckb5 = Checkbutton(bodebtn, text="Enab", style="Disab.TCheckbutton", variable=BodeDisp, command=BodeCheckBox)
    ckb5.pack(side=LEFT)
    BuildBodeScreen = Button(bodebtn, text="Bode Plot", style="W11.TButton", command=MakeBodeWindow)
    BuildBodeScreen.pack(side=LEFT)
#
if EnableImpedanceAnalizer > 0:
    impdbtn = Frame( frame2r )
    impdbtn.pack(side=TOP)
    ckb4 = Checkbutton(impdbtn, text="Enab", style="Disab.TCheckbutton", variable=IADisp, command=IACheckBox)
    ckb4.pack(side=LEFT)
    BuildIAScreen = Button(impdbtn, text="Impedance", style="W11.TButton", command=MakeIAWindow)
    BuildIAScreen.pack(side=LEFT)
#
if EnableOhmMeter > 0:
    dcohmbtn = Frame( frame2r )
    dcohmbtn.pack(side=TOP)
    ckb6 = Checkbutton(dcohmbtn, text="Enab", style="Disab.TCheckbutton", variable=OhmDisp, command=OhmCheckBox)
    ckb6.pack(side=LEFT)
    BuildOhmScreen = Button(dcohmbtn, text="Ohmmeter", style="W11.TButton", command=MakeOhmWindow)
    BuildOhmScreen.pack(side=LEFT)
#
if EnableDmmMeter > 0:
    dmmbtn = Frame( frame2r )
    dmmbtn.pack(side=TOP)
    ckb7 = Checkbutton(dmmbtn, text="Enab", style="Disab.TCheckbutton", variable=DMMDisp, command=DMMCheckBox)
    ckb7.pack(side=LEFT)
    BuildDMMScreen = Button(dmmbtn, text="DMM meter", style="W11.TButton", command=MakeMeterWindow)
    BuildDMMScreen.pack(side=LEFT)
#
# Digital Input / Output Option screens
if EnableDigIO > 0:
    BuildDigScreen = Button(frame2r, text="Digital I/O Screen", style="W17.TButton", command=MakeDigScreen)
    BuildDigScreen.pack(side=TOP)
#
if ShowTraceControls > 0:
    Labelfonttext = "Arial " + str(FontSize) + " bold"
    tracelab = Label(frame2r, text="Traces", font= Labelfonttext)
    tracelab.pack(side=TOP)
    trctrla = Frame( frame2r )
    trctrla.pack(side=TOP)
    if CHANNELS >= 1:
        ckbt1 = Checkbutton(trctrla, text='CH A (1)', style="Strace1.TCheckbutton", variable=ShowC1_V, command=SelectChannels) #
        ckbt1.pack(side=LEFT,fill=X)
    if CHANNELS >= 2:
        ckbt3 = Checkbutton(trctrla, text='CH B (2)', style="Strace2.TCheckbutton", variable=ShowC2_V, command=SelectChannels) #
        ckbt3.pack(side=LEFT,fill=X)
    trctrlc = Frame( frame2r )
    trctrlc.pack(side=TOP)
    if CHANNELS >= 3:
        ckbtc = Checkbutton(trctrlc, text='CH C (3)', style="Strace3.TCheckbutton", variable=ShowC3_V, command=SelectChannels) #
        ckbtc.pack(side=LEFT,fill=X)
    if CHANNELS >= 4:
        ckbtd = Checkbutton(trctrlc, text='CH D (4)', style="Strace4.TCheckbutton", variable=ShowC4_V, command=SelectChannels) #
        ckbtd.pack(side=LEFT,fill=X)
    if EnableLoopBack > 0:
        trctrlbk = Frame( frame2r )
        trctrlbk.pack(side=TOP)
        lbckb = Checkbutton(trctrlbk, text="LoopBack", style="Disab.TCheckbutton", variable=LoopBack, command=LbCheckBox)
        lbckb.pack(side=LEFT)
        LBsb = Spinbox(trctrlbk, cursor='double_arrow', width=5, values=LBList) #, command=LBSpinBox)
        LBsb.bind('<MouseWheel>', onSpinBoxScroll)
        LBsb.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
        LBsb.bind("<Button-5>", onSpinBoxScroll)
        LBsb.pack(side=LEFT)
        LBsb.delete(0,"end")
        LBsb.insert(0,"CH A") # "CH A"
        if ShowBallonHelp > 0:
            loopback_tip = CreateToolTip(lbckb, 'Enable / Disable loopback to AWG output')
            lbselect_tip = CreateToolTip(LBsb, 'Select which scope channel to loopback to AWG output')

#
if ShowBallonHelp > 0:
    try:
        BuildAWGScreen_tip = CreateToolTip(BuildAWGScreen, 'Surface AWG Controls window')
    except:
        donothing()
    try:
        BuildXYScreen_tip = CreateToolTip(BuildXYScreen, 'Open X vs Y plot window')
    except:
        donothing()
    try:
        BuildPhAScreen_tip = CreateToolTip(BuildPhAScreen, 'Open Phase Analyzer window')
    except:
        donothing()
    try:
        BuildSpectrumScreen_tip = CreateToolTip(BuildSpectrumScreen, 'Open Spectrum Analyzer window')
    except:
        donothing()
    try:
        BuildBodeScreen_tip = CreateToolTip(BuildBodeScreen, 'Open Bode plot window')
    except:
        donothing()
    try:
        BuildIAScreen_tip = CreateToolTip(BuildIAScreen, 'Open Impedance Analyzer window')
    except:
        donothing()
    try:
        BuildOhmScreen_tip = CreateToolTip(BuildOhmScreen, 'Open DC Ohmmeter window')
    except:
        donothing()
# Optional plugin tools
if EnableDigitalFilter >0:
    DigFiltScreen = Button(frame2r, text="Digital Filter", style="W17.TButton", command=MakeDigFiltWindow)
    DigFiltScreen.pack(side=TOP)
if EnableCommandInterface > 0:
    CommandLineScreen = Button(frame2r, text="Command Interface", style="W17.TButton", command=MakeCommandScreen)
    CommandLineScreen.pack(side=TOP)
if EnableMeasureScreen > 0:
    MeasureScreen = Button(frame2r, text="Measure Screen", style="W17.TButton", command=MakeMeasureScreen)
    MeasureScreen.pack(side=TOP)
# input probe wigets
prlab = Button(frame2r, text="Adjust Gain / Offset", command=MakeResDivWindow)
prlab.pack(side=TOP)
# Input Probes sub frame
if CHANNELS >= 1:
    ProbeA = Frame( frame2r )
    ProbeA.pack(side=TOP)
    gain1lab = Button(ProbeA, text="CA-V", width=4, style="Ctrace1.TButton", command=ReSetAGO) 
    gain1lab.pack(side=LEFT,fill=X)
    CHAVGainEntry = Entry(ProbeA, width=5, cursor='double_arrow')
    CHAVGainEntry.bind('<Return>', onTextKey)
    CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
    CHAVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHAVGainEntry.bind("<Button-5>", onTextScroll)
    CHAVGainEntry.bind('<Key>', onTextKey)
    CHAVGainEntry.pack(side=LEFT)
    CHAVGainEntry.delete(0,"end")
    CHAVGainEntry.insert(0,1.0)
    CHAVOffsetEntry = Entry(ProbeA, width=5, cursor='double_arrow')
    CHAVOffsetEntry.bind('<Return>', onTextKey)
    CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
    CHAVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHAVOffsetEntry.bind("<Button-5>", onTextScroll)
    CHAVOffsetEntry.bind('<Key>', onTextKey)
    CHAVOffsetEntry.pack(side=LEFT)
    CHAVOffsetEntry.delete(0,"end")
    CHAVOffsetEntry.insert(0,0.0)
#
if CHANNELS >= 2:
    ProbeB = Frame( frame2r )
    ProbeB.pack(side=TOP)
    gain2lab = Button(ProbeB, text="CB-V", width=4, style="Ctrace2.TButton", command=ReSetBGO) 
    gain2lab.pack(side=LEFT,fill=X)
    CHBVGainEntry = Entry(ProbeB, width=5, cursor='double_arrow')
    CHBVGainEntry.bind('<Return>', onTextKey)
    CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
    CHBVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHBVGainEntry.bind("<Button-5>", onTextScroll)
    CHBVGainEntry.bind('<Key>', onTextKey)
    CHBVGainEntry.pack(side=LEFT)
    CHBVGainEntry.delete(0,"end")
    CHBVGainEntry.insert(0,1.0)
    CHBVOffsetEntry = Entry(ProbeB, width=5, cursor='double_arrow')
    CHBVOffsetEntry.bind('<Return>', onTextKey)
    CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
    CHBVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHBVOffsetEntry.bind("<Button-5>", onTextScroll)
    CHBVOffsetEntry.bind('<Key>', onTextKey)
    CHBVOffsetEntry.pack(side=LEFT)
    CHBVOffsetEntry.delete(0,"end")
    CHBVOffsetEntry.insert(0,0.0)
#
if CHANNELS >= 3:
    ProbeC = Frame( frame2r )
    ProbeC.pack(side=TOP)
    gain3lab = Button(ProbeC, text="CC-V", width=4, style="Ctrace3.TButton", command=ReSetCGO) 
    gain3lab.pack(side=LEFT,fill=X)
    CHCVGainEntry = Entry(ProbeC, width=5, cursor='double_arrow')
    CHCVGainEntry.bind('<Return>', onTextKey)
    CHCVGainEntry.bind('<MouseWheel>', onTextScroll)
    CHCVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHCVGainEntry.bind("<Button-5>", onTextScroll)
    CHCVGainEntry.bind('<Key>', onTextKey)
    CHCVGainEntry.pack(side=LEFT)
    CHCVGainEntry.delete(0,"end")
    CHCVGainEntry.insert(0,1.0)
    CHCVOffsetEntry = Entry(ProbeC, width=5, cursor='double_arrow')
    CHCVOffsetEntry.bind('<Return>', onTextKey)
    CHCVOffsetEntry.bind('<MouseWheel>', onTextScroll)
    CHCVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHCVOffsetEntry.bind("<Button-5>", onTextScroll)
    CHCVOffsetEntry.bind('<Key>', onTextKey)
    CHCVOffsetEntry.pack(side=LEFT)
    CHCVOffsetEntry.delete(0,"end")
    CHCVOffsetEntry.insert(0,0.0)
#
if CHANNELS >= 4:
    ProbeD = Frame( frame2r )
    ProbeD.pack(side=TOP)
    gain4lab = Button(ProbeD, text="CD-V", width=4, style="Ctrace4.TButton", command=ReSetDGO) 
    gain4lab.pack(side=LEFT,fill=X)
    CHDVGainEntry = Entry(ProbeD, width=5, cursor='double_arrow')
    CHDVGainEntry.bind('<Return>', onTextKey)
    CHDVGainEntry.bind('<MouseWheel>', onTextScroll)
    CHDVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHDVGainEntry.bind("<Button-5>", onTextScroll)
    CHDVGainEntry.bind('<Key>', onTextKey)
    CHDVGainEntry.pack(side=LEFT)
    CHDVGainEntry.delete(0,"end")
    CHDVGainEntry.insert(0,1.0)
    CHDVOffsetEntry = Entry(ProbeD, width=5, cursor='double_arrow')
    CHDVOffsetEntry.bind('<Return>', onTextKey)
    CHDVOffsetEntry.bind('<MouseWheel>', onTextScroll)
    CHDVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHDVOffsetEntry.bind("<Button-5>", onTextScroll)
    CHDVOffsetEntry.bind('<Key>', onTextKey)
    CHDVOffsetEntry.pack(side=LEFT)
    CHDVOffsetEntry.delete(0,"end")
    CHDVOffsetEntry.insert(0,0.0)
#
# Add a pair of user entry wigets
if EnableUserEntries > 0:
    UserEnt = Frame( frame2r )
    UserEnt.pack(side=TOP)
    userentlab = Button(UserEnt, text="User", width=4, style="W4.TButton")
    userentlab.pack(side=LEFT,fill=X)
    User1Entry = Entry(UserEnt, width=5, cursor='double_arrow')
    User1Entry.bind('<Return>', onTextKey)
    User1Entry.bind('<MouseWheel>', onTextScroll)
    User1Entry.bind("<Button-4>", onTextScroll)# with Linux OS
    User1Entry.bind("<Button-5>", onTextScroll)
    User1Entry.bind('<Key>', onTextKey)
    User1Entry.pack(side=LEFT)
    User1Entry.delete(0,"end")
    User1Entry.insert(0,0.0)
    User2Entry = Entry(UserEnt, width=5, cursor='double_arrow')
    User2Entry.bind('<Return>', onTextKey)
    User2Entry.bind('<MouseWheel>', onTextScroll)
    User2Entry.bind("<Button-4>", onTextScroll)# with Linux OS
    User2Entry.bind("<Button-5>", onTextScroll)
    User2Entry.bind('<Key>', onTextKey)
    User2Entry.pack(side=LEFT)
    User2Entry.delete(0,"end")
    User2Entry.insert(0,0.0)
# add Alice logo Don't mess with this bit map data!
ALICElogo = "" ""
logo = PhotoImage(data=ALICElogo)
Alice1 = Label(frame2r, image=logo, anchor= "sw", compound="top") # , height=49, width=116
Alice1.pack(side=TOP)

# Bottom Buttons
# Voltage channel A
#
if CHANNELS >= 1:
    if ButtonOrder == 1:
        CHAlab = Button(frame3, text="A V/Div", style="Rtrace1.TButton", command=SetScaleA)
        CHAlab.pack(side=LEFT)
    CHAsb = Spinbox(frame3, cursor='double_arrow', width=6, values=CHvpdiv, command=BCHAlevel)
    CHAsb.bind('<MouseWheel>', onSpinBoxScroll)
    CHAsb.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
    CHAsb.bind("<Button-5>", onSpinBoxScroll)
    CHAsb.pack(side=LEFT)
    CHAsb.delete(0,"end")
    CHAsb.insert(0,CH1VRange) # "500mV"
    #
    if ButtonOrder == 0:
        CHAlab = Button(frame3, text="A V/Div", style="Rtrace1.TButton", command=SetScaleA)
        CHAlab.pack(side=LEFT)
    #
    if ButtonOrder == 1:
        CHAofflab = Button(frame3, text="A V Pos", style="Rtrace1.TButton", command=SetVAPoss)
        CHAofflab.pack(side=LEFT)
    CHAVPosEntry = Entry(frame3, width=5, cursor='double_arrow')
    CHAVPosEntry.bind("<Return>", BOffsetA)
    CHAVPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
    CHAVPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHAVPosEntry.bind("<Button-5>", onTextScroll)
    CHAVPosEntry.bind('<Key>', onTextKey)
    CHAVPosEntry.pack(side=LEFT)
    CHAVPosEntry.delete(0,"end")
    CHAVPosEntry.insert(0, 0.0)
    if ButtonOrder == 0:
        CHAofflab = Button(frame3, text="A V Pos", style="Rtrace1.TButton", command=SetVAPoss)
        CHAofflab.pack(side=LEFT)
# Voltage channel B
# Input config modes
if CHANNELS >= 2:
    if ButtonOrder == 1:
        CHBlab = Button(frame3, text="B V/Div", style="Strace2.TButton", command=SetScaleB)
        CHBlab.pack(side=LEFT)
    CHBsb = Spinbox(frame3, width=6, cursor='double_arrow', values=CHvpdiv, command=BCHBlevel)
    CHBsb.bind('<MouseWheel>', onSpinBoxScroll)
    CHBsb.bind('<Button-4>', onSpinBoxScroll)
    CHBsb.bind('<Button-4>', onSpinBoxScroll)
    CHBsb.pack(side=LEFT)
    CHBsb.delete(0,"end")
    CHBsb.insert(0,CH2VRange) # "500mV"
    #
    if ButtonOrder == 0:
        CHBlab = Button(frame3, text="B V/Div", style="Strace2.TButton", command=SetScaleB)
        CHBlab.pack(side=LEFT)
    #
    if ButtonOrder == 1:
        CHBofflab = Button(frame3, text="B V Pos", style="Rtrace2.TButton", command=SetVBPoss)
        CHBofflab.pack(side=LEFT)
    CHBVPosEntry = Entry(frame3, width=5, cursor='double_arrow')
    CHBVPosEntry.bind("<Return>", BOffsetB)
    CHBVPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
    CHBVPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHBVPosEntry.bind("<Button-5>", onTextScroll)
    CHBVPosEntry.bind('<Key>', onTextKey)
    CHBVPosEntry.pack(side=LEFT)
    CHBVPosEntry.delete(0,"end")
    CHBVPosEntry.insert(0,0.0)
    if ButtonOrder == 0:
        CHBofflab = Button(frame3, text="B V Pos", style="Rtrace2.TButton", command=SetVBPoss)
        CHBofflab.pack(side=LEFT)
# 
# Math controls
if ButtonOrder == 1:
    CHMlab = Button(frame3, text="Math V/Div", style="Rtrace5.TButton") #, command=SetScaleB)
    CHMlab.pack(side=LEFT)
CHMsb = Spinbox(frame3, width=6, cursor='double_arrow', values=CHvpdiv) #, command=BCHBlevel)
CHMsb.bind('<MouseWheel>', onSpinBoxScroll)
CHMsb.bind('<Button-4>', onSpinBoxScroll)
CHMsb.bind('<Button-4>', onSpinBoxScroll)
CHMsb.pack(side=LEFT)
CHMsb.delete(0,"end")
CHMsb.insert(0,"500mV")
#
if ButtonOrder == 0:
    CHMlab = Button(frame3, text="Math V/Div", style="Rtrace5.TButton") #, command=SetScaleB)
    CHMlab.pack(side=LEFT)
#
if ButtonOrder == 1:
    CHMofflab = Button(frame3, text="Math Pos", style="Rtrace5.TButton")#, command=SetVBPoss)
    CHMofflab.pack(side=LEFT)
CHMVPosEntry = Entry(frame3, width=5, cursor='double_arrow')
CHMVPosEntry.bind("<Return>", BOffsetB)
CHMVPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
CHMVPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHMVPosEntry.bind("<Button-5>", onTextScroll)
CHMVPosEntry.bind('<Key>', onTextKey)
CHMVPosEntry.pack(side=LEFT)
CHMVPosEntry.delete(0,"end")
CHMVPosEntry.insert(0,0.0)
#
if ButtonOrder == 0:
    CHMofflab = Button(frame3, text="Math Pos", style="Rtrace5.TButton") #, command=SetVBPoss)
    CHMofflab.pack(side=LEFT)
#
# Scope PGA controls
if EnablePGAGain == 1:
    if CHANNELS >= 1:
        CHApgalab = Button(frame3, text="A Gain", style="Rtrace1.TButton") #, command=SetScaleB)
        CHApgalab.pack(side=RIGHT)
        CHApgasb = Spinbox(frame3, width=3, cursor='double_arrow', values=ScopePGAGain, command=BCHAPGAgain)
        CHApgasb.bind('<MouseWheel>', onSpinBoxScroll)
        CHApgasb.bind('<Button-4>', onSpinBoxScroll)
        CHApgasb.bind('<Button-4>', onSpinBoxScroll)
        CHApgasb.pack(side=RIGHT)
        CHApgasb.delete(0,"end")
        CHApgasb.insert(0,"1")
#
if EnablePGAGain >= 2:
    if CHANNELS >= 2:
        CHBpgalab = Button(frame3, text="B Gain", style="Rtrace2.TButton") #, command=SetScaleB)
        CHBpgalab.pack(side=RIGHT)
        CHBpgasb = Spinbox(frame3, width=3, cursor='double_arrow', values=ScopePGAGain, command=BCHBPGAgain)
        CHBpgasb.bind('<MouseWheel>', onSpinBoxScroll)
        CHBpgasb.bind('<Button-4>', onSpinBoxScroll)
        CHBpgasb.bind('<Button-4>', onSpinBoxScroll)
        CHBpgasb.pack(side=RIGHT)
        CHBpgasb.delete(0,"end")
        CHBpgasb.insert(0,"1")
#
# Voltage channel C
#
if CHANNELS >= 3:
    if ButtonOrder == 1:
        CHClab = Button(frame4, text="C V/Div", style="Rtrace3.TButton", command=SetScaleC)
        CHClab.pack(side=LEFT)
    CHCsb = Spinbox(frame4, cursor='double_arrow', width=6, values=CHvpdiv, command=BCHClevel)
    CHCsb.bind('<MouseWheel>', onSpinBoxScroll)
    CHCsb.bind("<Button-4>", onSpinBoxScroll)# with Linux OS
    CHCsb.bind("<Button-5>", onSpinBoxScroll)
    CHCsb.pack(side=LEFT)
    CHCsb.delete(0,"end")
    CHCsb.insert(0,CH3VRange) # "500mV"
    #
    if ButtonOrder == 0:
        CHClab = Button(frame4, text="C V/Div", style="Rtrace3.TButton", command=SetScaleC)
        CHClab.pack(side=LEFT)
    #
    if ButtonOrder == 1:
        CHCofflab = Button(frame4, text="C V Pos", style="Rtrace3.TButton", command=SetVCPoss)
        CHCofflab.pack(side=LEFT)
    CHCVPosEntry = Entry(frame4, width=5, cursor='double_arrow')
    CHCVPosEntry.bind("<Return>", BOffsetC)
    CHCVPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
    CHCVPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHCVPosEntry.bind("<Button-5>", onTextScroll)
    CHCVPosEntry.bind('<Key>', onTextKey)
    CHCVPosEntry.pack(side=LEFT)
    CHCVPosEntry.delete(0,"end")
    CHCVPosEntry.insert(0, 2.5)
    if ButtonOrder == 0:
        CHCofflab = Button(frame4, text="C V Pos", style="Rtrace3.TButton", command=SetVCPoss)
        CHCofflab.pack(side=LEFT)
# Voltage channel D
# Input config modes
if CHANNELS >= 4:
    if ButtonOrder == 1:
        CHDlab = Button(frame4, text="D V/Div", style="Strace4.TButton", command=SetScaleD)
        CHDlab.pack(side=LEFT)
    CHDsb = Spinbox(frame4, width=6, cursor='double_arrow', values=CHvpdiv, command=BCHDlevel)
    CHDsb.bind('<MouseWheel>', onSpinBoxScroll)
    CHDsb.bind('<Button-4>', onSpinBoxScroll)
    CHDsb.bind('<Button-4>', onSpinBoxScroll)
    CHDsb.pack(side=LEFT)
    CHDsb.delete(0,"end")
    CHDsb.insert(0,CH4VRange) # "500mV"
    #
    if ButtonOrder == 0:
        CHDlab = Button(frame4, text="D V/Div", style="Strace4.TButton", command=SetScaleD)
        CHDlab.pack(side=LEFT)
    #
    if ButtonOrder == 1:
        CHDofflab = Button(frame4, text="B V Pos", style="Rtrace2.TButton", command=SetVDPoss)
        CHDofflab.pack(side=LEFT)
    CHDVPosEntry = Entry(frame4, width=5, cursor='double_arrow')
    CHDVPosEntry.bind("<Return>", BOffsetD)
    CHDVPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
    CHDVPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
    CHDVPosEntry.bind("<Button-5>", onTextScroll)
    CHDVPosEntry.bind('<Key>', onTextKey)
    CHDVPosEntry.pack(side=LEFT)
    CHDVPosEntry.delete(0,"end")
    CHDVPosEntry.insert(0,2.5)
    if ButtonOrder == 0:
        CHDofflab = Button(frame4, text="D V Pos", style="Rtrace4.TButton", command=SetVDPoss)
        CHDofflab.pack(side=LEFT)
# PGA controls
if EnablePGAGain >= 3:
    if CHANNELS >= 3:
        CHCpgalab = Button(frame4, text="C Gain", style="Rtrace3.TButton") #, command=SetScaleB)
        CHCpgalab.pack(side=RIGHT)
        CHCpgasb = Spinbox(frame4, width=3, cursor='double_arrow', values=ScopePGAGain, command=BCHCPGAgain)
        CHCpgasb.bind('<MouseWheel>', onSpinBoxScroll)
        CHCpgasb.bind('<Button-4>', onSpinBoxScroll)
        CHCpgasb.bind('<Button-4>', onSpinBoxScroll)
        CHCpgasb.pack(side=RIGHT)
        CHCpgasb.delete(0,"end")
        CHCpgasb.insert(0,"1")
    #
if EnablePGAGain >= 4:
    if CHANNELS >= 4:
        CHDpgalab = Button(frame4, text="D Gain", style="Rtrace4.TButton") #, command=SetScaleB)
        CHDpgalab.pack(side=RIGHT)
        CHDpgasb = Spinbox(frame4, width=3, cursor='double_arrow', values=ScopePGAGain, command=BCHDPGAgain)
        CHDpgasb.bind('<MouseWheel>', onSpinBoxScroll)
        CHDpgasb.bind('<Button-4>', onSpinBoxScroll)
        CHDpgasb.bind('<Button-4>', onSpinBoxScroll)
        CHDpgasb.pack(side=RIGHT)
        CHDpgasb.delete(0,"end")
        CHDpgasb.insert(0,"1")
    #
if ShowBallonHelp > 0:
    prlab_tip = CreateToolTip(prlab, 'Open input divider calculator')
    if CHANNELS >= 1:
        CHAlab_tip = CreateToolTip(CHAlab, 'Select Ch A-V vertical range/position axis to be used for markers and drawn color')
        CHAofflab_tip = CreateToolTip(CHAofflab, 'Set Ch A-V position to DC average of signal')
        gain1lab_tip = CreateToolTip(gain1lab, 'Reset Gain to 1.0 and Offset to 0.0')
    if CHANNELS >= 2:
        CHBlab_tip = CreateToolTip(CHBlab, 'Select Ch B-V vertical range/position axis to be used for markers and drawn color')
        CHBofflab_tip = CreateToolTip(CHBofflab, 'Set Ch B-V position to DC average of signal')
        gain2lab_tip = CreateToolTip(gain2lab, 'Reset Gain to 1.0 and Offset to 0.0')
    if CHANNELS >= 3:
        CHClab_tip = CreateToolTip(CHClab, 'Select Ch C-V vertical range/position axis to be used for markers and drawn color')
        CHCofflab_tip = CreateToolTip(CHCofflab, 'Set Ch C-V position to DC average of signal')
        gain3lab_tip = CreateToolTip(gain3lab, 'Reset Gain to 1.0 and Offset to 0.0')
    if CHANNELS >= 4:
        CHDlab_tip = CreateToolTip(CHDlab, 'Select Ch D-V vertical range/position axis to be used for markers and drawn color')
        CHDofflab_tip = CreateToolTip(CHDofflab, 'Set Ch D-V position to DC average of signal')
        gain4lab_tip = CreateToolTip(gain4lab, 'Reset Gain to 1.0 and Offset to 0.0')
#
root.geometry('+300+0')
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
# ===== Initalize device ======
if not numpy_found:
    root.update()
    showwarning("WARNING","Numpy not installed?!")
    root.destroy()
    exit()
#
if EnableScopeOnly == 0:
    if AWGChannels > 0:
        MakeAWGWindow() # build AWG window
else:
    AWGScreenStatus.set(1)
#
BLoadConfig("alice-last-config.cfg") # load configuration from last session
if LocalLanguage != "English":
    BLoadConfig(LocalLanguage) # load local language configuration 
#
if Sucess:
    # Get_Data() # do a dummy first data capture
    bcon.configure(text="Conn", style="GConn.TButton")
    BTime() # initally set Sample Rate by Horz Time base
    BSetTrigEdge()
    BSetTriggerSource()
    BTriglevel() # set trigger level
    MakeAWGwaves()
#
# ================ Call main routine ===============================
#
root.update() # Activate updated screens
# Start sampling
#
Analog_In()


