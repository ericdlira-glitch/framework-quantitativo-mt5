import pandas as pd


def calcular_medias(df, mm9=9, mm21=21, mm50=50, mm200=200):
    
    df = df.copy()

    # Cálculo das Médias Móveis Simples (SMA) ou Exponenciais (EMA)
    df['mm9']   = df['close'].rolling(window=mm9).mean()
    df['mm21']  = df['close'].rolling(window=mm21).mean()
    df['mm50']  = df['close'].rolling(window=mm50).mean()
    df['mm200'] = df['close'].rolling(window=mm200).mean()
    df["mm50_slope"] = (df["mm50"] - df["mm50"].shift(5)) / df["mm50"].shift(5)
    return df


def definir_tendencia(df):
    df = df.copy()
    df['tendencia'] = 0

    df.loc[df['mm21'] > df['mm50'], 'tendencia'] = 1
    df.loc[df['mm21'] < df['mm50'], 'tendencia'] = -1

    return df


def contexto_diario(df):
    df = calcular_medias(df)
    df = definir_tendencia(df)
    return df

def contexto_venda_favoravel(df, i):
    mm9 = df.loc[i, "mm9"]
    mm21 = df.loc[i, "mm21"]

    if pd.isna(mm9) or pd.isna(mm21):
        return False

    return mm9 < mm21

def contexto_compra_favoravel(df, i):
    mm9 = df.loc[i, "mm9"]
    mm21 = df.loc[i, "mm21"]

    if pd.isna(mm9) or pd.isna(mm21):
        return False

    # tendência de alta
    return mm9 > mm21