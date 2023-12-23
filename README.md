# SDR Beamforming

This is a research project repo for Software Defined Radio Phased Array Beamforming. Previously, we had extensively researched the PlutoSDR to evaluate it for a beamforming project. That was previously the `pluto-sdr` repo, which is now an additional folder inside this repo. Currently, we are researching the KrakenSDR as a stepping stone platform to a complete beamforming system.

## KrakenSDR Resources:

<div align="center">
    <p>
        KrakenSDR 5 Channel Internal Breakdown:
    </p>
<img src="./KrakenSDR/assets/KrakenSDR-1.png" alt="Pluto SDR" width="500"/><br>

<small>
    <a href="https://github.com/krakenrf/krakensdr_docs/wiki">
        Image Source
    </a>
</small>

</div>

- [KrakenRF Website](https://www.krakenrf.com/)
- [KrakenRF CrowdSupply Page](https://www.crowdsupply.com/krakenrf/krakensdr)
- [KrakenRF GitHub Page](https://github.com/krakenrf)
- [Kraken YT Page](https://www.youtube.com/@thekraken2086)
- [Kraken RPi 4 Pre-Configured Image](https://github.com/krakenrf/krakensdr_doa/releases)
- [Ubuntu VirtualBox Pre-Configured VMs](https://mega.nz/folder/MaFCyAyJ#TCl1uCNVAHkCbnSsrG56bQ)&nbsp;&nbsp;<strong>See Notes on VM Below</strong>
     - Use with VirtualBox 7.0 or later.
     - For Linux Hosts: `sudo adduser $USER vboxusers`
     - Ubuntu Username: `krakenrf`, Password: `krakensdr`
- [KrakenSDR Documentation Wiki](https://github.com/krakenrf/krakensdr_docs/wiki)
- A 3D Printable [Antenna Array Template](https://www.thingiverse.com/thing:5787042) on Thingiverse
- [Kraken Vehicle Direction Finding Video](https://www.youtube.com/watch?v=OY16y1Rl86g)
    - Compare to Rohde & Schwarz Live [Interference Hunting Demonstration](https://www.youtube.com/watch?v=IIH9OiLGN2g)
- [Passive Radar Applications](http://gbppr.net/kraken/index.html)
- [KrakenSDR RDF Android App](https://play.google.com/store/apps/details?id=com.krakensdr.krakendoa)
- [Arrow Antennas 5 Element Dipole Array](https://www.arrowantennas.com/arrowii/krsdr.html) for direction finding. Tower mount for the 5 channel KrakenSDR.
- [GNU Radio Source Block](https://github.com/krakenrf/gr-krakensdr) for the KrakenSDR.
- [Kraken DSP Direction of Arrival](https://github.com/krakenrf/krakensdr_doa) Repo.

### Notes on the Preconfigured VirtualBox VM:

- After importing the OVA appliance to VBox 7.0+:
    - I allocate 4 vCPUs & 8192 MB of RAM to my Kraken VM.
    - Increase the display video memory to 128 MB.
    - Make sure to test run and UPDATE the image (this may take awhile).
        - In Ubuntu, if this does not happen automatically, then click `Activities` in the top right corner and search for `Software Updater`.
- Next, we need to fix the 16 MB `usbfs_memory_mb` that will prevent using all 5 RTL-SDRs in the KrakenSDR.
    - Temporary Fix (Does Not Survive Reboot):
        - open a terminal and login as root: `sudo su` and enter the password.
        - now enter `echo 0 > /sys/module/usbcore/parameters/usbfs_memory_mb`
        - now verify the change by logging out of the root terminal (CTRL + D) and entering `cat /sys/module/usbcore/parameters/usbfs_memory_mb` and we should now see the value `0`.


## PlutoSDR Resources:

- [Previous PlutoSDR README Page](./PlutoSDR/README.md)

## Other Resources:

Useful SDR Programs:
- Linux:
     - [GNU Radio](https://wiki.gnuradio.org/index.php/InstallingGR) and [GNU Radio Tutorials](https://wiki.gnuradio.org/index.php?title=Tutorials)
     - [GQRX](https://gqrx.dk/)
- Windows:
     - [AirSpy: SDR Sharp](https://airspy.com/download/) 
         - [Add'l Plugins For SDR Sharp](https://www.rtl-sdr.com/sdrsharp-plugins/)
         - [Frequency Manager](https://www.freqmgrsuite.com/) For SDR Sharp
     - [SDR Console](https://www.sdr-radio.com/)
     - [HDSDR](http://www.hdsdr.de/)
     - [DSD+](https://www.dsdplus.com/) Digital Signal Decoder.
         - Note that v1.101 is free, but the latest version is a paid one-time subscription fee.
         - Also see [This RadioReference](https://forums.radioreference.com/threads/need-beginners-guide-to-dsd-fastlane.463963/) Get Started Guide.
     - [Unitrunker Digital Decoder](http://www.unitrunker.com/) 

Coding Docs:
- [PySDR Python Docs](https://pysdr.org/index.html)

Applications of Phased Arrays: 
- [ADI Phased Arrays](https://www.analog.com/en/applications/markets/aerospace-and-defense-pavilion-home/phased-array-solution.html)

Videos:
- [Advances in Phased Array Analog Beamforming Solutions](https://ez.analog.com/webinar/c/e/182)
- [What Is Beamforming?](https://www.youtube.com/watch?v=VOGjHxlisyo)
- [What Are Phased Arrays?](https://www.youtube.com/watch?v=9WxWun0E-PM)
- [Why Is Digital Beamforming Useful?](https://www.youtube.com/watch?v=Hb6BhqOgmAI)
- [Software Defined Radio Systems and Analysis Playlist](https://www.youtube.com/playlist?list=PLBfTSoOqoRnOTBTLahXBlxaDUNWdZ3FdS): 26 Lectures

SDR Online Lessons:
- [Great Scott Gadgets](https://greatscottgadgets.com/sdr/) Tutorials

Articles: 
- [DIY Radio: Jon Kraft](https://ez.analog.com/tags/DIYRadio)

Books: 
- [SDR For Engineers](https://www.analog.com/en/education/education-library/software-defined-radio-for-engineers.html)
- [Field Expedient SDR Volumes 1-3](https://www.factorialabs.com/fieldxp/)
- [Phased Array Antenna Handbook](http://twanclik.free.fr/electricity/electronic/pdfdone11/Phased.Array.Antenna.Handbook.Artech.House.Publishers.Second.Edition.eBook-kB.pdf)
- [Antenna Theory Analysis and Design](https://cds.cern.ch/record/1416310/files/047166782X_TOC.pdf)

## Status:

![GitHub repo size](https://img.shields.io/github/repo-size/ADolbyB/sdr-beamforming?logo=Github&label=Repo%20Size)