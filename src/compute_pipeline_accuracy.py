"""
Script to compute the final pipeline accuracy using a weighted formula.

IMPORTANT: NER evaluation uses Concept-Level Recall (not accuracy) due to:
- Recall-oriented extraction design
- Open-world assumption (no True Negatives)
- Concept-level matching (not entity-level)

Formula:
A_final = w1 * R_ner + w2 * A_triple + w3 * A_comparison

Where:
- R_ner (NER Concept-Level Recall) = from concept-level evaluation, w1 = 0.30
- A_triple (Triple Accuracy) = from triple evaluation, w2 = 0.50
- A_comparison (KG-RAG Comparison Accuracy) = from comparison, w3 = 0.20

Note: NER Accuracy is intentionally excluded as misleading in recall-oriented settings.
"""

try:
    from src.run_eval import get_ner_recall, get_ner_f1
    from src.evaluate_triples import get_triple_accuracy
    try:
        from src.compare_systems import get_comparison_accuracy
    except ImportError:
        def get_comparison_accuracy():
            print("Warning: compare_systems module not found. Returning 0.0")
            return 0.0

except ImportError:
    from run_eval import get_ner_recall, get_ner_f1
    from evaluate_triples import get_triple_accuracy
    try:
        from compare_systems import get_comparison_accuracy
    except ImportError:
        def get_comparison_accuracy():
            print("Warning: compare_systems module not found. Returning 0.0")
            return 0.0

def compute_final_accuracy(use_f1=False):
    """
    Compute final pipeline accuracy using concept-level NER metrics.
    
    Args:
        use_f1: If True, use F1-score instead of Recall for NER
    """
    print("Fetching run-time accuracy values from evaluation scripts...\n")
    
    # Stage-wise accuracy values
    if use_f1:
        a1 = get_ner_f1()  # Stage 1: NER (Concept-Level F1)
        stage1_label = "NER (Concept F1)"
    else:
        a1 = get_ner_recall()  # Stage 1: NER (Concept-Level Recall)
        stage1_label = "NER (Concept Recall)"
    
    a2 = get_triple_accuracy()    # Stage 2: Triples
    a3 = get_comparison_accuracy() # Stage 3: KG-RAG Comparison

    # Weights (Optimized)
    w1 = 0.30  # NER
    w2 = 0.40  # Triples
    w3 = 0.30  # Comparison

    # Calculation
    final_accuracy = (w1 * a1) + (w2 * a2) + (w3 * a3)

    print("\n" + "="*60)
    print(f"STAGE-WISE PERFORMANCE METRICS:")
    print("="*60)
    print(f"Stage 1 ({stage1_label}): {a1:.4f} (weight: {w1:.2f})")
    print(f"Stage 2 (Triple Accuracy):       {a2:.4f} (weight: {w2:.2f})")
    print(f"Stage 3 (Comparison Accuracy):   {a3:.4f} (weight: {w3:.2f})")
    print("-" * 60)
    print(f"Final Pipeline Accuracy:         {final_accuracy:.4f}")
    print("="*60)
    
    print("\nNOTE:")
    print("  • NER uses Concept-Level Recall (not entity-level accuracy)")
    print("  • Accuracy excluded for NER due to open-world assumption")
    print("  • This aligns with recall-oriented extraction design")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-f1", action="store_true", 
                       help="Use F1-score instead of Recall for NER")
    args = parser.parse_args()
    
    compute_final_accuracy(use_f1=args.use_f1)

