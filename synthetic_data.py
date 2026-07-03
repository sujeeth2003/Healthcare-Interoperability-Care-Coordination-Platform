"""
synthetic_data.py

Generates synthetic FHIR R4 resources: Patient, Condition, Observation,
MedicationRequest, CarePlan.

Mechanism: real EHR exports are imperfect. We reproduce that on purpose by
randomly deleting required fields and by randomly replacing standard codes
(LOINC/SNOMED/RxNorm) with free text, at a fixed defect rate. This gives the
validator and scorer real problems to find, instead of a clean dataset that
would make every score trivially 100%.

No real patient data is used or required anywhere in this project.
"""

import random
import uuid
from datetime import date, timedelta

random.seed(42)  # reproducible output run-to-run

FIRST_NAMES = ["James", "Maria", "Wei", "Fatima", "John", "Aisha", "Carlos",
               "Priya", "David", "Elena", "Mohammed", "Grace"]
LAST_NAMES = ["Smith", "Garcia", "Chen", "Khan", "Johnson", "Ali", "Rossi",
              "Patel", "Brown", "Nguyen", "Kim", "Davis"]
GENDERS = ["male", "female", "other", "unknown"]

# Real LOINC codes for common vital signs / labs
LOINC_OBSERVATIONS = [
    ("8480-6", "Systolic blood pressure", "mmHg"),
    ("8462-4", "Diastolic blood pressure", "mmHg"),
    ("8867-4", "Heart rate", "beats/min"),
    ("2160-0", "Creatinine", "mg/dL"),
    ("2339-0", "Glucose", "mg/dL"),
    ("4548-4", "Hemoglobin A1c", "%"),
]

# Real SNOMED CT codes for common chronic conditions
SNOMED_CONDITIONS = [
    ("44054006", "Type 2 diabetes mellitus"),
    ("38341003", "Hypertension"),
    ("195967001", "Asthma"),
    ("13645005", "Chronic obstructive pulmonary disease"),
    ("84114007", "Heart failure"),
]

# Real RxNorm codes for common medications
RXNORM_MEDICATIONS = [
    ("860975", "Metformin 500 MG"),
    ("197361", "Lisinopril 10 MG"),
    ("308136", "Atorvastatin 20 MG"),
    ("745679", "Albuterol 90 MCG inhaler"),
]

PROVIDER_ROLES = ["Primary Care Physician", "Cardiologist", "Endocrinologist",
                  "Care Coordinator", "Pharmacist"]

DEFECT_RATE = 0.30  # fraction of resources that get a deliberate defect


