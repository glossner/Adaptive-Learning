import json
import os
import re

RAW_PATH = "/home/jglossner/Adaptive-Learning/backend/data/standards_raw.json"
OUTPUT_DIR = "/home/jglossner/Adaptive-Learning/backend/data/knowledge_graphs/ELA"

# Grade Mapping
GRADE_MAP = {
    "KG": 0, "01": 1, "02": 2, "03": 3, "04": 4, "05": 5, 
    "06": 6, "07": 7, "08": 8, "09": 9, "10": 10, "11": 11, "12": 12
}

def load_data():
    with open(RAW_PATH, "r") as f:
        return json.load(f)

def build_tree(flat_list):
    """
    Reconstructs the parent-child tree from the flat list.
    Returns:
    - nodes: Dict mapping ID -> Node Object
    - roots: List of root node IDs
    """
    nodes = {}
    roots = []
    
    # First pass: Index nodes
    for item in flat_list:
        asn_id = item["ASN"]["id"]
        nodes[asn_id] = item
        item["_children_objs"] = [] # Placeholder for child objects
        
    # Second pass: Link parents and children
    for asn_id, item in nodes.items():
        parent_id = item["ASN"].get("parent")
        if parent_id and parent_id in nodes:
            nodes[parent_id]["_children_objs"].append(item)
        else:
            # No parent in list? Treat as root?
            # Some nodes might be orphans or their parent isn't in this subset.
            # But the roots usually have parent: null
            if item["ASN"].get("parent") is None:
                roots.append(asn_id)
                
    return nodes, roots

def clean_label(text):
    """Sanitize text for use as a label/key."""
    # Remove leading numbering like "1. ", "RL.K.1 " etc if present?
    # Actually, using the full statement as description and a short label is better.
    # We will use "shortCode" or "statementNotation" as the label/ID if available?
    # Or just the Topic Name.
    # For Dictionary Keys (Topic/Subtopic), we need a readable string.
    # Remove special chars.
    text = re.sub(r'[^\w\s-]', '', text)
    text = text.replace(" ", "_").strip()
    return text

def get_node_label(item):
    """Determine best label for the node."""
    # Use 'statement' content but truncated? 
    # Or use 'shortCode' (e.g. RL.K.1)?
    
    # For groupings (Folders):
    stmt = item.get("statement", "")
    
    # For Leafs (Standards):
    short_code = item.get("shortCode") 
    notation = item["ASN"].get("statementNotation")
    if short_code: return short_code
    if notation: return notation
    
    # Fallback for folders
    return stmt

def process_grade(grade_int, nodes, roots):
    """
    Traverses the tree and builds the taxonomy for a specific grade.
    """
    
    def recursive_build(node_id):
        node = nodes[node_id]
        
        # Check relevance:
        # 1. Direct match: grade_int in parsed gradeLevels of this node
        # 2. Indirect match: This node is a parent of a relevant node (we'll see if children return generic content)
        
        # Parse grades for this node
        node_grades = []
        raw_grades = node.get("gradeLevels") or []
        for g in raw_grades:
            if g in GRADE_MAP:
                node_grades.append(GRADE_MAP[g])
        
        # Is this node SPECIFICALLY for this grade? 
        # Or is it a container (K-12)?
        is_relevant_container = False
        gl_str = node.get("gradeLevel") or ""
        if "K-12" in gl_str:
            is_relevant_container = True
        elif grade_int in node_grades:
            is_relevant_container = True
            
        # Recurse children
        built_subtopics = {}
        built_concepts = []
        
        # Sort children safely? The list is arbitrary order.
        # 'listIdentifier' might help order?
        child_objs = node["_children_objs"]
        child_objs.sort(key=lambda x: x.get("listIdentifier", "0"))

        for child in child_objs:
            res = recursive_build(child["ASN"]["id"])
            if res:
                c_type, c_data = res
                if c_type == "concept":
                    built_concepts.append(c_data)
                elif c_type == "subtopic":
                    # Merge subtopics
                    key = c_data["label"] 
                    key = clean_label(key)
                    built_subtopics[key] = c_data["data"]
        
        # Decision: Am I a leaf for this grade?
        # Check 'leaf' property in ASN
        is_leaf = node["ASN"].get("leaf") == "true"
        
        if is_leaf:
            # I am a standard. Do I apply to this grade?
            if grade_int in node_grades:
                code = get_node_label(node)
                desc = node.get("statement", "")
                return "concept", {
                    "label": code,
                    "grade_level": grade_int,
                    "type": "core",
                    "description": desc,
                    "node_type": "core" # Standard
                }
            else:
                return None
        
        else:
            # I am a container.
            # If I have valid children for this grade, I persist.
            if built_subtopics or built_concepts:
                label = get_node_label(node)
                
                # Construct result
                # We need to distinguish between "Subtopic" (has concepts) and "Topic" (has subtopics)?
                # Our KG format allows mixing concepts/subtopics in "taxonomy" theoretically?
                # Usually:
                # Topic -> Subtopic -> Concepts
                
                out = {
                    "grade_level": grade_int,
                    "type": "core", # "topic" or "subtopic" inferred by parent
                    # "description": node.get("statement", "")
                }
                
                if built_subtopics:
                    out["subtopics"] = built_subtopics
                if built_concepts:
                    out["concepts"] = built_concepts
                    
                return "subtopic", { # Return as subtopic stucture
                    "label": label,
                    "data": out
                }
            else:
                return None

    # Main Loop for Roots
    taxonomy = {}
    
    for root_id in roots:
        res = recursive_build(root_id)
        if res:
            _, c_data = res
            key = clean_label(c_data["label"])
            taxonomy[key] = c_data["data"]
            
    return taxonomy

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    data = load_data()
    nodes, roots = build_tree(data)
    
    print(f"Loaded {len(nodes)} nodes. Found {len(roots)} roots.")
    
    for grade in range(13):
        print(f"Processing Grade {grade}...")
        tax = process_grade(grade, nodes, roots)
        
        if not tax:
            print(f"  Warning: No content for Grade {grade}")
            continue
            
        filename = f"{grade:02d}_ELA.json"
        
        out_json = {
            "subject": "ELA",
            "grade_level": grade,
            "taxonomy": tax
        }
        
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w") as f:
            json.dump(out_json, f, indent=4)
            # print(f"  Saved {filename}")

if __name__ == "__main__":
    main()
