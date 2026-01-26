
import os

MAIN_PATH = "backend/main.py"

OLD_BLOCK = """    # Access internal graph data to get type/parent
    for node_id in kg.graph.nodes():
        node_data = kg.graph.nodes[node_id]
        
        # Determine Status
        status = "locked"
        if node_id in completed_set:
            status = "completed"
        elif node_id == current_node_id:
            status = "current"
        else:
             # Check if available?
             # Simple heuristic: If parent is unlocked?
             # For now, default to locked unless completed.
             # Actually, if we want "Available" vs "Locked", we need `get_next_learnable`.
             pass
             
        # Parents: Find incoming edge from a non-concept node (Topic/Subtopic)
        # KG graph is generic DiGraph.
        parent_id = None
        for pred in kg.graph.predecessors(node_id):
            if kg.graph.nodes[pred].get("type") in ["topic", "subtopic"]:
                parent_id = pred
                break
        
        # If no parent found via graph (Root), it is None
        
        # Check availability roughly if not completed
        if status == "locked":
             # If parent is completed OR parent is root?
             # Simplify: Open if it is a learnable candidate
             pass
             
        result_nodes.append(GraphNode(
            id=node_id,
            label=node_data.get("label", node_id),
            grade_level=node_data.get("grade_level", 0),
            type=node_data.get("type", "concept"),
            status=status,
            parent=parent_id
        ))"""

NEW_BLOCK = """    # Access internal graph data to get type/parent
    # Windowing Logic
    focus = request.focus_node_id
    if not focus and current_node_id:
        focus = current_node_id
        
    window_limit = request.window_size if request.window_size > 0 else 20
    target_nodes = kg.get_window(focus, window_limit)
    
    for node_obj in target_nodes:
        node_id = node_obj.id
        node_data = kg.graph.nodes[node_id]
        
        # Determine Status
        status = "locked"
        if node_id in completed_set:
            status = "completed"
        elif node_id == current_node_id:
            status = "current"
        else:
             pass
             
        # Parents
        parent_id = None
        for pred in kg.graph.predecessors(node_id):
            if kg.graph.nodes[pred].get("type") in ["topic", "subtopic"]:
                parent_id = pred
                break
        
        result_nodes.append(GraphNode(
            id=node_id,
            label=node_data.get("label", node_id),
            grade_level=node_data.get("grade_level", 0),
            type=node_data.get("type", "concept"),
            status=status,
            parent=parent_id
        ))"""

with open(MAIN_PATH, "r") as f:
    content = f.read()

if OLD_BLOCK not in content:
    print("Error: OLD_BLOCK not found in file directly.")
    # Try fuzzy match?
    # Let's print the section of content where we expect it
    start_marker = "    # Access internal graph data to get type/parent"
    idx = content.find(start_marker)
    if idx != -1:
        print("Found start marker.")
        print("Existing content snippet:")
        print(content[idx:idx+500])
        
        # Force Replace if start matches
        # We need to find the end.
        end_marker = "    # Late pass for"
        end_idx = content.find(end_marker)
        if end_idx != -1:
             new_content = content[:idx] + NEW_BLOCK + "\n    " + content[end_idx:] # Adjust newline
             with open(MAIN_PATH, "w") as f:
                 f.write(new_content)
             print("Force replaced content between markers.")
        else:
             print("End marker not found.")
    else:
        print("Start marker not found.")
else:
    new_content = content.replace(OLD_BLOCK, NEW_BLOCK)
    with open(MAIN_PATH, "w") as f:
        f.write(new_content)
    print("Successfully replaced content.")
