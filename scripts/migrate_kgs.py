import json
import os
import copy
from typing import Dict, List

# Configuration
KG_DIR = "/home/jglossner/Adaptive-Learning/backend/data/knowledge_graphs"
SUBJECT_MAPPING = {
    "math.json": "Math",
    "english.json": "ELA",
    "history.json": "Social_Studies",
    "science.json": "Science"
}

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# -----------------------------------------------------------------------------
# TAXONOMY FILTERING (Recursively extract strict branches for a grade)
# -----------------------------------------------------------------------------
def filter_taxonomy_for_grade(taxonomy: Dict, target_grade: int) -> Dict:
    """
    Returns a new taxonomy dictionary containing ONLY:
    1. Concepts belonging exactly to target_grade.
    2. The topic structure (parents) needed to reach those concepts.
    
    If a topic has no relevant concepts (and no subtopics with relevant concepts),
    it is pruned.
    """
    filtered = {}
    
    for key, value in taxonomy.items():
        # Check if node itself is relevant?
        # Usually Topics have grade_level 0 or broad range. 
        # We only care about LEAF concepts matching the grade.
        
        # We need a deep copy to modify children
        node_copy = copy.deepcopy(value)
        keep_node = False
        
        # 1. Check Concepts (Leaves)
        if "concepts" in node_copy:
            relevant_concepts = [
                c for c in node_copy["concepts"]
                if c.get("grade_level", value.get("grade_level", 0)) == target_grade
            ]
            
            if relevant_concepts:
                node_copy["concepts"] = relevant_concepts
                keep_node = True
            else:
                del node_copy["concepts"]
                
        # 2. Check Subtopics (Branches)
        if "subtopics" in node_copy:
            filtered_subs = filter_taxonomy_for_grade(node_copy["subtopics"], target_grade)
            if filtered_subs:
                node_copy["subtopics"] = filtered_subs
                keep_node = True
            else:
                # If subtopics existed but none matched, and no concepts matched...
                # Check strict node grade? 
                # If a TOPIC is explicitly Grade X, but has no concepts?
                # Usually we want content. Let's ignore empty topics.
                del node_copy["subtopics"]
        
        if keep_node:
            filtered[key] = node_copy
            
    return filtered

# -----------------------------------------------------------------------------
# FLAT LIST FILTERING (For Science/History/English legacy formats)
# -----------------------------------------------------------------------------
def filter_flat_list_for_grade(nodes: List[Dict], target_grade: int) -> List[Dict]:
    """Filters a flat list of nodes for a specific grade level."""
    return [n for n in nodes if n.get("grade_level", 0) == target_grade]

# -----------------------------------------------------------------------------
# MAIN MIGRATION LOGIC
# -----------------------------------------------------------------------------
def migrate_subject(filename, new_subject_name):
    print(f"Migrating {filename} -> {new_subject_name}...")
    
    src_path = os.path.join(KG_DIR, filename)
    if not os.path.exists(src_path):
        print(f"  Skipping {filename} (not found)")
        return

    data = load_json(src_path)
    
    # Create Subject Directory
    dest_dir = os.path.join(KG_DIR, new_subject_name)
    ensure_dir(dest_dir)
    
    # Determine Structure Type
    is_taxonomy = "taxonomy" in data
    
    # Iterate Grades 0 to 12
    for grade in range(13): # 0-12
        grade_str = f"{grade:02d}"
        new_filename = f"{grade_str}_{new_subject_name}.json"
        out_path = os.path.join(dest_dir, new_filename)
        
        new_data = {
            "subject": new_subject_name,
            "version": "1.0",
            "grade_level": grade
        }
        
        content_found = False
        
        if is_taxonomy:
            filtered_max = filter_taxonomy_for_grade(data["taxonomy"], grade)
            if filtered_max:
                new_data["taxonomy"] = filtered_max
                content_found = True
        else:
            # Flat List (Science/History/English current state?)
            # Logic: data.get("nodes", [])?
            if "nodes" in data:
                filtered_nodes = filter_flat_list_for_grade(data["nodes"], grade)
                if filtered_nodes:
                    new_data["nodes"] = filtered_nodes
                    content_found = True
            elif "taxonomy" in data: 
                 # Fallback if mixed? structure
                 pass
                 
        if content_found:
            save_json(out_path, new_data)
            print(f"  Generated {new_filename}")
        else:
            # Optional: Don't create empty files? Or create placeholder?
            # User asked: "partition the files".
            # Usually strict partition implies no file if no content.
            pass

def main():
    print("Starting Knowledge Graph Migration...")
    for old_file, new_name in SUBJECT_MAPPING.items():
        migrate_subject(old_file, new_name)
    print("Migration Complete.")

if __name__ == "__main__":
    main()
