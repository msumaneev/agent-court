"""
Deterministic Fast Miner (Stage 1, 0 LLM Tokens).
Extracts anomalies and constructs localized dossiers with initiating user prompts.
"""

from __future__ import annotations

import re
from typing import List, Optional
from agent_court.core.models import (
    DocketItem,
    IncidentType,
    SeverityLevel,
    StepEvent,
)


class FastMiner:
    """
    Deterministic streaming anomaly detector and dossier builder.
    Runs in 0 tokens with O(1) memory per step.
    """

    # Russian & English user friction stopwords
    USER_FRICTION_PATTERNS = [
        r"\b(не то|не работает|переделай|исправь|хватит|стоп|почему ты|зачем ты|опять|ошибка|сломал|ты забыл)\b",
        r"\b(глупост[ьи]|ерунд[аы]|бред|неправильно|отмени|верни как было|косяк)\b",
        r"\b(wrong|broken|failed|stop|halt|undo|don't do that|you forgot|fix this|error)\b",
    ]

    # Tool error patterns in content or errors
    TOOL_ERROR_PATTERNS = [
        r"Encountered error in step execution",
        r"context deadline exceeded",
        r"timed out after",
        r"Traceback \(most recent call last\)",
        r"CommandNotFoundException",
        r"exit code [1-9]\d*",
        r"exited with code [1-9]\d*",
        r"FileNotFoundError",
        r"PermissionError",
        r"ConnectionRefusedError",
    ]

    def __init__(self, context_radius: int = 2, max_user_backtrack: int = 25):
        self.context_radius = context_radius
        self.max_user_backtrack = max_user_backtrack
        self._compiled_friction = [re.compile(p, re.IGNORECASE) for p in self.USER_FRICTION_PATTERNS]
        self._compiled_errors = [re.compile(p, re.IGNORECASE) for p in self.TOOL_ERROR_PATTERNS]

    def _find_initiating_prompt(self, steps: List[StepEvent], current_index: int) -> str:
        """
        Backtracks up to max_user_backtrack steps to find the preceding human command.
        """
        start = max(0, current_index - self.max_user_backtrack)
        for i in range(current_index, start - 1, -1):
            if i < len(steps):
                s = steps[i]
                if s.source == "USER_EXPLICIT" or s.type == "USER_INPUT":
                    content = s.content or ""
                    # Clean XML tags if present (<USER_REQUEST>...</USER_REQUEST>)
                    match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.DOTALL)
                    if match:
                        return match.group(1).strip()
                    # Fallback to first 300 chars of content
                    return content[:400].strip()

        # If no explicit user prompt in range, look for system task or earliest prompt
        for s in steps[:current_index + 1]:
            if s.source == "USER_EXPLICIT" or s.type == "USER_INPUT":
                return (s.content or "")[:400].strip()

        return "Autonomous agent execution (no direct human prompt found in window)"

    def _get_context_window(self, steps: List[StepEvent], incident_idx: int) -> List[StepEvent]:
        """
        Returns a slice of steps [i - radius, i + radius].
        """
        start = max(0, incident_idx - self.context_radius)
        end = min(len(steps), incident_idx + self.context_radius + 1)
        return steps[start:end]

    def mine_session(self, session_id: str, steps: List[StepEvent]) -> List[DocketItem]:
        """
        Analyzes a single session and extracts raw anomaly candidates.
        """
        candidates: List[DocketItem] = []
        docket_counter = 1

        # 1. Check Trajectory Bloat
        if len(steps) > 70:
            user_prompt = self._find_initiating_prompt(steps, 0)
            candidates.append(
                DocketItem(
                    docket_id=f"DKT-{session_id[:6]}-{docket_counter:02d}",
                    session_id=session_id,
                    incident_type=IncidentType.TRAJECTORY_BLOAT,
                    severity=SeverityLevel.MEDIUM,
                    trigger_marker=f"Session exceeded 70 steps (total: {len(steps)} steps)",
                    incident_step_index=len(steps) - 1,
                    initiating_prompt=user_prompt,
                    steps_context=steps[-5:],
                    metadata={"total_steps": len(steps)},
                )
            )
            docket_counter += 1

        # 2. Sequential step analysis
        consecutive_tool_calls: List[str] = []

        for idx, step in enumerate(steps):
            # A. Check User Friction
            if step.source == "USER_EXPLICIT" or step.type == "USER_INPUT":
                content = step.content or ""
                for pattern in self._compiled_friction:
                    if pattern.search(content):
                        user_prompt = content[:400].strip()
                        candidates.append(
                            DocketItem(
                                docket_id=f"DKT-{session_id[:6]}-{docket_counter:02d}",
                                session_id=session_id,
                                incident_type=IncidentType.USER_FRICTION,
                                severity=SeverityLevel.HIGH,
                                trigger_marker=f"User friction detected: '{content[:120]}...'",
                                incident_step_index=idx,
                                initiating_prompt=user_prompt,
                                steps_context=self._get_context_window(steps, idx),
                                metadata={"friction_snippet": content[:200]},
                            )
                        )
                        docket_counter += 1
                        break

            # B. Check Tool Failures & Error Cascades
            is_error = False
            error_reason = ""
            if step.status == "ERROR" or step.error:
                is_error = True
                error_reason = step.error or "Step marked with ERROR status"
            elif step.content:
                for pattern in self._compiled_errors:
                    match = pattern.search(step.content)
                    if match:
                        is_error = True
                        error_reason = f"Execution error: {match.group(0)}"
                        break

            if is_error:
                user_prompt = self._find_initiating_prompt(steps, idx)
                severity = SeverityLevel.HIGH if "context deadline" in error_reason or "exit code" in error_reason else SeverityLevel.MEDIUM
                candidates.append(
                    DocketItem(
                        docket_id=f"DKT-{session_id[:6]}-{docket_counter:02d}",
                        session_id=session_id,
                        incident_type=IncidentType.TOOL_FAILURE,
                        severity=severity,
                        trigger_marker=error_reason[:150],
                        incident_step_index=idx,
                        initiating_prompt=user_prompt,
                        steps_context=self._get_context_window(steps, idx),
                        metadata={"error_detail": error_reason},
                    )
                )
                docket_counter += 1

            # C. Check Tool Loops
            if step.tool_calls:
                for tc in step.tool_calls:
                    name = tc.get("name", "unknown")
                    consecutive_tool_calls.append(name)
                    if len(consecutive_tool_calls) > 5:
                        consecutive_tool_calls.pop(0)

                    # If last 3 tool calls are identical (e.g. status polling or view_file loop)
                    if len(consecutive_tool_calls) >= 3 and len(set(consecutive_tool_calls[-3:])) == 1:
                        user_prompt = self._find_initiating_prompt(steps, idx)
                        candidates.append(
                            DocketItem(
                                docket_id=f"DKT-{session_id[:6]}-{docket_counter:02d}",
                                session_id=session_id,
                                incident_type=IncidentType.TOOL_LOOP,
                                severity=SeverityLevel.HIGH,
                                trigger_marker=f"Repetitive tool call loop: '{name}' invoked 3+ times sequentially",
                                incident_step_index=idx,
                                initiating_prompt=user_prompt,
                                steps_context=self._get_context_window(steps, idx),
                                metadata={"tool_name": name},
                            )
                        )
                        docket_counter += 1
                        # reset to prevent spamming
                        consecutive_tool_calls.clear()
            else:
                consecutive_tool_calls.clear()

        return candidates
