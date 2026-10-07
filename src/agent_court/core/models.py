"""
Canonical data models and schemas for AgentCourt.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IncidentType(str, Enum):
    USER_FRICTION = "USER_FRICTION"
    TOOL_LOOP = "TOOL_LOOP"
    TOOL_FAILURE = "TOOL_FAILURE"
    RULE_BREACH = "RULE_BREACH"
    TRAJECTORY_BLOAT = "TRAJECTORY_BLOAT"
    HALLUCINATION = "HALLUCINATION"


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DefensePlea(str, Enum):
    USER_DIRECT_COMMAND = "USER_DIRECT_COMMAND"
    ENVIRONMENT_EXCEPTION = "ENVIRONMENT_EXCEPTION"
    LEGITIMATE_RECOVERY = "LEGITIMATE_RECOVERY"
    FALSE_ALARM_HEURISTIC = "FALSE_ALARM_HEURISTIC"


class VerdictStatus(str, Enum):
    ACQUITTED = "ACQUITTED"
    CONVICTED = "CONVICTED"
    MISTRIAL = "MISTRIAL"


class RootCauseCategory(str, Enum):
    CAT_A_RULE_AMBIGUITY = "Category A: Rule Ambiguity"
    CAT_B_TOOL_DEFECT = "Category B: Tool Defect / Protocol Violation"
    CAT_C_CONTEXT_DRIFT = "Category C: Context Drift / Trajectory Bloat"
    CAT_D_CAPABILITY_GAP = "Category D: Capability Gap / Fallback Failure"


class StepEvent(BaseModel):
    step_index: int
    source: str = "UNKNOWN"
    type: str = "GENERIC"
    status: str = "DONE"
    content: Optional[str] = None
    thinking: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    created_at: Optional[str] = None


class DocketItem(BaseModel):
    docket_id: str
    session_id: str
    incident_type: IncidentType
    severity: SeverityLevel
    trigger_marker: str
    repeat_count: int = 1
    incident_step_index: int
    initiating_prompt: str
    steps_context: List[StepEvent] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TrialAccusation(BaseModel):
    charge: str
    violation_rule: str
    evidence: str


class TrialDefense(BaseModel):
    plea: DefensePlea
    argument: str
    supporting_evidence: str


class IndividualVerdict(BaseModel):
    docket_id: str
    session_id: str
    step_index: int
    incident_type: IncidentType
    status: VerdictStatus
    confidence: float
    accusation: TrialAccusation
    defense: TrialDefense
    judge_rationale: str
    recommended_action: Optional[str] = None


class ClassActionRuling(BaseModel):
    case_id: str
    title: str
    severity: SeverityLevel
    category: RootCauseCategory
    occurrences: int
    sessions_affected: int
    affected_session_ids: List[str] = Field(default_factory=list)
    evidence_summary: str
    constitutional_remedy: str
    target_rule_file: str = "AGENTS.md"


class AuditReport(BaseModel):
    period_days: int
    start_date: str
    end_date: str
    total_sessions: int
    total_steps: int
    raw_incidents: int
    acquitted_count: int
    convicted_count: int
    raw_friction_index: float
    filtering_efficiency: float
    true_friction_index: float
    verdicts: List[IndividualVerdict] = Field(default_factory=list)
    class_actions: List[ClassActionRuling] = Field(default_factory=list)
