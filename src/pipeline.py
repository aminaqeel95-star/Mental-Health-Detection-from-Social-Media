import pandas as pd
import argparse
import os
try:
    from src.ner_engine import OntologyNER
    from src.kg_builder import KGBuilder
    from src.ontology_loader import load_hpo_ontology
except ImportError:
    from ner_engine import OntologyNER
    from kg_builder import KGBuilder
    from ontology_loader import load_hpo_ontology

def main():
    parser = argparse.ArgumentParser(description="Mental Health KG Pipeline with Enhanced NER")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of rows to process")
    parser.add_argument("--input", type=str, default="DATA/dreaddit-train.csv", help="Input CSV file")
    parser.add_argument("--min-confidence", type=float, default=0.6, help="Minimum confidence threshold for symptoms")
    parser.add_argument("--remove-negated", action="store_true", help="Remove negated symptoms from extraction")
    
    # Neo4j Args
    parser.add_argument("--neo4j-uri", default="neo4j+s://0525af13.databases.neo4j.io", help="Neo4j URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j Username")
    parser.add_argument("--neo4j-pass", default="IWJ388w0XXwuazMuj2IEvtIO7Tg_AEwknYmfadaWRao", help="Neo4j Password")
    parser.add_argument("--upload", action="store_true", help="Upload to Neo4j")
    
    args = parser.parse_args()
    
    # 1. Load Data
    print(f"Loading data from {args.input}...")
    try:
        df = pd.read_csv(args.input)
    except FileNotFoundError:
        print(f"Error: File {args.input} not found.")
        return

    if args.limit > 0:
        df = df.head(args.limit)
    
    print(f"Processing {len(df)} records...")
    
    # 2. Initialize Components
    print("Initializing enhanced NER system...")
    ontology_data = load_hpo_ontology()
    ner = OntologyNER(improved=True)  # Use improved mode for better recall
    kg = KGBuilder()
    
    print(f"Configuration:")
    print(f"  - Min confidence: {args.min_confidence}")
    print(f"  - Remove negated: {args.remove_negated}")
    print(f"  - Improved NER: Enabled")
    
    # 3. Process
    all_extractions = []
    total_raw_mentions = 0
    total_normalized_symptoms = 0
    
    # For progress tracking
    total = len(df)
    
    for i, row in df.iterrows():
        text = str(row.get('text', ''))
        
        # Extract raw matches
        raw_matches = ner.extract(text)
        total_raw_mentions += len(raw_matches)
        
        # Normalize and Filter (Inline)
        valid_matches = []
        for m in raw_matches:
            if args.remove_negated and m.get('negated'):
                continue
            if m.get('confidence', 0) < args.min_confidence:
                continue
            valid_matches.append(m)
            
        # Deduplicate by ID
        concept_ids = list(set([m['id'] for m in valid_matches]))
        total_normalized_symptoms += len(concept_ids)
        
        # Convert back to match format for KG builder compatibility
        clean_matches = [{'id': concept_id} for concept_id in concept_ids]
        
        # Ingest into KG (Concept-level only)
        kg.collect_symptoms(clean_matches)
        
        if i % 100 == 0:
            print(f"Processed {i}/{total}... (Raw: {total_raw_mentions}, Normalized: {total_normalized_symptoms})")
            
    # 4. Build KG (Rules applied during upload/export)
    print("\nKG Processing Complete.")
    print(f"Total raw mentions: {total_raw_mentions}")
    print(f"Total normalized unique symptoms: {total_normalized_symptoms}")
    print(f"Deduplication rate: {((total_raw_mentions - total_normalized_symptoms) / max(total_raw_mentions, 1) * 100):.1f}%")
    
    # 5. Export
    print("\nExporting KG...")
    kg.export("KG")
    
    # 6. Upload
    if args.upload:
        print("Uploading to Neo4j...")
        kg.upload_to_neo4j(args.neo4j_uri, args.neo4j_user, args.neo4j_pass)
        
    print("Done.")

if __name__ == "__main__":
    main()
