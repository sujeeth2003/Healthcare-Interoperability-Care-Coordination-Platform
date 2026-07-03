"""
interop_score.py

Computes an interoperability readiness score directly from the validator's
output. No separate estimation — the score is a straight count of
pass/fail checks the validator already performed.

Two components, each 0-100:
  completeness_score   = (required fields present) / (required fields total)
  standard_coding_score = (codeable fields using a standard system) /
                          (total codeable fields checked)

overall_score = 0.6 * completeness_score + 0.4 * standard_coding_score

Weighting rationale: a resource missing a required field cannot be
processed by a receiving system at all (hard failure), while a
non-standard code can sometimes still be read by a human or mapped later
(softer failure). 60/40 reflects that difference in severity.
"""

from fhir_validator import REQUIRED_FIELDS, CODEABLE_FIELD


def score_bundle(bundle, validation_results):
    """
    validation_results: list of dicts from fhir_validator.validate_bundle()
    Returns a dict with completeness_score, standard_coding_score,
    overall_score, and raw counts, for one patient bundle.
    """
    total_required_fields = 0
    missing_required_fields = 0
    total_codeable_fields = 0
    non_standard_codeable_fields = 0
    broken_references = 0

    for result in validation_results:
        rtype = result["resourceType"]
        total_required_fields += len(REQUIRED_FIELDS.get(rtype, []))
        missing_required_fields += len(result["missing_fields"])

