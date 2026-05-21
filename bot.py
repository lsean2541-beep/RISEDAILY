import os
import random
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Check if token exists
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
    print("ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
    exit(1)

# Quote database organized by topic
QUOTES = {
    "success": [
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
        "Success usually comes to those who are too busy to be looking for it. - Henry David Thoreau",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "The secret of success is to do the common thing uncommonly well. - John D. Rockefeller Jr."
    ],
    "life": [
        "Life is what happens when you're busy making other plans. - John Lennon",
        "In the end, it's not the years in your life that count. It's the life in your years. - Abraham Lincoln",
        "The purpose of our lives is to be happy. - Dalai Lama",
        "Life is really simple, but we insist on making it complicated. - Confucius",
        "Get busy living or get busy dying. - Stephen King"
    ],
    "happiness": [
        "Happiness is not something readymade. It comes from your own actions. - Dalai Lama",
        "For every minute you are angry you lose sixty seconds of happiness. - Ralph Waldo Emerson",
        "The happiness of your life depends upon the quality of your thoughts. - Marcus Aurelius",
        "Happiness is when what you think, what you say, and what you do are in harmony. - Mahatma Gandhi",
        "The secret of happiness is freedom. The secret of freedom is courage. - Thucydides"
    ],
    "strength": [
        "Strength does not come from physical capacity. It comes from an indomitable will. - Mahatma Gandhi",
        "You never know how strong you are until being strong is your only choice. - Bob Marley",
        "Strength and growth come only through continuous effort and struggle. - Napoleon Hill",
        "The world breaks everyone, and afterward, some are strong at the broken places. - Ernest Hemingway",
        "Difficulties strengthen the mind, as labor does the body. - Seneca"
    ]
}

# Flatten all quotes for random selection
ALL_QUOTES = []
for topic_quotes in QUOTES.values():
    ALL_QUOTES.extend(topic_quotes)

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to DailyMotivationBot\n\n"
        "Send /quote for a random motivational quote\n"
        "Send /topic to get quotes by category\n"
        "Send /help for all commands\n\n"
        "Available topics: success, life, happiness, strength\n\n"
        "Type /quote to get started."
    )
    await update.message.reply_text(welcome_message)

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "DailyMotivationBot Commands\n\n"
        "/quote - Get a random motivational quote\n"
        "/topic - Get a quote by topic\n"
        "/help - Show this message\n\n"
        "Quote Topics:\n"
        "• success\n"
        "• life\n"
        "• happiness\n"
        "• strength\n\n"
        "Example: /topic success"
    )
    await update.message.reply_text(help_message)

# /quote command - random quote
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(ALL_QUOTES)
    response = f"📖 Motivation for you:\n\n{quote}\n\nSend /quote for another or /topic for specific topics."
    await update.message.reply_text(response)

# /topic command - quote by topic
async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user provided a topic
    if not context.args:
        topic_help = (
            "Please specify a topic:\n\n"
            "Available topics:\n"
            "• success\n"
            "• life\n"
            "• happiness\n"
            "• strength\n\n"
            "Example: /topic success"
        )
        await update.message.reply_text(topic_help)
        return
    
    topic = context.args[0].lower()
    
    if topic in QUOTES:
        quote = random.choice(QUOTES[topic])
        response = f"📖 {topic.title()} quote:\n\n{quote}\n\nSend /quote for random or /topic [topic] for another."
        await update.message.reply_text(response)
    else:
        error_message = (
            f"Topic '{topic}' not found.\n\n"
            "Available topics:\n"
            "• success\n"
            "• life\n"
            "• happiness\n"
            "• strength\n\n"
            "Example: /topic success"
        )
        await update.message.reply_text(error_message)

# Handle unknown commands
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Command not recognized.\n\n"
        "Send /help to see all available commands."
    )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred. Please try again or send /help."
        )

# Set bot commands menu
async def post_init(application: Application):
    commands = [
        BotCommand("quote", "Get a random motivational quote"),
        BotCommand("topic", "Get quote by topic (success, life, happiness, strength)"),
        BotCommand("help", "Show all commands"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    print("Starting DailyMotivationBot...")
    print(f"Using token: {TOKEN[:10]}... (hidden)")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("topic", topic_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Set commands menu
    app.post_init = post_init
    
    # Start the bot
    print("Bot is running and ready for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()
