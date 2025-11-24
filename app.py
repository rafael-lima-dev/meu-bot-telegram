import asyncio
from flask import Flask
from bot import main as start_bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot rodando no Render!"

# Inicializa o bot de forma assíncrona
async def run_bot():
    await asyncio.to_thread(start_bot)

loop = asyncio.get_event_loop()
loop.create_task(run_bot())
