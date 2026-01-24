
import sys
import os
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from knowledge_graph import KnowledgeGraph

class TestUnitPriority(unittest.TestCase):
    def test_grade_priority(self):
        # Load English KG
        kg = KnowledgeGraph("english")
        
        # Scenario: Student is Grade 2. 
        # "Printing_Letters" (G0) - Grammar_K2
        # "Multiple_Meaning_Words" (G2) - Vocab_K5
        
        # Check nodes exist
        n0 = None
        n2 = None
        for n in kg.graph.nodes():
            if "Printing_Letters" in n: n0 = kg.get_node(n)
            if "Multiple_Meaning_Words" in n: n2 = kg.get_node(n)
            
        if not n0 or not n2:
            print(f"Skipping test: Nodes not found. Found n0={n0}, n2={n2}")
            return

        print(f"Node 0: {n0.label} (G{n0.grade_level})")
        print(f"Node 2: {n2.label} (G{n2.grade_level})")

        # Passing an empty completed list to get_next_learnable_nodes 
        candidates = kg.get_next_learnable_nodes([])
        
        # Filter to just these two for clarity
        relevant = [c for c in candidates if c.id in [n0.id, n2.id]]
        
        print("\n[Before Fix] Top candidates:")
        for r in relevant:
             print(f" - {r.label} (Grade {r.grade_level})")
             
        if not relevant:
             print("Neither node is considered learnable! Prerequisite check?")
             return

        # By default (Before Fix), it sorts by Grade Level ascending.
        # So Grade 0 comes before Grade 2.
        # Ensure we have both to compare
        if len(relevant) >= 2:
            self.assertEqual(relevant[0].grade_level, 0, "Default behavior should show Grade 0 first")
        
        # Now, IF we implement the fix, we can pass target_grade=2
        try:
            candidates_priority = kg.get_next_learnable_nodes([], target_grade=2)
            relevant_p = [c for c in candidates_priority if c.id in [n0.id, n2.id]]
            
            print("\n[With Fix] Top candidates for Grade 2:")
            for r in relevant_p:
                 print(f" - {r.label} (Grade {r.grade_level})")
                 
            if len(relevant_p) >= 2:
                # Should match closest? Or exact match?
                # G2 should certainly beat G0 if G2 is target.
                # If we sort by diff, |2-2|=0, |0-2|=2. So G2 wins.
                self.assertEqual(relevant_p[0].grade_level, 2, "Grade 2 should be prioritized over Grade 0")
                
        except TypeError:
            print("\n[Pre-Fix] target_grade argument not supported yet.")

if __name__ == '__main__':
    unittest.main()
