# SDR Beamforming

This is a research project repo for Software Defined Radio Phased Array Beamforming. Previously, we had extensively researched the PlutoSDR to evaluate it for a beamforming project. That was previously the `pluto-sdr` repo, which is now an additional folder inside this repo. Currently, we are researching many different options.

## Project GUI: `PyQT_GUI`

<div align="center">
<p>

Please visit the [`PyQT_GUI`](https://github.com/RayzrReptile/PyQT_GUI) Project Repo for more information.

</p>
<!-- <img src="./phaseCoherence/assets/GUI_initial_mockup.png" alt="GUI" width="800"/><br> -->
<img src="./PhaseCoherence/assets/GUI_2-0_nTSDR.png" alt="GUI" width="800"/><br>

<small>Courtesy of&nbsp;<a href="https://github.com/RayzrReptile">@RayzrReptile</a></small>

</div>

## Articles Discussing Multi-Transmitter Phase Alignment:

- [How to Generate Multi-Channel Phase-Stable and Phase-Coherent Signals](https://www.keysight.com/blogs/en/tech/rfmw/2019/04/10/how-to-generate-multi-channel-phase-stable-and-phase-coherent-signals)
- [How to Perform Multi-Channel Timing and Phase Alignment](https://www.keysight.com/blogs/en/tech/rfmw/2019/04/18/how-to-perform-multi-channel-timing-and-phase-alignment)
- [Phase Alignment Among Multiple Transmitters](https://www.freepatentsonline.com/y2016/0308598.html)
- [ADI CNO566 Phased Array (Phaser) Development Platform](https://www.analog.com/en/resources/reference-designs/circuits-from-the-lab/cn0566.html)
- [ADI Phased Arrays](https://www.analog.com/en/applications/markets/aerospace-and-defense-pavilion-home/phased-array-solution.html)

## Notable Repos for This Project:

- coherent-receiver's [`N-Channel Coherent Transceivers`](https://coherent-receiver.com/pluto-sdr) (Concept Only).
    - Note that we contacted this company and they did not offer any information about this product. This led us to believe it was either discontinued or did not work as advertised.
- Jon Kraft's [`Pluto_Beamformer`](https://github.com/jonkraft/Pluto_Beamformer) Repo for PlutoSDR.
- Jon Kraft's [`PlutoSDR_Labs`](https://github.com/jonkraft/PlutoSDR_Labs) Repo for PlutoSDR.
- Jon Kraft's [`PhasedArray`](https://github.com/jonkraft/PhasedArray) Repo for the Analog Devices [ADAR-1000](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/EVAL-ADAR1000.html). 
- KrakenRF's [`krakensdr_doa`](https://github.com/krakenrf/krakensdr_doa) Repo for Direction Finding 
on hardware w/ the RPi 4/5 (or on x64 hardware using VirtualBox 7.0+).
- mfkiwl's [`kraken_pr`](https://github.com/mfkiwl/krakensdr_pr) Repo for Passive Radar.
- osmocom's [`rtl-sdr`](https://github.com/osmocom/rtl-sdr) Repo for The Osmocom RTL-SDR.
- ptrkrysik's [`multi-rtl`](https://github.com/ptrkrysik/multi-rtl) Repo for Synchronizing RTL-SDRs.
- ptrkrysik's [`gr-gsm`](https://github.com/ptrkrysik/gr-gsm/tags) Repo for GSM signals on RTL-SDRs.
- analogdevicesinc's [`gr-iio`](https://github.com/analogdevicesinc/gr-iio) Repo for IIO (PlutoSDR) Devices.
- gnuradio's [`gnuradio`](https://github.com/gnuradio/gnuradio) Repo for the GNURadio Program.

## External Clock Sources:
### Guides:
- QSL.net's [`A Beginner's Guide to GPS Disciplined Oscillators`](https://www.qsl.net/zl1bpu/PROJ/NGPSDO/GPSDO%20Beginner.PDF)
- NIST's [`The Use of GPS Disciplined Oscillators as Primary Frequency Standards for Calibration and Metrology Laboratories`](https://www.nist.gov/publications/use-gps-disciplined-oscillators-primary-frequency-standards-calibration-and-metrology)
- The NIST [Time Measurement and Analysis Service](https://tf.nist.gov/general/pdf/2294.pdf)
### Square Wave Clocks:

- Texas Instruments [CDCLVC1310-EVM](https://www.ti.com/tool/CDCLVC1310-EVM)
    - Note that this clock is delivered with a 25MHz crystal which must be swapped out for a 40MHz surface mount crystal to work sucessfully with Multiple PlutoSDRs.
    - We sucessfully used this clock source board with a replacement 40MHz Crystal. The PlutoSDRs are then fed the external 40Mhz with an SMA-Male to u.FL connector for the PlutoSDR external clock input breakout.

- Leo Bodnar [LBE-1420 GPS Locked Clock Source](https://www.leobodnar.com/shop/index.php?main_page=product_info&cPath=107&products_id=393)
    - 1Hz to 1.1GHz adjustable GPSDO.
- Leo Bodnar [Mini Precision GPS Reference Clock](https://www.leobodnar.com/shop/index.php?main_page=product_info&cPath=107&products_id=301)
    - 400Hz to 810MHz adjustable GPSDO.
- Leo Bodnar [Precision GPS Reference Clock](https://www.leobodnar.com/shop/index.php?main_page=product_info&cPath=107&products_id=393)
    - 450Hz to 800MHz adjustable GPSDO.

## Alternative Hardware Options:
### Alternatives to the PlutoSDR & KrakenSDR for Beamforming:

- Option 1: The $1,000 Analog Devices [ADAR1000](https://www.analog.com/media/en/technical-documentation/data-sheets/adar1000.pdf)
    - Note that this device's frequency range is 8GHz tp 16GHz, so this may not be ideal. It is also Receive Only.
- Option 2: The $1,444.50 Analog Devices [AD-FMCOMMS5-EBZ](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-ad-fmcomms5-ebz.html)
    - This seems to be a great option for prototyping. Uses 2 AD9361 chips and is Frequency and Phase Coherent out of the box. Allows for 4x4 MIMO operation and has tuning range 70MHz - 6GHz.
- Option 3: The $2,165.00 Ettus [USRB B210](https://www.ettus.com/all-products/ub210-kit/) 2 channel phase coherent transceiver.
    - This is a viable option for RX & TX beamforming, but its only 2x2 MIMO operation.
- Option 4: The $2,500 Analog Devices [ADI CNO566](https://www.analog.com/en/resources/reference-designs/circuits-from-the-lab/cn0566.html#rd-overview)
    - More expensive than the FMComms5 and only allows 2x2 MIMO operation.
- Option 5: The $17,765 Ettus Research [USRP N310 ZYNQ-7100, 4 CHANNELS](https://www.ettus.com/all-products/usrp-n310/)
    - This is the most expensive, but it does provide 4x4 MIMO operation, since it also uses 2x Analog Devices AD9361 Chips.

## Cool stuff to do with MIMO:
- Tactical MIMO [StreamCaster Radios](https://silvustechnologies.com/products/streamcaster-radios/)
    - There are 2x2 and 4x4 models offered there.
- DTC's [Mission Critical COmmunications](https://www.domotactical.com/?utm_source=Unmanned%20Systems%20Technology&utm_medium=referral&utm_campaign=silver_profile)
- [StreamCaster Radios for UAVs](https://www.unmannedsystemstechnology.com/2022/09/streamcaster-radios-integrated-into-evtol-commerical-uav/) for streaming high bandwidth audio/video live back to the base station.

## KrakenSDR Resources:

- My [Previous KrakenSDR README](./Toolbox/KrakenSDR/README.md) Page.

## PlutoSDR Resources:

- My [Previous PlutoSDR README](./Toolbox/PlutoSDR/README.md) Page.

## GNURadio Resources:

- My [Previous GNURadio README](./Toolbox/GNURadio/README.md) Page.

## RF Theory, Components, and Test Equipment Articles:
### Theory:

- EE|Times Tutorial: [`SDR meets MIMO ... designing MIMO with a software-defined radio`](https://www.eetimes.com/tutorial-sdr-meets-mimo-or-all-you-need-to-know-about-designing-mimo-with-a-software-defined-radio/)
- SWA's [`Understanding the Basics of MIMO Communication Technology`](https://www.rfmw.com/data/swa-mimo-basics.pdf)
- Keysight's [`Technical Overview of MIMO`](https://www.keysight.com/us/en/lib/resources/training-materials/technical-overview-of-mimo-1179977.html)
- Ezurio (formerly Laird): [Basics of MIMO Radio Systems](https://www.ezurio.com/resources/white-papers/basics-of-mimo-radio-systems)
- [Spectrum Analysis Basics](https://www.keysight.com/blogs/en/tech/rfmw/2020/05/01/spectrum-analysis-basics-part-1-what-is-a-spectrum-analyzer): 5 part Series.
- Rohde & Schwarz's [`dB or not dB?`](https://www.rohde-schwarz.com/us/applications/db-or-not-db-educational-note_230850-15534.html) downloadable PDF. Also on that same page are download links for dB Calculator mobile apps.
- Mathworks [`Quadrature`](https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/quad.pdf) PDF with the mathematical details.
- The [Fourier Transform](https://www.thefouriertransform.com/) Website
- [I/Q Data for Dummies](http://whiteboard.ping.se/SDR/IQ)
- [How to Process I/Q Signals in a Software-Defined RF Receiver](https://www.allaboutcircuits.com/technical-articles/how-to-process-iq-signals-software-defined-rf-receiver-dsp-digital-signal/)
- [SDR For Engineers](https://www.analog.com/en/education/education-library/software-defined-radio-for-engineers.html)
- [Field Expedient SDR Volumes 1-3](https://www.factorialabs.com/fieldxp/)
- [Phased Array Antenna Handbook](http://twanclik.free.fr/electricity/electronic/pdfdone11/Phased.Array.Antenna.Handbook.Artech.House.Publishers.Second.Edition.eBook-kB.pdf)
- [Antenna Theory Analysis and Design](https://cds.cern.ch/record/1416310/files/047166782X_TOC.pdf)
- LibreTexts Engineering PDFs:
    1. [Fundamentals of Microwave and RF Design](https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Book%3A_Fundamentals_of_Microwave_and_RF_Design_(Steer))
    2. [Microwave and RF Design I: Radio Systems](https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Microwave_and_RF_Design_I_-_Radio_Systems_(Steer))
    3. [Microwave and RF Design II: Transmission Lines](https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Microwave_and_RF_Design_II_-_Transmission_Lines_(Steer))
    4. [Microwave and RF Design III: Networks](https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Microwave_and_RF_Design_III_-_Networks_(Steer))
    5. [Microwave and RF Design IV: Modules](https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Microwave_and_RF_Design_IV%3A_Modules_(Steer))
    6. [Microwave and RF Design V: Amplifiers and Oscillators](https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Microwave_and_RF_Design_V%3A_Amplifiers_and_Oscillators_(Steer))
- [Advances in Phased Array Analog Beamforming Solutions](https://ez.analog.com/webinar/c/e/182)
- [What Is Beamforming?](https://www.youtube.com/watch?v=VOGjHxlisyo)
- [What Are Phased Arrays?](https://www.youtube.com/watch?v=9WxWun0E-PM)
- [Why Is Digital Beamforming Useful?](https://www.youtube.com/watch?v=Hb6BhqOgmAI)
- [Software Defined Radio Systems and Analysis Playlist](https://www.youtube.com/playlist?list=PLBfTSoOqoRnOTBTLahXBlxaDUNWdZ3FdS): 26 Lectures

### SDR Online Lessons:
- [Great Scott Gadgets](https://greatscottgadgets.com/sdr/) Tutorials

### Articles:
- [DIY Radio: Jon Kraft](https://ez.analog.com/tags/DIYRadio)

### Antennas:

- Waveform's [`MIMO Antennas Explained: An In-Depth Guide`](https://www.waveform.com/a/b/guides/mimo-antenna-guide)

- MathWorks Video: [Array Design and Beamforming for Wireless MIMO Systems](https://www.mathworks.com/support/search.html/videos/array-design-and-beamforming-for-wireless-mimo-systems-1639591309094.html?fq%5B%5D=asset_type_name:video&fq%5B%5D=category:comm/index&page=1)

- [Antenna Theory](https://www.antenna-theory.com/) Website.
    - Don't forget [Smith Charts](https://www.antenna-theory.com/tutorial/smith/chart.php)!!!! (My Favorite)

#### Antenna Modeling (Windows OS):
- W7EL's [EZNEC Antenna Software](https://eznec.com/) for Antenna Modeling.
- QSL.net's [4nec2](https://www.qsl.net/4nec2/) NEC based antenna modeler and optimizer.

### Test Equipment:

- The ~ $150 TinySA Handheld Spectrum Analyzer: [tinySA Home](https://tinysa.org/wiki/pmwiki.php?n=Main.HomePage)
    - [Wiki Page](https://tinysa.org/wiki/pmwiki.php?n=Main.HomePage) and all the supporting docs for the pocket sized Spectrum Ananlyzer ~ 0.1MHz to 5.3GHz range.

- The ~ $120 NanoVNA: [NanoVNA Home](https://nanovna.com/)
    - [Absolute Beginner's Guide to the NanoVNA](http://www.nemarc.org/Absolute_Beginner_Guide_NanoVNA.pdf) downloadable PDF.
    - The [Unofficial NanoVNA User Guide](https://www.qsl.net/g0ftd/other/nano-vna-original/docs/NanoVNA%20User%20Guide-English-reformat-Oct-2-19.pdf) PDF.
    - [NanoVNA Calibration Routine](https://nanovna.com/?page_id=2)
    - Rigol's [`Basic Measurements with a VNA`](https://www.rigolna.com/pdfs/VNA-Measurements.pdf) downloadable PDF.
    - Video: [NanoVNA H4 Setup & Calibration](https://www.youtube.com/watch?v=rQGTG7GuPtM)
    - Video: [How to properly use a NanoVNA V2 Vector Network Analyzer & Smith Chart](https://www.youtube.com/watch?v=_pjcEKQY_Tk)

- Newer ~ $789.00 5kHz - 6 Ghz handheld VNA Unit: [NanoRFE VNA6000](https://nanorfe.com/vna6000.html) information Page.
    - NanoRFE [Home Page](https://nanorfe.com/nanovna-v2.html).
    - They also have a V2 version that is an older less capable model for $299.00.

- [The RF Engineer's Essential Guide to Frequency Counters](https://www.keysight.com/blogs/en/tech/educ/2023/frequency-counter-essential-guide)

## Other Resources:
### Useful Programs:
#### Linux & Windows:

- [QtTinySA](https://github.com/g4ixt/QtTinySA) Desktop GUI for the TinySA Spectrum Analyzer.

#### Linux:
- [GQRX](https://gqrx.dk/)

#### Windows:

- [AirSpy: SDR Sharp](https://airspy.com/download/) 
    - [Add'l Plugins For SDR Sharp](https://www.rtl-sdr.com/sdrsharp-plugins/)
    - [Frequency Manager](https://www.freqmgrsuite.com/) For SDR Sharp
- [SDR Console](https://www.sdr-radio.com/)
- [HDSDR](http://www.hdsdr.de/)
- [DSD+](https://www.dsdplus.com/) Digital Signal Decoder.
    - Note that v1.101 is free, but the latest version is a paid one-time subscription fee.
    - Also see [This RadioReference Get Started Guide](https://forums.radioreference.com/threads/need-beginners-guide-to-dsd-fastlane.463963/).
- [Unitrunker Digital Decoder](http://www.unitrunker.com/)

## Status:

![GitHub repo size](https://img.shields.io/github/repo-size/ADolbyB/sdr-beamforming?logo=Github&label=Repo%20Size)