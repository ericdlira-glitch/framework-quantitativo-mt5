import pandas as pd
import numpy as np

def grid_search_pesos(df, backtest_portfolio_func):

    resultados = []

    B_values = np.arange(0.5, 2.01, 0.25)
    V_values = np.arange(0.0, 1.01, 0.25)

    for B in B_values:
        for V in V_values:

            risk_map = {
                "C": 1.0,
                "B": round(B, 2),
                "V": round(V, 2),
            }

            resultado = backtest_portfolio_func(df, risk_map=risk_map)

            resultados.append({
                "B": B,
                "V": V,
                "capital_final": resultado["capital_final"],
                "drawdown": resultado["max_drawdown_pct"],
                "trades": resultado["trades"],
                "winrate": resultado["winrate"],
            })

    df_resultados = pd.DataFrame(resultados)

    df_resultados["score"] = (
        df_resultados["capital_final"] /
        (1 + df_resultados["drawdown"])
    )

    return df_resultados.sort_values(by="score", ascending=False)