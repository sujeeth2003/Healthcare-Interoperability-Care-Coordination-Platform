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

        if rtype in CODEABLE_FIELD:
            total_codeable_fields += 1
            if result["coding_problems"]:
                non_standard_codeable_fields += 1

        broken_references += len(result["reference_problems"])

    completeness_score = (
        100.0 * (total_required_fields - missing_required_fields) / total_required_fields
        if total_required_fields else 100.0
    )
    standard_coding_score = (
        100.0 * (total_codeable_fields - non_standard_codeable_fields) / total_codeable_fields
        if total_codeable_fields else 100.0
    )
    overall_score = 0.6 * completeness_score + 0.4 * standard_coding_score

    return {
        "patient_id": bundle["patient"].get("id"),
        "completeness_score": round(completeness_score, 1),
        "standard_coding_score": round(standard_coding_score, 1),
        "overall_score": round(overall_score, 1),
        "missing_required_fields": missing_required_fields,
        "non_standard_codeable_fields": non_standard_codeable_fields,
        "broken_references": broken_references,
    }


def score_dataset(bundles, all_validation_results):
    """
    all_validation_results: list (one entry per patient) of lists of
    validation result dicts, aligned with `bundles`.
    Returns per-patient scores plus dataset-wide averages.
    """
    per_patient = [
        score_bundle(bundle, results)
        for bundle, results in zip(bundles, all_validation_results)
    ]
    n = len(per_patient) or 1
    dataset_summary = {
        "avg_completeness_score": round(sum(p["completeness_score"] for p in per_patient) / n, 1),
        "avg_standard_coding_score": round(sum(p["standard_coding_score"] for p in per_patient) / n, 1),
        "avg_overall_score": round(sum(p["overall_score"] for p in per_patient) / n, 1),
        "total_missing_fields": sum(p["missing_required_fields"] for p in per_patient),
        "total_non_standard_codings": sum(p["non_standard_codeable_fields"] for p in per_patient),
        "total_broken_references": sum(p["broken_references"] for p in per_patient),
        "patient_count": len(per_patient),
    }
    return per_patient, dataset_summary
