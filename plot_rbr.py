# processamento RBR praia de caopacabana

import pandas as pd
import matplotlib.pyplot as plt

plt.close('all')

# pth = 'teste_copacabana_20240921/RBR/055161_20240921_1904.xlsx'
pth = '../dados/teste_copacabana_20240929/RBR/055161_20240929_1733.xlsx'

df = pd.read_excel(pth,
        sheet_name='Bursts', header=1)

df.index = pd.to_datetime(df.Time, format="%Y-%m-%d %H:%M:%S.%f")

df.index.name = 'time'

# df.Wave.plot(ylabel='Heave [m]', grid='on')
df.Pressure.plot(ylabel='Pressure [dbar]', grid='on')

plt.show(block=False)


