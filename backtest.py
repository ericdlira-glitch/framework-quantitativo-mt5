
import pandas as pd


def backtest_portfolio(
    df,
    setup_filtrado=None,
    risco_retorno=2.0,
    risco_pct=0.01,
    capital_inicial=100,
    ordem_execucao="stop_first",
    usar_be=True,
    evitar_overtrade=True,
    cooldown_candles=3
):

    # =========================
    # CONFIG POR SETUP
    # =========================
    CONFIG_SETUPS = {
        "sinais_mm3_mm10_mm50": {
            "rr": 1.5,
            "be_r": 1.0,
            "entrada_tipo": "fechamento"
        },
        
            "sinais_mm3_mm10_mm50_teste": {
            "rr": 1.5,
            "be_r": 1.0,
            "entrada_tipo": "fechamento",}
            
        
    }

    df = df.copy()

    trades = []
    wins = 0
    losses = 0
    breakevens = 0

    capital_R = 0.0
    capital = capital_inicial

    equity = [capital]

    fim_trade_idx = -1

    # =========================
    # LOOP PRINCIPAL
    # =========================
    for i in range(len(df)):

        # -------------------------
        # EVITA OVERTRADE
        # -------------------------
        if evitar_overtrade and i <= fim_trade_idx:
            continue

        # -------------------------
        # SEM SINAL
        # -------------------------
        if df["sinal"].iloc[i] != 1:
            continue

        setup_atual = df["setup_usado"].iloc[i]

        # -------------------------
        # FILTRO SETUP
        # -------------------------
        if setup_filtrado is not None:
            if setup_atual != setup_filtrado:
                continue

        # =========================
        # CONFIG SETUP
        # =========================
        config = CONFIG_SETUPS.get(
            setup_atual,
            {
                "rr": risco_retorno,
                "be_r": False,
                "entrada_tipo": "fechamento"
            }
        )

        rr = config["rr"]
        be_trigger_R = config["be_r"]
        entrada_tipo = config["entrada_tipo"]

        # =========================
        # DADOS DA OPERAÇÃO
        # =========================
        entrada = float(df["preco_entrada"].iloc[i])
        stop_inicial = float(df["stop"].iloc[i])
        lado = df["lado"].iloc[i]

        if pd.isna(entrada) or pd.isna(stop_inicial):
            continue

        long_trade = lado == "compra"

        # =========================
        # RISCO E ALVO
        # =========================
        if long_trade:

            risco = entrada - stop_inicial

            if risco <= 0:
                continue

            alvo = entrada + (risco * rr)

        else:

            risco = stop_inicial - entrada

            if risco <= 0:
                continue

            alvo = entrada - (risco * rr)

        resultado_R = None
        exit_j = None

        stop_atual = stop_inicial

        be_ativo = False

        # =========================
        # TIPO DE ENTRADA
        # =========================
        trade_ativado = (
            entrada_tipo == "fechamento"
        )

        # =========================
        # LOOP EXECUÇÃO
        # =========================
        for j in range(i + 1, len(df)):

            low_j = df["low"].iloc[j]
            high_j = df["high"].iloc[j]

            if pd.isna(low_j) or pd.isna(high_j):
                continue

            # =========================
            # ENTRADA POR ROMPIMENTO
            # =========================
            if not trade_ativado:

                if long_trade:

                    if high_j >= entrada:
                        trade_ativado = True

                    else:
                        continue

                else:

                    if low_j <= entrada:
                        trade_ativado = True

                    else:
                        continue

            # =========================
            # BREAK EVEN
            # =========================
            if usar_be and be_trigger_R is not None and not be_ativo:

                if long_trade:

                    if high_j >= entrada + (risco * be_trigger_R):
                        stop_atual = entrada
                        be_ativo = True

                else:

                    if low_j <= entrada - (risco * be_trigger_R):
                        stop_atual = entrada
                        be_ativo = True

            # =========================
            # SAÍDAS
            # =========================
            if long_trade:

                stop_batido = low_j <= stop_atual
                alvo_batido = high_j >= alvo

                # -------------------------
                # STOP E ALVO NO MESMO CANDLE
                # -------------------------
                if stop_batido and alvo_batido:

                    if ordem_execucao == "stop_first":
                        resultado_R = 0 if be_ativo else -1

                    else:
                        resultado_R = rr

                    exit_j = j
                    break

                # -------------------------
                # STOP
                # -------------------------
                if stop_batido:

                    resultado_R = 0 if be_ativo else -1
                    exit_j = j
                    break

                # -------------------------
                # ALVO
                # -------------------------
                if alvo_batido:

                    resultado_R = rr
                    exit_j = j
                    break

            else:

                stop_batido = high_j >= stop_atual
                alvo_batido = low_j <= alvo

                # -------------------------
                # STOP E ALVO NO MESMO CANDLE
                # -------------------------
                if stop_batido and alvo_batido:

                    if ordem_execucao == "stop_first":
                        resultado_R = 0 if be_ativo else -1

                    else:
                        resultado_R = rr

                    exit_j = j
                    break

                # -------------------------
                # STOP
                # -------------------------
                if stop_batido:

                    resultado_R = 0 if be_ativo else -1
                    exit_j = j
                    break

                # -------------------------
                # ALVO
                # -------------------------
                if alvo_batido:

                    resultado_R = rr
                    exit_j = j
                    break

        # =========================
        # RESULTADO OPERAÇÃO
        # =========================
        if resultado_R is not None:
             
            print("\n📌 TRADE FINALIZADO")

            print("Data:", df.index[i])

            print("Resultado R:", resultado_R)

            print("Setup:", setup_atual)

            print("Entrada:", round(entrada, 2))

            print("Stop:", round(stop_inicial, 2))

            print("Alvo:", round(alvo, 2))

            print("Risco:", round(risco, 2))

            if "dist_mm3_mm10" in df.columns:
                print(
                    "dist_mm3_mm10:",
                    round(df["dist_mm3_mm10"].iloc[i], 2)
                )

            if "dist_preco_mm10" in df.columns:
                print(
                    "dist_preco_mm10:",
                    round(df["dist_preco_mm10"].iloc[i], 2)
                )

            if "mm3" in df.columns:
                print(
                    "MM3:",
                    round(df["mm3"].iloc[i], 2)
                )

            if "mm10" in df.columns:
                print(
                    "MM10:",
                    round(df["mm10"].iloc[i], 2)
                )

            print("-" * 120) 
             
            if resultado_R > 0:
                wins += 1

            elif resultado_R < 0:
                losses += 1

                print("\n❌ LOSS DETECTADO")
                print("Data:", df.index[i])

                print("Setup:", setup_atual)

                print("Entrada:", round(entrada, 2))
                print("Stop:", round(stop_inicial, 2))
                print("Alvo:", round(alvo, 2))

                print("Risco:", round(risco, 2))

                if "mm3" in df.columns:
                    print("MM3:", round(df['mm3'].iloc[i], 2))

                if "mm10" in df.columns:
                    print("MM10:", round(df['mm10'].iloc[i], 2))

            else:
                breakevens += 1

            retorno = resultado_R * risco_pct

            capital *= (1 + retorno)

            capital_R += resultado_R

            trades.append(resultado_R)

            equity.append(capital)

            if evitar_overtrade and exit_j is not None:
                fim_trade_idx = exit_j + cooldown_candles

    # =========================
    # RESULTADOS
    # =========================
    winrate = (
        (pd.Series(trades) > 0).mean() * 100
        if trades else 0
    )

    return {
        "trades": len(trades),
        "winrate": winrate,
        "resultado_final_R": capital_R,
        "capital_final": capital,
        "max_drawdown_pct": 0,
        "wins": wins,
        "losses": losses,
        "breakevens": breakevens,
    }




