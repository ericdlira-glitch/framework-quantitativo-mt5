from backtest import backtest_portfolio
import pandas as pd

def testar_multiplos_periodos(df, janela=3000, passo=1000, setup_filtrado=None):

    resultados = []

    for inicio in range(0, len(df) - janela, passo):
        fim = inicio + janela
        df_slice = df.iloc[inicio:fim].reset_index(drop=True)

        res = backtest_portfolio(df_slice, setup_filtrado=setup_filtrado)

        if res["trades"] == 0:
            continue

        resultados.append({
            "inicio": inicio,
            "fim": fim,
            "trades": res["trades"],
            "winrate": res["winrate"],
            "resultado_R": res["resultado_final_R"],
        })

    return pd.DataFrame(resultados)