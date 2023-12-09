# Universal-ALICE
With the goal of "Instrumentation for Every Student" in mind this project is intended to lower all barriers to providing a hardware and software platform for teaching electronic circuits to engineering students. Every student should have access to affordable hardware and software to measure their experiments.
This project offers a free open source software user interface that is compatable with hardware produced in large quantities at low cost (ranging from $5 to $20) from multiple suppliers.
#
Repository for the Python source code and hardware level specification files.
#
The main Universal ALICE GUI is written in Python (3.x) and depends only on the more or less generic standardly available Python plugin libraries (such as Tcl/Tk, numpy, pyplot etc.). The hardware specific interface level is also generally implemented in Python plus any plugin libraries (such as pyserial, Pyusb, pyaudio etc.) with possible C extensions depending on the target hardware. Under the hardware driver level are any specific host USB drivers for the various operating systems / host platforms and of course the firmware that runs on the target data acquisition hardware board (micro-controller). Some hardware specific tool chains or drivers might need to be obtained directly from the hardware vendors and not necessarily hosted on this archive.

![Screenshot mainscreen](/main_screenshot.png)
#
Currently available hardware interfaces (some are works in progress):

* Arduino compatible microcontroler boards:
  + Seeed Studio XIAO SAMD21
  + Seeed Studio XIAO RP-2040
    - With external SPI DAC or PWM analog AWG output
  + Raspberry Pi Pico RP-2040
    - With external R/2R DAC or SPI DAC or PWM analog AWG output
  + Adafruit QT Pi - SAMD21
  + Adafruit Trinket M0
  + Adafruit ItsyBitsy M0 Express
* Infineon-Cypress PSoC 5 kits:
  + CY8CKIT-059
  + CY8CKIT-043
  + CY8CKIT-044
* Bench Instruments:
  + Multicomp pro MP720781
