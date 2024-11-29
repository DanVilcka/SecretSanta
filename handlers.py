import random
import logging
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackContext
from utils import session_scope, save_name, save_wish, update_wish, list_all_participants, list_wish_with_id, add_gift_exchange, clear_gift_exchange, add_gift_exchange_check, list_participant_with_id
from config import ADMIN_USER_IDS

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

WISH_INPUT, WISH_CHANGE, NAME = range(3)

def is_admin(user_id):
    return user_id in ADMIN_USER_IDS

async def distribution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text('У вас нет прав на выполнение этой команды.')
        return
    logger.warning(f'Admin {update.effective_user.id} is trying to distribution the Secret Santa.')
    try:
        with session_scope() as session:
            participants = list_all_participants(session)
            
            if len(participants) < 2:
                await update.effective_message.reply_text('Недостаточно участников для проведения жеребьевки.')
                return

            random.shuffle(participants)
            for i, participant in enumerate(participants):
                recipient = participants[(i + 1) % len(participants)]
                add_gift_exchange(session, participant.user_id, recipient.user_id)
                wish_with_id = list_wish_with_id(session, recipient.user_id)
                await context.bot.send_message(chat_id=participant.user_id, text=f'Ты тайный Санта для: {recipient.name}!\nЖелания:\n{wish_with_id.wish_text}')
                
            await update.effective_message.reply_text('Жеребьевка завершена! Участники получили свои назначения.')

    except Exception as e:
        logger.error(f'Error in /distribution command: {e}')
        await update.effective_message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

    return ConversationHandler.END

async def list_participants(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text('У вас нет прав на выполнение этой команды.')
        return
    logger.warning(f'Admin {update.effective_user.id} is trying to list participants.')
    try:
        with session_scope() as session:
            participants = list_all_participants(session)
            if participants:
                participant_list = "\n".join([f"{p.name} (@{p.username})" for p in participants])
                await context.application.bot.send_message(chat_id=update.effective_chat.id, text=participant_list)
            else:
                await context.application.bot.send_message(chat_id=update.effective_chat.id, text='Нет участников.')
    except Exception as e:
        logger.error(f'Error in /list command: {e}')
        await context.application.bot.send_message(chat_id=update.effective_chat.id, text='Произошла ошибка. Пожалуйста, попробуйте позже.')
    
    return ConversationHandler.END

async def check_distribution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text('У вас нет прав на выполнение этой команды.')
        return
    logger.info(f'Admin {update.effective_user.id} is checking the distribution.')
    try:
        with session_scope() as session:
            clear_gift_exchange(session)

            participants = list_all_participants(session)
            if len(participants) < 2:
                await update.effective_message.reply_text('Недостаточно участников для проведения жеребьевки.')
                return

            random.shuffle(participants)
            distribution_list = []
            for i, participant in enumerate(participants):
                recipient = participants[(i + 1) % len(participants)]
                logger.warning(f'Admin {update.effective_user.id} checking ststus of query {recipient.user_id}')
                wish_with_id = list_wish_with_id(session, recipient.user_id)
                distribution_list.append(f'{participant.name} (@{participant.username}) будет Сантой для {recipient.name} (@{recipient.username}) c желаниями:\n {wish_with_id.wish_text}')
                add_gift_exchange_check(session, participant.user_id, recipient.user_id)

            distribution_text = "\n".join(distribution_list)
            await update.effective_message.reply_text(f'Тестовое распределение:\n{distribution_text}')

    except Exception as e:
        logger.error(f'Error in /check_distribution command: {e}')
        await update.effective_message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Я Бот, который подберет тебе тайного санту!\n"
        "Чтобы закончить разговор отправь /cancel\n\n"
        "Теперь мне необходимы твоё истинное имя и фамилия"
    )
    return NAME

async def name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    with session_scope() as session:
        if not list_participant_with_id(session, user.id):
            save_name(session, user.id, update.message.text, user.username)
        else:
            await update.message.reply_text(
                "Вы уже зарегистрированы на игру!\n"
            )
            return ConversationHandler.END

    await update.message.reply_text(
        "Записал! Перехожу к следующему шагу!\n"
        "Попробуй придумать несколько идей для подарка самому себе!\n"
        "В случае, если совсем ничего не приходит в голову, я советую написать подсказки (свои хобби или интересы)"
    )

    return WISH_INPUT

async def wish_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    wish_text = update.message.text

    try:
        with session_scope() as session:
            save_wish(session, user_id, wish_text)
        await context.application.bot.send_message(chat_id=update.effective_chat.id, text='Ваше желание сохранено!\n')
        
    except ValueError as e:
        await context.application.bot.send_message(chat_id=update.effective_chat.id, text=str(e))

    await update.message.reply_text(
        "Ваша регистрация на игру закончена!\n"
        "Вы можете в любой момент изменить ваши желания по команде /wish_change\n"
    )
    
    return ConversationHandler.END

async def wish_change_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет!\n"
        "Введите выши новые желания!\n"
    )

    return WISH_CHANGE

async def wish_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    new_wish_text = update.message.text
    
    try:
        with session_scope() as session:
            logger.info(f"Click button of updating wish for user {user_id}")
            update_wish(session, user_id, new_wish_text)
        await context.application.bot.send_message(chat_id=update.effective_chat.id, text='Ваше желание обновлено!')
        
    except ValueError as e:
        await context.application.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.warning("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day."
    )

    return ConversationHandler.END