import time
from dados import carregar_dados
from contexto import contexto_diario
from execucao import tomar_decisao


def loop_tempo_real():
    print("🚀 Iniciando monitoramento em tempo real...\n")

    while True:
        try:
            # 1. Carregar dados atualizados
            df = carregar_dados(modo='mt5')

            # 2. Atualizar contexto
            df = contexto_diario(df)

           
            # 4. Pegar último candle
            ultimo = df.iloc[-1]

            # 5. Decisão
            entrada = tomar_decisao(df)

            if entrada:
                print(f"📢 SINAL DETECTADO: {entrada}")
                print(f"⏰ Horário: {ultimo.name}")
                print("-" * 40)

            else:
                print("...monitorando")

        except Exception as e:
            print(f"Erro no loop: {e}")

        # 6. Espera (ajustável)
        time.sleep(60)  # 1 minuto


if __name__ == "__main__":
    loop_tempo_real()