import csv
import json
import re
import os

# Grade mapping
GRADE_FILES = {
    0: "00_Science.json",
    1: "01_Science.json",
    2: "02_Science.json",
    3: "03_Science.json",
    4: "04_Science.json",
    5: "05_Science.json",
    6: "06_Science.json",
    7: "07_Science.json",
    8: "08_Science.json",
    9: "09_Science.json",
    10: "10_Science.json",
    11: "11_Science.json",
    12: "12_Science.json"
}

OUTPUT_DIR = "/home/jglossner/Adaptive-Learning/backend/data/knowledge_graphs/NH/Science"

def get_target_grades(pe_code, csv_grade_range):
    """
    Determines the target grade(s) from the PE code (e.g., '5-PS1-1' -> [5], 'MS-PS1-1' -> [6,7,8]).
    Falls back to csv_grade_range if PE code is ambiguous.
    """
    code = pe_code.strip().upper()
    
    # Specific grade prefix
    if code.startswith("K-"):
        return [0]
    
    match = re.match(r"^(\d)-", code)
    if match:
        return [int(match.group(1))]
        
    # Grade bands
    if code.startswith("MS-"):
        return [6, 7, 8]
    if code.startswith("HS-"):
        return [9, 10, 11, 12]
        
    # Fallback to CSV range
    grades = []
    parts = csv_grade_range.replace('"', '').split(',')
    for part in parts:
        part = part.strip().lower()
        if part == 'k':
            grades.append(0)
        elif part.isdigit():
            grades.append(int(part))
    return grades

def main():
    csv_path = "/home/jglossner/Adaptive-Learning/backend/data/ngss_standards_raw.csv"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Initialize data structures
    grade_data = {g: {"name": "Science", "children": []} for g in GRADE_FILES}

    # Helper to find or create nodes
    def get_or_create_child(parent_list, name, description=""):
        for child in parent_list:
            if child["name"] == name:
                return child
        new_child = {"name": name, "description": description, "children": []}
        parent_list.append(new_child)
        return new_child

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        seen_pes = set() # Avoid duplicates if multiple rows list the same PE

        for row in reader:
            pe_code = row['PEcode']
            if not pe_code:
                continue
            
            # Use a unique key to prevent duplicate standards in the same grade
            # (The CSV might have multiple rows for the same PE if it maps to multiple DCIs)
            if pe_code in seen_pes:
                continue
            seen_pes.add(pe_code)

            description = row['performanceExpectation']
            subcat = row['subcategory'] # e.g., "Structure & Properties of Matter"
            
            # Clean up subcategory
            domain = subcat.strip()
            
            target_grades = get_target_grades(pe_code, row['grade'])
            
            for grade in target_grades:
                if grade not in grade_data:
                    continue
                
                grade_root = grade_data[grade]
                
                # Level 1: Domain (Subcategory from CSV)
                domain_node = get_or_create_child(grade_root["children"], domain)
                
                # Level 2: Standard (The PE Code)
                # Ensure we don't duplicate standards
                standard_exists = False
                for existing in domain_node["children"]:
                    if existing["name"] == pe_code:
                        standard_exists = True
                        break
                
                if not standard_exists:
                    domain_node["children"].append({
                        "name": pe_code,
                        "description": description,
                        "children": []
                    })

    # Write files
    for grade, filename in GRADE_FILES.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(grade_data[grade], f, indent=2)
        print(f"Generated {filepath} with {len(grade_data[grade]['children'])} domains.")

if __name__ == "__main__":
    main()
