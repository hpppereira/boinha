'''
Leitura dos sensores do acelerometro
para medicao de ondas
'''

import pandas as pd
import matplotlib.pylab as pl
import numpy as np
import os
import espec
import datetime


pl.close('all')

pathname = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/Reserva/AndroSensor/'
pathname_adcp = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/Reserva/ADCP/20151111/'

#escolha o dado para reprocessar
dd1 = pd.read_csv(pathname + 'Sensor_record_20151111_111033_AndroSensor_reserva_hp.csv') #data eh coluna 22
dd2 = pd.read_csv(pathname + 'Sensor_record_20151111_110929_AndroSensor_reserva_fv.csv') #data eh coluna 22

adcp = pd.read_table(pathname_adcp + 'ADCP_REEF_11_11_2015011.wad',sep='\s*',header=None)

#cria vetor de data com 2 hz e 1024 pontos
adcp['date'] = pd.date_range('2015-11-11-10:15',periods=1024,freq='500L')

adcp = adcp.set_index(['date'])


adcp['pr'] = adcp.ix[:,2]
adcp['vx'] = adcp.ix[:,5]
adcp['vy'] = adcp.ix[:,6]
adcp['vz'] = adcp.ix[:,7]

'''
pl.figure()
pl.plot(adcp.pr - adcp.pr.mean())
pl.plot(adcp.vx - adcp.vx.mean())
pl.plot(adcp.vy - adcp.vy.mean())
pl.plot(adcp.vz - adcp.vz.mean())
pl.legend(['pr','vx','vy','vz'])
'''

#cria coluna time com datetime (ate milesimo) - 4hz
dd1['time'] = pd.to_datetime(dd1.ix[:,15], format='%Y-%m-%d %H:%M:%S:%f')
dd2['time'] = pd.to_datetime(dd2.ix[:,22], format='%Y-%m-%d %H:%M:%S:%f')

#coloca data como indice
dd1 = dd1.set_index(['time'])
dd2 = dd2.set_index(['time'])

#variaveis (dd1 - hp ; dd2 - fv)
dd1['ax'] = dd1.ix[:,0]
dd1['ay'] = dd1.ix[:,1]
dd1['az'] = dd1.ix[:,2]

dd2['ax'] = dd2.ix[:,0] #accel
dd2['ay'] = dd2.ix[:,1]
dd2['az'] = dd2.ix[:,2]
dd2['mx'] = dd2.ix[:,3] #magnetic field
dd2['my'] = dd2.ix[:,4]
dd2['mz'] = dd2.ix[:,5] 
dd2['oz'] = dd2.ix[:,6] #orientation 
dd2['pt'] = dd2.ix[:,7]
dd2['rl'] = dd2.ix[:,8] #azimuth

#escolhe um sensor para fazer a analise espectral
#dd = dd2

#
dd2.index = datetime.timedelta(seconds=0.751) + dd2.index

#calculo da aceleracao vertical a partir das 3 aceleracoes x, y e z
dd1['av'] = np.sqrt(dd1.ax**2 + dd1.ay**2 + dd1.az**2)
dd2['av'] = np.sqrt(dd2.ax**2 + dd2.ay**2 + dd2.az**2)


dd11 = dd1
dd22 = dd2
dd1 = dd1['2015-11-11 10:15:00':'2015-11-11 10:23:31']
dd2 = dd2['2015-11-11 10:15:00':'2015-11-11 10:23:31']
#dd1 = dd1['2015-11-11 10:18:00':'2015-11-11 10:40:31']
#dd2 = dd2['2015-11-11 10:18:00':'2015-11-11 10:40:31']


######################################################

#media movel
#dd1.av = pd.rolling_mean(dd1.av,2)


######################################################
##### integracao numerica 
#calcula a velocidade (a partir da aceleracao)
vzi = []
for i in range(len(dd1.av)-1):
	vzi.append( (dd1.av[i] + dd1.av[i+1]) / 2 )
vzi = np.array(vzi - np.mean(vzi))

#calcula o deslocamento (a partir da serie de velocidade)
dzi = []
for i in range(len(vzi)-1):
	dzi.append( (vzi[i] + vzi[i+1]) / 2 )
dzi = np.array(dzi - np.mean(dzi))

#coloca dois zeros nos ultimos indices
dzi = np.concatenate((dzi,([0,0])))

dd1['hv'] = dzi
#dd1['av'] = dd1.hv


'''
pl.figure()
pl.plot(adcp.index,adcp.vz - adcp.vz.mean())
pl.plot(dd1.index,dd1.av - dd1.av.mean())
pl.legend(['adcp','dd1av'])

pl.figure()
pl.subplot(211)
pl.title('acel.V')
pl.plot(dd1.index,dd1.av,'-o',dd2.index,dd2.av,'-o')
pl.legend(['hp','fv'])
pl.subplot(212)
pl.plot(dd11.index,dd11.av,'-o',dd22.index,dd22.av,'-o')
pl.grid()
pl.show()
'''


fs = 2
nfft = len(dd1) / 3

#espectro de pressao
aadcp_pr = espec.espec1(adcp.pr,nfft,fs)

