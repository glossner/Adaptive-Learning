import json
import os
import sys

# Add backend directory to sys.path to resolve imports if needed, 
# but picking up math_raw from data directory might require appending that path
sys.path.append(os.path.join(os.path.dirname(__file__), '../data/knowledge_graphs'))

try:
    import math_raw
except ImportError:
    print("Error: Could not import math_raw. Make sure math_raw.py is in backend/data/knowledge_graphs/")
    sys.exit(1)

def parse_taxonomy():
    taxonomy = {}
    
    # Grade Level Mappings (US Standard Approximation)
    # Topic -> Starting Grade Level
    topic_grades = {
        "Arithmetic": 1,
        "Algebra": 7,
        "Geometry": 9,
        "Trigonometry": 10,
        "Statistics_and_Probability": 9,
        "Pre-Calculus": 11,
        "Calculus": 12,
        "Advanced_Calculus": 13, # College
        "Discrete_Mathematics": 13,
        "Linear_Algebra": 13,
        "Advanced_Statistics": 13,
        "Mathematical_Proofs_and_Theory": 13,
    }

    # Specific Subtopic Overrides for granular accuracy
    subtopic_grades = {
        # K (0)
        "Recognizing_Shapes": 0,
        "Number_Sense": 0,
        "Counting": 0,

        # Grade 1
        "Basic_Operations": 1,
        "Number_Properties": 1,
        "Laws": 1,

        # Grade 2
        "Place_Values": 2,
        "Time_and_Calendar": 2,
        "Money": 2,
        "Measurements_and_Units": 2,

        # Grade 3
        "Fractions": 3,

        # Grade 4
        "Decimals": 4,

        # Grade 5
        "Factors_and_Multiples": 5,
        "Graphs": 5,
        "Estimation_and_Rounding": 5,

        # Grade 6
        "Percentages": 6,
        "Ratios_and_Proportions": 6,
        "Negative_Numbers": 6,

        # Grade 7 (Pre-Algebra / Algebra I start)
        "Algebraic_Expressions": 7,
        "Linear_Equations": 7,
        
        # Grade 8 (Algebra I cont. / Geometry Intro)
        "Exponents_and_Square_Roots": 8,
        "Functions": 8,
        "Systems_of_Equations": 8,
        "Inequalities": 8,
        "Pythagorean_Theorem": 8,
    }

    # Helper to clean string arrow notation
    # e.g. "Arithmetic->Recognizing_Shapes" -> "Recognizing_Shapes"
    def get_leaf(full_str):
        return full_str.split("->")[-1]

    # Level 1: Topics
    for topic, subtopics in math_raw.topics_and_subtopics.items():
        base_grade = topic_grades.get(topic, 0)
        
        taxonomy[topic] = {
            "color": math_raw.topic_colors.get(topic, "100,100,100"),
            "grade_level": base_grade,
            "subtopics": {}
        }
        
        # Level 2: SubTopics
        for subtopic_str in subtopics:
            subtopic_name = get_leaf(subtopic_str)
            # Check override, else inherit topic grade
            sub_grade = subtopic_grades.get(subtopic_name, base_grade)
            
            sub_node = {
                "grade_level": sub_grade,
                "subtopics": {}
            }
            taxonomy[topic]["subtopics"][subtopic_name] = sub_node
            
            # Level 3: SubSubTopics
            if subtopic_str in math_raw.subsub_topics:
                for subsub_str in math_raw.subsub_topics[subtopic_str]:
                    subsub_name = get_leaf(subsub_str)
                    
                    subsub_node = {
                        "grade_level": sub_grade, # Inherit from subtopic
                        "concepts": []
                    }
                    sub_node["subtopics"][subsub_name] = subsub_node
                    
                    # Level 4: Concepts (SubSubSubTopics)
                    if subsub_str in math_raw.subsubsub_topics:
                        for concept_str in math_raw.subsubsub_topics[subsub_str]:
                            concept_name = get_leaf(concept_str)
                            # Create a concept object
                            concept_obj = {
                                "label": concept_name,
                                "grade_level": sub_grade, # Inherit
                                "description": concept_name.replace("_", " ") # Default description
                            }
                            subsub_node["concepts"].append(concept_obj)

    final_json = {
        "subject": "Math",
        "taxonomy": taxonomy
    }
    
    return final_json

if __name__ == "__main__":
    data = parse_taxonomy()
    
    output_path = os.path.join(os.path.dirname(__file__), '../data/knowledge_graphs/math.json')
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
        print(f"Successfully converted math taxonomy to {output_path}")
