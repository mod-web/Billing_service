import requests

from tests.conftest import HOST, TEST_USER_ID, TEST_ROLE_ID, TEST_LOGIN, TEST_PASSWORD


def test_add_role_to_user(get_tokens_for_admin, create_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens_for_admin["access_token"]}',
    }
    data = {
        'role_id': TEST_ROLE_ID,
        'user_id': TEST_USER_ID,

    }
    url = f'{HOST}/api/v1/users/apply-role'
    response = requests.post(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 200


def test_delete_role_to_user(get_tokens_for_admin, create_role, create_user_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens_for_admin["access_token"]}',
    }
    data = {
        'role_id': TEST_ROLE_ID,
        'user_id': TEST_USER_ID,
    }
    url = f'{HOST}/api/v1/users/delete-role'
    response = requests.delete(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 200


def test_get_login_history(get_tokens_for_admin):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens_for_admin["access_token"]}',
    }
    url = f'{HOST}/api/v1/users/login-history'
    response = requests.get(
        url=url,
        headers=headers,
    )
    assert response.status_code == 200


def test_change_password(get_tokens):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["access_token"]}',
    }
    data = {'login': TEST_LOGIN, 'old_password': TEST_PASSWORD, 'new_password': 'new_password'}
    url = f'{HOST}/api/v1/users/change-password'
    response = requests.post(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 200


def test_change_login(get_tokens):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["access_token"]}',
    }
    data = {'login': TEST_LOGIN, 'password': TEST_PASSWORD, 'new_login': 'new_login'}
    url = f'{HOST}/api/v1/users/change-login'
    response = requests.post(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 200
