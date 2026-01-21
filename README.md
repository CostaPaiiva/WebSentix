FabricaDeModelosML

Plataforma AutoML em Python que treina, avalia, versiona e compara modelos de Machine Learning automaticamente através de uma interface web.

🚀 Visão Geral

O FabricaDeModelosML é uma aplicação que automatiza todo o processo de Machine Learning:

📥 Upload de dataset (CSV)

🧠 Detecção automática do tipo de problema:

Classificação ou Regressão

🧹 Pré-processamento automático dos dados

🤖 Treinamento de vários modelos automaticamente

🏆 Seleção do melhor modelo com base na métrica

📊 Geração de ranking visual dos modelos

🗂️ Versionamento automático de treinos (v1, v2, v3, ...)

📄 Geração de relatório em PDF

📈 Dashboard web para visualizar resultados

📦 Estrutura pronta para virar produto real

🖥️ Interface Web

A aplicação possui:

Página inicial para upload do dataset

Dashboard por projeto

Histórico de versões de treino

Ranking dos modelos

Download do relatório em PDF

Estrutura pronta para:

Comparação entre versões

Evolução para MLOps

🧠 O que o sistema faz automaticamente?

✔️ Detecta se o problema é classificação ou regressão
✔️ Limpa e prepara os dados
✔️ Treina múltiplos modelos
✔️ Avalia todos
✔️ Escolhe o melhor
✔️ Gera gráfico de ranking
✔️ Salva tudo em versão (v1, v2, v3...)
✔️ Gera relatório PDF
✔️ Exibe tudo no dashboard

FabricadeModelosML/
│
├── app.py                # Servidor Flask (rotas e páginas)
├── run_app.py            # Inicializador da aplicação
├── automl_engine.py      # Coração do AutoML (treino, avaliação, ranking)
├── predictor.py         # Futuro módulo de inferência/predição
├── versionador.py       # Sistema de versionamento dos modelos
├── pdf_report.py        # Gerador de relatório PDF
├── requirements.txt     # Dependências
│
├── utils/                # Funções auxiliares
│
├── static/               # CSS e assets
├── templates/            # HTML (Flask)
│
├── uploads/              # Onde os CSVs são enviados
│
├── projects/             # Onde ficam os projetos treinados
│   └── nome_do_projeto/
│       ├── dataset.csv
│       ├── relatorio.pdf
│       └── treinos/
│           ├── v1/
│           ├── v2/
│           ├── v3/
│           └── ...
│
└── venv/                 # Ambiente virtual (não subir pro Git)

🗂️ Sistema de Versionamento de Modelos

Cada vez que você treina novamente um projeto:
projects/meu_projeto/treinos/
├── v1/
├── v2/
├── v3/

Cada versão guarda:

Modelo treinado

Métricas

Ranking

Gráficos

Dados do treino

Isso permite:

📜 Histórico completo

🔁 Comparar evoluções

🧪 Reproduzir experimentos

🏗️ Base para MLOps real

📊 Modelos Usados Atualmente
Classificação:

Logistic Regression

Random Forest

KNN

Naive Bayes

SVM

Regressão:

Linear Regression

Random Forest Regressor

KNN Regressor

Decision Tree Regressor

(O sistema escolhe automaticamente quais usar)

📈 Métricas
Classificação:

Accuracy

Regressão:

R² Score

📄 Relatório PDF

O sistema gera automaticamente:

Resumo do dataset

Tipo do problema

Melhor modelo

Score

Ranking dos modelos

Gráfico

E salva em:

projects/nome_do_projeto/relatorio.pdf