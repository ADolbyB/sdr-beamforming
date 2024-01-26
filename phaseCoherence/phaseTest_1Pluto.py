# Peyton Adkins
# Generic test code skeleton by Joel Brigida
# to be tested on a single 2r2t PlutoSDR
# This can prove if both local transmitters and receivers are phase aligned

import numpy as np
import adi
import matplotlib.pyplot as plt

# Generate Noise for Alignment
def generateNoiseSig(freq, duration, sampleRate, noiseAmplitude):
    t = np.arange(0, duration, (1 / sampleRate))    # Create empty array for samples.
    signal = np.sin(2 * np.pi * freq * t) + noiseAmplitude * np.random.normal(size=len(t))
    # TODO: Need to trigger the noise source here to fill array with samples
    return signal

# Align Phase
def phaseAlign(XCVR, extNoiseFreq, duration, sampleRate):
    # Generate a reference signal with external noise
    refSignal = generateNoiseSig(extNoiseFreq, duration, sampleRate, noiseAmplitude=0.1)

    # TX the reference signal using both Transceivers
    txData = XCVR.tx([refSignal, refSignal])
    txSig1 = txData[0] # May not return any variable - [psuedo-code]
    txSig2 = txData[1] # May not return any variable - [psuedo-code]

    # RX signals from both Transceivers
    rxData = XCVR.rx()
    rxSig1 = rxData[0]
    rxSig2 = rxData[1]

    # Cross-correlate rec'd signals with the reference
    crossCorrelation1 = np.correlate(rxSig1, refSignal, mode='full')
    crossCorrelation2 = np.correlate(rxSig2, refSignal, mode='full')

    # Calculate time delay between signals
    timeDelay1 = np.argmax(crossCorrelation1) / sampleRate
    timeDelay2 = np.argmax(crossCorrelation2) / sampleRate

    # Calculate phase difference based on time delay
    phaseDiff = 2 * np.pi * extNoiseFreq * (timeDelay2 - timeDelay1)

    # Apply phase correction to XCVR 2 to match XCVR 1
    newTXsig2 = np.roll(txSig2, int(phaseDiff * sampleRate))

    # Transmit corrected signal using both XCVRs
    txData = XCVR.tx([newTXsig2, refSignal])
    txSig1 = txData[0] # May not return any variable - [psuedo-code]
    txSig2 = txData[1] # May not return any variable - [psuedo-code]

    # Plot results for visualization
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(refSignal, label='Reference Signal')
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(txSig1, label='XCVR 1 TX')
    plt.plot(rxSig1, label='XCVR 1 RX')
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(txSig2, label='XCVR 2 TX (Uncorrected)') 
    plt.plot(newTXsig2, label='XCVR 2 TX (Corrected)')
    plt.plot(rxSig2, label='XCVR 2 RX')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    
    # sdr = adi.ad9361(uri='ip:192.168.2.1')    # Reference Syntax
    # sdr = adi.Pluto("ip:pluto.local")         # Reference Syntax
    
    # Define and connect to single PlutoSDR:
    XCVR = adi.ad9361(uri="ip:192.168.2")
    XCVR.rx_enabled_channels = [0, 1]
    XCVR.tx_enabled_channels = [0, 1]

    # Define test parameters:
    extNoiseFreq = 100e6            # Ext noise frequency (Hz)
    duration = 1.0                  # Noise signal duration (seconds)
    sampleRate = 1e6                # Sample rate (Hz)

    # Achieve phase coherence
    phaseAlign(XCVR, extNoiseFreq, duration, sampleRate)