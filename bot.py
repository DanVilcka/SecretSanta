from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from telegram import Update
from config import BOT_TOKEN
from models import create_tables
from handlers import start, cancel, distribution, list_participants, check_distribution, wish_input, wish_change, name_input, wish_change_start, WISH_INPUT, WISH_CHANGE, NAME

def main() -> None:
    create_tables()

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler_registration = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_input)],
            WISH_INPUT:[MessageHandler(filters.TEXT & ~filters.COMMAND, wish_input)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_update = ConversationHandler(
        entry_points=[CommandHandler('wish_change', wish_change_start)],
        states={
            WISH_CHANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wish_change)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # application.add_handler(conv_handler_registration)
    application.add_handler(conv_handler_update)

    application.add_handler(CommandHandler("distribution", distribution))
    application.add_handler(CommandHandler("list", list_participants))
    application.add_handler(CommandHandler("check", check_distribution))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()