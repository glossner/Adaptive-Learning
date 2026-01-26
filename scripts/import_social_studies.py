import csv
import json
import re
import os

# Grade mapping
OUTPUT_DIR = "/home/jglossner/Adaptive-Learning/backend/data/knowledge_graphs/NH/Social_Studies"

GRADE_FILES = {
    0: "00_Social_Studies.json",
    1: "01_Social_Studies.json",
    2: "02_Social_Studies.json",
    3: "03_Social_Studies.json",
    4: "04_Social_Studies.json",
    5: "05_Social_Studies.json",
    6: "06_Social_Studies.json",
    7: "07_Social_Studies.json",
    8: "08_Social_Studies.json",
    9: "09_Social_Studies.json",
    10: "10_Social_Studies.json",
    11: "11_Social_Studies.json",
    12: "12_Social_Studies.json"
}

def parse_grades(grade_str):
    """
    Parses grade string from CSV (e.g., "3,4,5", "K,1,2", "9,10,11,12").
    Returns list of integers (0 for K).
    """
    grades = []
    parts = grade_str.replace('"', '').split(',')
    for part in parts:
        part = part.strip().lower()
        if part == 'k':
            grades.append(0)
        elif part.isdigit():
            grades.append(int(part))
    return grades

def main():
    csv_path = "/home/jglossner/Adaptive-Learning/backend/data/c3_standards_raw.csv"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Initialize data structures: Grade -> Root Node
    grade_data = {g: {"name": "Social Studies", "children": []} for g in GRADE_FILES}

    # Helper to find or create nodes
    def get_or_create_child(parent_list, name, description=""):
        for child in parent_list:
            if child["name"] == name:
                return child
        new_child = {"name": name, "description": description, "children": []}
        parent_list.append(new_child)
        return new_child

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        seen_standards = set()

        for row in reader:
            code = row['code']
            statement = row['statement']
            dimension = row['dimension'] # e.g., "Civics, Economics, Geography & History"
            
            # Use 'dim' or 'orig_dimension' for more granular topics if available?
            # The CSV has 'dimension' (broad) and 'orig_dimension' (broad).
            # But the code itself reveals structure (e.g., D2.Civ.1...).
            
            # Let's map Codes to meaningful sublevels.
            # D1 = Developing Questions & Planning Inquiries
            # D2 = Civics/Econ/Geo/Hist (The Core)
            # D3 = Evaluating Sources
            # D4 = Communicating Conclusions
            
            # We can use the 'dimension' column as the top branching.
            # Then maybe group by the code prefix or just list them.
            
            grades = parse_grades(row['grade'])

            for grade in grades:
                if grade not in grade_data:
                    continue
                
                grade_root = grade_data[grade]
                
                # Level 1: Dimension (e.g. "Civics...")
                dim_node = get_or_create_child(grade_root["children"], dimension)
                
                # Level 2: Sub-category from Code?
                # D2.Civ -> Civics
                # D2.Eco -> Economics
                # D2.Geo -> Geography
                # D2.His -> History
                
                subcat_name = "General"
                if "Civ" in code: subcat_name = "Civics"
                elif "Eco" in code: subcat_name = "Economics"
                elif "Geo" in code: subcat_name = "Geography"
                elif "His" in code: subcat_name = "History"
                elif "D1" in code: subcat_name = "Inquiry"
                elif "D3" in code: subcat_name = "Evaluating Sources"
                elif "D4" in code: subcat_name = "Communicating Conclusions"
                
                # Create Subcat Node if we are in D2 (the big one)
                target_list = dim_node["children"]
                if dimension == "Civics, Economics, Geography & History":
                     subcat_node = get_or_create_child(dim_node["children"], subcat_name)
                     target_list = subcat_node["children"]

                # Level 3: Standard
                # Check for dupes in this specific grade/list
                exists = False
                for existing in target_list:
                    if existing["name"] == code:
                        exists = True
                        break
                
                if not exists:
                    target_list.append({
                        "name": code,
                        "description": statement,
                        "children": []
                    })

    # Write files
    for grade, filename in GRADE_FILES.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(grade_data[grade], f, indent=2)
        print(f"Generated {filepath} with {len(grade_data[grade]['children'])} dimensions.")

if __name__ == "__main__":
    main()
