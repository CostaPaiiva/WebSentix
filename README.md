Fábrica de Modelos ML (FabricaDeModelosML):

É Plataforma AutoML local para criação, versionamento, comparação e gerenciamento de modelos de Machine Learning com interface web.

Visão Geral:

A FabricaDeModelosML é uma plataforma desenvolvida em Python + Flask que permite:

✔️ Enviar um dataset CSV

✔️ Detectar automaticamente o tipo de problema (Regressão ou Classificação)

✔️ Treinar vários modelos automaticamente (AutoML)

✔️ Gerar ranking dos modelos

✔️ Criar gráficos de comparação

✔️ Versionar cada treino (v1, v2, v3, ...)

✔️ Gerar relatório PDF automático

✔️ Visualizar tudo em um dashboard web

✔️ Preparar o projeto para uso real em produção ou como produto

✔️ Interface

✔️ Tema escuro (preto + roxo)

✔️ Dashboard de projetos

✔️ Ranking visual de modelos

✔️ Gráficos de comparação

✔️ Histórico de treinos

✔️ Download de relatório em PDF

Como Usar:

- Acesse a página inicial
- Envie um arquivo CSV

O sistema:

✔️ Detecta o tipo de problema

✔️ Treina vários modelos

✔️ Cria ranking

✔️ Salva versão automaticamente

✔️ Gera gráfico e PDF

✔️ Você é redirecionado para o dashboard do projeto

✔️ Sistema de Versionamento

✔️ Cada novo treino cria automaticamente:

projects/nome_do_projeto/treinos/v1
projects/nome_do_projeto/treinos/v2
projects/nome_do_projeto/treinos/v3
...


Cada versão contém:

✅ modelo.pkl

✅ resultado.txt

✅ ranking.png

✅meta.json

✅relatorio.pdf

✅produção.json

Funcionalidades Principais:

✅ AutoML automático

✅ Detecção de regressão ou classificação

✅ Ranking de modelos

✅ Versionamento automático

✅ Dashboard web

✅ Gráficos comparativos

✅ Relatório PDF

✅ Histórico de projetos

Tratamento de Erros:

O sistema possui:

✔️ Validação de dataset

✔️ Proteção contra CSV inválido

✔️ Proteção contra treino vazio

✔️ Mensagens de erro amigáveis
