import requests 
import xmltodict
import pandas as pd
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import re
from datetime import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator

st.set_page_config(layout = "wide") #Faz o dashboard ocupar toda a tela

#Tenta criar o analisador de sentimentos
try:
    analisador = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download('vader_lexicon')
    analisador = SentimentIntensityAnalyzer()

#Cria um tradutor de português para inglês e um de inglês para português
tradutorP_ingles = GoogleTranslator(source='pt', target='en')
tradutorP_portugues = GoogleTranslator(source='en', target='pt')

#Função de coleta de dados
def coletar_e_processar_noticias():
    st.title("Monitoramento de Percepção Pública sobre IA no Piauí")
    #st.info("Coletando as notícias mais recentes")
    barra_progresso = st.progress(0, text = 'Coletando as notícias mais recentes...')

    #Constrói a URL completa do feed RSS do Google Notícias
    query = "Inteligência Artificial no Piauí"   
    google_rss_url = f"https://news.google.com/rss/search?q={query}" 

    lista_dados = [] 

    try: 
        #Faz a requisição HTTP e armazena a resposta
        resposta = requests.get(google_rss_url) 
        resposta.raise_for_status()        
        resposta_dicionario = xmltodict.parse(resposta.text) #Converte a resposta XML em um dicionário Python
        noticias = resposta_dicionario['rss']['channel']['item'] #Busca a lista de notícias

        if not isinstance(noticias, list): #Tratamento para evitar erros em loop
            noticias = [noticias]

        for noticia in noticias[:10]: 
            #Extrai o título, o linl, a descrição e a data
            descricao_crua = (noticia.get('description', ''))
            descricao_limpa = re.sub(r'<[^>]+>|&nbsp;|\s+', ' ', descricao_crua).strip()
            data_publicacao = noticia.get('pubDate')
            try: 
                data_publicacao_formatada = datetime.strptime(data_publicacao, '%a, %d %b %Y %H:%M:%S %Z')
            except (ValueError, TypeError):
                data_publicacao_formatada = None
            
            #Traduz o título e a descrição
            titulo_traduzido = tradutorP_portugues.translate(noticia.get('title'))
            descricao_traduzida = tradutorP_portugues.translate(descricao_limpa)

            lista_dados.append({
                'titulo' : titulo_traduzido,
                'link' : noticia.get('link'),
                'data' : data_publicacao_formatada,
                'descricao_limpa' : descricao_limpa,
                'descricao_traduzida' : descricao_traduzida
            })

            #Atualiza a barra
            porcentagem_completada = (noticias.index(noticia) + 1)/len(noticias)
            barra_progresso.progress(porcentagem_completada, text=f'Analisando notícia {noticias.index(noticia) + 1} de {len(noticias)}')

        barra_progresso.empty()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        st.stop()
    except Exception as e:
        print(f"Ocorreu um erro no processamento do XML: {e}")
        st.stop()

    #Transforma a lista de notícias em uma tabela
    data_frame = pd.DataFrame(lista_dados)
    
    #Salva o data_frame em um arquivo csv
    if not data_frame.empty:
        data_frame.to_csv("noticias_processadas.csv", index=False)

    return data_frame

#Função auxiliar para analisar cada notícia
def analisar_sentimento(texto): 
    if not isinstance(texto, str):
        return 'Neutro'
    
    #Traduz a descrição para inglês para a análise de sentimento
    texto_ingles = tradutorP_ingles.translate(texto)
    #Analisa o sentimento
    scores = analisador.polarity_scores(texto_ingles)
    #Pontua o sentimento de -1 (muito negativo) a 1 (muito positivo)
    pontuacao_sentimento = scores['compound']

    if pontuacao_sentimento >= 0.05:
        return 'Positivo'
    elif pontuacao_sentimento <= -0.05:
        return 'Negativo'
    else:
        return 'Neutro'

#Função de processamento dos dados coletados  
def processar_dashboard():
    #Tenta ler o arquivo das notícias processadas
    try:
        df = pd.read_csv("noticias_processadas.csv")
    except:
        return pd.DataFrame()
    
    #Cria uma barra de progresso
    mensagem_progresso = 'Analisando as notícias do Piauí. Por favor, aguarde...'
    barra_progresso = st.progress(0, text = mensagem_progresso)

    for i, row in df.iterrows():
        df.at[i, 'sentimento'] = analisar_sentimento(row['descricao_limpa'])
   
        #Atualiza a barra
        porcentagem_completada = (i+1)/len(df)
        barra_progresso.progress(porcentagem_completada, text=f'Analisando notícia {i+1} de {len(df)}')

    barra_progresso.empty()
    #Salva o arquivo CSV
    df.to_csv("noticias_processadas.csv", index=False)
    return df

