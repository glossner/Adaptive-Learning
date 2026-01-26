import json
import os
import re

RAW_PATH = "/home/jglossner/Adaptive-Learning/backend/data/math_standards_raw.json"
OUTPUT_DIR = "/home/jglossner/Adaptive-Learning/backend/data/knowledge_graphs/NH/Math"

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
    """
    nodes = {}
    roots = []
    
    # First pass: Index nodes
    for item in flat_list:
        # Use ASN id if available, else item["id"]?
        # The flat list in math JSON uses "id" at top level, and "ASN.id" inside.
        # But ELA used 'ASN.id'. Let's check parent references.
        # Math parents (e.g. S1143409) seem to map to ASN identifiers.
        
        asn_id = item.get("asnIdentifier")
        if not asn_id:
            # Maybe inside ASN object?
            if "ASN" in item and item["ASN"].get("id"):
                asn_id = item["ASN"]["id"]
        
        # Fallback to main ID if ASN identifier is missing
        main_id = item["id"]
        
        # Store by both? Or rely on reference consistency?
        # Let's verify which ID the 'parent' field uses.
        # Example: "parent": "S2366905" -> This looks like an ASN ID.
        
        # We'll key by ASN ID if present, else Main ID.
        # BUT we need to be able to lookup by Parent ID.
        
        key = asn_id if asn_id else main_id
        nodes[key] = item
        item["_children_objs"] = []
        item["_my_key"] = key
        
        # Also map main_id to this item if different, just in case
        if main_id != key:
             nodes[main_id] = item

    # Second pass: Link parents and children
    for key, item in nodes.items():
        if key != item.get("_my_key"): continue # Skip alias entries
        
        parent_id = None
        if "ASN" in item and item["ASN"].get("parent"):
             parent_id = item["ASN"]["parent"]
        elif "asnParent" in item:
             parent_id = item["asnParent"]
             
        if parent_id and parent_id in nodes:
            nodes[parent_id]["_children_objs"].append(item)
        else:
             # Is it a root?
             # Domains usually have no parent or parent is root container?
             # Check if gradeLevel is set or if it's a domain
             if not parent_id:
                 roots.append(key)
                
    return nodes, roots

def clean_label(text):
    text = re.sub(r'[^\w\s-]', '', text)
    text = text.replace(" ", "_").strip()
    return text

def get_node_label(item):
    # Try ShortCode (K.CC.1)
    if item.get("shortCode"):
         return item["shortCode"]
    # Try Code (Math.K.CC.1)
    if item.get("code"):
         return item["code"]
         
    # Try statementNotation
    if "ASN" in item and item["ASN"].get("statementNotation"):
         return item["ASN"]["statementNotation"]
         
    # Fallback to statement text (truncated?)
    stmt = item.get("statement", "")
    return stmt

def process_grade(grade_int, nodes, roots):
    
    def recursive_build(node_id):
        if node_id not in nodes: return None
        node = nodes[node_id]
        
        # Determine grades for this node
        node_grades = []
        raw_grades = node.get("gradeLevels") or []
        for g in raw_grades:
            if g in GRADE_MAP:
                node_grades.append(GRADE_MAP[g])
        
        is_relevant_container = False
        gl_str = node.get("gradeLevel") or ""
        
        if "K-12" in gl_str:
            is_relevant_container = True
        elif grade_int in node_grades:
            is_relevant_container = True
            
        # Optimization: If I'm a specific grade container (e.g. "Kindergarten") and not my grade -> Skip
        # But "Kindergarten" usually matches grade_int 0.
        
        # Recurse
        built_subtopics = {}
        built_concepts = []
        
        child_objs = node["_children_objs"]
        child_objs.sort(key=lambda x: x.get("listIdentifier", "0"))

        for child in child_objs:
            res = recursive_build(child["_my_key"])
            if res:
                c_type, c_data = res
                if c_type == "concept":
                    built_concepts.append(c_data)
                elif c_type == "subtopic":
                    key = c_data["label"] 
                    key = clean_label(key)
                    # Merge logic?
                    built_subtopics[key] = c_data["data"]
        
        # Am I a leaf?
        is_leaf = False
        if "ASN" in node and node["ASN"].get("leaf") == "true":
            is_leaf = True
            
        if is_leaf:
            # Must match grade EXACTLY or be K-12?
            # Standards are usually specific.
            if grade_int in node_grades:
                code = get_node_label(node)
                desc = node.get("statement", "")
                return "concept", {
                    "label": code,
                    "grade_level": grade_int,
                    "type": "core",
                    "description": desc,
                    "node_type": "core"
                }
            else:
                return None
        else:
            # Container. Keep if has children OR if I am relevant and have content?
            if built_subtopics or built_concepts:
                label = get_node_label(node)
                
                out = {
                    "grade_level": grade_int,
                    "type": "core", 
                }
                
                if built_subtopics:
                    out["subtopics"] = built_subtopics
                if built_concepts:
                    out["concepts"] = built_concepts
                    
                return "subtopic", { 
                    "label": label,
                    "data": out
                }
            else:
                return None

    # Main taxonomy build
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
    
    # Process K-12
    for grade in range(13):
        print(f"Processing Grade {grade}...")
        tax = process_grade(grade, nodes, roots)
        
        if not tax:
            print(f"  Warning: No content for Grade {grade}")
            
        # Always write file? Or skip?
        # Better to have empty file than missing partition for consistency
        
        filename = f"{grade:02d}_Math.json"
        
        out_json = {
            "subject": "Math",
            "grade_level": grade,
            "taxonomy": tax
        }
        
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w") as f:
            json.dump(out_json, f, indent=4)

if __name__ == "__main__":
    main()
