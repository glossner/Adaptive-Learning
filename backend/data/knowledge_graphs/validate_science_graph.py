
import json
import sys

def validate_coverage(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return False

    found_grades = set()
    
    def traverse(node):
        if 'grade_level' in node and node.get('type') == 'core':
            found_grades.add(node['grade_level'])
        
        if 'subtopics' in node:
            for key, child in node['subtopics'].items():
                traverse(child)
        if 'concepts' in node:
            for child in node['concepts']:
                # concepts might have grade levels too
                if 'grade_level' in child and child.get('type') == 'core':
                    found_grades.add(child['grade_level'])

    if 'taxonomy' in data:
        for domain, content in data['taxonomy'].items():
            traverse(content)
    
    missing = []
    for g in range(13): # 0 to 12
        if g not in found_grades:
            missing.append(g)
            
    if missing:
        print(f"FAIL: Missing core content for grades: {missing}")
        return False
    else:
        print("PASS: All grades 0-12 covered with core content.")
        
    optional_count = 0
    def count_optional(node):
        nonlocal optional_count
        if node.get('type') in ['optional', 'enrichment']:
            optional_count += 1
        if 'subtopics' in node:
            for child in node['subtopics'].values():
                count_optional(child)
        if 'concepts' in node:
            for child in node['concepts']:
                if child.get('type') in ['optional', 'enrichment']:
                    optional_count += 1
                    
    if 'taxonomy' in data:
        for content in data['taxonomy'].values():
            count_optional(content)
            
    print(f"INFO: Found {optional_count} optional/enrichment topics.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_science_graph.py <path_to_json>")
        sys.exit(1)
    
    success = validate_coverage(sys.argv[1])
    if not success:
        sys.exit(1)
