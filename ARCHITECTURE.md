# AgentCourt (`agent-court`): Architecture & Implementation Blueprint

**Author:** Mikhail Sumaneev  
**Project:** Universal Adversarial Trajectory Auditor & Constitutional Patch Engine  

---

## 1. System Architecture & Component Interactions

```mermaid
graph TD
    subgraph "Phase 0: Multi-Agent Ingestion (Adapters)"
        AG["Antigravity<br/>(transcript.jsonl)"] --> UNIFY
        CC["Claude Code<br/>(history / json)"] --> UNIFY
        CR["Cursor / Windsurf<br/>(composer state)"] --> UNIFY
        CL["Cline / Roo Code<br/>(task JSONs)"] --> UNIFY
        OH["OpenHands<br/>(event stream)"] --> UNIFY
        UNIFY["Canonical Trajectory Ingestion<br/>(agent_court.adapters)"]
    end

    subgraph "Phase 1: Deterministic Fast Miner (0 Tokens)"
        UNIFY --> STREAM["Streaming Log Parser<br/>(O(1) memory per step)"]
        STREAM --> HEUR["Deterministic Anomaly Detectors<br/>• User Friction Stopwords<br/>• Unhandled Error Cascades<br/>• Tool Call Loops (3+ reps)<br/>• Boundary / Rule Breaches<br/>• Trajectory Bloat"]
        HEUR --> DOCKET["Docket Deduplication Filter<br/>(Collapse 20 serial tool clicks → 1 Case)"]
        DOCKET --> DOSSIER["Context Window Builder<br/>[±2 Steps + Initiating Human Prompt]"]
    end

    subgraph "Phase 2: Adversarial Courtroom Hearing"
        DOSSIER --> TRIAL{"Hearing Mode"}
        TRIAL -->|"LLM Available"| LLM_COURT["Single-Prompt Adversarial Debate"]
        TRIAL -->|"Offline / 0 Tokens"| HEUR_COURT["Deterministic Heuristic Judge<br/>(100% Cron Reliability)"]
        
        LLM_COURT --> ADV["🏛️ Prosecutor: Rule Violation Charges<br/>⚖️ Defense: Human Directives & Env Outages<br/>🧑‍⚖️ Judge: Weighs Precedence & Intent"]
        HEUR_COURT --> ADV
        
        ADV --> VERDICT["Individual Verdicts<br/>• 🟢 ACQUITTED (68.6% False Alarms Cleared)<br/>• 🔴 CONVICTED (Rogue Drifts & Loops)"]
    end

    subgraph "Phase 3: Plenum of the Supreme Court"
        VERDICT -->|"CONVICTED Cases"| PLENUM["Cross-Session Root Cause Clustering"]
        PLENUM --> CAT["Root Cause Quadrants:<br/>A: Rule Ambiguity | B: Tool Defect<br/>C: Context Drift  | D: Capability Gap"]
        CAT --> CLASS["Consolidated Class Action Rulings<br/>(Cross-Session Evidence Synthesis)"]
    end

    subgraph "Phase 4: Constitutional Patch & Reporting"
        CLASS --> PATCHER["Constitutional Patch Engine<br/>Auto-revises .cursorrules / CLAUDE.md / AGENTS.md"]
        CLASS --> REPORTERS["Reporters:<br/>• Rich CLI Gavel View<br/>• Portable Outlook/Email HTML<br/>• Markdown CI Summaries<br/>• GitHub Action PR Bot"]
    end
```

---

## 2. Core Modules Specification (`agent_court.core`)

