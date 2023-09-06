import logging

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    filename='bot_backend_api.log',
    format='%(asctime)s - %(name)s - %(levelname)s - LINE: %(lineno)d'
    ' - FUNCTION: %(funcName)s - MESSAGE: %(message)s',
    level=logging.DEBUG,
    filemode='w'
)


def check_case(case):
    try:
        headers = {'user-agent': 'my-app/0.0.1'}
        search_url = ('https://mos-gorsud.ru/search?formType=shortForm'
                      '&courtAlias=&uid=' + case + ''
                      )
        r = requests.get(search_url, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")
        link_object = soup.find_all('a', class_='detailsLink')
        detail_link = link_object[0]['href']
        return True if detail_link else False
    except Exception:
        logging.critical('шибка подключения к mos-gorsud {error}')
        return False


def case_search(case, update, context):
    """Функия получения информации о судебном деле по номеру дела."""
    chat = update.effective_chat

    text = 'запрашиваем информацию'
    context.bot.send_message(chat_id=chat.id,
                             text=text,
                             )
    headers = {'user-agent': 'my-app/0.0.1'}

    try:
        search_url = ('https://mos-gorsud.ru/search?formType=shortForm'
                      '&courtAlias=&uid=' + case + ''
                      )
        r = requests.get(search_url, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")
        link_object = soup.find_all('a', class_='detailsLink')
        detail_link = link_object[0]['href']
    except IndexError:
        text = 'поиск не выдал результатов'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )

    except Exception:
        logging.critical('шибка подключения к mos-gorsud {error}')
        text = 'произошла ошибка при запросе информации у сервера'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )

    try:
        detail_url = 'https://mos-gorsud.ru' + detail_link
        r = requests.get(detail_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        left_info = soup.find_all(class_="left")
        right_info = soup.find_all(class_="right")
        list_left = [i.text.replace('\n', '').strip() for i in left_info]
        strip = '                                    '
        strange_strip = '   '
        right_left = [
            i.text.replace(
                '\n', '').replace(
                    f'{strip}', '').replace(
                        f'{strange_strip}', '').strip() for i in right_info]

        result_dict = dict(zip(list_left, right_left))
        result_str = ''
        for i in result_dict:
            result_str += (f'{i}: {result_dict[i]} \n')
        context.bot.send_message(chat_id=chat.id,
                                 text=result_str,
                                 )
    except Exception:
        logging.critical('шибка подключения к mos-gorsud {error}')
        text = 'ошибка при запросе дополнительной информации у сервера'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )
