"""
Rich terminal report generator for AgentCourt.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from agent_court.core.models import AuditReport, VerdictStatus


def render_terminal_report(report: AuditReport, console: Console | None = None) -> None:
    if console is None:
        console = Console(legacy_windows=False)

    # Title Banner
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]🏛️  AGENTCOURT DOCKET & JUDICIAL VERDICT REPORT[/bold cyan]\n"
            f"[dim]Universal Adversarial Trajectory Auditor & Constitutional Patch Engine[/dim]",
            border_style="cyan",
        )
    )

    # Overview Metrics Table
    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", justify="right", style="cyan")

    table.add_row("Audit Window", f"{report.start_date} to {report.end_date} ({report.period_days} days)")
    table.add_row("Total Analyzed Sessions", f"{report.total_sessions:,}")
    table.add_row("Total Trajectory Steps", f"{report.total_steps:,}")
    table.add_row("Raw Heuristic Anomaly Triggers", f"{report.raw_incidents}")
    table.add_row("Acquitted False Alarms (Noise Filtered)", f"[green]{report.acquitted_count} ({report.filtering_efficiency:.1f}%)[/green]")
    table.add_row("Convicted Systemic Failures (True Drifts)", f"[red]{report.convicted_count}[/red]")
    table.add_row("Raw Friction Index", f"{report.raw_friction_index:.2f}%")
    table.add_row("True Net Friction Index", f"[bold green]{report.true_friction_index:.2f}%[/bold green]")

    console.print(table)
    console.print()

    # First Instance Hearings (Sample Dossiers)
    console.print("[bold yellow]⚖️  FIRST INSTANCE HEARINGS (Adversarial Dossiers)[/bold yellow]")
    console.print("─" * 78, style="dim")

    if not report.verdicts:
        console.print("[green]✓ No suspect anomalies or friction points detected in the analyzed period.[/green]")
    else:
        sample_verdicts = report.verdicts[:8]
        for v in sample_verdicts:
            status_badge = (
                f"[bold green]🟢 ACQUITTED[/bold green] [dim](Conf: {int(v.confidence * 100)}%)[/dim]"
                if v.status == VerdictStatus.ACQUITTED
                else f"[bold red]🔴 CONVICTED[/bold red] [dim](Conf: {int(v.confidence * 100)}%)[/dim]"
            )
            console.print(f"[{v.docket_id}] {status_badge} — [dim]Session {v.session_id[:8]}… : step {v.step_index}[/dim]")
            console.print(f"  [cyan]🏛️ Charge:[/cyan]  {v.accusation.charge}")
            console.print(f"  [yellow]⚖️ Defense:[/yellow] {v.defense.argument}")
            console.print(f"  [magenta]🧑‍⚖️ Ruling:[/magenta]  {v.judge_rationale}")
            if v.recommended_action and v.status == VerdictStatus.CONVICTED:
                console.print(f"  [dim red]⚡ Remedy:[/dim red]  {v.recommended_action}")
            console.print()

        if len(report.verdicts) > 8:
            console.print(f"[dim]... and {len(report.verdicts) - 8} more adjudicated dossiers.[/dim]\n")

    # Supreme Court Plenum Class Actions
    console.print("═" * 78, style="dim")
    console.print("[bold cyan]🧑‍⚖️  PLENUM OF THE SUPREME COURT: CONSOLIDATED CLASS ACTION RULINGS[/bold cyan]")
    console.print("─" * 78, style="dim")

    if not report.class_actions:
        console.print("[green]✓ Clean Judicial Sheet: No recurring systemic patterns warranted Class Action intervention.[/green]\n")
    else:
        for ca in report.class_actions:
            sev_color = "red" if ca.severity.value == "CRITICAL" else "yellow"
            console.print(
                f"[bold white]Case ID: {ca.case_id}[/bold white] "
                f"([{sev_color}]Severity: {ca.severity.value}[/{sev_color}] | "
                f"Occurrences: [bold]{ca.occurrences}[/bold] across [bold]{ca.sessions_affected}[/bold] sessions)"
            )
            console.print(f"[bold]Title:[/bold]   {ca.title}")
            console.print(f"[bold]Cause:[/bold]   {ca.category.value}")
            console.print(f"[dim]Evidence:[/dim] {ca.evidence_summary}")
            console.print()
            console.print(f"[bold green]📜 Prescribed Constitutional Remedy (Target: {ca.target_rule_file}):[/bold green]")
            
            # Format diff box
            patch_panel = Panel(
                ca.constitutional_remedy,
                style="green",
                border_style="green",
                title=f"Patch for {ca.target_rule_file}",
            )
            console.print(patch_panel)
            console.print()