### `agent_court.core.models`
Defines canonical typing and schema contracts using Pydantic v2 / dataclasses:
- `IncidentType`: `USER_FRICTION`, `TOOL_LOOP`, `TOOL_FAILURE`, `RULE_BREACH`, `TRAJECTORY_BLOAT`, `HALLUCINATION`.
- `SeverityLevel`: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- `DefensePlea`: `USER_DIRECT_COMMAND`, `ENVIRONMENT_EXCEPTION`, `LEGITIMATE_RECOVERY`, `FALSE_ALARM_HEURISTIC`.
- `VerdictStatus`: `ACQUITTED`, `CONVICTED`, `MISTRIAL`.
- `StepEvent`: Canonical representation of one execution step (`step_index`, `role`, `content`, `thinking`, `tool_calls`, `created_at`, `source_line`).
- `DocketItem`: Deduplicated incident cluster containing the 5-step localized dossier (`steps_context`), `repeat_count`, `trigger_marker`, and session metadata.
- `IndividualVerdict`: First-instance judgment with complete trial records: `TrialAccusation` (Prosecutor), `TrialDefense` (Defense Counsel), and `judge_rationale` (Judge).
- `ClassActionRuling`: Aggregated Supreme Court precedent consolidating convicted verdicts across all sessions with empirical cross-validation and prescribed patches.
- `AuditReport`: Global container computing:
  $$\text{Raw Friction Index} = \frac{\text{Raw Incidents}}{\\text{Total Steps}} \times 100$$
  $$\text{Filtering Efficiency} = \frac{\text{Acquitted Counts}}{\text{Raw Incidents}} \times 100$$
  $$\text{True Friction Index} = \frac{\text{Convicted Counts}}{\text{Total Steps}} \times 100$$

### `agent_court.core.miner`
- **Streaming Parser**: Line-by-line JSONL reader with bounded memory usage, handling files up to gigabytes in seconds.
- **Context Window Builder**: Extracts a localized 5-step slice ($i-2 \le k \le i+2$) combined with a backwards search (up to 25 turns) to locate the earliest relevant human prompt that initiated the current autonomous phase.

### `agent_court.core.docket_filter`
- **Serial Compression**: When an agent gets caught in a retry loop (e.g. calling `view_file` or `run_command` 15 times consecutively), raw monitoring triggers 15 alerts. The `docket_filter` hashes normalized trigger signatures:
  `Key = (session_id, trigger_category, incident_type)`
  This collapses 15 raw events into **1 Docket Item with `repeat_count=15`**, preserving context density.

### `agent_court.core.courtroom`
- **Adversarial Triad**: Executes single-prompt structured arbitration using OpenAI, Anthropic, or local Ollama endpoints:
  - *The Prosecutor*: Checks action against the loaded constitutional files (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`).
  - *The Defense Counsel*: Analyzes preceding human prompts for explicit directives (*"Check this file"*, *"Investigate logs"*, *"Run tests"*).
  - *The Judge*: Issues ruling with confidence rating ($0.0 \dots 1.0$) and formal justification.
- **Deterministic Heuristic Judge (Offline Fallback)**: Built-in deterministic regex and intent analyzer. If no API key is provided, the trial runs offline in 0 tokens with zero network dependency.

### `agent_court.core.plenum`
- Consolidates all `CONVICTED` individual verdicts into high-level Class Actions.
- Maps failure signatures to 4 architectural root causes:
  - `CAT_A_RULE_AMBIGUITY`: Missing or contradictory agent rules.
  - `CAT_B_TOOL_DEFECT`: Tool crash, API parameter mismatch, or network timeout.
  - `CAT_C_CONTEXT_DRIFT`: Excessive session length (>30 steps) causing prompt washed-out.
  - `CAT_D_CAPABILITY_GAP`: Agent lacks appropriate tools, resorting to crude shell hacks.

### `agent_court.core.patcher` (Constitutional Patch Engine)
- Parses target rule files (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`).
- Implements AST-safe / Markdown-section insertions.
- Inserts surgical guard clauses with comment metadata:
  ```markdown
  <!-- [AgentCourt Precedent CLASS-2026W40-01] Applied 2026-10-07 -->
  ### Hard Gate: Attachment Inspection Isolation
  Parent dispatcher must never call view_file on attachments/ or screens/.
  Delegate file analysis strictly to background subagents.
  <!-- [/AgentCourt Precedent] -->
  ```

---

## 3. Pluggable Adapters (`agent_court.adapters`)

