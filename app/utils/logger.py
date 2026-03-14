# 1. Importa suporte para anotações futuras de tipo, permitindo tipagem moderna em versões antigas do Python.
# 2. Configura e utiliza o módulo de logging do Python para registrar mensagens de log da aplicação.
# 3. Define uma função utilitária `get_logger` que retorna um objeto logger configurado.
# 4. Cria ou obtém um logger específico com base no nome passado como parâmetro.
# 5. Verifica se já existem handlers configurados no logger raiz; se não houver, aplica configuração padrão.
# 6. Define o nível de log dinamicamente a partir das configurações da aplicação (settings.log_level).
# 7. Especifica o formato das mensagens de log, incluindo data/hora, nível, nome do logger e mensagem, garantindo clareza nos registros.

# Ativa o comportamento moderno das anotações de tipo do Python,
# permitindo que elas sejam avaliadas apenas em tempo de execução.
from __future__ import annotations

# Importa o módulo padrão de logging do Python,
# usado para registrar mensagens de log (debug, info, erro, etc.).
import logging

# Importa o tipo Logger da biblioteca logging,
# usado para tipagem da função.
from logging import Logger

# Importa as configurações da aplicação (settings),
# onde ficam valores como nível de log, variáveis de ambiente etc.
from app.config.settings import settings


# Função responsável por criar ou retornar um logger configurado.
# Recebe o nome do logger e retorna um objeto Logger.
def get_logger(name: str) -> Logger:

    # Obtém (ou cria) um logger com o nome fornecido.
    # Loggers com o mesmo nome compartilham a mesma configuração.
    logger = logging.getLogger(name)

    # Verifica se o logger raiz ainda não possui handlers configurados.
    # Isso evita configurar o logging várias vezes.
    if not logging.getLogger().handlers:

        # Configura o logging básico da aplicação.
        logging.basicConfig(

            # Define o nível de log com base na configuração da aplicação.
            # Caso o valor não exista, usa INFO como padrão.
            level=getattr(logging, settings.log_level.upper(), logging.INFO),

            # Define o formato das mensagens de log.
            # Inclui data/hora, nível do log, nome do logger e mensagem.
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

    # Retorna o logger configurado.
    return logger