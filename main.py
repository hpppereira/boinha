# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import matplotlib.pylab as pl
import acc2heave

pl.close('all')

# pathname = "C:\\Users\Luiz Felipe\Google Drive\LIOc\Boia Henrique\Boinha\dados"
pathname = os.environ['HOME'] + '/Dropbox/boinha/data/Testes/USB/'
filename0 = '_dev_ttyUSB0_2017-02-09_19_37_35.086_.txt'
filename1 = '_dev_ttyUSB1_2017-02-09_19_37_37.019_.txt'

dd0 = pd.read_table(pathname + filename0, sep=',')
dd1 = pd.read_table(pathname + filename1, sep=',')

#retira os valores com erro
dd0 = dd0.ix[pl.find(dd0.ix[:,3].isnull() == False),:]
dd1 = dd1.ix[pl.find(dd1.ix[:,3].isnull() == False),:]

#data como datetime
dd0.index = pd.to_datetime(dd0.index, format='%Y-%m-%d_%H:%M:%S.%f')
dd1.index = pd.to_datetime(dd1.index, format='%Y-%m-%d_%H:%M:%S.%f')

#escolhe o mesmo periodo de amostragem
ini = '2017-02-09 19:37:40'
fim = '2017-02-09 19:57:35'

dd0 = dd0[ini:fim]
dd1 = dd1[ini:fim]

#nome do index como data
dd0.index.name = 'date'
dd1.index.name = 'date'

dd0['PacketCounter'] = dd0['PacketCounter'].astype(int)
dd1['PacketCounter'] = dd1['PacketCounter'].astype(int)

#print(dd0.columns)
#print(dd1.columns)

# %matplotlib inline
# pl.figure(figsize=(10,8))
# pl.plot(dd0.index,'.')
# pl.plot(dd1.index,'.')
# # pl.xlim(5000,len(dd0))
# pl.grid()
#pl.show()

# print(dd0.index[0], dd1.index[0])
# print(dd0.index[-1], dd1.index[-1])

# for col in dd0.columns:
#     # print()
#     # col

#     #pl.figure(figsize=(10, 8))
#     #pl.plot(dd0.index, dd0[col], '.', label='USB0')
#     #pl.plot(dd1.index, dd1[col], '.', label='USB1')
#     #pl.grid()
#     #pl.legend(loc=0)
#     #pl.title(col)
#     #pl.xticks(rotation=20)

#     if col == ' magnecticFieldZ':
#         pl.ylim(0.2, 0.6)

# pl.plot(dd0[col])
#pl.show()

#pl.figure(figsize=(10,8))
#pl.plot(dd0.index, dd0[' AccelerationZ'] - dd0[' AccelerationZ'].mean())
#pl.plot(dd1.index, dd1[' AccelerationZ'] - dd1[' AccelerationZ'].mean())
#pl.title('Ac. Z')

#pl.figure(figsize=(10,8))
#pl.plot(dd0.index, dd0[' AccelerationZ'] - dd0[' AccelerationZ'].mean())
#pl.plot(dd1.index, dd1[' AccelerationZ'] - dd1[' AccelerationZ'].mean())
#pl.xlim(dd0.index[500], dd0.index[600])
#pl.title('Ac. Z')

#print(dd0[' AccelerationX'])
accX, accY, accZ, accV, velZ, heave = acc2heave.acc2heave(dd0[' AccelerationX'], dd0[' AccelerationY'], dd0[' AccelerationZ'], dd0[' EulerRoll'], dd0[' EulerPitch'], dd0[' EulerYaw'], 1./5)
# print(heave)
# print('Heave: ', heave.shape)
# print('dd0.index: ', dd0.index.shape)
# pl.plot(dd0.index[0:len(heave)], heave, '.')


# pl.figure()
# pl.plot(heave)
# pl.title('Heave')
# pl.show()
# print(dd0.index)


tit = ['accX', 'accY', 'accZ', 'accV', 'velZ', 'heave']
cont = 0
for a in [accX, accY, accZ, accV, velZ, heave]:
    pl.figure()
    pl.plot(a)
    pl.title(tit[cont])
    pl.savefig('../fig/' + tit[cont] + '.png')
    cont += 1

pl.show()