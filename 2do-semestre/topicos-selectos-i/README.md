# Tópicos Selectos de Grandes Bases de Datos I
**Semester:** 2nd | **Department:** DSI | **Credits:** 7

In practice, the course covered two independent blocks: (1) AI agent design and behavioral analysis, and (2) decision theory under uncertainty applied to agricultural investment.

## Activities (`tareas/actividades/`)

### Block 1 — AI Agents and Decision Making
| # | Activity | Score | Status |
|---|----------|-------|--------|
| 1 | Diagnostic exam | 100/100 | ✅ Done |
| 2 | Design an AI agent — Drow Battle Master Warrior (identity, traits, morals) | 75/100 | ✅ Done |
| 3 | Coherence and decision evaluation — predict vs. execute vs. analyze (Strahd scenario) | 100/100 | ✅ Done |
| 4 | Agent inventory — weapons, wealth, persistent state | 100/100 | ✅ Done |
| 5 | Agent self-perception — agent describes itself according to its parameters | 100/100 | ✅ Done |

### Block 2 — Decision Theory Under Uncertainty
| # | Activity | Score | Status |
|---|----------|-------|--------|
| 6 | Decision tree + Monte Carlo simulation — irrigation investment for sugar cane producer, Pánuco | 100/100 | ✅ Done |
| 7 | Viability conditions for irrigation investment — seller's perspective, 5-slide pitch | — | ✅ Done |

## Key Results — Activity 6 & 7

| Metric | Temporal (no irrigation) | Irrigation — full price | Irrigation — 30% discount |
|--------|--------------------------|------------------------|---------------------------|
| Expected yield (ton/ha/year) | 47.0 | 88.7 | 88.7 |
| Expected annual utility | −$4,902 MXN | +$860,851 MXN | +$860,851 MXN |
| Net cumulative utility (7 years) | −$34,316 MXN | −$1,974,042 MXN | **+$425,958 MXN** |
| Breakeven horizon | — | 9.2 years | **6.5 years** |
| Price of indifference (7 years) | — | $873.48 MXN/ton | **$791.27 MXN/ton** |
| P(irrigation > temporal) — Monte Carlo | — | 35.3% | 44.5% |

## Glossary

### AI Agents
| Term | Definition |
|------|------------|
| **AI Agent** | Autonomous system with defined identity, internal rules, and capacity to make decisions in context |
| **Persistent state** | Agent memory (inventory, attributes, history) that survives between interactions |
| **Alignment** | Degree to which an agent's actual behavior matches the values and intentions of its designer |
| **Coherence** | Consistency between an agent's identity/values and its real decisions when facing ambiguous input |
| **Explainable reasoning** | Ability to justify a decision in terms of the agent's own identity, context, and evidence |
| **Prediction vs. result** | Core evaluation framework: what you expected the agent to do vs. what it actually did — analogous to model error analysis |

### Decision Theory
| Term | Definition |
|------|------------|
| **Decision tree** | Graphical model that maps choices, probabilistic events, and their outcomes to support structured decision-making |
| **Expected utility** | Probability-weighted average of outcomes across all scenarios; the standard criterion for decisions under uncertainty |
| **Monte Carlo simulation** | Method of estimating a distribution by running thousands of random scenarios independently |
| **Price of indifference** | The price level at which two alternatives produce equal cumulative utility; below it one wins, above it the other |
| **Breakeven horizon** | Number of years required for an investment's cumulative utility to equal the next-best alternative |
| **Loss aversion** | Psychological bias where losses are weighted more heavily than equivalent gains — used in Act. 7 sales framing |
| **Asymmetric distribution** | When the mean of an outcome differs significantly from its median due to rare but extreme events (e.g., 200 ton/ha years pulling riego's mean up despite fewer winning scenarios) |

## Tools
Python 3.13 · NumPy · python-docx · LibreOffice headless · Jupyter · conda env `MCD`
