# Pluto SDR

This repo is a compilation of code for the ADALM-PLUTO SDR module for project research of the beamforming 
concept. Most of this code I compiled from other sources so it was all in one place to minimize search time.

<div align="center">

<img src="./assets/ADALM-Pluto.png" alt="Pluto SDR" width="600"/><br>

<small>
    <a href="https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/adalm-pluto.html">
        Image Source
    </a>
</small>

</div>

## Sources:

Pluto SDR Tools and Overview:
 - [Overview and Introduction](https://wiki.analog.com/university/tools/pluto)

Pluto SDR Quick Start:
 - [Quick Start Resources](https://wiki.analog.com/university/tools/pluto/users/quick_start)

Pluto SDR Firmware Updates:
 - [Pluto/M2k Firmware](https://wiki.analog.com/university/tools/pluto/users/firmware)

Enable Dual Receive, Dual Transmit and Expand Tuning Range to 0.7 - 6.0GHz for Rev C and newer Pluto SDR:
 - Video: [Enable Dual TX & Dual RX](https://www.youtube.com/watch?v=ph0Kv4SgSuI)
 - Code: [Jon Kraft: Pluto SDR Labs](https://github.com/jonkraft/PlutoSDR_Labs/tree/master)
 - Settings Table: [Environmental Settings](https://wiki.analog.com/university/tools/pluto/devs/booting)
     - Use PuTTY for Windows or a Terminal in Linux for shell access.
     - In my case, I connected via the serial COM port with PuTTY in Windows 10.

Build Your Own Phased Array Beamformer using Pluto SDR:
 - Video: [Basic Prototype](https://www.youtube.com/watch?v=2QXKuEYR4Bw)
 - Code: [Jon Kraft: Pluto Beamformer](https://github.com/jonkraft/Pluto_Beamformer)
 - Video: [Understanding and Prototyping](https://www.youtube.com/watch?v=0hnWfTvETcU)
 - Code: [Jon Kraft: Phased Array Workshop](https://github.com/jonkraft/PhasedArray)
 - Video: [Jon Kraft: Rapid Phased Array Prototyping](https://www.youtube.com/watch?v=B_icccUpxV0)

PyADI-IIO: Python for ADI Industrial I/O Devices:
 - Web Docs: [AD936x Hardware](https://analogdevicesinc.github.io/pyadi-iio/devices/adi.ad936x.html)
 - Code: [Examples, Test, RF](https://github.com/analogdevicesinc/pyadi-iio/tree/master/examples) Folders.

ADI Kuiper Linux for Raspberry Pi:
 - [Information and Downloads](https://wiki.analog.com/resources/tools-software/linux-software/kuiper-linux)
 - [Pre-Configured Image](https://download.analog.com/phased-array-lab/raspi.7z)

Basic Raspberry Pi Install From Scratch:
 - [RPi 3B+ Bare Install](https://github.com/jonkraft/Pluto-Install-for-Raspberry-Pi)

## Other Resources:

 - Phased Array Applications: [ADI Phased Arrays](https://www.analog.com/en/applications/markets/aerospace-and-defense-pavilion-home/phased-array-solution.html)
 - Coding Docs: [Pluto SDR in Python](https://pysdr.org/content/pluto.html)
 - Presentations: [Advances in Phased Array Analog Beamforming Solutions](https://ez.analog.com/webinar/c/e/182)
 - Archived Articles: [DIY Radio: Jon Kraft](https://ez.analog.com/tags/DIYRadio)
 - Also see the informational documents posted in the [assets-docs](./assets-docs/) folder of this repo.
 - Video: [What Is Beamforming?](https://www.youtube.com/watch?v=VOGjHxlisyo)
 - Video: [What Are Phased Arrays?](https://www.youtube.com/watch?v=9WxWun0E-PM)
 - Video: [Why Is Digital Beamforming Useful?](https://www.youtube.com/watch?v=Hb6BhqOgmAI)
 - Book: [SDR For Engineers](https://www.analog.com/en/education/education-library/software-defined-radio-for-engineers.html)
 - Books: [Field Expedient SDR Volumes 1-3](https://www.factorialabs.com/fieldxp/)

## Status:

![GitHub repo size](https://img.shields.io/github/repo-size/ADolbyB/pluto-sdr?logo=Github&label=Repo%20Size)