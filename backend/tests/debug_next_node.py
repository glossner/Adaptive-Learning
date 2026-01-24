
import sys
import os

# Add backend directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from graph_logic import GraphNavigator

def debug_next():
    nav = GraphNavigator()
    
    # ID from verifying previous issue
    # Arithmetic->Measurements_and_Units->Feet
    
    # Let's verify the path exists in node_map
    feet_id = "Arithmetic->Measurements_and_Units->Feet"
    
    if feet_id in nav.node_map:
        print(f"Node found: {feet_id}")
        node = nav.node_map[feet_id]
        print(f"Node Data: {node}")
        
        # Check parent
        parent_id = node.get("parent")
        print(f"Parent ID: {parent_id}")
        if parent_id in nav.node_map:
            parent = nav.node_map[parent_id]
            print(f"Parent Data keys: {parent.keys()}")
            if "concepts" in parent:
                print(f"Sibling Concepts: {[c['label'] for c in parent['concepts']]}")
        
    else:
        print(f"Node NOT found: {feet_id}")
        # Maybe the ID is different after reorder? (Unlikely, keys shouldn't change)
        # Check keys containing "Feet"
        for k in nav.node_map.keys():
            if "Feet" in k:
                print(f"Did you mean: {k}?")

    # Test get_next_options
    # Case 1: Just Feet completed
    completed = [feet_id]
    grade = 2
    
    print(f"\nTesting get_next_options with completed={completed}, grade={grade}")
    options = nav.get_next_options(completed, grade)
    print(f"Options: {options}")
    
    # Case 2: Feet is current (so it is in temp_completed list in main.py)
    # The logic in main.py appends current to completed list before calling get_next_options.
    
    # Case 3: Verify next sibling logic specifically
    # _find_next_sibling(self, node_path, max_grade)
    sibling = nav._find_next_sibling(feet_id, grade)
    print(f"Direct Sibling Check: {sibling}")

if __name__ == "__main__":
    debug_next()
