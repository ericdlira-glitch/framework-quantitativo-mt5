import pandas as pd
from core.backtest import backtest_R_lado


def teste_robustez_rr(df, rr_lista):

    resultados = []

    for rr in rr_lista:

        resultado = backtest_R_lado(
            df,
            risco_retorno=rr
        )

        resultados.append({
            "RR": rr,
            "Trades": resultado["trades"],
            "Winrate": resultado["winrate"],
            "Resultado_R": resultado["resultado_final_R"],
            "Drawdown_R": resultado["max_drawdown_R"],
            "Expectancia": resultado["resultado_final_R"] / resultado["trades"] if resultado["trades"] > 0 else 0
        })

    return pd.DataFrame(resultados)