#!/work/projetos/projeto-oceanpact_surf/venv/bin/python

import os
import matplotlib
matplotlib.use('Agg')
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from importlib import reload
from datetime import datetime, timedelta
from glob import glob
sys.path.append('../ocean-wave/')
import waveproc, waveplot
reload(waveproc)
reload(waveplot)
from waveproc import time_domain, freq_domain, \
                     prob_domain, wave_group
from pathlib import Path
import subprocess
from time import sleep


if __name__ == "__main__":

    pth_out = 'data/'
    fln = 'boinha'
    # boia = '6613'

    filepath = os.path.join(pth_out, f'{fln}.csv')

    print ('Iniciando processamento com dos dados de heave', flush=True)

    param = pd.DataFrame() # quando for a primeira vez    

    # param = pd.read_csv(pth_out + f'param_{fln}.csv',
    #                     parse_dates=True, index_col='date')

    while True:

            # leitura dos dados do heave
            try:
                df = pd.read_csv(filepath, parse_dates=True, index_col='date')


                df['heave'] = df.linear_acceleration_z

                # iniciar as 2025-07-16 14:30:00 - local
                # df = df.iloc[294:]
                # param = pd.read_csv(f'out/op_param_obscape_{boia}.csv',
                #                      parse_dates=True, index_col='date')

                delta = np.diff(df.index)[-1]
                dt = delta / np.timedelta64(1, 's')
                fs = 1.0 / dt

                # duracao da serie temporal, em minutos
                ii = 5
                intervalo = int(ii*60*fs)

                df1 = df.iloc[-intervalo:]

                print (df1.index[-1], flush=True)
                print (len(df1), flush=True)

                nfft = int(len(df1) / 4)

                t = np.arange(0, len(df1)*dt, dt)
                n1 = df1.heave.values

                ppt, tt = time_domain(t, n1)

                ppf, cc = freq_domain(t, n1, s2=[], s3=[],
                                    Fs=fs, NFFT=nfft)

                ppp = prob_domain(n1, tt)

                ppg, envelope_hilbert = wave_group(n1, ppt, tt, ppf, cc,
                                                fs, nfft)

                pp = pd.concat([ppt, ppf, ppp, ppg, ], axis=1)

                pp['date'] = df1.index[-1]
                pp.set_index('date', inplace=True)

                param = pd.concat([param, pp], axis=0)

                param.sort_index(inplace=True)

                param = param[~param.index.duplicated(keep='first')]

                print (param, flush=True)

                param.to_csv(pth_out + f'param_{fln}.csv',
                            float_format='%.3f')

                time.sleep(5)

            except:
                 sleep(1)
