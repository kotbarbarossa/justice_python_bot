import logging

import requests


def request_backend_api(*args, **kwargs):

    method = kwargs.get('method')
    chat_id = kwargs.get('chat_id')
    backend_token = kwargs.get('backend_token')
    data = kwargs.get('data')

    headers = {
        'Authorization': f'{backend_token}'
        }

    endpoint = 'http://backend:8000/api/v1/telegram_users/'

    request_params = dict(
        url=endpoint,
        headers=headers,
    )
    try:
        if method == 'GET':
            endpoint += str(chat_id)+'/'
            request_params['url'] = endpoint
            response = requests.get(**request_params)

        elif method == 'POST':
            request_params['data'] = {'chat_id': chat_id}
            response = requests.post(**request_params)

        elif method == 'PUT':
            endpoint += str(chat_id)+'/'
            request_params['url'] = endpoint
            request_params['data'] = data
            response = requests.patch(**request_params)
        status_code = response.status_code
        return status_code, response.json()
    except requests.RequestException as error:
        logging.critical(f'Ошибка подключения к backend API {error}')
        return None, None
        # raise ConnectionError(f'Ошибка подключения к backend API {error}')


if __name__ == '__main__':

    logging.basicConfig(
        filename='bot_backend_api.log',
        format='%(asctime)s - %(name)s - %(levelname)s - LINE: %(lineno)d'
        ' - FUNCTION: %(funcName)s - MESSAGE: %(message)s',
        level=logging.INFO,
        filemode='w'
    )
