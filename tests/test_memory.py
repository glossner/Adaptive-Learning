import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_memory():
    # 1. Select Book
    print("\n1. Selecting Book...")
    resp = requests.post(f"{BASE_URL}/select_book", json={
        "username": "mem_test_user",
        "topic": "Math 10"
    })
    data = resp.json()
    session_id = data["session_id"]
    print(f"Session ID: {session_id}")

    # 2. Ask for Quiz
    print("\n2. Requesting Quiz...")
    resp = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Quiz Me"
    })
    print(f"Agent: {resp.json()['response']}")
    state = resp.json().get("state_snapshot", {})
    print(f"State Action: {state.get('current_action')}")

    # 3. Answer
    print("\n3. Answering...")
    resp = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "The answer is 42"
    })
    print(f"Agent: {resp.json()['response']}")

if __name__ == "__main__":
    test_memory()
