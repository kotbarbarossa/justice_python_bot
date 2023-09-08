import logging
import os
# import datetime as dt
import re
import time
from random import randrange

import telegram
from bot_backend_api import request_backend_api
from case_detail_by_number import case_search, check_case
from dotenv import load_dotenv
from surname_search import cases_search_by_name
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

RETRY_TIME = 60

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BACKEND_TOKEN = os.getenv('Authorization')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

buttons = [
    ["Прсмртеть список дел \U00002696 \U0001F50D"],
    ["Посмотреть избранное дело \U00002696 \U0001F4DA"],
    ['Тыкнуть бота']
]


def wake_up(update, context):
    """Отправка сообщения при подключении бота."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    username = update.message.chat.username
    status_code, response = request_backend_api(
        method='GET',
        chat_id=chat.id,
        backend_token=BACKEND_TOKEN
        )

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

    if status_code == 404:
        logging.info(
            f'Функция {wake_up.__name__} подключает бота '
            f'для пользователся {update.message.chat.username}')
        text = (
            f'Привет {name}.{username}! Это твой персональный приватный бот. '
            f'Он закреплен за твоим пользователем: ({chat.id})!'
            f'Пожалуйста веди свое имя в формате "Иванов И.И."'
        )
        send_message(update, context, text)
        logging.info(f'Пользователь {name}.{username} активировал бота')
        request_backend_api(
            method='POST',
            chat_id=chat.id,
            backend_token=BACKEND_TOKEN
            )

    elif status_code in {200, 201}:
        if not response['name'] and not response['case_id']:
            text = (
                f'Бот {status}. Отслеживание дел не ведется.'
                'Пожалуйста веди свое имя в формате "Иванов И.И."'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        elif not response['case_id']:
            text = (
                f'Бот {status}. '
                f'Отслеживание дел ведется для имени: {response["name"]}! '
                'Сохраненного дела нет.'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        elif not response['name']:
            text = (
                f'Бот {status}. Отслеживание дел не ведется. '
                f'Сохраненое дело -> {response["case_id"]}.'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        else:
            text = (
                f'Бот {status}. '
                f'Отслеживание дел ведется для имени: {response["name"]}! '
                f'Сохраненое дело -> {response["case_id"]}.'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
    else:
        text = 'Ведутся технические работы. Пожалуйста повторите запрос позже.'
        send_message(update, context, text)


def check_tokens():
    """Функия проверки наличия токенов."""
    logging.info('Проверка токенов')
    flag = True
    tokens = [
        TELEGRAM_TOKEN,
        BACKEND_TOKEN,
    ]
    for token in tokens:
        if token is None:
            flag = False
            logging.critical('Ошибка проверки токенов')
    return flag


def parse_text(update, context):
    """Разбор сообщений пользователя."""
    chat = update.effective_chat
    command = update.message.text
    logging.info(f'В функцию parse_text пришел запрос "{command}".')

    commands = {
        "Прсмртеть список дел \U00002696 \U0001F50D": user_cases_list,
        "Посмотреть избранное дело \U00002696 \U0001F4DA": user_favorite_case,
        'Тыкнуть бота': wake_up,
    }

    if command not in commands:
        pattern_name = re.compile(r"([А-ЯЁ][а-яё]+[ ][А-ЯЁ]\.[А-ЯЁ]\.)")
        pattern_case = re.compile(
            r"(\d\d[A-Z][A-Z]\d\d\d\d[-]\d\d[-]\d\d\d\d[-]\d\d\d\d\d\d[-]\d\d)"
            )
        if pattern_name.match(command):
            data = {'name': command}
            request_backend_api(
                method='PUT',
                chat_id=chat.id,
                data=data,
                backend_token=BACKEND_TOKEN)
            text = f'Данные для {command} сохранены'
            send_message(update, context, text)
            logging.info(f'Добавлено имя "{command}".')
        elif pattern_case.match(command):
            text = 'запрашиваем информацию на сервере'
            send_message(update, context, text)
            if check_case(command):
                data = {'case_id': command}
                request_backend_api(
                    method='PUT',
                    chat_id=chat.id,
                    data=data,
                    backend_token=BACKEND_TOKEN)
                text = f'Дело {command} добавлено в избранное!'
                send_message(update, context, text)
                logging.info(f'Добавлено дело "{command}".')

            else:
                text = ('Дела с таким номером не существует! \n'
                        'Дело не было добавлено в избранное')
                send_message(update, context, text)

        else:
            text = ('Для добавления/изменения имени или номера дела '
                    'нужно следовать шаблону: '
                    'Вввод для имени должен соответствовать -> "Иванов И.И.". '
                    'Вввод для номера дела должен соответствовать -> '
                    '"77RS0020-01-2018-016832-97"')
            send_message(update, context, text)

    else:
        commands[command](update, context)


def user_cases_list(update, context):
    """Функция для вывода списка дел по ФИО."""
    chat = update.effective_chat
    status, response = request_backend_api(
        method='GET',
        chat_id=chat.id,
        backend_token=BACKEND_TOKEN
        )
    if status == 200 and response['name']:
        cases_search_by_name(response['name'], update, context)
        logging.info(f'Поьзователю {chat.id} отправлен список дел.')
    elif status == 200:
        text = ('Для добавления имени '
                'пожалуйста веди свое имя в формате "Иванов И.И."')
        send_message(update, context, text)
    else:
        logging.critical(
            f'Функция {user_cases_list.__name__} '
            'не получила ожидаемый ответ от backend.')
        text = 'Ведутся технические работы. Пожалуйста повторите запрос позже.'
        send_message(update, context, text)


def user_favorite_case(update, context):
    """Функция для вывода избранного дела но номеру дела."""
    chat = update.effective_chat
    status, response = request_backend_api(
        method='GET',
        chat_id=chat.id,
        backend_token=BACKEND_TOKEN
        )
    if status == 200 and response['case_id']:
        case_search(response['case_id'], update, context)
        logging.info(f'Поьзователю {chat.id} отправлено сохраненное дело.')
    elif status == 200:
        text = ('Для добавления номера дела '
                'пожалуйста веди номер дела в формате -> '
                '"77RS0020-01-2018-016832-97"')
        send_message(update, context, text)
    else:
        logging.critical(
            f'Функция {user_favorite_case.__name__} '
            'не получила ожидаемый ответ от backend.')
        text = 'Ведутся технические работы. Пожалуйста повторите запрос позже.'
        send_message(update, context, text)


def send_message(update, context, text):
    chat = update.effective_chat
    text = text
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=reply_markup
            )
    except Exception as error:
        logging.critical(
            f'Функция {send_message.__name__} '
            f'не смогла отправить сообщение. Ошибка: {error}')
        raise AssertionError(f'{error} Ошибка отправки сообщения в телеграм')


def main():
    """Основная логика работы бота."""
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, parse_text))

    updater.start_polling()

    check_tokens()

    i = 0

    while True:

        print(f'online time: {i} minutes!')
        i += 1

        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        filename='justice_bot_main.log',
        format='%(asctime)s - %(name)s - %(levelname)s - LINE: %(lineno)d'
        ' - FUNCTION: %(funcName)s - MESSAGE: %(message)s',
        level=logging.INFO,
        filemode='w'
    )
    main()
