🏭 Fábrica de Modelos ML (FabricaDeModelosML)

Plataforma AutoML local para criação, versionamento, comparação e gerenciamento de modelos de Machine Learning com interface web.

🚀 Visão Geral

O FabricaDeModelosML é uma plataforma desenvolvida em Python + Flask que permite:

📁 Enviar um dataset CSV

🤖 Detectar automaticamente o tipo de problema (Regressão ou Classificação)

🧠 Treinar vários modelos automaticamente (AutoML)

🏆 Gerar ranking dos modelos

📊 Criar gráficos de comparação

🗂️ Versionar cada treino (v1, v2, v3, ...)

📄 Gerar relatório PDF automático

🌐 Visualizar tudo em um dashboard web

📦 Preparar o projeto para uso real em produção ou como produto

🖥️ Interface

🎨 Tema escuro (preto + roxo)

🚀 Dashboard de projetos

📊 Ranking visual de modelos

📈 Gráficos de comparação

📁 Histórico de treinos

📄 Download de relatório em PDF

FabricadeModelosML/
│
├── app.py                 # Servidor Flask (interface web)
├── automl_engine.py       # Motor AutoML (treino, ranking, gráficos)
├── versionador.py         # Sistema de versionamento de modelos
├── pdf_report.py          # Gerador de relatório em PDF
├── predictor.py           # Carregar e usar modelos treinados
├── requirements.txt       # Dependências do projeto
│
├── static/                # CSS, imagens e assets do frontend
├── templates/             # HTML do sistema
│
├── uploads/               # Onde os CSVs são enviados
│
├── projects/              # Projetos treinados
│   └── nome_do_projeto/
│       ├── dataset.csv
│       ├── relatorio.pdf
│       └── treinos/
│           ├── v1/
│           │   ├── modelo.pkl
│           │   ├── resultado.txt
│           │   └── ranking.png
│           ├── v2/
│           └── v3/
│
└── venv/                  # Ambiente virtual Python

⚙️ Instalação
1️⃣ Clonar o projeto
git clone https://github.com/SEU_USUARIO/FabricadeModelosML.git
cd FabricadeModelosML

2️⃣ Criar ambiente virtual
python -m venv venv

3️⃣ Ativar o ambiente

Windows:

venv\Scripts\activate


Linux/Mac:

source venv/bin/activate

4️⃣ Instalar dependências
pip install -r requirements.txt

▶️ Como Executar
python app.py


Depois acesse no navegador:

http://127.0.0.1:5000

📊 Como Usar

Acesse a página inicial

Envie um arquivo CSV

O sistema:

Detecta o tipo de problema

Treina vários modelos

Cria ranking

Salva versão automaticamente

Gera gráfico e PDF

Você é redirecionado para o dashboard do projeto

🧠 Sistema de Versionamento

Cada novo treino cria automaticamente:

projects/nome_do_projeto/treinos/v1
projects/nome_do_projeto/treinos/v2
projects/nome_do_projeto/treinos/v3
...


Cada versão contém:

✅ modelo.pkl

✅ resultado.txt

✅ ranking.png

🏆 Funcionalidades Principais

✅ AutoML automático

✅ Detecção de regressão ou classificação

✅ Ranking de modelos

✅ Versionamento automático

✅ Dashboard web

✅ Gráficos comparativos

✅ Relatório PDF

✅ Histórico de projetos

🛡️ Tratamento de Erros

O sistema possui:

✔️ Validação de dataset

✔️ Proteção contra CSV inválido

✔️ Proteção contra treino vazio

✔️ Mensagens de erro amigáveis
