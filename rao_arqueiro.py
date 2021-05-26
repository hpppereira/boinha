# -*- coding: utf-8 -*-
"""
Processamento dos  dados dos acelerometros do celular e tablet
medidos no arqueiro para retirar a funcao de transferencia do veleiro
atoll 23

Sensores:
Celular:
Tablet:

- Colunas

ACCELEROMETER X (m/s²);ACCELEROMETER Y (m/s²);ACCELEROMETER Z (m/s²);
PROXIMITY (i);SOUND LEVEL( (dB);LOCATION Latitude : ;LOCATION Longitude : ;
LOCATION Altitude ( m);LOCATION Altitude-google ( m);LOCATION Speed ( Kmh);
LOCATION Accuracy ( m);LOCATION ORIENTATION (°);Satellites in range;
Time since start in ms ;YYYY-MO-DD HH-MI-SS_SSS
"""

# importa bibliotecas
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from waveproc import WaveProc
plt.close('all')

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S:%f')

# leitura dos dados
cel = pd.read_csv('Sensor_record_20180404_213936_AndroSensor_Celular.csv',
                   sep=';', delimiter=';', skiprows=2, usecols=[0,1,2,8],
                   names = ['ax', 'ay', 'az', 'date'],
                   parse_dates={'datetime': ['date']}, date_parser=dateparse,
                   index_col='datetime')

tab = pd.read_csv('Sensor_record_20180404_214515_AndroSensor_Tablet.csv',
                   sep=';', delimiter=';', skiprows=2, usecols=[0,1,2,13],
                   names = ['ax', 'ay', 'az', 'date'],
                   parse_dates={'datetime': ['date']}, date_parser=dateparse,
                   index_col='datetime')



# intervalo de medicao
timei = '2018-04-04 20:50'
timef = '2018-04-04 21:35'

cel = cel[timei:timef]
tab = tab[timei:timef]

# calculo da aceleracao vertical
cel['av'] = np.sqrt(cel.ax**2 + cel.ay**2 + cel.az**2)
tab['av'] = np.sqrt(tab.ax**2 + tab.ay**2 + tab.az**2)

# retira a media
cel['av'] = cel.av - cel.av.mean()
tab['av'] = tab.av - tab.av.mean()

# calculo do espectro

fs = 2 #hz
nfft = len(cel)/8
h = 7 #prof

w = WaveProc()

ecel = w.espec1(cel.av.values, fs, int(nfft))
etab = w.espec1(tab.av.values, fs, int(nfft))


# espectro de deslocamento (divide por w4)

f = ecel[:,0]

dcel = ecel[:,1] / (2*np.pi*f)**4
dtab = etab[:,1] / (2*np.pi*f)**4


# plotagem



# serie temporal

plt.figure()
plt.plot(cel.index, cel.ax, 'b-', cel.index, cel.ay, 'r-', cel.index, cel.az, 'g-')
plt.plot(tab.index, tab.ax, 'b--', tab.index, tab.ay, 'r--', tab.index, tab.az, 'g--')

plt.figure()
plt.plot(cel.index, cel.av, 'b-', label='cel-barco')
plt.plot(tab.index, tab.av, 'r-', label='tab-boia')

plt.legend()

# espectro

plt.figure()

plt.plot(f,dcel, label='cel-barco')
plt.plot(f,dtab, label='tab-boia')
plt.xlim(0.2,0.8)
plt.ylim(0,0.015)
plt.grid()

plt.legend()
plt.show()
