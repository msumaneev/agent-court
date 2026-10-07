"""
Supreme Court Plenum Engine (Stage 3).
Aggregates convicted verdicts across sessions into high-level Class Actions and synthesizes constitutional remedies.
"""

from __future__ import annotations

from typing import Dict, List
from agent_court.core.models import (
    ClassActionRuling,
    IncidentType,
    IndividualVerdict,
    RootCauseCategory,
    SeverityLevel,
    VerdictStatus,
)


class SupremePlenum:
    """
    Synthesizes systemic Class Action Rulings from cross-session convicted verdicts.
    """

    def synthesize_class_actions(self, verdicts: List[IndividualVerdict]) -> List[ClassActionRuling]:
        convicted = [v for v in verdicts if v.status == VerdictStatus.CONVICTED]
        if not convicted:
            return []

        # Group convicted verdicts by incident type
        groups: Dict[IncidentType, List[IndividualVerdict]] = {}
        for v in convicted:
            groups.setdefault(v.incident_type, []).append(v)

        rulings: List[ClassActionRuling] = []
        counter = 1

        for inc_type, v_list in groups.items():
            sessions = list({v.session_id for v in v_list})
            occurrences = len(v_list)

            if inc_type == IncidentType.TOOL_LOOP:
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="Serial Tool Loop & Unchecked Polling Cadence",
                        severity=SeverityLevel.CRITICAL,
                        category=RootCauseCategory.CAT_B_TOOL_DEFECT,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=f"Detected {occurrences} instances of unvaried sequential tool calls across {len(sessions)} sessions.",
                        constitutional_remedy=(
                            "+ ### Zero-Polling & Anti-Loop Protocol:\n"
                            "+ Agents MUST NOT invoke the same tool with identical or failing parameters consecutively.\n"
                            "+ After two consecutive identical executions without progress, agent MUST yield turn or alter strategy."
                        ),
                        target_rule_file="AGENTS.md",
                    )
                )
                counter += 1

            elif inc_type == IncidentType.USER_FRICTION:
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="User Correction Interruption & Prompt Drift",
                        severity=SeverityLevel.HIGH,
                        category=RootCauseCategory.CAT_A_RULE_AMBIGUITY,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=f"Human developer intervened with explicit corrective friction in {len(sessions)} sessions ({occurrences} times).",
                        constitutional_remedy=(
                            "+ ### Intent Verification Gate:\n"
                            "+ When executing architectural or destructive modifications, provide a succinct preview.\n"
                            "+ If requirements are ambiguous, clarify before executing speculative tool sequences."
                        ),
                        target_rule_file="AGENTS.md",
                    )
                )
                counter += 1

            elif inc_type == IncidentType.TOOL_FAILURE:
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="Repeated Tool Execution Exceptions Without Fallback",
                        severity=SeverityLevel.HIGH,
                        category=RootCauseCategory.CAT_D_CAPABILITY_GAP,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=f"Encountered {occurrences} unhandled tool command exit errors or crashes.",
                        constitutional_remedy=(
                            "+ ### Tool Resilience & Fallback Handling:\n"
                            "+ Inspect stderr and return codes on every command before proceeding.\n"
                            "+ If a tool fails twice, formulate alternative approach or report exact limitation immediately."
                        ),
                        target_rule_file="AGENTS.md",
                    )
                )
                counter += 1

            elif inc_type == IncidentType.TRAJECTORY_BLOAT:
                rulings.append(
                    ClassActionRuling(
                        case_id=f"CLASS-2026W40-{counter:02d}",
                        title="Unconstrained Trajectory Horizon (Session Bloat)",
                        severity=SeverityLevel.MEDIUM,
                        category=RootCauseCategory.CAT_C_CONTEXT_DRIFT,
                        occurrences=occurrences,
                        sessions_affected=len(sessions),
                        affected_session_ids=sessions,
                        evidence_summary=f"Sessions exceeding 70 steps observed {occurrences} times.",
                        constitutional_remedy=(
                            "+ ### Bounded Turn Horizon:\n"
                            "+ Deconstruct complex multi-phase tasks into checkpoints.\n"
                            "+ Compact working context every 30 steps to prevent hallucination and instruction wash-out."
                        ),
                        target_rule_file="AGENTS.md",
                    )
                )
                counter += 1

        return rulings
