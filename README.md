Desenvolvendo uma plataforma AutoML em Python que treina, compara, escolhe o melhor modelo de Machine Learning e gera relatórios automaticamente — tudo com interface web e versão desktop (.EXE).

🚀 O que este sistema faz?
✅ Lê arquivos CSV ou Excel
✅ Detecta automaticamente se o problema é Classificação ou Regressão
✅ Faz pré-processamento automático dos dados
✅ Faz feature engineering automático
✅ Testa 20+ modelos de Machine Learning
✅ Usa validação cruzada
✅ Escolhe o melhor modelo automaticamente
✅ Gera:
•	📈 Gráficos de performance
•	🧪 Métricas completas
•	🧾 Relatório profissional em PDF
✅ Possui:
•	🌐 Interface Web (local)
•	💻 Versão Desktop .EXE
•	🔮 Tela para fazer previsões com novos arquivos
________________________________________
🖥️ Como funciona?
Apesar de abrir no navegador, o sistema é:
✅ 100% local (offline)
Ele roda no seu próprio computador usando:
•	Flask (backend)
•	Scikit-learn (ML)
•	Pandas (dados)
•	Matplotlib (gráficos)
•	ReportLab (PDF)
________________________________________
🗂️ Estrutura do Projeto
FabricaDeModelo/
 ├── app.py
 ├── run_app.py
 ├── automl_engine.py
 ├── predictor.py
 ├── pdf_report.py
 ├── requirements.txt
 ├── uploads/
 ├── projects/
 ├── static/
 │    └── style.css
 └── templates/
      ├── index.html
      ├── dashboard.html
      └── prever.html
________________________________________
⚙️ Instalação
1️⃣ Criar ambiente virtual (opcional, recomendado)
python -m venv venv
venv\Scripts\activate
________________________________________
2️⃣ Instalar dependências
pip install -r requirements.txt
________________________________________
3️⃣ Rodar o sistema
python app.py
Abra no navegador:
http://127.0.0.1:5000
________________________________________
🧪 Como usar
🏗️ Treinar modelo
1.	Clique em Escolher arquivo
2.	Envie um CSV
3.	Clique em Treinar
4.	Aguarde o processamento
5.	O sistema:
o	Testa vários modelos
o	Escolhe o melhor
o	Gera gráfico
o	Gera relatório
o	Gera PDF automaticamente
________________________________________
📊 Ver resultados
•	Clique no projeto salvo
•	Veja:
o	Métricas
o	Ranking de modelos
o	Gráfico
•	Baixe o PDF
________________________________________
🔮 Fazer previsões
1.	Clique em Fazer previsões
2.	Escolha um projeto treinado
3.	Envie um novo CSV
4.	O sistema gera um novo arquivo com as previsões
________________________________________
📦 Gerar versão .EXE
Instale o PyInstaller:
pip install pyinstaller
Depois:
pyinstaller --onefile --noconsole run_app.py
O executável estará em:
dist/FabricaDeModelo.exe
________________________________________
🧠 Tecnologias usadas
•	Python
•	Flask
•	Pandas
•	Scikit-learn
•	Matplotlib
•	ReportLab
•	PyInstaller
________________________________________
📌 Casos de uso
•	Análise de:
o	Clientes
o	Churn
o	Vendas
o	Preços
o	Score
o	Risco
o	Qualquer dataset tabular
________________________________________
⭐ Próximas versões (roadmap)
•	🌐 Versão online (SaaS)
•	📊 Dashboard mais avançado
•	🧠 Deep Learning
•	📦 Auto deploy

