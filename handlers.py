import random
import logging
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models import Participant
from utils import session_scope
from config import ADMIN_USER_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Присоединиться к игре", callback_data='join')],
        [InlineKeyboardButton("Покинуть игру", callback_data='leave')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет! Это бот для игры в Тайного Санту.', reply_markup=reply_markup)

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f'User {user.id} ({user.first_name}) is trying to join the game.')
    try:
        with session_scope() as session:
            participant = session.query(Participant).filter_by(user_id=user.id).first()
            if not participant:
                participant = Participant(user_id=user.id, name=user.first_name, username=user.username)
                session.add(participant)
                await update.effective_message.reply_text(f'{user.first_name}, вы присоединились к игре!')
            else:
                await update.effective_message.reply_text('Вы уже присоединились к игре.')
    except Exception as e:
        logger.error(f'Error in /join command: {e}')
        await update.effective_message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f'User {user.id} ({user.first_name}) is trying to leave the game.')
    try:
        with session_scope() as session:
            participant = session.query(Participant).filter_by(user_id=user.id).first()
            if participant:
                session.delete(participant)
                await update.effective_message.reply_text(f'{user.first_name}, вы покинули игру.')
            else:
                await update.effective_message.reply_text('Вы не участвуете в игре.')
    except Exception as e:
        logger.error(f'Error in /leave command: {e}')
        await update.effective_message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text('У вас нет прав на выполнение этой команды.')
        return
    logger.info(f'Admin {update.effective_user.id} is trying to draw the Secret Santa.')
    try:
        with session_scope() as session:
            participants = session.query(Participant).all()
            if len(participants) < 2:
                await update.effective_message.reply_text('Недостаточно участников для проведения жеребьевки.')
                return

            random.shuffle(participants)
            for i, participant in enumerate(participants):
                participant.recipient_id = participants[(i + 1) % len(participants)].user_id

            for participant in participants:
                await context.bot.send_message(chat_id=participant.user_id, text=f'Ты тайный Санта для: {participant.recipient.name}')

            await update.effective_message.reply_text('Жеребьевка завершена! Участники получили свои назначения.')
    except Exception as e:
        logger.error(f'Error in /draw command: {e}')
        await update.effective_message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

async def list_participants(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text('У вас нет прав на выполнение этой команды.')
        return
    logger.info(f'Admin {update.effective_user.id} is trying to list participants.')
    try:
        with session_scope() as session:
            participants = session.query(Participant).all()
            if participants:
                participant_list = "\n".join([f"{p.name} (@{p.username})" for p in participants])
                await update.effective_message.reply_text(f'Участники:\n{participant_list}')
            else:
                await update.effective_message.reply_text('Нет участников.')
    except Exception as e:
        logger.error(f'Error in /list command: {e}')
        await update.effective_message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

async def check_distribution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text('У вас нет прав на выполнение этой команды.')
        return
    logger.info(f'Admin {update.effective_user.id} is checking the distribution.')
    try:
        with session_scope() as session:
            participants = session.query(Participant).all()
            if len(participants) < 2:
                await update.effective_message.reply_text('Недостаточно участников для проведения жеребьевки.')
                return

            random.shuffle(participants)
            distribution_list = []
            for i, participant in enumerate(participants):
                recipient = participants[(i + 1) % len(participants)]
                distribution_list.append(f'{participant.name} (@{participant.username}) будет Сантой для {recipient.name} (@{recipient.username})')

            distribution_text = "\n".join(distribution_list)
            await update.effective_message.reply_text(f'Тестовое распределение:\n{distribution_text}')
    except Exception as e:
        logger.error(f'Error in /check_distribution command: {e}')
        await update.effective_message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'join':
        await join(update, context)
    elif query.data == 'leave':
        await leave(update, context)