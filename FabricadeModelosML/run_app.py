import webbrowser   # Módulo para abrir URLs diretamente no navegador padrão
import threading    # Módulo para trabalhar com threads (execução paralela)
from app import app # Importa a aplicação Flask definida no arquivo app.py

# Função que abre o navegador na URL local da aplicação Flask
def abrir():
    webbrowser.open("http://127.0.0.1:5000")

# Ponto de entrada principal do programa
if __name__ == "__main__":
    # Cria um temporizador que aguarda 1.5 segundos e depois chama a função 'abrir'
    # Isso garante que o servidor Flask já esteja rodando antes de abrir o navegador
    threading.Timer(1.5, abrir).start()

    # Inicia a aplicação Flask
    # debug=False significa que não será usado o modo de depuração (sem recarregamento automático e sem debugger ativo)
    app.run(debug=False)
