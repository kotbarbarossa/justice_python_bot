import logging

import requests
from bs4 import BeautifulSoup


def get_case_url(name, page_number):
    """Функия генерирует ссылку на список дел."""
    return ('https://mos-gorsud.ru/search?formType=shortForm'
            '&participant='f'"{name}"'
            '&page='f'{page_number}'
            )


def cases_search_by_name(name):
    """Функия получения информации о судебном деле по ФИО."""

    headers = {'user-agent': 'my-app/0.0.1'}

    page = 1

    try:

        r = requests.get(get_case_url(name, page), headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")

        resultsearch_text = soup.find_all('div', class_='resultsearch_text')[0]
        resultsearch_text_message = [i.text.strip() for i in resultsearch_text]

        table_headers = soup.find_all('th',)
        table_headers_list = [i.text.replace(
            '\n', '').replace('\t', '').strip() for i in table_headers]

        table_content = soup.find_all('td',)
        table_content_list = [i.text.replace(
            '\n', '').replace(
            '\t', '').replace('   ', '').strip() for i in table_content]

        table_lenght: int = 7

        table_content_list = list(
            func_chunks_generators(table_content_list, table_lenght)
        )

        result_list = []
        for row_content in table_content_list:
            result_list.append(dict(zip(table_headers_list, row_content)))
        return resultsearch_text_message[0], result_list

    except IndexError:
        logging.critical('Поиск не выдал результатов')

    except Exception as error:
        logging.critical(
            f'Произошла ошибка при запросе информации у сервера {error}')


def count_case_numbers(name):
    """Функия получения информации о количестве дел."""
    headers = {'user-agent': 'my-app/0.0.1'}

    page = 1

    try:
        r = requests.get(get_case_url(name, page), headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        table_content = soup.find_all('td',)

        table_lenght: int = 7

        return len(table_content) // table_lenght

    except Exception as error:
        logging.critical(
            f'Произошла ошибка при запросе информации у сервера {error}')


def func_chunks_generators(lst, n):
    """Функия разделения списка на списки длинной n."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


if __name__ == '__main__':

    logging.basicConfig(
        filename='surname_search.log',
        format='%(asctime)s - %(name)s - %(levelname)s - LINE: %(lineno)d'
        ' - FUNCTION: %(funcName)s - MESSAGE: %(message)s',
        level=logging.INFO,
        filemode='w'
    )

    name = input()
    result_count, result_list = cases_search_by_name(name)
    for i, case in enumerate(result_list):
        result_str = ''

        for i in case:

            result_str += (f'{i}: {case[i]} \n')
        print(result_str)
    print(result_count)
