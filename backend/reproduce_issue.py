import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from graph_logic import GraphNavigator

def test_unit_selection():
    nav = GraphNavigator()
    
    # 1. Test "Start Support" for Grade 2 student in English
    print("--- Test 1: Start Support (Grade 2, English) ---")
    grade = 2
    subject = "English"
    completed = []
    
    options = nav.get_next_options(completed, grade, subject_filter=subject)
    print(f"Options for Grade {grade} (Empty History): {options}")
    
    # 2. Check if Printing_Letters is in there?
    if "Printing_Letters" in options:
        print("FAIL: Printing_Letters found in root options!")
    else:
        print("OK: Printing_Letters NOT in root options.")

    # 3. Simulate traversing down if 'Language' is selected?
    # Maybe the frontend calls get_next_options with completed=['Language']?
    print("\n--- Test 2: If 'Language' is marked complete/current ---")
    # 'Language' is a topic. If I mark it as 'completed', what's next?
    # Note: 'Language' is a container. Usually we don't complete containers until all children are done?
    # But let's see what happens if we pass it as 'completed' (maybe implies 'entered'?)
    
    # Actually, in graph_logic, completed_nodes usually contains leaf nodes (concepts).
    # But let's try passing the path to 'Language'.
    options_2 = nav.get_next_options(["Language"], grade, subject_filter=subject)
    print(f"Options after 'Language' completed: {options_2}")

    # 4. Try traversing down to Printing_Letters
    # Path: Language -> Conventions -> Grammar_K2 -> Printing_Letters
    # If I complete 'Language' (root), does it suggest 'Conventions'?
    
    # 5. What if the user is Grade 2?
    # 'Grammar_K2' is Grade 0.
    # 'Printing_Letters' is Grade 0.
    
    # The issue: "Printing_Letters... is the first that shows up".
    # This implies the user sees it.
    
    # Let's inspect what happens if we feed a path that leads to it.
    
if __name__ == "__main__":
    test_unit_selection()
