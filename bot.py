from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from models import create_tables
from handlers import start, join, leave, draw, list_participants, check_distribution, button

def main() -> None:
    create_tables()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("leave", leave))
    application.add_handler(CommandHandler("draw", draw))
    application.add_handler(CommandHandler("list", list_participants))
    application.add_handler(CommandHandler("check_distribution", check_distribution))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()