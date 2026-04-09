def generate_report(score, severity, complexity, smells, vulnerabilities):

    report = f"""
CODE SECURITY ANALYSIS REPORT
----------------------------------

Risk Score : {score}
Severity   : {severity}
Complexity : {complexity}

Detected Vulnerabilities:
{', '.join(vulnerabilities) if vulnerabilities else 'None'}

Code Smells:
{', '.join(smells) if smells else 'None'}

Recommendation:
Review high complexity functions and remove risky patterns such as eval() or hardcoded secrets.
"""

    return report.strip()