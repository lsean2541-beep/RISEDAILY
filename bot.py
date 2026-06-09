import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import threading

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8080))

# Motivational quotes in Portuguese
QUOTES = [
    "✨ Nem todo dia é bom, mas existe algo bom em todo dia.",
    "⚽ O jogo só acaba quando o apito final toca. Continue.",
    "🌅 Pequenos passos todos os dias. É assim que se chega longe.",
    "💪 Você é mais forte do que os desafios de hoje.",
    "📖 Cada dia é uma nova página. Escreva algo bonito.",
    "🎯 Foco no que você pode controlar. O resto é barulho.",
    "🕊️ Respire. Recomece. Siga em frente.",
    "🏆 A jornada é difícil, mas a chegada vale cada momento.",
    "🌱 Pequenas vitórias também são vitórias. Comemore cada uma.",
    "🎧 Coloque sua música favorita. Hoje vai ser um bom dia.",
    "☕ Uma coisa de cada vez. Sem pressa. Sem pressão.",
    "🌟 Você já superou dias piores. Este também vai passar.",
    "📌 Hoje é um novo começo. Use bem ele.",
    "🤝 Seja gentil com você mesmo. Você está tentando.",
    "🎈 Sorria. Nem que seja por um segundo. Isso já ajuda.",
]

# Categories
CATEGORIES = {
    "vida": ["🌱 A vida é feita de recomeços. Hoje é um deles.", "📖 Sua história ainda está sendo escrita.", "🌟 A vida não é perfeita, mas você pode tornar seu dia melhor."],
    "forca": ["💪 Você já superou desafios antes. Este não será diferente.", "⚡ A força não vem do corpo. Vem da vontade.", "🛡️ Mesmo cansado, você continua. Isso é força."],
    "felicidade": ["😊 Felicidade não é um destino. É um jeito de caminhar.", "🌸 Pequenas coisas trazem alegria. Um café. Um sol. Uma pausa.", "🎵 A felicidade mora nos momentos simples."],
    "sucesso": ["🎯 Sucesso é não desistir um dia a mais que os outros.", "📈 Cada pequeno avanço é vitória.", "🏆 Sucesso é seguir em frente quando tudo diz para parar."],
}

# Welcome message
WELCOME_MESSAGE = """
📌 *Segundo Tempo*

Frases curtas para o seu dia.

/enviar - receba uma frase
/topico - escolha por categoria
/ajuda - veja os comandos

Uma mensagem por vez. 18+
"""

# Create Flask app
flask_app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    keyboard = [
        [InlineKeyboardButton("📨 Enviar frase", callback_data='quote')],
        [InlineKeyboardButton("📂 Escolher categoria", callback_data='topic')],
        [InlineKeyboardButton("❓ Ajuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode='Markdown', reply_markup=reply_markup)

async def send_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random quote"""
    quote = random.choice(QUOTES)
    keyboard = [[InlineKeyboardButton("📨 Nova frase", callback_data='quote')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text(quote, reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(quote, reply_markup=reply_markup)

async def show_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show topic categories"""
    keyboard = [
        [InlineKeyboardButton("🌱 Vida", callback_data='topic_vida')],
        [InlineKeyboardButton("💪 Força", callback_data='topic_forca')],
        [InlineKeyboardButton("😊 Felicidade", callback_data='topic_felicidade')],
        [InlineKeyboardButton("🎯 Sucesso", callback_data='topic_sucesso')],
        [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text("📂 *Escolha uma categoria:*", parse_mode='Markdown', reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text("📂 *Escolha uma categoria:*", parse_mode='Markdown', reply_markup=reply_markup)

async def send_topic_quote(update: Update, context: ContextTypes.DEFAULT_TYPE, topic_key):
    """Send quote from specific category"""
    quotes = CATEGORIES.get(topic_key, QUOTES)
    quote = random.choice(quotes)
    keyboard = [
        [InlineKeyboardButton("📨 Outra frase", callback_data=f'topic_{topic_key}')],
        [InlineKeyboardButton("🔙 Voltar aos tópicos", callback_data='topic')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(quote, reply_markup=reply_markup)
    await update.callback_query.answer()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
📌 *Comandos disponíveis:*

/enviar - frase aleatória
/topico - frases por categoria
/ajuda - este menu
/start - voltar ao início

📂 *Categorias:*
vida, força, felicidade, sucesso

Uma mensagem por vez. 18+
"""
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    keyboard = [
        [InlineKeyboardButton("📨 Enviar frase", callback_data='quote')],
        [InlineKeyboardButton("📂 Escolher categoria", callback_data='topic')],
        [InlineKeyboardButton("❓ Ajuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(WELCOME_MESSAGE, parse_mode='Markdown', reply_markup=reply_markup)
    await update.callback_query.answer()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    data = query.data
    
    if data == 'quote':
        await send_quote(update, context)
    elif data == 'topic':
        await show_topics(update, context)
    elif data == 'help':
        await help_command(update, context)
    elif data == 'back':
        await back_to_start(update, context)
    elif data.startswith('topic_'):
        topic_key = data.replace('topic_', '')
        await send_topic_quote(update, context, topic_key)

# Flask routes
@flask_app.route('/')
def home():
    return "Bot is running!", 200

@flask_app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error', 500

def run_flask():
    flask_app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    # Create bot application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("enviar", send_quote))
    application.add_handler(CommandHandler("quote", send_quote))
    application.add_handler(CommandHandler("topico", show_topics))
    application.add_handler(CommandHandler("topic", show_topics))
    application.add_handler(CommandHandler("ajuda", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Set webhook if on Render
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        webhook_url = f"{render_url}/webhook/{TOKEN}"
        application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
        import time
        while True:
            time.sleep(1)
    else:
        logger.info("Starting polling...")
        application.run_polling()
