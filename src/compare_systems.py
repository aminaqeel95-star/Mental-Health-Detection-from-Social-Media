import pandas as pd
import os

class SystemComparator:
    def __init__(self):
        # KG Mapping Rules (from kg_builder.py)
        self.kg_rules = {
            "Depression": ["sad", "depressed", "hopeless", "unhappy", "cry", "gloom", "misery", "kill myself", "suicide", "die"],
            "Anxiety": ["anxiety", "anxious", "fear", "nervous", "panic", "scared", "worry"],
            "Stress": ["stress", "stressed", "overwhelmed", "pressure", "burnout", "exhausted", "agitation"]
        }

        # RAG Clinical Mappings (from rag_pipeline.py)
        self.rag_mappings = {
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

        # Load counts for support-based stabilization
        try:
            nodes_df = pd.read_csv("KG/nodes.csv")
            self.symptom_to_count = dict(zip(nodes_df['name'].str.lower(), nodes_df['count']))
        except:
            self.symptom_to_count = {}

        # Ambiguous or weak symptoms to ignore
        self.ambiguous_symptoms = [
            "odd", "negative", "negative thoughts", "on edge", "bad", "feeling bad",
            "low", "down", "empty", "blue", "mad", "angry", "screaming"
        ]

    def _filter_symptoms(self, symptoms):
        # Filter by ambiguity AND low support (confidence)
        filtered = []
        for s in symptoms:
            s_low = s.lower()
            if s_low in self.ambiguous_symptoms:
                continue
            # Prune very rare symptoms (likely noise)
            if self.symptom_to_count.get(s_low, 100) < 2:
                continue
            filtered.append(s)
        return filtered

    def predict_kg(self, symptoms):
        filtered = self._filter_symptoms(symptoms)
        if not filtered: filtered = symptoms # Fallback if all filtered
        
        counts = {"Depression": 0, "Anxiety": 0, "Stress": 0}
        for symptom in filtered:
            s_lower = symptom.lower()
            for disorder, keywords in self.kg_rules.items():
                if any(kw in s_lower for kw in keywords):
                    counts[disorder] += 1
        
        # Select best match
        max_val = max(counts.values())
        if max_val == 0:
            return "None"
        
        # Handle ties (alphabetical for consistency)
        best = [d for d, v in counts.items() if v == max_val]
        return sorted(best)[0]

    def predict_rag(self, symptoms):
        filtered = self._filter_symptoms(symptoms)
        if not filtered: filtered = symptoms # Fallback if all filtered
        
        counts = {"Depression": 0, "Anxiety": 0, "Stress": 0}
        for symptom in filtered:
            s_lower = symptom.lower()
            for mapping_key, disorder in self.rag_mappings.items():
                if mapping_key in s_lower:
                    counts[disorder] += 1
                    break # One symptom maps to one disorder in RAG logic
        
        # Select best match
        max_val = max(counts.values())
        if max_val == 0:
            return "None"
        
        best = [d for d, v in counts.items() if v == max_val]
        return sorted(best)[0]

    def run(self, input_file, output_dir="evaluation"):
        print(f"Loading symptoms from {input_file}...")
        df = pd.read_csv(input_file)
        
        # Group symptoms by post_id
        post_data = df.groupby('post_id')['symptom'].apply(list).to_dict()
        
        results = []
        agreement_count = 0
        conflict_count = 0
        
        for post_id, symptoms in post_data.items():
            kg_pred = self.predict_kg(symptoms)
            rag_pred = self.predict_rag(symptoms)
            
            # Per user rule: Return MATCH or MISMATCH
            comparison = "MATCH" if kg_pred == rag_pred else "MISMATCH"
            
            if comparison == "MATCH":
                agreement_count += 1
            else:
                conflict_count += 1
                
            results.append({
                "post_id": post_id,
                "symptoms": ", ".join(symptoms),
                "KG Disorder": kg_pred,
                "Ontology-RAG Disorder": rag_pred,
                "Comparison Result": comparison
            })
            
        # Export detailed results
        os.makedirs(output_dir, exist_ok=True)
        results_df = pd.DataFrame(results)
        results_df.to_csv(f"{output_dir}/system_comparison_detailed.csv", index=False)
        
        # Export summary
        total = len(results)
        agreement_rate = (agreement_count / total) * 100 if total > 0 else 0
        conflict_rate = (conflict_count / total) * 100 if total > 0 else 0
        
        report = f"""SYSTEM COMPARISON REPORT (KG vs RAG)
=====================================
Total Posts Analyzed: {total}
Total Agreement (MATCH): {agreement_count} ({agreement_rate:.2f}%)
Total Conflicts (MISMATCH): {conflict_count} ({conflict_rate:.2f}%)

METHODOLOGY:
- KG Prediction: Highest keyword matches based on kg_builder.py rules.
- RAG Prediction: Highest clinical mapping matches based on rag_pipeline.py rules.
- Comparison: Binary match/mismatch on final predicted disorder label.
"""
        with open(f"{output_dir}/system_comparison_summary.txt", "w") as f:
            f.write(report)
            
        print("\n" + report)
        print(f"Detailed results saved to {output_dir}/system_comparison_detailed.csv")
        return agreement_rate / 100.0

def get_comparison_accuracy(input_file="KG/post_symptoms.csv"):
    comparator = SystemComparator()
    return comparator.run(input_file)

if __name__ == "__main__":
    comparator = SystemComparator()
    comparator.run("KG/post_symptoms.csv")
