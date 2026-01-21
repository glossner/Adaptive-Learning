import json
import os
import sys

# Add backend directory to sys.path to resolve imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../data/knowledge_graphs'))

# Import taxonomies
try:
    import math_raw
    import english_raw
    import science_raw
    import social_studies_raw
except ImportError as e:
    print(f"Error: Could not import taxonomy files: {e}")
    # Don't exit, try to continue with what we have
    pass

def parse_taxonomy(subject_module, subject_name):
    # Use internal name "History" for Social Studies to match frontend
    output_subject_name = "History" if subject_name == "Social_Studies" else subject_name
    
    taxonomy = {}
    
    # Generic Grade Mappings (Extend as needed)
    topic_grades = {
        # MATH
        "Arithmetic": 1, "Algebra": 7, "Geometry": 9, "Trigonometry": 10,
        "Statistics_and_Probability": 9, "Pre-Calculus": 11, "Calculus": 12,
        "Advanced_Calculus": 13, "Discrete_Mathematics": 13,
        "Linear_Algebra": 13, "Advanced_Statistics": 13,
        "Mathematical_Proofs_and_Theory": 13,

        # ENGLISH
        "Reading_Literature": 1, "Reading_Informational": 1,
        "Writing": 1, "Language": 1, "Speaking_and_Listening": 1,
        "Literature_Library": 0, # Spans all grades

        # SCIENCE
        "Physical_Science": 1, "Life_Science": 1, "Earth_and_Space_Science": 1, 
        "Engineering_Technology": 1,
        "Science_Library": 0,

        # SOCIAL STUDIES
        "History": 1, "Geography": 1, "Civics_and_Government": 1, "Economics": 1,
        "Historical_Library": 0,
    }

    # Subtopic Overrides (Math & English)
    subtopic_grades = {
        # MATH (Legacy)
        "Recognizing_Shapes": 0, "Number_Sense": 0, "Counting": 0,
        "Basic_Operations": 1, "Number_Properties": 1, "Laws": 1,
        "Place_Values": 2, "Time_and_Calendar": 2, "Money": 2, "Measurements_and_Units": 2,
        "Fractions": 3, "Decimals": 4, "Factors_and_Multiples": 5, "Graphs": 5, "Estimation_and_Rounding": 5,
        "Percentages": 6, "Ratios_and_Proportions": 6, "Negative_Numbers": 6,
        "Algebraic_Expressions": 7, "Linear_Equations": 7,
        "Exponents_and_Square_Roots": 8, "Functions": 8, "Systems_of_Equations": 8,
        "Inequalities": 8, "Pythagorean_Theorem": 8,

        # SCIENCE & SOCIAL STUDIES
        # (Handled by keywords or defaults in logic below)
    }
    
    # Determine Node Type (Core vs Recommended)
    def get_node_type(name, root_topic):
        recommended_roots = ["Literature_Library", "Science_Library", "Historical_Library"]
        if root_topic in recommended_roots:
            return "recommended"
        return "core"

    # Helper to clean string arrow notation
    def get_leaf(full_str):
        return full_str.split("->")[-1]

    # Level 1: Topics
    for topic, subtopics in subject_module.topics_and_subtopics.items():
        base_grade = topic_grades.get(topic, 0)
        
        taxonomy[topic] = {
            "color": subject_module.topic_colors.get(topic, "100,100,100"),
            "grade_level": base_grade,
            "type": get_node_type(topic, topic),
            "subtopics": {}
        }
        
        # Level 2: SubTopics
        for subtopic_str in subtopics:
            subtopic_name = get_leaf(subtopic_str)
            # Check override, else inherit topic grade (or try to parse Key_Ideas)
            sub_grade = subtopic_grades.get(subtopic_name, base_grade)
            
            # Smart Guessing for Grades (English/Science/History)
            if "Grade_K" in subtopic_name: sub_grade = 0
            elif "Grade_2" in subtopic_name: sub_grade = 2
            elif "Grade_4" in subtopic_name: sub_grade = 4
            elif "Grade_6" in subtopic_name: sub_grade = 6
            elif "Grade_9" in subtopic_name: sub_grade = 9
            elif "Grade_11" in subtopic_name: sub_grade = 11

            sub_node = {
                "grade_level": sub_grade,
                "type": get_node_type(subtopic_name, topic),
                "subtopics": {}
            }
            taxonomy[topic]["subtopics"][subtopic_name] = sub_node
            
            # Level 3: SubSubTopics
            if subtopic_str in subject_module.subsub_topics:
                for subsub_str in subject_module.subsub_topics[subtopic_str]:
                    subsub_name = get_leaf(subsub_str)
                    
                    subsub_node = {
                        "grade_level": sub_grade, # Inherit
                        "type": get_node_type(subsub_name, topic),
                        "concepts": []
                    }
                    sub_node["subtopics"][subsub_name] = subsub_node
                    
                    # Level 4: Concepts
                    if subsub_str in subject_module.subsubsub_topics:
                        for concept_str in subject_module.subsubsub_topics[subsub_str]:
                            concept_name = get_leaf(concept_str)
                            # English/Science/History Concept Grade overrides
                            # Hacky heuristic for concepts that have grade bands in name/comment context
                            c_grade = sub_grade
                            # (Note: In raw files we might not have the grade in the key name, 
                            # but if we did or if we added logic here, it would work.
                            # For now, defaulting to subtopic grade is acceptable for broad buckets)
                            
                            concept_obj = {
                                "label": concept_name,
                                "grade_level": c_grade,
                                "type": get_node_type(concept_name, topic),
                                "description": concept_name.replace("_", " ")
                            }
                            subsub_node["concepts"].append(concept_obj)

    final_json = {
        "subject": output_subject_name,
        "taxonomy": taxonomy
    }
    
    return final_json

if __name__ == "__main__":
    # Convert Math
    if "math_raw" in sys.modules:
        math_data = parse_taxonomy(math_raw, "Math")
        with open(os.path.join(os.path.dirname(__file__), '../data/knowledge_graphs/math.json'), 'w') as f:
            json.dump(math_data, f, indent=4)
        print("Converted Math.")

    # Convert English
    if "english_raw" in sys.modules:
        eng_data = parse_taxonomy(english_raw, "English")
        with open(os.path.join(os.path.dirname(__file__), '../data/knowledge_graphs/english.json'), 'w') as f:
            json.dump(eng_data, f, indent=4)
        print("Converted English.")

    # Convert Science
    if "science_raw" in sys.modules:
        sci_data = parse_taxonomy(science_raw, "Science")
        with open(os.path.join(os.path.dirname(__file__), '../data/knowledge_graphs/science.json'), 'w') as f:
            json.dump(sci_data, f, indent=4)
        print("Converted Science.")
    
    # Convert Social Studies (as History)
    if "social_studies_raw" in sys.modules:
        # Note: mapping subject_name "Social_Studies" will output "History" inside the function
        hist_data = parse_taxonomy(social_studies_raw, "Social_Studies") 
        with open(os.path.join(os.path.dirname(__file__), '../data/knowledge_graphs/history.json'), 'w') as f:
            json.dump(hist_data, f, indent=4)
        print("Converted Social Studies (to history.json).")
