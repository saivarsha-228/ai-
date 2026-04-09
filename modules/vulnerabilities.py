def detect_vulnerabilities(code):

    threat_library = {
        'INJECTION_VECTOR': ['eval(', 'exec(', 'system(', 'SELECT *', 'DROP TABLE'],
        'SENSITIVE_DATA': ['password', 'secret_key', 'api_token'],
        'PERMISSION_RISK': ['chmod 777', 'sudo ']
    }

    detected = []

    for category, keys in threat_library.items():
        for key in keys:
            if key.lower() in code.lower():
                detected.append(category)
                break

    return detected