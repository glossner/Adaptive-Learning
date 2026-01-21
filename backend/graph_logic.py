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
        # Path format: Topic->Subtopic->SubSubTopic->Concept (Subject implicit/separate)
        # Note: KnowledgeGraph.py uses "->" separator.
        
        for topic_key, topic_data in taxonomy.items():
            # In KG, root topics (Level 1) are just "TopicName" (ID).
            # But here we might want to track subject?
            # KG IDs: "Physical_Science", "Arithmetic"
            
            path = topic_key 
            # We track "subject" in the node data to separate namespaces if needed
            self.node_map[path] = {**topic_data, "kind": "topic", "path": path, "parent": None, "subject": subject}
            
            subtopics = topic_data.get("subtopics", {})
            for sub_key, sub_data in subtopics.items():
                sub_path = f"{path}->{sub_key}"
                self.node_map[sub_path] = {**sub_data, "kind": "subtopic", "path": sub_path, "parent": path, "subject": subject}
                
                subsubtopics = sub_data.get("subtopics", {})
                for subsub_key, subsub_data in subsubtopics.items():
                    subsub_path = f"{sub_path}->{subsub_key}"
                    self.node_map[subsub_path] = {**subsub_data, "kind": "subsubtopic", "path": subsub_path, "parent": sub_path, "subject": subject}
                    
                    concepts = subsub_data.get("concepts", [])
                    for i, concept in enumerate(concepts):
                        c_label = concept.get("label")
                        c_path = f"{subsub_path}->{c_label}"
                        # Concept structure in JSON is a bit lean, enrich it
                        self.node_map[c_path] = {
                            **concept, 
                            "kind": "concept", 
                            "path": c_path, 
                            "parent": subsub_path,
                            "index": i, # Store list index for sequencing
                            "subject": subject
                        }

    def get_node(self, path):
        return self.node_map.get(path)

    def get_next_options(self, completed_nodes, current_grade_level, subject_filter=None):
        """
        Returns a list of available next nodes (paths).
        """
        
        # 1. Start Support
        if not completed_nodes:
            options = []
            for subject, taxonomy in self.tree.items():
                if subject_filter and subject != subject_filter:
                    continue
                # Get Topics (Root IDs)
                for topic, data in taxonomy.items():
                     if data.get("grade_level", 99) <= current_grade_level:
                         # Root ID is just topic name in KG scheme
                         options.append(topic) 
            return options

        # 2. Traversal from Last Completed
        last_completed_path = completed_nodes[-1]
        
        if last_completed_path not in self.node_map:
            # Fallback: Scan for roots?
            return []

        candidates = []
        
        # Look for immediate next sibling of Last Completed
        next_sibling = self._find_next_sibling(last_completed_path, current_grade_level)
        if next_sibling:
            candidates.append(next_sibling)
        
        # Back up to parents
        curr = last_completed_path
        while not candidates:
            node = self.node_map.get(curr)
            if not node: break
            
            parent_path = node.get("parent")
            if not parent_path:
                # We are at root.
                break
            
            siblings = self._get_uncompleted_siblings(curr, completed_nodes, current_grade_level)
            if siblings:
                candidates.extend(siblings)
                break
            
            curr = parent_path
            
        return candidates

    def _get_uncompleted_siblings(self, node_path, completed_nodes, max_grade):
        node = self.node_map.get(node_path)
        if not node: return []
        
        kind = node.get("kind")
        if kind == "concept":
            return []

        parent_path = node.get("parent")
        children_map = {}
        base_path = ""

        if not parent_path:
            # Root Topic siblings
            subject = node.get("subject")
            children_map = self.tree.get(subject, {})
            base_path = "" # Root has no prefix
        else:
            parent = self.node_map.get(parent_path)
            children_map = parent.get("subtopics", {})
            base_path = parent_path

        siblings = []
        for key, data in children_map.items():
            if base_path:
                child_path = f"{base_path}->{key}"
            else:
                child_path = key # Root topic ID is just key
            
            if child_path in completed_nodes:
                continue
            if data.get("grade_level", 99) > max_grade:
                continue
                
            siblings.append(child_path)
            
        return siblings

    def _find_next_sibling(self, node_path, max_grade):
        node = self.node_map.get(node_path)
        if not node or node.get("kind") != "concept":
            return None
            
        parent = self.node_map.get(node.get("parent"))
        concepts = parent.get("concepts", [])
        
        idx = node.get("index", -1)
        if idx != -1 and idx + 1 < len(concepts):
            next_c = concepts[idx+1]
            if next_c.get("grade_level", 99) <= max_grade:
                return f"{node.get('parent')}->{next_c.get('label')}"
        
        return None
