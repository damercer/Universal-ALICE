# Universal-ALICE
Repository for the Python source code and hardware level specification files
#
The main Universal ALICE GUI is written in Python (3.x) and depends only on the more or less generic standardly available Python plugin libraries (such as Tcl/Tk, numpy, pyplot etc.). The hardware specific interface level would generally also be implemented in Python plus any plugin libraries (such as pyserial, pyaudio etc.) with possible C extensions depending on the target hardware. Under the hardware driver level are any specific host USB drivers for the various operating systems / host platforms and of course the firmware that runs on the target data acquisition hardware board (micro-controller). Some hardware specific tool chains or drivers might need to be obtained directly from the hardware vendors and not necessarily hosted on this archive.