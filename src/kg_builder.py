import pandas as pd
import os

class KGBuilder:
    def __init__(self):
        # Store unique normalized symptoms only
        self.unique_symptoms = set()
        self.disorders = ["Depression", "Anxiety", "Stress"]
        
        # Hard-coded Mapping Rules (Symptom name -> Disorder)
        self.mapping_rules = {
            "Depression": ["sad", "depressed", "hopeless", "unhappy", "cry", "gloom", "misery", "kill myself", "suicide", "die"],
            "Anxiety": ["anxiety", "anxious", "fear", "nervous", "panic", "scared", "worry"],
            "Stress": ["stress", "stressed", "overwhelmed", "pressure", "burnout", "exhausted", "agitation"]
        }

    def collect_symptoms(self, matches):
        """
        Ingests NER matches and stores unique symptom identifiers.
        matches: list of dicts from ner.extract() or normalized concept IDs
        
        Supports both formats:
        - [{'id': 'HP:XXXXXXX', 'term': '...'}] (from NER)
        - [{'id': 'HP:XXXXXXX'}] (from normalizer)
        """
        for match in matches:
            # Handle both HPO IDs and text terms
            if 'id' in match:
                symptom_id = match['id']
                self.unique_symptoms.add(symptom_id)
            elif 'term' in match:
                # Fallback for legacy format
                symptom_name = match['term'].lower().strip()
                if symptom_name:
                    self.unique_symptoms.add(symptom_name)

    def upload_to_neo4j(self, uri, username, password):
        """
        Uploads the concept-level graph to Neo4j:
        (Symptom)-[:INDICATES]->(Disorder)
        """
        print(f"Connecting to Neo4j at {uri}...")
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("Error: neo4j package not found. Please pip install neo4j.")
            return

        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        def init_schema(tx):
            # Schema Modifications (MUST be in separate transaction)
            # Remove Post constraint if it exists (optional cleanup, or just ignore)
            tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE")
            tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disorder) REQUIRE d.name IS UNIQUE")

        def upload_data(tx):
            # 1. Create Predefined Disorder Nodes
            print("Creating Disorder nodes...")
            for d_name in self.disorders:
                tx.run("MERGE (d:Disorder {name: $name})", name=d_name)

            # 2. Create Unique Symptom Nodes
            if self.unique_symptoms:
                print(f"Uploading {len(self.unique_symptoms)} unique concept nodes...")
                batch_data = [{"name": s} for s in self.unique_symptoms]
                
                query_create_symptoms = """
                UNWIND $batch AS row
                MERGE (s:Symptom {name: row.name})
                """
                tx.run(query_create_symptoms, batch=batch_data)

            # 3. Create Symptom-to-Disorder Relationships (INDICATES)
            print("Applying concept mapping rules...")
            for disorder, keywords in self.mapping_rules.items():
                # We match symptoms that contain any of the keywords
                # Note: This is a simple substring match. You might want exact match or regex depending on strictness.
                query_indicates = """
                MATCH (s:Symptom)
                WHERE any(kw in $keywords WHERE s.name CONTAINS kw)
                MATCH (d:Disorder {name: $disorder})
                MERGE (s)-[:INDICATES]->(d)
                """
                tx.run(query_indicates, keywords=keywords, disorder=disorder)

        def verify_counts(tx):
            s_count = tx.run("MATCH (s:Symptom) RETURN count(s) as count").single()['count']
            d_count = tx.run("MATCH (d:Disorder) RETURN count(d) as count").single()['count']
            r_count = tx.run("MATCH ()-[r:INDICATES]->() RETURN count(r) as count").single()['count']
            print(f"Verification: {s_count} Symptoms, {d_count} Disorders, {r_count} INDICATES relationships.")

        with driver.session() as session:
            # First transaction for schema
            session.execute_write(init_schema)
            # Second transaction for data
            session.execute_write(upload_data)
            # Verification
            session.execute_read(verify_counts)
            
        driver.close()
        print("Neo4j Knowledge Graph Construction Complete.")

    def export(self, output_dir="KG"):
        """
        Exports unique symptoms/concepts to CSV for manual analysis.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Exporting local concept list to {output_dir}...")
        df = pd.DataFrame(list(self.unique_symptoms), columns=["concept"])
        df.sort_values(by="concept", inplace=True)
        df.to_csv(f"{output_dir}/concepts.csv", index=False)
        
        with open(f"{output_dir}/kg_summary.txt", "w") as f:
            f.write(f"Unique Concepts: {len(self.unique_symptoms)}\n")
            f.write(f"Note: Concepts may be HPO IDs (HP:XXXXXXX) or symptom terms\n")

if __name__ == "__main__":
    # Test script (dummy data)
    kg = KGBuilder()
    kg.collect_symptoms([{"term": "anxiety"}, {"term": "sadness"}])
    kg.collect_symptoms([{"term": "stressed"}, {"term": "panic"}])
    kg.collect_symptoms([{"term": "anxiety"}]) # Duplicate
    kg.export("test_kg_concepts")

