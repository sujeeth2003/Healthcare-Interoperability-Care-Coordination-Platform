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

