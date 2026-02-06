// Create Constraint
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Symptom) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Disorder) REQUIRE n.id IS UNIQUE;

MERGE (n:Disorder {id: 'DISORDER_Stress', name: 'Stress', count: 0});
MERGE (n:Disorder {id: 'DISORDER_Anxiety', name: 'Anxiety', count: 0});
MERGE (n:Disorder {id: 'DISORDER_Depression', name: 'Depression', count: 0});
MERGE (n:Symptom {id: 'HP:0033845', name: 'sense of doom', count: 1});
MERGE (n:Symptom {id: 'MANUAL_LEX:ANGER', name: 'mad', count: 35});
MERGE (n:Symptom {id: 'MANUAL_LEX:UNHAPPY', name: 'unhappy', count: 13});
MERGE (n:Symptom {id: 'HP:0033676', name: 'ptsd', count: 182});
MERGE (n:Symptom {id: 'HP:0000739', name: 'anxiety', count: 404});
MERGE (n:Symptom {id: 'HP:0025269', name: 'panic attack', count: 41});
MERGE (n:Symptom {id: 'HP:0031467', name: 'feeling bad', count: 2});
MERGE (n:Symptom {id: 'HP:0002013', name: 'vomiting', count: 7});
MERGE (n:Symptom {id: 'HP:0012735', name: 'coughing', count: 8});
MERGE (n:Symptom {id: 'HP:0031473', name: 'anger', count: 75});
MERGE (n:Symptom {id: 'HP:0002315', name: 'headaches', count: 17});
MERGE (n:Symptom {id: 'MANUAL_LEX:SADNESS', name: 'sad', count: 38});
MERGE (n:Symptom {id: 'MANUAL_LEX:AGITATION', name: 'screaming', count: 40});
MERGE (n:Symptom {id: 'HP:0000722', name: 'ocd', count: 20});
MERGE (n:Symptom {id: 'HP:0002829', name: 'joint pain', count: 1});
MERGE (n:Symptom {id: 'HP:0002527', name: 'falls', count: 42});
MERGE (n:Symptom {id: 'HP:0000716', name: 'depression', count: 112});
MERGE (n:Symptom {id: 'HP:0100754', name: 'manic', count: 5});
MERGE (n:Symptom {id: 'HP:0012531', name: 'pain', count: 41});
MERGE (n:Symptom {id: 'HP:0025095', name: 'sneeze', count: 2});
MERGE (n:Symptom {id: 'HP:0009926', name: 'watery eyes', count: 5});
MERGE (n:Symptom {id: 'HP:0012393', name: 'allergy', count: 3});
MERGE (n:Symptom {id: 'HP:0000737', name: 'on edge', count: 13});
MERGE (n:Symptom {id: 'HP:0007018', name: 'adhd', count: 7});
MERGE (n:Symptom {id: 'HP:0001649', name: 'increased heart rate', count: 2});
MERGE (n:Symptom {id: 'HP:0031273', name: 'shock', count: 9});
MERGE (n:Symptom {id: 'MANUAL_LEX:CRYING', name: 'crying', count: 106});
MERGE (n:Symptom {id: 'HP:0012378', name: 'tired', count: 85});
MERGE (n:Symptom {id: 'HP:0032940', name: 'dissociation', count: 7});
MERGE (n:Symptom {id: 'HP:6000029', name: 'social anxiety', count: 12});
MERGE (n:Symptom {id: 'HP:0030955', name: 'alcoholism', count: 7});
MERGE (n:Symptom {id: 'HP:0001658', name: 'heart attack', count: 7});
MERGE (n:Symptom {id: 'HP:5200271', name: 'hopeless', count: 14});
MERGE (n:Symptom {id: 'MANUAL_LEX:STRESS', name: 'overwhelmed', count: 14});
MERGE (n:Symptom {id: 'HP:5200217', name: 'depersonalization', count: 3});
MERGE (n:Symptom {id: 'HP:0041248', name: 'broken wrist', count: 1});
MERGE (n:Symptom {id: 'HP:0100785', name: 'insomnia', count: 9});
MERGE (n:Symptom {id: 'HP:0002329', name: 'sleepy', count: 3});
MERGE (n:Symptom {id: 'HP:0001259', name: 'coma', count: 3});
MERGE (n:Symptom {id: 'HP:5200205', name: 'illusion', count: 1});
MERGE (n:Symptom {id: 'HP:0010865', name: 'odd', count: 10});
MERGE (n:Symptom {id: 'HP:0003510', name: 'dwarfism', count: 1});
MERGE (n:Symptom {id: 'HP:0007302', name: 'bipolar disorder', count: 6});
MERGE (n:Symptom {id: 'HP:0031589', name: 'suicidal ideation', count: 3});
MERGE (n:Symptom {id: 'HP:0011999', name: 'paranoia', count: 9});
MERGE (n:Symptom {id: 'MANUAL_LEX:SUICIDAL_IDEATION', name: 'killing myself', count: 18});
MERGE (n:Symptom {id: 'HP:0004324', name: 'weight gain', count: 2});
MERGE (n:Symptom {id: 'MANUAL_LEX:NEGATIVE_THOUGHTS', name: 'negative', count: 32});
MERGE (n:Symptom {id: 'HP:0002664', name: 'cancer', count: 15});
MERGE (n:Symptom {id: 'HP:0100526', name: 'lung cancer', count: 2});
MERGE (n:Symptom {id: 'HP:0004396', name: 'no appetite', count: 1});
MERGE (n:Symptom {id: 'HP:0031844', name: 'euphoria', count: 1});
MERGE (n:Symptom {id: 'HP:0012452', name: 'restless leg', count: 1});
MERGE (n:Symptom {id: 'HP:0001369', name: 'arthritis', count: 1});
MERGE (n:Symptom {id: 'HP:0012432', name: 'chronic fatigue', count: 2});
MERGE (n:Symptom {id: 'HP:0025273', name: 'achilles tendonitis', count: 1});
MERGE (n:Symptom {id: 'HP:0002758', name: 'osteoarthritis', count: 1});
MERGE (n:Symptom {id: 'HP:0000975', name: 'sweating', count: 5});
MERGE (n:Symptom {id: 'HP:0025143', name: 'chills', count: 6});
MERGE (n:Symptom {id: 'HP:0001945', name: 'fever', count: 3});
MERGE (n:Symptom {id: 'HP:0002321', name: 'dizziness', count: 4});
MERGE (n:Symptom {id: 'HP:0031246', name: 'dry cough', count: 1});
MERGE (n:Symptom {id: 'HP:0000756', name: 'agoraphobia', count: 6});
MERGE (n:Symptom {id: 'HP:5200273', name: 'emotional pain', count: 2});
MERGE (n:Symptom {id: 'HP:6000011', name: 'guilt', count: 13});
MERGE (n:Symptom {id: 'HP:5200339', name: 'cutting', count: 6});
MERGE (n:Symptom {id: 'HP:5200134', name: 'bouncing', count: 7});
MERGE (n:Symptom {id: 'HP:0025502', name: 'overweight', count: 2});
MERGE (n:Symptom {id: 'HP:0002099', name: 'asthma', count: 3});
MERGE (n:Symptom {id: 'HP:0100723', name: 'gist', count: 1});
MERGE (n:Symptom {id: 'HP:0100716', name: 'self-harm', count: 2});
MERGE (n:Symptom {id: 'MANUAL_LEX:NUMBNESS', name: 'numb', count: 11});
MERGE (n:Symptom {id: 'HP:0033630', name: 'brain fog', count: 1});
MERGE (n:Symptom {id: 'HP:5200231', name: 'hypervigilance', count: 3});
MERGE (n:Symptom {id: 'HP:0002018', name: 'nausea', count: 6});
MERGE (n:Symptom {id: 'HP:0000656', name: 'ectropion', count: 1});
MERGE (n:Symptom {id: 'HP:0030212', name: 'collecting', count: 2});
MERGE (n:Symptom {id: 'HP:0001824', name: 'weight loss', count: 1});
MERGE (n:Symptom {id: 'HP:0100753', name: 'schizophrenia', count: 5});
MERGE (n:Symptom {id: 'HP:0000741', name: 'apathy', count: 1});
MERGE (n:Symptom {id: 'HP:5200049', name: 'arranging', count: 2});
MERGE (n:Symptom {id: 'HP:0002608', name: 'celiac disease', count: 1});
MERGE (n:Symptom {id: 'HP:0000738', name: 'hallucinations', count: 4});
MERGE (n:Symptom {id: 'HP:0008763', name: 'no social interaction', count: 1});
MERGE (n:Symptom {id: 'HP:0012076', name: 'bpd', count: 9});
MERGE (n:Symptom {id: 'HP:0033748', name: 'numbness', count: 2});
MERGE (n:Symptom {id: 'HP:0000622', name: 'blurred vision', count: 1});
MERGE (n:Symptom {id: 'HP:0041092', name: 'overly sensitive', count: 3});
MERGE (n:Symptom {id: 'HP:0100710', name: 'impulsive', count: 3});
MERGE (n:Symptom {id: 'HP:0010536', name: 'central sleep apnea', count: 1});
MERGE (n:Symptom {id: 'HP:5200232', name: 'phobia', count: 5});
MERGE (n:Symptom {id: 'HP:0002014', name: 'diarrhea', count: 1});
MERGE (n:Symptom {id: 'HP:0100749', name: 'chest pain', count: 2});
MERGE (n:Symptom {id: 'HP:0033844', name: 'racing thoughts', count: 1});
MERGE (n:Symptom {id: 'HP:0001962', name: 'palpitations', count: 3});
MERGE (n:Symptom {id: 'HP:0012532', name: 'chronic pain', count: 6});
MERGE (n:Symptom {id: 'HP:0010546', name: 'twitching', count: 1});
MERGE (n:Symptom {id: 'HP:0001250', name: 'seizures', count: 13});
MERGE (n:Symptom {id: 'HP:0002181', name: 'brain swelling', count: 1});
MERGE (n:Symptom {id: 'HP:0410281', name: 'indigestion', count: 1});
MERGE (n:Symptom {id: 'HP:0500001', name: 'body odor', count: 1});
MERGE (n:Symptom {id: 'HP:0001631', name: 'asd', count: 3});
MERGE (n:Symptom {id: 'HP:0000704', name: 'periodontitis', count: 1});
MERGE (n:Symptom {id: 'HP:0100699', name: 'scarring', count: 3});
MERGE (n:Symptom {id: 'HP:0000717', name: 'autism', count: 4});
MERGE (n:Symptom {id: 'HP:0007185', name: 'fainting', count: 3});
MERGE (n:Symptom {id: 'HP:0033850', name: 'coldness', count: 1});
MERGE (n:Symptom {id: 'HP:0025267', name: 'snore', count: 2});
MERGE (n:Symptom {id: 'HP:0000726', name: 'dementia', count: 3});
MERGE (n:Symptom {id: 'HP:0031987', name: 'concentration problems', count: 2});
MERGE (n:Symptom {id: 'HP:0030166', name: 'night sweats', count: 1});
MERGE (n:Symptom {id: 'HP:0001217', name: 'clubbing', count: 1});
MERGE (n:Symptom {id: 'HP:0033834', name: 'malaise', count: 1});
MERGE (n:Symptom {id: 'HP:0000010', name: 'urinary tract infection', count: 1});
MERGE (n:Symptom {id: 'HP:0001394', name: 'liver cirrhosis', count: 1});
MERGE (n:Symptom {id: 'HP:0001061', name: 'acne', count: 1});
MERGE (n:Symptom {id: 'HP:0030153', name: 'bile duct cancer', count: 1});
MERGE (n:Symptom {id: 'HP:0100242', name: 'sarcoma', count: 2});
MERGE (n:Symptom {id: 'HP:0009830', name: 'neuropathy', count: 1});
MERGE (n:Symptom {id: 'HP:0033513', name: 'cocaine addiction', count: 2});
MERGE (n:Symptom {id: 'HP:0031354', name: 'trouble falling asleep', count: 1});
MERGE (n:Symptom {id: 'HP:0031469', name: 'low self-esteem', count: 1});
MERGE (n:Symptom {id: 'HP:0012075', name: 'personality disorder', count: 2});
MERGE (n:Symptom {id: 'HP:0002104', name: 'apnea', count: 1});
MERGE (n:Symptom {id: 'HP:0001289', name: 'confusion', count: 4});
MERGE (n:Symptom {id: 'HP:0002039', name: 'anorexia', count: 1});
MERGE (n:Symptom {id: 'HP:0000012', name: 'overactive bladder', count: 1});
MERGE (n:Symptom {id: 'HP:0100739', name: 'bulimia', count: 1});
MERGE (n:Symptom {id: 'HP:0002098', name: 'respiratory distress', count: 1});
MERGE (n:Symptom {id: 'HP:0003401', name: 'tingling', count: 1});
MERGE (n:Symptom {id: 'HP:0025144', name: 'shivering', count: 2});
MERGE (n:Symptom {id: 'HP:0100658', name: 'cellulitis', count: 1});
MERGE (n:Symptom {id: 'HP:0033705', name: 'tearfulness', count: 1});
MERGE (n:Symptom {id: 'HP:0000853', name: 'thyroid goiter', count: 1});
MERGE (n:Symptom {id: 'HP:0030692', name: 'brain tumor', count: 3});
MERGE (n:Symptom {id: 'HP:0020083', name: 'boil', count: 1});
MERGE (n:Symptom {id: 'HP:0025771', name: 'rumination', count: 1});
MERGE (n:Symptom {id: 'HP:6000789', name: 'corn', count: 1});
MERGE (n:Symptom {id: 'HP:0012125', name: 'prostate cancer', count: 1});
MERGE (n:Symptom {id: 'HP:0000745', name: 'lack of motivation', count: 1});
MERGE (n:Symptom {id: 'HP:0031955', name: 'limp', count: 1});
MERGE (n:Symptom {id: 'HP:0033517', name: 'heroin addiction', count: 1});
MERGE (n:Symptom {id: 'HP:0003418', name: 'back pain', count: 2});
MERGE (n:Symptom {id: 'HP:0100614', name: 'muscle inflammation', count: 1});
MERGE (n:Symptom {id: 'HP:0002094', name: 'trouble breathing', count: 1});
MERGE (n:Symptom {id: 'HP:0033726', name: 'lupus nephritis', count: 1});
MERGE (n:Symptom {id: 'HP:0002883', name: 'hyperventilation', count: 2});
MERGE (n:Symptom {id: 'HP:0040213', name: 'shallow breathing', count: 2});
MERGE (n:Symptom {id: 'HP:0005263', name: 'gastritis', count: 2});
MERGE (n:Symptom {id: 'HP:0000787', name: 'kidney stones', count: 1});
MERGE (n:Symptom {id: 'HP:0000822', name: 'high blood pressure', count: 1});
MERGE (n:Symptom {id: 'HP:0030448', name: 'soft tissue sarcoma', count: 1});
MERGE (n:Symptom {id: 'HP:0001533', name: 'thin build', count: 1});
MERGE (n:Symptom {id: 'HP:5200233', name: 'anticipatory anxiety', count: 3});
MERGE (n:Symptom {id: 'HP:5200218', name: 'derealization', count: 3});
MERGE (n:Symptom {id: 'HP:0001297', name: 'stroke', count: 2});
MERGE (n:Symptom {id: 'HP:0031217', name: 'hot flash', count: 1});
MERGE (n:Symptom {id: 'HP:0012005', name: 'deja vu', count: 2});
MERGE (n:Symptom {id: 'HP:0001742', name: 'stuffy nose', count: 1});
MERGE (n:Symptom {id: 'HP:0001263', name: 'cognitive delay', count: 1});
MERGE (n:Symptom {id: 'HP:0000360', name: 'tinnitus', count: 1});
MERGE (n:Symptom {id: 'HP:0000718', name: 'aggression', count: 3});
MERGE (n:Symptom {id: 'HP:0033838', name: 'dysphoria', count: 1});
MERGE (n:Symptom {id: 'HP:0025113', name: 'misophonia', count: 1});
MERGE (n:Symptom {id: 'HP:0000713', name: 'agitation', count: 1});
MERGE (n:Symptom {id: 'HP:0033454', name: 'tube feeding', count: 1});
MERGE (n:Symptom {id: 'HP:0002571', name: 'achalasia', count: 1});
MERGE (n:Symptom {id: 'HP:0001699', name: 'sudden death', count: 1});
MERGE (n:Symptom {id: 'HP:0002027', name: 'upset stomach', count: 1});
MERGE (n:Symptom {id: 'HP:0000746', name: 'delusions', count: 1});
MERGE (n:Symptom {id: 'HP:0001287', name: 'meningitis', count: 1});
MERGE (n:Symptom {id: 'HP:0000729', name: 'autism spectrum disorder', count: 1});
MERGE (n:Symptom {id: 'HP:0001249', name: 'intellectual disability', count: 1});
MERGE (n:Symptom {id: 'HP:0004279', name: 'short hand', count: 1});
MERGE (n:Symptom {id: 'HP:0030834', name: 'shoulder pain', count: 1});
MERGE (n:Symptom {id: 'HP:0025406', name: 'weakness', count: 2});
MERGE (n:Symptom {id: 'HP:0003470', name: 'paralysis', count: 1});
MERGE (n:Symptom {id: 'HP:0032551', name: 'pile', count: 1});
MERGE (n:Symptom {id: 'HP:0012189', name: 'hodgkin's lymphoma', count: 1});
MERGE (n:Symptom {id: 'HP:0000711', name: 'restlessness', count: 1});

MATCH (s:Symptom {id: 'MANUAL_LEX:UNHAPPY'})
MATCH (d:Disorder {id: 'DISORDER_Depression'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0000739'})
MATCH (d:Disorder {id: 'DISORDER_Anxiety'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0025269'})
MATCH (d:Disorder {id: 'DISORDER_Anxiety'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'MANUAL_LEX:SADNESS'})
MATCH (d:Disorder {id: 'DISORDER_Depression'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0000716'})
MATCH (d:Disorder {id: 'DISORDER_Depression'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'MANUAL_LEX:CRYING'})
MATCH (d:Disorder {id: 'DISORDER_Depression'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:6000029'})
MATCH (d:Disorder {id: 'DISORDER_Anxiety'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:5200271'})
MATCH (d:Disorder {id: 'DISORDER_Depression'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'MANUAL_LEX:STRESS'})
MATCH (d:Disorder {id: 'DISORDER_Stress'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0031589'})
MATCH (d:Disorder {id: 'DISORDER_Depression'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0000756'})
MATCH (d:Disorder {id: 'DISORDER_Anxiety'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:5200232'})
MATCH (d:Disorder {id: 'DISORDER_Anxiety'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0002098'})
MATCH (d:Disorder {id: 'DISORDER_Stress'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0033705'})
MATCH (d:Disorder {id: 'DISORDER_Depression'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:0000822'})
MATCH (d:Disorder {id: 'DISORDER_Stress'})
MERGE (s)-[:INDICATES]->(d);
MATCH (s:Symptom {id: 'HP:5200233'})
MATCH (d:Disorder {id: 'DISORDER_Anxiety'})
MERGE (s)-[:INDICATES]->(d);
