
import pandas as pd
import ast
import os

def create_dataset():
    # 1. Load existing annotated data (recovery)
    existing_file = "evaluation/eval_results_detailed.csv"
    existing_data = []
    
    if os.path.exists(existing_file):
        try:
            df_old = pd.read_csv(existing_file)
            # Need to get text from Dreaddit
            dreaddit = pd.read_csv("DATA/dreaddit-train.csv")
            id_to_text = dict(zip(dreaddit['id'], dreaddit['text']))
            
            for _, row in df_old.iterrows():
                rid = row['id']
                gold = row['gold']
                text = id_to_text.get(rid, "")
                if text and gold and str(gold) != "[]":
                    existing_data.append({
                        "id": rid,
                        "text": text,
                        "gold_symptoms": gold
                    })
        except Exception as e:
            print(f"Error reading existing: {e}")

    # 2. Sample new data
    dreaddit = pd.read_csv("DATA/dreaddit-train.csv")
    
    # Exclude existing IDs
    existing_ids = set([x['id'] for x in existing_data])
    remaining_df = dreaddit[~dreaddit['id'].isin(existing_ids)]
    
    needed = 50 - len(existing_data)
    if needed > 0:
        sample = remaining_df.sample(n=needed, random_state=42)
        for _, row in sample.iterrows():
            existing_data.append({
                "id": row['id'],
                "text": row['text'],
                "gold_symptoms": "" # Empty for annotation
            })
            
    # 3. Save
    out_df = pd.DataFrame(existing_data)
    out_path = "evaluation/ner_eval_dataset.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Created {out_path} with {len(out_df)} rows ({len(existing_ids)} pre-filled).")

if __name__ == "__main__":
    create_dataset()
