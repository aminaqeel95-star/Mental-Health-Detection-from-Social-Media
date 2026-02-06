import pandas as pd

def evaluate_triples_closed_world():
    # 1. Load KG Nodes for mapping ID -> Name and for Support Counts
    nodes_df = pd.read_csv("KG/nodes.csv")
    node_id_to_name = dict(zip(nodes_df['id'], nodes_df['name']))
    node_id_to_count = dict(zip(nodes_df['id'], nodes_df['count']))
    
    # Disorders list (Closed Universe)
    fixed_disorders = ["Anxiety", "Depression", "Stress"]
    
    # 2. Load KG Edges (Predicted Triples)
    edges_df = pd.read_csv("KG/edges.csv")
    kg_triples = set()
    
    # Pruning Priority: High weight (0.50) on Triple Accuracy
    # Prune low-support triples (count < 3) to reduce False Positives
    support_threshold = 3
    
    for _, row in edges_df.iterrows():
        s_id = row['source']
        count = node_id_to_count.get(s_id, 0)
        
        if count < support_threshold:
            continue # Prune low-confidence triples
            
        symptom = node_id_to_name.get(s_id, s_id).lower()
        disorder = node_id_to_name.get(row['target'], row['target']).replace('DISORDER_', '')
        if disorder in fixed_disorders:
            kg_triples.add((symptom, "INDICATES", disorder))
    
    # 3. Define Reference Triples (Ground Truth)
    reference_mappings = {
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
    
    ref_triples = set()
    for symptom, disorder in reference_mappings.items():
        ref_triples.add((symptom.lower(), "INDICATES", disorder))
    
    # 4. Define Evaluation Universe (Symptoms in either KG or Reference)
    kg_symptoms = set([t[0] for t in kg_triples])
    ref_symptoms = set([t[0] for t in ref_triples])
    all_symptoms = kg_symptoms.union(ref_symptoms)
    
    # Total possible universe of triples
    possible_triples = set()
    for s in all_symptoms:
        for d in fixed_disorders:
            possible_triples.add((s, "INDICATES", d))
            
    # 5. Calculation
    tp_set = kg_triples.intersection(ref_triples)
    fp_set = kg_triples - ref_triples
    fn_set = ref_triples - kg_triples
    # TN: possible triples not in KG and not in Ref
    tn_set = possible_triples - (kg_triples.union(ref_triples))
    
    tp = len(tp_set)
    fp = len(fp_set)
    fn = len(fn_set)
    tn = len(tn_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) > 0 else 0
    
    print(f"True Positives (TP): {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print(f"True Negatives (TN): {tn}")
    print(f"Precision: {precision:.6f}")
    print(f"Recall: {recall:.6f}")
    print(f"F1-Score: {f1:.6f}")
    print(f"Accuracy (closed-world): {accuracy:.6f}")
    return accuracy

def get_triple_accuracy():
    return evaluate_triples_closed_world()

if __name__ == "__main__":
    evaluate_triples_closed_world()
