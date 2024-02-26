import numpy as np
import matplotlib.pyplot as plt

# Read in file.  We have to tell it what format it is (np.complex64)
samples = np.fromfile('GNURadio/plutoSDR/fileOutput/bpsk_in_noise.iq', np.complex64)

# print(samples) # Prints valies in (a + bj) format in the terminal for debug

# Plot constellation to make sure it looks right
plt.plot(np.real(samples), np.imag(samples), '.')
plt.title('Complex IQ Samples')
plt.xlabel('Real Data')
plt.ylabel('Imaginary Data')
plt.grid(True)
plt.show()