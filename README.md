# WebSentix

<p align="center">
  <strong>Análise de sentimento em português a partir de texto, URLs e arquivos</strong>
</p>

<p align="center">
  Aplicação web desenvolvida com FastAPI para analisar sentimentos, extrair palavras-chave, gerar resumos e exportar resultados.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-blue">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Web%20Framework-009688">
  <img alt="Status" src="https://img.shields.io/badge/status-em%20desenvolvimento-orange">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## Sobre o projeto

O **WebSentix** é uma aplicação web orientada para análise de sentimento em **português**, construída com **FastAPI**, capaz de processar conteúdo vindo de diferentes fontes:

- texto digitado manualmente
- URLs públicas
- arquivos enviados em `.txt`, `.pdf` e `.docx`

A plataforma realiza o processamento e limpeza do conteúdo, aplica análise de sentimento, gera um resumo extrativo, extrai palavras-chave relevantes, salva o histórico localmente e permite exportar resultados em **PDF**, **TXT** e **Excel**.

## Funcionalidades

- Análise de sentimento a partir de:
  - texto manual
  - URL pública
  - upload de arquivos
- Classificação de sentimento em:
  - **Positivo**
  - **Negativo**
  - **Neutro**
- Score de confiança e polaridade
- Extração automática de palavras-chave
- Resumo extrativo
- Suporte para arquivos `.txt`, `.pdf` e `.docx`
- Histórico local de análises
- Exportação do resultado em:
  - PDF
  - TXT
  - Excel
- Exportação do histórico em Excel
- Interface responsiva renderizada no servidor com **FastAPI + Jinja2**

## Tecnologias utilizadas

### Backend
- FastAPI
- Uvicorn
- Pydantic

### Frontend
- Jinja2
- HTML5
- CSS3
- JavaScript

### NLP e processamento
- Transformers
- Torch
- YAKE

### Manipulação de conteúdo e arquivos
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

## Estrutura do projeto

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
Arquitetura por camadas

routers/: define rotas HTTP, páginas, endpoints de análise e exportação

services/: concentra a lógica de negócio para NLP, scraping, leitura de arquivos, histórico e exportação

models/: reúne schemas, enums e estruturas compartilhadas

utils/: utilitários de validação, limpeza de texto e logging

templates/ e static/: responsáveis pela interface web

config/: centraliza configurações baseadas em ambiente

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

3. Configurar variáveis de ambiente
Linux/macOS
cp .env.example .env
Windows
copy .env.example .env
Como executar o projeto
Rodando localmente
python run.py

Ou:

uvicorn app.main:app --reload

Acesse em:

http://127.0.0.1:8000
Rodando com Docker
docker build -t websentix .
docker run -p 8000:8000 websentix
Executando os testes
pytest -q
Endpoints principais
Método	Endpoint	Descrição
GET	/	Interface principal
POST	/api/analyze	Análise via formulário
POST	/api/analyze/json	Retorno da análise em JSON
GET	/exports/latest/pdf	Exporta o último resultado em PDF
GET	/exports/latest/txt	Exporta o último resultado em TXT
GET	/exports/latest/excel	Exporta o último resultado em Excel
GET	/exports/history/excel	Exporta o histórico em Excel
GET	/health	Healthcheck da aplicação

Limitações

Alguns sites podem bloquear scraping

PDFs escaneados em imagem podem exigir OCR

O resumo é extrativo e heurístico

O modelo de sentimento é multilíngue, não especializado em um domínio específico

Melhorias futuras

Persistência com SQLite ou PostgreSQL

Autenticação e autorização

OCR para PDFs escaneados

Cache de modelo na inicialização

Schemas REST completos para todos os endpoints

Processamento assíncrono para documentos grandes

Melhor observabilidade e logging estruturado

Demonstração

Você pode adicionar aqui:

screenshot da interface

GIF de uso

link para deploy

exemplos de entrada e saída

Objetivo do projeto

O WebSentix foi criado para fins de estudo e servir como uma base prática e extensível para aplicações de análise textual em português, reunindo processamento de linguagem natural, leitura de múltiplas fontes e exportação de resultados em uma interface simples e funcional.

Licença

Este projeto pode ser distribuído sob a licença MIT.