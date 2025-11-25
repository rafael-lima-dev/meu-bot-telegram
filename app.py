from flask import Flask
import asyncio
import threading
from bot import main_async

app = Flask(__name__)

# Inicia o bot em uma thread separada
def start_bot():
    asyncio.run(main_async())

threading.Thread(target=start_bot, daemon=True).start()

@app.route("/")
def home():
    return "BOT RODANDO! 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
