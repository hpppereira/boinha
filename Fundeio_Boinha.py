
# coding: utf-8

# # Avaliação do Fundeio da Boinha
# - Samuel Stefani
# - Henrique Pereira
# - Fabio Nascimento
# - 18/10/2017
# 
# ## Descrição
# 
# - Sistema de Coordenadas:
# - Paralelo a praia: eixo X
# - Perpendicular a praia: eixo Y
# - Vertical: Eixo Z

# In[22]:


# import bibliotecas

import numpy as np
import pandas as pd
import xlrd


# ## Entrada de Dados

# In[28]:


# Cabos

comprimento_cabo_x = [10,20,30]
comprimento_cabo_y = [10,20,30,40,50]

carga_ruptura = 380 #kg
alongamento_cabo = 0.15 #% - a 380 kg o cabo alonga 15% e rompe

x1 = 0
y1 = 30
x2 = 0
y2 = -30
zi = 3.5
zf = 5
k1 = 0.15
C1 = carga_ruptura
k2 = 0.15
C2 = carga_ruptura

# Boia
raio_boia = 0.2 #metros
coef_arrasto = 0.470
area_lateral = np.pi * raio_boia ** 2

# Ondas


# In[9]:





# ## Leitura de Arquivo Externo (excel)

# In[26]:


# leitura das especificacoes do cabo

# pathname = '/home/hp/Dropbox/boinha/fundeio/'
# filename = 'Tabela_Fundeio.xlsx'

# # xls = pd.read_excel(pathname + filename)
# xls = xlrd.open_workbook(pathname + filename)


# ## Funções 

# In[35]:


# Deslocamento Horizontal da Boia

def deltay2(x1,y1,x2,y2,zi,zf,k1,C1,k2,C2):
 
    """
    Descricao:
    
    Input:
    x1 - Comprimento do Cabo para offshore
    y1 - ...
    ...
    
    Output:
    D - Deslocamento horizontal do cabo (positivo: offshore, negativo: praia)
    R - Limite??
    """
    
    # Comprimento inicial dos cabos 1 e 2
    Li1=np.sqrt(x1**2+y1**2+zi**2)
    Li2=np.sqrt(x2**2+y2**2+zi**2)
    
    D=0
    R=(2*C1*((np.sqrt(x1**2+(y1-D)**2+zf**2))-Li1)*(y1-D))/(k1*Li1*(np.sqrt(x1**2+(y1-D)**2+zf**2)))     + (C2*(np.sqrt(x2**2+(y2-D)**2+zf**2)-Li2)*(y2+D))/(k2*Li2*(np.sqrt(x2**2+(y2+D)**2+zf**2)))
    
    while R>0.05 or R<-0.05:
        D=D+0.0001
        R=(2*C1*((np.sqrt(x1**2+(y1-D)**2+zf**2))-Li1)*(y1-D))/(k1*Li1*(np.sqrt(x1**2+(y1-D)**2+zf**2)))         + (C2*(np.sqrt(x2**2+(y2-D)**2+zf**2)-Li2)*(y2+D))/(k2*Li2*(np.sqrt(x2**2+(y2+D)**2+zf**2)))

        R1 = C2*(np.sqrt(x2**2+(y2-D)**2+zf**2)-Li2)*(y2+D)/(k2*Li2*(np.sqrt(x2**2+(y2+D)**2+zf**2)))
    
    print ('R=%.5f --> D=%.5f' %(R, D))
    
    return D, R, R1


# In[ ]:


# Comprimento do Cabo na posicao da onda

def comp_cabo_onda(comp_x, ....):
    
    compr_vale = ..
    compr_cabo = ..
    
    return comp, ...


# In[27]:


# Tração máxima em kg

def tracao_max():
    
    ...


# ## Execução

# In[36]:


d, r, r1 = deltay2(x1,y1,x2,y2,zi,zf,k1,C1,k2,C2)


# In[38]:


r1

