import os

class OntologyRAG:
    """
    Ontology-Only RAG pipeline for clinical symptom-disorder mapping.
    Handles extraction from internet, caching, and keyword-based retrieval.
    """
    def __init__(self, prompt_path=None):
        self.system_prompt = None
        self.symptom_map = {}
        # Clinically Valid Mappings (Derived from HPO)
        self.clinical_mappings = {
            "anxiety": "Anxiety",
            "anticipatory anxiety": "Anxiety",
            "panic attack": "Anxiety",
            "social anxiety": "Anxiety",
            "agoraphobia": "Anxiety",
            "phobia": "Anxiety",
            "depression": "Depression",
            "depressed mood": "Depression",
            "suicidal ideation": "Depression",
            "tearfulness": "Depression",
            "hopelessness": "Depression",
            "posttraumatic stress symptom": "Stress",
            "intense psychological distress": "Stress"
        }
        if prompt_path:
            self.load_prompt(prompt_path)

    def load_prompt(self, path):
        """Loads a prompt template from a file."""
        with open(path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
        print(f"Loaded prompt from {path}")

    def load_ontology(self):
        """
        Loads the HPO ontology using the OntologyLoader.
        This will download and cache the file from the internet if needed.
        """
        try:
            from src.ontology_loader import load_hpo_ontology
        except ImportError:
            from ontology_loader import load_hpo_ontology
            
        print("Initializing Ontology Retrieval System...")
        self.symptom_map = load_hpo_ontology()
        print(f"Ontology loaded with {len(self.symptom_map)} concepts.")

    def retrieve_context(self, symptoms, top_n=5):
        """
        Performs a local keyword-based retrieval from the HPO symptom map.
        Matches symptoms against HPO labels and synonyms.
        Returns a tuple of (retrieved_chunks, supported_symptoms).
        """
        if not self.symptom_map:
            self.load_ontology()
            
        results = []
        for hp_id, synonyms in self.symptom_map.items():
            # Check for overlap with any input symptom
            match_score = 0
            concept_matched_symptoms = set()
            
            for s in symptoms:
                s_lower = s.lower().strip()
                for syn in synonyms:
                    syn_lower = syn.lower()
                    if s_lower in syn_lower or syn_lower in s_lower:
                        match_score += 1
                        concept_matched_symptoms.add(s)
                        break # Only count each symptom once per concept
            
            if match_score > 0:
                # Construct a text representation for the "Ontology Unit"
                context_text = f"Concept: {hp_id}\nLabels/Synonyms: {', '.join(synonyms)}"
                
                # Check for explicit clinical mappings (HPO-based)
                for s in concept_matched_symptoms:
                    s_lower = s.lower().strip()
                    for mapping_key, disorder in self.clinical_mappings.items():
                        if mapping_key in s_lower:
                            context_text += f"\nClinical Mapping (HPO): '{s_lower}' maps to -> {disorder}"
                            break
                            
                results.append((match_score, context_text, concept_matched_symptoms))
        
        # Sort by score and return top N
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:top_n]
        
        chunks = [r[1] for r in top_results]
        supported_symptoms = set()
        for r in top_results:
            supported_symptoms.update(r[2])
            
        return chunks, sorted(list(supported_symptoms))

    def format_prompt(self, symptoms, retrieved_chunks=None, system_prompt=None):
        """
        Formats a prompt by injecting symptoms and ontology context.
        If retrieved_chunks is None, it performs retrieval automatically.
        """
        prompt_template = system_prompt or self.system_prompt
        if not prompt_template:
            return "Error: No prompt template loaded or provided."
            
        supported_symptoms = symptoms # Default to all if chunks provided externally
        if retrieved_chunks is None:
            print("Performing retrieval for context...")
            retrieved_chunks, supported_symptoms = self.retrieve_context(symptoms)
        else:
            # If chunks are provided, we should ideally know which symptoms they support.
            # For simplicity, we assume the caller provides correct symptoms, 
            # or we can try to re-derive them if needed.
            # But usually it's None.
            pass
            
        symptom_str = ", ".join(supported_symptoms)
        context_block = "\n\n".join([f"ONTOLOGY UNIT {i}:\n{c}" for i, c in enumerate(retrieved_chunks, 1)])
        
        # If no chunks were found, provide a fallback message
        if not context_block:
            context_block = "No relevant ontology units found for the provided symptoms."
            symptom_str = "None (No ontology support)"
        
        try:
            return prompt_template.format(
                SYMPTOM_LIST=symptom_str,
                ONTOLOGY_CONTEXT=context_block
            )
        except KeyError as e:
            return f"Error: Prompt template missing placeholder {e}"

if __name__ == "__main__":
    # End-to-End Test
    PROMPT_FILE = "src/prompts/validation_prompt.txt"
    rag = OntologyRAG(prompt_path=PROMPT_FILE)
    
    # Example symptoms from a post
    test_symptoms = ["sadness", "low energy", "fearful", "enjoys pizza"]
    
    print("\n--- Running RAG Pipeline Test ---")
    final_prompt = rag.format_prompt(test_symptoms)
    
    print("\n=== GENERATED PROMPT PREVIEW (Stage 4 Focus) ===")
    # Print SYMPTOMS and small part of context
    print(final_prompt)
    print("================================================")


