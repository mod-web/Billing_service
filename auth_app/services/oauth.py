import requests as requests
from flask import redirect

from config import google_config, BASE_HOST, yandex_config
from services.user import user_service


class GoogleOauth:
    """Класс для работы с авторизацией гугла."""
    def __init__(self):
        self.user_service = user_service
        self.client_id = google_config.client_id
        self.secret = google_config.secret
        self.redirect_url = f'{BASE_HOST}api/v1/oauth/redirect/google'
        self.scope = 'email profile openid'
        self.authorization_url = f'https://accounts.google.com/o/oauth2/auth?client_id={self.client_id}&' \
                                 f'scope={self.scope}&state=google' \
                                 f'access_type=offline&response_type=code&redirect_uri={self.redirect_url}&'

    def authorize(self):
        """Редирект на авторизацию в гугле."""
        return redirect(self.authorization_url, code=302)

    def get_tokens(self, code: str) -> dict[str, str]:
        """Получить токены от гугла по коду."""
        return requests.post(
            url='https://oauth2.googleapis.com/token',
            data={
                'client_id': self.client_id,
                'client_secret': self.secret,
                'code': code,
                'redirect_uri': self.redirect_url,
                'grant_type': 'authorization_code',
            }
        ).json()

    def get_user_info(self, code: str) -> dict[str, str]:
        """Получить информацию о юзере гугла по токенам."""
        tokens = self.get_tokens(code)
        return requests.get(
            url='https://www.googleapis.com/userinfo/v2/me',
            headers={'Authorization': f'{tokens["token_type"]} {tokens["access_token"]}'},
        ).json()

    def register(self, user_agent: str, user_info: dict):
        return user_service.register_user_oauth(
            user_agent=user_agent,
            email=user_info['email'],
            oauth_id=user_info['id'],
            oauth_first_name=user_info['given_name'],
            oauth_last_name=user_info['family_name'],
        )


class YandexOauth:
    """Класс для работы с авторизацией яндекса."""
    def __init__(self):
        self.client_id = yandex_config.client_id
        self.secret = yandex_config.secret
        self.authorization_url = f'https://oauth.yandex.ru/authorize?client_id={self.client_id}' \
                                 f'&display=popup&response_type=code&state=yandex'

    def authorize(self):
        """Редирект на авторизацию в яндексе."""
        return redirect(self.authorization_url, code=302)

    def get_tokens(self, code: str) -> dict[str, str]:
        """Получить токены от яндекса по коду."""
        return requests.post(
            url='https://oauth.yandex.ru/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.secret,
                'code': code
            }
        ).json()

    def get_user_info(self, code: str) -> dict[str, str]:
        """Получить информацию о юзере яндекса по токенам."""
        tokens = self.get_tokens(code)
        return requests.get(
            url='https://login.yandex.ru/info?',
            params={
                'Authorization': 'OAuth',
                'oauth_token': tokens['access_token'],
            },
        ).json()

    def register(self, user_agent: str, user_info: dict):
        return user_service.register_user_oauth(
            user_agent=user_agent,
            email=user_info['default_email'],
            oauth_id=user_info['id'],
            oauth_first_name=user_info['first_name'],
            oauth_last_name=user_info['last_name'],
        )


def get_service_instance(service_name: str):
    if service_name == 'google':
        return GoogleOauth()
    if service_name == 'yandex':
        return YandexOauth()
