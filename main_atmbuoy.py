"""
Processamento dos dados da Boinha

16/05/2018
AtmosMarine
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

pathname = os.environ['HOME'] + '/Dropbox/atmbuoy/data/teste_20180504/'
filename = 'A201805161500.csv'

df = pd.read_csv(pathname + filename)

df['datetime'] = pd.to_datetime(df.datetime)

df = df.set_index('datetime')



for c in df.columns:
    print c
    plt.figure()
    plt.plot(df[c])
    plt.title(c)
    plt.savefig('../fig/%s' %c)
    plt.close('all')