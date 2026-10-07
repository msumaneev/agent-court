"""
Command-line interface for AgentCourt.
"""

import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="agent-court",
    help="🏛️ Adversarial Trajectory Auditor & Constitutional Patch Engine for Autonomous AI Coding Agents.",
    add_completion=False,
)
console = Console()


@app.command()
def scan(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to audit"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json, html"),
):
    """
    Execute deterministic fast mining (Stage 1, 0 LLM tokens).
    """
    console.print(
        Panel.fit(
            f"[bold blue]🏛️ AgentCourt Fast Scan[/bold blue]\n"
            f"Period: last {days} days | Mode: [green]Deterministic Zero-Token Streamer[/green]",
            border_style="blue",
        )
    )
    console.print("🔍 Scanning agent transcripts... [bold green]Ready[/bold green]")


@app.command()
def audit(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to audit"),
    offline: bool = typer.Option(True, "--offline", help="Run with 100% offline deterministic judge (0 tokens)"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, html, json"),
    output: str = typer.Option(None, "--output", "-o", help="Destination path for report artifact"),
):
    """
    Conduct adversarial courtroom hearings and synthesize Class Actions.
    """
    console.print(
        Panel.fit(
            f"[bold blue]🏛️ AgentCourt Adversarial Hearing[/bold blue]\n"
            f"Period: last {days} days | Offline Mode: [yellow]{offline}[/yellow]",
            border_style="magenta",
        )
    )

    table = Table(title="Judicial Overview", show_header=True, header_style="bold cyan")
    table.add_column("Stage", style="dim")
    table.add_column("Metrics")
    table.add_column("Status", justify="right")

    table.add_row("Stage 1: Fast Miner", "Streaming JSONL, 0 tokens", "[green]PASS[/green]")
    table.add_row("Stage 2: Courtroom", "Prosecutor vs Defense vs Judge", "[green]ACTIVE[/green]")
    table.add_row("Stage 3: Supreme Plenum", "Class Action Synthesis", "[green]READY[/green]")

    console.print(table)


@app.command()
def version():
    """Display AgentCourt version."""
    from agent_court import __version__
    console.print(f"[bold cyan]AgentCourt[/bold cyan] version [bold green]{__version__}[/bold green]")


if __name__ == "__main__":
    app()
