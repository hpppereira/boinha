'''
Programa para processar os dados do ADCP
instalado na Praia da Reserva junto
com a boia costeira

Henrique Pereira
Douglas Nemes
Felive Miranda
Bruno Saliba

Data da ultima modificacao: 16/11/2015

Observacoes:
- concatena os dados .wad (pegar o ja concatenado)
- processamento no dominio do tempo e frequencia
- processar utilizando a serie de velocidade veritical
 e dividir por omega2 para obter o espectro de heave
'''

import os
import numpy as np
import pylab as pl
import datetime as dt
import proconda
import jonswap
import espec
import pandas as pd

#pl.close('all')

reload(proconda)

#pathname = os.environ['HOME'] + '/Dropbox/nemes/dados/ADCP_Reef_Reserva/20150805/'
pathname = os.environ['HOME'] + '/Dropbox/coastalbuoy/dados/Reserva/ADCP/20151111/'

#carrega arquivo .sen
sen = np.loadtxt(pathname + 'ADCP_REEF_11_11_2015.sen')

#lista os arquivo .wad
lista = []
for f in os.listdir(pathname):
    if f.endswith('.wad'):
        lista.append(f)

lista = np.sort(lista)[1:] #retira o primeiro arquivo que tem todos os .wad (eh o primeiro do sort)

#retira os 2 ultimos arquivos que vieram ruins (adcp fora d agua?)
lista = lista[:-3]
sen = sen[:-3,:]

#cria data
data = np.array([dt.datetime(int(sen[i,2]),int(sen[i,0]),int(sen[i,1]),int(sen[i,3]),int(sen[i,4])) for i in range(len(sen))])

h = 2.5 #profundidade 
nfft = 128 #para 1024 pontos - 16 gl #numero de dados para a fft (p/ nlin=1312: 32gl;nfft=82, 16gl;nfft=164, 8gl;nfft=328)
fs = 2 #freq de amostragem
nlin = 512#comprimento da serie temporal a ser processada
gl = (nlin/nfft) * 2
t = np.linspace(0,nlin*1./fs,nlin) #vetor de tempo

#numero de testes habilitados (parametros para consistencia)
#ntb = 9 #brutos
#ntp = 3 #processado
#npa = 19 #numero de parametros a serem calculados

#retira o primeiro arquivo que tem todas as medicoes
#e os dados que o adcp estava fora da agua
#lista=np.sort(lista)[:]
#data = np.array(data)[0:37]

#matonda:  0    1   2    3    4    5    6  7  8    9       10     11  12   13  14  15   16  17  18   19
#         data, hs,h10,hmax,tmed,thmax,hm0,tp,dp,sigma1p,sigma2p,hm01,tp1,dp1,hm02,tp2,dp2,gam,gam1,gam2
matonda = [] #matriz com parametros de onda
matondap = [] #pressao - hs, tp dp
fase_nnx = [] #valor do espec de fase para a fp
fase_nny = [] #valor do espec de fase para a fp
fase_nxny = [] #valor do espec de fase para a fp
coer_nnx = [] #valor do espec de coerencia para a fp
coer_nny = [] #valor do espec de coerencia para a fp
coer_nxny = [] #valor do espec de coerencia para a fp

#concatena todos os valores de vz (para hist)
eta = np.array([])

