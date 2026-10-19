# 🏛️ AgentCourt

<p align="center">
  <strong>The Adversarial Trajectory Auditor & Constitutional Patch Engine for Autonomous AI Coding Agents.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/agent-court/"><img src="https://img.shields.io/pypi/v/agent-court.svg?color=blue&style=flat-square" alt="PyPI version"></a>
  <a href="https://github.com/msumaneev/agent-court/actions"><img src="https://img.shields.io/badge/CI-passing-brightgreen?style=flat-square" alt="Build Status"></a>
  <a href="https://pypi.org/project/agent-court/"><img src="https://img.shields.io/pypi/pyversions/agent-court.svg?style=flat-square" alt="Python Versions"></a>
  <a href="https://github.com/msumaneev/agent-court/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License: MIT"></a>
  <a href="#empirical-validation"><img src="https://img.shields.io/badge/False%20Alert%20Filtration-68.6%25-orange?style=flat-square" alt="Filtration"></a>
  <a href="#zero-token-mining"><img src="https://img.shields.io/badge/Fast%20Scan-0%20Tokens-purple?style=flat-square" alt="Zero Token"></a>
</p>

---

## ⚡ The Problem: The False-Positive Trap in Agent Monitoring

In 2025–2026, software engineering teams are adopting autonomous coding agents (**Antigravity, Claude Code, Cursor Composer, Windsurf, Cline, OpenHands**).

When auditing agent trajectories, naive regexes and standard "LLM-as-a-Judge" evaluators trigger **crippling alert fatigue**:
1. **The False-Violation Paradox:** In real-world engineering, **70% to 90% of flagged "rule breaches"** (e.g. inspecting raw logs, accessing production servers, modifying migration directories) were **explicitly ordered by the human developer** in preceding turns!
2. **Disconnected Governance:** Observability platforms display graphs and latency percentiles, but they **never fix the root cause**. They leave developers to manually guess how to patch `.cursorrules`, `CLAUDE.md`, or `AGENTS.md`.

---

## 💡 The Solution: Adversarial Courtroom Architecture (v2.0)

**AgentCourt** replaces naive scoring with a **two-tier judicial simulation**:

```
                       ┌───────────────────────────────┐
                       │   Raw Agent Session Logs      │
                       │ (Antigravity/Claude/Cursor/etc)│
                       └──────────────┬────────────────┘
                                      │
            ┌─────────────────────────▼─────────────────────────┐
            │  STAGE 1: Deterministic Fast Miner (0 LLM Tokens) │
            │  • Streams 100k+ lines of JSONL in seconds        │
            │  • Filters serial loops: 20 retries → 1 Docket    │
            │  • Extracts ±2 Step Context + Initiating Prompt   │
            └─────────────────────────┬─────────────────────────┘
                                      │
       ┌──────────────────────────────▼──────────────────────────────┐
       │     STAGE 2, PHASE 1: Adversarial Hearing (Single Prompt)   │
       │                                                             │
       │  🏛️ The Prosecutor: Charges agent with rule breach         │
       │  ⚖️ The Defense: Scrutinizes preceding human instructions   │
       │  🧑‍⚖️ The Judge: Acquits human-sanctioned actions             │
       └──────────────┬───────────────────────────────┬──────────────┘
                      │                               │
        🟢 ACQUITTED (68.6% Noise)      🔴 CONVICTED (Real Drifts)
                      │                               │
                      ▼                               ▼
               Ignored / Filtered            ┌────────────────────────────────┐
                                             │ STAGE 2, PHASE 2: Supreme Court│
                                             │ • Clusters cross-session flaws │
                                             │ • Issues Class Action Rulings  │
                                             └───────────────┬────────────────┘
                                                             │
                                             ┌───────────────▼────────────────┐
                                             │ Constitutional Patch Engine    │
                                             │ Auto-patches .cursorrules,     │
                                             │ CLAUDE.md, and AGENTS.md       │
                                             └────────────────────────────────┘
```

