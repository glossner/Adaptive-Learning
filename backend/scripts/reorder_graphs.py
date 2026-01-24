import json
import os

def sort_taxonomy(taxonomy):
    # Sort the current level by grade_level
    # Convert dict items to a list of (key, value) tuples
    items = list(taxonomy.items())
    
    # Sort function: defaults to 99 if no grade_level
    def get_sort_key(item):
        key, val = item
        grade = val.get("grade_level", 99)
        return (grade, key) # Secondary sort by key (alpha)
        
    items.sort(key=get_sort_key)
    
    # Reconstruct sorted dict and recurse
    sorted_taxonomy = {}
    for key, val in items:
        # Recurse if there are subtopics
        if "subtopics" in val:
            val["subtopics"] = sort_taxonomy(val["subtopics"])
        sorted_taxonomy[key] = val
        
    return sorted_taxonomy

def reorder_file(filepath):
    print(f"Processing {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        if "taxonomy" in data:
            data["taxonomy"] = sort_taxonomy(data["taxonomy"])
            
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
            
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "../data/knowledge_graphs")
    files = ["math.json", "science.json", "history.json", "english.json"]
    
    for f in files:
        path = os.path.join(base_dir, f)
        if os.path.exists(path):
            reorder_file(path)
