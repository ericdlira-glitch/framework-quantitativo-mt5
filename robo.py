import time
import traceback
from sinais_intraday import gerar_sinais_mm3_mm10_mm50_lateral
from datetime import timedelta
from dados_mt5 import conectar_mt5, pegar_candles
from setup_teste import gerar_sinais_mm3_mm10_mm50_lateral_teste
from execucao import tomar_decisao
from ordens import executar_ordem

SIMBOLO = "USTEC"


def rodar_robo():

    print("🚀 Robô iniciado...\n")

    conectar_mt5()

    ultimo_horario_sinal = None

    ultimo_candle_processado = None

    while True:

        try:

            # =========================
            # DADOS
            # =========================
            df = pegar_candles(SIMBOLO)

            if df is None or len(df) < 60:

                print("⚠️ Dados insuficientes...")

                time.sleep(60)

                continue

            # =========================
            # AJUSTE HORÁRIO
            # =========================
            df.index = (
                df.index
                - timedelta(hours=3)
            )

            # =========================
            # IGNORA CANDLE ABERTO
            # =========================
            df = df.iloc[:-1]

            if len(df) < 60:

                print(
                    "⚠️ Poucos dados "
                    "após ajuste..."
                )

                time.sleep(60)

                continue

            # =========================
            # CONTROLE NOVO CANDLE
            # =========================
            candle_atual = (
                df.index[-1]
                .replace(
                    second=0,
                    microsecond=0
                )
            )

            # -------------------------
            # EVITA REPROCESSAMENTO
            # -------------------------
            if (
                candle_atual
                ==
                ultimo_candle_processado
            ):

                time.sleep(5)

                continue

            # 🔥 novo candle
            ultimo_candle_processado = (
                candle_atual
            )

            print(
                f"\n🕒 Novo candle: "
                f"{candle_atual.strftime('%H:%M')}"
            )

            # =========================
            # GERA SINAIS
            # =========================

            # setup congelado
            df = gerar_sinais_mm3_mm10_mm50_lateral(df)

            # setup teste
            df = gerar_sinais_mm3_mm10_mm50_lateral_teste(df)

            # =========================
            # DEBUG
            # =========================
            print(
                df.tail(3)[[
                    "close",
                    "mm3",
                    "mm10",
                    "sinal",
                    "setup_usado",
                    "debug"
                ]]
            )

            # =========================
            # DECISÃO
            # =========================
            decisao = tomar_decisao(df)

            # =========================
            # EXECUÇÃO
            # =========================
            if decisao is not None:

                horario_sinal = df.index[-1]

                if (
                    horario_sinal
                    !=
                    ultimo_horario_sinal
                ):

                    print(
                        f"\n📢 NOVO SINAL: "
                        f"{decisao['setup_usado']}"
                    )

                    print(
                        f"⏰ {horario_sinal}"
                    )

                    print(
                        f"💰 Entrada: "
                        f"{decisao['preco_entrada']}"
                    )

                    print(
                        f"🛑 Stop: "
                        f"{decisao['stop']}"
                    )

                    executar_ordem(
                        SIMBOLO,
                        decisao
                    )

                    ultimo_horario_sinal = (
                        horario_sinal
                    )

                else:

                    print(
                        "⏸️ Sinal já "
                        "executado anteriormente"
                    )

            else:

                print(
                    f"🕒 {candle_atual} | "
                    f"monitorando..."
                )

        except Exception:

            print("\n❌ Erro no robô:")

            traceback.print_exc()

            try:

                print(
                    "\n🔄 Tentando "
                    "reconectar MT5..."
                )

                conectar_mt5()

            except:

                print(
                    "⚠️ Falha ao "
                    "reconectar MT5"
                )

        # =========================
        # LOOP
        # =========================
        time.sleep(30)