# import requests
import os
from dotenv import load_dotenv
import time
import telegram
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup
# import logging
from random import randrange
# import datetime as dt
import re

RETRY_TIME = 60

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OWNER_CHAT_ID = None
OWNER_NAME = None
OWNER_CASE = None

bot = telegram.Bot(token=TELEGRAM_TOKEN)

buttons = [
    ["Прсмртеть список дел \U00002696 \U0001F50D"],
    ["Посмотреть избранное дело \U00002696 \U0001F4DA"],
    ['Тыкнуть бота']
]

reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def wake_up(update, context):
    """Отправка сообщения при подключении бота."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    username = update.message.chat.username
    global OWNER_CHAT_ID

    if OWNER_CHAT_ID is not None and OWNER_CHAT_ID != chat.id:
        text = 'You dont have permisson to use this bot!'
        return context.bot.send_message(chat_id=chat.id, text=text,)

    random_status = randrange(6)
    statuses = {
        '0': 'подключен черз канал межгалактической связи',
        '1': 'внимательно смотрит',
        '2': 'вышел из матрицы',
        '3': 'весь в внимании',
        '4': 'перепрошит новой виндой',
        '5': 'перезапущен и помыт с мылом',
    }
    status = statuses[str(random_status)]

    if OWNER_CHAT_ID is None:
        hello = (
            f'Привет {name}.{username}! Это твой персональный приватный бот. '
            f'Он закреплен за твоим пользователем: ({chat.id})!'
            f'Пожалуйста веди свое имя в формате "Иванов И.И."'
        )
        context.bot.send_message(chat_id=chat.id,
                                 text=hello,
                                 )

        OWNER_CHAT_ID = chat.id

    else:
        if OWNER_NAME is None:
            hello_again = (
                f'Бот {status}. Отслеживание дел не ведется.'
                'Пожалуйста веди свое имя в формате "Иванов И.И."'
            )
            context.bot.send_message(chat_id=chat.id,
                                     text=hello_again,
                                     )

        else:
            hello_again = (
                f'Бот {status}. '
                f'Отслеживание дел ведется для имени: {OWNER_NAME}! '
                f'Сохраненое дело -> {OWNER_CASE}.'
            )
            context.bot.send_message(chat_id=chat.id,
                                     text=hello_again,
                                     reply_markup=reply_markup
                                     )


def check_tokens():
    """Функия проверяет наличие токенов."""
    flag = True
    tokens = [
        TELEGRAM_TOKEN,
    ]
    for token in tokens:
        if token is None:
            flag = False
    return flag


def parse_text(update, context):
    """Разбор сообщений пользователя."""
    chat = update.effective_chat
    command = update.message.text
    global OWNER_NAME
    global OWNER_CASE

    if OWNER_CHAT_ID is not None and OWNER_CHAT_ID != chat.id:
        text = 'You dont have permisson to use this bot!'
        return context.bot.send_message(chat_id=chat.id, text=text,)

    COMMANDS = {
        "Прсмртеть список дел \U00002696 \U0001F50D": user_cases_list,
        "Посмотреть избранное дело \U00002696 \U0001F4DA": user_favorite_case,
        'Тыкнуть бота': wake_up,
    }

    if command not in COMMANDS:
        pattern_name = re.compile(r"([А-ЯЁ][а-яё]+[ ][А-ЯЁ]\.[А-ЯЁ]\.)")
        pattern_case = re.compile(
            r"(\d\d[A-Z][A-Z]\d\d\d\d[-]\d\d[-]\d\d\d\d[-]\d\d\d\d\d\d[-]\d\d)"
            )
        if pattern_name.match(command):
            OWNER_NAME = command
            text = f'Данные для {OWNER_NAME} сохранены'
            context.bot.send_message(chat_id=chat.id,
                                     text=text,
                                     reply_markup=reply_markup
                                     )
        elif pattern_case.match(command):
            OWNER_CASE = command
            text = f'Дело {OWNER_CASE} добавлено в избранное!'
            context.bot.send_message(chat_id=chat.id,
                                     text=text,
                                     reply_markup=reply_markup
                                     )
        else:
            text = ('Для добавления/изменения имени или номера дела '
                    'нужно следовать шаблону: '
                    'Вввод для имени должен соответствовать -> "Иванов И.И.". '
                    'Вввод для номера дела должен соответствовать -> '
                    '"77RS0020-01-2018-016832-97"')
            context.bot.send_message(chat_id=chat.id,
                                     text=text,
                                     reply_markup=reply_markup
                                     )

    else:
        COMMANDS[command](update, context)


def user_cases_list(update, context):
    """Функция для вывода списка дел."""
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=f'тут будет список для {OWNER_NAME}',
                             reply_markup=reply_markup
                             )


def user_favorite_case(update, context):
    """Функция для вывода избранного дела."""
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=f'тут будет информация о деле {OWNER_CASE}',
                             reply_markup=reply_markup
                             )


def main():
    """Основная логика работы бота."""
    UPADTER = Updater(token=TELEGRAM_TOKEN)
    UPADTER.dispatcher.add_handler(CommandHandler('start', wake_up))
    UPADTER.dispatcher.add_handler(MessageHandler(Filters.text, parse_text))

    UPADTER.start_polling()

    check_tokens()

    i = 0

    while True:

        print(f'online time: {i} minutes!')
        i += 1

        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
