import MetaTrader5 as mt5
from datetime import datetime

# =========================
# CONFIG
# =========================
MAX_R_DIA = -3  # parar em -3R

# =========================
# ESTADO
# =========================
estado = {
    "data": None,
    "resultado_R": 0
}


# =========================
# RESET DIÁRIO
# =========================
def reset_se_necessario():
    hoje = datetime.now().date()

    if estado["data"] != hoje:
        estado["data"] = hoje
        estado["resultado_R"] = 0


# =========================
# REGISTRAR MANUAL (backup)
# =========================
def registrar_trade(resultado_R):
    reset_se_necessario()
    estado["resultado_R"] += resultado_R


# =========================
# MT5 - ATUALIZAÇÃO REAL
# =========================
def atualizar_resultado_mt5(risco_por_trade):
    reset_se_necessario()

    hoje = datetime.now()
    inicio = datetime(hoje.year, hoje.month, hoje.day)

    deals = mt5.history_deals_get(inicio, hoje)

    if deals is None:
        print("⚠️ Nenhum histórico encontrado")
        return

    lucro_total = 0

    for deal in deals:
        # 🔥 só considerar FECHAMENTO de posição
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            lucro_total += deal.profit

    if risco_por_trade == 0:
        return

    resultado_R = lucro_total / risco_por_trade

    estado["resultado_R"] = resultado_R


# =========================
# VERIFICAR LIMITE
# =========================
def pode_operar():
    reset_se_necessario()

    if estado["resultado_R"] <= MAX_R_DIA:
        print(f"🛑 Limite diário atingido: {estado['resultado_R']:.2f}R")
        return False

    return True