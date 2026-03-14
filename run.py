# Importa a biblioteca uvicorn, que é um servidor ASGI para aplicações web.
import uvicorn

# Importa a instância 'settings' do módulo de configurações da aplicação.
from app.config.settings import settings

# Verifica se o script está sendo executado diretamente (e não importado como um módulo).
if __name__ == "__main__":
    # Inicia o servidor uvicorn.
    uvicorn.run(
        # Especifica o módulo e a instância da aplicação FastAPI a ser executada ("app.main" e a variável "app").
        "app.main:app",
        # Define o host onde o servidor irá escutar, obtido das configurações.
        host=settings.host,
        # Define a porta onde o servidor irá escutar, obtida das configurações.
        port=settings.port,
        # Habilita o modo de recarregamento automático (o servidor reinicia ao detectar mudanças no código).
        reload=True,
    )
