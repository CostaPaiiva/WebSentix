O **WebSentix** é uma aplicação web baseada em **FastAPI** para análise de sentimento a partir de textos, URLs e arquivos enviados, com recursos de resumo, extração de palavras-chave, histórico e exportação.

## Visão Geral

O **WebSentix** é uma aplicação web em Python, orientada para produção, projetada para analisar sentimentos a partir de diferentes fontes de conteúdo:

- entrada manual de texto
- URLs públicas
- arquivos enviados nos formatos `.txt`, `.pdf` e `.docx`

A plataforma processa e limpa o conteúdo, realiza análise de sentimento em português, gera um resumo leve, extrai palavras-chave, armazena um histórico local e permite exportações em PDF, TXT e Excel.

## Funcionalidades

- Análise de sentimento a partir de texto, URL ou upload de arquivo
- Pipeline de PLN amigável para português
- Classificação de sentimento: **positivo**, **negativo** e **neutro**
- Pontuação de confiança e polaridade
- Extração automática de palavras-chave
- Resumo extrativo
- Suporte a upload de arquivos `.txt`, `.pdf`, `.docx`
- Armazenamento de histórico local
- Exportação de resultados em **PDF**, **TXT** e **Excel**
- Exportação do histórico em **Excel**
- Frontend responsivo renderizado no servidor com **FastAPI + Jinja2**

## Stack Tecnológica

### Backend

- FastAPI
- Uvicorn
- Pydantic

### Frontend

- Jinja2
- HTML5
- CSS3
- JavaScript

### PLN e Processamento

- Transformers
- Torch
- YAKE

### Manipulação de Conteúdo e Arquivos

- httpx
- BeautifulSoup
- python-docx
- pypdf

### Exportação

- ReportLab
- pandas
- openpyxl

### Testes

- pytest

## Arquitetura

```text
websentix/
├── app/
│   ├── routers/
│   ├── services/
│   ├── models/
│   ├── utils/
│   ├── config/
│   ├── templates/
│   └── static/
├── tests/
├── data/
├── requirements.txt
├── Dockerfile
└── run.py
Camadas

routers/: rotas HTTP, páginas, exportações e endpoints de análise

services/: lógica de negócio para PLN, leitura de arquivos, scraping, histórico e exportação

models/: esquemas e enums compartilhados

utils/: validação, logging e utilitários de limpeza de texto

templates/ e static/: interface web

config/: configurações baseadas em ambiente

Instalação
1. Criar ambiente virtual

Linux/macOS

python -m venv .venv
source .venv/bin/activate

Windows

python -m venv .venv
.venv\Scripts\activate
2. Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
3. Configurar ambiente

Linux/macOS

cp .env.example .env

Windows

copy .env.example .env
Execução Local
python run.py

Ou:

uvicorn app.main:app --reload

Acesse no navegador:

http://127.0.0.1:8000
Execução com Docker
docker build -t websentix .
docker run -p 8000:8000 websentix
Testes
pytest -q
Principais Endpoints

GET / — interface principal

POST /api/analyze — análise baseada em formulário

POST /api/analyze/json — endpoint com resposta orientada a JSON

GET /exports/latest/pdf — exporta o resultado mais recente em PDF

GET /exports/latest/txt — exporta o resultado mais recente em TXT

GET /exports/latest/excel — exporta o resultado mais recente em Excel

GET /exports/history/excel — exporta o histórico em Excel

GET /health — verificação de saúde da aplicação

Observações e Limitações

Alguns sites podem bloquear scraping

PDFs digitalizados apenas como imagem podem exigir OCR

O resumo é extrativo e heurístico

O modelo de sentimento escolhido é multilíngue, não específico de domínio

Próximas Melhorias

Persistência com SQLite ou PostgreSQL

Autenticação e autorização

OCR para PDFs digitalizados

Cache do modelo na inicialização

Esquemas de resposta REST para todos os endpoints

Jobs assíncronos para documentos grandes

Melhor observabilidade e logging estruturado