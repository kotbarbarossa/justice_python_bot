import logging

import requests
from bs4 import BeautifulSoup


def case_search(case, name, update, context):
    """Функия получения информации о судебном деле по номеру дела."""
    chat = update.effective_chat

    text = 'Запрашиваем информацию'
    context.bot.send_message(chat_id=chat.id,
                             text=text,
                             )
    headers = {'user-agent': 'my-app/0.0.1'}

    try:
        search_url = ('https://mos-gorsud.ru/search?formType=shortForm'
                      '&caseNumber=' + case + ''
                      '&participant=' + name + ''
                      )

        r = requests.get(search_url, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")
        link_object = soup.find_all('a', class_='detailsLink')
        detail_link = link_object[0]['href']
    except IndexError:
        text = 'Поиск не выдал результатов'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )

    except Exception:
        logging.critical('Ошибка подключения к mos-gorsud {error}')
        text = 'Произошла ошибка при запросе информации у сервера'
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
        list_right = [
            i.text.replace(
                '\n', '').replace(
                    f'{strip}', '').replace(
                        f'{strange_strip}', '').strip() for i in right_info]

        result_dict = dict(zip(list_left, list_right))
        result_str = ''
        for i in result_dict:
            result_str += (f'{i}: {result_dict[i]} \n')
        context.bot.send_message(chat_id=chat.id,
                                 text=result_str,
                                 )
    except Exception:
        logging.critical('Ошибка подключения к mos-gorsud {error}')
        text = 'Ошибка при запросе дополнительной информации у сервера'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )


if __name__ == '__main__':

    logging.basicConfig(
        filename='case_detail_by_number.log',
        format='%(asctime)s - %(name)s - %(levelname)s - LINE: %(lineno)d'
        ' - FUNCTION: %(funcName)s - MESSAGE: %(message)s',
        level=logging.DEBUG,
        filemode='w'
    )
