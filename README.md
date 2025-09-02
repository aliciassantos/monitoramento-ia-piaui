# monitoramento-ia-piaui
Case técnico para monitoramento da percepção pública sobre IA no Piauí

Este projeto é um dashboard interativo desenvolvido para o case técnico da Secretaria de Inteligência Artificial do Piauí. O objetivo é coletar e monitorar menções sobre "Inteligência Artificial no Piauí" em fontes de notícias, com foco em análise de sentimento e identificação de temas recorrentes.

O dashboard oferece as seguintes funcionalidades:

* Coleta de Dados: Coleta notícias recentes usando o feed RSS do Google   Notícias.

* Análise de Sentimento: Classifica o sentimento de cada notícia (positivo, negativo ou neutro) usando uma abordagem baseada em regras.

* Visualização Interativa: Exibe um painel completo com um gráfico de pizza, uma nuvem de palavras e uma tabela interativa.

* Filtro por Data: Permite filtrar os dados por um período de tempo específico.


Pré-requisitos:
Certifique-se de que você tem o Python e o Git instalados na sua máquina.

Como Rodar o Projeto:
Siga os passos abaixo para executar o dashboard em ambiente local.

1. Clone o repositório
Abra o seu terminal e clone o repositório do GitHub para o seu computador.

        git clone /aliciassantos/monitoramento-ia-piaui
        cd monitoramento-ia-piaui

2. Crie e ative o ambiente virtual
É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

        python -m venv .venv
        source .venv/Scripts/activate

3. Instale as bibliotecas necessárias
Instale todas as bibliotecas listadas no arquivo requirements.txt.

        pip install -r requirements.txt

4. Execute o dashboard
Com o ambiente virtual ativado, rode o comando Streamlit para iniciar o aplicativo no seu navegador.

        streamlit run app.py

O dashboard será aberto automaticamente no seu navegador padrão.