import logging
import os
# import datetime as dt
import re
import time
from random import randrange

import telegram
from bot_backend_api import get_api_answer, post_new_user, put_user_info
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
    logging.info(
        f'Функция {wake_up.__name__} подключает бота '
        f'для пользователся {update.message.chat.username}')
    chat = update.effective_chat
    name = update.message.chat.first_name
    username = update.message.chat.username
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    user = get_api_answer(chat.id, BACKEND_TOKEN)

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

    if not user:
        hello = (
            f'Привет {name}.{username}! Это твой персональный приватный бот. '
            f'Он закреплен за твоим пользователем: ({chat.id})!'
            f'Пожалуйста веди свое имя в формате "Иванов И.И."'
        )
        context.bot.send_message(chat_id=chat.id,
                                 text=hello,
                                 reply_markup=reply_markup
                                 )
        logging.info(f'Пользователь {name}.{username} активировал бота')
        post_new_user(chat.id, BACKEND_TOKEN)

    else:
        if not user['name'] and not user['case_id']:
            hello_again = (
                f'Бот {status}. Отслеживание дел не ведется.'
                'Пожалуйста веди свое имя в формате "Иванов И.И."'
            )
            context.bot.send_message(chat_id=chat.id,
                                     text=hello_again,
                                     reply_markup=reply_markup
                                     )
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        elif not user['case_id']:
            hello_again = (
                f'Бот {status}. '
                f'Отслеживание дел ведется для имени: {user["name"]}! '
                'Сохраненного дела нет.'
            )
            context.bot.send_message(chat_id=chat.id,
                                     text=hello_again,
                                     reply_markup=reply_markup
                                     )
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        elif not user['name']:
            hello_again = (
                f'Бот {status}. Отслеживание дел не ведется. '
                f'Сохраненое дело -> {user["case_id"]}.'
            )
            context.bot.send_message(chat_id=chat.id,
                                     text=hello_again,
                                     reply_markup=reply_markup
                                     )
            logging.info(f'Пользователь {name}.{username} тыкнул бота')
        else:
            hello_again = (
                f'Бот {status}. '
                f'Отслеживание дел ведется для имени: {user["name"]}! '
                f'Сохраненое дело -> {user["case_id"]}.'
            )
            context.bot.send_message(chat_id=chat.id,
                                     text=hello_again,
                                     reply_markup=reply_markup
                                     )
            logging.info(f'Пользователь {name}.{username} тыкнул бота')


def check_tokens():
    """Функия проверяет наличие токенов."""
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

    # global buttons

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

            put_user_info(chat.id, 'name', command, BACKEND_TOKEN)
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            text = f'Данные для {command} сохранены'
            context.bot.send_message(chat_id=chat.id,
                                     text=text,
                                     reply_markup=reply_markup
                                     )
            logging.info(f'Добавлено имя "{command}".')
        elif pattern_case.match(command):
            text = 'запрашиваем информацию на сервере'
            context.bot.send_message(chat_id=chat.id,
                                     text=text,
                                     )
            if check_case(command):
                put_user_info(chat.id, 'case_id', command, BACKEND_TOKEN)
                reply_markup = ReplyKeyboardMarkup(
                    buttons,
                    resize_keyboard=True)
                text = f'Дело {command} добавлено в избранное!'
                context.bot.send_message(chat_id=chat.id,
                                         text=text,
                                         reply_markup=reply_markup
                                         )
                logging.info(f'Добавлено дело "{command}".')

            else:
                text = ('Дела с таким номером не существует! \n'
                        'Дело не было добавлено в избранное')
                context.bot.send_message(chat_id=chat.id,
                                         text=text,
                                         )

        else:
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
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
        commands[command](update, context)


def user_cases_list(update, context):
    """Функция для вывода списка дел."""
    chat = update.effective_chat
    name = get_api_answer(chat.id, BACKEND_TOKEN)
    if name['name']:
        cases_search_by_name(name['name'], update, context)
        logging.info(f'Поьзователю {chat.id} отправлен список дел.')
    else:
        text = ('Для добавления имени '
                'пожалуйста веди свое имя в формате "Иванов И.И."')
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )


def user_favorite_case(update, context):
    """Функция для вывода избранного дела."""
    chat = update.effective_chat
    case_id = get_api_answer(chat.id, BACKEND_TOKEN)
    if case_id['case_id']:
        case_search(case_id['case_id'], update, context)
        logging.info(f'Поьзователю {chat.id} отправлено сохраненное дело.')
    else:
        text = ('Для добавления номера дела '
                'пожалуйста веди номер дела в формате -> '
                '"77RS0020-01-2018-016832-97"')
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )


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
        level=logging.DEBUG,
        filemode='w'
    )
    main()
