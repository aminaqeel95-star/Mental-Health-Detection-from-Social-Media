import pandas as pd
import os
import argparse

def prepare_data(input_path, output_path, n=100):
    """
    Samples 100 random rows for manual NER annotation.
    """
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    df = pd.read_csv(input_path)
    
    # Sample
    sample_df = df.sample(n=n, random_state=42)
    
    # Keep only relevant columns
    # Assuming 'text' and 'id' exist. If 'id' not exist, create index.
    if 'id' not in sample_df.columns:
        if 'post_id' in sample_df.columns:
            sample_df['id'] = sample_df['post_id']
        else:
            sample_df = sample_df.reset_index().rename(columns={"index": "id"})
            
    # Prepare output DF
    out_df = sample_df[['id', 'text']].copy()
    out_df['gold_symptoms'] = "" # Empty column for annotator
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out_df.to_csv(output_path, index=False)
    
    print(f"Sampled {n} posts to {output_path}")
    print("INSTRUCTIONS FOR ANNOTATOR:")
    print("1. Open the CSV file.")
    print("2. In 'gold_symptoms' column, list explicit symptoms found in 'text', separated by commas.")
    print("Example: 'anxiety, panic attack, sad'")
    print("Do not annotate disorders or treatments.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="DATA/dreaddit-train.csv")
    parser.add_argument("--output", default="evaluation/ner_annotation_task.csv")
    args = parser.parse_args()
    
    prepare_data(args.input, args.output)
