import pandas as pd
import MetaTrader5 as mt5

from dados_mt5 import pegar_candles, conectar_mt5


def converter_volume(valor):
    valor = str(valor).strip()

    if valor.endswith('B'):
        return float(valor.replace('B', '').replace(',', '.')) * 1_000_000_000
    elif valor.endswith('M'):
        return float(valor.replace('M', '').replace(',', '.')) * 1_000_000
    elif valor.endswith('K'):
        return float(valor.replace('K', '').replace(',', '.')) * 1_000
    else:
        return float(valor.replace(',', '.'))


def carregar_dados(modo="csv", caminho_csv=None):

    if modo == "csv":
        df = pd.read_csv(caminho_csv)

        df = df.rename(columns={
            'Data': 'date',
            'Abertura': 'open',
            'Máxima': 'high',
            'Mínima': 'low',
            'Último': 'close',
            'Vol.': 'volume'
        })

        if 'Var%' in df.columns:
            df = df.drop(columns=['Var%'])

        df['date'] = pd.to_datetime(df['date'], dayfirst=True)

        for col in ['open', 'high', 'low', 'close']:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )

        df['volume'] = df['volume'].apply(converter_volume).astype(float)

        df = df.sort_values('date')
        df.set_index('date', inplace=True)

        return df

    elif modo == "mt5":
        conectar_mt5()
        return pegar_candles("USTEC", mt5.TIMEFRAME_M5, 500)

    else:
        raise ValueError("Modo inválido")