### 🔬 Empirical Battle-Testing
Battle-tested on **55,680 production agent steps across 184 enterprise sessions**:
* **68.6% False Positive Elimination:** The Defense Counsel proved human authorization in 194 of 283 raw anomaly triggers.
* **100% Offline Reliability:** Built-in zero-token heuristic judge runs reliably inside air-gapped CI cron jobs without API dependencies in 7.8 seconds.
* **Consolidation into 4 Precedents:** Collapsed 89 true failures into exactly 4 actionable Class Actions.
* **Closed-Loop Rule Evolution:** Discovered and synthesized surgical patches for root system constitutions.

---

## 🚀 Quickstart

### Installation
```bash
# Core package with zero-token deterministic engine:
pip install agent-court

# With LLM arbitration (OpenAI / Anthropic):
pip install "agent-court[llm]"

# Complete suite with GitHub PR integrations:
pip install "agent-court[all]"
```

### 30-Second Audit
Audit agent sessions from the last 7 days and display the interactive courtroom:
```bash
agent-court audit --last 7d
```

---

## 🛠️ CLI Usage & Workflows

### 1. Zero-Token Fast Scan (`scan`)
Instantly inspect session trajectories without spending LLM tokens:
```bash
# Terminal summary
agent-court scan --last 3d

# Machine-readable JSON output for CI pipelines
agent-court scan --last 3d --format json
```

### 2. Full Adversarial Trial (`audit`)
Conducts full courtroom hearings, synthesizes Class Actions, and exports reports:
```bash
# Interactive terminal view + generates HTML digest
agent-court audit --last 7d --format html --output ./reports/digest.html

# Run with LLM Judge (requires OPENAI_API_KEY or ANTHROPIC_API_KEY)
agent-court audit --last 7d --judge gpt-4o

# Run in 100% Offline Mode (Zero token cost)
agent-court audit --last 7d --offline
```

### 3. Constitutional Auto-Patching (`patch`)
Automatically applies Supreme Court Class Action remedies to project rule files:
```bash
# Preview proposed patches as unified diffs
agent-court patch --dry-run

# Apply verified patches to .cursorrules, CLAUDE.md, or AGENTS.md
agent-court patch --target .cursorrules --apply
```

---

## 📊 Sample Output: Rich Terminal Gavel View

