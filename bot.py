import os
import random
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Ativar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Obter token da variável de ambiente
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Verificar se o token existe
if not TOKEN:
    logger.error("A variável de ambiente TELEGRAM_BOT_TOKEN não está definida!")
    print("ERRO: A variável de ambiente TELEGRAM_BOT_TOKEN não está definida!")
    exit(1)

# Banco de dados de frases organizado por tópicos
QUOTES = {
    "sucesso": [
        "O sucesso não é definitivo, o fracasso não é fatal: o que conta é a coragem para continuar. - Winston Churchill",
        "O único limite para a nossa realização de amanhã são as nossas dúvidas de hoje. - Franklin D. Roosevelt",
        "O sucesso geralmente vem para aqueles que estão ocupados demais para procurá-lo. - Henry David Thoreau",
        "Não olhe para o relógio; faça o que ele faz. Continue andando. - Sam Levenson",
        "O segredo do sucesso é fazer o que é comum de maneira incomum. - John D. Rockefeller Jr."
    ],
    "vida": [
        "A vida é o que acontece enquanto você está ocupado fazendo outros planos. - John Lennon",
        "No final, não são os anos em sua vida que contam. É a vida nos seus anos. - Abraham Lincoln",
        "O propósito das nossas vidas é ser feliz. - Dalai Lama",
        "A vida é muito simples, mas insistimos em torná-la complicada. - Confúcio",
        "Ocupe-se vivendo ou ocupe-se morrendo. - Stephen King"
    ],
    "felicidade": [
        "A felicidade não é algo pronto. Ela vem das suas próprias ações. - Dalai Lama",
        "Para cada minuto que você passa com raiva, você perde sessenta segundos de felicidade. - Ralph Waldo Emerson",
        "A felicidade da sua vida depende da qualidade dos seus pensamentos. - Marcus Aurelius",
        "A felicidade é quando o que você pensa, o que você diz e o que você faz estão em harmonia. - Mahatma Gandhi",
        "O segredo da felicidade é a liberdade. O segredo da liberdade é a coragem. - Tucídides"
    ],
    "forca": [
        "A força não vem da capacidade física. Ela vem de uma vontade indomável. - Mahatma Gandhi",
        "Você nunca sabe quão forte é, até que ser forte seja a sua única escolha. - Bob Marley",
        "A força e o crescimento vêm apenas através do esforço e da luta contínuos. - Napoleon Hill",
        "O mundo quebra a todos, e depois, alguns são mais fortes nos lugares quebrados. - Ernest Hemingway",
        "As dificuldades fortalecem a mente, assim como o trabalho faz com o corpo. - Sêneca"
    ]
}

# Juntar todas as frases para seleção aleatória
ALL_QUOTES = []
for topic_quotes in QUOTES.values():
    ALL_QUOTES.extend(topic_quotes)

# Comando /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Bem-vindo ao DailyMotivationBot\n\n"
        "Envie /quote para receber uma frase motivacional aleatória\n"
        "Envie /topic para receber frases por categoria\n"
        "Envie /help para ver todos os comandos\n\n"
        "Tópicos disponíveis: sucesso, vida, felicidade, forca\n\n"
        "Digite /quote para começar."
    )
    await update.message.reply_text(welcome_message)

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "Comandos do DailyMotivationBot\n\n"
        "/quote - Receba uma frase motivacional aleatória\n"
        "/topic - Receba uma frase por tópico\n"
        "/help - Mostra esta mensagem\n\n"
        "Tópicos de Frases:\n"
        "• sucesso\n"
        "• vida\n"
        "• felicidade\n"
        "• forca\n\n"
        "Exemplo: /topic sucesso"
    )
    await update.message.reply_text(help_message)

# Comando /quote - frase aleatória
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(ALL_QUOTES)
    response = f"📖 Motivação para você:\n\n{quote}\n\nEnvie /quote para outra ou /topic para tópicos específicos."
    await update.message.reply_text(response)

# Comando /topic - frase por tópico
async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar se o usuário forneceu um tópico
    if not context.args:
        topic_help = (
            "Por favor, especifique um tópico:\n\n"
            "Tópicos disponíveis:\n"
            "• sucesso\n"
            "• vida\n"
            "• felicidade\n"
            "• forca\n\n"
            "Exemplo: /topic sucesso"
        )
        await update.message.reply_text(topic_help)
        return
    
    topic = context.args[0].lower()
    
    if topic in QUOTES:
        quote = random.choice(QUOTES[topic])
        response = f"📖 Frase sobre {topic.title()}:\n\n{quote}\n\nEnvie /quote para uma aleatória ou /topic [{topic}] para outra."
        await update.message.reply_text(response)
    else:
        error_message = (
            f"O tópico '{topic}' não foi encontrado.\n\n"
            "Tópicos disponíveis:\n"
            "• sucesso\n"
            "• vida\n"
            "• felicidade\n"
            "• forca\n\n"
            "Exemplo: /topic sucesso"
        )
        await update.message.reply_text(error_message)

# Lidar com comandos desconhecidos
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comando não reconhecido.\n\n"
        "Envie /help para ver todos os comandos disponíveis."
    )

# Gerenciador de erros
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"A atualização {update} causou o erro {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Ocorreu um erro. Por favor, tente novamente ou envie /help."
        )

# Definir o menu de comandos do bot
async def post_init(application: Application):
    commands = [
        BotCommand("quote", "Receba uma frase motivacional aleatória"),
        BotCommand("topic", "Frase por tópico (sucesso, vida, felicidade, forca)"),
        BotCommand("help", "Mostrar todos os comandos"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    print("Iniciando DailyMotivationBot...")
    print(f"Usando o token: {TOKEN[:10]}... (oculto)")
    
    # Criar aplicação
    app = Application.builder().token(TOKEN).build()
    
    # Adicionar manipuladores de comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("topic", topic_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Adicionar gerenciador de erros
    app.add_error_handler(error_handler)
    
    # Definir menu de comandos
    app.post_init = post_init
    
    # Iniciar o bot
    print("O bot está rodando e pronto para receber mensagens...")
    app.run_polling()

if __name__ == "__main__":
    main()
