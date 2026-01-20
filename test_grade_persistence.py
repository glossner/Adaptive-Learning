import requests

BASE_URL = "http://127.0.0.1:8000"

def test_grade_persistence_manual():
    username = "manual_grade_test"
    topic = "Math 3.0"
    
    # 1. Initialize session as Grade 10 (simulate startup default)
    print("\n1. Initializing Session (Grade 10)...")
    requests.post(f"{BASE_URL}/init_session", json={
        "username": username,
        "grade_level": 10,
        "location": "NH",
        "learning_style": "Visual"
    })
    
    # 2. Select Book "Math 3" with Manual Mode ON
    print("\n2. Selecting 'Math 3' (Manual Mode ON)...")
    resp = requests.post(f"{BASE_URL}/select_book", json={
        "username": username,
        "topic": topic,
        "manual_mode": True
    })
    data = resp.json()
    summary = data["history_summary"]
    
    print(f"Summary: {summary}")
    
    # Check if warning is suppressed
    if "too easy" in summary:
        print("FAILURE: Warning still present!")
    else:
        print("SUCCESS: Warning suppressed.")

    # 3. Chat to verify context
    session_id = data["session_id"]
    print("\n3. Sending 'Hello' to check agent context...")
    resp = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Hello"
    })
    print(f"Agent: {resp.json()['response']}")

if __name__ == "__main__":
    test_grade_persistence_manual()
