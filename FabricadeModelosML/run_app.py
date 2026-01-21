import webbrowser
import threading
from app import app

def abrir():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.5, abrir).start()
    app.run(debug=False)
