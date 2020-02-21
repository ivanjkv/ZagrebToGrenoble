# -*- coding: utf-8 -*-
__author__ = "ijakovac@phy.hr"

"""
Created on Thu Jan 16 09:35:39 2020

@author: Ivan
"""

from tecmag import TNTReader
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 340, 220)
        self.setWindowTitle('Zagreb to Grenoble')
        self.setWindowIcon(QtGui.QIcon('tg.ico'))
        self.statusBar()


        self.list = QtWidgets.QListWidget(self)
        self.list.addItem('... no file selected ...')
        self.list.move(20,20)
        self.list.resize(300,120)

        btnSelectFile = QtWidgets.QPushButton('Select .tnt file(s)', self)
        btnSelectFile.setGeometry(QtCore.QRect(80,150,180,30))
        btnSelectFile.clicked.connect(self.browse)

        self.files = []

    def browse(self):
        self.statusBar().setStyleSheet("QStatusBar{padding-left:8px;background:rgba(255,0,0,255);color:black;font-weight:bold;}")
        self.statusBar().showMessage('Translating...')
        self.files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select file(s) to translate', filter='*.tnt')[0]
        self.list.clear()
        try:
            for i, file in enumerate(self.files):
                self.translate(file)
                self.list.addItem(file)
        except:
            QtWidgets.QMessageBox.critical(self, "Critical error", "Unsupported file. {} file(s) translated.".format(i) , QtWidgets.QMessageBox.Ok)
            i-=1
        self.statusBar().setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,255,0,255);color:black;font-weight:bold;}")
        self.statusBar().showMessage('{} file(s) translated!'.format(i+1))


    def translate(self, file):
        tnt = TNTReader(file)
        
        with open(file.replace('.tnt', '.dat'), 'w') as output:
            # header, comments and details
            output.write('%%\nPython translator\nFile translated from Tecmag spectrometer (TNT format)\n%End%\n\n')
            output.write('%Program Comments%\nPulse prog comments\n%End%\n\n')
            output.write('%Pulse Program%\nPulse prog details\n%End%\n\n')
        
            # PhaseList
            output.write('%Phase Lists%\nTl1\nTl2\nTl3\nRl1\nRl2\n%End%\n\n')
        
            # Number of skipped transfers
            output.write('%nb of skipped transfers%\n0\n%End%\n\n')
        
            # Loops
            output.write('%loops%\n1\t0\n1\t0\n%End%\n\n')
        
            # Delays
            output.write('%Delays%\nAcq.time\t{0:.1f}u\t0\n'.format(float(tnt.params['acq_time'])*10**6))
            for i in range(5): output.write('\t\t0\n')
            output.write('%End%\n\n')
        
            # Parameters
            output.write('%Parameters%\n')
            output.write('Frequency\t{0:.6f} MHz\t{1}\n'.format(tnt.params['ob_freq'][0], tnt.params['obs_channel']))
            output.write('Field\t{0:.5f} T\t0\n'.format(tnt.params['magnet_field']))
            output.write('DW\t{0:.3f} us\t0\n'.format(float(tnt.params['dwell'][0])*10**6))
            output.write('Sensitivity\t? V\t0\n')
            output.write('Scans\t{}\t0\n'.format(int(tnt.params['scans'])))
            output.write('Transfer\t{}\t0\n'.format(int(tnt.params['actual_scans'])))
            output.write('Record size\t{}\t0\n'.format(int(tnt.params['acq_points'])))
            output.write('Power\t0 dB\t0\n')
            output.write('Aux. frequency\t{0:.2f} MHz\t0\n'.format(float(tnt.params['ref_freq'])))
            output.write('Temperature\t{0:.1f} K\t0\n'.format(int(tnt.params['actual_temperature'])))
            output.write('%End%\n\n')
        
            # Variables
            # Identify a type of measurement
            typ = ''
            for i in range(tnt.params['NCols']):
                if tnt.params['Sequence']['F1_Freq'][i][3] != '':
                    typ = 'fsw'
                    table = tnt.params['Sequence']['F1_Freq'][i][3] # index [3] is a 2D table
                    break
                elif tnt.params['Sequence']['F1_Atten'][i][3] != '':
                    typ = 'att'
                    table = tnt.params['Sequence']['F1_Atten'][i][3]
                    break
                elif tnt.params['Sequence']['Delay'][i][3] != '':
                    typ = 't1'
                    table = tnt.params['Sequence']['Delay'][i][3]
                    break

            output.write('%Variables : level1%\n')
            if typ == 'fsw' or typ == 'att':
                output.write('Frequency\t')
                frequencies = ['{0:.6f} MHz'.format(tnt.params['ob_freq'][0]+int(offset)/10**6) for offset in tnt.params['Tables'][table]]
                output.write('\t'.join(frequencies))
            elif typ == 't1':
                output.write('delta\t')
                output.write(' us\t'.join(tnt.params['Tables'][table]).replace('u us', ' us').replace('m us', ' ms'))
            else:
                output.write('Frequency\t')
                output.write('{0:.6f} MHz'.format(tnt.params['ob_freq'][0]))
            output.write('\n\tNone\n%End%\n\n')
        
            output.write('%Variables : level2%\n\tNone\n\tNone\n%End%\n\n')
            output.write('%Nb max of Measurements%\n{}\n%End%\n\n'.format(tnt.data.shape[1]))
            output.write('%Comments on experiment%\nExp Comments\n%End%\n\n')
        
            # Data output
            output.write('%Data%\n')
            data = np.array(tnt.data)
            for measurement in range(data.shape[1]):
                output.write('measure {}\n'.format(measurement+1))
                output.write('scans {}\n'.format(int(tnt.params['actual_scans'])))
                reals = ['{0:.3E}'.format(float(np.real(data[data_point, measurement]))) for data_point in range(tnt.data.shape[0])]
                imags = ['{0:.3E}'.format(float(np.imag(data[data_point, measurement]))) for data_point in range(tnt.data.shape[0])]
                output.write('\t'.join(reals))
                output.write('\n')
                output.write('\t'.join(imags))
                output.write('\n')

if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    GUI = Window()
    GUI.show()
    sys.exit(app.exec_())
