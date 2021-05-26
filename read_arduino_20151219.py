'''
Leitura dos dados coletados pelo
arduino

Data: 22/01/2016
'''

import os
import pandas as pd
import datetime as dt
import numpy as np
import pylab as pl
import espec

pl.close('all')

#pathname = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/Reserva/Arduino/'
pathname = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/Reserva/Arduino/'


dd1 = pd.read_csv(pathname + 'Teste_boia_Reserva_21-12-2015.CSV',sep=';')

##separa os dados

time = []
gyx = []
gyy = []
gyz = []
acx = []
acy = []
acz = []
bx = []
by = []
bz = []
temp = []
pr = []


for i in range(len(dd1)):

	time.append(dt.datetime.strptime(dd1.ix[i,0][14:],'%Y/%m/%d %H:%M:%S'))
	
	gyx.append(float(dd1.ix[i,1].split(':')[1]))
	gyy.append(float(dd1.ix[i,2].split(':')[1]))
	gyz.append(float(dd1.ix[i,3].split(':')[1]))

	acx.append(float(dd1.ix[i,4].split('=')[1]))
	acy.append(float(dd1.ix[i,5].split('=')[1]))
	acz.append(float(dd1.ix[i,6].split('=')[1]))
	
	bx.append(float(dd1.ix[i,7].split(':')[1]))
	by.append(float(dd1.ix[i,8].split(':')[1]))
	bz.append(float(dd1.ix[i,9].split(':')[1]))

	temp.append(float(dd1.ix[i,10].split(':')[1][:-1]))
	pr.append(float(dd1.ix[i,11].split(':')[1][:-2]))
	

df = pd.DataFrame(np.array([time,gyx,gyy,gyz,acx,acy,acz,bx,by,bz,temp,pr]).T,columns=['time','gyx','gyy','gyz','ax','ay','az','bx','by','bz','temp','pr'])

df.to_csv('out/Reserva_Arduino_20151221.csv',sep=',')

#pega um segmento do dado
df = df.ix[10000:15000,:]

#fs = 1. / 2.5
fs = 4
nfft = len(df) / 20

#espectro de aceleracao
f, aaz = espec.espec1(df.ax,nfft,fs)[:,[0,1]].T

#espectro de heave
aah = aaz / ((2 * np.pi * f) ** 4)

pl.figure()
pl.plot(df.az)

pl.figure()
pl.plot(f,aaz)
