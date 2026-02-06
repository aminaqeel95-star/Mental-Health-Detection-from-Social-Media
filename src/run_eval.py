import pandas as pd
import argparse
import os
import re
import nltk
import ast
import sys
from nltk.stem import WordNetLemmatizer

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Ensure NLTK resources
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)

try:
    from src.ner_engine import OntologyNER
except ImportError:
    from ner_engine import OntologyNER

# Validation Data (Internal Fallback)
HARDCODED_EXAMPLES = [
    {
        "id": 1,
        "text": "I feel so anxious and my heart is pounding.",
        "gold_symptoms": "anxious, heart is pounding"
    },
    {
        "id": 2,
        "text": "Depression hits hard, I can't sleep.",
        "gold_symptoms": "depression, can't sleep"
    },
    {
        "id": 3,
        "text": "Just stressed out.",
        "gold_symptoms": "stressed"
    }
]

def load_dreaddit_lookup(dreaddit_path="DATA/dreaddit-train.csv"):
    """Loads a lookup dictionary from post_id to text."""
    if not os.path.exists(dreaddit_path):
        return {}
    try:
        df = pd.read_csv(dreaddit_path)
        return dict(zip(df['id'], df['text']))
    except Exception:
        return {}

def parse_gold_entry(entry, ner_engine):
    """Parses a gold entry into a set of HPO Concept IDs."""
    if pd.isna(entry) or str(entry).strip() == "":
        return set()
    
    entry_str = str(entry).strip()
    terms = []
    
    if entry_str.startswith("[") and entry_str.endswith("]"):
        try:
            terms = ast.literal_eval(entry_str)
        except:
            terms = [entry_str]
    else:
        terms = [t.strip() for t in entry_str.split(",")]
        
    concept_ids = set()
    for term in terms:
        term_lower = str(term).lower()
        c_id = ner_engine.term_to_id.get(term_lower)
        if not c_id and ner_engine.lemmatizer:
             lem_term = " ".join([ner_engine.lemmatizer.lemmatize(w) for w in term_lower.split()])
             c_id = ner_engine.term_to_id.get(lem_term)
        if c_id:
            concept_ids.add(c_id)
    return concept_ids

def get_tokens(text):
    """Simple tokenizer."""
    return set(re.findall(r'\w+', text.lower()))

def lemmatize_text(text, lemmatizer):
    """Lemmatizes a string (multi-word aware)."""
    return " ".join([lemmatizer.lemmatize(w) for w in text.split()])

def is_relaxed_match(gold, pred, threshold=0.5):
    """Checks if predicted entity overlaps with gold entity by at least threshold tokens."""
    g_tokens = get_tokens(gold)
    p_tokens = get_tokens(pred)
    if not g_tokens: return False
    
    intersection = g_tokens.intersection(p_tokens)
    overlap_ratio = len(intersection) / len(g_tokens)
    return overlap_ratio >= threshold

def calculate_metrics_strict(gold_set, pred_set):
    gold_norm = set([g.strip().lower() for g in gold_set if g.strip()])
    pred_norm = set([p.strip().lower() for p in pred_set if p.strip()])
    
    tp = len(gold_norm.intersection(pred_norm))
    fp = len(pred_norm - gold_norm)
    fn = len(gold_norm - pred_norm)
    return tp, fp, fn

def calculate_metrics_concept(gold_set, pred_set, lemmatizer):
    """Concept-Level Evaluation (Lemmatized)."""
    gold_concepts = set([lemmatize_text(g.strip().lower(), lemmatizer) for g in gold_set if g.strip()])
    pred_concepts = set([lemmatize_text(p.strip().lower(), lemmatizer) for p in pred_set if p.strip()])
    
    tp = len(gold_concepts.intersection(pred_concepts))
    fp = len(pred_concepts - gold_concepts)
    fn = len(gold_concepts - pred_concepts)
    return tp, fp, fn

def calculate_metrics_strict_concept(gold_ids, pred_ids):
    """Strict Concept-Level Evaluation (HPO ID Match)."""
    tp = len(gold_ids.intersection(pred_ids))
    fp = len(pred_ids - gold_ids)
    fn = len(gold_ids - pred_ids)
    return tp, fp, fn

def calculate_metrics_relaxed(gold_set, pred_set, threshold=0.5):
    gold_list = [g.strip().lower() for g in gold_set if g.strip()]
    pred_list = [p.strip().lower() for p in pred_set if p.strip()]
    
    tp = 0
    matched_gold = [False] * len(gold_list)
    matched_pred = [False] * len(pred_list)
    
    for p_idx, p in enumerate(pred_list):
        for g_idx, g in enumerate(gold_list):
            if not matched_gold[g_idx] and is_relaxed_match(g, p, threshold):
                tp += 1
                matched_gold[g_idx] = True
                matched_pred[p_idx] = True
                break
                
    fp = matched_pred.count(False)
    fn = matched_gold.count(False)
    return tp, fp, fn

def compute_and_print_stats(name, total_tp, total_fp, total_fn, total_gold):
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    denominator = total_tp + total_fp + total_fn
    accuracy = total_tp / denominator if denominator > 0 else 0
    
    return {
        "Mode": name,
        "TP": total_tp,
        "FP": total_fp,
        "FN": total_fn,
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1": round(f1, 4),
        "Accuracy (E)": round(accuracy, 4)
    }

