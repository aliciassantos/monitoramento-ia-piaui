1. Escolha da Abordagem de Análise de Sentimento
Eu optei por uma abordagem de análise de sentimento baseada em regras, em vez de um modelo de Machine Learning (ML), por duas razões principais:

* Escopo e Prazo do Projeto: A abordagem de regras é mais rápida de implementar e permite focar na construção do pipeline completo (coleta → processamento → dashboard) dentro do prazo do teste. Um modelo de ML exigiria um conjunto de dados rotulado para treinamento, o que não estava disponível e consumiria um tempo significativo.

* Limitações do Método: A abordagem de regras, apesar de ser mais simples, me permitiu focar na lógica de programação e na manipulação de DataFrames. Eu compreendo que essa análise de sentimento é limitada e pode não capturar sarcasmo ou contextos complexos, uma limitação que adicionei como aviso no rodapé do dashboard. Eu também observei que o tom majoritariamente neutro das notícias de IA no Piauí limitou a quantidade de notícias classificadas como positivas ou negativas, o que é uma limitação inerente aos dados.

2. Tratamento de Erros e Dados Ausentes
O projeto foi desenvolvido para ser robusto e lidar com possíveis falhas na coleta de dados. As seguintes decisões foram tomadas para garantir a estabilidade do dashboard:

Requisições (Requests): O código usa blocos try...except para lidar com erros de conexão de internet e outros problemas durante a requisição do feed RSS.

Dados Incompletos: O código inclui uma verificação (if not isinstance(noticias, list)) para lidar com casos em que o feed RSS retorna apenas uma única notícia, em vez de uma lista. Isso evita erros de loop e garante que o script funcione corretamente.

Falta de Notícias: Para evitar que o dashboard fique em branco, o código verifica se o DataFrame de notícias está vazio (if df.empty). Se a pesquisa não encontrar nenhuma notícia, uma mensagem de aviso é exibida em vez de um erro. Isso demonstra que a aplicação foi projetada para lidar com a falta de dados.

Limpeza de Dados: A limpeza de texto foi aprimorada com o uso de expressões regulares para remover não apenas as tags HTML, mas também caracteres especiais, garantindo que a nuvem de palavras seja mais relevante e livre de ruídos, o que é um ponto importante para a qualidade da análise.