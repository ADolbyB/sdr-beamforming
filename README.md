# SDR Beamforming

This is a research project repo for Software Defined Radio Phased Array Beamforming. Previously, we had extensively researched the PlutoSDR to evaluate it for a beamforming project. That was previously the `pluto-sdr` repo, which is now an additional folder inside this repo. Currently, we are researching the KrakenSDR as a stepping stone platform to a complete beamforming system.

## Project GUI: `PyQT_GUI`

<div align="center">
<p>

Please visit the [`PyQT_GUI`](https://github.com/RayzrReptile/PyQT_GUI) Project Repo for more information.

</p>

<img src="./phaseCoherence/assets/GUI_initial_mockup.png" alt="GUI" width="800"/><br>
<small>Courtesy of<a href="https://github.com/RayzrReptile">@RayzrReptile</a></small>

</div>

## Articles Discussing Multi-Transmitter Phase Alignment:

- [How to Generate Multi-Channel Phase-Stable and Phase-Coherent Signals](https://www.keysight.com/blogs/en/tech/rfmw/2019/04/10/how-to-generate-multi-channel-phase-stable-and-phase-coherent-signals)
- [How to Perform Multi-Channel Timing and Phase Alignment](https://www.keysight.com/blogs/en/tech/rfmw/2019/04/18/how-to-perform-multi-channel-timing-and-phase-alignment)
- [Phase Alignment Among Multiple Transmitters](https://www.freepatentsonline.com/y2016/0308598.html)
- [ADI Phased Arrays](https://www.analog.com/en/applications/markets/aerospace-and-defense-pavilion-home/phased-array-solution.html)

## Notable Repos for This Project:

- Jon Kraft's [`Pluto_Beamformer`](https://github.com/jonkraft/Pluto_Beamformer) Repo for PlutoSDR.
- Jon Kraft's [`PlutoSDR_Labs`](https://github.com/jonkraft/PlutoSDR_Labs) Repo for PlutoSDR.
- Jon Kraft's [`PhasedArray`](https://github.com/jonkraft/PhasedArray) Repo for the ADAR-1000.
- KrakenRF's [`krakensdr_doa`](https://github.com/krakenrf/krakensdr_doa) Repo for Direction Finding.
- mfkiwl's [`kraken_pr`](https://github.com/mfkiwl/krakensdr_pr) Repo for Passive Radar.
- ptrkrysik's [`multi-rtl`](https://github.com/ptrkrysik/multi-rtl) Repo for Synchronizing RTL-SDRs.


## RF Theory & Test Equipment Articles:

- [Spectrum Analysis Basics](https://www.keysight.com/blogs/en/tech/rfmw/2020/05/01/spectrum-analysis-basics-part-1-what-is-a-spectrum-analyzer): 5 part Series.
- [The RF Engineer's Essential Guide to Frequency Counters](https://www.keysight.com/blogs/en/tech/educ/2023/frequency-counter-essential-guide)
- [TinySA Ultra Wiki Page](https://tinysa.org/wiki/pmwiki.php?n=Main.HomePage) and all the supporting docs for the pocket sized Spectrum Ananlyzer ~ 0.1MHz to 5.3GHz range.
- [Absolute Beginner's Guide to the NanoVNA](http://www.nemarc.org/Absolute_Beginner_Guide_NanoVNA.pdf)
- The [Unofficial NanoVNA User Guide](https://www.qsl.net/g0ftd/other/nano-vna-original/docs/NanoVNA%20User%20Guide-English-reformat-Oct-2-19.pdf).
    - [NanoVNA Calibration Routine](https://nanovna.com/?page_id=2)
- Video: [NanoVNA H4 Setup & Calibration](https://www.youtube.com/watch?v=rQGTG7GuPtM)


## KrakenSDR Resources:

- My [Previous KrakenSDR README](./KrakenSDR/README.md) Page.

## PlutoSDR Resources:

- My [Previous PlutoSDR README](./PlutoSDR/README.md) Page.

## Other Resources:

Useful Programs:
- [QtTinySA](https://github.com/g4ixt/QtTinySA) Linux & Windows GUI for the TinySA Spectrum Analyzer.
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
         - Also see [This RadioReference Get Started Guide](https://forums.radioreference.com/threads/need-beginners-guide-to-dsd-fastlane.463963/).
     - [Unitrunker Digital Decoder](http://www.unitrunker.com/)

Coding Docs:
- [PySDR Python Docs](https://pysdr.org/index.html)
Books: 
- [SDR For Engineers](https://www.analog.com/en/education/education-library/software-defined-radio-for-engineers.html)
- [Field Expedient SDR Volumes 1-3](https://www.factorialabs.com/fieldxp/)
- [Phased Array Antenna Handbook](http://twanclik.free.fr/electricity/electronic/pdfdone11/Phased.Array.Antenna.Handbook.Artech.House.Publishers.Second.Edition.eBook-kB.pdf)
- [Antenna Theory Analysis and Design](https://cds.cern.ch/record/1416310/files/047166782X_TOC.pdf)

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

## Status:

![GitHub repo size](https://img.shields.io/github/repo-size/ADolbyB/sdr-beamforming?logo=Github&label=Repo%20Size)