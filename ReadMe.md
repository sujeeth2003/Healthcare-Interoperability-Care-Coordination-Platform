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

## Validation Checks

### Required Fields

Ensures mandatory FHIR R4 fields exist for every resource.

### Standard Terminology

Verifies coded elements use standard systems: - LOINC - SNOMED CT -
RxNorm

### Reference Integrity

Checks that every `subject.reference` points to an existing patient.

## Scoring

-   **Completeness Score** = Required fields present ÷ Required fields
    total
-   **Standard Coding Score** = Standard coded fields ÷ Total coded
    fields
-   **Overall Score** = 0.6 × Completeness + 0.4 × Standard Coding

## Running

``` bash
python main.py
```

Outputs:

-   `validation_report.json`
-   `dashboard.html`

Open `dashboard.html` in any web browser.

## Technologies

-   Python 3
-   FHIR R4
-   JSON
-   HTML
-   JavaScript
-   Chart.js

## Future Improvements

-   Additional FHIR resources
-   Official FHIR profile validation
-   FastAPI REST API
-   Docker support
-   Database integration

## License

MIT License
