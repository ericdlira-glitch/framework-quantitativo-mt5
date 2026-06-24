import numpy as np
import pandas as pd


def gerar_sinais_mm3_mm10_mm50_lateral(df):

    df = df.copy()

    # =========================
    # INDICADORES
    # =========================
    df["mm3"] = df["close"].rolling(3).mean()
    df["mm10"] = df["close"].rolling(10).mean()
    df["mm50"] = df["close"].rolling(50).mean()

    # =========================
    # PERNADA EXPLOSIVA CURTA (Substituindo o rolling de 20)
    # =========================
    JANELA_CURTA = 4  # Captura a variação nos últimos 4 candles
    
    # 1. Encontra a amplitude estrita desse bloco curto
    df["low_curto"] = df["low"].rolling(JANELA_CURTA).min()
    df["high_curto"] = df["high"].rolling(JANELA_CURTA).max()
    df["pernada_alta"] = df["high_curto"] - df["low_curto"]
    
    # 2. Filtro de Força: O preço andou rápido? (Preço Atual vs Fechamento de X candles atrás)
    # Isso garante que o preço subiu de verdade nesses poucos candles
    df["momentum_preco"] = df["close"] - df["close"].shift(JANELA_CURTA)
    
    # 3. Filtro de Volume Acumulado: Teve volume comprador injetado na pernada?
    df["volume_acumulado_pernada"] = df["tick_volume"].rolling(JANELA_CURTA).sum()
    df["media_volume_antecedente"] = df["tick_volume"].shift(JANELA_CURTA).rolling(10).mean()
    
    
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
    # =========================
    # FLUXO VETORIZADO (Ajustado para Pernada Curta)
    # =========================
    candle_fluxo_individual = (
        (df["close"] > df["open"])
        & (df["corpo"] > df["media_corpos_6"].shift(1) * 1.5)
        & (df["tick_volume"] > df["media_volume_6"].shift(1))
    )

    # Agora contamos quantos desses candles fortes aconteceram 
    # EXATAMENTE dentro da nossa janela de pernada de 4 períodos
    df["qtd_candles_fortes"] = (
        candle_fluxo_individual
        .astype(int)
        .rolling(4) # Mudamos de 10 para 4 para casar com a nova pernada
        .sum()
        .shift(1) # Mantém a proteção contra olhar pro futuro
    )

    # =========================
    # CONFIG
    # =========================
    COOLDOWN = 10
    RISCO_MAXIMO = 18
    RR = 2
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

        # Em vez de um limite fixo de 20 pontos, o preço de fechamento 
        #  não pode estar mais longe da média do que o tamanho do stop aceitável.
        if distancia_mm10 > RISCO_MAXIMO:
            debug_arr[i] = "fechamento_muito_longe_da_mm10"
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
        # INCLINAÇÃO MM10
        # =========================
        inclinacao_mm10 = (
            mm10[i]
            -
            mm10[i - 3]
        )

        if inclinacao_mm10 < 2:

            debug_arr[i] = (
                "mm10_sem_inclinacao"
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
        
        # ==================================================
        # FILTRO: AFASTAMENTO MÁXIMO MM3-MM10 NO TOQUE
        # ==================================================
        # Defina o limite máximo de pontos/ticks tolerável entre as médias.
        # Se as médias estiverem mais afastadas que isso, o pullback foi violento demais.
        AFASTAMENTO_MAX_MEDIAS = 20.0  # Ajuste esse valor conforme o ativo (Ex: 15 pontos)

        afastamento_atual_medias = mm3[i] - mm10[i]

        if afastamento_atual_medias > AFASTAMENTO_MAX_MEDIAS:
            debug_arr[i] = "pullback_muito_violento_medias_afastadas"
            continue
        
        # =========================
        # ANTI-DOJI
        # =========================
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
        # FECHAMENTO FORTE
        # =========================
        distancia_topo = (
            highs[i] - closes[i]
        )

        if distancia_topo > (
            tamanhos_totais[i] * 0.25
        ):

            debug_arr[i] = (
                "fechamento_fraco"
            )

            continue  
          
        # # =========================
        # # FILTRO: CANDLE EXPANSIVO
        # # =========================
        # if (
        #     corpos[i]
        #     <
        #     media_corpos_6_arr[i - 1] * 1.2
        # ):

        #     debug_arr[i] = (
        #         "gatilho_sem_expansao"
        #     )

        #     continue
        
        # if corpos[i] > media_corpos_6_arr[i - 1] * 2.5:
            
        #     debug_arr[i] = (
        #         "gatilho_exagerado"
        #     )

        #     continue
        
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

        # ==================================================
        # FILTRO: ACIONAMENTO E MM3 NO INSTANTE DO ROMPIMENTO
        # ==================================================
        # 1. Trava de segurança para não estourar o fim dos arrays
        if i + 1 >= tamanho:
            continue

        # 2. Verifica se o candle seguinte [i + 1] realmente rompeu a entrada
        if highs[i + 1] >= entrada:
            
            # MATEMÁTICA PURA: Calcula a MM3 exata que estará na tela no milissegundo do rompimento
            # Usamos o preço da nossa entrada projetada + os 2 fechamentos anteriores que já conhecemos
            mm3_no_instante_do_rompimento = (entrada + closes[i] + closes[i - 1]) / 3
            
            mm3_gatilho = mm3[i]
            mm3_anterior = mm3[i - 1]

            # Condição: No instante do clique a mercado, a MM3 precisa estar maior que os 2 candles anteriores
            if not (mm3_no_instante_do_rompimento > mm3_gatilho and mm3_no_instante_do_rompimento > mm3_anterior):
                debug_arr[i] = "mm3_nao_confirmou_no_instante_do_rompimento"
                continue
                
        else:
            # Se o candle seguinte não romper a máxima do gatilho, o sinal é descartado
            debug_arr[i] = "sem_rompimento_no_candle_seguinte"
            continue

        # =========================
        # RISCO
        # =========================
        if risco <= 0:

            debug_arr[i] = (
                "risco_invalido"
            )

            continue

        if risco < 8:

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
        # VALIDAÇÃO DA PERNADA CURTA E FORTE
        # =========================
        # Regra 1: O momentum tem que ser positivo (mercado realmente subiu nos últimos 4 candles)
        if df["momentum_preco"].values[i] <= 0:
            debug_arr[i] = "sem_momentum_de_alta"
            continue
            
        # Regra 2: O volume acumulado dessa pernada curta TEM que ser maior 
        # do que a média dos volumes dos candles que antecederam a pernada.
        volume_pernada = df["volume_acumulado_pernada"].values[i]
        volume_medio_anterior = df["media_volume_antecedente"].values[i] * JANELA_CURTA
        
        if volume_pernada < (volume_medio_anterior * 1.3): # 30% a mais de volume no mínimo
            debug_arr[i] = "pernada_sem_volume_institucional"
            continue
        
        # 3. FILTRO DE FLUXO (A mágica acontece aqui!):
        # Dos 4 candles da pernada, exigimos que pelo menos 2 tenham sido "Candles Fortes"
        if qtd_fortes[i] < 2:
            debug_arr[i] = "pernada_curta_mas_sem_fluxo_agressivo"
            continue
        
        
        # =========================
        # SINAL
        # =========================
        sinal_arr[i] = 1

        setup_arr[i] = (
            "sinais_mm3_mm10_mm50"
        )

        entrada_arr[i] = entrada

        stop_arr[i] = stop

        tp_arr[i] = (
            entrada + (risco * RR)
        )

        lado_arr[i] = "compra"

       

        debug_arr[i] = (
            f"setup_ok | "
            f"risco={round(risco, 2)} | "
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