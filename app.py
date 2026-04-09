from flask import Flask, request,render_template, jsonify, send_from_directory
import lizard
import os
import json
import sqlite3
from datetime import datetime

from modules.smells import detect_code_smells
from modules.vulnerabilities import detect_vulnerabilities
from modules.risk import calculate_risk
from modules.report import generate_report
from modules.history import init_db, save_scan
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

print("🔥 THIS FILE IS RUNNING")

app = Flask(__name__)
def generate_pdf(report_text, filename):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []
    for line in report_text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)

init_db()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/json')
def json_page():
    return send_from_directory('.', 'json.html')

@app.route('/audit')
def audit():
    return render_template('audit.html')

@app.route('/main.js')
def serve_js():
    return send_from_directory('.', 'main.js')

@app.route('/api/json-reports')
def json_reports():
    files = os.listdir('reports')
    return jsonify(files)

@app.route('/reports/<path:filename>')
def download_report(filename):
    return send_from_directory('reports', filename)

@app.route('/api/audit', methods=['POST'])
def run_polyglot_audit():

    data = request.json
    code_content = data.get('code', '')

    if not code_content:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    try:

        analysis = lizard.analyze_file.analyze_source_code(
            "input_stream.txt", code_content
        )

        if analysis.function_list:
            avg_complexity = sum(
                f.cyclomatic_complexity for f in analysis.function_list
            ) / len(analysis.function_list)
        else:
            avg_complexity = (
                code_content.count("if") +
                code_content.count("for") +
                code_content.count("while")
            ) * 0.5 + 1

        grade = "A" if avg_complexity <= 5 else "B" if avg_complexity <= 12 else "C"

        vulnerabilities = detect_vulnerabilities(code_content)

        smells = detect_code_smells(code_content)

        risk_score, severity = calculate_risk(
            vulnerabilities,
            smells,
            avg_complexity
        )

        report = generate_report(
            risk_score,
            severity,
            round(avg_complexity,1),
            smells,
            vulnerabilities
        )
        print("Saving scan:", risk_score, severity, avg_complexity)

        save_scan(risk_score, severity, avg_complexity)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report_data = {
            "risk_score": risk_score,
            "severity": severity,
            "complexity": avg_complexity,
            "vulnerabilities": vulnerabilities,
            "smells": smells,
            "report": report,
            "timestamp": timestamp
        }

        os.makedirs("reports", exist_ok=True)

        json_file = f"reports/report_{report_data['timestamp']}.json"

        with open(json_file, "w") as f:
            json.dump(report_data, f, indent=4)
            pdf_filename = f"report_{timestamp}.pdf"
            pdf_path = os.path.join("reports", pdf_filename)
            generate_pdf(report, pdf_path)

        return jsonify({
            "status": "success",
            "score": risk_score,
            "severity": severity,
            "complexity": grade,
            "raw_complexity": round(avg_complexity,1),
            "details": vulnerabilities,
            "smells": smells,
            "report": report,
            "json_report": json_file,
            "pdf_report": f"reports/{pdf_filename}"
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/history')
def get_history():
    try:
        db_path = os.path.join(os.getcwd(), "coderisk_history.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scans")
        rows = cursor.fetchall()

        conn.close()

        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "timestamp": row[1],
                "risk_score": row[2],
                "severity": row[3],
                "complexity": row[4],
                "file": f"reports/report_{row[1].replace('-', '').replace(':', '').replace(' ', '_')}.json"
            })

        return jsonify(history)
        

    except Exception as e:
        return jsonify({"error": str(e)})


# ✅ ALWAYS KEEP THIS AT THE VERY END
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)