def run_evaluation_suite(df, ner, name, mode="strict", param=None, lookup=None):
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_gold = 0
    
    sample_errors = []
    lemmatizer = WordNetLemmatizer() if mode == "concept" else None

    for _, row in df.iterrows():
        text = str(row.get('text', ''))
        if (not text or text == 'nan') and lookup:
            text = lookup.get(row.get('id'), '')
            
        gold_raw = row.get('gold_symptoms') if 'gold_symptoms' in row else row.get('gold', '')
        gold_entries = [g.strip().lower() for g in str(gold_raw).split(',') if g.strip()]
        
        matches = ner.extract(text)
        
        if mode == "strict-concept":
            gold_ids = parse_gold_entry(gold_raw, ner)
            if not gold_ids: continue
            pred_ids = set(m['id'] for m in matches)
            tp, fp, fn = calculate_metrics_strict_concept(gold_ids, pred_ids)
            total_gold += len(gold_ids)
            pred_labels, gold_labels = list(pred_ids), list(gold_ids)
        elif mode == "concept":
            tp, fp, fn = calculate_metrics_concept(gold_entries, [m['text'] for m in matches], lemmatizer)
            total_gold += len(gold_entries)
            pred_labels, gold_labels = [m['text'] for m in matches], gold_entries
        elif mode == "relaxed":
            tp, fp, fn = calculate_metrics_relaxed(gold_entries, [m['text'] for m in matches], threshold=param)
            total_gold += len(gold_entries)
            pred_labels, gold_labels = [m['text'] for m in matches], gold_entries
        else: # strict
            tp, fp, fn = calculate_metrics_strict(gold_entries, [m['text'] for m in matches])
            total_gold += len(gold_entries)
            pred_labels, gold_labels = [m['text'] for m in matches], gold_entries
            
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        if (fp > 0 or fn > 0) and len(sample_errors) < 3:
            sample_errors.append({
                "id": row.get('id'),
                "gold": gold_labels,
                "pred": pred_labels
            })
            
    stats = compute_and_print_stats(name, total_tp, total_fp, total_fn, total_gold)
    return stats, sample_errors

def main(annotated_file):
    if os.path.exists(annotated_file):
        df = pd.read_csv(annotated_file)
        # Handle flexible column naming
        gold_col = 'gold_symptoms' if 'gold_symptoms' in df.columns else 'gold'
        if gold_col not in df.columns:
            print(f"Error: Neither 'gold_symptoms' nor 'gold' column found in {annotated_file}")
            return []
        
        df['gold_symptoms'] = df[gold_col].fillna("").astype(str)
        annotated_df = df[df['gold_symptoms'].str.strip() != ""]
    else:
        print(f"Warning: {annotated_file} not found. Using internal validation set.")
        annotated_df = pd.DataFrame(HARDCODED_EXAMPLES)
    
    if len(annotated_df) == 0:
        print(f"\n[!] No annotations found.")
        return []
    
    print(f"\n--- Starting Comparative Evaluation ({len(annotated_df)} posts) ---\n")
    
    lookup = load_dreaddit_lookup()
    ner_hybrid = OntologyNER(improved=True)
    all_reports = []
    
    # 1. Strict Entity-Level
    stats_strict, _ = run_evaluation_suite(annotated_df, ner_hybrid, "Strict Entity-Level", mode="strict", lookup=lookup)
    all_reports.append(stats_strict)
    
    # 2. Concept-Level Evaluation (Lemmatized)
    stats_concept, _ = run_evaluation_suite(annotated_df, ner_hybrid, "Concept-Level (Lemma)", mode="concept", lookup=lookup)
    all_reports.append(stats_concept)
    
    # 3. Strict Concept-Level (HPO ID Match)
    stats_strict_concept, errs_strict = run_evaluation_suite(annotated_df, ner_hybrid, "Strict Concept-Level (ID)", mode="strict-concept", lookup=lookup)
    all_reports.append(stats_strict_concept)
    
    # 4. Relaxed Match (50% Overlap)
    stats_relaxed, _ = run_evaluation_suite(annotated_df, ner_hybrid, "Relaxed Match (50%)", mode="relaxed", param=0.5, lookup=lookup)
    all_reports.append(stats_relaxed)
    
    report_df = pd.DataFrame(all_reports)
    print("\n=== NER PERFORMANCE COMPARISON ===")
    print(report_df.to_string(index=False))
    
    print("\n[METHODOLOGY NOTES]")
    print("- Strict Entity-Level: Exact surface match for every independent mention.")
    print("- Concept-Level (Lemma): Lemmatizes and deduplicates surface form concepts.")
    print("- Strict Concept-Level (ID): Evaluates exact matches on HPO Concept IDs (Recommended).")
    print("- Accuracy (E): Reported as TP / (TP + FP + FN).")
    
    print("\n=== ERROR ANALYSIS (Strict Concept-Level) ===")
    for err in errs_strict:
        print(f"Post {err['id']}:")
        print(f"  Gold IDs: {err['gold']}")
        print(f"  Pred IDs: {err['pred']}")
        
    return all_reports

def get_ner_recall():
    reports = main("evaluation/ner_annotation_task.csv")
    for r in reports:
        if r["Mode"] == "Strict Concept-Level (ID)":
            return r["Recall"]
    return 0.0

def get_ner_f1():
    reports = main("evaluation/ner_annotation_task.csv")
    for r in reports:
        if r["Mode"] == "Strict Concept-Level (ID)":
            return r["F1"]
    return 0.0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="evaluation/ner_annotation_task.csv")
    args = parser.parse_args()
    main(args.input)