#espectro do adcp
aadcp = espec.espec1(adcp.vz,nfft,fs)
aadcp_hv = aadcp[:,1] / ((2*np.pi*aadcp[:,0])**2)

#espectro de heave do adcp a partir da soma dos espectros de velocidade
aadcp_vx = espec.espec1(adcp.vx,nfft,fs)
aadcp_vy = espec.espec1(adcp.vy,nfft,fs)

#soma dos espectros
ss = aadcp_vx[:,1] + aadcp_vx[:,1]
ss1 = ss / ((2*np.pi*aadcp_vx[:,0])**2)


#espectro de aceleracao
aaz1 = espec.espec1(dd1.az,nfft,fs)
aav1 = espec.espec1(dd1.av,nfft,fs)

aaz2 = espec.espec1(dd2.az,nfft,fs)
aav2 = espec.espec1(dd2.av,nfft,fs)

#espectro de heave do adcp (velocidade corrigida)
aazv1 = aaz1[:,1] / ((2*np.pi*aaz1[:,0])**2)
aavv1 = aav1[:,1] / ((2*np.pi*aav1[:,0])**2)
aazv2 = aaz2[:,1] / ((2*np.pi*aaz2[:,0])**2)
aavv2 = aav2[:,1] / ((2*np.pi*aav2[:,0])**2)

#espectro de heave
aazh1 = aaz1[:,1] / ((2*np.pi*aaz1[:,0])**4)
aavh1 = aav1[:,1] / ((2*np.pi*aav1[:,0])**4)
aazh2 = aaz2[:,1] / ((2*np.pi*aaz2[:,0])**4)
aavh2 = aav2[:,1] / ((2*np.pi*aav2[:,0])**4)

#calculo do espectro cruzado
#aa2 = espec.espec2(adcp.vz,dd1.az,nfft,fs)


#plota series temporais
pl.figure()
pl.plot(dd1.index,dd1.av-dd1.av.mean(),'b',label='boia (m/s2)')
pl.legend(loc=2)
pl.twinx()
pl.plot(adcp.index,adcp.vz-adcp.vz.mean(),'r',label='adcp (m/s)')
pl.legend(loc=1)

#espectro de heave do adcp e a soma dos espec de hv vx e vy
pl.figure()
pl.plot(aadcp_vx[:,0],ss1)
pl.plot(aadcp[:,0],aadcp_hv,label='adcphv')


#espectro de pressa e heave do adcp
pl.figure()
pl.plot(aadcp_pr[:,0],aadcp_pr[:,1])
pl.plot(aadcp[:,0],aadcp_hv,label='adcphv')


#compara espectro do adcp e boia
pl.figure()
pl.plot(aadcp[:,0],aadcp[:,1],label='adcpvz')
pl.plot(aadcp[:,0],aadcp_hv,label='adcphv')
pl.legend(loc=2)
pl.ylim(0,1)
pl.twinx()
pl.plot(aaz1[:,0],aavh1,'r',label='aavh1')
pl.ylim(0,4)
pl.xlim(0,0.5)
pl.legend(loc=1)
pl.grid()


'''
#espectro cruzado - coerencia
pl.figure()
pl.subplot(211)
pl.plot(aaz1[:,0],aavh1,'r',label='aavh1')
pl.ylim(0,4)
pl.xlim(0,0.5)
pl.grid()
pl.subplot(212)
pl.plot(aa2[:,0],aa2[:,5])
pl.plot(aa2[:,0],aa2[:,8],'r--')
pl.xlim(0,0.5)
pl.grid()

pl.figure()
pl.subplot(121)
pl.plot(aaz1[:,0],aaz1[:,1],label='aav1')
pl.plot(aaz2[:,0],aaz2[:,1],label='aav2')
pl.legend()
pl.subplot(122)
pl.plot(aaz1[:,0],aazh1,label='aavh1')
pl.plot(aaz2[:,0],aazh2,label='aavh2')
pl.ylim(0,40)
pl.xlim(0,0.3)
pl.legend()

#espectro de velocidade (para comparar com adcp)
pl.figure()
pl.title('Vel')
pl.plot(aaz1[:,0],aavv1,label='aavv1')
pl.plot(aaz2[:,0],aavv2,label='aavv2')
pl.ylim(0,40)
pl.xlim(0,0.3)
pl.legend()


# pl.plot(aa2[:,0],aa2[:,1],'r',label='ac.dd2')
# pl.plot(aa3[:,0],aa3[:,1],'g',label='ac.dd3')
# pl.plot(aa4[:,0],aa4[:,1],'k',label='ac.dd4')

#pl.figure()
#pl.plot(aa1[:,0],aa1h,'b',label='hv.dd1')
# pl.plot(aa2[:,0],aa2h,'r',label='hv.dd2')
# pl.plot(aa3[:,0],aa3h,'g',label='hv.dd3')
# pl.plot(aa4[:,0],aa4h,'k',label='hv.dd4')
#pl.grid()
#pl.ylim(0,100)
#pl.xlim(0,0.35)
'''



pl.show()