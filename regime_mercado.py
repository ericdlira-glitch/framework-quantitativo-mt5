def classificar_regime(df):
    
    df = df.copy()

    df["regime"] = "neutro"

    for i in range(len(df)):

        mm9 = df.loc[i, "mm9"]
        mm21 = df.loc[i, "mm21"]
        mm50 = df.loc[i, "mm50"]

        if mm9 > mm21 and mm21 > mm50:
            df.loc[i, "regime"] = "tendencia"

        elif mm21 > mm50 and mm9 <= mm21:
            df.loc[i, "regime"] = "pullback"

        elif mm21 <= mm50:
            df.loc[i, "regime"] = "fraqueza"

    return df