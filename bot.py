import os
import logging
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

# Channel links
CHANNEL_1_LINK = "https://t.me/LMPbravo1"
CHANNEL_2_LINK = "https://t.me/Santorini222"

# Welcome message
WELCOME_MESSAGE = """
🎯 *BEM-VINDO AO PORTAL DE APOSTAS* 🎯

Escolha seu canal de football betting preferido:

📢 *Canal 1:* LMP BRAVO - Múltiplas diárias
🎲 *Canal 2:* SANTORINI - Odds especiais

*Clique nos botões abaixo para entrar!* 💰
"""

# Create Flask app
flask_app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with channel buttons"""
    keyboard = [
        [InlineKeyboardButton("📢 CANAL 1 - LMP BRAVO", url=CHANNEL_1_LINK)],
        [InlineKeyboardButton("🎲 CANAL 2 - SANTORINI", url=CHANNEL_2_LINK)],
        [InlineKeyboardButton("❓ AJUDA", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
🤖 *Como usar:*
• Clique nos botões acima para entrar nos canais
• Receba múltiplas e odds diárias
• Use /start para ver os canais novamente

📌 *Canais:*
@LMPbravo1 - Múltiplas com odds até 3.38x
@Santorini222 - Seleções especiais +12.5% extra
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        help_text = "Clique nos botões acima para entrar nos canais de apostas! 🚀"
        await query.edit_message_text(help_text, parse_mode='Markdown')
        
        # Resend keyboard
        keyboard = [
            [InlineKeyboardButton("📢 CANAL 1 - LMP BRAVO", url=CHANNEL_1_LINK)],
            [InlineKeyboardButton("🎲 CANAL 2 - SANTORINI", url=CHANNEL_2_LINK)],
            [InlineKeyboardButton("❓ AJUDA", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("👇 *Escolha seu canal:*", parse_mode='Markdown', reply_markup=reply_markup)

# Flask route for health check
@flask_app.route('/')
def home():
    return "Bot is running!", 200

@flask_app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error', 500

def run_flask():
    """Run Flask server"""
    flask_app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    # Create bot application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
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
        # Keep the application running
        import time
        while True:
            time.sleep(1)
    else:
        # Use polling for local development
        logger.info("Starting polling...")
        application.run_polling()
