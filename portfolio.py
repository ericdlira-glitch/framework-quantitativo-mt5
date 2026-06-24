import numpy as np
import pandas as pd


def combinar_setups(df, prioridade=("C", "B", "V")):
    df = df.copy()

    # Dicionário para guardar as condições de ativação de cada setup
    condicoes_setups = {}

    for s in prioridade:
        sinal_col = f"sinal_{s}"
        if sinal_col not in df.columns:
            continue

        # 1. Filtro de Regime
        if s in ("C", "B"):
            cond = (df[sinal_col] == 1) & (df["regime"] == "tendencia")
        elif s == "V":
            cond = (df[sinal_col] == 1) & (
                df["regime"].isin(["pullback", "fraqueza"])
            )
        else:
            cond = df[sinal_col] == 1

        # 2. Filtro exclusivo do C
        if s == "C":
            cond = cond & (
                (df["range"] >= df["range20"])
                & df["range"].notna()
                & df["range20"].notna()
            )

        condicoes_setups[s] = cond

    # Se nenhum setup válido foi encontrado nas colunas, retorna o df original
    if not condicoes_setups:
        return df

    # Listas na ordem exata da tupla de 'prioridade'
    lista_condicoes = [condicoes_setups[s] for s in prioridade]

    # 3. Execução Vetorizada usando np.select
    # O np.select avalia as condições na ordem da lista. A primeira que for True ganha.
    df["setup_usado"] = np.select(
        lista_condicoes, prioridade, default=None
    )
    df["sinal"] = np.select(
        lista_condicoes, [1] * len(prioridade), default=0
    )

    # Preenche preços de entrada e stop com base no setup que ganhou
    df["preco_entrada"] = np.select(
        lista_condicoes,
        [df[f"preco_entrada_{s}"] for s in prioridade],
        default=np.nan,
    )
    df["stop"] = np.select(
        lista_condicoes,
        [df[f"stop_{s}"] for s in prioridade],
        default=np.nan,
    )

    # Define o lado (V é short, o resto é long)
    lados = ["short" if s == "V" else "long" for s in prioridade]
    df["lado"] = np.select(lista_condicoes, lados, default=None)

    return df