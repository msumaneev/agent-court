"""
Supreme Court Plenum Engine (Stage 3).
Aggregates convicted verdicts across sessions into high-level Class Actions and synthesizes constitutional remedies.
Includes SurfaceSpec Layer Routing and Cue -> Lesson -> Evidence ExperienceTriad (inspired by Google Research Harness², arXiv:2610.14224).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from agent_court.core.models import (
    ClassActionRuling,
    ExperienceTriad,
    IncidentType,
    IndividualVerdict,
    RootCauseCategory,
    SeverityLevel,
    VerdictStatus,
)

# Maximum recommended size (in bytes) for Always-On root instruction surface (AGENTS.md)
# Prevents Instruction Entropy / rule bloat across evolutionary cycles.
ALWAYS_ON_MAX_BYTES = 16384  # 16 KB


def check_surface_entropy_budget(workspace_dir: Optional[Path] = None) -> Tuple[int, float, bool]:
    """
    Measures the size of Always-On instruction files (AGENTS.md / CLAUDE.md) against the 16 KB cap.
    Returns (always_on_bytes, budget_pct, graduation_recommended).
    """
    base = workspace_dir or Path.cwd()
    candidates = [
        base / "AGENTS.md",
        base / "CLAUDE.md",
        base / ".agent" / "rules" / "AGENTS.md",
    ]
    total_bytes = 0
    for c in candidates:
        if c.exists() and c.is_file():
            try:
                total_bytes += c.stat().st_size
            except OSError:
                pass
            break
    pct = round((total_bytes / ALWAYS_ON_MAX_BYTES) * 100.0, 1) if ALWAYS_ON_MAX_BYTES else 0.0
    return total_bytes, pct, (total_bytes > ALWAYS_ON_MAX_BYTES or pct >= 85.0)


class SupremePlenum:
    """
    Synthesizes systemic Class Action Rulings from cross-session convicted verdicts.
    """

    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir

    def synthesize_class_actions(self, verdicts: List[IndividualVerdict]) -> List[ClassActionRuling]:
        convicted = [v for v in verdicts if v.status == VerdictStatus.CONVICTED]
        if not convicted:
            return []

        _, _, over_budget = check_surface_entropy_budget(self.workspace_dir)

        # Group convicted verdicts by incident type
        groups: Dict[IncidentType, List[IndividualVerdict]] = {}
        for v in convicted:
            groups.setdefault(v.incident_type, []).append(v)

        # Also collect contrastive recoveries across all verdicts (including acquitted self-corrections!) by incident_type
        recoveries_by_type: Dict[IncidentType, List[str]] = {}
        for v in verdicts:
            if v.recovery_evidence and v.recovery_evidence.strip():
                rec_list = recoveries_by_type.setdefault(v.incident_type, [])
                entry = f"[{v.session_id[:8]} step #{v.step_index}]: {v.recovery_evidence}"
                if entry not in rec_list and len(rec_list) < 3:
                    rec_list.append(entry)

        rulings: List[ClassActionRuling] = []
        counter = 1

        for inc_type, v_list in groups.items():
            sessions = list({v.session_id for v in v_list})
            occurrences = len(v_list)
            contrasts = recoveries_by_type.get(inc_type, [])

            if inc_type == IncidentType.TOOL_LOOP:
                evidence_str = f"Detected {occurrences} instances of unvaried sequential tool calls across {len(sessions)} sessions."
                if contrasts:
                    evidence_str += f" Contrastive Recovery: {contrasts[0]}"
                patch_scope = "DOMAIN" if over_budget else "INVARIANT"
                target_file = "rules/anti-loop.md" if patch_scope == "DOMAIN" else "AGENTS.md"
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="Serial Tool Loop & Unchecked Polling Cadence",
                        severity=SeverityLevel.CRITICAL,
                        category=RootCauseCategory.CAT_B_TOOL_DEFECT,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=evidence_str,
                        constitutional_remedy=(
                            "+ ### Zero-Polling & Anti-Loop Protocol:\n"
                            "+ Agents MUST NOT invoke the same tool with identical or failing parameters consecutively.\n"
                            "+ After two consecutive identical executions without progress, agent MUST yield turn or alter strategy."
                        ),
                        target_rule_file=target_file,
                        patch_scope=patch_scope,
                        experience=ExperienceTriad(
                            cue="When invoking any CLI command, status check, or MCP tool that fails or returns unchanged state twice consecutively",
                            lesson="Immediately halt identical calls after 2 attempts; switch tool/arguments or yield turn instead of looping",
                            evidence=evidence_str,
                        ),
                        recovery_contrasts=contrasts,
                    )
                )
                counter += 1

            elif inc_type == IncidentType.USER_FRICTION:
                evidence_str = f"Human developer intervened with explicit corrective friction in {len(sessions)} sessions ({occurrences} times)."
                if contrasts:
                    evidence_str += f" Contrastive Recovery: {contrasts[0]}"
                patch_scope = "DOMAIN" if over_budget else "INVARIANT"
                target_file = "rules/intent-gate.md" if patch_scope == "DOMAIN" else "AGENTS.md"
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="User Correction Interruption & Prompt Drift",
                        severity=SeverityLevel.HIGH,
                        category=RootCauseCategory.CAT_A_RULE_AMBIGUITY,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=evidence_str,
                        constitutional_remedy=(
                            "+ ### Intent Verification Gate:\n"
                            "+ When executing architectural or destructive modifications, provide a succinct preview.\n"
                            "+ If requirements are ambiguous, clarify before executing speculative tool sequences."
                        ),
                        target_rule_file=target_file,
                        patch_scope=patch_scope,
                        experience=ExperienceTriad(
                            cue="Before starting multi-file architectural edits, destructive operations, or unconfirmed speculative tool sequences",
                            lesson="Output a concise plan preview and wait for explicit user confirmation rather than assuming intent",
                            evidence=evidence_str,
                        ),
                        recovery_contrasts=contrasts,
                    )
                )
                counter += 1

            elif inc_type == IncidentType.TOOL_FAILURE:
                evidence_str = f"Encountered {occurrences} unhandled tool command exit errors or crashes."
                if contrasts:
                    evidence_str += f" Contrastive Recovery: {contrasts[0]}"
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="Repeated Tool Execution Exceptions Without Fallback",
                        severity=SeverityLevel.HIGH,
                        category=RootCauseCategory.CAT_D_CAPABILITY_GAP,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=evidence_str,
                        constitutional_remedy=(
                            "+ ### Tool Resilience & Fallback Handling:\n"
                            "+ Inspect stderr and return codes on every command before proceeding.\n"
                            "+ If a tool fails twice, formulate alternative approach or report exact limitation immediately."
                        ),
                        target_rule_file="rules/tool-resilience.md",
                        patch_scope="DOMAIN",
                        experience=ExperienceTriad(
                            cue="When a shell command, script, or MCP tool exits with a non-zero code or exception",
                            lesson="Inspect stderr immediately and switch to the designated fallback tool instead of blind retrying",
                            evidence=evidence_str,
                        ),
                        recovery_contrasts=contrasts,
                    )
                )
                counter += 1

            elif inc_type == IncidentType.TRAJECTORY_BLOAT:
                evidence_str = f"Sessions exceeding 70 steps observed {occurrences} times."
                if contrasts:
                    evidence_str += f" Contrastive Recovery: {contrasts[0]}"
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="Unconstrained Trajectory Horizon (Session Bloat)",
                        severity=SeverityLevel.MEDIUM,
                        category=RootCauseCategory.CAT_C_CONTEXT_DRIFT,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=evidence_str,
                        constitutional_remedy=(
                            "+ ### Bounded Turn Horizon:\n"
                            "+ Deconstruct complex multi-phase tasks into checkpoints.\n"
                            "+ Compact working context every 30 steps to prevent hallucination and instruction wash-out."
                        ),
                        target_rule_file="rules/context-horizon.md",
                        patch_scope="DOMAIN",
                        experience=ExperienceTriad(
                            cue="When a single session trajectory exceeds 35 steps or spans multiple sub-tasks",
                            lesson="Decompose remaining work into subagent handoffs or checkpoint summaries to prevent context drift",
                            evidence=evidence_str,
                        ),
                        recovery_contrasts=contrasts,
                    )
                )
                counter += 1

        return rulings

