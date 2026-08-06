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

