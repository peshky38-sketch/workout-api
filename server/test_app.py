import pytest
from app import app
from models import db


@pytest.fixture()
def client(tmp_path):
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}")
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_create_workout(client):
    response = client.post("/workouts", json={"date": "2026-10-17", "duration_minutes": 30})
    assert response.status_code == 201
    assert client.get("/workouts").status_code == 200


def test_reject_zero_duration(client):
    response = client.post("/workouts", json={"date": "2026-10-17", "duration_minutes": 0})
    assert response.status_code == 400


def test_add_exercise_to_workout(client):
    workout = client.post("/workouts", json={"date": "2026-10-17", "duration_minutes": 30}).json
    exercise = client.post("/exercises", json={
        "name": "Push-ups", "category": "Strength", "equipment_needed": False
    }).json
    response = client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={"reps": 12, "sets": 3}
    )
    assert response.status_code == 201


def test_reject_blank_exercise_name(client):
    response = client.post("/exercises", json={
        "name": "  ", "category": "Strength", "equipment_needed": False
    })
    assert response.status_code == 400


def test_missing_workout_is_404(client):
    assert client.get("/workouts/999").status_code == 404
