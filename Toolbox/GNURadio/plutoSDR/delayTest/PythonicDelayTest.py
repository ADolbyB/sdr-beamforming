import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import math as mth
import adi

app = pg.mkQApp("Plotting Example")
#mw = QtWidgets.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Test Plot
normWindow = win.addPlot(title="Normal plot")
curve = normWindow.plot(pen='y')
delayWindow = win.addPlot(title='Delayed Plot')
delayedCurve = delayWindow.plot(pen='b')

# Test data
xData = np.arange(0, 250, 1)
yData = np.random.rand(250)


# Number of items to skip
DELAY_DELTA = 24

# Trim the first delayDelta inputs
def trimDelay(xInput, yInput, delayDelta):
    yDelta = np.arange(delayDelta, len(xInput), 1)
    yOutput = yInput[yDelta]
    xDelta = np.arange(0, len(yOutput), 1)
    xOutput = xInput[xDelta]
    return xOutput, yOutput

def xcorr(refSignal, inputSignal, maxlag):
    N = max(len(refSignal), len(inputSignal))
    N_power = mth.ceil(mth.log(N + maxlag, 2))
    M = 2**N_power
    if len(refSignal) < M:
        postpad_ref = int(M-len(refSignal)-maxlag)
    else:
        postpad_ref = 0

    if len(inputSignal) < M:
        postpad_inp = int(M-len(inputSignal))
    else:
        postpad_inp = 0

    pre = np.fft( np.pad(refSignal, (maxlag, postpad_ref), 'constant', constant_values=(0,0)))
    post = np.fft( np.pad(inputSignal, (0, postpad_inp), 'constant', constant_values=(0,0)))
    cor = np.ifft( pre * np.conj(post))
    R = cor[0:2*maxlag]
    return R

# Testing cross-correlation and setting delay
xDataDelay, yDataDelay = trimDelay(xData, yData, DELAY_DELTA)

curve.setData(xData, yData)
delayedCurve.setData(xDataDelay, yDataDelay)

if __name__ == '__main__':
    pg.exec()