import requests
from bs4 import BeautifulSoup as bs


def get_case_url(name, page_number):
    """Функия генерирует ссылку на список дел."""
    search_url = ('https://mos-gorsud.ru/search?formType=shortForm'
                  '&participant='f'"{name}"'
                  '&page='f'{page_number}'
                  )
    return search_url


def cases_search_by_name(name, update, context):
    """Функия получения информации о судебном деле по номеру дела."""
    chat = update.effective_chat

    text = 'запрашиваем информацию'
    context.bot.send_message(chat_id=chat.id,
                             text=text,
                             )

    headers = {'user-agent': 'my-app/0.0.1'}

    page = 1

    try:

        r = requests.get(get_case_url(name, page), headers=headers)

        soup = bs(r.text, "html.parser")

        resultsearch_text = soup.find_all('div', class_='resultsearch_text')[0]
        resultsearch_text_message = [i.text.strip() for i in resultsearch_text]

        table_headers = soup.find_all('th',)
        table_headers_list = [i.text.replace(
            '\n', '').replace('\t', '').strip() for i in table_headers]

        table_content = soup.find_all('td',)
        table_content_list = [i.text.replace(
            '\n', '').replace(
            '\t', '').replace('   ', '').strip() for i in table_content]

        TABLE_LENGHT = 7

        table_content_list = list(
            func_chunks_generators(table_content_list, TABLE_LENGHT)
        )

        result_list = []
        for row_content in table_content_list:
            result_list.append(dict(zip(table_headers_list, row_content)))

        for i, case in enumerate(result_list):
            result_str = ''

            for i in case:

                result_str += (f'{i}: {case[i]} \n')

            context.bot.send_message(chat_id=chat.id,
                                     text=result_str,
                                     )

        text = resultsearch_text_message[0]
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )

        text = f'Показано: {len(result_list)}'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )

    except IndexError:
        text = 'поиск не выдал результатов'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )
        return None
    except Exception:
        text = 'произошла ошибка при запросе информации у сервера'
        context.bot.send_message(chat_id=chat.id,
                                 text=text,
                                 )
        return None


def func_chunks_generators(lst, n):
    """Функия разделения списка на списки длинной n."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


if __name__ == '__main__':

    name = input()
    cases_search_by_name(name)
