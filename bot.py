import logging
import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler,
    filters, 
    ContextTypes
)

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# ---------------------------------------------------------------------------
TOKEN = os.getenv("TOKEN")

# ---------------------------------------------------------------------------
# BANCO DE DADOS DOS CURSOS
# ---------------------------------------------------------------------------
CATALOGO = {
    "portugues": {  
        "titulo": "📚 Português para Concursos",
        "desc": "Gramática completa e interpretação de texto. Módulo único.",
        "preco": "R$ 29,90",
        "chave_pix": "pix-portugues@email.com",
        # ID do Canal de Português (Antigo)
        "id_canal": "-1003378442615" 
    },
    "informatica": { 
        "titulo": "💻 Informática Essencial",
        "desc": "Hardware, Windows e Office. Módulo único.",
        "preco": "R$ 49,90",
        "chave_pix": "pix-informatica@email.com",
        # ID do Canal de Informática (NOVO)
        "id_canal": "-1003335284498" 
    },
    "vip": {
        "titulo": "💎 PACOTE VIP (ACESSO TOTAL)",
        "desc": "Acesso liberado aos DOIS canais (Português + Informática).",
        "preco": "R$ 69,90",
        "chave_pix": "pix-vip@email.com",
        # VIP libera todos os canais acima
        "id_canal": "todos"
    }
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ---------------------------------------------------------------------------
# 1. MENU E BOAS VINDAS
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Prova Social: Número aleatório de alunos online para gerar autoridade
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
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = texto_msg or "📂 **CATÁLOGO DE CURSOS:**"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

# ---------------------------------------------------------------------------
# 2. FILTRO DE TEXTO (RESPONDER A "OLÁ", ETC)
# ---------------------------------------------------------------------------
async def filtrar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await mostrar_vitrine(update, context, f"Olá, {user.first_name}! Use os botões abaixo para navegar:")

# ---------------------------------------------------------------------------
# 3. DETALHES E COMPRA
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
        [InlineKeyboardButton("✅ QUERO COMPRAR", callback_data=f'pagar_{produto_key}')],
        [InlineKeyboardButton("🔙 Voltar", callback_data='menu_principal')]
    ]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

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
        [InlineKeyboardButton("✅ JÁ PAGUEI", callback_data=f'confirmar_{produto_key}')],
        [InlineKeyboardButton("🔙 Cancelar", callback_data=f'info_{produto_key}')]
    ]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ---------------------------------------------------------------------------
# 4. ENTREGA INTELIGENTE (LINKS SEPARADOS)
# ---------------------------------------------------------------------------
async def entregar_acesso(update: Update, context: ContextTypes.DEFAULT_TYPE, produto_key):
    query = update.callback_query
    await query.answer("Validando pagamento...")
    
    item = CATALOGO[produto_key]
    id_alvo = item['id_canal']
    
    try:
        # --- CENÁRIO 1: COMPRA VIP (ENTREGA TUDO) ---
        if id_alvo == "todos":
            # Gera link para Português
            link_port = await context.bot.create_chat_invite_link(
                chat_id=CATALOGO['portugues']['id_canal'], 
                member_limit=1,
                name=f"VIP: {query.from_user.first_name}"
            )
            # Gera link para Informática
            link_info = await context.bot.create_chat_invite_link(
                chat_id=CATALOGO['informatica']['id_canal'], 
                member_limit=1,
                name=f"VIP: {query.from_user.first_name}"
            )
            
            # Mensagem em HTML para suportar múltiplos links
            mensagem_final = (
                "🎉 <b>PARABÉNS! VOCÊ VIROU VIP!</b> 💎\n\n"
                "Seu acesso total foi liberado. Entre nos canais abaixo:\n\n"
                f"1️⃣ <b>Canal de Português:</b> <a href='{link_port.invite_link}'>[CLIQUE PARA ENTRAR]</a>\n"
                f"2️⃣ <b>Canal de Informática:</b> <a href='{link_info.invite_link}'>[CLIQUE PARA ENTRAR]</a>\n\n"
                "<i>Bons estudos!</i>"
            )

        # --- CENÁRIO 2: COMPRA INDIVIDUAL ---
        else:
            convite = await context.bot.create_chat_invite_link(
                chat_id=id_alvo,
                member_limit=1,
                name=f"Venda: {query.from_user.first_name}"
            )
            
            mensagem_final = (
                f"🎉 <b>PAGAMENTO APROVADO!</b>\n\n"
                f"Aqui está seu acesso exclusivo ao curso de <b>{item['titulo']}</b>:\n\n"
                f"👉 {convite.invite_link}\n\n"
                "<i>Clique agora, este é um link único!</i>"
            )
            
        await query.edit_message_text(mensagem_final, parse_mode='HTML')
        
    except Exception as e:
        # Tratamento de erros comuns (Bot não é admin)
        erro_txt = str(e)
        dica = ""
        if "Chat not found" in erro_txt:
            dica = "Dica: Verifique se o ID do canal está correto e começa com -100."
        elif "Administrator rights" in erro_txt:
            dica = "Dica: Coloque o Bot como ADMIN no canal e dê permissão de convidar usuários."

        await query.edit_message_text(
            f"❌ <b>Erro na Entrega:</b> {erro_txt}<br><br>{dica}", 
            parse_mode='HTML'
        )

# ---------------------------------------------------------------------------
# 5. GERENCIADOR DE CLIQUES
# ---------------------------------------------------------------------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'menu_principal':
        await mostrar_vitrine(update, context)
        
    elif data.startswith('info_'):
        prod = data.split('_')[1] 
        await mostrar_detalhes(update, context, prod)
        
    elif data.startswith('pagar_'):
        prod = data.split('_')[1]
        await tela_pagamento(update, context, prod)
        
    elif data.startswith('confirmar_'):
        prod = data.split('_')[1]
        await entregar_acesso(update, context, prod)
        
    elif data == 'suporte':
        msg = "👨‍💻 **Suporte Técnico**\n\nPrecisa de ajuda? Chame o @Murilo."
        kb = [[InlineKeyboardButton("🔙 Voltar", callback_data='menu_principal')]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')



def main():
    print("🚀 BOT DE VENDAS MULTI-CANAIS INICIADO!")

    application = ApplicationBuilder().token(TOKEN).build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtrar_texto))

    print("Aguardando clientes...")

    application.run_polling()



if __name__ == "__main__":
    main()