| Adapter | Source Path / Environment | Key Ingestion Strategy |
| :--- | :--- | :--- |
| **`AntigravityAdapter`** | `~/.gemini/antigravity/brain/<id>/.../transcript.jsonl` | Stream JSONL parser, extracts thoughts, steps, and tool calls. |
| **`ClaudeCodeAdapter`** | `~/.claude/projects/...` or JSON CLI exports | Maps Claude Code tool executions and bash turns into canonical steps. |
| **`CursorAdapter`** | Cursor workspace storage / `composer.json` | Extracts user requests, AI diff suggestions, and terminal runs. |
| **`ClineAdapter`** | VSCode global storage `saoudrizwan.claude-dev/tasks/*.json` | Reconstructs step history, user feedback, and tool results. |
| **`OpenHandsAdapter`** | OpenHands conversation `events.jsonl` | Normalizes action/observation event streams into canonical steps. |
| **`GenericJsonlAdapter`** | User-specified JSONL/JSON path | Accepts standard schema for LangGraph, AutoGen, CrewAI, and custom agents. |

---

## 4. Empirical Validation Benchmark

Battle-tested on **55,680 production agent steps across 184 enterprise sessions** (and 54,374 steps / 203 sessions in v0.3.0):
* **Runtime:** 7.8 seconds on standard commodity CPU.
* **Tokens Spent in Phase 1:** Exactly 0 LLM tokens.
* **Raw Heuristic Triggers:** 283 suspect incidents (582 in v0.3.0 extended run).
* **Acquittals by Defense Counsel:** 194 cases / 68.6% noise reduction (301 cases / 51.7% in v0.3.0).
* **In-Session Contrastive Recoveries Extracted:** 10 real self-recovery trajectories mined at 0 token cost.
* **Supreme Court Class Actions:** Exactly 4 consolidated rulings with `Cue → Lesson → Evidence` Triads and `SurfaceSpec` routing.
* **True Friction Index:** Reduced from 0.48% (raw) to **0.16%** (net).

---

## 5. v0.3.0 Architectural Upgrades: Recursive Harnessing (`Harness²` Integration)

Inspired by Google Cloud AI Research & Northwestern University's [***Harness²: Recursive Agent Harnessing for an Open World*** (`arXiv:2610.14224`)](https://github.com/google-research/harness2) (Xu et al., 2026), `AgentCourt v0.3.0` incorporates three core mechanisms adapted for zero-token offline trajectory auditing:

### 5.1. Zero-Token In-Session Contrastive Recovery (`_extract_recovery_evidence`)
Instead of spawning expensive online candidate rollouts ($N$ parallel runs) to obtain a `Pass vs. Fail` contrast, `FastMiner._extract_recovery_evidence` scans forward up to $K=12$ steps within the *same* session trajectory after an error or loop trigger. If the agent switches tool or argument signature and achieves `status == "DONE"`, the miner records the exact contrastive transition:
`Failed on <ToolA> -> Recovered at step #M via <ToolB(args)>`.

### 5.2. Structured `ExperienceTriad` (`Cue → Lesson → Evidence`)
Every `ClassActionRuling` synthesized by `SupremePlenum` includes a validated `ExperienceTriad`:
- **`cue` (*When*):** Exact environmental or tool-call precondition that should trigger the rule in the agent's attention.
- **`lesson` (*What*):** Concrete imperative action or fallback strategy.
- **`evidence` (*Why*):** Empirical cross-session occurrence telemetry + extracted in-session contrastive recoveries.

### 5.3. `SurfaceSpec` Layer Routing & Instruction Entropy Cap (`16 KB`)
To prevent **Instruction Entropy** (rule bloat in root `AGENTS.md` / `CLAUDE.md` that washes out LLM attention), `check_surface_entropy_budget()` measures the byte size of Always-On instruction files against a `16 KB` (`16,384` bytes) ceiling:
- **`INVARIANT` Scope:** Only critical global invariants enter `AGENTS.md` when the budget is healthy ($< 85\%$).
- **`DOMAIN` Scope:** Specialized tool resilience, anti-loop, and horizon rules—or any ruling generated when `AGENTS.md` exceeds $85\%$ of its `16 KB` cap—are automatically routed to modular on-demand files (`rules/anti-loop.md`, `rules/intent-gate.md`, `rules/tool-resilience.md`, `rules/context-horizon.md`).

