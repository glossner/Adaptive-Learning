import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_progress():
    username = "prog_test_user"
    topic = "Math 10"
    
    # 1. Initial State
    print(f"\n1. Selecting Book [{topic}] (Manual Mode)...")
    resp = requests.post(f"{BASE_URL}/select_book", json={
        "username": username,
        "topic": topic,
        "manual_mode": True
    })
    data = resp.json()
    session_id = data["session_id"]
    initial_mastery = data["mastery"]
    print(f"Session ID: {session_id}")
    print(f"Initial Mastery: {initial_mastery}%")

    # 2. Ask for Quiz
    print("\n2. Requesting Quiz...")
    requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "Quiz Me on 2+2"
    })
    
    # 3. Answer Correctly
    # We cheat and say "The answer is 4" hoping the LLM generates a simple problem or accepts it
    # Ideally we'd parse the question, but for 2+2 it works
    print("\n3. Answering '4'...")
    resp = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "message": "The answer is 4"
    })
    response_text = resp.json()["response"]
    print(f"Agent: {response_text[:100]}...")
    
    # Check if [CORRECT] token was present (debug)
    if "[CORRECT]" in response_text:
        print(">>> [CORRECT] token detected in response!")
    else:
        print(">>> WARNING: [CORRECT] token NOT detected. Mastery might not update.")

    # 4. Check Mastery Increase
    print("\n4. Re-selecting Book to check persistence...")
    resp = requests.post(f"{BASE_URL}/select_book", json={
        "username": username,
        "topic": topic,
        "manual_mode": True
    })
    new_mastery = resp.json()["mastery"]
    print(f"New Mastery: {new_mastery}%")
    
    if new_mastery > initial_mastery:
        print("SUCCESS: Mastery increased!")
    else:
        print("FAILURE: Mastery did not increase.")

if __name__ == "__main__":
    test_progress()
