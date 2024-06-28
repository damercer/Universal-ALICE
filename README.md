# Universal-ALICE
With the goal of "Instrumentation for Every Student" in mind this project is intended to lower all barriers to providing a hardware and software platform for teaching electronic circuits to engineering students. Every student should have access to affordable hardware and software to measure their experiments.
This project offers a free open source software user interface that is compatible with hardware produced in large quantities at low cost (ranging from $5 to $20) from multiple suppliers.
#
Repository for the Python source code and hardware level specification files.
#
The main Universal ALICE GUI is written in Python (3.x) and depends only on the more or less generic standardly available Python plugin libraries (such as Tcl/Tk, numpy, pyplot etc.). The hardware specific interface level is also generally implemented in Python plus any plugin libraries (such as pyserial, Pyusb, pyaudio etc.) with possible C extensions depending on the target hardware. Under the hardware driver level are any specific host USB drivers for the various operating systems / host platforms and of course the firmware that runs on the target data acquisition hardware board (micro-controller). Some hardware specific tool chains or drivers might need to be obtained directly from the hardware vendors and not necessarily hosted on this archive.

![Screenshot mainscreen](/main_screenshot.png)
ALICE Main Scope Screen

![pi pico spi dac](/pi-pico-solder-board-1.png)
Solder Breadboard with Pi-Pico and dual SPI DAC

#
Currently available hardware interfaces (some are works in progress):

* Arduino compatible microcontroler boards:
  + Adafruit QT Pi - SAMD21
  + Adafruit Trinket M0 (ATSAMD21)
  + Adafruit ItsyBitsy M0 Express (ATSAMD21)
  + Adafruit ItsyBitsy M4 Express (ATSAMD51)
  + Raspberry Pi Pico RP-2040
    - With external R/2R DAC or SPI DAC or PWM analog AWG output
  + Seeed Studio XIAO SAMD21
  + Seeed Studio XIAO RP-2040
    - With external SPI DAC or PWM analog AWG output
* Infineon-Cypress PSoC 5 kits:
  + CY8CKIT-059
  + CY8CKIT-043
  + CY8CKIT-044
* Bench Instruments:
  + Multicomp pro MP720781
  + Owon SDS1104 (VEVOR DS1104)

If you are not a technical individual or highly familiar with computer operating systems and you have your choice of computers, a Windows computer is highly recommended. You will usually run into fewer issues, if any, with that operating system.

Known Issues: If your computer encrypts files saved on external storge devices (USB disk drives) then the UF2 Bootloader method of flashing firmware to micro-controller boards will not work. You would need to use a different computer that does not encrypt files or consult your local system administrator.

Linux Operating system: On Linux computers access to USB based serial comms devices is not allowed for non root users by default. A udev rules file needs to be added. Place the 99-arduino.rules from this repository in etc/udev/rules.d

It contains one line per board / vendor:

SUBSYSTEMS=="usb", ATTRS{idVendor}=="802F", ATTRS{idProduct}=="2886", GROUP="dialout", MODE="0666"

The above idVendor value is board / vendor specific and may need to be adjusted to match your specific board(s). The one above is specifically for the XIAO SAMD21 board.

If this rules file does not work on your version of Linux there may be other things like this that work. Searching the web on how to make serial USB devices work may provide an alternate solution or consult with your local Linux expert.