dc = -1
#loop para processar os dados
for arq in lista:#:[0:1]:
    
    	dc += 1

        #data do processamento
        datan = data[dc]
    
    	print(arq + ' - ' + str(datan)) 
    
    	dd = np.loadtxt(pathname + arq)
    	pr, vx, vy, vz = dd[:,[2,5,6,7]].T
        vz = pr
    
    	eta = np.concatenate((eta,vz),axis=1)
    
    	#processamento no dominio do tempo
    	hs,h10,hmax,tmed,thmax = proconda.ondat(t,vz,h)
    
    	#processamento no dominio da frequencia
    	#hm0_pr, tp_pr, dp_pr, sigma1, sigma2, sigma1p, sigma2p, freq, df, k, sn_pr, snx,sny, snn, snnx, snny, snxny, snxnx, snyny, a1, b1, a2, b2, dire1_pr, dire2 = proconda.ondaf(
    	#pr,vx,vy,h,nfft,fs) ##pressao
    
    	hm0, tp, dp, sigma1, sigma2, sigma1p, sigma2p, freq, df, k, sn, snx,sny, snn, snnx, snny, snxny, snxnx, snyny, a1, b1, a2, b2, dire1, dire2 = proconda.ondaf(
    	vz,vx,vy,h,nfft,fs)
     
     
     #calcula os espectros de pr, vz, vx e vy
    	apr = espec.espec1(pr,nfft,fs)
    	avz = espec.espec1(vz,nfft,fs)
    	avx = espec.espec1(vx,nfft,fs)
    	avy = espec.espec1(vy,nfft,fs)
    
    
    	#corrige a declinacao magnetica
    	dp = dp - 23
    	dire1 = dire1 - 23
    	dire2 = dire2 - 23
    
    	#calcula o espectro de fase (fase e coerencia)
    	#acha o indice da fp
    	indfp = pl.find(sn[:,0]==sn[sn[:,1]==max(sn[:,1]),0])
    
    	fase_nnx.append(np.real(snnx[indfp,4])[0]) #fase de heave e dspx
    	fase_nny.append(np.real(snny[indfp,4])[0]) #fase de heave e dspx
    	fase_nxny.append(np.real(snxny[indfp,4])[0]) #fase de heave e dspx
    
    	coer_nnx.append(np.real(snnx[indfp,5])[0]) #coerencia de heave e dspx
    	coer_nny.append(np.real(snny[indfp,5])[0]) #coerencia de heave e dspx
    	coer_nxny.append(np.real(snxny[indfp,5])[0]) #coerencia de heave e dspx
    
        '''
    	# #plota serie
    	# pl.figure()
    	# pl.plot(t,vz)
    	# pl.title(str(data[dc]) + ' - Hs=%.1f' %hm0 + ' m ; Tp=%.1f ' %tp + 's; Dp=%i' %dp + ' gr')
    	# pl.plot([t[0],t[-1]],[0,0],'--r',linewidth=3)
    	# pl.axis('tight'), pl.grid()
    	# pl.ylim(-1.2,1.2)
    	# pl.ylabel('Vel. Z (m/s)')
    	# pl.xlabel('Tempo (s)')
    	# pl.savefig('fig/vz_serie_' + data[dc].strftime('%Y%m%d%H%M'))
    
        '''
    	#plota o espectro
    	pl.figure()
    	pl.subplot(211)
    	pl.plot(sn[:,0],sn[:,1])
    	#pl.plot(sn_pr[:,0],sn_pr[:,1],label='pr')
    	pl.title(str(data[dc]) + ' - Hs=%.1f' %hm0 + ' m ; Tp=%.1f ' %tp + ' s; Dp=%i' %dp + ' gr')
    	pl.grid()
    	pl.legend()
    	pl.ylabel(r'$(m/s)^{2}/Hz$',size=14)
    	pl.subplot(212)
    	pl.plot(sn[:,0],dire1)
    	pl.yticks(np.arange(0,360+45,45))
    	pl.ylim(0,360)
    	#pl.plot(sn_pr[:,0],dire1_pr)
    	pl.grid()
    	pl.xlabel('Freq. (Hz)')
    	pl.ylabel('Dir (graus)')
    	pl.savefig('fig/20151111/espec_pr_ADCP_' + data[dc].strftime('%Y%m%d%H%M'))
        '''
    
    	#plota o espectro de cada variavel (pr, vz, vx e vy)
    	pl.figure()
    	pl.subplot(221)
    	pl.plot(apr[:,0],apr[:,1])
    	pl.title('Pressao')
    	pl.grid()
    	pl.subplot(222)
    	pl.plot(avz[:,0],avz[:,1])
    	pl.title('Vz')
    	pl.grid()
    	pl.subplot(223)
    	pl.plot(avx[:,0],avx[:,1])
    	pl.title('Vx')
    	pl.grid()
    	pl.subplot(224)
    	pl.plot(avy[:,0],avy[:,1])
    	pl.title('Vy')
    	pl.grid()
       	pl.savefig('fig/20151111/espec_ADCP_' + data[dc].strftime('%Y%m%d%H%M'))
     
        pl.close('all')
        '''

    	#processamento no dominio da frequencia particionado (sea e swell)
    	hm01, tp1, dp1, hm02, tp2, dp2 = proconda.ondap(hm0,tp,dp,sn,dire1,df)
    
    	#calculo do parametro gamma - LIOc
    	gam = jonswap.gamma(tp)
    	gam1 = jonswap.gamma(tp1)
    	gam2 = jonswap.gamma(tp2)
    
    	#espectro de jonswap
    	s_js = jonswap.spec(hm0,tp,freq,gam)
    	s_js2 = jonswap.spec(hm02,tp2,freq,gam2)
    
    	#concatena os dados
    	matonda.append([int(data[dc].strftime('%Y%m%d%H%M')),hs,h10,hmax,tmed,thmax,hm0,tp,dp,sigma1p,sigma2p,hm01,tp1,dp1,hm02,tp2,dp2,gam,gam1,gam2])

#	matondap.append([hm0_pr,tp_pr,dp_pr])

matonda = np.array(matonda)
#matondap = np.array(matondap)
#data = np.array(data)

#converte para dataframe
dw = pd.DataFrame(matonda[:,1:],columns=['hs','h10','hmax','tmed','thmax','hm0','tp','dp','sigma1p','sigma2p','hm01','tp1','dp1','hm02','tp2','dp2','gam','gam1','gam2'])
dw = dw.set_index(data)

#eta = np.array(eta).reshape(np.size(eta),1)
'''
pl.figure()
h = pl.hist(eta,100)
pl.axis('tight')
pl.xlim(-1,1)
pl.grid()
pl.xlabel(r'$m/s$',fontsize=14)
pl.ylabel(r'$Nu\'mero\ de\ ocorre\^ncias$',fontsize=14)
pl.plot([0,0],[0,np.max(h[0])],'r--',linewidth=3)


pl.figure()
pl.plot(vz)

pl.figure()
pl.plot(sn[:,0],sn[:,1])

pl.figure()
pl.subplot(311)
pl.plot(data,matonda[:,6],label='vz')
#pl.plot(data,matondap[:,0],label='pr')
pl.legend()
pl.ylabel('Hm0 (m)')
pl.subplot(312)
pl.plot(data,matonda[:,7])
#pl.plot(data,matondap[:,1])
pl.ylabel('Tp (s)')
pl.subplot(313)
#pl.plot(data,matondap[:,2])
pl.plot(data,matonda[:,8])
pl.ylabel('Dp (graus)')

pl.figure()
pl.title('Espectros de Fase')
pl.plot(data,fase_nnx,label='nnx')
pl.plot(data,fase_nny,label='nny')
pl.plot(data,fase_nxny,label='nxny')
pl.ylabel('graus')

'''

pl.show()

