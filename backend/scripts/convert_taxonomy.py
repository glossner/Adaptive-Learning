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
        # Initialize Topic Node
        # We will determine the TRUE grade level by checking children
        # Default to a high number (e.g. 99) so min() works, or keep the map as a fallback baseline
        initial_grade = topic_grades.get(topic, 99) 
        
        taxonomy[topic] = {
            "color": subject_module.topic_colors.get(topic, "100,100,100"),
            "grade_level": initial_grade, 
            "type": get_node_type(topic, topic),
            "subtopics": {}
        }
        
        topic_min_grade = 99 # Tracker for this level

        # Level 2: SubTopics
        for subtopic_str in subtopics:
            subtopic_name = get_leaf(subtopic_str)
            # Check override, else inherit topic grade (or try to parse Key_Ideas)
            sub_grade_default = subtopic_grades.get(subtopic_name, initial_grade)
            
            # Smart Guessing for Grades in Subtopic Names (English/Science/History)
            if "Grade_K" in subtopic_name: sub_grade_default = 0
            elif "Grade_2" in subtopic_name: sub_grade_default = 2
            elif "Grade_4" in subtopic_name: sub_grade_default = 4
            elif "Grade_6" in subtopic_name: sub_grade_default = 6
            elif "Grade_9" in subtopic_name: sub_grade_default = 9
            elif "Grade_11" in subtopic_name: sub_grade_default = 11
            
            sub_node = {
                "grade_level": sub_grade_default,
                "type": get_node_type(subtopic_name, topic),
                "subtopics": {}
            }
            taxonomy[topic]["subtopics"][subtopic_name] = sub_node
            
            sub_min_grade = 99
            has_concepts_anywhere = False

            # Level 3: SubSubTopics
            if subtopic_str in subject_module.subsub_topics:
                for subsub_str in subject_module.subsub_topics[subtopic_str]:
                    subsub_name = get_leaf(subsub_str)
                    
                    subsub_node = {
                        "grade_level": sub_grade_default, # Placeholder
                        "type": get_node_type(subsub_name, topic),
                        "concepts": []
                    }
                    sub_node["subtopics"][subsub_name] = subsub_node
                    
                    # Level 4: Concepts
                    concept_grades = []
                    if subsub_str in subject_module.subsubsub_topics:
                        for concept_str in subject_module.subsubsub_topics[subsub_str]:
                            concept_name = get_leaf(concept_str)
                            
                            # Grade Parsing Logic (Explicit Suffixes)
                            import re
                            grade_match = re.search(r'\(Grade_([K0-9]+)(?:-[0-9]+)?\)', concept_name)
                            
                            c_grade = sub_grade_default # Default
                            
                            if grade_match:
                                g_str = grade_match.group(1)
                                if g_str == 'K': 
                                    c_grade = 0
                                else:
                                    try:
                                        c_grade = int(g_str)
                                    except:
                                        pass
                                concept_name = re.sub(r'_\(Grade_.*\)', '', concept_name)
                                concept_name = re.sub(r' \(Grade .*\)', '', concept_name)
                            else:
                                # Fallback Heuristics
                                if "K-2" in concept_str: c_grade = 0
                                if "3-5" in concept_str: c_grade = 3
                                if "6-8" in concept_str: c_grade = 6
                                if "9-12" in concept_str: c_grade = 9
                            
                            concept_grades.append(c_grade)
                            
                            concept_obj = {
                                "label": concept_name,
                                "grade_level": c_grade,
                                "type": get_node_type(concept_name, topic),
                                "description": concept_name.replace("_", " ")
                            }
                            subsub_node["concepts"].append(concept_obj)
                    
                    # Bubble Up: SubSubTopic Grade
                    if concept_grades:
                        computed_subsub = min(concept_grades)
                        subsub_node["grade_level"] = computed_subsub
                        if computed_subsub < sub_min_grade:
                            sub_min_grade = computed_subsub
                        has_concepts_anywhere = True
                    else:
                        # Fallback for empty sub-subtopics: trusting the name suffix
                        if "High_School" in subsub_name:
                            subsub_node["grade_level"] = 9
                        elif "Middle_School" in subsub_name:
                            subsub_node["grade_level"] = 6
                        elif "Elementary" in subsub_name:
                            subsub_node["grade_level"] = 1 # or 0, but 1 is safer for "Elementary" generic
                        
                        # If we enforced a grade, treat it as valid for bubble up ONLY if it's the only info we have?
                        # Actually, if it's empty, we should probably let it bubble up so the parents know.
                        # But wait, if it's High School, we don't want it to drag DOWN the parent if the parent has mixed content?
                        # No, if it's High School, it's grade 9. 9 > 1. 
                        # The problem was default being 1.
                        # So let's use this enforced grade for min calculation too, IF we want empty folders to define structure.
                        # Yes, user implies structure > content existence.
                        current_enforced = subsub_node["grade_level"]
                        if current_enforced < sub_min_grade:
                            sub_min_grade = current_enforced
                        # We mark has_concepts_anywhere = True so that the parent actually assumes this grade
                        has_concepts_anywhere = True
            
            # Bubble Up: SubTopic Grade
            # If no concepts found via SubSub, check if Subtopic had concepts directly? 
            # (Current structure is always Topic->Sub->SubSub->Concept for Sci/Hist, but Math might differ)
            if has_concepts_anywhere:
               sub_node["grade_level"] = sub_min_grade
               
            # Update Topic Tracker
            current_sub_grade = sub_node["grade_level"]
            # If sub_grade is 99 (no data), ignore it unless it's the only one?
            # Actually, if sub_grade is still default, trust it (e.g. Math subtopics without explicit children yet)
            if current_sub_grade < topic_min_grade:
                topic_min_grade = current_sub_grade
        
        # Bubble Up: Topic Grade
        if topic_min_grade != 99:
            taxonomy[topic]["grade_level"] = topic_min_grade
        # If still 99, revert to initial (safe fallback for empty topics)
        elif initial_grade != 99:
            taxonomy[topic]["grade_level"] = initial_grade
        else:
            taxonomy[topic]["grade_level"] = 0 # Final fallback

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
