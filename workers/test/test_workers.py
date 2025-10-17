import pytest
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.test import APIClient

from workers.models import Worker


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_is_staff(db):
    return User.objects.create_user(
        username="admin", password="testpass123", email="admin@test.com", is_staff=True
    )


@pytest.fixture
def user_not_is_staff(db):
    return User.objects.create_user(
        username="user_test",
        password="testpas123",
        email="user@test.com",
        is_staff=False,
    )


@pytest.fixture
def worker_factory(db):
    def factory(*args, **kwargs):
        return baker.make(Worker, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get(client, user_is_staff, worker_factory):
    client.force_authenticate(user=user_is_staff)

    worker = worker_factory(_quantity=10)
    response = client.get("/api/workers/")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == len(worker)

    worker_data = data["results"][0]
    assert "first_name" in worker_data
    assert "middle_name" in worker_data
    assert "position" in worker_data
    assert "is_active" in worker_data


@pytest.mark.django_db
def test_post_worker(client, user_is_staff):
    client.force_authenticate(user=user_is_staff)

    response = client.post(
        "/api/workers/",
        {
            "first_name": "Саша",
            "last_name": "Кузнецов",
            "email": "s@test.com",
            "position": "Developer",
            "is_active": True,
        },
    )
    assert response.status_code == 201

    data = response.json()

    assert "id" in data

    worker_id = data["id"]
    detail_response = client.get(f"/api/workers/{worker_id}/")
    assert detail_response.status_code == 200

    detail_data = detail_response.json()
    assert data["first_name"] == "Саша"
    assert data["last_name"] == "Кузнецов"
    assert data["middle_name"] == ""
    assert detail_data["is_active"] is True
    assert detail_data["position"] == "Developer"


@pytest.mark.django_db
def test_updata_worker(client, user_is_staff, worker_factory):
    client.force_authenticate(user=user_is_staff)

    worker = worker_factory()

    response = client.patch(
        f"/api/workers/{worker.id}/",
        {"first_name": "Катя", "position": "Developer", "is_active": False},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "Катя"
    assert data["position"] == "Developer"
    assert data["is_active"] is False


@pytest.mark.django_db
def test_delete_worker(client, user_is_staff, worker_factory):
    client.force_authenticate(user=user_is_staff)

    worker = worker_factory()

    response = client.delete(f"/api/workers/{worker.id}/")

    assert response.status_code == 204


@pytest.mark.django_db
def test_post_worker_not_is_staff(client, user_not_is_staff, worker_factory):
    client.force_authenticate(user=user_not_is_staff)

    response = client.post(
        "/api/workers/",
        {
            "first_name": "Саша",
            "last_name": "Кузнецов",
            "email": "test@test.com",
            "position": "Developer",
            "is_active": True,
        },
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_import_workers_excel(client, user_is_staff):
    client.force_authenticate(user=user_is_staff)

    import io

    import pandas as pd

    df = pd.DataFrame(
        {
            "first_name": ["Саша", "Петя"],
            "middle_name": ["Кузецов", "Иванов"],
            "email": ["s@test.com", "p@test.com"],
            "position": ["Developer", "Designer"],
            "is_active": [True, False],
        }
    )

    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False, engine="openpyxl")
    excel_file.name = "workers.xlsx"
    excel_file.seek(0)

    response = client.post("/api/workers/import/", {"file": excel_file})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] == 2

    from workers.models import Worker

    assert Worker.objects.filter(email="s@test.com").exists()
    assert Worker.objects.filter(email="p@test.com").exists()


@pytest.mark.django_db
def test_worker_filtering(client, user_is_staff, worker_factory):
    client.force_authenticate(user=user_is_staff)

    worker_factory(first_name="Саша", is_active=True, position="Developer")
    worker_factory(first_name="Петя", is_active=False, position="Designer")
    worker_factory(first_name="Миша", is_active=True, position="Designer")

    response_active = client.get("/api/workers/?is_active=True")
    assert response_active.status_code == 200
    data_active = response_active.json()
    assert all(w["is_active"] is True for w in data_active["results"])
    assert len(data_active["results"]) == 2

    response_designer = client.get("/api/workers/?position=Designer")
    assert response_designer.status_code == 200
    data_designer = response_designer.json()
    assert all(w["position"] == "Designer" for w in data_designer["results"])
    assert len(data_designer["results"]) == 2

    response_filtered = client.get("/api/workers/?is_active=False&position=Designer")
    assert response_filtered.status_code == 200
    data_filtered = response_filtered.json()
    assert len(data_filtered["results"]) == 1
    assert data_filtered["results"][0]["first_name"] == "Петя"
