"""
main.py

Runs the whole pipeline and writes two output files:
  - validation_report.json  (raw validator + score output, for inspection or re-use)
  - dashboard.html          (open this in any browser, no server needed)

Run with:  python main.py
"""

import json
from synthetic_data import generate_dataset
from fhir_validator import validate_bundle
from interop_score import score_dataset


def build_report(num_patients=25):
    bundles = generate_dataset(num_patients=num_patients)
    valid_patient_ids = {b["patient"]["id"] for b in bundles if "id" in b["patient"]}

    all_validation_results = [validate_bundle(b, valid_patient_ids) for b in bundles]
    per_patient_scores, dataset_summary = score_dataset(bundles, all_validation_results)

    # Attach human-readable display info (name, providers, meds, goals) for the dashboard
    display_rows = []
    for bundle, results, score in zip(bundles, all_validation_results, per_patient_scores):
        patient = bundle["patient"]
        name_parts = patient.get("name", [{}])[0]
        full_name = " ".join(name_parts.get("given", ["(no given name)"])) + " " + name_parts.get("family", "(no family name)")

        medication_names = []
        for m in bundle["medications"]:
            med = m.get("medicationCodeableConcept", {})
            codings = med.get("coding")
            medication_names.append(codings[0]["display"] if codings else med.get("text", "(unspecified)"))

        condition_names = []
        for c in bundle["conditions"]:
            code = c.get("code", {})
            codings = code.get("coding")
            condition_names.append(codings[0]["display"] if codings else code.get("text", "(unspecified)"))

        providers = bundle["care_plan"].get("careTeam", [])
        activities = [a["detail"]["description"] for a in bundle["care_plan"].get("activity", [])]

        error_count = sum(
            len(r["missing_fields"]) + len(r["coding_problems"]) + len(r["reference_problems"])
            for r in results
        )

        display_rows.append({
            "patient_id": patient.get("id", "(missing id)"),
            "name": full_name,
            "conditions": condition_names,
            "medications": medication_names,
            "providers": [f"{p['name']} ({p['role']})" for p in providers],
            "activities": activities,
            "score": score,
            "error_count": error_count,
        })

