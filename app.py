import threading
from flask import Flask
from bot import main as start_bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot rodando no Render!"

# inicia o bot em uma thread separada
def run_bot_thread():
    start_bot()

threading.Thread(target=run_bot_thread, daemon=True).start()
