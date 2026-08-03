"""
fhir_validator.py

Validates FHIR R4 resources against two concrete, checkable rules:

1. REQUIRED FIELD PRESENCE — per FHIR R4, each resource type has fields
   marked cardinality 1..1 or 1..* (mandatory). We check those exact fields.
2. STANDARD TERMINOLOGY BINDING — a coded field must reference a real
   standard code system URI. If it instead only has "text" (free text) or
   uses an unrecognized system string, that's a coding-standard failure,
   because two different systems cannot machine-match on free text.

This module does not guess or use heuristics. It checks explicit rules
taken from the FHIR R4 specification.
"""

STANDARD_CODE_SYSTEMS = {
    "http://loinc.org",
    "https://www.snomed.org/about-us",
    "http://www.nlm.nih.gov/research/umls/rxnorm",
    "http://terminology.hl7.org/CodeSystem/condition-clinical",
    "http://hl7.org/fhir/us/core/CodeSystem/careplan-category",
}

REQUIRED_FIELDS = {
    "Patient": ["resourceType", "id", "identifier", "name", "gender", "birthDate"],
    "Condition": ["resourceType", "id", "subject", "clinicalStatus", "code"],
    "Observation": ["resourceType", "id", "status", "code", "subject"],
    "MedicationRequest": ["resourceType", "id", "status", "intent",
                           "medicationCodeableConcept", "subject"],
    "CarePlan": ["resourceType", "id", "status", "intent", "subject",
                 "category", "activity"],
}

# Which field on each resource type carries the clinically coded concept
CODEABLE_FIELD = {
    "Condition": "code",
    "Observation": "code",
    "MedicationRequest": "medicationCodeableConcept",
}


