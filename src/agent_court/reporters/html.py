"""
HTML Digest generator for AgentCourt.
"""

from __future__ import annotations

from pathlib import Path
from agent_court.core.models import AuditReport, VerdictStatus


def export_html_report(report: AuditReport, output_path: str | Path) -> Path:
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    verdicts_html = ""
    for v in report.verdicts:
        badge_class = "badge-acquitted" if v.status == VerdictStatus.ACQUITTED else "badge-convicted"
        badge_text = "🟢 ACQUITTED" if v.status == VerdictStatus.ACQUITTED else "🔴 CONVICTED"
        verdicts_html += f"""
        <div class="card dossier">
            <div class="dossier-header">
                <span class="docket-id">[{v.docket_id}]</span>
                <span class="badge {badge_class}">{badge_text} ({int(v.confidence * 100)}%)</span>
                <span class="session-info">Session: {v.session_id[:12]}… | Step: {v.step_index}</span>
            </div>
            <div class="dossier-body">
                <p><strong>🏛️ Charge:</strong> {v.accusation.charge}</p>
                <p><strong>⚖️ Defense:</strong> {v.defense.argument}</p>
                <p><strong>🧑‍⚖️ Ruling:</strong> {v.judge_rationale}</p>
                {f'<p class="remedy"><strong>⚡ Action:</strong> {v.recommended_action}</p>' if v.recommended_action and v.status == VerdictStatus.CONVICTED else ''}
            </div>
        </div>
        """

    class_actions_html = ""
    for ca in report.class_actions:
        class_actions_html += f"""
        <div class="card class-action">
            <div class="class-header">
                <h3>{ca.case_id}: {ca.title}</h3>
                <span class="badge badge-convicted">{ca.severity.value}</span>
            </div>
            <p><strong>Cause:</strong> {ca.category.value}</p>
            <p><strong>Impact:</strong> {ca.occurrences} occurrences across {ca.sessions_affected} sessions</p>
            <p><strong>Evidence:</strong> {ca.evidence_summary}</p>
            <div class="patch-box">
                <div class="patch-title">Prescribed Remedy ({ca.target_rule_file}):</div>
                <pre><code>{ca.constitutional_remedy}</code></pre>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentCourt Judicial Audit Report</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --text: #f8fafc;
            --text-dim: #94a3b8;
            --border: #334155;
            --accent: #38bdf8;
            --green: #4ade80;
            --red: #f87171;
            --yellow: #facc15;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            margin: 0 0 8px 0;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }}
        .metric-val {{
            font-size: 26px;
            font-weight: bold;
            color: var(--accent);
        }}
        .metric-lbl {{
            color: var(--text-dim);
            font-size: 13px;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 16px;
        }}
        .dossier-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }}
        .badge {{
            font-size: 12px;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        .badge-acquitted {{
            background: rgba(74, 222, 128, 0.15);
            color: var(--green);
            border: 1px solid var(--green);
        }}
        .badge-convicted {{
            background: rgba(248, 113, 113, 0.15);
            color: var(--red);
            border: 1px solid var(--red);
        }}
        .patch-box {{
            background: #020617;
            border: 1px solid var(--green);
            border-radius: 6px;
            padding: 12px;
            margin-top: 12px;
        }}
        .patch-title {{
            color: var(--green);
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 6px;
        }}
        pre {{
            margin: 0;
            color: #86efac;
            font-family: monospace;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏛️ AgentCourt Judicial Audit Report</h1>
            <p style="color: var(--text-dim); margin: 0;">Period: {report.start_date} to {report.end_date} ({report.period_days} days)</p>
        </header>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-val">{report.total_sessions}</div>
                <div class="metric-lbl">Total Sessions</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{report.total_steps:,}</div>
                <div class="metric-lbl">Trajectory Steps</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{report.raw_incidents}</div>
                <div class="metric-lbl">Raw Anomalies</div>
            </div>
            <div class="metric-card">
                <div class="metric-val" style="color: var(--green);">{report.filtering_efficiency:.1f}%</div>
                <div class="metric-lbl">Noise Elimination</div>
            </div>
            <div class="metric-card">
                <div class="metric-val" style="color: var(--green);">{report.true_friction_index:.2f}%</div>
                <div class="metric-lbl">True Net Friction Index</div>
            </div>
        </div>

        <h2>🧑‍⚖️ Supreme Court Class Action Rulings</h2>
        {class_actions_html if class_actions_html else '<p style="color: var(--green);">No systemic Class Action rulings required.</p>'}

        <h2 style="margin-top: 40px;">⚖️ Adjudicated Dossiers (First Instance Hearings)</h2>
        {verdicts_html}
    </div>
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")
    return out
