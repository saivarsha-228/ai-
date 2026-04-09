def calculate_risk(vulnerabilities, smells, complexity):

    risk_score = round(
        min(
            (len(vulnerabilities) * 0.25) +
            (len(smells) * 0.15) +
            (complexity * 0.03),
            0.99
        ),
        2
    )

    if risk_score < 0.30:
        severity = "LOW"
    elif risk_score < 0.60:
        severity = "MEDIUM"
    else:
        severity = "HIGH"

    return risk_score, severity