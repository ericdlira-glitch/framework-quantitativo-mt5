def tomar_decisao(df):
    
    # =========================
    # PROTEÇÃO
    # =========================
    if df is None or len(df) < 60:
        return None

    i = len(df) - 1
    row = df.iloc[i]

    if i < 5:
        return None

    # =========================
    # 🔥 REGRA MAIS IMPORTANTE
    # =========================
    # Só aceita sinal do candle atual
    if row["sinal"] != 1:
        return None

    setup = row["setup_usado"]

    # =========================
    # CONTEXTO (TENDÊNCIA)
    # =========================
    mm50 = df["mm50"]

    slope = mm50.iloc[i] - mm50.iloc[i - 5]
    preco = row["close"]

    tendencia_forte = abs(slope) > (0.0008 * preco)

    # =========================
    # VALIDAÇÃO POR SETUP
    # =========================

    # 1️⃣ Pullback (tendência)
    if setup == "pullback_mm50":
        if not tendencia_forte:
            return None

        # preço ainda próximo da mm50 (evita atraso)
        distancia = abs(preco - mm50.iloc[i])
        if distancia > (0.01 * preco):
            return None

        return row

    # 2️⃣ Lateral
    elif setup == "C_LATERAL_DOJI":
        if tendencia_forte:
            return None
        return row

    # 3️⃣ Reversão
    elif setup == "V_REV_MM9":
        return row

    return None