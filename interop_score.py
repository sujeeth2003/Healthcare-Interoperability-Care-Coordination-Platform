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

