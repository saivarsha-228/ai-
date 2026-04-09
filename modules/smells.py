def detect_code_smells(code):

    smells = []

    if len(code.splitlines()) > 250:
        smells.append("Large File Size")

    if code.count("if(") + code.count("if (") > 10:
        smells.append("Too Many Conditional Branches")

    if code.count("for(") + code.count("while(") > 8:
        smells.append("Excessive Looping")

    if "global " in code:
        smells.append("Global Variable Usage")

    if "goto " in code:
        smells.append("Use of GOTO Statement")

    return smells