import logging
import os
import re
from random import randrange

import telegram
from bot_backend_api import request_backend_api
from case_detail_by_number import case_search
from dotenv import load_dotenv
from surname_search import cases_search_by_name, count_case_numbers
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

RETRY_TIME = 60

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BACKEND_TOKEN = os.getenv('Authorization')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

buttons = [
    ["Посмотреть список дел \U00002696 \U0001F50D"],
    ["Посмотреть избранное дело \U00002696 \U0001F4DA"],
    ['Тыкнуть бота']
]


def wake_up(update, context):
    """
    Функция идентификации, добавления пользователя
    и измениния текущих параметров пользователя.
    Отправка приветственных сообщений и статусов.
    """
    chat = update.effective_chat
    name = update.message.chat.first_name
    username = update.message.chat.username
    status_code, response = request_backend_api(
        method='GET',
        chat_id=chat.id,
        backend_token=BACKEND_TOKEN
        )

    statuses = {
        '0': 'подключен через канал межгалактической связи',
        '1': 'внимательно смотрит',
        '2': 'вышел из матрицы',
        '3': 'весь в внимании',
        '4': 'перепрошит новой виндой',
        '5': 'перезапущен и помыт с мылом',
    }
    random_status = randrange(len(statuses))
    status = statuses[str(random_status)]

    if status_code == 404:
        logging.info(
            f'Функция {wake_up.__name__} подключает бота '
            f'для пользователся {username}')
        text = (
            f'Привет {name}.{username}! Это твой персональный помощник бот. '
            'Бот умеет проверять наличие/отсутствие судебных дел! '
            'Введи имя человека чьи судебные дела тебя интересуют. '
            'При появлении новых дел бот пришлет уведомление!'
            'Имя необходимо ввести в формате "Иванов И.И."'
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
                'Пожалуйста веди имя в формате "Иванов И.И."'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        elif not response['case_id']:
            text = (
                f'Бот {status}. '
                f'Отслеживание дел ведется для имени: {response["name"]}! '
                'При появлении новых дел бот пришлет уведомление! '
                'Сохраненного дела нет.'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        elif not response['name']:
            text = (
                f'Бот {status}. Отслеживание дел не ведется. '
                f'Сохраненое дело -> {response["case_id"]}. '
                'Но вообще-то ты не должен видеть это сообщение! '
                'Потому что механика бота не подразумеваеи наличия '
                'сохраненного дела без сохраненного имени!'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        else:
            text = (
                f'Бот {status}. '
                f'Отслеживание дел ведется для имени: {response["name"]}! '
                'При появлении новых дел бот пришлет уведомление! '
                f'Сохраненое дело -> {response["case_id"]}.'
            )
            send_message(update, context, text)
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
    else:
        text = 'Ведутся технические работы. Пожалуйста повтори запрос позже.'
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
        "Посмотреть список дел \U00002696 \U0001F50D": user_cases_list,
        "Посмотреть избранное дело \U00002696 \U0001F4DA": user_favorite_case,
        'Тыкнуть бота': wake_up,
    }

    if command not in commands:
        pattern_name = re.compile(r"([А-ЯЁ][а-яё]+[ ][А-ЯЁ]\.[А-ЯЁ]\.)")
        if pattern_name.match(command):
            text = 'Запрашиваем информацию на сервере.'
            send_message(update, context, text)
            try:
                case_count = count_case_numbers(command)
                data = {
                    'name': command,
                    'number_of_cases': case_count,
                    'case_id': '',
                    'case_url': '',
                    'case_status': '',
                    }
                request_backend_api(
                    method='PUT',
                    chat_id=chat.id,
                    data=data,
                    backend_token=BACKEND_TOKEN)
                text = f'Данные для {command} сохранены'
                send_message(update, context, text)
                logging.info(f'Добавлено имя "{command}".')
            except Exception:
                text = 'Произошла ошибка при запросе информации у сервера'
                send_message(update, context, text)
        else:
            text = ('Для добавления/изменения имени '
                    'нужно следовать шаблону: '
                    'Вввод для имени должен соответствовать -> "Иванов И.И." '
                    )
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
    name = response.get('name')
    if status == 200 and name:
        text = 'Запрашиваем информацию на сервере.'
        send_message(update, context, text)
        try:
            result_count, result_list = cases_search_by_name(name)
            for i, case in enumerate(result_list):
                result_str = ''
                for i in case:
                    result_str += (f'{i}: {case[i]} \n')
                case_id = case['Номер дела ~ материала']
                update_button = InlineKeyboardButton(
                    "Добавить дело в избранное",
                    callback_data=f'{case_id}|{name}')
                reply_markup = InlineKeyboardMarkup([[update_button]])
                update.message.reply_text(
                    result_str, reply_markup=reply_markup)
            text = result_count
            send_message(update, context, text)
            text = f'Показано: {len(result_list)}'
            send_message(update, context, text)
            logging.info(f'Поьзователю {chat.id} отправлен список дел.')
        except Exception:
            text = 'Произошла ошибка при запросе информации у сервера.'
            send_message(update, context, text)
    elif status == 200:
        text = ('Для добавления имени '
                'пожалуйста веди свое имя в формате "Иванов И.И."')
        send_message(update, context, text)
    else:
        logging.critical(
            f'Функция {user_cases_list.__name__} '
            'не получила ожидаемый ответ от backend.')
        text = 'Ведутся технические работы. Пожалуйста повтори запрос позже.'
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
        text = 'Запрашиваем информацию'
        send_message(update, context, text)
        text, detail_url, case_status = case_search(
            response['case_id'], response['name'])
        url_button = InlineKeyboardButton(
            "Посмотреть на сайте", url=detail_url)
        reply_markup = InlineKeyboardMarkup([[url_button]])
        update.message.reply_text(text, reply_markup=reply_markup)
        logging.info(f'Поьзователю {chat.id} отправлено {text}')
    elif status == 200:
        text = ('Для добавления дела в избранное '
                'пожалуйста выбери интересующее тебя дело '
                'в списке дел полученных для введенного имени '
                'и нажми на кнопку "Добавить дело в избранное"')
        send_message(update, context, text)
    else:
        logging.critical(
            f'Функция {user_favorite_case.__name__} '
            'не получила ожидаемый ответ от backend.')
        text = 'Ведутся технические работы. Пожалуйста повтори запрос позже.'
        send_message(update, context, text)


def send_message(update, context, text):
    """Отправка сообщения в чат."""
    chat = update.effective_chat
    text = text
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
            )
    except Exception as error:
        logging.critical(
            f'Функция {send_message.__name__} '
            f'не смогла отправить сообщение. Ошибка: {error}')
        raise AssertionError(f'{error} Ошибка отправки сообщения в телеграм')


def button_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    callback_data_list = callback_data.split('|')
    case_id = callback_data_list[0]
    name = callback_data_list[1]
    text = 'Идет запись. Не выключайте питание.'
    send_message(update, context, text)

    try:
        text, detail_url, case_status = case_search(case_id, name)

        data = {
            'case_id': case_id,
            'case_url': detail_url,
            'case_status': case_status,
            }
        request_backend_api(
            method='PUT',
            chat_id=user_id,
            data=data,
            backend_token=BACKEND_TOKEN)
        text = f'Дело {callback_data} добавлено в избранное!'
        logging.info(f'Добавлено дело "{callback_data}".')
    except Exception as e:
        text = 'Ошибка при добавлении дела в избранное.'
        logging.error(f'Ошибка при добавлении дела в избранное "{e}".')
    finally:
        send_message(update, context, text)


def main():
    """Основная логика работы бота."""
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, parse_text))

    updater.start_polling()

    check_tokens()


if __name__ == '__main__':
    logging.basicConfig(
        filename='justice_bot_main.log',
        format='%(asctime)s - %(name)s - %(levelname)s - LINE: %(lineno)d'
        ' - FUNCTION: %(funcName)s - MESSAGE: %(message)s',
        level=logging.INFO,
        filemode='w'
    )
    main()
