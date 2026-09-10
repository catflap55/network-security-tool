def test_health_open(client) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_settings_requires_token(client) -> None:
    r = client.get("/settings")
    assert r.status_code == 401


def test_settings_with_token(client, auth) -> None:
    r = client.get("/settings", headers=auth)
    assert r.status_code == 200
    assert r.json()["token_required"] is True


def test_project_rejects_bad_target(client, auth) -> None:
    client.put("/settings", headers=auth, json={"authorization_acknowledged": True})
    r = client.post(
        "/projects",
        headers=auth,
        json={"name": "bad", "targets": "1.2.3.4; rm -rf /", "environment": "lab"},
    )
    assert r.status_code == 400


def test_job_requires_ack(client, auth) -> None:
    client.put("/settings", headers=auth, json={"authorization_acknowledged": False})
    r = client.post(
        "/projects",
        headers=auth,
        json={"name": "home", "targets": "127.0.0.1", "environment": "home"},
    )
    assert r.status_code == 200
    pid = r.json()["id"]
    job = client.post(f"/projects/{pid}/jobs", headers=auth, json={"plugin_id": "nmap_quick"})
    assert job.status_code == 403


def test_start_and_cancel_tls_job(client, auth) -> None:
    client.put("/settings", headers=auth, json={"authorization_acknowledged": True})
    r = client.post(
        "/projects",
        headers=auth,
        json={"name": "local", "targets": "127.0.0.1", "environment": "lab"},
    )
    pid = r.json()["id"]
    job = client.post(f"/projects/{pid}/jobs", headers=auth, json={"plugin_id": "tls_inspect"})
    assert job.status_code == 200
    jid = job.json()["id"]
    listed = client.get(f"/projects/{pid}/jobs", headers=auth)
    assert listed.status_code == 200
    cancel = client.post(f"/projects/{pid}/jobs/{jid}/cancel", headers=auth)
    assert cancel.status_code in (200, 409)


def test_diff_same_empty(client, auth) -> None:
    client.put("/settings", headers=auth, json={"authorization_acknowledged": True})
    r = client.post(
        "/projects",
        headers=auth,
        json={"name": "d", "targets": "127.0.0.1", "environment": "lab"},
    )
    pid = r.json()["id"]
    j1 = client.post(f"/projects/{pid}/jobs", headers=auth, json={"plugin_id": "http_headers"}).json()
    j2 = client.post(f"/projects/{pid}/jobs", headers=auth, json={"plugin_id": "http_headers"}).json()
    # second may 429 if first still running
    if "id" not in j2:
        return
    diff = client.get(f"/projects/{pid}/jobs/{j1['id']}/diff/{j2['id']}", headers=auth)
    assert diff.status_code == 200
    assert "summary" in diff.json()
