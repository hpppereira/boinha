'''
Wave Data Processing

Uses 2 main modules for data analysis
- Raw data
- Processed data

Developed by: Henrique P. P. Pereira
'''

import os
import numpy as np
import pandas as pd
from matplotlib import mlab

class WaveProc(object):
    
    def __init__(self):

        self.n1 = None
        # self.n2 = n2
        # self.n3 = n3
        # self.fs = fs
        # self.nfft = nfft
        # self.h = h

    #Espectro simples
    def espec1(self, x, fs, nfft):
        '''
         Calcula o espectro simples de uma serie real
        
         Dados de entrada: n1 = serie real
                           nfft - Numero de pontos utilizado para o calculo da FFT
                           fs - frequencia de amostragem
        
         Dados de saida: [aa] - col 0: vetor de frequencia
                                col 1: autoespectro
                                col 2: intervalo de confianca inferior
                                col 3: intervalo de confianca superior
        
         Infos:	detrend - mean
        			window - hanning
        			noverlap (welch) - 50%

        '''

        #received serie 
        self.x = x
        self.fs = fs
        self.nfft = nfft

        #calculo do espectro
        sp = mlab.psd(self.x, NFFT=self.nfft, Fs=self.fs, detrend=mlab.detrend_mean,
                      window=mlab.window_hanning, noverlap=self.nfft/2)

        self.f  = sp[1][1:]

        sp = sp[0][1:]

        #degrees of freedom
        self.dof = len(self.x) / self.nfft * 2
        
        #confidence interval 95%
        ici = sp * self.dof / 26.12
        ics = sp * self.dof / 5.63
        
        self.aa1 = np.array([self.f,sp,ici,ics]).T
        
        return self.aa1

    #Espectro cruzado
    def espec2(self, x, y, fs, nfft):

        """
        #
        # Calcula o espectro cruzado entre duas series reais
        #
        # Dados de entrada: x = serie real 1 (potencia de 2)
        #                   y = serie real 2 (potencia de 2)
        #                   nfft - Numero de pontos utilizado para o calculo da FFT
        #                   fs - frequencia de amostragem
        #
        # Dados de saida: [aa2] - col 0: vetor de frequencia
        #                         col 1: amplitude do espectro cruzado
        #                         col 2: co-espectro
        #                         col 3: quad-espectro
        #                         col 4: espectro de fase
        #                         col 5: espectro de coerencia
        #                         col 6: intervalo de confianca inferior do espectro cruzado
        #                         col 7: intervalo de confianca superior do espectro cruzado
        #                         col 8: intervalo de confianca da coerencia
        #
        # Infos:	detrend - mean
        #			window - hanning
        #			noverlap - 50%
        #
        """

        self.x = x
        self.y = y
        self.fs = fs
        self.nfft = nfft

        #cross-spectral density - welch method (complex valued)
        sp2 = mlab.csd(self.x, self.y, NFFT=self.nfft, Fs=self.fs, detrend=mlab.detrend_mean,
                       window=mlab.window_hanning, noverlap=self.nfft/2)

        self.f   = sp2[1][1:]

        sp2 = sp2[0][1:]
        
        #co e quad espectro (real e imag) - verificar com parente
        co = np.real(sp2)
        qd = np.imag(sp2)
        
        #phase (angle function)
        ph = np.angle(sp2,deg=True)
        
        #ecoherence between x and y (0-1)
        coer = mlab.cohere(self.x , self.y, NFFT=self.nfft, Fs=self.fs, detrend=mlab.detrend_mean, window=mlab.window_hanning, noverlap=self.nfft/2)
        coer = coer[0][1:]
        
        #intervalo de confianca para a amplitude do espectro cruzado - 95%
        ici = sp2 * 14 /26.12
        ics = sp2 * 14 /5.63
        
        #intervalo de confianca para coerencia
        icc = np.zeros(len(sp2))
        icc[:] = 1 - (0.05 ** (1 / (14 / 2.0 - 1)))
        
        self.aa2 = np.array([self.f,sp2,co,qd,ph,coer,ici,ics,icc]).T

        return self.aa2

    def wavenumber(self, f, h):

        ''' 
        Calculate wave number (k)
        Input:     
        h       - depth - profundidade
        df      - vetor de frequencia
        reg     - comprimento do vetor de frequencia
        
        Output: 
        k       - vetor numero de onda
        '''        

        self.f = f
        self.h = h
        
        g      = 9.8     #gravity accel
        self.k = []     #vetor numero de onda a ser criado
        kant   = 0.001  #k anterior
        kpos   = 0.0011 #k posterior

        for j in range(len(self.f)):

        	sigma = (2 * np.pi * self.f[j] ) ** 2
        	
        	while abs(kpos - kant) > 0.001:
        	
        		kant = kpos

        		dfk = g * kant * self.h * (1 / np.cosh(kant * self.h) ) ** 2 + g + np.tanh( kant * self.h)

        		fk = g * kant * np.tanh(kant * self.h) - sigma

        		kpos = kant - fk / dfk
        	
        	kant = kpos - 0.002
        	
        	self.k.append(kpos)
        
    #Pocessamento no dominio do tempo
    def timedomain(self):

        '''
        #======================================================================#
        
        Calcula parametros de onda no dominio do tempo
        
        Dados de entrada: t - vetor de tempo  
                          eta - vetor de elevacao
                          h - profundidade
        
        Dados de saida: pondat = [Hs,H10,Hmax,THmax,Tmed,]
        				  Hs - altura significativa
                        H10 - altura de 1/10 das maiores
                        Hmax - altura maxima
                        THmax - periodo associado a altura maxima
                        Tmed - periodo medio
        
        #======================================================================#
        '''

        # self.n1 = n1
        self.dt = 1/self.fs

        #criando os vetores H(altura),Cr(crista),Ca(cavado),T (periodo)
        Cr = []
        Ca = []
        H = []
        T = []

        #acha os indices que cruzam o zero ascendente
        z = np.where(np.diff(np.sign(self.n1)))[0]

        #zeros ascendentes e descendentes
        zas=z[0::2]
        zde=z[1::2]

        #calcula ondas individuas
        for i in range(0,len(zas)-1):
            onda = self.n1[zas[i]:(zas[i+1])+1] #perfil da onda
            cr = np.max(onda) #
            Cr.append(cr)
            ca = np.min(onda)
            Ca.append(ca)
            H.append(cr + np.abs(ca))
            T.append( (((zas[i+1])+1) - zas[i]) * self.dt )

        #coloca as alturas em ordem crescente
        Hss = np.sort(H)
        Hss = np.flipud(Hss)

        #calcula a altura significativa (H 1/3)
        div = len(Hss) / 3
        self.hs = np.mean(Hss[0:div+1])
        
        #calcula a altura das 1/10 maiores (H 1/10)
        div1 = len(Hss) / 10
        self.h10 = np.mean(Hss[0:div1+1]) #altura da media das um decimo maiores
        
        #altura maxima
        self.hmax = np.max(H)
        
        #periodo medio
        self.tmed = np.mean(T)
        
        #calcula periodo associado a altura maxima
        ind = np.where(H == self.hmax)[0][0]
        self.thmax = T[ind]

        #calculo o periodo maximo de zero ascendente
        self.tzamax = np.max(T)

    #Processamento no dominio da frequencia
    def freqdomain(self):
    
        """
        #======================================================================#
        
        Calcula parametros de onda no dominio da frequencia
        
        Dados de entrada: eta - vetor de elevacao
                          etax - vetor de deslocamento em x
                          etay - vetor de deslocamento em y
        					h - profundidade
        					nfft - Numero de pontos utilizado para o calculo da FFT
                          fs - frequencia de amostragem
        
        Dados de saida: pondaf = [hm0 tp dp]	
        
        #======================================================================#
        """
    
        # self.n1 = n1
        # self.n2 = n2
        # self.n3 = n3
        # self.fs = fs
        # self.nfft = nfft
        # self.h = n1
        

        #self.df = self.f[1] - self.f[0]
        #frequency vector
        #fv = fftshift(fftfreq(len(eta),1./fs))
        #fv = fv[len(fv)/2:]
    
        #spectral analysis
        self.sn1   = self.espec1(self.n1, self.fs, self.nfft)
        self.sn2   = self.espec1(self.n2, self.fs, self.nfft)
        self.sn3   = self.espec1(self.n3, self.fs, self.nfft)
        self.sn12  = self.espec2(self.n1,self.n2, self.fs, self.nfft)
        self.sn13  = self.espec2(self.n1,self.n3, self.fs, self.nfft)
        self.sn23  = self.espec2(self.n2,self.n3, self.fs, self.nfft)
        
        #delta freq
        self.df = self.f[3] - self.f[2]

        #calculo do numero de onda
        #self.wavenumber()
        #k = numeronda(h,f,len(f))
        #k = np.array(k)

        #calculo dos coeficientes de fourier - NDBC 96_01 e Steele (1992)
        c = self.sn2[:,1] + self.sn3[:,1]
        cc = np.sqrt(self.sn1[:,1] * (c))
    
        self.a1 = self.sn12[:,3] / cc
        self.b1 = self.sn13[:,3] / cc
    
        self.a2 = (self.sn2[:,1] - self.sn3[:,1]) / c
        self.b2 = 2 * self.sn12[:,2] / c
    
        #calcula direcao de onda
        #mean direction
        self.dire1 = np.array([np.angle(np.complex(self.b1[i],self.a1[i]),deg=True) for i in range(len(self.a1))])
    
        #principal direction
        self.dire2 = 0.5 * np.array([np.angle(np.complex(self.b2[i],self.a2[i]),deg=True) for i in range(len(self.a2))])
    
        #condicao para valores maiores que 360 e menores que 0
        self.dire1[np.where(self.dire1 < 0)]        = self.dire1[np.where(self.dire1 < 0)]   + 360
        self.dire1[np.where(self.dire1 > 360)]      = self.dire1[np.where(self.dire1 > 360)] - 360
        self.dire2[np.where(self.dire2 < 0)]        = self.dire2[np.where(self.dire2 < 0)]   + 360
        self.dire2[np.where(self.dire2 > 360)]      = self.dire2[np.where(self.dire2 > 360)] - 360
    
        #acha o indice da frequencia de pico
        ind = np.where(self.sn1[:,1] == np.max(self.sn1[:,1]))[0]
    
        #periodo de pico
        self.tp = (1. / self.f[ind])[0]
    
        #momento espectral de ordem zero total - m0
        self.m0 = np.sum(self.sn1[:,1]) * self.df
    
        #calculo da altura significativa
        self.hm0 = 4.01 * np.sqrt(self.m0)
    
        #direcao do periodo de pico
        self.dp = self.dire1[ind][0]
    
        #Espalhamento direcional
        #Formula do sigma1 do livro Tucker&Pitt(2001) "Waves in Ocean Engineering" pags 196-198
        c1 = np.sqrt(self.a1 ** 2 + self.b1 ** 2)
        c2 = np.sqrt(self.a2 ** 2 + self.b2 ** 2)
        
        s1 = c1 / (1-c1)
        s2 = (1 + 3 * c2 + np.sqrt(1 + 14 * c2 + c2 ** 2)) / (2 * (1 - c2))
        
        self.sigma1 = np.sqrt(2 - 2 * c1) * 180 / np.pi
        self.sigma2 = np.sqrt((1 - c2) / 2) * 180 / np.pi
    
        self.sigma1p = np.real(self.sigma1[ind])[0]
        self.sigma2p = np.real(self.sigma2[ind])[0]
    
        # pondaf = np.array([hm0, tp, dp, sigma1p, sigma2p])
    
        #hm0, tp, dp, sigma1, sigma2, sigma1p, sigma2p, f, df, k, sn, snx, sny, snn, snnx, snny, snxny, snxnx, snyny, a1, b1, a2, b2, dire1, dire2
        #return hm0, tp, dp, sigma1, sigma2, sigma1p, sigma2p, f, df, k, sn, snx, sny, snn, snnx, snny, snxny, snxnx, snyny, a1, b1, a2, b2, dire1, dire2


