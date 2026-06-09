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

# Motivational quotes in English
QUOTES = [
    "✨ Not every day is good, but there is something good in every day.",
    "⚽ The game only ends when the final whistle blows. Keep going.",
    "🌅 Small steps every day. That's how you go far.",
    "💪 You are stronger than today's challenges.",
    "📖 Each day is a new page. Write something beautiful.",
    "🎯 Focus on what you can control. The rest is noise.",
    "🕊️ Breathe. Restart. Move forward.",
    "🏆 The journey is hard, but the arrival is worth every moment.",
    "🌱 Small wins are still wins. Celebrate each one.",
    "🎧 Play your favorite song. Today will be a good day.",
    "☕ One thing at a time. No rush. No pressure.",
    "🌟 You have survived worse days. This one will pass too.",
    "📌 Today is a new beginning. Use it well.",
    "🤝 Be kind to yourself. You are trying.",
    "🎈 Smile. Even for one second. It helps.",
]

# Categories
CATEGORIES = {
    "life": ["🌱 Life is made of fresh starts. Today is one of them.", "📖 Your story is still being written.", "🌟 Life is not perfect, but you can make your day better."],
    "strength": ["💪 You have overcome challenges before. This one is no different.", "⚡ Strength does not come from the body. It comes from will.", "🛡️ Even tired, you keep going. That is strength."],
    "happiness": ["😊 Happiness is not a destination. It is a way of walking.", "🌸 Small things bring joy. A coffee. The sun. A pause.", "🎵 Happiness lives in simple moments."],
    "success": ["🎯 Success is not giving up one day longer than others.", "📈 Every small step forward is a win.", "🏆 Success is moving forward when everything says to stop."],
}

# Welcome message
WELCOME_MESSAGE = """
📌 *Second Half*

Short phrases for your day.

/send - get a random phrase
/topic - choose by category
/help - see all commands

One message at a time.
"""

# Create Flask app
flask_app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    keyboard = [
        [InlineKeyboardButton("📨 Send phrase", callback_data='quote')],
        [InlineKeyboardButton("📂 Choose category", callback_data='topic')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode='Markdown', reply_markup=reply_markup)

async def send_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random quote"""
    quote = random.choice(QUOTES)
    keyboard = [[InlineKeyboardButton("📨 New phrase", callback_data='quote')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text(quote, reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(quote, reply_markup=reply_markup)

async def show_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show topic categories"""
    keyboard = [
        [InlineKeyboardButton("🌱 Life", callback_data='topic_life')],
        [InlineKeyboardButton("💪 Strength", callback_data='topic_strength')],
        [InlineKeyboardButton("😊 Happiness", callback_data='topic_happiness')],
        [InlineKeyboardButton("🎯 Success", callback_data='topic_success')],
        [InlineKeyboardButton("🔙 Back", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text("📂 *Choose a category:*", parse_mode='Markdown', reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text("📂 *Choose a category:*", parse_mode='Markdown', reply_markup=reply_markup)

async def send_topic_quote(update: Update, context: ContextTypes.DEFAULT_TYPE, topic_key):
    """Send quote from specific category"""
    quotes = CATEGORIES.get(topic_key, QUOTES)
    quote = random.choice(quotes)
    keyboard = [
        [InlineKeyboardButton("📨 Another phrase", callback_data=f'topic_{topic_key}')],
        [InlineKeyboardButton("🔙 Back to topics", callback_data='topic')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(quote, reply_markup=reply_markup)
    await update.callback_query.answer()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
📌 *Available commands:*

/send - random phrase
/topic - phrases by category
/help - this menu
/start - return to main menu

📂 *Categories:*
life, strength, happiness, success

One message at a time.
"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    keyboard = [
        [InlineKeyboardButton("📨 Send phrase", callback_data='quote')],
        [InlineKeyboardButton("📂 Choose category", callback_data='topic')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
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
    application.add_handler(CommandHandler("send", send_quote))
    application.add_handler(CommandHandler("quote", send_quote))
    application.add_handler(CommandHandler("topic", show_topics))
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
