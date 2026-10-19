"""
Command-line interface for AgentCourt.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent_court import __version__
from agent_court.adapters.antigravity import AntigravityAdapter
from agent_court.core.courtroom import Courtroom
from agent_court.core.docket_filter import DocketFilter
from agent_court.core.miner import FastMiner
from agent_court.core.models import AuditReport, DocketItem, IndividualVerdict
from agent_court.core.plenum import SupremePlenum, check_surface_entropy_budget
from agent_court.reporters.html import export_html_report
from agent_court.reporters.terminal import render_terminal_report

app = typer.Typer(
    name="agent-court",
    help="🏛️ Adversarial Trajectory Auditor & Constitutional Patch Engine for Autonomous AI Coding Agents.",
    add_completion=False,
)
console = Console(legacy_windows=False)


@app.command()
def scan(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to scan"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Custom path to brain directory or transcript.jsonl"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json"),
):
    """
    Execute deterministic fast mining (Stage 1, 0 LLM tokens).
    """
    console.print(
        Panel.fit(
            f"[bold blue]🏛️ AgentCourt Fast Scan[/bold blue]\n"
            f"Period: last [bold cyan]{days}[/bold cyan] days | Mode: [green]Deterministic Zero-Token Streamer[/green]",
            border_style="blue",
        )
    )

    adapter = AntigravityAdapter(base_dir=path)
    sessions = list(adapter.load_sessions(days=days))

    if not sessions:
        console.print(f"[yellow]No agent transcripts found in the last {days} days at: {adapter.base_dir}[/yellow]")
        return

    miner = FastMiner()
    docket_filter = DocketFilter()

    total_steps = 0
    all_raw_dockets: list[DocketItem] = []

    with console.status("[bold green]Mining trajectories...[/bold green]"):
        for session_id, steps in sessions:
            total_steps += len(steps)
            dockets = miner.mine_session(session_id, steps)
            all_raw_dockets.extend(dockets)

    filtered_dockets = docket_filter.filter_dockets(all_raw_dockets)

    if format.lower() == "json":
        data = {
            "period_days": days,
            "total_sessions": len(sessions),
            "total_steps": total_steps,
            "raw_incidents": len(all_raw_dockets),
            "dockets": [d.model_dump() for d in filtered_dockets],
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    table = Table(title="Mining Results (Stage 1)", show_header=True, header_style="bold cyan")
    table.add_column("Docket ID", style="bold")
    table.add_column("Session", style="dim")
    table.add_column("Type", style="yellow")
    table.add_column("Severity")
    table.add_column("Reps", justify="right")
    table.add_column("Trigger Marker")

    for d in filtered_dockets[:15]:
        sev_style = "red" if d.severity.value in ("CRITICAL", "HIGH") else "yellow"
        table.add_row(
            d.docket_id,
            d.session_id[:8] + "…",
            d.incident_type.value,
            f"[{sev_style}]{d.severity.value}[/{sev_style}]",
            str(d.repeat_count),
            d.trigger_marker[:55] + "…",
        )

    console.print(table)
    console.print(
        f"\n[bold]Scanned {len(sessions)} sessions ({total_steps:,} steps). "
        f"Found {len(all_raw_dockets)} raw triggers collapsed to {len(filtered_dockets)} unique dockets.[/bold]\n"
    )


@app.command()
def audit(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to audit"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Custom path to brain directory or transcript.jsonl"),
    offline: bool = typer.Option(True, "--offline/--no-offline", help="Run with 100% offline deterministic judge (0 tokens)"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, html, json"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Destination path for report artifact (HTML or JSON)"),
):
    """
    Conduct adversarial courtroom hearings and synthesize Class Actions.
    """
    adapter = AntigravityAdapter(base_dir=path)
    sessions = list(adapter.load_sessions(days=days))

    if not sessions:
        console.print(f"[yellow]No agent transcripts found in the last {days} days at: {adapter.base_dir}[/yellow]")
        return

    miner = FastMiner()
    docket_filter = DocketFilter()
    courtroom = Courtroom(offline=offline)
    plenum = SupremePlenum()

    total_steps = 0
    all_raw_dockets: list[DocketItem] = []

    with console.status("[bold green]Conducting Stage 1 & Stage 2 Judicial Hearings...[/bold green]"):
        for session_id, steps in sessions:
            total_steps += len(steps)
            dockets = miner.mine_session(session_id, steps)
            all_raw_dockets.extend(dockets)

        filtered_dockets = docket_filter.filter_dockets(all_raw_dockets)
        verdicts = courtroom.adjudicate_all(filtered_dockets)
        class_actions = plenum.synthesize_class_actions(verdicts)

    now = datetime.now(timezone.utc)
    start_dt = now - timedelta(days=days)

    acquitted_count = sum(1 for v in verdicts if v.status.value == "ACQUITTED")
    convicted_count = sum(1 for v in verdicts if v.status.value == "CONVICTED")
    raw_incidents = len(filtered_dockets)

    raw_friction_index = (raw_incidents / total_steps * 100) if total_steps > 0 else 0.0
    filtering_efficiency = (acquitted_count / raw_incidents * 100) if raw_incidents > 0 else 0.0
    true_friction_index = (convicted_count / total_steps * 100) if total_steps > 0 else 0.0
    always_on_bytes, budget_pct, grad_rec = check_surface_entropy_budget()

    report = AuditReport(
        period_days=days,
        start_date=start_dt.strftime("%Y-%m-%d"),
        end_date=now.strftime("%Y-%m-%d"),
        total_sessions=len(sessions),
        total_steps=total_steps,
        raw_incidents=raw_incidents,
        acquitted_count=acquitted_count,
        convicted_count=convicted_count,
        raw_friction_index=raw_friction_index,
        filtering_efficiency=filtering_efficiency,
        true_friction_index=true_friction_index,
        always_on_bytes=always_on_bytes,
        entropy_budget_pct=budget_pct,
        graduation_recommended=grad_rec,
        verdicts=verdicts,
        class_actions=class_actions,
    )

    # Render Terminal output
    render_terminal_report(report, console=console)

    # Export formats
    if format.lower() == "html" or (output and output.endswith(".html")):
        out_file = output or f"reports/audit_report_{now.strftime('%Y%m%d_%H%M%S')}.html"
        saved = export_html_report(report, out_file)
        console.print(f"[bold green]HTML Judicial Report exported to:[/bold green] {saved}")

    elif format.lower() == "json" or (output and output.endswith(".json")):
        out_file = output or f"reports/audit_report_{now.strftime('%Y%m%d_%H%M%S')}.json"
        p = Path(out_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"[bold green]JSON Audit Report exported to:[/bold green] {p}")


@app.command()
def version():
    """Display AgentCourt version."""
    console.print(f"[bold cyan]AgentCourt[/bold cyan] version [bold green]{__version__}[/bold green]")


if __name__ == "__main__":
    app()
