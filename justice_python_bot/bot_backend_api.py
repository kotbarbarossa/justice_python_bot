import requests

HEADERS = {
    # 'Authorization': f'OAuth {backend_token}'
    }


def get_api_answer(chat_id):
    """Get response from backend API."""

    endpoint = f'http://backend:8000/api/v1/telegram_users/{chat_id}/'

    request_params = dict(
        url=endpoint,
        headers=HEADERS,
    )
    try:
        response = requests.get(**request_params)
    except requests.RequestException as error:
        raise ConnectionError(f'Ошибка подключения к backend API {error}')
    status_code = response.status_code
    if status_code == 200:
        return response.json()

    return None


def post_new_user(chat_id):
    """Post new user."""

    endpoint = 'http://backend:8000/api/v1/telegram_users/'

    request_params = dict(
        url=endpoint,
        headers=HEADERS,
        data={'chat_id': chat_id}
    )
    try:
        response = requests.post(**request_params)
    except requests.RequestException as error:
        raise ConnectionError(f'Ошибка подключения к backend API {error}')
    status_code = response.status_code
    if status_code == 201:
        return response.json()

    return status_code


def put_user_info(chat_id, key, value):
    """Update user info."""

    endpoint = f'http://backend:8000/api/v1/telegram_users/{chat_id}/'

    request_params = dict(
        url=endpoint,
        headers=HEADERS,
        data={f'{key}': value}
    )
    try:
        response = requests.patch(**request_params)
    except requests.RequestException as error:
        raise ConnectionError(f'Ошибка подключения к backend API {error}')
    status_code = response.status_code
    if status_code == 200:
        return response.json()

    return status_code


if __name__ == '__main__':

    chat_id = 323124501

    user = get_api_answer(chat_id)
    if not user:
        print('начальное сообщение')
        new_user = post_new_user(chat_id)
        print(f' пользователь создан: {new_user}')
    else:
        print(f'привет опять {chat_id}')

    print(put_user_info(chat_id, 'name', 'Дулин И.И.'))
