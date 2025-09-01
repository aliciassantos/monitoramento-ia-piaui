import requests #importa a biblioteca requests para fazer requisições HTTP
import xmltodict
import pandas as pd
lista_dados = [] #Armazena os dados coletados
# Listas de palavras para análise de sentimento
palavras_positivas = ['inovação', 'sucesso', 'crescimento', 'desenvolvimento', 'oportunidade', 'avanços', 'melhoria', 'potencial', 'criação', 'parceria', 'lançamento', 'investimento', 'destaque']
palavras_negativas = ['desafio', 'problema', 'barreira', 'crise', 'risco', 'falha', 'atraso', 'preocupação', 'limitação', 'ameaça', 'prejuízo', 'dificuldade']


query = "Inteligência Artificial Piauí"   #Armazena o tema da pesquisa
google_rss_url = f"https://news.google.com/rss/search?q={query}" #Constrói a URL completa do feed RSS

try: 
    resposta = requests.get(google_rss_url) #Faz a requisição HTTP e armazena a resposta
    resposta.raise_for_status() #Verifica se a requisição foi bem sucedida
    print("Operação bem sucedida!")

    resposta_dicionario = xmltodict.parse(resposta.text) #Converte a resposta XML em um dicionário Python
    noticias = resposta_dicionario['rss']['channel']['item'] #Busca a lista de notícias
    if not isinstance(noticias, list): #Tratamento para evitar erros em loop
        noticias = [noticias]

    print("\nÚltimas notícias encontradas:")
    for article in noticias[:10]: # Limita a 10 notícias para teste
        #Extrai o título, o link e a descrição
        titulo = article.get('title') 
        link = article.get('link')
        descricao = article.get('description')

        lista_dados.append({
            'titulo' : titulo,
            'link' : link,
            'descricao' : descricao
        })
    print(f'Coletadas {len(lista_dados)} notícias.')

    #Salva os dados em um arquivo CSV
    df = pd.DataFrame(lista_dados)
    df.to_csv('noticias_coletadas.csv', index = False)
    print('Dados salvos em noticias_coletadas.csv com sucesso')


except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")
except Exception as e:
    print(f"Ocorreu um erro no processamento do XML: {e}")

try:
    df = pd.read_csv('noticias_coletadas.csv')
    #Função para classificar o sentimento
    def classificar_sentimento(texto): 
        if not isinstance(texto, str):
            return 'Neutro'
        
        texto_limpo = texto.lower() #Converte o texto para minúsculos, facilitando a busca
        pontuacao_positiva = sum(1 for palavra in palavras_positivas if palavra in texto_limpo)
        pontuacao_negativa = sum(1 for palavra in palavras_negativas if palavra in texto_limpo)

        if pontuacao_positiva > pontuacao_negativa:
            return 'Positivo'
        elif pontuacao_negativa > pontuacao_positiva:
            return 'Negativo'
        else:
            return 'Neutro'
        
    df['sentimento'] = df['descricao'].apply(classificar_sentimento) #Aplica a classificação a cada linha do DataFrame
    print("\nDistribuição de sentimentos:")
    print(df['sentimento'].value_counts())

    df.to_csv('noticias_processadas.csv', index = False)
    print("Dados processados e salvos em noticias_processadas.csv.")

except FileNotFoundError:
     print("Erro: O arquivo 'noticias_coletadas.csv' não foi encontrado. Execute a coleta de dados primeiro.")
except Exception as e:
    print(f"Ocorreu um erro na análise de sentimento: {e}")
