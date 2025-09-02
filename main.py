import requests 
import xmltodict
import pandas as pd
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import re
from datetime import datetime, timedelta

st.set_page_config(layout = "wide") #Faz o dashboard ocupar toda a tela

#Função de coleta e análise de dados
def coletar_e_processar_noticias():
    st.title("Monitoramento de Percepção Pública sobre IA no Piauí")
    st.info("Coletando as notícias mais recentes")

    # Listas de palavras para análise de sentimento
    palavras_positivas = ['inovação', 'sucesso', 'crescimento', 'desenvolvimento', 'oportunidade', 'avanços', 'melhoria', 'potencial', 'criação', 'parceria', 'lançamento', 'investimento', 'destaque', 'progresso', 'benefício', 'excelência', 'expansão', 'fortalecimento', 'reforço', 'superação', 'otimização', 'reestruturação', 'melhora', 'êxito', 'solução']
    palavras_negativas = ['dúvida', 'fracasso', 'obstáculo', 'incerteza', 'declínio', 'instabilidade', 'conflito', 'inadequado', 'insatisfação', 'restrição', 'desvantagem', 'incompetência', 'problema', 'barreira', 'crise', 'risco', 'falha', 'atraso', 'preocupação', 'limitação', 'ameaça', 'prejuízo', 'dificuldade']
    
    #Constrói a URL completa do feed RSS do Google Notícias
    query = "Inteligência Artificial Piauí"   
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

            lista_dados.append({
                'titulo' : noticia.get('title'),
                'link' : noticia.get('link'),
                'data' : data_publicacao_formatada,
                'descricao_limpa' : descricao_limpa
            })

        #Salva os dados em um arquivo CSV
        data_frame = pd.DataFrame(lista_dados)

        def classificar_sentimento(texto): 
            if not isinstance(texto, str):
                return 'Neutro'
            
            texto_limpo = texto.lower() #Converte o texto para minúsculos, facilitando a busca
            #Contabiliza os sentimentos
            pontuacao_positiva = sum(1 for palavra in palavras_positivas if palavra in texto_limpo)
            pontuacao_negativa = sum(1 for palavra in palavras_negativas if palavra in texto_limpo)

            if pontuacao_positiva > pontuacao_negativa:
                return 'Positivo'
            elif pontuacao_negativa > pontuacao_positiva:
                return 'Negativo'
            else:
                return 'Neutro'
            
        data_frame['sentimento'] = data_frame['descricao_limpa'].apply(classificar_sentimento) #Aplica a classificação a cada linha do DataFrame
        return data_frame
    
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        st.stop()
    except Exception as e:
        print(f"Ocorreu um erro no processamento do XML: {e}")
        st.stop()

    return data_frame

#Estrutura do dashboard
data_frame = coletar_e_processar_noticias()

#Verifica se a pesquisa funcionou
if data_frame.empty:
    st.warning("A pesquisa não encontrou nenhuma notícia recente. Tente novamente mais tarde")
    st.stop()

st.success(f'Coletadas {len(data_frame)} notícias sobre IA no Piauí')

#Filtro de Data
st.sidebar.subheader("Filtro por Data")
data_frame['data'] = pd.to_datetime(data_frame['data'])
min_data = data_frame['data'].min().date()
max_data = data_frame['data'].max().date()
start_date, end_date = st.sidebar.date_input("Selecione o período", value=[min_data, max_data], min_value=min_data, max_value=max_data)

dataframe_filtrado = data_frame[(data_frame['data'].dt.date >= start_date) & (data_frame['data'].dt.date <= end_date)]
st.subheader(f"Resultados de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")

#Cria um gráfico com a distribuição dos sentimentos 
st.subheader("Distribuição de sentimentos")
contagem_sentimentos = dataframe_filtrado['sentimento'].value_counts()
grafico_torta = px.pie(contagem_sentimentos, values = contagem_sentimentos.values, names = contagem_sentimentos.index, title = "Distribuição de sentimentos das notícias", color_discrete_sequence = px.colors.qualitative.Pastel)
st.plotly_chart(grafico_torta, use_container_width = True)

#Tabela iterativa
st.subheader("Dados Coletados e Classificados")
st.dataframe(dataframe_filtrado)

#Nuvem de palavras
st.subheader("Nuvem de Palavras")
texto_completo = ' '.join(dataframe_filtrado['descricao_limpa'].dropna())
wordcloud = WordCloud(width = 800, height = 400, background_color = 'white').generate(texto_completo)
st.image(wordcloud.to_array(), caption = 'Nuvem de palavras com os termos mais frequentes', use_container_width = True)

#Aviso de ética e transparência
st.markdown('---')
st.markdown('Aviso de limitação de análise')
st.markdown('Esta análise de sentimento é baseada em regras simples e pode não capturar sarcasmo ou contextos complexos.')