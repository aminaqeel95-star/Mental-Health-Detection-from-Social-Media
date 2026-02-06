import os
import owlready2
from owlready2 import get_ontology, default_world
import json
from typing import Dict, List, Set, Tuple

ONTOLOGY_URL = "http://purl.obolibrary.org/obo/hp.owl"
CACHE_PATH = "DATA/hp_cache.owl"
JSON_CACHE_PATH = "DATA/hpo_processed_cache.json"

def load_from_cache():
    """Load processed ontology data from JSON cache."""
    if os.path.exists(JSON_CACHE_PATH):
        print(f"Loading processed ontology from JSON cache: {JSON_CACHE_PATH}")
        try:
            with open(JSON_CACHE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded {len(data['symptom_map'])} concepts from cache.")
                return data
        except Exception as e:
            print(f"Failed to load JSON cache: {e}")
    return None

def cache_ontology_data(symptom_map, hierarchy, synonym_types, metadata):
    """Save processed ontology data to JSON cache."""
    try:
        data = {
            'symptom_map': symptom_map,
            'hierarchy': hierarchy,
            'synonym_types': synonym_types,
            'metadata': metadata
        }
        with open(JSON_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Cached processed ontology data to {JSON_CACHE_PATH}")
    except Exception as e:
        print(f"Failed to cache ontology data: {e}")

def get_synonyms_with_types(entity):
    """
    Collect all synonyms with their relationship types.
    Returns: dict with 'exact', 'related', 'narrow', 'broad', 'label' keys
    """
    synonyms = {
        'label': [],
        'exact': [],
        'related': [],
        'narrow': [],
        'broad': []
    }
    
    # Collect labels
    if hasattr(entity, 'label'):
        synonyms['label'] = [l for l in entity.label if isinstance(l, str)]
    
    # Collect typed synonyms
    synonym_mapping = {
        'hasExactSynonym': 'exact',
        'hasRelatedSynonym': 'related',
        'hasNarrowSynonym': 'narrow',
        'hasBroadSynonym': 'broad'
    }
    
    for prop, syn_type in synonym_mapping.items():
        if hasattr(entity, prop):
            vals = getattr(entity, prop)
            if isinstance(vals, list):
                synonyms[syn_type].extend([v for v in vals if isinstance(v, str)])
            elif isinstance(vals, str):
                synonyms[syn_type].append(vals)
    
    return synonyms

def get_concept_hierarchy(onto):
    """
    Extract parent-child relationships from HPO.
    Returns: dict mapping {child_id: [parent_id1, parent_id2, ...]}
    """
    hierarchy = {}
    
    for cls in onto.classes():
        if not cls.name.startswith("HP_"):
            continue
        
        child_id = cls.name.replace("_", ":")
        parents = []
        
        # Get direct superclasses (is_a relationships)
        if hasattr(cls, 'is_a'):
            for parent in cls.is_a:
                if hasattr(parent, 'name') and parent.name.startswith("HP_"):
                    parents.append(parent.name.replace("_", ":"))
        
        if parents:
            hierarchy[child_id] = parents
    
    return hierarchy

def get_metadata(entity):
    """Extract metadata like definitions and comments."""
    metadata = {}
    
    # Definition
    if hasattr(entity, 'IAO_0000115'):  # definition property
        defs = entity.IAO_0000115
        if isinstance(defs, list):
            metadata['definition'] = defs[0] if defs else ""
        elif isinstance(defs, str):
            metadata['definition'] = defs
    
    # Comments
    if hasattr(entity, 'comment'):
        comments = entity.comment
        if isinstance(comments, list):
            metadata['comment'] = comments[0] if comments else ""
        elif isinstance(comments, str):
            metadata['comment'] = comments
    
    return metadata

def load_hpo_ontology(force_reload=False):
    """
    Loads the Human Phenotype Ontology (HPO) with enhanced features.
    
    Args:
        force_reload: If True, bypass JSON cache and reload from OWL
    
    Returns:
        dict: Contains 'symptom_map', 'hierarchy', 'synonym_types', 'metadata'
    """
    # Try loading from JSON cache first
    if not force_reload:
        cached_data = load_from_cache()
        if cached_data:
            return cached_data
    
    # Create data dir if not exists
    os.makedirs("DATA", exist_ok=True)
    
    # Load or download OWL file
    if not os.path.exists(CACHE_PATH):
        print(f"Downloading HPO from {ONTOLOGY_URL}...")
        try:
            import requests
            response = requests.get(ONTOLOGY_URL, stream=True)
            response.raise_for_status()
            with open(CACHE_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Ontology downloaded and cached.")
            
            import time
            time.sleep(1)
            
            onto = get_ontology(CACHE_PATH).load()
        except Exception as e:
            print(f"Failed to download ontology: {e}")
            return {
                'symptom_map': {},
                'hierarchy': {},
                'synonym_types': {},
                'metadata': {}
            }
    else:
        print(f"Loading HPO from OWL cache: {CACHE_PATH}...")
        onto = get_ontology(CACHE_PATH).load()
    
    print("Extracting concepts, hierarchies, and metadata...")
    
    symptom_map = {}
    synonym_types = {}
    metadata_map = {}
    
    # Find root node
    roots = []
    try:
        roots.append(onto.search_one(iri="*HP_0000118"))  # Phenotypic abnormality
    except:
        pass
    
    if not roots or roots[0] is None:
        print("Could not find root HP_0000118. Scanning all HP_* classes.")
        classes_to_process = [cls for cls in onto.classes() if cls.name.startswith("HP_")]
    else:
        root = roots[0]
        print(f"Found root: {root}")
        classes_to_process = [cls for cls in root.descendants() if cls.name.startswith("HP_")]
    
    # Process each class
    for cls in classes_to_process:
        hp_id = cls.name.replace("_", ":")
        
        # Get synonyms with types
        syn_data = get_synonyms_with_types(cls)
        synonym_types[hp_id] = syn_data
        
        # Flatten all synonyms for backward compatibility
        all_syns = []
        for syn_list in syn_data.values():
            all_syns.extend(syn_list)
        symptom_map[hp_id] = list(set(all_syns))
        
        # Get metadata
        metadata_map[hp_id] = get_metadata(cls)
    
    # Extract hierarchy
    hierarchy = get_concept_hierarchy(onto)
    
    print(f"Extracted {len(symptom_map)} concepts with hierarchical relationships.")
    
    # Prepare return data
    result = {
        'symptom_map': symptom_map,
        'hierarchy': hierarchy,
        'synonym_types': synonym_types,
        'metadata': metadata_map
    }
    
    # Cache for future use
    cache_ontology_data(symptom_map, hierarchy, synonym_types, metadata_map)
    
    return result

if __name__ == "__main__":
    symptoms = load_hpo_ontology()
    # Print sample
    print("Sample Symptoms:")
    for k, v in list(symptoms.items())[:5]:
        print(f"{k}: {v}")