# def ondap(hm0,tp,dp,sn,dire1,df):
        
#         '''
    
#         #======================================================================#
#         Programa para calcular parametros
#         de onda nas particoes de sea e swell
        
#         desenvolvido para 32 gl
        
#         divide o espectro em 2 partes: 
#         parte 1 - 8.33 a 50 seg
#         parte 2 - 1.56 a 7.14 seg
        
#         calcula o periodo de pico de cada particao, e despreza o
#         pico 2 (menos energetico) se a energia for inferior a 15% da
#         energia do pico 1 (mais energetico)
#         #======================================================================#
    
#         '''
    
#         #vetor de frequencia e energia
#         f,s = sn[:,[0,1]].T
    
#         # seleciona os picos espectrais - considera somente 2 picos
#         g1=np.diff(s)
#         g1=np.sign(g1)
#         g1=np.diff(g1)
#         g1=np.concatenate(([0],g1))
#         g2=np.where(g1==-2)[0]
#         picos=1 # a principio e unimodal
#         l=np.size(g2)
    
#         # inicializar considerando ser unimodal
#         hm02 = np.nan #9999
#         tp2 = np.nan #9999
#         dp2 = np.nan #9999
#         hm01 = hm0
#         tp1 = tp 
#         dp1 = dp 
    
