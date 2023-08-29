import requests
import os
from dotenv import load_dotenv
import time
import telegram
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup
import logging
from random import randrange
import datetime as dt

RETRY_TIME = 60

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

buttons = [
    ["Кнопка 1 \U00002696 \U0001F50D", "Кнопка 2 \U00002696 \U0001F4DA"],
]

reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def wake_up(update, context):
    """Отправка сообщения при подключении бота."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    username = update.message.chat.username
    hello = (
        f'Привет {name}.{username}!'
    )
    context.bot.send_message(chat_id=chat.id,
                             text=hello,
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


def main():
    """Основная логика работы бота."""
    UPADTER = Updater(token=TELEGRAM_TOKEN)
    UPADTER.dispatcher.add_handler(CommandHandler('start', wake_up))

    UPADTER.start_polling()

    check_tokens()

    i = 0

    while True:

        print(f'online time: {i} minutes!')
        i += 1

        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
