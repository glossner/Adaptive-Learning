import json
import os

class GraphNavigator:
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Default to backend/data/knowledge_graphs relative to this file
            data_dir = os.path.join(os.path.dirname(__file__), "data/knowledge_graphs")
        self.data_dir = data_dir
        self.graphs = {}
        self.node_map = {} # path -> node_data
        self.tree = {} # subject -> tree
        self._load_graphs()

    def _load_graphs(self):
        # Load known files
        files = ["science.json", "history.json", "math.json", "english.json"]
        for f in files:
            path = os.path.join(self.data_dir, f)
            if os.path.exists(path):
                try:
                    with open(path, 'r') as file:
                        data = json.load(file)
                        subject = data.get("subject")
                        taxonomy = data.get("taxonomy", {})
                        self.tree[subject] = taxonomy
                        self._index_nodes(subject, taxonomy)
                except Exception as e:
                    print(f"Error loading {f}: {e}")

    def _index_nodes(self, subject, taxonomy):
        # Recursively index nodes by full path for easy lookup
        # Path format: Subject/Topic/Subtopic/SubSubTopic/Concept
        
        for topic_key, topic_data in taxonomy.items():
            path = f"{subject}/{topic_key}"
            self.node_map[path] = {**topic_data, "kind": "topic", "path": path, "parent": None}
            
            subtopics = topic_data.get("subtopics", {})
            for sub_key, sub_data in subtopics.items():
                sub_path = f"{path}/{sub_key}"
                self.node_map[sub_path] = {**sub_data, "kind": "subtopic", "path": sub_path, "parent": path}
                
                subsubtopics = sub_data.get("subtopics", {})
                for subsub_key, subsub_data in subsubtopics.items():
                    subsub_path = f"{sub_path}/{subsub_key}"
                    self.node_map[subsub_path] = {**subsub_data, "kind": "subsubtopic", "path": subsub_path, "parent": sub_path}
                    
                    concepts = subsub_data.get("concepts", [])
                    for i, concept in enumerate(concepts):
                        c_label = concept.get("label")
                        c_path = f"{subsub_path}/{c_label}"
                        # Concept structure in JSON is a bit lean, enrich it
                        self.node_map[c_path] = {
                            **concept, 
                            "kind": "concept", 
                            "path": c_path, 
                            "parent": subsub_path,
                            "index": i # Store list index for sequencing
                        }

    def get_node(self, path):
        return self.node_map.get(path)

    def get_next_options(self, completed_nodes, current_grade_level, subject_filter=None):
        """
        Returns a list of available next nodes (paths).
        Logic:
        1. Identify the 'User Frontier'.
           - Usually defined by the most recently completed node? 
           - Or we scan the whole tree?
           - User asked: "from the most recently completed node"
        
        So we take the LAST node in completed_nodes as the anchor.
        
        If completed_nodes is empty:
            Return Entry Point roots (Level 1 Topics) for the subject(s).
        """
        
        # 1. Start Support
        if not completed_nodes:
            options = []
            for subject, taxonomy in self.tree.items():
                if subject_filter and subject != subject_filter:
                    continue
                # Get Topics
                for topic, data in taxonomy.items():
                     if data.get("grade_level", 99) <= current_grade_level:
                         options.append(f"{subject}/{topic}")
            return options

        # 2. Traversal from Last Completed
        # Check the last one
        last_completed_path = completed_nodes[-1]
        
        # If the last completed path is not in our loaded graphs (e.g. from a file we failed to load), fallback
        if last_completed_path not in self.node_map:
            # Fallback: Scan for any available root?
            # For now, just return empty or roots
            return []

        # We need to find the "Next Sibling" or "Next Logical Step"
        # Algorithm:
        # Start at Node N.
        # Check if N has children? (Container completed?) -> usually completed_nodes tracks LEAVES (concepts). 
        # But if we track containers too, we must handle that.
        # Let's assume we track concepts.
        
        # Candidate List
        candidates = []
        
        # Look for immediate next sibling of Last Completed
        next_sibling = self._find_next_sibling(last_completed_path, current_grade_level)
        if next_sibling:
            candidates.append(next_sibling)
        
        # IF no next sibling (Container Finished), Go Up to Parent and find ITS next sibling steps
        # "Back up to the non-selected edge"
        # We do this recursively up the chain until we find something OR hit root.
        
        curr = last_completed_path
        while not candidates:
            node = self.node_map.get(curr)
            if not node: break
            
            parent_path = node.get("parent")
            if not parent_path:
                # We are at root (Subject). If we finished a Subject, maybe suggest other Subjects?
                # Or other Topics in Subject.
                
                # Check siblings of the Root (Topics)
                # Actually _find_next_sibling handles siblings of whatever node we pass.
                # So if curr is "Physical_Science", its sibling is "Life_Science".
                # But _find_next_sibling needs to know if the sibling is completed.
                # Problem: self._find_next_sibling as written below usually just returns ONE next. 
                # We need all UNCOMPLETED siblings.
                break
            
            # Check for uncompleted siblings of the CURRENT CONTAINER (parent's children)
            # e.g. We finished "Solids". Parent is "Structure_Elem".
            # We looked for "Solids" next sibling -> found none (List done).
            # Now we look at "Structure_Elem"'s siblings (e.g. "Chemical Reactions").
            
            siblings = self._get_uncompleted_siblings(curr, completed_nodes, current_grade_level)
            if siblings:
                # Found branches!
                candidates.extend(siblings)
                break
            
            # If parent also done, go up again
            curr = parent_path
            
        return candidates

    def _get_uncompleted_siblings(self, node_path, completed_nodes, max_grade):
        """
        Returns a list of sibling paths that are NOT in completed_nodes and fit the grade.
        For Concepts (Linear): Returns [] (handled by _find_next_sibling).
        For Containers (Dicts): Returns all uncompleted siblings.
        """
        node = self.node_map.get(node_path)
        if not node: return []
        
        kind = node.get("kind")
        
        # If it's a concept, we assume strict linearity (Sequence), so no "Choice" of siblings.
        # Unless the user wants to skip concepts? Assuming no.
        if kind == "concept":
            return []

        parent_path = node.get("parent")
        children_map = {}
        base_path = ""

        if not parent_path:
            # Root Topic siblings (e.g. Physical Science vs Life Science)
            # Subject is the first part of path
            subject = node_path.split("/")[0]
            children_map = self.tree.get(subject, {})
            base_path = subject
        else:
            parent = self.node_map.get(parent_path)
            # Subtopics or SubSubTopics
            children_map = parent.get("subtopics", {})
            base_path = parent_path

        siblings = []
        for key, data in children_map.items():
            child_path = f"{base_path}/{key}"
            
            # skip self (though usually self is completed if we are here?)
            # Wait, if we are looking for siblings AFTER finishing 'node_path', 
            # 'node_path' is in completed_nodes.
            if child_path in completed_nodes:
                continue
            
            # Check grade
            if data.get("grade_level", 99) > max_grade:
                continue
                
            siblings.append(child_path)
            
        return siblings

    def _find_next_sibling(self, node_path, max_grade):
        """
        Strict Next for ordered lists (Concepts). 
        Returns single path or None.
        """
        node = self.node_map.get(node_path)
        if not node or node.get("kind") != "concept":
            return None
            
        parent = self.node_map.get(node.get("parent"))
        concepts = parent.get("concepts", [])
        
        idx = node.get("index", -1)
        if idx != -1 and idx + 1 < len(concepts):
            next_c = concepts[idx+1]
            if next_c.get("grade_level", 99) <= max_grade:
                return f"{node.get('parent')}/{next_c.get('label')}"
        
        return None
