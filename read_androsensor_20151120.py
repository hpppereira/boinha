'''
Leitura dos sensores do acelerometro
para medicao de ondas

- aplica filtro fft
'''

import pandas as pd
import matplotlib.pylab as pl
import numpy as np
import os
import espec
import datetime

pl.close('all')

pathname = os.environ['HOME'] + '/Dropbox/boinha/data/Reserva/AndroSensor/'
#pathname_adcp = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/Reserva/ADCP/20151111/'

#escolha o dado para reprocessar
dd = pd.read_csv(pathname + 'Sensor_record_20151120_155731_AndroSensor_reserva_hp.csv')

#cria coluna time com datetime (ate milesimo) - 4hz
dd['time'] = pd.to_datetime(dd.ix[:,15], format='%Y-%m-%d %H:%M:%S:%f')

#coloca data como indice
dd = dd.set_index(['time'])

#variaveis (dd1 - hp ; dd2 - fv)
dd['ax'] = dd.ix[:,0]
dd['ay'] = dd.ix[:,1]
dd['az'] = dd.ix[:,2]

#escolhe um sensor para fazer a analise espectral
#dd = dd2

#
dd = dd['2015-11-20 11:00:00':'2015-11-20 14:00:00'] #irado

'''
######################################################
#prepara filtro fft

dd['fftaz'] = np.fft.fft(dd.az)
dd['fftfreq'] = np.fft.fftfreq(len(dd),0.25)

#frequencia de corte
fc = 0.5

#filtra a fft
dd.fftaz[pl.find((dd.fftfreq<fc) & (dd.fftfreq>-fc))] = 0

#figura da fft
pl.figure()
pl.plot(dd.fftfreq[:len(dd)/2],np.abs(dd.fftaz[:len(dd)/2]))

#calcula a fft de heave (divide por w4)
w4 = (2*np.pi*dd.fftfreq) ** 4
dd['ffthv'] = dd.fftaz / w4

#serie temporal de heave
iffthv = np.fft.ifft(dd.ffthv.loc[dd.ffthv<>0][1:])

pl.figure()
pl.plot(iffthv)
'''

######################################################

#media movel
#dd['az'] = pd.rolling_mean(dd.az,4)

fs = 4
nfft = len(dd) / 30


#espectro de aceleracao
aaz = espec.espec1(dd.az.loc[dd.az.notnull()],nfft,fs)
#aav1 = espec.espec1(dd1.av,nfft,fs)

#espectro de heave
aah = aaz[:,1] / ((2*np.pi*aaz[:,0])**4)
#aavh1 = aav1[:,1] / ((2*np.pi*aav1[:,0])**4)
#aazh2 = aaz2[:,1] / ((2*np.pi*aaz2[:,0])**4)
#aavh2 = aav2[:,1] / ((2*np.pi*aav2[:,0])**4)

f = aaz[100:170,0]
df = f[3] -f[2]

#moemento espec 0
m0 = np.sum(aah[100:170]) * df

hm0 = 4 * np.sqrt(m0)

#acha o maximo valor do espectro de acel.
aux = pl.find(aaz[:,1] == aaz[:,1].max())

tp = 1 / aaz[aux,0]

pl.figure()
pl.subplot(211)
pl.plot(dd.index,dd.az,'b')
pl.ylabel(r'$Accel. V\ (m/s^{2})$',size=15)
pl.xlabel('Time')
pl.grid()
pl.subplot(212)
pl.plot(aaz[:,0],aaz[:,1],'b-')
pl.legend(['Ac.'],loc=2)
pl.ylabel(r'$S(f)\ Accel.$',size=15)
pl.xlabel(r'$Frequency\ (Hz)$',size=15)
pl.grid()
pl.twinx()
pl.plot(aaz[:,0],aah,'r-')
pl.legend(['Hv.'],loc=1)
pl.ylabel(r'$S(f)\ Heave$',size=15)
pl.ylim(0,5)
#pl.xlim(0,0.4)


pl.show()