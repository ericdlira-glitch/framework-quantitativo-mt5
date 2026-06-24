import MetaTrader5 as mt5

def calcular_lote(symbol, saldo, risco_pct, entrada, stop):
    
    symbol_info = mt5.symbol_info(symbol)
    
    if symbol_info is None:
        print("Erro ao obter informações do símbolo")
        return 0.0
    
    # risco em dinheiro
    risco_dinheiro = saldo * risco_pct
    
    # distância do stop
    distancia = abs(entrada - stop)
    
    if distancia == 0:
        return 0.0
    
    # valor por ponto
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    
    valor_por_ponto = tick_value / tick_size
    
    # cálculo do lote
    lote = risco_dinheiro / (distancia * valor_por_ponto)
    
    # arredondar para o mínimo permitido
    lote = max(symbol_info.volume_min, lote)
    
    return round(lote, 2)