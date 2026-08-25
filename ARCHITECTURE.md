# CodeScanner: Multi-Agent Refactoring Architecture

Visual diagram: https://claude.ai/code/artifact/eccfb241-a567-4358-8255-8a32b5d25779

CodeScanner doesn't just flag issues — it iterates on the code itself. Multiple agents propose competing fixes, an evaluator picks the best one, a validator confirms it's safe, and the loop repeats until the code hits a target grade.

## The Core Loop

```
Scan code
   → 3 agents each propose a fix independently
   → Evaluation Agent scores and picks the winner
   → Validator Agent checks it's safe to apply
   → Apply
   → Rescan
   → repeat until Grade A
```

## Why 3 Agents, Not 1

Each agent optimizes for a different goal, so they don't compete on the same axis — they compete on philosophy:

| Agent | Strategy | Optimizes for |
|---|---|---|
| **Agent A** | Simplicity First | Smallest, lowest-risk diff |
| **Agent B** | Architecture Focused | Long-term structure, maintainability |
| **Agent C** | Performance Optimized | Speed, resource efficiency |

This gives the evaluator real tradeoffs to score, instead of a single opinion.

## Picking the Winner

The **Evaluation Agent** scores every suggestion on a weighted rubric:

- Risk of errors — **40%**
- Complexity reduction — **30%**
- Code clarity improvement — **20%**
- Implementation time — **10%**

Risk is weighted highest on purpose — a clever but risky fix loses to a boring, safe one.

## The Safety Net

Before anything is applied, the **Validator Agent** independently re-checks the winning suggestion: syntax validity, import availability, logic preservation, and test/performance impact. This decouples "is this a good idea" (evaluation) from "is this safe to run" (validation) — two different failure modes, two different checks.

## Shared Contract

All three strategy agents inherit from a common `RefactoringAgent` base class and speak the same two data shapes:

- `Issue` — a problem found by the scanner (type, location, severity)
- `Suggestion` — a proposed fix (description, changes, complexity reduction, risk level, clarity improvement, estimated time)

Because every agent speaks the same contract, agents are interchangeable — a strategy pattern where each strategy is agent-driven.

## Beyond the Loop: General Agent Framework

Separate from the refactor loop, a general-purpose agent framework runs any agent — concurrently or chained:

- `agent_registry.py` — defines, loads (including custom YAML-defined agents), and executes agents
- `parallel_agent_executor.py` — runs multiple agents concurrently
- `agent_chain_executor.py` — chains agents sequentially, output of one feeds the next
- `agent_finetuner.py` — tuning/calibration logic for agent behavior

Three standalone specialized agents also run on this framework, independent of the refactor loop:

- **SecurityAuditor**
- **PerformanceOptimizer**
- **DocumentationGenerator**

## File Map

```
api/services/
├── agents/
│   ├── refactoring_agent.py       # base class + Issue/Suggestion contracts
│   ├── agent_a_simplicity.py      # Agent A: Simplicity First
│   ├── agent_b_architecture.py    # Agent B: Architecture Focused
│   ├── agent_c_performance.py     # Agent C: Performance Optimized
│   ├── evaluation_agent.py        # scores suggestions, picks winner
│   └── validator_agent.py         # validates before applying
├── specialized_agents.py          # SecurityAuditor, PerformanceOptimizer, DocumentationGenerator
├── agent_registry.py              # agent definitions, loading, execution
├── parallel_agent_executor.py     # concurrent agent execution
├── agent_chain_executor.py        # sequential agent chaining
└── agent_finetuner.py             # agent tuning/calibration
```
