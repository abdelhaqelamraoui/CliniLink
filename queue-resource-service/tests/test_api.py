import asyncio
import uuid

from app.consumer import process_message
from tests.conftest import DAY, booked, token


async def seed(doctor, patients_and_times):
    for patient, start in patients_and_times:
        await process_message(*booked(uuid.uuid4(), 1, patient, doctor, start))


async def test_requests_without_token_get_problem_details(client):
    r = await client.get(f"/api/v1/queues/doctors/{uuid.uuid4()}", headers={"X-Correlation-ID": "abc-123"})
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["code"] == "UNAUTHORIZED" and body["correlation_id"] == "abc-123"


async def test_patient_sees_anonymized_queue_ordered_by_time(client):
    doctor, me, other = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    await seed(doctor, [(other, "09:00"), (me, "09:30")])
    r = await client.get(f"/api/v1/queues/doctors/{doctor}?date={DAY}", headers=token(me, "PATIENT"))
    assert r.status_code == 200
    body = r.json()
    assert body["waiting_count"] == 2
    assert [e["position"] for e in body["waiting"]] == [1, 2]
    assert [e["is_mine"] for e in body["waiting"]] == [False, True]
    assert all("patient_id" not in e for e in body["waiting"])


async def test_doctor_sees_patient_ids_in_own_queue(client):
    doctor, patient = uuid.uuid4(), uuid.uuid4()
    await seed(doctor, [(patient, "09:00")])
    r = await client.get(f"/api/v1/queues/doctors/{doctor}?date={DAY}", headers=token(doctor, "DOCTOR"))
    assert r.json()["waiting"][0]["patient_id"] == str(patient)


async def test_empty_day_returns_empty_queue(client):
    r = await client.get(f"/api/v1/queues/doctors/{uuid.uuid4()}?date={DAY}", headers=token(uuid.uuid4(), "PATIENT"))
    assert r.status_code == 200 and r.json()["queue_id"] is None and r.json()["waiting"] == []


async def test_call_next_flow_and_permissions(client):
    doctor, p1, p2 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    await seed(doctor, [(p2, "10:00"), (p1, "09:00")])
    queue_id = (await client.get(f"/api/v1/queues/doctors/{doctor}?date={DAY}", headers=token(doctor, "DOCTOR"))).json()["queue_id"]

    # a patient or another doctor cannot call patients
    assert (await client.post(f"/api/v1/queues/{queue_id}/call-next", headers=token(p1, "PATIENT"))).status_code == 403
    assert (await client.post(f"/api/v1/queues/{queue_id}/call-next", headers=token(uuid.uuid4(), "DOCTOR"))).status_code == 403

    r = await client.post(f"/api/v1/queues/{queue_id}/call-next", headers=token(doctor, "DOCTOR"))
    assert r.status_code == 200
    assert r.json()["called"]["patient_id"] == str(p1)  # earliest appointment first
    assert r.json()["queue"]["waiting_count"] == 1

    staff = token(uuid.uuid4(), "STAFF")
    assert (await client.post(f"/api/v1/queues/{queue_id}/call-next", headers=staff)).json()["called"]["patient_id"] == str(p2)
    r = await client.post(f"/api/v1/queues/{queue_id}/call-next", headers=staff)
    assert r.status_code == 409 and r.json()["code"] == "QUEUE_EMPTY"


async def test_concurrent_call_next_never_calls_the_same_patient_twice(client):
    doctor = uuid.uuid4()
    await seed(doctor, [(uuid.uuid4(), f"09:{m:02d}") for m in range(0, 50, 10)])  # 5 patients
    queue_id = (await client.get(f"/api/v1/queues/doctors/{doctor}?date={DAY}", headers=token(doctor, "DOCTOR"))).json()["queue_id"]
    staff = token(uuid.uuid4(), "STAFF")
    results = await asyncio.gather(*(client.post(f"/api/v1/queues/{queue_id}/call-next", headers=staff) for _ in range(8)))
    called = [r.json()["called"]["entry_id"] for r in results if r.status_code == 200]
    assert len(called) == 5 and len(set(called)) == 5
    assert sorted(r.status_code for r in results).count(409) == 3


async def test_status_transitions(client):
    doctor = uuid.uuid4()
    await seed(doctor, [(uuid.uuid4(), "09:00")])
    q = (await client.get(f"/api/v1/queues/doctors/{doctor}?date={DAY}", headers=token(doctor, "DOCTOR"))).json()
    url = f"/api/v1/queues/{q['queue_id']}/entries/{q['waiting'][0]['entry_id']}"
    h = token(doctor, "DOCTOR")

    r = await client.patch(url, json={"status": "DONE"}, headers=h)  # WAITING -> DONE not allowed
    assert r.status_code == 409 and r.json()["code"] == "INVALID_TRANSITION"
    for status in ("CALLED", "IN_CONSULTATION"):
        assert (await client.patch(url, json={"status": status}, headers=h)).status_code == 200
    r = await client.patch(url, json={"status": "DONE"}, headers=h)
    assert r.status_code == 200 and r.json()["current"] == [] and r.json()["waiting"] == []
    assert (await client.patch(url, json={"status": "BOGUS"}, headers=h)).status_code == 400


async def test_my_entries_gives_position(client):
    from app.service import today

    doctor, me = uuid.uuid4(), uuid.uuid4()
    day = str(today())
    for patient, start in [(uuid.uuid4(), "08:00"), (uuid.uuid4(), "08:30"), (me, "09:00")]:
        await process_message(*booked(uuid.uuid4(), 1, patient, doctor, start, day=day))
    r = await client.get("/api/v1/queues/me", headers=token(me, "PATIENT"))
    assert r.status_code == 200
    [mine] = r.json()
    assert mine["doctor_id"] == str(doctor) and mine["entry"]["position"] == 3


def test_websocket_pushes_updates():
    from starlette.testclient import TestClient

    from app.main import app

    doctor, patient = uuid.uuid4(), uuid.uuid4()
    with TestClient(app) as tc, tc.websocket_connect(f"/api/v1/ws/queues/doctors/{doctor}?date={DAY}") as ws:
        assert ws.receive_json()["waiting_count"] == 0
        tc.portal.call(process_and_publish, booked(uuid.uuid4(), 1, patient, doctor, "09:00"))
        update = ws.receive_json()
        assert update["waiting_count"] == 1 and "patient_id" not in update["waiting"][0]


async def process_and_publish(msg):
    from app.realtime import publish_snapshots

    _, keys = await process_message(*msg)
    await publish_snapshots(keys)


async def test_health(client):
    assert (await client.get("/health/live")).json() == {"status": "UP"}
    r = await client.get("/health/ready")
    assert r.status_code == 200 and r.json()["checks"]["database"] == "UP"
