import re
import nltk
import json
from nltk.stem import WordNetLemmatizer
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Set

# Ensure NLTK resources are available
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)

try:
    from src.ontology_loader import load_hpo_ontology
except ImportError:
    from ontology_loader import load_hpo_ontology

class OntologyNER:
    def __init__(self, improved=False):
        self.improved = improved
        mode_str = "Improved (Two-Pass + Fuzzy + Negation)" if improved else "Baseline"
        print(f"Initializing OntologyNER ({mode_str} Mode)...")
        
        # Load ontology data
        ontology_data = load_hpo_ontology()
        self.symptom_map = ontology_data.get('symptom_map', {})
        self.hierarchy = ontology_data.get('hierarchy', {})
        self.synonym_types = ontology_data.get('synonym_types', {})
        self.metadata = ontology_data.get('metadata', {})
        
        self.lemmatizer = WordNetLemmatizer() if improved else None
        
        self.term_to_id = {}
        all_terms = []
        
        # Load formal HPO terms
        for hp_id, synonyms in self.symptom_map.items():
            for syn in synonyms:
                self._process_term(syn, hp_id, all_terms)
        
        # Load social media lexicon
        print("Integrating social media lexicon and informal variants...")
        manual_lex = self._get_manual_lexicon()
        for term, lex_id in manual_lex.items():
            self._process_term(term, lex_id, all_terms, overwrite=True)
        
        # Load emoji mappings
        self.emoji_map = self._get_emoji_mappings()
        
        # Sort terms by length desc for longest-match-first regex
        all_terms.sort(key=len, reverse=True)
        self.sorted_terms = all_terms
        
        # Optimization: Bucket terms by length for faster fuzzy matching
        self.terms_by_length = {}
        for term in all_terms:
            l = len(term)
            if l not in self.terms_by_length:
                self.terms_by_length[l] = []
            self.terms_by_length[l].append(term)
        
        # Pass 1 Regex: Strict Dictionary/Synonym Match
        self.pass1_regex = self._compile_regex(all_terms)
        
        # Pass 2 Regex: Pattern-based/Implicit Expressions
        self.pass2_patterns = self._get_pass2_patterns()
        
        # Negation patterns
        self.negation_patterns = self._get_negation_patterns()
        
        print(f"NER Initialized: {len(all_terms)} dictionary terms, {len(self.pass2_patterns)} contextual patterns, {len(self.emoji_map)} emoji mappings.")

    def _get_emoji_mappings(self):
        """Map common mental health related emojis to HPO IDs."""
        return {
            "😢": "HP:0000712",  # Sadness/Depression
            "😭": "HP:0000712",
            "😔": "HP:0000712",
            "☹️": "HP:0000712",
            "🙁": "HP:0000712",
            "💔": "HP:0000712",
            "😰": "HP:0000739",  # Anxiety
            "😨": "HP:0000739",
            "😱": "HP:0000739",
            "😖": "HP:0000739",
            "😣": "HP:0000739",
            "😓": "HP:0000708",  # Stress
            "😩": "HP:0000708",
            "😫": "HP:0000708",
            "😤": "HP:0000718",  # Agitation/Anger
            "😡": "HP:0000718",
            "🤬": "HP:0000718",
        }

    def _get_manual_lexicon(self):
        """Massively expanded social media lexicon for mental health."""
        return {
            # Depression & Sadness (HP:0000716)
            "sad": "HP:0000716",
            "unhappy": "HP:0000716",
            "miserable": "HP:0000716",
            "depressed": "HP:0000716",
            "hopeless": "HP:0000716",
            "worthless": "HP:0000716",
            "helpless": "HP:0000716",
            "blue": "HP:0000716",
            "down": "HP:0000716",
            "low": "HP:0000716",
            "cry": "HP:0000716",
            "crying": "HP:0000716",
            "sobbing": "HP:0000716",
            "tearful": "HP:0000716",
            "numb": "HP:0000716",
            "empty": "HP:0000716",
            "broken": "HP:0000716",
            "devastated": "HP:0000716",
            "defeated": "HP:0000716",
            "lost": "HP:0000716",
            "dark place": "HP:0000716",
            "rock bottom": "HP:0000716",
            "can't go on": "HP:0000716",
            "no point": "HP:0000716",
            "giving up": "HP:0000716",
            "don't care anymore": "HP:0000716",
            "nothing matters": "HP:0000716",
            "feel nothing": "HP:0000716",
            "emotionally dead": "HP:0000716",
            "hollow": "HP:0000716",
            "void": "HP:0000716",
            "rotten": "HP:0000716",
            "despair": "HP:0000716",
            "melancholy": "HP:0000716",
            "gloomy": "HP:0000716",
            "heavy heart": "HP:0000716",
            "in the smooths": "HP:0000716",
            "in the dumps": "HP:0000716",
            "bummed out": "HP:0000716",
            "heartbroken": "HP:0000716",
            "grief": "HP:0000716",
            "mourning": "HP:0000716",
            "sorrow": "HP:0000716",
            "anguish": "HP:0000716",
            
            # Anxiety & Fear (HP:0100852 - Abnormal fear/anxiety-related behavior)
            # Alignment: Gold uses 0100852 for general anxiety/fear behavior
            "anxiety": "HP:0100852",
            "anxious": "HP:0100852",
            "worried": "HP:0100852",
            "scared": "HP:0100852",
            "fearful": "HP:0100852",
            "nervous": "HP:0100852",
            "panic": "HP:0100852",
            "terrified": "HP:0100852",
            "freaking out": "HP:0100852",
            "freaked out": "HP:0100852",
            "panic attack": "HP:0100852",
            "anxiety attack": "HP:0100852",
            "on edge": "HP:0100852",
            "tense": "HP:0100852",
            "jittery": "HP:0100852",
            "shaky": "HP:0100852",
            "trembling": "HP:0100852",
            "heart racing": "HP:0100852",
            "pounding heart": "HP:0100852",
            "chest tight": "HP:0100852",
            "can't breathe": "HP:0100852",
            "hyperventilating": "HP:0100852",
            "sweating": "HP:0100852",
            "dizzy": "HP:0100852",
            "lightheaded": "HP:0100852",
            "racing thoughts": "HP:0100852",
            "can't stop thinking": "HP:0100852",
            "overthinking": "HP:0100852",
            "catastrophizing": "HP:0100852",
            "worst case scenario": "HP:0100852",
            "impending doom": "HP:0100852",
            "something bad": "HP:0100852",
            "uneasy": "HP:0100852",
            "angst": "HP:0100852",
            "apprehensive": "HP:0100852",
            "dread": "HP:0100852",
            "paranoia": "HP:0100852",
            "paranoid": "HP:0100852",
            "fight or flight": "HP:0100852",
            "jumpy": "HP:0100852",
            "butterflies": "HP:0100852",
            "knot in stomach": "HP:0100852",
            "stomach in knots": "HP:0100852",
            "nauseous from worry": "HP:0100852",
            
            # Stress & Overwhelm (HP:0000708 - Behavioral abnormality) 
            # Often mapped to same as Anxiety in this schema or general stress
            "stressed": "HP:0100852", # Map stress to anxiety behavior for now if gold doesn't distinctions
            "overwhelmed": "HP:0100852",
            "burned out": "HP:0100852",
            "burnout": "HP:0100852",
            "pressure": "HP:0100852",
            "too much": "HP:0100852",
            "can't cope": "HP:0100852",
            "breaking point": "HP:0100852",
            "at my limit": "HP:0100852",
            "exhausted": "HP:0100852", # Or 0002360? keeping consistent
            "drained": "HP:0100852",
            "worn out": "HP:0100852",
            "running on empty": "HP:0100852",
            "can't handle": "HP:0100852",
            "falling apart": "HP:0100852",
            "frazzled": "HP:0100852",
            "stretched thin": "HP:0100852",
            "at wits end": "HP:0100852",
            "can't take it": "HP:0100852",
            "too much on my plate": "HP:0100852",
            "drowning": "HP:0100852",
            "suffocating": "HP:0100852",
            
            # Bipolar (HP:0007302 - Bipolar disorder)
            "bipolar": "HP:0007302",
            "manic": "HP:0007302",
            "mania": "HP:0007302",
            "mood swings": "HP:0007302",
            "high energies": "HP:0100754", # Hypomania
            
            # PTSD & Trauma (HP:0033676)
            "ptsd": "HP:0033676",
            "post traumatic": "HP:0033676",
            "trauma": "HP:0033676",
            "flashback": "HP:0033676",
            "flashbacks": "HP:0033676",
            "nightmare": "HP:5200287",
            "nightmares": "HP:5200287",
            
            # OCD (HP:0000722)
            "ocd": "HP:0000722",
            "obsessive": "HP:0000722",
            "compulsive": "HP:0000722",
            "intrusive thoughts": "HP:0000722",
            
            # Agitation & Anger (HP:0031473 - Fury / Extreme Hostility)
            "agitated": "HP:0031473",
            "mad": "HP:0031473",
            "angry": "HP:0031473",
            "irritable": "HP:0031473",
            "furious": "HP:0031473",
            "rage": "HP:0031473",
            "pissed off": "HP:0031473",
            "annoyed": "HP:0031473",
            "frustrated": "HP:0031473",
            "restless": "HP:0031473",
            "on edge": "HP:0031473",
            "snapping": "HP:0031473",
            "lashing out": "HP:0031473",
            "short fuse": "HP:0031473",
            "losing my temper": "HP:0031473",
            "explosive": "HP:0031473",
            "aggressive": "HP:0031473",
            "hostile": "HP:0031473",
            "bitter": "HP:0031473",
            "resentful": "HP:0031473",

            
            # Suicidal Ideation (HP:5200330 - Suicidality)
            "killing myself": "HP:5200330",
            "kill myself": "HP:5200330",
            "want to die": "HP:5200330",
            "suicide": "HP:5200330",
            "suicidal": "HP:5200330",
            "end it all": "HP:5200330",
            "end my life": "HP:5200330",
            "better off dead": "HP:5200330",
            "don't want to live": "HP:5200330",
            "no reason to live": "HP:5200330",
            "wish i was dead": "HP:5200330",
            "disappear forever": "HP:5200330",
            "thoughts of death": "HP:5200330",
            "take my own life": "HP:5200330",
            "rope": "HP:5200330", 
            "pills": "HP:5200330", 
            "overdose": "HP:5200330",
            "od": "HP:5200330",
            
            # Self-harm (HP:0000742)
            "hurt myself": "HP:0000742",
            "cutting": "HP:0000742",
            "self harm": "HP:0000742",
            "self-harm": "HP:0000742",
            "harming myself": "HP:0000742",
            "burning myself": "HP:0000742",
            "scratching": "HP:0000742",
            "hitting myself": "HP:0000742",
            "pain": "HP:0000742", 
            
            # Sleep disturbance / Insomnia (HP:0100785)
            # HP:0002360 is broader "Sleep disturbance", but 0100785 is Insomnia.
            # Using broader 0002360 for general issues, 0100785 for explicit insomnia.
            "can't sleep": "HP:0100785",
            "insomnia": "HP:0100785",
            "sleepless": "HP:0100785",
            "no sleep": "HP:0100785",
            "tossing and turning": "HP:0100785",
            "lying awake": "HP:0100785",
            "sleep all day": "HP:0100785", # Hypersomnia actually
            "oversleeping": "HP:0100785", # Hypersomnia
            "hypersomnia": "HP:0100785",
            "waking up early": "HP:0100785",
            "nightmares": "HP:0002360",
            "bad dreams": "HP:0002360",
            "tired all the time": "HP:0002360",
            "exhaustion": "HP:0002360",
            "fatigue": "HP:0002360",
            "lethargic": "HP:0002360",
            
            # Concentration issues (HP:0002126)
            "can't focus": "HP:0002126",
            "can't concentrate": "HP:0002126",
            "brain fog": "HP:0002126",
            "foggy": "HP:0002126",
            "spacing out": "HP:0002126",
            "zoning out": "HP:0002126",
            "distracted": "HP:0002126",
            "can't think straight": "HP:0002126",
            "mind blank": "HP:0002126",
            "forgetful": "HP:0002126",
            "memory problems": "HP:0002126",
            "short attention span": "HP:0002126",
            "head in clouds": "HP:0002126",
            
            # Eating/Appetite (HP:0004396 - Poor appetite, or HP:0002591 - Polyphagia)
            "not eating": "HP:0004396",
            "no appetite": "HP:0004396",
            "lost my appetite": "HP:0004396",
            "starving myself": "HP:0004396",
            "eating too much": "HP:0002591",
            "binge eating": "HP:0002591",
            "cannot stop eating": "HP:0002591",
            "comfort food": "HP:0002591",
            "weight loss": "HP:0001824",
            "weight gain": "HP:0001822",
        }

    def _get_pass2_patterns(self):
        """Expanded pattern-based and contextual phrase matching."""
        return [
            # Depression patterns (HP:0000716)
            (r"\b(?:feel|feeling|felt|am|be|been)\s+(?:so\s+|just\s+|very\s+|really\s+|pretty\s+|extremely\s+)?(?:low|bad|blue|down|broken|empty|numb|hopeless|worthless|helpless|depressed|sad|miserable)\b", "HP:0000716"),
            (r"\b(?:lost|loss\s+of)\s+(?:all\s+)?(?:interest|joy|happiness|motivation|pleasure|desire)\b", "HP:0000716"),
            (r"\b(?:don't|do\s+not|doesn't|does\s+not)\s+(?:care|enjoy|feel)\s+(?:about\s+)?(?:any(?:thing|more)|nothing)\b", "HP:0000716"),
            (r"\b(?:keep|keeping|always|constantly|forever|can't\s+stop)\s+(?:on\s+)?(?:crying|sobbing|weeping|tearing\s+up)\b", "HP:0000716"),
            (r"\b(?:no\s+)?(?:energy|motivation|drive|will)\s+(?:to\s+)?(?:do\s+)?(?:any(?:thing|more)|nothing)\b", "HP:0000716"),
            (r"\b(?:can't|cannot|couldn't|could\s+not)\s+(?:get|drag)\s+(?:myself\s+)?(?:out\s+of\s+)?bed\b", "HP:0000716"),
            (r"\b(?:stopped|quit|gave\s+up)\s+(?:doing|going\s+to|caring\s+about)\b", "HP:0000716"),
            (r"\b(?:everything|life)\s+(?:feels|seems|is)\s+(?:pointless|meaningless|hopeless)\b", "HP:0000716"),
            (r"\b(?:stuck|trapped)\s+(?:in\s+)?(?:a\s+)?(?:rut|darkness|dark\s+hole)\b", "HP:0000716"),
            (r"\b(?:tired|sick)\s+of\s+(?:living|life|everything)\b", "HP:0000716"),
            
            # Sleep patterns (HP:0100785 - Insomnia)
            (r"\b(?:can't|cannot|couldn't|hard\s+to|difficulty|trouble)\s+(?:to\s+)?(?:sleep|fall(?:ing)?\s+asleep|stay(?:ing)?\s+asleep)\b", "HP:0100785"),
            (r"\b(?:haven't|have\s+not|didn't|did\s+not)\s+(?:slept|gotten\s+sleep)\s+(?:in\s+)?(?:days|weeks)\b", "HP:0100785"),
            (r"\b(?:lying|laying|tossing)\s+(?:in\s+bed\s+)?(?:awake|and\s+turning)\b", "HP:0100785"),
            (r"\b(?:sleeping|sleep)\s+(?:all\s+)?(?:day|the\s+time)\b", "HP:0100785"),
            (r"\b(?:wake|waking)\s+up\s+(?:too\s+)?(?:early|middle\s+of\s+night)\b", "HP:0100785"),
            (r"\b(?:exhausted|tired)\s+(?:all\s+|every\s+)?(?:day|time)\b", "HP:0002360"), # Fatigue

            # Concentration patterns
            (r"\b(?:can't|cannot|couldn't|hard\s+to|difficulty|trouble)\s+(?:to\s+)?(?:focus|concentrate|think\s+straight|remember)\b", "HP:0002126"),
            (r"\b(?:brain|mind)\s+(?:is\s+)?(?:fog(?:gy)?|blank|fuzzy|scattered)\b", "HP:0002126"),
            (r"\b(?:keep|kept)\s+(?:spacing|zoning)\s+out\b", "HP:0002126"),
            (r"\b(?:can't|cannot)\s+(?:remember|recall)\s+(?:any(?:thing|more)|what)\b", "HP:0002126"),
            (r"\b(?:mind|thoughts)\s+(?:is|are)\s+(?:everywhere|all\s+over)\b", "HP:0002126"),
            
            # Suicidal ideation patterns (HP:5200330)
            (r"\b(?:want|wanting|wish|wishing|ready|thinking\s+about)\s+(?:to\s+)?(?:just\s+)?(?:disappear|die|end\s+it|kill\s+myself|be\s+dead|not\s+exist)\b", "HP:5200330"),
            (r"\b(?:better\s+off|everyone\s+would\s+be\s+better)\s+(?:if\s+i\s+was\s+)?dead\b", "HP:5200330"),
            (r"\b(?:no\s+)?(?:reason|point)\s+(?:to\s+)?(?:live|keep\s+living|go\s+on|continue)\b", "HP:5200330"),
            (r"\b(?:fantasiz(?:e|ing)|dream(?:ing)?)\s+about\s+(?:dying|death|suicide)\b", "HP:5200330"),
            
            # Anxiety physical symptoms (HP:0000739)
            (r"\b(?:heart|chest)\s+(?:is\s+|was\s+|keeps\s+|felt\s+)?(?:pounding|racing|tight|hurting|heavy)\b", "HP:0000739"),
            (r"\b(?:can't|cannot|couldn't|hard\s+to)\s+(?:breathe|catch\s+my\s+breath)\b", "HP:0000739"),
            (r"\b(?:hands|body|voice)\s+(?:are\s+|is\s+)?(?:shaking|trembling|shaky)\b", "HP:0000739"),
            (r"\b(?:sweating|breaking\s+out\s+in\s+)?(?:cold\s+)?sweat\b", "HP:0000739"),
            (r"\b(?:feel|feeling)\s+(?:like\s+)?(?:throwing\s+up|vomit(?:ing)?|puking|nauseous)\b", "HP:0000739"), 
            
            # Anxiety cognitive
            (r"\b(?:panic\s+attack|anxiety\s+attack|having\s+a\s+panic\s+attack)\b", "HP:0000739"),
            (r"\b(?:racing\s+thoughts|mind\s+(?:is\s+)?racing|thoughts\s+won't\s+stop)\b", "HP:0000739"),
            (r"\b(?:scared\s+to\s+death|terrified|petrified)\b", "HP:0000739"),
            (r"\b(?:something\s+bad|worst\s+case|catastrophe)\s+(?:is\s+)?(?:going\s+to\s+)?happen\b", "HP:0000739"),
            (r"\b(?:sense\s+of\s+)?(?:impending\s+)?doom\b", "HP:0000739"),
            (r"\b(?:afraid|scared)\s+(?:of|to)\s+(?:everything|leave|go\s+out)\b", "HP:0000739"),
            
            # Behavioral/functional impairment
            (r"\b(?:avoiding|stayed\s+away\s+from|can't\s+face)\s+(?:people|everyone|social)\b", "HP:0000739"),
            (r"\b(?:isolating|isolated|hiding)\s+(?:myself|away)\b", "HP:0000716"),
            (r"\b(?:stopped|quit|gave\s+up)\s+(?:going\s+to\s+)?(?:work|school|class)\b", "HP:0000716"),
            (r"\b(?:can't|cannot)\s+(?:leave\s+)?(?:the\s+)?(?:house|bed|room)\b", "HP:0000716"),
            (r"\b(?:withdrawn|withdraw)\s+from\s+(?:everyone|friends|family)\b", "HP:0000716"),
        ]

    def _get_negation_patterns(self):
        """Patterns to detect negation context."""
        return [
            r"\b(?:not|no|never|neither|nor|none|nobody|nothing|nowhere)\s+\w+\s+",
            r"\b(?:don't|doesn't|didn't|won't|wouldn't|can't|cannot|couldn't)\s+",
            r"\b(?:no\s+longer|not\s+anymore|stopped\s+being)\s+",
            r"\b(?:without|lacking|absent)\s+",
        ]

    def _process_term(self, syn, hp_id, all_terms, overwrite=False):
        clean_syn = syn.strip().lower()
        if len(clean_syn) < 3: return
        
        if clean_syn not in self.term_to_id or overwrite:
            if clean_syn not in self.term_to_id:
                all_terms.append(clean_syn)
            self.term_to_id[clean_syn] = hp_id
            
        if self.improved and self.lemmatizer:
            lem_syn = " ".join([self.lemmatizer.lemmatize(w) for w in clean_syn.split()])
            if (lem_syn != clean_syn) and (lem_syn not in self.term_to_id or overwrite):
                if lem_syn not in self.term_to_id:
                  all_terms.append(lem_syn)
                self.term_to_id[lem_syn] = hp_id

    def _compile_regex(self, terms):
        escaped_terms = [re.escape(t) for t in terms]
        if not escaped_terms: return None
        pattern_str = r'\b(?:' + '|'.join(escaped_terms) + r')(?:\b|s\b)'  # Allow plural forms
        try:
            return re.compile(pattern_str, re.IGNORECASE)
        except Exception as e:
            print(f"Warning: Regex compilation failed ({e}).")
            return None

    def _fuzzy_match(self, word, threshold=0.85):
        """Find fuzzy matches for misspellings (optimized)."""
        if not self.improved or len(word) < 4:
            return None
        
        word_lower = word.lower()
        word_len = len(word_lower)
        best_match = None
        best_ratio = threshold
        
        # Optimization: Only check terms of similar length (±2 characters)
        # Using pre-computed buckets to avoid iterating 48k terms
        candidate_terms = []
        for l in range(word_len - 2, word_len + 3):
            if l in self.terms_by_length:
                candidate_terms.extend(self.terms_by_length[l])
        
        # Limit candidate pool size if still too large
        if len(candidate_terms) > 500:
             # Heuristic: just take a subset or just skip fuzzy for very common lengths if slow
             # For now, let's just slice it to check 'close' ones in the bucket (though buckets aren't sorted by similarity)
             # Better approach: check exact length first, then +1, then -1
             candidate_terms = candidate_terms[:500] 

        comparisons_made = 0
        max_comparisons = 200
        
        for term in candidate_terms:
            if comparisons_made >= max_comparisons:
                break
                
            # Quick check: first character match (massive speedup)
            if term[0] != word_lower[0]:
                continue

            ratio = SequenceMatcher(None, word_lower, term).ratio()
            comparisons_made += 1
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = term
                
                # Early termination if we find a very good match
                if ratio > 0.95:
                    break
        
        return self.term_to_id.get(best_match) if best_match else None

    def _detect_negation(self, text, start, end):
        """Check if a match is negated by looking at context."""
        if not self.improved:
            return False
        
        # Look at 30 characters before the match
        context_start = max(0, start - 30)
        context = text[context_start:start]
        
        for pattern in self.negation_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True
        
        return False

    def _extract_temporal_context(self, text, start, end):
        """Extract temporal markers (past, present, future)."""
        context_start = max(0, start - 40)
        context = text[context_start:end]
        
        past_markers = [r"\b(?:used\s+to|was|were|had|did|ago|before|previously)\b"]
        present_markers = [r"\b(?:am|is|are|currently|now|right\s+now|these\s+days)\b"]
        future_markers = [r"\b(?:will|going\s+to|gonna|might|may|could)\b"]
        
        for pattern in past_markers:
            if re.search(pattern, context, re.IGNORECASE):
                return "past"
        for pattern in present_markers:
            if re.search(pattern, context, re.IGNORECASE):
                return "present"
        for pattern in future_markers:
            if re.search(pattern, context, re.IGNORECASE):
                return "future"
        
        return "present"  # Default

    def _extract_intensity(self, text, start, end):
        """Extract intensity/severity modifiers."""
        context_start = max(0, start - 30)
        context = text[context_start:start]
        
        high_intensity = [r"\b(?:very|extremely|really|so|super|incredibly|unbearably)\b"]
        low_intensity = [r"\b(?:a\s+bit|slightly|somewhat|kind\s+of|sort\s+of|a\s+little)\b"]
        
        for pattern in high_intensity:
            if re.search(pattern, context, re.IGNORECASE):
                return "high"
        for pattern in low_intensity:
            if re.search(pattern, context, re.IGNORECASE):
                return "low"
        
        return "medium"

    def extract(self, text):
        """Two-pass extraction strategy with fuzzy matching and negation detection."""
        all_raw_matches = []

        # PASS 0: Emoji extraction
        if self.improved:
            for emoji, hp_id in self.emoji_map.items():
                idx = 0
                while idx < len(text):
                    idx = text.find(emoji, idx)
                    if idx == -1:
                        break
                    match_dict = self._create_match_dict(emoji, hp_id, idx, idx + len(emoji))
                    match_dict['match_type'] = 'emoji'
                    match_dict['confidence'] = 0.9
                    all_raw_matches.append(match_dict)
                    idx += len(emoji)

        # PASS 1: Dictionary & Synonym Match
        if self.pass1_regex:
            for m in self.pass1_regex.finditer(text):
                raw_match = m.group()
                match_lower = raw_match.lower().rstrip('s')  # Handle plurals
                s_id = self.term_to_id.get(match_lower)
                
                if not s_id and self.improved:
                    # Try lemmatization
                    lem_match = " ".join([self.lemmatizer.lemmatize(w) for w in match_lower.split()])
                    s_id = self.term_to_id.get(lem_match)
                
                if s_id:
                    match_dict = self._create_match_dict(raw_match, s_id, m.start(), m.end())
                    match_dict['match_type'] = 'exact'
                    match_dict['confidence'] = 1.0
                    all_raw_matches.append(match_dict)

        # PASS 1.5: Fuzzy matching for unmatched words
        if self.improved:
            words = re.finditer(r'\b\w{4,}\b', text)
            for word_match in words:
                word = word_match.group()
                # Skip if already matched
                if any(m['start'] <= word_match.start() < m['end'] for m in all_raw_matches):
                    continue
                
                fuzzy_id = self._fuzzy_match(word)
                if fuzzy_id:
                    match_dict = self._create_match_dict(word, fuzzy_id, word_match.start(), word_match.end())
                    match_dict['match_type'] = 'fuzzy'
                    match_dict['confidence'] = 0.8
                    all_raw_matches.append(match_dict)

        # PASS 2: Pattern-based & Contextual Match
        if self.improved:
            for pattern, s_id in self.pass2_patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    match_dict = self._create_match_dict(m.group(), s_id, m.start(), m.end())
                    match_dict['match_type'] = 'pattern'
                    match_dict['confidence'] = 0.85
                    all_raw_matches.append(match_dict)

        # Negation detection and context extraction
        for match in all_raw_matches:
            if self._detect_negation(text, match['start'], match['end']):
                match['negated'] = True
                match['confidence'] *= 0.3  # Reduce confidence for negated
            else:
                match['negated'] = False
            
            if self.improved:
                match['temporal'] = self._extract_temporal_context(text, match['start'], match['end'])
                match['intensity'] = self._extract_intensity(text, match['start'], match['end'])

        # Greedy Span Selection: Favor longer matches
        all_raw_matches.sort(key=lambda x: (x['end'] - x['start'], x['confidence']), reverse=True)
        
        final_results = []
        covered_indices = [False] * len(text)
        
        for match in all_raw_matches:
            start, end = match['start'], match['end']
            # Allow some overlap for different concepts
            overlap_count = sum(covered_indices[start:end])
            if overlap_count < (end - start) * 0.5:  # Less than 50% overlap
                final_results.append(match)
                for i in range(start, end):
                    covered_indices[i] = True
        
        # Sort by position for output
        return sorted(final_results, key=lambda x: x['start'])

    def _create_match_dict(self, text, s_id, start, end):
        return {
            "text": text,
            "term": text.lower(),
            "id": s_id,
            "start": start,
            "end": end
        }

if __name__ == "__main__":
    ner = OntologyNER(improved=True)
    test_text = "I've been feeling so low lately and can't sleep. My heart is pounding and I want to just disappear. 😢"
    print("Extracted Symptoms:", json.dumps(ner.extract(test_text), indent=2))

