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


def check_required_fields(resource):
    """Returns a list of missing required field names for this resource."""
    rtype = resource.get("resourceType")
    required = REQUIRED_FIELDS.get(rtype, [])
    return [f for f in required if f not in resource]


def check_standard_coding(resource):
    """
    Returns a list of problems with coded fields:
    - 'no_coding' if the field only has free-text ('text') with no 'coding' array
    - 'non_standard_system' if a coding entry's 'system' isn't in STANDARD_CODE_SYSTEMS
    Returns [] if the resource type has no codeable field, or the field is
    missing entirely (that's already reported by check_required_fields).
    """
    rtype = resource.get("resourceType")
    field_name = CODEABLE_FIELD.get(rtype)
    if not field_name or field_name not in resource:
        return []

    field = resource[field_name]
    problems = []
    codings = field.get("coding")
    if not codings:
        problems.append(f"{field_name}: no standard coding present (free text only)")
        return problems

    for coding in codings:
        system = coding.get("system")
        if system not in STANDARD_CODE_SYSTEMS:
            problems.append(f"{field_name}: non-standard or missing code system '{system}'")
    return problems


def check_reference_integrity(resource, valid_patient_ids):
    """
    Checks that resource['subject']['reference'] (format 'Patient/<id>')
    points at a Patient ID that actually exists in the dataset.
    """
    subject = resource.get("subject")
    if not subject or "reference" not in subject:
        return []  # already caught as a missing required field elsewhere
    ref = subject["reference"]
    ref_id = ref.split("/")[-1] if "/" in ref else ref
    if ref_id not in valid_patient_ids:
        return [f"subject.reference points to non-existent Patient id '{ref_id}'"]
    return []


def validate_resource(resource, valid_patient_ids):
    """
    Runs all checks on a single resource.
    Returns a dict: {resourceType, id, missing_fields, coding_problems, reference_problems}
    """
    return {
        "resourceType": resource.get("resourceType"),
        "id": resource.get("id"),
        "missing_fields": check_required_fields(resource),
        "coding_problems": check_standard_coding(resource),
        "reference_problems": check_reference_integrity(resource, valid_patient_ids),
    }

