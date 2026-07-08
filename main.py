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