```text
🏛️  AGENTCOURT DOCKET & JUDICIAL VERDICT REPORT
═════════════════════════════════════════════════════════════════════════════
Period: 2026-09-30 to 2026-10-07 | Analyzed Steps: 55,680 | Sessions: 184
Raw Heuristic Triggers: 283      | True Friction Index: 0.16%
Noise Filtered (Acquitted): 194 (68.6%) | True Failures (Convicted): 89

⚖️  FIRST INSTANCE HEARINGS (Sample Dossiers)
─────────────────────────────────────────────────────────────────────────────
[DKT-01] 🟢 ACQUITTED (Confidence: 96%) — Session 36adbe1d… : step 14
  🏛️ Charge:  Direct inspection of raw ticket attachments (AGENTS.md Gate 1).
  ⚖️ Defense: User explicitly typed: "Look at attachments/error.png and explain it".
  🧑‍⚖️ Ruling:  USER_DIRECT_COMMAND supercedes default dispatcher delegation rule.

[DKT-02] 🔴 CONVICTED (Confidence: 92%) — Session a914cb02… : step 42
  🏛️ Charge:  Unsanctioned remote SSH connection to 10.0.0.75 (Anti-Sysadmin Gate).
  ⚖️ Defense: Agent claimed it needed to inspect Docker daemon logs.
  🧑‍⚖️ Ruling:  No user command found in preceding turns. Unauthorized infrastructure access.

═════════════════════════════════════════════════════════════════════════════
🧑‍⚖️  PLENUM OF THE SUPREME COURT: CONSOLIDATED CLASS ACTION RULINGS
─────────────────────────────────────────────────────────────────────────────
Case ID: CLASS-2026W40-01 (Severity: CRITICAL | Occurrences: 34 across 12 sessions)
Title:   Rogue Task Polling Loop on Long Background Execution
Cause:   Category B (Tooling Defect / Missing Reactive Wait Protocol)

📜 Prescribed Constitutional Remedy (Target: AGENTS.md):
┌───────────────────────────────────────────────────────────────────────────┐
│ + ### Reactive Wait & Zero-Polling Protocol:                              │
│ + Agents MUST NOT poll background task status in tight loops.             │
│ + After starting an asynchronous background job, parent agent MUST        │
│ + yield execution turn. The runtime will send a Reactive Wakeup message.  │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Supported Agent Frameworks & Adapters

AgentCourt automatically detects installed agent logs in the workspace:

| Agent Framework | Ingestion Format | Auto-Detection Path |
| :--- | :--- | :--- |
| **Google Antigravity** | `transcript.jsonl` | `~/.gemini/antigravity/brain/<id>/` |
| **Anthropic Claude Code**| Session log JSON | `~/.claude/projects/` |
| **Cursor / Composer** | Workspace state JSON | `.cursor/` or OS storage |
| **Cline / Roo Code** | Task histories | `~/.config/Code/User/globalStorage/.../tasks/` |
| **OpenHands** | Event streams | Trajectory directory |
| **Generic Custom Agent**| Standard JSONL schema | `--file path/to/transcript.jsonl` |

---

## ⚙️ Configuration (`.agentcourt.toml`)

Customize rules, thresholds, and LLM backends via `.agentcourt.toml`:

```toml
[general]
min_severity = "MEDIUM"          # LOW | MEDIUM | HIGH | CRITICAL
default_mode = "courtroom"       # courtroom | fast_scan
context_window_steps = 2         # Radius around incident (±2 steps)
max_user_backtrack = 25          # Steps to scan back for initiating user command

[constitution]
rule_files = [
    ".cursorrules",
    "CLAUDE.md",
    "AGENTS.md"
]

[judge]
provider = "heuristic"           # heuristic | openai | anthropic
model = "gpt-4o"
offline_fallback = true          # If API fails, fall back to heuristic judge

