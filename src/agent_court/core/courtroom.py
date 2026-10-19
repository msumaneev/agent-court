"""
Adversarial Courtroom Engine (Stage 2).
Simulates Prosecutor, Defense Counsel, and Judge to adjudicate suspect incidents.
Supports both deterministic zero-token heuristic judge and LLM judge.
"""

from __future__ import annotations

import re
from typing import List, Optional
from agent_court.core.models import (
    DefensePlea,
    DocketItem,
    IncidentType,
    IndividualVerdict,
    TrialAccusation,
    TrialDefense,
    VerdictStatus,
)


class Courtroom:
    """
    Adjudicates DocketItems using adversarial simulation.
    """

    def __init__(self, offline: bool = True):
        self.offline = offline

    def adjudicate_docket(self, docket: DocketItem) -> IndividualVerdict:
        """
        Adjudicates a single DocketItem.
        In offline mode, executes deterministic heuristic courtroom simulation.
        """
        user_prompt_lower = (docket.initiating_prompt or "").lower()
        trigger_lower = docket.trigger_marker.lower()

        # 1. Prosecutor Formulation
        if docket.incident_type == IncidentType.TOOL_FAILURE:
            charge = f"Tool failure encountered without immediate prevention: {docket.trigger_marker[:100]}"
            violation_rule = "Standard Reliability Protocol: Agent must anticipate and handle tool execution boundaries."
            evidence = f"Step {docket.incident_step_index}: Encountered {docket.trigger_marker} (repeated {docket.repeat_count}x)."
        elif docket.incident_type == IncidentType.TOOL_LOOP:
            charge = f"Serial unvaried execution loop: repeated tool calls without state change."
            violation_rule = "Zero-Polling & Anti-Loop Protocol: Agent must not repeat identical calls > 2 times without alternative strategy."
            evidence = f"Step {docket.incident_step_index}: Tool loop detected with repeat count {docket.repeat_count}."
        elif docket.incident_type == IncidentType.USER_FRICTION:
            charge = f"User expressed explicit friction/correction during autonomous flow."
            violation_rule = "Alignment & Intent Preservation Rule: Agent actions triggered user intervention."
            evidence = f"User statement: '{docket.trigger_marker}'"
        elif docket.incident_type == IncidentType.TRAJECTORY_BLOAT:
            charge = f"Trajectory bloat: excessively long execution chain without synthesis."
            violation_rule = "Bounded Horizon Protocol: Complex goals must be partitioned into verifiable subgoals."
            evidence = f"Trajectory reached {docket.metadata.get('total_steps', 'many')} steps."
        else:
            charge = f"Suspected anomaly: {docket.trigger_marker[:100]}"
            violation_rule = "Operational Integrity Contract"
            evidence = f"Step {docket.incident_step_index}: Trigger marker matched."

        accusation = TrialAccusation(
            charge=charge,
            violation_rule=violation_rule,
            evidence=evidence,
        )

        # 2. Defense Counsel Analysis
        # Check if the user explicitly ordered or authorized the action/command
        user_directed = False
        direct_keywords = ["запусти", "проверь", "попробуй", "выполни", "run", "check", "test", "install", "поищи", "найди", "search", "скачай"]
        for kw in direct_keywords:
            if kw in user_prompt_lower:
                user_directed = True
                break

        # Check if the tool failure was due to external environment/timeout/MCP context deadline
        is_env_error = any(
            err in trigger_lower
            for err in ["context deadline exceeded", "timed out", "connectionrefused", "not found", "commandnotfound", "mcp tool call"]
        )

        # Check if agent recovered in adjacent context
        recovered = False
        for s in docket.steps_context:
            if s.step_index > docket.incident_step_index and s.status == "DONE" and s.content:
                recovered = True
                break

        if is_env_error:
            defense = TrialDefense(
                plea=DefensePlea.ENVIRONMENT_EXCEPTION,
                argument="The failure was caused by external environmental conditions (e.g. MCP timeout or network deadline), not flawed agent logic.",
                supporting_evidence=f"Trigger marker confirms environmental condition: {docket.trigger_marker[:90]}",
            )
        elif user_directed and docket.incident_type != IncidentType.USER_FRICTION:
            defense = TrialDefense(
                plea=DefensePlea.USER_DIRECT_COMMAND,
                argument="The preceding human prompt explicitly instructed the agent to perform or test this operation.",
                supporting_evidence=f"Initiating user instruction: '{docket.initiating_prompt[:120]}...'",
            )
        elif recovered:
            defense = TrialDefense(
                plea=DefensePlea.LEGITIMATE_RECOVERY,
                argument="The agent encountered an obstacle but successfully adapted and completed subsequent execution steps.",
                supporting_evidence="Subsequent context steps executed with DONE status and provided valid output.",
            )
        else:
            defense = TrialDefense(
                plea=DefensePlea.FALSE_ALARM_HEURISTIC,
                argument="The agent was exploring necessary diagnostic paths within permitted workspace autonomy.",
                supporting_evidence="No malicious intent; incident occurred during normal exploration.",
            )

        # 3. Judge's Verdict
        # Rules for acquittal:
        # - Environment exception where agent handled or tried gracefully -> ACQUITTED
        # - User direct command -> ACQUITTED (User directive supercedes default restriction)
        # - Legitimate recovery with repeat_count <= 2 -> ACQUITTED
        # Rules for conviction:
        # - Repeat count >= 3 on failures/loops without resolution -> CONVICTED
        # - Direct user friction where user had to intervene with "стоп/не то/ошибка" -> CONVICTED
        # - Trajectory bloat > 70 steps without convergence -> CONVICTED

        if docket.incident_type == IncidentType.USER_FRICTION:
            status = VerdictStatus.CONVICTED
            confidence = 0.94
            rationale = "CONVICTED: Explicit human intervention was required due to drifted trajectory or erroneous assumptions."
            recommended_action = "Refine prompt parsing and confirm intent before initiating complex multi-step commands."

        elif docket.incident_type == IncidentType.TOOL_LOOP and docket.repeat_count >= 2:
            status = VerdictStatus.CONVICTED
            confidence = 0.92
            rationale = f"CONVICTED: Agent entered a repetitive invocation loop ({docket.repeat_count} cycles) without adapting its parameter space or strategy."
            recommended_action = "Implement circuit-breaker in agent rules: halt identical tool executions after 2 consecutive attempts."

        elif is_env_error and docket.repeat_count == 1:
            status = VerdictStatus.ACQUITTED
            confidence = 0.95
            rationale = "ACQUITTED: External timeout or MCP context deadline was outside agent's deterministic control; agent handled the fault without runaway cascade."
            recommended_action = None

        elif user_directed and docket.repeat_count <= 2:
            status = VerdictStatus.ACQUITTED
            confidence = 0.96
            rationale = "ACQUITTED: Human developer explicitly sanctioned the command in preceding turns (USER_DIRECT_COMMAND supercedes default gate)."
            recommended_action = None

        elif recovered and docket.repeat_count <= 2:
            status = VerdictStatus.ACQUITTED
            confidence = 0.88
            rationale = "ACQUITTED: First attempt encountered an error, but agent demonstrated legitimate adaptive self-correction in subsequent steps."
            recommended_action = None

        elif docket.repeat_count >= 3:
            status = VerdictStatus.CONVICTED
            confidence = 0.91
            rationale = f"CONVICTED: Unresolved repetitive failure ({docket.repeat_count} recurrences). Agent failed to alter strategy despite repeated negative outcomes."
            recommended_action = "Enforce hard error budget: terminate repetitive tool executions after second failure."

        elif docket.incident_type == IncidentType.TRAJECTORY_BLOAT:
            status = VerdictStatus.CONVICTED
            confidence = 0.86
            rationale = "CONVICTED: Excessive step volume without intermediate checkpoints degrades context fidelity and token economics."
            recommended_action = "Add intermediate checkpointing and decomposition guidelines into agent prompt constitution."

        else:
            # Default mild acquittal for exploratory steps
            status = VerdictStatus.ACQUITTED
            confidence = 0.82
            rationale = "ACQUITTED: Isolated anomaly during legitimate exploratory phase; no systemic failure detected."
            recommended_action = None

        return IndividualVerdict(
            docket_id=docket.docket_id,
            session_id=docket.session_id,
            step_index=docket.incident_step_index,
            incident_type=docket.incident_type,
            status=status,
            confidence=confidence,
            accusation=accusation,
            defense=defense,
            judge_rationale=rationale,
            recommended_action=recommended_action,
            recovery_evidence=docket.recovery_evidence,
        )

    def adjudicate_all(self, dockets: List[DocketItem]) -> List[IndividualVerdict]:
        return [self.adjudicate_docket(d) for d in dockets]
