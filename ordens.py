import MetaTrader5 as mt5
from datetime import datetime
from risco_diario import pode_operar, atualizar_resultado_mt5

# =========================
# CONFIG
# =========================
HORARIO_INICIO = 9
HORARIO_FIM = 19

RISCO_POR_TRADE = 0.01
MODO_CONTA = "demo"

# 🔥 CONTROLE DE EXECUÇÃO
MODO_EXECUCAO = "teste"  # "teste" ou "real"

# 🔥 AJUSTADO PARA ÍNDICE (USTEC)
SPREAD_MAX = 150


# =========================
# VALIDAÇÃO DE CONTA
# =========================
def validar_conta(conta):
    if conta is None:
        print("❌ Não foi possível obter dados da conta")
        return False

    print(f"🔎 Conta: {conta.login} | Servidor: {conta.server}")

    if MODO_CONTA == "demo":
        if "demo" not in conta.server.lower():
            print("🚨 BLOQUEADO: Conta NÃO é demo!")
            return False

    return True


# =========================
# FILTRO DE HORÁRIO
# =========================
def dentro_do_horario():
    agora = datetime.now()
    return HORARIO_INICIO <= agora.hour < HORARIO_FIM


# =========================
# EVITAR MÚLTIPLAS POSIÇÕES
# =========================
def tem_posicao_aberta(simbolo):
    posicoes = mt5.positions_get(symbol=simbolo)
    return posicoes is not None and len(posicoes) > 0


# =========================
# CÁLCULO DE LOTE
# =========================
def calcular_lote(simbolo, saldo, risco_pct, entrada, stop):
    info = mt5.symbol_info(simbolo)

    if info is None:
        print("❌ Erro ao obter symbol_info")
        return 0.0

    risco_dinheiro = saldo * risco_pct
    distancia = abs(entrada - stop)

    if distancia == 0:
        return 0.0

    tick_value = info.trade_tick_value
    tick_size = info.trade_tick_size

    if tick_size == 0:
        print("❌ tick_size inválido")
        return 0.0

    valor_por_ponto = tick_value / tick_size

    lote = risco_dinheiro / (distancia * valor_por_ponto)

    lote = max(info.volume_min, lote)
    lote = min(info.volume_max, lote)

    return round(lote, 2)


# =========================
# EXECUÇÃO
# =========================
def executar_ordem(simbolo, decisao):

    # =========================
    # MT5 CHECK
    # =========================
    if not mt5.initialize():
        print("❌ MT5 não inicializado")
        return

    info = mt5.symbol_info(simbolo)

    if info is None:
        print(f"❌ Símbolo {simbolo} não encontrado")
        return

    if not info.visible:
        mt5.symbol_select(simbolo, True)

    # =========================
    # VALIDAÇÕES
    # =========================
    if decisao is None:
        print("⏸️ Nenhuma ordem enviada")
        return

    # 🔥 FILTRO DE HORÁRIO (SÓ NO REAL)
    if MODO_EXECUCAO == "real":
        if not dentro_do_horario():
            print("⏸️ Fora do horário operacional")
            return

    if tem_posicao_aberta(simbolo):
        print("⏸️ Já existe posição aberta")
        return

    entrada = decisao["preco_entrada"]
    stop = decisao["stop"]
    lado = decisao["lado"]
    setup = decisao.get("setup_usado", "desconhecido")

    risco = abs(entrada - stop)

    if risco == 0:
        print("❌ Risco inválido")
        return

    # =========================
    # CONTA
    # =========================
    conta = mt5.account_info()
    if conta is None:
        print("❌ Erro ao obter conta")
        return

    if not validar_conta(conta):
        return

    saldo = conta.balance
    risco_dinheiro = saldo * RISCO_POR_TRADE

    atualizar_resultado_mt5(risco_dinheiro)

    if not pode_operar():
        print("⏸️ Robô pausado por risco diário")
        return

    # =========================
    # PREÇO / SPREAD
    # =========================
    tick = mt5.symbol_info_tick(simbolo)
    if tick is None:
        print("❌ Erro ao obter preço")
        return

    spread_pontos = (tick.ask - tick.bid) / info.point
    print(f"📊 Spread atual: {spread_pontos}")

    if spread_pontos > SPREAD_MAX:
        print(f"⏸️ Spread alto: {spread_pontos}")
        return

    # =========================
    # DIREÇÃO
    # =========================
    if lado == "compra":
        tipo = mt5.ORDER_TYPE_BUY
        preco = tick.ask
        tp = decisao.get("tp", entrada + (risco * 1.5))

    elif lado == "venda":
        tipo = mt5.ORDER_TYPE_SELL
        preco = tick.bid
        tp = decisao.get("tp", entrada - (risco * 1.5))

    else:
        print("❌ Lado inválido")
        return

    # =========================
    # EVITA ENTRADA ATRASADA
    # =========================
    if abs(preco - entrada) > (20 * info.point):
        print("⏸️ Preço já andou muito (slippage)")
        return

    # =========================
    # NORMALIZAÇÃO
    # =========================
    digits = info.digits
    stop = round(stop, digits)
    tp = round(tp, digits)

    # =========================
    # PROTEÇÃO EXTRA
    # =========================
    if abs(preco - stop) < (10 * info.point):
        print("⏸️ Stop muito curto")
        return

    # =========================
    # LOTE
    # =========================
    lote = calcular_lote(simbolo, saldo, RISCO_POR_TRADE, entrada, stop)

    if lote < info.volume_min or lote <= 0:
        print("⏸️ Lote inválido")
        return

    # =========================
    # LOG
    # =========================
    print(f"""
📊 NOVA ORDEM
Ativo: {simbolo}
Setup: {setup}
Lado: {lado}
Entrada: {preco}
Stop: {stop}
TP: {tp}
Lote: {lote}
Spread: {spread_pontos}
Saldo: {saldo}
""")

    # =========================
    # ORDEM
    # =========================
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": simbolo,
        "volume": lote,
        "type": tipo,
        "price": preco,
        "sl": stop,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "robo_intraday",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result is None:
        print("❌ Falha ao enviar ordem")
        return

    # =========================
    # RESULTADO
    # =========================
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Erro ao executar ordem: {result.retcode}")
        print(result)
    else:
        print(f"""
✅ TRADE EXECUTADO
Ativo: {simbolo}
Setup: {setup}
Lado: {lado}
Entrada: {preco}
Stop: {stop}
TP: {tp}
Lote: {lote}
Spread: {spread_pontos}
Saldo: {saldo}
Ticket: {result.order}
Hora: {datetime.now()}
""")