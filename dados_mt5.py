import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

# =========================
# ⚙️ CONFIGURAÇÃO GLOBAL
# =========================
MODO = "backtest"  # "live" ou "backtest"

# =========================
# CONEXÃO
# =========================
def conectar_mt5():
    if not mt5.initialize():
        raise Exception(f"Erro ao conectar MT5: {mt5.last_error()}")
    print("✅ MT5 conectado")

# =========================
# CANDLES GENÉRICO
# =========================
def pegar_candles(ativo, timeframe=mt5.TIMEFRAME_M5, n=500):

    if not mt5.symbol_select(ativo, True):
        raise Exception(f"Erro ao selecionar ativo {ativo}: {mt5.last_error()}")

    rates = mt5.copy_rates_from_pos(ativo, timeframe, 0, n)

    if rates is None or len(rates) == 0:
        raise Exception(f"Erro ao puxar dados do MT5: {mt5.last_error()}")

    df = pd.DataFrame(rates)

    if 'time' not in df.columns:
        raise Exception("Coluna 'time' não encontrada nos dados do MT5")

    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    return df

# =========================
# 🔵 TEMPO REAL (HOJE)
# =========================
def pegar_candles_hoje(ativo, timeframe=mt5.TIMEFRAME_M5):

    if not mt5.symbol_select(ativo, True):
        raise Exception(f"Erro ao selecionar ativo {ativo}: {mt5.last_error()}")

    tick = mt5.symbol_info_tick(ativo)
    agora = datetime.fromtimestamp(tick.time)

    inicio_dia = datetime(agora.year, agora.month, agora.day)
    print("TIMEFRAME:", timeframe)
    rates = mt5.copy_rates_range(
        ativo,
        mt5.TIMEFRAME_M5,
        inicio_dia,
        agora
    )

    if rates is None or len(rates) == 0:
        raise Exception(f"Nenhum dado retornado hoje: {mt5.last_error()}")

    df = pd.DataFrame(rates)

    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    return df

# =========================
# 🟢 BACKTEST (DIA COMPLETO)
# =========================
def pegar_candles_dia(ativo, data, timeframe=mt5.TIMEFRAME_M5):
    
    # =========================
    # SELECIONA ATIVO
    # =========================
    if not mt5.symbol_select(ativo, True):

        print(
            f"❌ Erro ao selecionar ativo: "
            f"{mt5.last_error()}"
        )

        return pd.DataFrame()

    # =========================
    # PERÍODO
    # =========================
    inicio = datetime(
        data.year,
        data.month,
        data.day
    )

    fim = datetime(
        data.year,
        data.month,
        data.day,
        23,
        59
    )

    # =========================
    # DEBUG
    # =========================
    print("\n🔎 DEBUG COLETA")

    print("Ativo:", ativo)

    print("Início:", inicio)

    print("Fim:", fim)

    # =========================
    # COLETA
    # =========================
    rates = mt5.copy_rates_range(
        ativo,
        timeframe,
        inicio,
        fim
    )

    print(
        "MT5 LAST ERROR:",
        mt5.last_error()
    )

    # =========================
    # VALIDAÇÕES
    # =========================
    if rates is None:

        print("❌ rates = None")

        return pd.DataFrame()

    if len(rates) == 0:

        print("⚠️ Nenhum candle encontrado")

        return pd.DataFrame()

    print(
        "✅ Candles encontrados:",
        len(rates)
    )
    print(rates[:5])
    # =========================
    # DATAFRAME
    # =========================
    df = pd.DataFrame(rates)

    if 'time' not in df.columns:

        print("❌ Coluna time ausente")

        return pd.DataFrame()

    df['time'] = pd.to_datetime(
        df['time'],
        unit='s'
    )

    df.set_index(
        'time',
        inplace=True
    )

    return df
# =========================
# 🔁 FUNÇÃO INTELIGENTE
# =========================
def pegar_dados(ativo, timeframe=mt5.TIMEFRAME_M5, data=None):

    if MODO == "live":
        return pegar_candles_hoje(ativo, timeframe)

    elif MODO == "backtest":
        if data is None:
            raise Exception("Você precisa passar uma data para backtest")
        return pegar_candles_dia(ativo, data, timeframe)

    else:
        raise Exception("Modo inválido! Use 'live' ou 'backtest'")