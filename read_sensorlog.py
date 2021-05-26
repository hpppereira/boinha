'''
Leitura de arquivos de dados
do app SensorLog do iPhone
'''

import pandas as pd
import matplotlib.pylab as pl
import numpy as np
import os
import espec

pl.close('all')


pathname = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/WaveFlume/SensorLog/'

#escolha o dado para reprocessar
dd = pd.read_csv(pathname + '2015-12-08_10-21-02.csv') #data eh coluna 19

#cria coluna time com datetime (ate milesimo) - 4hz
dd['time'] = pd.to_datetime(dd.loggingTime, format='%Y-%m-%d %H:%M:%S.%f')

#coloca data como indice
dd = dd.set_index(['time'])

dd['ax'] = dd.accelerometerAccelerationX
dd['ay'] = dd.accelerometerAccelerationY
dd['az'] = dd.accelerometerAccelerationZ


# dd1 = dd

# #periodo de dados bons
# dd = dd[6600:8124]

# #reamostra de segundo e segundo
# dd = dd[0:-1:4]

# nfft = len(dd) / 2
# fs = 1

# #calculo do espectro
# aa = espec.espec1(dd.az,nfft,fs)
# aaz = espec.espec1(dd.az,nfft,fs)
# aax = espec.espec1(dd.ax,nfft,fs)
# aay = espec.espec1(dd.ay,nfft,fs)
# aa2_zx = espec.espec2(dd.az,dd.ax,nfft,fs)
# aa2_zy = espec.espec2(dd.az,dd.ay,nfft,fs)
# aa2_xy = espec.espec2(dd.ax,dd.ay,nfft,fs)

# #espectro de heave (divide por w4)
# sdz = aaz[:,1] / ((2*np.pi*aa[:,0])**4)
# sdx = aax[:,1] / ((2*np.pi*aa[:,0])**4)
# sdy = aay[:,1] / ((2*np.pi*aa[:,0])**4)


# pl.figure()
# pl.plot(aa[:,0],sdz,'b')
# #pl.plot(aa[:,0],sdx,'r')
# #pl.plot(aa[:,0],sdy,'g')
# pl.legend(['az','ax','ay'])

# pl.figure()
# pl.plot(dd.index,dd.ax-np.mean(dd.ax),'b-',dd.index,dd.ay-np.mean(dd.ay),'r-',dd.index,dd.az-np.mean(dd.az),'g-')
# pl.legend(['ax','ay','az'])

# pl.figure()
# pl.plot(aa[:,0],aa[:,1])
# pl.title('Espectro de aZ')

# pl.figure()
# pl.subplot(211)
# pl.plot(aa2_zx[:,0],aa2_zx[:,4])
# pl.title('Espectro de Fase - aZ e aX')
# pl.subplot(212)
# pl.plot(aa2_zx[:,0],aa2_zx[:,5])
# pl.title('Espectro de Coerencia - aZ e aX')

# pl.figure()
# pl.subplot(211)
# pl.plot(aa2_zy[:,0],aa2_zy[:,4])
# pl.title('Espectro de Fase - aZ e aY')
# pl.subplot(212)
# pl.plot(aa2_zy[:,0],aa2_zy[:,5])
# pl.title('Espectro de Coerencia - aZ e aY')

# pl.figure()
# pl.subplot(211)
# pl.plot(aa2_xy[:,0],aa2_xy[:,4])
# pl.title('Espectro de Fase - aX e aY')
# pl.subplot(212)
# pl.plot(aa2_xy[:,0],aa2_xy[:,5])
# pl.title('Espectro de Coerencia - aX e aY')

# pl.figure()


# pl.show()