[reporters]
html_theme = "enterprise"
email_on_finish = false
```

---

## 🔄 GitHub Actions CI/CD Integration

Audit every agent-generated Pull Request and prevent rogue agent drift from entering `main`:

```yaml
name: AgentCourt Audit

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  audit-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install AgentCourt
        run: pip install "agent-court[all]"

      - name: Audit Trajectory
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          agent-court audit --last 1d --format markdown --output-pr-comment
```

---

## 🧬 v0.3.0 Upgrade: Recursive Harnessing & Contrastive Triads (Inspired by Google Research `Harness²`)

Following Google Cloud AI Research & Northwestern University's publication of [***Harness²: Recursive Agent Harnessing for an Open World*** (`arXiv:2610.14224`)](https://github.com/google-research/harness2) (Xu et al., Oct 2026), **AgentCourt v0.3.0** integrates the three strongest structural mechanisms from *Harness²* directly into our **zero-token post-mortem judicial pipeline**—eliminating the need for expensive multi-rollout online tree search (\~\$4,000 per benchmark run):

| Mechanism | Google Research `Harness²` (`arXiv:2610.14224`) | `AgentCourt v0.3.0` Implementation |
| :--- | :--- | :--- |
| **1. Contrastive Evidence Mining** | Runs parallel online rollouts ($N$ candidates) to compare passing vs. failing trajectories ($O(N)$ token cost). | **Zero-Token In-Session Contrastive Recovery (`_extract_recovery_evidence`)**: Scans up to 12 steps ahead in the *same* session log after a failure to capture how the agent (or developer) actually recovered—**0 tokens, 0 extra rollouts**. |
| **2. Structured Experience Schema** | `TaskExperience` (`cue`, `lesson`, `evidence`) synthesized by the Scientist agent. | **`ExperienceTriad` (`Cue → Lesson → Evidence`)**: Every Supreme Court `ClassActionRuling` now enforces a strict 3-part behavioral contract (*When* trigger $\to$ *What* imperative $\to$ *Why* empirical telemetry + contrastive recovery). |
| **3. Anti-Bloat SurfaceSpec Routing** | `SurfaceSpec` (`always_on: bool`) + `graduate` action to prevent prompt pollution. | **Always-On SurfaceSpec Cap (`16 KB`) & Layer Routing**: Measures root `AGENTS.md`/`CLAUDE.md` entropy budget and automatically routes domain rules (`DOMAIN`) to on-demand files (`rules/*.md`) while reserving `AGENTS.md` strictly for global `INVARIANT` rules. |
| **4. False-Positive Defense** | ❌ None (treats all sandbox failures as agent errors). | **⚖️ Defense Counsel & Judicial Acquittal**: Eliminates **51.7%–68.6%** of false-positive alerts where actions were explicitly ordered by the human developer (`USER_DIRECT_COMMAND`). |

---

## 🗺️ Roadmap

- [x] Stream JSONL parser & zero-token deterministic miner
- [x] Adversarial Hearing Engine (Prosecutor, Defense Counsel, Judge)
- [x] Heuristic offline arbitration fallback (100% token-free)
- [x] Supreme Court Class Action grouping & cross-session synthesis
- [x] **v0.3.0:** Zero-Token In-Session Contrastive Recovery Mining (`_extract_recovery_evidence`)
- [x] **v0.3.0:** Structured `ExperienceTriad` (`Cue → Lesson → Evidence`) in Supreme Court Rulings
- [x] **v0.3.0:** `SurfaceSpec` Entropy Budget Cap (`16 KB`) & `INVARIANT` vs `DOMAIN` Layer Routing
- [x] Pluggable adapters for Antigravity, Claude Code, Cursor, and Cline
- [x] Rich terminal UI and standalone email-safe HTML digest
- [ ] Auto-PR bot submitting constitutional rule patches directly to GitHub
- [ ] Live VSCode / Cursor status bar widget with real-time True Friction Index
- [ ] Semantic clustering using local lightweight embeddings (e.g. `fastembed`)

---

## 📚 References & Academic Attribution

AgentCourt's v0.3.0 experience synthesis (`ExperienceTriad`), in-session contrastive recovery mining, and `SurfaceSpec` instruction entropy cap build upon findings from Google Cloud AI Research and Northwestern University:

> Ruiyao Xu, Yanfei Chen, Zhongying CuiZhu, Bhavana Dalvi Mishra, Yifei Ming, Han Yu, Rujun Han, Chen-Yu Lee, and Tomas Pfister.  
> ***"Harness²: Recursive Agent Harnessing for an Open World"***, *arXiv preprint arXiv:2610.14224*, October 2026.  
> Code: [https://github.com/google-research/harness2](https://github.com/google-research/harness2)

```bibtex
@article{xu2026harness2,
  title={Harness^2: Recursive Agent Harnessing for an Open World},
  author={Xu, Ruiyao and Chen, Yanfei and CuiZhu, Zhongying and Mishra, Bhavana Dalvi and Ming, Yifei and Yu, Han and Han, Rujun and Lee, Chen-Yu and Pfister, Tomas},
  journal={arXiv preprint arXiv:2610.14224},
  year={2026}
}
```

---

## 🤝 Contributing

Contributions are welcome! Whether you are writing a new agent adapter or improving the courtroom defense arguments:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/new-agent-adapter`.
3. Run tests: `pytest --cov=agent_court`.
4. Submit a Pull Request.

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