#Função e exibição do resultado da coleta e análise
def exibir_resultado(dataframe_exibir):
    #---Cria um gráfico com a distribuição dos sentimentos--- 
    st.subheader("Distribuição de sentimentos")
    contagem_sentimentos = dataframe_exibir['sentimento'].value_counts()
    grafico_torta = px.pie(contagem_sentimentos, values = contagem_sentimentos.values, names = contagem_sentimentos.index, title = "Distribuição de sentimentos das notícias", color_discrete_sequence = px.colors.qualitative.Pastel)
    st.plotly_chart(grafico_torta, width = 'stretch')

    #---Tabela iterativa---
    st.subheader("Dados Coletados e Classificados")
    st.dataframe(dataframe_exibir)

    #---Nuvem de palavras---
    stop_words = {'a', 'o', 'de', 'da', 'do','dos', 'das', 'que', 'em', 'para', 'com', 'um', 'uma', 'os', 'as', 'sem', 'e', 'na'}

    st.subheader("Nuvem de Palavras")
    texto_completo = ' '.join(dataframe_exibir['descricao_traduzida'].dropna())

    if texto_completo.strip():  
        try:
            wordcloud = WordCloud(width = 800, height = 400, background_color = 'white', stopwords = stop_words).generate(texto_completo)
            st.image(wordcloud.to_array(), caption = 'Nuvem de palavras com os termos mais frequentes', width = 'stretch')
        except:
            st.warning("As notícias deste período contêm apenas palavras comuns (stop words).")
    else:
        st.warning("Não há texto suficiente para gerar a nuvem de palavras nesse período.")

    #---Aviso de ética e transparência---
    st.markdown('---')
    st.markdown('Aviso de limitação de análise')
    st.markdown('Esta análise de sentimento é baseada em regras simples e pode não capturar sarcasmo ou contextos complexos.')


#---Estrutura do dashboard---
df_novo = coletar_e_processar_noticias()

#Carrega o que existe no arquivo CSV
try:
    df_antigo = pd.read_csv("noticias_processadas.csv")
except:
    df_antigo = pd.DataFrame()

if not df_novo.empty:
    #Processa as novas notícias
    df_novo = processar_dashboard()
    #Junta as novas notícias com as antigas
    data_frame = pd.concat([df_novo, df_antigo], ignore_index=True)
else:
    #Se não há noticias novas, mantém as antigas
    data_frame = df_antigo

if not data_frame.empty:
    #Elimina notícias duplicadas
    data_frame = data_frame.drop_duplicates(subset=['link'], keep='first')
    #Salva o arquivo
    data_frame.to_csv("noticias_processadas.csv", index=False)
  

#---Verifica se a pesquisa funcionou---
else:
    st.warning("A pesquisa não encontrou nenhuma notícia recente. Tente novamente mais tarde")
    st.stop()

st.success(f'Coletadas {len(data_frame)} notícias sobre IA no Piauí')

#---Filtro de Data---
st.sidebar.subheader("Filtro por Data")
data_frame['data'] = pd.to_datetime(data_frame['data'])
min_data = data_frame['data'].min().date()
max_data = data_frame['data'].max().date()

dataframe_filtrado = data_frame

with st.sidebar.form("filtro_datas"):
    st.write('Configurar Período')    
    #Coleta a data de inicio e fim
    periodo = st.date_input(
        "Data de início",
        value = [min_data, max_data],
        min_value = min_data,
        max_value = max_data,
        format = "DD/MM/YYYY"
    )

    #Botão de filtro
    if st.form_submit_button("Filtrar Notícias"):
        #Permite a filtragem se houver data de início e de fim
        if len(periodo) == 2:
            start_date, end_date = periodo

            dataframe_filtrado = data_frame[(data_frame['data'].dt.date >= start_date) & (data_frame['data'].dt.date <= end_date)]
            st.subheader(f"Resultados de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
        else:
            st.info("Por favor, selecione a data de início e a data de fim no calendário")
            st.stop()

#Mostra o resultado da análise
exibir_resultado(dataframe_exibir = dataframe_filtrado)
