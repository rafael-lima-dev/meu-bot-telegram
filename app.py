import threading
import asyncio
from flask import Flask
from bot import main_async

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot rodando no Render!"

def run_bot_thread():
    asyncio.run(main_async())

threading.Thread(target=run_bot_thread, daemon=True).start()
