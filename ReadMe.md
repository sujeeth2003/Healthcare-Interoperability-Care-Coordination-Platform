# Healthcare Interoperability & Care Coordination Platform

A Python project that simulates healthcare data exchange using the
**FHIR R4** standard, validates interoperability issues, computes
interoperability metrics, and generates a standalone HTML dashboard.

## Features

-   Generate synthetic FHIR R4 resources
-   Validate required FHIR fields
-   Detect non-standard terminology usage (LOINC, SNOMED CT, RxNorm)
-   Detect broken patient references
-   Compute interoperability readiness scores
-   Generate an interactive HTML dashboard
-   Export a JSON validation report

## Project Structure

``` text
Healthcare-Interoperability-Care-Coordination-Platform/
│
├── synthetic_data.py
├── fhir_validator.py
├── interop_score.py
├── main.py
├── dashboard.html
├── validation_report.json
└── README.md
```

## Validation Pipeline

``` text
Synthetic FHIR Dataset
        │
        ▼
FHIR Validation Engine
        │
        ▼
Interoperability Scoring
        │
        ▼
HTML Dashboard + JSON Report
```

## Supported Resources

-   Patient
-   Condition
-   Observation
-   MedicationRequest
-   CarePlan

