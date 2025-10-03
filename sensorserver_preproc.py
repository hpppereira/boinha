# Organiza tabela de dados


import pandas as pd
from datetime import datetime, timedelta
from time import sleep


df_concat = pd.read_csv('data/boinha.csv', parse_dates=True, index_col='datetime')

while True:

    # lê o CSV
    df1 = pd.read_csv("data/sensores.csv")

    # remove espacos do cabecalho
    df1.columns = [c.strip() for c in df1.columns]

    # cria um dicionário de DataFrames, um por sensor
    dfs = {sensor: g.reset_index(drop=True) for sensor, g in df1.groupby("sensor_type")}

    # remove espacos 
    dfs = {sensor.strip().split('.')[-1]: g for sensor, g in dfs.items()}

    df = pd.DataFrame()
    for k in dfs.keys():

        aux = dfs[k]

        # data em hora local
        # aux['date'] = pd.to_datetime(aux['wall_time'], unit='s') - timedelta(hours=3)
        aux['datetime'] = pd.to_datetime(aux['datetime'])

        aux.set_index('datetime', inplace=True)

        aux.drop(['wall_time', 'sensor_type', 'timestamp_ns'], axis=1, inplace=True)

        aux.columns = [f'{k}_{c}' for c in aux.columns]

        aux = aux.resample('0.2s').mean()

        df = pd.concat([df, aux], axis=1)
        # df = df.join(aux, how='outer')

    df_concat = pd.concat([df_concat.drop_duplicates(),
                           df.drop_duplicates()], axis=0)

    df = df.dropna()

    print (df.iloc[-1])

    df.to_csv('data/boinha.csv', float_format='%.6f', index=True)

    sleep(1)

    print ('\n')