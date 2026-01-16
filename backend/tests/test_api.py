import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_init_session():
    response = client.post("/init", json={
        "user_id": "test_user",
        "grade_level": "10",
        "topic": "Python"
    })
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data

def test_chat_without_init():
    response = client.post("/chat", json={
        "session_id": "fake-session",
        "message": "Hello"
    })
    assert response.status_code == 404

# Note: Full chat flow needs OpenAI API Key.
# We skip the external call or mock it if we wanted to be robust.
# For now, we assume the environment might not have the key, so we strictly test the existence of the endpoint logic 
# up to the point of invocation.
# But 'client' calls will trigger the graph.
# If no key, it will fail with OpenAIError.
# We should probably mock langchain_openai.ChatOpenAI if we want this test to pass without creds.
