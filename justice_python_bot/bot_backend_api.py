import logging

import requests

logging.basicConfig(
    filename='bot_backend_api.log',
    format='%(asctime)s - %(name)s - %(levelname)s - LINE: %(lineno)d'
    ' - FUNCTION: %(funcName)s - MESSAGE: %(message)s',
    level=logging.DEBUG,
    filemode='w'
)


def get_headers(backend_token):
    return {
        'Authorization': f'{backend_token}'
        }


def get_api_answer(chat_id, backend_token):
    """Get response from backend API."""

    endpoint = f'http://backend:8000/api/v1/telegram_users/{chat_id}/'

    request_params = dict(
        url=endpoint,
        headers=get_headers(backend_token),
    )
    try:
        response = requests.get(**request_params)
    except requests.RequestException as error:
        logging.critical('шибка подключения к backend API {error}')
        raise ConnectionError(f'Ошибка подключения к backend API {error}')
    status_code = response.status_code
    if status_code == 200:
        return response.json()

    return None


def post_new_user(chat_id, backend_token):
    """Post new user."""

    endpoint = 'http://backend:8000/api/v1/telegram_users/'

    request_params = dict(
        url=endpoint,
        headers=get_headers(backend_token),
        data={'chat_id': chat_id}
    )
    try:
        response = requests.post(**request_params)
    except requests.RequestException as error:
        logging.critical('шибка подключения к backend API {error}')
        raise ConnectionError(f'Ошибка подключения к backend API {error}')
    status_code = response.status_code
    if status_code == 201:
        return response.json()

    return status_code


def put_user_info(chat_id, key, value, backend_token):
    """Update user info."""

    endpoint = f'http://backend:8000/api/v1/telegram_users/{chat_id}/'

    request_params = dict(
        url=endpoint,
        headers=get_headers(backend_token),
        data={f'{key}': value}
    )
    try:
        response = requests.patch(**request_params)
    except requests.RequestException as error:
        logging.critical('шибка подключения к backend API {error}')
        raise ConnectionError(f'Ошибка подключения к backend API {error}')
    status_code = response.status_code
    if status_code == 200:
        return response.json()

    return status_code


if __name__ == '__main__':

    chat_id = 'num'
    backend_token = 'token'

    user = get_api_answer(chat_id, backend_token)
    if not user:
        print('начальное сообщение')
        new_user = post_new_user(chat_id)
        print(f' пользователь создан: {new_user}')
    else:
        print(f'привет опять {chat_id}')

    print(put_user_info(chat_id, 'name', 'Дулин И.И.'))
