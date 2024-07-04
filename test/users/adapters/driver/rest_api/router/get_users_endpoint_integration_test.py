import typing

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.users.domain.factories import get_users_case
from app.users.domain.ports.driver import GetUsersUseCase
from app.users.domain import User
from faker import Faker


@pytest.fixture
def client_factory(application: FastAPI) -> typing.Callable[..., TestClient]:
    def factory(get_users_use_case: typing.Callable[..., GetUsersUseCase]):
        application.dependency_overrides[get_users_case] = get_users_use_case
        return TestClient(application)
    yield factory
    application.dependency_overrides = {}


def generate_fake_user(faker: Faker) -> dict:
    return {
        "identifier": str(faker.uuid4()),
        "name": faker.name(),
        "lastname": faker.last_name(),
        "age": faker.pyint(min_value=1, max_value=90),
        "email": faker.email(),
    }


class TestGetUsers:

    def test__should_return_an_user_array(
        self,
        faker: Faker,
        client_factory: typing.Callable[..., TestClient]
    ) -> None:
        class FakeGetUsersUseCase(GetUsersUseCase):
            def handle(self) -> typing.List[User]:
                return [
                    User(**first_user),
                    User(**second_user)
                ]

        first_user = generate_fake_user(faker)
        second_user = generate_fake_user(faker)
        expected_data = [first_user, second_user]

        client = client_factory(get_users_use_case=FakeGetUsersUseCase)
        response = client.get(url="/users")

        assert response.status_code == 200
        assert response.json() == expected_data
