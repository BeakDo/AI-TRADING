import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.settings import refresh_kis_credentials, settings
from backend.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_kis_credentials_persist(tmp_path):
    client = TestClient(app)

    tmp_file = tmp_path / "kis_credentials.json"
    original_file = settings.KIS_CREDENTIALS_FILE
    original_values = {
        "appkey": settings.KIS_APPKEY,
        "appsecret": settings.KIS_APPSECRET,
        "account_no8": settings.KIS_ACCOUNT_NO8,
        "account_prod2": settings.KIS_ACCOUNT_PROD2,
        "is_paper": settings.KIS_IS_PAPER,
    }

    settings.KIS_CREDENTIALS_FILE = str(tmp_file)
    settings.KIS_APPKEY = ""
    settings.KIS_APPSECRET = ""
    settings.KIS_ACCOUNT_NO8 = ""
    settings.KIS_ACCOUNT_PROD2 = ""
    settings.KIS_IS_PAPER = True

    payload = {
        "appkey": "TESTAPPKEY123",
        "appsecret": "SECRET456",
        "account_no8": "12345678",
        "account_prod2": "01",
        "is_paper": False,
    }

    response = client.post("/api/admin/kis/credentials", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["has_credentials"] is True
    assert data["appkey_preview"].startswith(payload["appkey"][:3])
    assert data["account_prod2_preview"] == "**"

    assert tmp_file.exists()
    stored = json.loads(Path(tmp_file).read_text("utf-8"))
    assert stored["appkey"] == payload["appkey"]
    assert stored["appsecret"] == payload["appsecret"]
    assert settings.KIS_APPKEY == payload["appkey"]
    assert settings.KIS_IS_PAPER is False

    status_response = client.get("/api/admin/kis/credentials")
    assert status_response.status_code == 200
    assert status_response.json()["has_credentials"] is True

    settings.KIS_CREDENTIALS_FILE = original_file
    settings.KIS_APPKEY = original_values["appkey"]
    settings.KIS_APPSECRET = original_values["appsecret"]
    settings.KIS_ACCOUNT_NO8 = original_values["account_no8"]
    settings.KIS_ACCOUNT_PROD2 = original_values["account_prod2"]
    settings.KIS_IS_PAPER = original_values["is_paper"]
    refresh_kis_credentials(settings)
