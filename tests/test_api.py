from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200

def test_generate_caption():
    r = client.post("/generate_caption", json={"video_id":"demo"})
    js = r.json()
    assert r.status_code == 200
    assert "caption" in js and "highlight_segments" in js

def test_retrieve_info():
    r = client.post("/retrieve_info", json={"query":"台灣人去斯里蘭卡要簽證嗎？"})
    js = r.json()
    assert r.status_code == 200
    assert "answer" in js and "citations" in js
