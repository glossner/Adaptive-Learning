import sys
import os
import unittest

# Add backend directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from knowledge_graph import KnowledgeGraph

class TestMathOrder(unittest.TestCase):
    def test_measurement_sequence(self):
        kg = KnowledgeGraph("math")
        
        # ID prefixes might vary if I normalized spaces.
        # Arithmetic -> Measurements_and_Units -> Feet
        
        feet_id = "Arithmetic->Measurements_and_Units->Feet"
        conversion_id = "Arithmetic->Measurements_and_Units->Standard_to_Metric"
        
        # Verify nodes exist
        self.assertIsNotNone(kg.get_node(feet_id), "Feet node not found")
        self.assertIsNotNone(kg.get_node(conversion_id), "Conversion node not found")
        
        # Check explicit prerequisite edge
        # The list order in JSON should create: Feet -> Pounds -> ... -> Standard_to_Metric
        # So Feet should be an ancestor of Standard_to_Metric
        
        import networkx as nx
        is_ancestor = nx.has_path(kg.graph, feet_id, conversion_id)
        self.assertTrue(is_ancestor, "Feet should be a prerequisite for Standard_to_Metric")
        
        # Check get_next_learnable_nodes
        # If we have done nothing, Feet should be available (assuming Arithmetic parent is open?)
        # Actually, Arithmetic is a Topic. Is it "done"?
        # KG logic: if parent is a Topic, it might be a prereq?
        # knowledge_graph.py: _parse_taxonomy adds edge Parent -> Child.
        # So Arithmetic -> Measurements_and_Units -> Feet.
        # BUT get_next_learnable_nodes checks:
        # "Prerequisites are ONLY other 'concept' nodes." (lines 135-138 of knowledge_graph.py)
        # It ignores Topic predecessors!
        
        # So Feet should be learnable immediately if it has no OTHER concept prereqs.
        
        candidates = kg.get_next_learnable_nodes([], target_grade=2)
        candidate_ids = [c.id for c in candidates]
        
        print("Candidates[0:5]:", candidate_ids[0:5])
        
        self.assertIn(feet_id, candidate_ids)
        self.assertNotIn(conversion_id, candidate_ids, "Conversion should NOT be learnable yet (requires Feet)")
        
        # If we complete Feet...Liters, then Conversion should appear.
        # Let's verify strict prereq chain.
        # Predecessor of Conversion should be Liters?
        liter_id = "Arithmetic->Measurements_and_Units->Liters"
        preds = list(kg.graph.predecessors(conversion_id))
        print(f"Predecessors of {conversion_id}: {preds}")
        self.assertIn(liter_id, preds)

if __name__ == '__main__':
    unittest.main()
