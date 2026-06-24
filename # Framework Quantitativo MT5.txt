# Framework Quantitativo MT5

# Framework Quantitativo MT5

Projeto desenvolvido em Python para pesquisa, validação e execução automatizada de estratégias quantitativas integradas ao MetaTrader 5.

## Objetivo

O objetivo deste projeto é estudar e aplicar conceitos de:

* Programação em Python
* Análise de dados financeiros
* Automação de processos
* Backtesting de estratégias
* Gestão de risco
* Integração com APIs
* Arquitetura de software

## Principais Funcionalidades

* Coleta de dados via MetaTrader 5
* Processamento de séries temporais com Pandas
* Classificação de contexto e regime de mercado
* Estratégias quantitativas baseadas em médias móveis
* Backtesting com controle de risco
* Controle de Break Even
* Controle de Overtrade
* Position Sizing automático
* Limite diário de perdas
* Otimização de parâmetros via Grid Search
* Execução automatizada de ordens

## Tecnologias Utilizadas

* Python
* Pandas
* NumPy
* MetaTrader5

## Estrutura do Projeto

```text
core/

├── dados_mt5.py       # Coleta de dados
├── contexto.py        # Indicadores e contexto
├── regime_mercado.py  # Classificação de mercado
├── sinais_intraday.py # Estratégias
├── backtest.py        # Motor de backtest
├── portfolio.py       # Gestão de resultados
├── risco.py           # Position sizing
├── risco_diario.py    # Controle de perdas diárias
├── execucao.py        # Tomada de decisão
├── ordens.py          # Execução de ordens
├── otimizacao.py      # Grid Search
└── robo.py            # Orquestrador principal
```

## Fluxo do Sistema

MetaTrader 5

↓

Coleta de Dados

↓

Indicadores e Contexto

↓

Classificação de Mercado

↓

Geração de Sinais

↓

Tomada de Decisão

↓

Gestão de Risco

↓

Execução Automatizada

## Sobre o Desenvolvimento

Este projeto foi desenvolvido como parte do meu processo de aprendizado em Python, análise de dados e automação.

Durante o desenvolvimento foram utilizadas ferramentas de Inteligência Artificial, principalmente ChatGPT, como apoio para estudo, revisão de código, esclarecimento de conceitos e aceleração do desenvolvimento.

As regras de negócio, análise dos resultados, validação dos backtests, definição dos filtros operacionais e evolução das estratégias foram conduzidas de forma iterativa através de estudo, experimentação e testes sucessivos.

O objetivo principal foi desenvolver conhecimento prático em programação, arquitetura de software, integração com APIs, automação e análise de dados.
