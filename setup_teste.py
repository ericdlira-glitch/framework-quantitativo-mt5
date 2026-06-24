import numpy as np
import pandas as pd


def gerar_sinais_mm3_mm10_mm50_lateral_teste(df):

    df = df.copy()

    # =========================
    # INDICADORES
    # =========================
    df["mm3"] = df["close"].rolling(3).mean()
    df["mm10"] = df["close"].rolling(10).mean()
    df["mm50"] = df["close"].rolling(50).mean()

    # =========================
    # PERNADA
    # =========================
    df["low_20"] = df["low"].rolling(20).min()
    df["high_20"] = df["high"].rolling(20).max()

    df["pernada_alta"] = (
        df["high_20"] - df["low_20"]
    )
    
    # =========================
    # VOLATILIDADE
    # =========================
    df["range_20"] = (
        (df["high"] - df["low"])
        .rolling(20)
        .mean()
    )
        
    # =========================
    # CANDLE / VOLUME
    # =========================
    df["corpo"] = (
        df["close"] - df["open"]
    ).abs()

    df["tamanho_total"] = (
        df["high"] - df["low"]
    )
    
    df["media_corpos_6"] = (
        df["corpo"].rolling(6).mean()
    )

    df["media_volume_6"] = (
        df["tick_volume"].rolling(6).mean()
    )

    # =========================
    # FLUXO VETORIZADO
    # =========================
    candle_fluxo_individual = (
        (df["close"] > df["open"])
        &
        (
            df["corpo"]
            >
            df["media_corpos_6"].shift(1) * 1.5
        )
        &
        (
            df["tick_volume"]
            >
            df["media_volume_6"].shift(1)
        )
    )

    df["qtd_candles_fortes"] = (
        candle_fluxo_individual
        .astype(int)
        .rolling(10)
        .sum()
        .shift(1)
    )

    # =========================
    # CONFIG
    # =========================
    COOLDOWN = 10
    RISCO_MAXIMO = 18
    RR = 2
    DISTANCIA_MAX_MM10 = 20
    TICK = 0.25

    inicio = pd.to_datetime(
        "13:00"
    ).time()

    fim = pd.to_datetime(
        "18:00"
    ).time()

    # =========================
    # ARRAYS NUMPY
    # =========================
    tamanho = len(df)

    times = df.index.time

    closes = df["close"].values
    opens = df["open"].values
    highs = df["high"].values
    lows = df["low"].values

    mm3 = df["mm3"].values
    mm10 = df["mm10"].values
    mm50 = df["mm50"].values

    corpos = df["corpo"].values
    media_corpos_6_arr = (
    df["media_corpos_6"].values
)
    tamanhos_totais = df["tamanho_total"].values

    pernadas = df["pernada_alta"].values
    range_medio = (
    df["range_20"].values
)

    qtd_fortes = (
        df["qtd_candles_fortes"].values
    )

    # =========================
    # ARRAYS RESULTADO
    # =========================
    sinal_arr = np.zeros(
        tamanho,
        dtype=int
    )

    setup_arr = np.full(
        tamanho,
        None,
        dtype=object
    )

    entrada_arr = np.full(
        tamanho,
        np.nan
    )

    stop_arr = np.full(
        tamanho,
        np.nan
    )

    tp_arr = np.full(
        tamanho,
        np.nan
    )

    lado_arr = np.full(
        tamanho,
        None,
        dtype=object
    )

    grupo_arr = np.full(
        tamanho,
        None,
        dtype=object
    )

    debug_arr = np.full(
        tamanho,
        None,
        dtype=object
    )

    ultimo_sinal_idx = -20

    # =========================
    # LOOP PRINCIPAL
    # =========================
    for i in range(50, tamanho):

        hora_atual = times[i]

        # =========================
        # HORÁRIO
        # =========================
        if not (
            inicio <= hora_atual <= fim
        ):

            debug_arr[i] = (
                "fora_horario"
            )

            continue

        # =========================
        # COOLDOWN
        # =========================
        if (
            i - ultimo_sinal_idx
            <
            COOLDOWN
        ):

            debug_arr[i] = "cooldown"

            continue

        # =========================
        # DISTÂNCIA MM10
        # =========================
        distancia_mm10 = abs(
            closes[i - 1]
            -
            mm10[i - 1]
        )

        if (
            distancia_mm10
            >
            DISTANCIA_MAX_MM10
        ):

            debug_arr[i] = (
                "distante_mm10"
            )
            continue
        # =========================
        # MM50
        # =========================
        if not (
            mm50[i] < closes[i]
        ):

            debug_arr[i] = (
                "mm50_acima_gatilho"
            )

            continue
        
        # =========================
        # VOLATILIDADE
        # =========================
        if range_medio[i] > 15:

            debug_arr[i] = (
                "volatilidade_alta"
            )

            continue
        
        # =========================
        # INCLINAÇÃO MM10
        # =========================
        inclinacao_mm10 = abs(
            mm10[i]
            -
            mm10[i - 3]
        )

        if inclinacao_mm10 > 6:

            debug_arr[i] = (
                "mm10_muito_inclinada"
            )

            continue

        # =========================
        # PADRÃO CANDLE
        # =========================
        if not (
            closes[i - 1]
            <
            opens[i - 1]
        ):

            debug_arr[i] = (
                "anterior_nao_baixa"
            )

            continue

        if not (
            closes[i] > opens[i]
        ):

            debug_arr[i] = (
                "gatilho_nao_alta"
            )

            continue

        # =========================
        # TOQUE MM10
        # =========================
        if not (
            lows[i]
            <=
            mm10[i] + TICK
        ):

            debug_arr[i] = (
                "nao_tocou_mm10"
            )

            continue
        
        # # =========================
        # # ANTI-DOJI
        # # =========================
        if tamanhos_totais[i] > 0:

            proporcao_corpo = (
                corpos[i]
                /
                tamanhos_totais[i]
            )

            if proporcao_corpo <= 0.50:

                debug_arr[i] = (
                    "gatilho_e_doji"
                )

                continue
            
        # =========================
        # FILTRO: CANDLE EXPANSIVO
        # =========================
        if (
            corpos[i]
            <
            media_corpos_6_arr[i - 1] * 1.2
        ):

            debug_arr[i] = (
                "gatilho_sem_expansao"
            )

            continue
        
        if corpos[i] > media_corpos_6_arr[i - 1] * 2.5:
            
            debug_arr[i] = (
                "gatilho_exagerado"
            )

            continue
        
        # =========================
        # ALINHAMENTO MM3
        # =========================
        if not (
            mm3[i] > mm10[i]
        ):

            debug_arr[i] = (
                "mm3_abaixo_mm10"
            )

            continue

        if not (
            mm3[i] > mm3[i - 3]
        ):

            debug_arr[i] = (
                "mm3_sem_inclinacao"
            )

            continue

        # =========================
        # PULLBACK
        # =========================
        if closes[i] < mm10[i] + 1:

            debug_arr[i] = (
                "pullback_longo"
            )

            continue

        # =========================
        # FLUXO
        # =========================
        if qtd_fortes[i] < 2:

            debug_arr[i] = (
                "pernada_sem_fluxo"
            )

            continue

        # =========================
        # ENTRADA
        # =========================
        entrada = highs[i] + 2

        stop = lows[i]

        risco = entrada - stop
        
        # =========================
        # EXPANSÃO MM3/MM10
        # =========================
        distancia_mm3_mm10 = (
            mm3[i] - mm10[i]
        )

        print(
            f"{df.index[i]} | "
            
            f"dist_mm3_mm10={round(distancia_mm3_mm10,2)} | "
            
            f"inclinacao_mm10={round(inclinacao_mm10,2)} | "
            
            f"dist_preco_mm10={round(distancia_mm10,2)} | "
            
            f"qtd_fortes={int(qtd_fortes[i])} | "
            
            f"range20={round(range_medio[i],2)} | "
            
            f"risco={round(risco,2)}"
        )

        if distancia_mm3_mm10 < 4:

            debug_arr[i] = (
                "mm3_sem_expansao"
            )
            continue
        
        if distancia_mm3_mm10 > 7:
        
            debug_arr[i] = (
                "mm3_muito_esticada"
            )

            continue
        # =========================
        # FECHAMENTO FORTE
        # =========================
        # distancia_topo = (
        #     highs[i] - closes[i]
        # )

        # if distancia_topo > (
        #     tamanhos_totais[i] * 0.25
        # ):

        #     debug_arr[i] = (
        #         "fechamento_fraco"
        #     )

        #     continue

        # =========================
        # RISCO
        # =========================
        if risco <= 0:

            debug_arr[i] = (
                "risco_invalido"
            )

            continue

        if risco < 5:

            debug_arr[i] = (
                "risco_muito_curto"
            )

            continue

        if risco > RISCO_MAXIMO:

            debug_arr[i] = (
                "risco_alto"
            )

            continue

        # =========================
        # CLASSIFICAÇÃO
        # =========================
        pernada_alta = pernadas[i]

        if pernada_alta < 50:

            grupo = "0-50"

        elif pernada_alta < 100:

            grupo = "50-100"

        elif pernada_alta < 150:

            grupo = "100-150"

        else:

            grupo = "150+"

        # =========================
        # SINAL
        # =========================
        sinal_arr[i] = 1

        setup_arr[i] = (
            "sinais_mm3_mm10_mm50_teste"
        )

        entrada_arr[i] = entrada

        stop_arr[i] = stop

        tp_arr[i] = (
            entrada + (risco * RR)
        )

        lado_arr[i] = "compra"

        grupo_arr[i] = grupo

        debug_arr[i] = (
            f"setup_ok | "
            
            f"dist_mm3_mm10={round(distancia_mm3_mm10,2)} | "
            
            f"inclinacao_mm10={round(inclinacao_mm10,2)} | "
            
            f"dist_preco_mm10={round(distancia_mm10,2)} | "
            
            f"qtd_fortes={int(qtd_fortes[i])} | "
            
            f"range20={round(range_medio[i],2)} | "
            
            f"risco={round(risco, 2)} | "
            
            f"grupo={grupo}"
        )
        ultimo_sinal_idx = i

        print(
            f"🚀 SINAL GERADO EM "
            f"{df.index[i]}"
        )

    # =========================
    # ATRIBUIÇÃO FINAL
    # =========================
    df["sinal"] = sinal_arr
    df["setup_usado"] = setup_arr
    df["preco_entrada"] = entrada_arr
    df["stop"] = stop_arr
    df["tp"] = tp_arr
    df["lado"] = lado_arr
    df["grupo_pernada"] = grupo_arr
    df["debug"] = debug_arr

    return df