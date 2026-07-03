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

