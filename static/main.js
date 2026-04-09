document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Identify which page we are on
    const path = window.location.pathname;
    
    // If we are on the audit page, run the analysis automatically
    if (path.includes('/audit')) {
        loadAuditReport();
    }
});

/**
 * BUTTON CONNECTION: Captured from analyzer.html
 */
function startPolyAudit() {
    const file = document.getElementById('fileInput').files[0];
    const textArea = document.getElementById('polyCode');

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            localStorage.setItem('sentinel_pending_code', e.target.result);
            window.location.href = '/audit';
        };
        reader.readAsText(file);
    } else {
        const code = textArea.value;
        localStorage.setItem('sentinel_pending_code', code);
        window.location.href = '/audit';
    }
}

/**
 * AUDIT PAGE LOGIC: Runs when audit.html loads
 */
async function loadAuditReport() {
    const code = localStorage.getItem('sentinel_pending_code');
    const timeDisplay = document.getElementById('timestamp');
    const downloadBtn = document.getElementById('downloadBtn');

    
    
    if (!code) {
        window.location.href = '/'; // Redirect home if no code is found
        return;
    }

    try {
        // Fetch analysis from the Python Backend on Render
        const response = await fetch('/api/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();

        if (data.status === "success") {
            if (downloadBtn && data.json_report) {
                downloadBtn.onclick = () => {
                    window.open('/' + data.json_report, '_blank');
                };
        }
            const smellBox = document.getElementById('smellBox');
            if (smellBox) {
                smellBox.innerHTML = data.smells.length > 0
                ? data.smells.map(s => `<span class="v-badge detected">${s}</span>`).join('')
                : '<span class="v-badge" style="color:#3fb950">No Code Smells</span>';
            }
            const sev = document.getElementById('severityLevel');
            if (sev) {
                sev.innerText = data.severity;
                sev.style.color =
                data.severity === "HIGH" ? "#f85149" :
                data.severity === "MEDIUM" ? "#f59e0b" :
                "#3fb950";
            }
            // REPORT
            const reportBox = document.getElementById('reportText');
            if (reportBox) {
                reportBox.innerText = data.report;
            }
            // --- YOUR COMPLEXITY CHART LOGIC ---
            renderAuditCharts(data);

            // Populate the Threat Detection tags
            const pBox = document.getElementById('patterns');
            if (pBox) {
                pBox.innerHTML = data.details.length > 0 
                    ? data.details.map(v => `<span class="v-badge detected">${v.replace('_', ' ')}</span>`).join('')
                    : '<span class="v-badge" style="color:#3fb950">SECURE LOGIC</span>';
            }

            if (timeDisplay) timeDisplay.innerText = "Analyzed: " + new Date().toLocaleString();
        }
    } catch (err) {
        console.error("Connection failed to Python Kernel:", err);
    }
}

/**
 * VISUALIZATION: Your Chart.js Implementation
 * DO NOT CHANGE: This renders the visual gauges
 */
function renderAuditCharts(data) {
    if (typeof Chart === 'undefined') return;

    // Complexity Gauge
    const ctxComp = document.getElementById('complexityChart');
    if (ctxComp) {
        const compVal = data.complexity === 'A' ? 20 : data.complexity === 'B' ? 60 : 100;
        
        new Chart(ctxComp.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [compVal, 100 - compVal],
                    backgroundColor: [data.complexity === 'A' ? '#3fb950' : '#f85149', '#161b22'],
                    borderWidth: 0,
                    borderRadius: 10
                }]
            },
            options: { cutout: '85%', plugins: { tooltip: { enabled: false } }, animation: { duration: 2000 } }
        });
        document.getElementById('gradeLabel').innerText = data.complexity;
        document.getElementById('gradeLabel').style.color = data.complexity === 'A' ? '#3fb950' : '#f85149';
    }

    // Risk Gauge
    const ctxRisk = document.getElementById('riskChart');
    if (ctxRisk) {
        const riskPct = data.score * 100;
        new Chart(ctxRisk.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [riskPct, 100 - riskPct],
                    backgroundColor: [riskPct > 50 ? '#f85149' : '#3fb1ff', '#161b22'],
                    borderWidth: 0,
                    borderRadius: 10
                }]
            },
            options: { cutout: '85%', plugins: { tooltip: { enabled: false } }, animation: { duration: 2500 } }
        });
        document.getElementById('riskLabel').innerText = riskPct.toFixed(0) + '%';
    }
}