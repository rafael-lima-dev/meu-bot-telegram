import os
import threading
from flask import Flask
from bot import main as start_bot  # importa sua função main()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot rodando no Render!"

# Iniciar o bot em uma thread separada
threading.Thread(target=start_bot).start()
