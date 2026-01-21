from backend.database import SessionLocal, Player, TopicProgress
from backend.knowledge_graph import get_graph
import json

def debug_db():
    db = SessionLocal()
    players = db.query(Player).all()
    print(f"Found {len(players)} players.")
    
    for p in players:
        print(f"\nPlayer: {p.username} (ID: {p.id})")
        progs = db.query(TopicProgress).filter(TopicProgress.player_id == p.id).all()
        for prog in progs:
            print(f"  Topic: {prog.topic_name}")
            print(f"  Current Node: {prog.current_node}")
            print(f"  Mastery: {prog.mastery_score}%")
            print(f"  Completed Nodes: {prog.completed_nodes}")
            
            # Check against KG
            if prog.topic_name:
                kg = get_graph(prog.topic_name)
                if kg:
                    print(f"  [KG] Graph Loaded: {len(kg.graph.nodes)} nodes")
                    if prog.completed_nodes:
                        stats = kg.get_completion_stats(prog.completed_nodes)
                        print(f"  [KG] Calculated Stats: {stats}")
                        
                        # Verify IDs
                        for nid in prog.completed_nodes:
                            if nid not in kg.graph:
                                print(f"  [WARNING] Node ID '{nid}' NOT found in KG!")
                            else:
                                print(f"  [OK] Node '{nid}' valid.")
                else:
                    print(f"  [ERROR] Could not load graph for topic '{prog.topic_name}'")

if __name__ == "__main__":
    debug_db()
