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

    report = {
        "dataset_summary": dataset_summary,
        "patients": display_rows,
    }
    return report


def render_dashboard(report, output_path="dashboard.html"):
    data_json = json.dumps(report)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Healthcare Interoperability & Care Coordination Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
  body { font-family: -apple-system, Segoe UI, Arial, sans-serif; background:#f4f6f8; margin:0; padding:24px; color:#1b1f23; }
  h1 { font-size: 22px; margin-bottom: 4px; }
  .subtitle { color:#5b6572; margin-bottom:24px; }
  .summary-grid { display:grid; grid-template-columns: repeat(4, 1fr); gap:16px; margin-bottom:28px; }
  .card { background:white; border-radius:10px; padding:16px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .card .value { font-size:28px; font-weight:700; }
  .card .label { color:#5b6572; font-size:13px; margin-top:4px; }
  .charts { display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:28px; }
  .chart-box { background:white; border-radius:10px; padding:16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  table { width:100%; border-collapse: collapse; background:white; border-radius:10px; overflow:hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08);}
  th, td { text-align:left; padding:10px 12px; border-bottom:1px solid #eef0f2; font-size:13px; vertical-align:top; }
  th { background:#eef1f4; }
  .score-good { color:#1a7f37; font-weight:600; }
  .score-mid  { color:#9a6700; font-weight:600; }
  .score-bad  { color:#cf222e; font-weight:600; }
  .tag { display:inline-block; background:#eef1f4; border-radius:6px; padding:1px 6px; margin:1px; font-size:12px; }
</style>
</head>
<body>

<h1>Healthcare Interoperability & Care Coordination Dashboard</h1>
<div class="subtitle">Synthetic FHIR R4 dataset — validated against required fields and standard terminology (LOINC / SNOMED CT / RxNorm)</div>

<div class="summary-grid" id="summaryGrid"></div>

<div class="charts">
  <div class="chart-box"><canvas id="scoreChart" height="180"></canvas></div>
  <div class="chart-box"><canvas id="issueChart" height="180"></canvas></div>
</div>

<table id="patientTable">
  <thead>
    <tr>
      <th>Patient</th>
      <th>Conditions</th>
      <th>Medications</th>
      <th>Care Team</th>
      <th>Care Plan Activities</th>
      <th>Completeness</th>
      <th>Standard Coding</th>
      <th>Overall Score</th>
      <th>Issues Found</th>
    </tr>
  </thead>
  <tbody></tbody>
</table>

<script>
const report = __DATA_JSON__;

function scoreClass(score) {
  if (score >= 85) return "score-good";
  if (score >= 60) return "score-mid";
  return "score-bad";
}

// --- Summary cards ---
const s = report.dataset_summary;
const summaryGrid = document.getElementById("summaryGrid");
const cards = [
  ["Patients in dataset", s.patient_count, ""],
  ["Avg. overall score", s.avg_overall_score + "%", ""],
  ["Missing required fields (total)", s.total_missing_fields, ""],
  ["Non-standard codings (total)", s.total_non_standard_codings, ""],
];
summaryGrid.innerHTML = cards.map(c =>
  `<div class="card"><div class="value">${c[1]}</div><div class="label">${c[0]}</div></div>`
).join("");

// --- Chart 1: overall score per patient ---
const ctx1 = document.getElementById("scoreChart").getContext("2d");
new Chart(ctx1, {
  type: "bar",
  data: {
    labels: report.patients.map(p => p.name.trim().slice(0, 14)),
    datasets: [{
      label: "Overall interoperability score",
      data: report.patients.map(p => p.score.overall_score),
      backgroundColor: report.patients.map(p =>
        p.score.overall_score >= 85 ? "#2da44e" : p.score.overall_score >= 60 ? "#bf8700" : "#cf222e"
      )
    }]
  },
  options: {
    responsive: true,
    plugins: { title: { display: true, text: "Overall Interoperability Score per Patient" } },
    scales: { y: { beginAtZero: true, max: 100 } }
  }
});

// --- Chart 2: issue type breakdown across dataset ---
const ctx2 = document.getElementById("issueChart").getContext("2d");
new Chart(ctx2, {
  type: "doughnut",
  data: {
    labels: ["Missing required fields", "Non-standard codings", "Broken references"],
    datasets: [{
      data: [s.total_missing_fields, s.total_non_standard_codings, s.total_broken_references],
      backgroundColor: ["#cf222e", "#bf8700", "#57606a"]
    }]
  },
  options: {
    responsive: true,
    plugins: { title: { display: true, text: "Data Quality Issues by Type (Dataset-wide)" } }
  }
});

// --- Patient table ---
const tbody = document.querySelector("#patientTable tbody");
tbody.innerHTML = report.patients.map(p => `
  <tr>
    <td><strong>${p.name}</strong><br><span style="color:#5b6572;font-size:11px;">${p.patient_id}</span></td>
    <td>${p.conditions.map(c => `<span class="tag">${c}</span>`).join("") || "—"}</td>
    <td>${p.medications.map(m => `<span class="tag">${m}</span>`).join("") || "—"}</td>
    <td>${p.providers.join("<br>") || "—"}</td>
    <td>${p.activities.join("<br>") || "—"}</td>
    <td class="${scoreClass(p.score.completeness_score)}">${p.score.completeness_score}%</td>
    <td class="${scoreClass(p.score.standard_coding_score)}">${p.score.standard_coding_score}%</td>
    <td class="${scoreClass(p.score.overall_score)}">${p.score.overall_score}%</td>
    <td>${p.error_count}</td>
  </tr>
`).join("");
</script>

