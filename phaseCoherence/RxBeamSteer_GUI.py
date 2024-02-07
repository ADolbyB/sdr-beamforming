'''
Peyton Adkins
February 1st, 2024

The following programis composed of code sourced from Analog Devices Inc. associate Jon Kraft and his work with phased array beamforming utilizing the Pluto SDR. The program utilizes a compact GUI for input receiving to control an Rx beam.

Acknowledgments to colleague Joel Brigida for his contributions to the beamforming code modifications to better suit our project specifications.

Jon Kraft, Nov 5 2022
https://github.com/jonkraft/Pluto_Beamformer
video walkthrough of this at:  https://www.youtube.com/@jonkraft

'''
# Copyright (C) 2020 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg
import numpy as np
import math
import time
import sys
import adi
print(f'sys.path = {sys.path}') 

class Ui_MainWindow(object):
    def togglePause(self):
        text = self.toggleTrackerButton.text()
        if text == 'PAUSE':
            self.toggleTrackerButton.setText("PLAY")
            self.phaseCalibration.setEnabled(True)
        elif text == 'PLAY':
            self.toggleTrackerButton.setText("PAUSE")
            self.phaseCalibration.setEnabled(False)

    def getPauseToggle(self):
            text = self.toggleTrackerButton.text()
            if text == 'PAUSE':
                return True
            elif text == 'PLAY':
                return False

    def getPhaseCal(self):
        return self.phaseCalibration.value()
    
    def togglePeakDisplay(self):
        text = self.buttonDisplayPeaks.text()
        if text == 'DISPLAY PEAKS: \nON':
            self.buttonDisplayPeaks.setText('DISPLAY PEAKS: \nOFF')
        elif text == 'DISPLAY PEAKS: \nOFF':
            self.buttonDisplayPeaks.setText('DISPLAY PEAKS: \nON')

    def getPeakDisplayToggle(self):
        text = self.buttonDisplayPeaks.text()
        if text == 'DISPLAY PEAKS: \nON':
            return True
        elif text == 'DISPLAY PEAKS: \nOFF':
            return False

    def toggleResetPeaks(self):
        text = self.buttonResetPeaks.text()
        if text == 'RESET PEAKS: \nON':
            self.buttonResetPeaks.setText('RESET PEAKS: \nOFF')
        elif text == 'RESET PEAKS: \nOFF':
            self.buttonResetPeaks.setText('RESET PEAKS: \nON')

    def getResetPeaksToggle(self):
        text = self.buttonResetPeaks.text()
        if text == 'RESET PEAKS: \nON':
            return True
        elif text == 'RESET PEAKS: \nOFF':
            return False
        
    def adjustPhase(self):
        phaseValue = self.dialPhaseIncrement.value()
        self.labelPhaseIncrement.setText(str(phaseValue)+" deg")

    def adjustSpeed(self):
        speedValue = self.speedDial.value()
        self.labelSpeed.setText(str(speedValue)+" ms")

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 601)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.phaseCalibration = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.phaseCalibration.setGeometry(QtCore.QRect(150, 480, 101, 31))
        self.phaseCalibration.setMinimum(-180.0)
        self.phaseCalibration.setMaximum(180.0)
        self.phaseCalibration.setSingleStep(0.5)
        self.phaseCalibration.setEnabled(False)
        self.phaseCalibration.setObjectName("phaseCalibration")
        self.labelPhaseCal = QtWidgets.QLabel(self.centralwidget)
        self.labelPhaseCal.setGeometry(QtCore.QRect(150, 460, 101, 16))
        self.labelPhaseCal.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPhaseCal.setObjectName("labelPhaseCal")
        self.winFFT = GraphicsLayoutWidget(self.centralwidget)
        self.winFFT.setGeometry(QtCore.QRect(20, 20, 361, 281))
        self.winFFT.setObjectName("winFFT")
        self.toggleTrackerButton = QtWidgets.QPushButton(self.centralwidget)
        self.toggleTrackerButton.setGeometry(QtCore.QRect(20, 430, 111, 101))
        self.toggleTrackerButton.setObjectName("toggleTrackerButton")
        self.toggleTrackerButton.clicked.connect(self.togglePause)
        self.labelPhaseIncrement = QtWidgets.QLabel(self.centralwidget)
        self.labelPhaseIncrement.setEnabled(True)
        self.labelPhaseIncrement.setGeometry(QtCore.QRect(530, 420, 111, 21))
        self.labelPhaseIncrement.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPhaseIncrement.setIndent(7)
        self.labelPhaseIncrement.setObjectName("labelPhaseIncrement")
        self.trackerView = GraphicsLayoutWidget(self.centralwidget)
        self.trackerView.setGeometry(QtCore.QRect(390, 20, 391, 391))
        self.trackerView.setObjectName("trackerView")
        self.dialPhaseIncrement = QtWidgets.QDial(self.centralwidget)
        self.dialPhaseIncrement.setGeometry(QtCore.QRect(540, 440, 91, 91))
        self.dialPhaseIncrement.setAcceptDrops(False)
        self.dialPhaseIncrement.setMinimum(-5)
        self.dialPhaseIncrement.setMaximum(5)
        self.dialPhaseIncrement.setNotchTarget(1.0)
        self.dialPhaseIncrement.setNotchesVisible(True)
        self.dialPhaseIncrement.setValue(1)
        self.dialPhaseIncrement.setObjectName("dialPhaseIncrement")
        self.dialPhaseIncrement.valueChanged.connect(self.adjustPhase)
        self.labelSpeed = QtWidgets.QLabel(self.centralwidget)
        self.labelSpeed.setGeometry(QtCore.QRect(400, 420, 91, 21))
        self.labelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.labelSpeed.setObjectName("labelSpeed")
        self.staticLabelSpeed = QtWidgets.QLabel(self.centralwidget)
        self.staticLabelSpeed.setGeometry(QtCore.QRect(410, 520, 71, 21))
        self.staticLabelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.staticLabelSpeed.setObjectName("staticLabelSpeed")
        self.staticLabelPhaseIncrement = QtWidgets.QLabel(self.centralwidget)
        self.staticLabelPhaseIncrement.setGeometry(QtCore.QRect(520, 520, 131, 21))
        self.staticLabelPhaseIncrement.setTextFormat(QtCore.Qt.PlainText)
        self.staticLabelPhaseIncrement.setScaledContents(False)
        self.staticLabelPhaseIncrement.setAlignment(QtCore.Qt.AlignCenter)
        self.staticLabelPhaseIncrement.setObjectName("staticLabelPhaseIncrement")
        self.winRADAR = GraphicsLayoutWidget(self.centralwidget)
        self.winRADAR.setGeometry(QtCore.QRect(390, 20, 391, 391))
        self.winRADAR.setObjectName("winRADAR")
        self.speedDial = QtWidgets.QDial(self.centralwidget)
        self.speedDial.setGeometry(QtCore.QRect(400, 440, 91, 91))
        self.speedDial.setMaximum(100)
        self.speedDial.setProperty("value", 50)
        self.speedDial.setNotchTarget(5.0)
        self.speedDial.setNotchesVisible(True)
        self.speedDial.setObjectName("speedDial")
        self.speedDial.valueChanged.connect(self.adjustSpeed)
        self.buttonDisplayPeaks = QtWidgets.QPushButton(self.centralwidget)
        self.buttonDisplayPeaks.setGeometry(QtCore.QRect(670, 425, 111, 55)) #670, 450, 111, 71
        self.buttonDisplayPeaks.setAcceptDrops(False)
        self.buttonDisplayPeaks.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonDisplayPeaks.setAutoFillBackground(False)
        self.buttonDisplayPeaks.setObjectName("buttonDisplayPeaks")
        self.buttonDisplayPeaks.clicked.connect(self.togglePeakDisplay)

        self.buttonResetPeaks = QtWidgets.QPushButton(self.centralwidget)
        self.buttonResetPeaks.setGeometry(QtCore.QRect(670, 485, 111, 55)) #670, 450, 111, 71
        self.buttonResetPeaks.setAcceptDrops(False)
        self.buttonResetPeaks.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonResetPeaks.setAutoFillBackground(False)
        self.buttonResetPeaks.setObjectName("buttonResetPeaks")
        self.buttonResetPeaks.clicked.connect(self.toggleResetPeaks)

        self.lcdPhase = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdPhase.setGeometry(QtCore.QRect(20, 330, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lcdPhase.setFont(font)
        self.lcdPhase.setSmallDecimalPoint(False)
        self.lcdPhase.setDigitCount(4)
        self.lcdPhase.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdPhase.setObjectName("lcdPhase")
        self.labelPhaseLCD = QtWidgets.QLabel(self.centralwidget)
        self.labelPhaseLCD.setGeometry(QtCore.QRect(20, 310, 101, 16))
        self.labelPhaseLCD.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPhaseLCD.setObjectName("labelPhaseLCD")
        self.lcdSteering = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdSteering.setGeometry(QtCore.QRect(150, 330, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lcdSteering.setFont(font)
        self.lcdSteering.setSmallDecimalPoint(False)
        self.lcdSteering.setDigitCount(4)
        self.lcdSteering.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdSteering.setObjectName("lcdSteering")
        self.lcdSignal = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdSignal.setGeometry(QtCore.QRect(280, 330, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lcdSignal.setFont(font)
        self.lcdSignal.setSmallDecimalPoint(False)
        self.lcdSignal.setDigitCount(4)
        self.lcdSignal.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdSignal.setObjectName("lcdSignal")
        self.labelSteeringLCD = QtWidgets.QLabel(self.centralwidget)
        self.labelSteeringLCD.setGeometry(QtCore.QRect(140, 310, 121, 16))
        self.labelSteeringLCD.setAlignment(QtCore.Qt.AlignCenter)
        self.labelSteeringLCD.setObjectName("labelSteeringLCD")
        self.labelSignalLCD = QtWidgets.QLabel(self.centralwidget)
        self.labelSignalLCD.setGeometry(QtCore.QRect(280, 310, 101, 16))
        self.labelSignalLCD.setAlignment(QtCore.Qt.AlignCenter)
        self.labelSignalLCD.setObjectName("labelSignalLCD")
        self.labelPeakPhaseLCD = QtWidgets.QLabel(self.centralwidget)
        self.labelPeakPhaseLCD.setGeometry(QtCore.QRect(270, 370, 121, 16))
        self.labelPeakPhaseLCD.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPeakPhaseLCD.setObjectName("labelPeakPhaseLCD")
        self.labelPeakSteeringLCD = QtWidgets.QLabel(self.centralwidget)
        self.labelPeakSteeringLCD.setGeometry(QtCore.QRect(20, 370, 101, 16))
        self.labelPeakSteeringLCD.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPeakSteeringLCD.setObjectName("labelPeakSteeringLCD")
        self.lcdPeakPhase = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdPeakPhase.setGeometry(QtCore.QRect(20, 390, 101, 31)) #(280, 390, 101, 31)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lcdPeakPhase.setFont(font)
        self.lcdPeakPhase.setSmallDecimalPoint(False)
        self.lcdPeakPhase.setDigitCount(4)
        self.lcdPeakPhase.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdPeakPhase.setObjectName("lcdPeakPhase")
        self.labelPeakSignalLCD = QtWidgets.QLabel(self.centralwidget)
        self.labelPeakSignalLCD.setGeometry(QtCore.QRect(140, 370, 121, 16))
        self.labelPeakSignalLCD.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPeakSignalLCD.setObjectName("labelPeakSignalLCD")
        self.lcdPeakSteering = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdPeakSteering.setGeometry(QtCore.QRect(150, 390, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lcdPeakSteering.setFont(font)
        self.lcdPeakSteering.setSmallDecimalPoint(False)
        self.lcdPeakSteering.setDigitCount(4)
        self.lcdPeakSteering.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdPeakSteering.setObjectName("lcdPeakSteering")
        self.lcdPeakSignal = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdPeakSignal.setGeometry(QtCore.QRect(280, 390, 101, 31)) #(20, 390, 101, 31)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lcdPeakSignal.setFont(font)
        self.lcdPeakSignal.setSmallDecimalPoint(False)
        self.lcdPeakSignal.setDigitCount(4)
        self.lcdPeakSignal.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdPeakSignal.setObjectName("lcdPeakSignal")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "nTSDR - Linear Rx Beam Steering"))
        self.labelPhaseCal.setText(_translate("MainWindow", "Phase Calibration"))
        self.toggleTrackerButton.setText(_translate("MainWindow", "PAUSE"))
        self.labelPhaseIncrement.setText(_translate("MainWindow", "1 deg"))
        self.labelSpeed.setText(_translate("MainWindow", "50 ms"))
        self.staticLabelSpeed.setText(_translate("MainWindow", "Loop Speed"))
        self.staticLabelPhaseIncrement.setText(_translate("MainWindow", "Phase Increment"))
        self.buttonDisplayPeaks.setText(_translate("MainWindow", "DISPLAY PEAKS: \n"
"ON"))
        self.buttonResetPeaks.setText(_translate("MainWindow", "RESET PEAKS: \n"
"ON"))
        self.labelPhaseLCD.setText(_translate("MainWindow", "Phase Shift [deg]"))
        self.labelSteeringLCD.setText(_translate("MainWindow", "Steering Angle [deg]"))
        self.labelSignalLCD.setText(_translate("MainWindow", "Rx0+Rx1 [dBfs]"))
        self.labelPeakPhaseLCD.setText(_translate("MainWindow", "Peak Signal [dBfs]"))
        self.labelPeakSteeringLCD.setText(_translate("MainWindow", "Peak Phase [deg]"))
        self.labelPeakSignalLCD.setText(_translate("MainWindow", "Estimated DOA [deg]"))

    def setFFTGraph(self):
        p1 = self.winFFT.addPlot()
        p1.setXRange(-1.00, 1.00)
        p1.setYRange(-100, 0)
        p1.setLabel('bottom', 'frequency', '[MHz]', **{'color': '#FFF', 'size': '14pt'})
        p1.setLabel('left', 'Rx0 + Rx1', '[dBfs]', **{'color': '#FFF', 'size': '14pt'})
        return p1
    
    def setRADARGraph(self):
        def addText(plot, degree, x, y):
            text = pg.TextItem(degree)
            plot.addItem(text)
            text.setPos(x, y)
        p2 = self.winRADAR.addPlot()
        p2.setAspectLocked()
        p2.setMouseEnabled(x=False, y=False)
        # Add polar grid lines
        p2.addLine(x=0, pen=0.2)
        p2.addLine(y=0, pen=0.2)
        for r in range(2, 36, 4):
            circle = QtWidgets.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(pg.mkPen(0.2))
            p2.addItem(circle)
            p2.hideAxis('bottom')
            p2.hideAxis('left')
        # Add text
        addText(p2, "0°", -2, 40)
        addText(p2, "45°", 24, 30)
        addText(p2, "90°", 36, 3)
        addText(p2, "135°", 24, -24)
        addText(p2, "180°", -2, -34)
        addText(p2, "225°", -30, -24)
        addText(p2, "270°", -44, 3)
        addText(p2, "315°", -30, 30)
        return p2

'''Setup'''
samp_rate = 2e6             # must be <= 30.72 MHz if both channels are enabled
NumSamples = 2**12
rx_lo = 2.3e9
rx_mode = "manual"          # can be "manual" or "slow_attack"
rx_gain0 = 40
rx_gain1 = 40
tx_lo = rx_lo
tx_gain = -3
fc0 = int(200e3)

''' Set distance between Rx antennas '''
d_wavelength = 0.5                      # distance between elements as a fraction of wavelength.  This is normally 0.5
wavelength = 3E8 / rx_lo                # wavelength of the RF carrier
d = d_wavelength * wavelength           # distance between elements in meters
print("Set distance between Rx Antennas to ", int(d*1000), "mm")

'''Create Radio'''
sdr = adi.ad9361(uri='ip:192.168.2.1')

''' Configure properties for the Rx Pluto '''
def setupPluto(samp_rate, fc0, rx_lo, rx_mode, rx_gain0, rx_gain1, NumSamples, tx_lo, tx_gain):
    sdr.rx_enabled_channels = [0, 1]
    sdr.sample_rate = int(samp_rate)
    sdr.rx_rf_bandwidth = int(fc0*3)
    sdr.rx_lo = int(rx_lo)
    sdr.gain_control_mode = rx_mode
    sdr.rx_hardwaregain_chan0 = int(rx_gain0)
    sdr.rx_hardwaregain_chan1 = int(rx_gain1)
    sdr.rx_buffer_size = int(NumSamples)
    sdr._rxadc.set_kernel_buffers_count(1)   # set buffers to 1 (instead of the default 4) to avoid stale data on Pluto
    sdr.tx_rf_bandwidth = int(fc0*3)
    sdr.tx_lo = int(tx_lo) #make same as rx_lo
    sdr.tx_cyclic_buffer = True
    sdr.tx_hardwaregain_chan0 = int(tx_gain)
    sdr.tx_hardwaregain_chan1 = int(-88)
    sdr.tx_buffer_size = int(2**18)

setupPluto(samp_rate, fc0, rx_lo, rx_mode, rx_gain0, rx_gain1, NumSamples, tx_lo, tx_gain)

'''Program Tx and Send Data'''
fs = int(sdr.sample_rate)
N = 2**16
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i0 = np.cos(2 * np.pi * t * fc0) * 2 ** 14
q0 = np.sin(2 * np.pi * t * fc0) * 2 ** 14
iq0 = i0 + 1j * q0
sdr.tx([iq0,iq0])                           # Send Tx data.

xf = np.fft.fftfreq(NumSamples, ts)         # Assign frequency bins
xf = np.fft.fftshift(xf)/1e6

def calcTheta(phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c*deltaphase/(2*pi*f*d)
    arcsin_arg = np.deg2rad(phase) * 3E8 / (2 * np.pi * rx_lo * d)
    arcsin_arg = max(min(1, arcsin_arg), -1)     # arcsin argument must be between 1 and -1, or numpy will throw a warning
    calc_theta = np.rad2deg(np.arcsin(arcsin_arg))
    return calc_theta

def dbfs(raw_data):                         # function to convert IQ samples to FFT plot, scaled in dBFS
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20*np.log10(np.abs(s_shift)/(2**11))   # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS
    return s_dbfs

''' Setup Main UI Window '''
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

''' Setup Graphs '''
p1 = ui.setFFTGraph()
p2 = ui.setRADARGraph()
steerArrow = pg.ArrowItem()
steerArrow.setStyle(angle=-90, tipAngle=8, tailLen=105, brush=pg.mkColor('w'))
p2.addItem(steerArrow)
peakSteerArrow = pg.ArrowItem()
peakSteerArrow.setStyle(angle=-90, tipAngle=8, tailLen=105, brush=pg.mkColor('b'))
p2.addItem(peakSteerArrow)
baseCurve = p1.plot()
baseCurve.setZValue(1)
peakCurve = p1.plot(pen=pg.mkPen('b'))

''' Rx Data '''
data = sdr.rx()
Rx_0 = data[0]
Rx_1 = data[1]

'''Initialize loop variables'''
peak_sum = -10000
peak_delay = -10000
peak_steer_angle = -10000
delay_phases = np.arange(-180, 180, 2)  # phase delay in degrees
i = 0 # index for iterating through phases
phaseIncrement = 1 # dictates phase incrementation in loop - integers
speed = 50 # speed of loop in milliseconds
phase_cal = 0 # start with 0 to calibrate
rotateMode = "loop" # 'loop' or 'bounce'
peakDisplayToggle = True # Bool for keeping track of peak values
resetPeaksToggle = True # Bool for reseting peak values each loop
resetFlag = False # Initial condition for main toggle

def rescan():
    global Rx_0, Rx_1, peak_sum, peak_delay, peak_steer_angle
    data = sdr.rx()
    Rx_0 = data[0]
    Rx_1 = data[1]
    peak_sum = -10000
    peak_delay = -10000
    peak_steer_angle = -10000

def rotate():
    global baseCurve, peakCurve, peak_steer_angle, steer_angle, steerArrow, peakSteerArrow, peak_sum, peak_delay, i, phaseIncrement, speed, phase_cal, rotateMode, peakDisplayToggle, resetPeaksToggle

    phase_delay = delay_phases[i]
    delayed_Rx_1 = Rx_1 * np.exp(1j*np.deg2rad(phase_delay+phase_cal))
    delayed_sum = dbfs(Rx_0 + delayed_Rx_1)
    # Find max delay and max steering angle
    if (peakDisplayToggle and np.max(delayed_sum) > np.max(peak_sum)):
        peak_sum = delayed_sum 
        peak_delay = phase_delay
        peak_steer_angle = int(calcTheta(peak_delay))

    ''' FFT Plot '''
    peakCurve.setData([0], [0])
    if peakDisplayToggle:
        peakCurve.setData(xf, peak_sum)
    baseCurve.setData(xf, delayed_sum)
    steer_angle = int(calcTheta(phase_delay))
    # Set labels
    ui.lcdPhase.display(phase_delay)
    ui.lcdSteering.display(steer_angle)
    ui.lcdSignal.display(int(math.floor(np.max(delayed_sum))))
    ui.lcdPeakPhase.display(0)
    ui.lcdPeakSteering.display(0)
    ui.lcdPeakSignal.display(0)
    if peakDisplayToggle:
        ui.lcdPeakPhase.display(peak_delay)
        ui.lcdPeakSteering.display(peak_steer_angle)
        ui.lcdPeakSignal.display(int(math.floor(np.max(peak_sum))))

    ''' RADAR Plot '''
    p2.removeItem(peakSteerArrow)
    if peakDisplayToggle:
        peakSteerArrow = pg.ArrowItem()
        peakSteerArrow.setStyle(angle=peak_steer_angle-90, tipAngle=8, tailLen=105, brush=pg.mkColor('b'))
        p2.addItem(peakSteerArrow)
    p2.removeItem(steerArrow)
    steerArrow = pg.ArrowItem()
    steerArrow.setStyle(angle=steer_angle-90, tipAngle=8, tailLen=105, brush=pg.mkColor('w'))
    p2.addItem(steerArrow)

    # Increment through phases - Reset peaks
    i=i+math.floor(phaseIncrement)
    if (rotateMode == 'loop'):
        if (i>=len(delay_phases)):
            i=0
            if resetPeaksToggle:
                rescan()
        elif (i<=-1):
            i=len(delay_phases)-1
            if resetPeaksToggle:
                rescan()
    elif (rotateMode == 'bounce'):
        if (i>=len(delay_phases) or i<=-1):
            phaseIncrement=-1*phaseIncrement
            i=i+math.floor(phaseIncrement)
            if resetPeaksToggle:
                rescan()

def mainLoop():
    global baseCurve, peakCurve, peak_steer_angle, steer_angle, steerArrow, peakSteerArrow, peak_sum, peak_delay, i, phaseIncrement, speed, phase_cal, rotateMode, peakDisplayToggle, resetPeaksToggle, resetFlag, sdr

    loopToggle = ui.getPauseToggle()
    newPeakDisplayToggle = ui.getPeakDisplayToggle()
    newResetPeaksToggle = ui.getResetPeaksToggle()
    newPhaseCal = ui.getPhaseCal()
    newPhaseIncrement = ui.dialPhaseIncrement.value()
    newSpeed = ui.speedDial.value()

    # If toggle is on to continue tracker
    if loopToggle:
        # If change has occured to Pluto variables
        if resetFlag:
            print("Restart Pluto")
            sdr.tx_destroy_buffer()
            # New Pluto instance
            sdr = adi.ad9361(uri='ip:192.168.2.1')
            setupPluto(samp_rate, fc0, rx_lo, rx_mode, rx_gain0, rx_gain0, NumSamples, tx_lo, tx_gain)
            rescan()
            resetFlag = False

        # If Peak Display toggle changed
        if newPeakDisplayToggle != peakDisplayToggle:
            peakDisplayToggle = newPeakDisplayToggle
        # If Peak Reset toggle changed
        if newResetPeaksToggle != resetPeaksToggle:
            resetPeaksToggle = newResetPeaksToggle
        # If Phase Increment dial changed
        if newPhaseIncrement != phaseIncrement:
            phaseIncrement = newPhaseIncrement
        # If Speed dial is changed
        if newSpeed != speed:
            speed = newSpeed

        rotate()
    else:
        # If Phase Calibration is changed
        if newPhaseCal != phase_cal:
            phase_cal = newPhaseCal
            # resetFlag = True


    # Control rate of rotation
    time.sleep(speed/1000)

timer = pg.QtCore.QTimer()
timer.timeout.connect(mainLoop)
timer.start(0)

if __name__ == "__main__":
    sys.exit(app.exec_())

sdr.tx_destroy_buffer()