#         if l > 1: #verificando espacamento entre picos (espacamento maior que 4 df)
#         	fr=np.argsort(s[g2])[::-1] #frequencia decrescente
#         	er=np.sort(s[g2])[::-1] # energia decrescente
    
#         	if (f[g2[fr[1]]]-f[g2[fr[0]]]) > 4*(f[1]-f[0]) and (er[1]/er[0] >= 0.15): #adota criterio de 4*deltaf
#         		picos=2
            
#             # calcular o Hs dos picos pegando a cava e dividindo em pico 1 e pico 2
#         	if picos == 2:
#         		n1=g2[0] #pico mais energetico
#         		n2=g2[1] #pico menos energetico
#         		nc=np.where(g1[n1:n2]==2) #indice da cava
    
#         		#particao do swell e sea
#         		swell = range(n1+nc+1)
#         		sea = range(n1+nc+1,len(s))
    
#         		#maxima energia do swell
#         		esw = max(s[swell])
    
#         		#maxima energia do sea
#         		ese = max(s[sea])
    
#         		#indice do pico do swell
#         		isw = np.where(s==esw)[0][0]
    
#         		#indice do pico do sea
#         		ise = np.where(s==ese)[0][0]
    
#         		#altura sig. do swell
#         		hm0sw = 4.01 * np.sqrt(sum(s[swell]) * df)
    
