import uuid
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker with a stable seed for deterministic interview demos
fake = Faker()
Faker.seed(42)
random.seed(42)

TOTAL_ROWS = 10500
OUTPUT_FILE = "db/init/seed.sql"

# Common realistic ICD-10 medical diagnostics codes for statistical groupings
ICD10_POOL = [
    ("I10", "Essential (primary) hypertension"),
    ("E11.9", "Type 2 diabetes mellitus without complications"),
    ("E78.5", "Hyperlipidemia, unspecified"),
    ("J45.909", "Unspecified asthma, uncomplicated"),
    ("M25.561", "Pain in right knee"),
    ("F41.1", "Generalized anxiety disorder"),
]

def generate_blood_pressure():
    """Generates physiologically correlated systolic/diastolic values."""
    phenotype = random.choices(
        ['normal', 'prehypertension', 'hypertension_s1', 'hypertension_s2'], 
        weights=[0.40, 0.35, 0.15, 0.10]
    )[0]
    
    if phenotype == 'normal':
        return random.randint(90, 119), random.randint(60, 79)
    elif phenotype == 'prehypertension':
        return random.randint(120, 129), random.randint(80, 84)
    elif phenotype == 'hypertension_s1':
        return random.randint(130, 139), random.randint(85, 89)
    else: # Stage 2 Hypertension
        return random.randint(140, 180), random.randint(90, 110)

def main():
    print(f"[*] Fabricating {TOTAL_ROWS} synthetic compliance-safe clinical records...")
    
    start_date = datetime.now() - timedelta(days=3*365)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # 1. Write DDL boilerplate
        f.write("-- Synthetic PHI Database Seed File\n")
        f.write("CREATE TABLE IF NOT EXISTS patients_clinical_histories (\n")
        f.write("    id UUID PRIMARY KEY,\n")
        f.write("    full_name VARCHAR(255) NOT NULL,\n")
        f.write("    date_of_birth DATE NOT NULL,\n")
        f.write("    zip_code VARCHAR(10) NOT NULL,\n")
        f.write("    systolic_bp INT NOT NULL,\n")
        f.write("    diastolic_bp INT NOT NULL,\n")
        f.write("    icd10_code VARCHAR(10) NOT NULL,\n")
        f.write("    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL\n")
        f.write(");\n\n")
        
        # 2. Write Bulk Insert statements in optimized batches
        f.write("INSERT INTO patients_clinical_histories (id, full_name, date_of_birth, zip_code, systolic_bp, diastolic_bp, icd10_code, recorded_at) VALUES\n")
        
        for i in range(TOTAL_ROWS):
            row_id = str(uuid.uuid4())
            name = fake.name().replace("'", "''") # Escape single quotes for SQL safety
            dob = fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
            
            # To test k-anonymity later, we need a small subset of repeating ZIPs
            # We'll mix localized zip regions with a few rare ones
            if i % 100 == 0: 
                zip_code = "90210" # Hyper-isolated micro-cohort indicator
            else:
                zip_code = f"{random.randint(100, 999)}XX" # Anonymized regional prefix format
                
            systolic, diastolic = generate_blood_pressure()
            icd10, _ = random.choice(ICD10_POOL)
            
            # Scatter timestamps over 3 years
            random_days = random.randint(0, 3*365)
            random_seconds = random.randint(0, 86400)
            recorded_time = (start_date + timedelta(days=random_days, seconds=random_seconds)).strftime('%Y-%m-%d %H:%M:%S+00')
            
            terminator = ",\n" if i < TOTAL_ROWS - 1 else ";\n"
            f.write(f"    ('{row_id}', '{name}', '{dob}', '{zip_code}', {systolic}, {diastolic}, '{icd10}', '{recorded_time}'){terminator}")

    print(f"[+] Successfully wrote out database schema and fixtures to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()