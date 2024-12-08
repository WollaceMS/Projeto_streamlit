#Passos

#importar bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
#criar as funções de carregamento de dados
    #cotações
@st.cache_data #decorator atribui uma nova funcionalidade a função que esta logo abaixo
def carregar_dados(empresas):
    texto_tickers = ' '.join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacao_acao = dados_acao.history(period='1d', start='2010-01-01', end='2024-07-01') #cotação diaria (1d)
    #print(cotacao_acao)
    cotacao_acao =cotacao_acao['Close'] #para retornar um dataframe e não uma serie ([[close]])
    return cotacao_acao

    
@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv('IBOV.csv',sep=';')
    tickers = list(base_tickers['Código'])
    tickers = [item +'.SA' for item in tickers]
    return tickers

acoes = carregar_tickers_acoes()
dados =carregar_dados(acoes)
#print(dados)


#cria a interface do streamlit
st.write(''' 
# App preço de ações
O gráfico apresenta a evolução das cotações ao longo dos anos
''') #ideia do markdown do jupyter

#prepara as visualizações = filtros
st.sidebar.header('Filtros')   #barra lateral

#filtro de ações
lista_acoes = st.sidebar.multiselect('Escolha as ações para visualizar', dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) ==1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica:'Close'}) #macete para mostrar uma ação
    

#filtro de data
data_inicial = dados.index.min().to_pydatetime() #transforma o timestamp em datetime
data_final = dados.index.max().to_pydatetime()
intervalo_datas = st.sidebar.slider('Escolha a data',min_value= data_inicial, max_value=data_final, 
                    value=(data_inicial, data_final), step= timedelta(days=1)) 
#o value torna possivel selecionar um intervalo de datas
#print(intervalo_datas)

dados = dados.loc[intervalo_datas[0]:intervalo_datas[1]]

# cria o grafico
st.line_chart(dados)


texto_performance_ativos = ''

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) ==1:
    dados = dados.rename(columns={'Close':acao_unica}) #revertendo o processo acima que foi usado para criar o grafico (macete)

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)


for i,acao in enumerate(lista_acoes):
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] -1
    performance_ativo = float(performance_ativo)
    #print(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo)
    if performance_ativo > 0:
        # :cor[texto]
        texto_performance_ativos = texto_performance_ativos + f'  \n{acao}: :green[{performance_ativo:.1%}]'
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f'  \n{acao}: :red[{performance_ativo:.1%}]'
    else:
        texto_performance_ativos = texto_performance_ativos + f'  \n{acao}: {performance_ativo:.1%}'

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira -1


if performance_carteira > 0:
    texto_performance_carteira =  f'Performance da carteira com todos os ativos: :green[{performance_carteira:.1%}]'
elif performance_carteira < 0:
    texto_performance_carteira =  f'Performance da carteira com todos os ativos: :red[{performance_carteira:.1%}]'

else:
    texto_performance_carteira = f'Performance da carteira com todos os ativos: {performance_carteira:.1%}'



st.write(f''' 
### Performance dos ativos
Essa foi a performance de cada ativo no periodo selecionado:

{texto_performance_ativos}

{texto_performance_carteira}
''') #ideia do markdown do jupyter