#         		#altura sig. do sea
#         		hm0se = 4.01 * np.sqrt(sum(s[sea]) * df)
    
#         		#periodo de pico do swell
#         		tpsw = 1./f[isw]
    
#         		#periodo de pico do sea
#         		tpse = 1./f[ise]
    
#         		#direcao do swell
#         		dpsw = dire1[isw]
    
#         		#direcao do sea
#         		dpse = dire1[ise]
    
        		
#         		#deixa o pico 1 como swell e pico 2 como sea
#         		en1 = esw ; en2 = ese
#         		hm01 = hm0sw ; hm02 = hm0se
#         		tp1 = tpsw ; tp2 = tpse
#         		dp1 = dpsw ; dp2 = dpse
        	
#         		#seleciona pico 1 como mais energetico
#         		# e pico 2 com o menos energetico
#         		# if esw > ese:
#         		# 	en1 = esw ; en2 = ese
#         		# 	hm01 = hm0sw ; hm02 = hm0se
#         		# 	tp1 = tpsw ; tp2 = tpse
#         		# 	dp1 = dpsw ; dp2 = dpse
#         		# else:
#         		# 	en1 = ese ; en2 = esw
#         		# 	hm01 = hm0se ; hm02 = hm0sw
#         		# 	tp1 = tpse ; tp2 = tpsw
#         		# 	dp1 = dpse ; dp2 = dpsw
    
#         # pondaf1 = np.array([hm01, tp1, dp1, hm02, tp2, dp2])
    
#         return hm01, tp1, dp1, hm02, tp2, dp2 #pondaf1


        #def spread(en,a1,b1):
    
        #'''
        ##======================================================================#
        #Programa para calcular o espelhamento
        #angular
        #Kuik et al 1988
        #
        #Entrada:
        #en - espectro 1D
        #a1 - coef de fourier de 1 ordem
        #b1 - conef de fourir de 1 ordem 
    
        #Saida:
        #spr - valor do espalhamento angular para cada
        #frequencia
        ##======================================================================#
        #'''
    
        ##esplhamento com vetor complexo - radianos?
        #sprc = (2 * (1 - ( (a1**2 + b1**2) / (en**2) ) **0.5) **0.5)
    
        ##soma a parte real e imag e coloca em graus
        #spr = (np.real(sprc) + np.imag(sprc)) * 180 / np.pi
    
        ##parece que aparece na parte real onde tem energia no espectro
        #sprr = np.real(sprc)
    
        ##diminui 360 nos maiores que 360
        ## spr[np.where(spr>360)[0]] = spr[np.where(spr>360)[0]] - 360
    
        ##coloca zeros nos valores muito altos
        ## spr[np.where(spr>360)[0]] = 0
    
        #return sprc, spr, sprr
    
    