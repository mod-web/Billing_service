import requests

from tests.conftest import HOST, TEST_ROLE_ID


def test_create_role(get_tokens_for_admin):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens_for_admin["access_token"]}',
    }
    data = {'role': 'test_role'}
    url = f'{HOST}/api/v1/roles/create'
    response = requests.post(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 201


def test_create_role_not_admin(get_tokens):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["access_token"]}',
    }
    data = {'role': 'test_role'}
    url = f'{HOST}/api/v1/roles/create'
    response = requests.post(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 403


def test_delete_role(get_tokens_for_admin, create_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens_for_admin["access_token"]}',
    }
    url = f'{HOST}/api/v1/roles/{TEST_ROLE_ID}'
    response = requests.delete(
        url=url,
        headers=headers,
    )
    assert response.status_code == 200


def test_delete_role_not_admin(get_tokens, create_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["access_token"]}',
    }
    url = f'{HOST}/api/v1/roles/{TEST_ROLE_ID}'
    response = requests.delete(
        url=url,
        headers=headers,
    )
    assert response.status_code == 403


def test_patch_role(get_tokens_for_admin, create_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens_for_admin["access_token"]}',
    }
    data = {'role': 'new_test_role'}
    url = f'{HOST}/api/v1/roles/{TEST_ROLE_ID}'
    response = requests.patch(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 201


def test_patch_role_not_admin(get_tokens, create_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["access_token"]}',
    }
    data = {'role': 'new_test_role'}
    url = f'{HOST}/api/v1/roles/{TEST_ROLE_ID}'
    response = requests.patch(
        url=url,
        json=data,
        headers=headers,
    )
    assert response.status_code == 403


def test_get_roles(get_tokens_for_admin, create_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens_for_admin["access_token"]}',
    }
    url = f'{HOST}/api/v1/roles'
    response = requests.get(
        url=url,
        headers=headers,
    )
    assert response.status_code == 200


def test_get_roles_not_admin(get_tokens, create_role):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["access_token"]}',
    }
    url = f'{HOST}/api/v1/roles'
    response = requests.get(
        url=url,
        headers=headers,
    )
    assert response.status_code == 403
