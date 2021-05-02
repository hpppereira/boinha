'''
Leitura dos sensores do acelerometro
para medicao de ondas

SensorLog mediu com 10 Hz - parece que deu umas falhadas
AndroSensor mediu com 4 Hz

data:

'''

import pandas as pd
import matplotlib.pylab as pl
import numpy as np
import os
import espec
import datetime

pl.close('all')

pathname_androsensor = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/WaveFlume/AndroSensor/'
pathname_sensorlog = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/WaveFlume/SensorLog/'

#escolha o dado para reprocessar
dd1 = pd.read_csv(pathname_androsensor + 'Sensor_record_20151208_123421_AndroSensor_waveflume.csv') #androsensor
dd2 = pd.read_csv(pathname_sensorlog + '2015-12-08_10-21-02.csv') #sensor log


#cria coluna time com datetime (ate milesimo)
dd1['time'] = pd.to_datetime(dd1.ix[:,4], format='%Y-%m-%d %H:%M:%S:%f')
dd2['time'] = pd.to_datetime(dd2.loggingTime, format='%Y-%m-%d %H:%M:%S.%f')

#coloca data como indice
dd1 = dd1.set_index(['time'])
dd2 = dd2.set_index(['time'])


#define variaveis de aceleracao

#androsensor
dd1['ax'] = dd1.ix[:,0]
dd1['ay'] = dd1.ix[:,1]
dd1['az'] = dd1.ix[:,2]

#sensorlog
dd2['ax'] = dd2.accelerometerAccelerationX
dd2['ay'] = dd2.accelerometerAccelerationY
dd2['az'] = dd2.accelerometerAccelerationZ

#media movel
#dd['az'] = pd.rolling_mean(dd.az,4)


#dd1 = dd1['2015-12-08 11:57:00':'2015-12-08 11:57:26'] #very shot 1s period
#dd1 = dd1['2015-12-08 11:47:00':'2015-12-08 11:53:00'] #large period


fs = 4
nfft = len(dd1) #/ 30

#espectro de aceleracao
f, aaz = espec.espec1(dd1.az,nfft,fs)[:,[0,1]].T

#espectro de heave
aah = aaz / ((2 * np.pi * f) ** 4)


#to show all the measurement for calibration (make a zoom to view with details in one event)
pl.figure()
pl.plot(dd1.index,dd1.az)
pl.ylabel('Accel. Z')
pl.grid()

#to show the sensor resolution (make a large zoom in a part without movement)
pl.figure()
pl.plot(dd1.index,dd1.az,'-o')
pl.ylabel('Accel. Z (m/s^2)')
pl.grid()

#to show the three accelerations (removing the mean)
pl.figure()
pl.plot(dd1.index,dd1.ax-dd1.ax.mean())
pl.plot(dd1.index,dd1.ay-dd1.ay.mean())
pl.plot(dd1.index,dd1.az-dd1.az.mean())
pl.ylabel('Accel. (m/s^2)')
pl.legend(['Ac.X','Ac.Y','Ac.Z'])
pl.grid()


# #aav1 = espec.espec1(dd1.av,nfft,fs)

# #espectro de heave
# aah = aaz[:,1] / ((2*np.pi*aaz[:,0])**4)
# #aavh1 = aav1[:,1] / ((2*np.pi*aav1[:,0])**4)
# #aazh2 = aaz2[:,1] / ((2*np.pi*aaz2[:,0])**4)
# #aavh2 = aav2[:,1] / ((2*np.pi*aav2[:,0])**4)

# #f = aaz[100:170,0]
# df = aaz[3,0] - aaz[2,0]

# #moemento espec 0
# m0 = np.sum(aah[100:170]) * df

# hm0 = 4 * np.sqrt(m0)

# #acha o maximo valor do espectro de acel.
# aux = pl.find(aaz[:,1] == aaz[:,1].max())

# tp = 1 / aaz[aux,0]




pl.figure()
pl.subplot(211)
pl.plot(dd1.index,dd1.az,'b')
pl.ylabel(r'$Accel. V\ (m/s^{2})$',size=15)
pl.xlabel('Time')
pl.grid()
pl.subplot(212)
pl.plot(f,aaz,'b-')
pl.legend(['Ac.'],loc=2)
pl.ylabel(r'$S(f)\ Accel.$',size=15)
pl.xlabel(r'$Frequency\ (Hz)$',size=15)
pl.grid()
pl.twinx()
pl.plot(f,aah,'r-')
pl.legend(['Hv.'],loc=1)
pl.ylabel(r'$S(f)\ Heave$',size=15)
pl.ylim(0,.07)
#pl.xlim(0,0.4)

pl.show()
