from fastapi.testclient import TestClient
import pytest

from src.main import app
from src.fake_db.database import db

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]


@pytest.fixture(autouse=True)
def reset_db():
    db._users = [user.copy() for user in users]
    db._id = len(db._users)

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'unknown@mail.com'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {'name': 'Sergey Sergeev', 'email': 's.s.sergeev@mail.com'}
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    assert response.json() == 3

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    duplicated_user = {'name': 'New Name', 'email': users[0]['email']}
    response = client.post("/api/v1/user", json=duplicated_user)
    assert response.status_code == 409
    assert response.json() == {'detail': 'User with this email already exists'}

def test_delete_user():
    '''Удаление пользователя'''
    email = users[1]['email']
    response = client.delete("/api/v1/user", params={'email': email})
    assert response.status_code == 204

    response_after_delete = client.get("/api/v1/user", params={'email': email})
    assert response_after_delete.status_code == 404