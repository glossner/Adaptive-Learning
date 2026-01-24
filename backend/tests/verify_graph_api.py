import sys
import os
import asyncio
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from backend.main import app, get_db
from backend.database import init_db, SessionLocal, Player, TopicProgress

client = TestClient(app)

def test_graph_api():
    # Setup
    init_db()
    db = SessionLocal()
    
    username = "TestGraphUser"
    topic = "Math"
    
    # Create Player
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        player = Player(username=username, grade_level=2)
        db.add(player)
        db.commit()
    
    # Create Progress: Complete "Feet", Current "Standard_to_Metric"
    # Node IDs: 
    # Feet: Arithmetic->Measurements_and_Units->Feet
    # Stand_to_Met: Arithmetic->Measurements_and_Units->Standard_to_Metric
    
    feet_id = "Arithmetic->Measurements_and_Units->Feet"
    conv_id = "Arithmetic->Measurements_and_Units->Standard_to_Metric"
    
    prog = db.query(TopicProgress).filter(TopicProgress.player_id == player.id, TopicProgress.topic_name == topic).first()
    if not prog:
        prog = TopicProgress(player_id=player.id, topic_name=topic, mastery_score=50)
        db.add(prog)
    
    prog.completed_nodes = [feet_id]
    prog.current_node = conv_id
    db.commit()
    
    # Call API
    response = client.post("/get_topic_graph", json={"username": username, "topic": topic})
    
    print("Response Code:", response.status_code)
    if response.status_code != 200:
        print("Error:", response.text)
        return
        
    data = response.json()
    nodes = data.get("nodes", [])
    print(f"Received {len(nodes)} nodes.")
    
    # Verify Status
    feet_node = next((n for n in nodes if n["id"] == feet_id), None)
    conv_node = next((n for n in nodes if n["id"] == conv_id), None)
    
    if feet_node:
        print(f"Feet Status: {feet_node['status']} (Expected: completed)")
        assert feet_node['status'] == 'completed'
        
    if conv_node:
        print(f"Conv Status: {conv_node['status']} (Expected: current)")
        assert conv_node['status'] == 'current'
        
    # Verify Hierarchy
    # Feet parent should be Arithmetic->Measurements_and_Units
    parent_id = "Arithmetic->Measurements_and_Units"
    if feet_node:
        print(f"Feet Parent: {feet_node['parent']}")
        assert feet_node['parent'] == parent_id
        
    print("Graph API Verification Passed!")

if __name__ == "__main__":
    test_graph_api()
