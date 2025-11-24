import threading
from flask import Flask
from bot import main as start_bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot rodando no Render!"

def run_bot_thread():
    start_bot()

# iniciar bot em thread separada (ESSENCIAL NO RENDER)
threading.Thread(target=run_bot_thread, daemon=True).start()
