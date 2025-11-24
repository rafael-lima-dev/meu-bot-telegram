import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")

CATALOGO = {
    "portugues": {  
        "titulo": "📚 Português para Concursos",
        "desc": "Gramática completa e interpretação de texto. Módulo único.",
        "preco": "R$ 29,90",
        "chave_pix": "pix-portugues@email.com",
        "id_canal": "-1003378442615"
    },
    "informatica": { 
        "titulo": "💻 Informática Essencial",
        "desc": "Hardware, Windows e Office. Módulo único.",
        "preco": "R$ 49,90",
        "chave_pix": "pix-informatica@email.com",
        "id_canal": "-1003335284498"
    },
    "vip": {
        "titulo": "💎 PACOTE VIP (ACESSO TOTAL)",
        "desc": "Acesso liberado aos DOIS canais (Português + Informática).",
        "preco": "R$ 69,90",
        "chave_pix": "pix-vip@email.com",
        "id_canal": "todos"
    }
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------------------------
# 1. MENU E BOAS-VINDAS
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    inscritos = random.randint(4850, 4990)
    
    texto = (
        f"Olá, {user.first_name}! 👋\n\n"
        f"🎓 Bem-vindo à **Escola Tech Brasil**.\n"
        f"🚀 **{inscritos} alunos online estudando agora!**\n\n"
        "👇 Escolha sua especialização abaixo:"
    )
    
    await mostrar_vitrine(update, context, texto)

async def mostrar_vitrine(update: Update, context: ContextTypes.DEFAULT_TYPE, texto_msg=None):
    keyboard = [
        [InlineKeyboardButton("📚 Curso de Português", callback_data='info_portugues')],
        [InlineKeyboardButton("💻 Curso de Informática", callback_data='info_informatica')],
        [InlineKeyboardButton("💎 PACOTE VIP (Leve Tudo)", callback_data='info_vip')],
        [InlineKeyboardButton("🆘 Suporte", callback_data='suporte')]
    ]
    
    msg = texto_msg or "📂 **CATÁLOGO DE CURSOS:**"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            msg, 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            msg, 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# ---------------------------------------------------------------------------
# 2. FILTRO TEXTO
# ---------------------------------------------------------------------------
async def filtrar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await mostrar_vitrine(update, context, f"Olá, {user.first_name}! Use os botões abaixo para navegar:")

# ---------------------------------------------------------------------------
# 3. DETALHES DO CURSO
# ---------------------------------------------------------------------------
async def mostrar_detalhes(update: Update, context: ContextTypes.DEFAULT_TYPE, produto_key):
    query = update.callback_query

    if produto_key not in CATALOGO:
        await query.answer("Produto não encontrado.", show_alert=True)
        return
    
    item = CATALOGO[produto_key]
    
    texto = (
        f"📦 **{item['titulo']}**\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        f"{item['desc']}\n\n"
        f"💰 **Investimento:** {item['preco']}\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "Deseja garantir sua vaga?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ QUERO COMPRAR", callback_data=f"pagar_{produto_key}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")]
    ]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def tela_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE, produto_key):
    query = update.callback_query
    item = CATALOGO[produto_key]
    
    texto = (
        f"💳 **PAGAMENTO VIA PIX**\n\n"
        f"Curso: **{item['titulo']}**\n"
        f"Valor: **{item['preco']}**\n\n"
        "1️⃣ Copie a chave Pix:\n"
        f"`{item['chave_pix']}`\n\n"
        "2️⃣ Pague no seu banco.\n"
        "3️⃣ Confirme abaixo."
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ JÁ PAGUEI", callback_data=f"confirmar_{produto_key}")],
        [InlineKeyboardButton("🔙 Cancelar", callback_data=f"info_{produto_key}")]
    ]
    
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ---------------------------------------------------------------------------
# 4. ENTREGA DO ACESSO
# ---------------------------------------------------------------------------
async def entregar_acesso(update: Update, context: ContextTypes.DEFAULT_TYPE, produto_key):
    query = update.callback_query
    await query.answer("Validando pagamento...")

    item = CATALOGO[produto_key]
    bot = context.bot

    try:
        if item["id_canal"] == "todos":
            link_port = await bot.create_chat_invite_link(
                chat_id=CATALOGO["portugues"]["id_canal"],
                member_limit=1
            )
            link_info = await bot.create_chat_invite_link(
                chat_id=CATALOGO["informatica"]["id_canal"],
                member_limit=1
            )

            texto = (
                "🎉 <b>PARABÉNS! VOCÊ VIROU VIP!</b> 💎\n\n"
                f"1️⃣ <a href='{link_port.invite_link}'>Entrar no canal de Português</a>\n"
                f"2️⃣ <a href='{link_info.invite_link}'>Entrar no canal de Informática</a>\n\n"
                "<i>Bons estudos!</i>"
            )
        else:
            convite = await bot.create_chat_invite_link(
                chat_id=item["id_canal"],
                member_limit=1
            )

            texto = (
                "🎉 <b>PAGAMENTO CONFIRMADO!</b>\n\n"
                f"Aqui está seu acesso ao curso:\n"
                f"{convite.invite_link}"
            )

        await query.edit_message_text(texto, parse_mode="HTML")

    except Exception as e:
        await query.edit_message_text(
            f"❌ <b>Erro ao gerar link:</b>\n{e}",
            parse_mode="HTML"
        )

# ---------------------------------------------------------------------------
# 5. CALLBACK DOS BOTÕES
# ---------------------------------------------------------------------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_principal":
        await mostrar_vitrine(update, context)

    elif data.startswith("info_"):
        await mostrar_detalhes(update, context, data.split("_")[1])

    elif data.startswith("pagar_"):
        await tela_pagamento(update, context, data.split("_")[1])

    elif data.startswith("confirmar_"):
        await entregar_acesso(update, context, data.split("_")[1])

    elif data == "suporte":
        await query.edit_message_text(
            "👨‍💻 **Suporte Técnico**\nFale com @Murilo",
            parse_mode="Markdown"
        )

# ---------------------------------------------------------------------------
# 6. MAIN — (CORRETO PARA RENDER + PTB 21 + FLASK)
# ---------------------------------------------------------------------------
def main():
    print("🚀 BOT DE VENDAS INICIADO!")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, filtrar_texto)
    )

    application.run_polling()  # NÃO usar async

if __name__ == "__main__":
    main()
