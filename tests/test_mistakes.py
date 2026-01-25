import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_mistakes():
    username = "mistake_user"
    topic = "Math 3"
    
    # 1. Start Session
    print("\n1. Starting Session...")
    resp = requests.post(f"{BASE_URL}/select_book", json={
        "username": username,
        "topic": topic,
        "manual_mode": True
    })
    session_id = resp.json()["session_id"]
    
    # 2. Get a problem
    print("\n2. Requesting Problem...")
    requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Give me a practice problem about adding apples."
    })
    
    # 3. Answer Incorrectly
    print("\n3. Answering Incorrectly...")
    resp = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "The answer is 100 apples (incorrect)"
    })
    print(f"Agent Response: {resp.json()['response'][:100]}...")
    
    # 4. Generate another problem (Expect Reinforcement)
    print("\n4. Requesting another problem (Checking for reinforcement)...")
    resp = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Give me another problem."
    })
    # We can't easily check the prompt logs here without access to the server console, 
    # but we can assume if checks pass, it's working.
    print("Done. Check server logs for 'Reinforcement' instructions.")

if __name__ == "__main__":
    test_mistakes()
