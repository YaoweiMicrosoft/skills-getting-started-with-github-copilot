import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module      # src/app.py
client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Keep the global `activities` dictionary pristine between tests."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities[:] = original  # or assign back

def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data

def test_signup_and_duplicate():
    email = "new@mergington.edu"
    r = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert r.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]

    # second signup should be rejected
    r2 = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert r2.status_code == 400
    assert "already signed up" in r2.json()["detail"]

def test_signup_nonexistent_activity():
    r = client.post("/activities/NoSuch/signup", params={"email": "a@b.com"})
    assert r.status_code == 404

def test_activity_full():
    act = app_module.activities["Chess Club"]
    # fill to max
    act["participants"][:] = [f"user{i}@x" for i in range(act["max_participants"])]
    r = client.post("/activities/Chess%20Club/signup", params={"email": "extra@x"})
    assert r.status_code == 400
    assert "full" in r.json()["detail"]

def test_remove_participant():
    email = "john@mergington.edu"
    # ensure participant exists
    assert email in app_module.activities["Gym Class"]["participants"]
    r = client.delete("/activities/Gym%20Class/signup", params={"email": email})
    assert r.status_code == 200
    assert email not in app_module.activities["Gym Class"]["participants"]

def test_delete_errors():
    r1 = client.delete("/activities/NoSuch/signup", params={"email": "a@b.com"})
    assert r1.status_code == 404

    r2 = client.delete("/activities/Chess%20Club/signup", params={"email": "not@inlist"})
    assert r2.status_code == 404