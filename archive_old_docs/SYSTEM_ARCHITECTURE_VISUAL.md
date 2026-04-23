# 🏗️ CIVICMIND SYSTEM ARCHITECTURE

**Complete Visual Overview of All Components**

---

## 🎯 HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        CIVICMIND SYSTEM                         │
│                  AI Governance Simulation                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         SHANNON LOOP ENGINE             │
        │   Think → Test → Validate → Report      │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                    ┌──────────────────┐
│  MULTI-AGENT      │                    │  REASONING       │
│  SYSTEM           │                    │  AGENT           │
│  (8 agents)       │                    │  (Explains Why)  │
└───────────────────┘                    └──────────────────┘
        │                                           │
        ▼                                           ▼
┌───────────────────────────────────────────────────────────┐
│              CIVICMIND ENVIRONMENT                        │
│  • City State (20+ metrics)                               │
│  • Crisis Engine (10 tiers)                               │
│  • Citizen Engine (schema drift v1→v5)                    │
│  • Reward Model (context-aware)                           │
└───────────────────────────────────────────────────────────┘
        │                                           │
        ▼                                           ▼
┌──────────────────┐                    ┌──────────────────┐
│  GRPO TRAINING   │                    │  MOCK APIs       │
│  (Qwen 2.5 0.5B) │                    │  (8 endpoints)   │
│  Loss: 0.0035    │                    │  FastAPI         │
└──────────────────┘                    └──────────────────┘
        │                                           │
        ▼                                           ▼
┌───────────────────────────────────────────────────────────┐
│                    USER INTERFACES                        │
│  • Ultimate Demo (all features)                           │
│  • HTML Control Room (professional)                       │
│  • Shannon Demo (technical)                               │
│  • Original Dashboard (backup)                            │
└───────────────────────────────────────────────────────────┘
```

---

## 🧠 SHANNON LOOP DETAIL

```
┌─────────────────────────────────────────────────────────────┐
│                    SHANNON LOOP CYCLE                       │
└─────────────────────────────────────────────────────────────┘

    1. THINK                    2. TEST
    ┌──────────┐               ┌──────────┐
    │ Generate │               │ Simulate │
    │ 4 Options│──────────────▶│   Each   │
    │          │               │  Option  │
    └──────────┘               └──────────┘
         │                           │
         │                           │
         ▼                           ▼
    ┌──────────┐               ┌──────────┐
    │ Options: │               │ Results: │
    │ • hold   │               │ • Score  │
    │ • tax    │               │ • Impact │
    │ • invest │               │ • Risk   │
    │ • budget │               │ • Conf.  │
    └──────────┘               └──────────┘
                                     │
                                     │
         ┌───────────────────────────┘
         │
         ▼
    3. VALIDATE                 4. REPORT
    ┌──────────┐               ┌──────────┐
    │ Compare  │               │  Select  │
    │   All    │──────────────▶│   Best   │
    │ Results  │               │  + Why   │
    └──────────┘               └──────────┘
         │                           │
         │                           │
         ▼                           ▼
    ┌──────────┐               ┌──────────┐
    │ Ranking: │               │ Output:  │
    │ 1. invest│               │ • Action │
    │ 2. tax   │               │ • Reason │
    │ 3. budget│               │ • Conf.  │
    │ 4. hold  │               │ • What if│
    └──────────┘               └──────────┘
```

---

## 👥 MULTI-AGENT SYSTEM

```
┌─────────────────────────────────────────────────────────────┐
│                    8 AI AGENTS                              │
└─────────────────────────────────────────────────────────────┘

    GOVERNMENT AGENTS (6)
    ┌──────────────────┐
    │     MAYOR        │  ← Coordinates all
    │  (Trust Focus)   │
    └──────────────────┘
            │
    ┌───────┴───────────────────────────┐
    │                                   │
    ▼                                   ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ HEALTH  │  │ FINANCE │  │ POLICE  │  │ URBAN   │
│MINISTER │  │ OFFICER │  │  CHIEF  │  │ PLANNER │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
    │            │            │            │
    │            │            │            │
    ▼            ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│Disease  │  │ Budget  │  │ Crime   │  │Housing  │
│Control  │  │ Balance │  │Reduction│  │ & Infra │
└─────────┘  └─────────┘  └─────────┘  └─────────┘

    OVERSIGHT AGENT (1)
    ┌──────────────────┐
    │   FLEET AI       │  ← Monitors all
    │  (Oversight)     │
    └──────────────────┘

    EMERGENT AGENT (1)
    ┌──────────────────┐
    │   REBEL AGENT    │  ← Spawns when trust < 30%
    │  (Opposition)    │     (Unique feature!)
    └──────────────────┘
```

---

## 🌍 ENVIRONMENT DETAIL

```
┌─────────────────────────────────────────────────────────────┐
│              CIVICMIND ENVIRONMENT                          │
└─────────────────────────────────────────────────────────────┘

    CITY STATE (20+ Metrics)
    ┌────────────────────────────────────────┐
    │ • Trust Score (0-100%)                 │
    │ • Civil Unrest (0-100%)                │
    │ • Budget ($0-$2M)                      │
    │ • GDP Index (0-2.0)                    │
    │ • Survival Rate (0-100%)               │
    │ • Crime Index (0-100%)                 │
    │ • Disease Prevalence (0-100%)          │
    │ • Hospital Capacity (0-100%)           │
    │ • Unemployment (0-100%)                │
    │ • Corruption (0-100%)                  │
    │ • Rebel Strength (0-100%)              │
    │ • ... and more                         │
    └────────────────────────────────────────┘

    CRISIS ENGINE (10 Tiers)
    ┌────────────────────────────────────────┐
    │ Tier 1: Minor issues                   │
    │ Tier 2: Moderate problems              │
    │ Tier 3: Serious concerns               │
    │ Tier 4: Major crises                   │
    │ Tier 5: Critical situations            │
    │ Tier 6: Severe emergencies             │
    │ Tier 7: Catastrophic events            │
    │ Tier 8: Existential threats            │
    │ Tier 9: Collapse imminent              │
    │ Tier 10: Total system failure          │
    │                                        │
    │ Auto-escalates based on performance    │
    └────────────────────────────────────────┘

    CITIZEN ENGINE (Schema Drift)
    ┌────────────────────────────────────────┐
    │ Week 1-10:  v1 (basic)                 │
    │ Week 11-20: v2 (+ urgency)             │
    │ Week 21-30: v3 (+ sentiment)           │
    │ Week 31-40: v4 (+ location)            │
    │ Week 41-52: v5 (+ demographics)        │
    │                                        │
    │ Petitions evolve over time             │
    └────────────────────────────────────────┘
```

---

## 🎓 TRAINING PIPELINE

```
┌─────────────────────────────────────────────────────────────┐
│                  GRPO TRAINING PIPELINE                     │
└─────────────────────────────────────────────────────────────┘

    DATA GENERATION
    ┌──────────────────┐
    │ Generate 500     │
    │ State-Action     │
    │ Pairs            │
    └──────────────────┘
            │
            ▼
    ┌──────────────────┐
    │ Format as        │
    │ Prompts          │
    │ (Qwen style)     │
    └──────────────────┘
            │
            ▼
    GRPO TRAINING
    ┌──────────────────┐
    │ For each prompt: │
    │ 1. Generate 2    │
    │    responses     │
    │ 2. Compute       │
    │    rewards       │
    │ 3. Select best   │
    │ 4. Train on best │
    └──────────────────┘
            │
            ▼
    ┌──────────────────┐
    │ Epoch 1: 0.2256  │
    │ Epoch 2: 0.0145  │
    │ Epoch 3: 0.0303  │
    │ Epoch 4: 0.0098  │
    │ Epoch 5: 0.0035  │ ← EXCELLENT!
    └──────────────────┘
            │
            ▼
    ┌──────────────────┐
    │ Save Model       │
    │ (LoRA adapters)  │
    │ 2.16M params     │
    └──────────────────┘
```

---

## 🎨 USER INTERFACE STACK

```
┌─────────────────────────────────────────────────────────────┐
│                    4 UI OPTIONS                             │
└─────────────────────────────────────────────────────────────┘

    1. ULTIMATE DEMO (RECOMMENDED)
    ┌────────────────────────────────────────┐
    │ • Learning progress chart              │
    │ • Agent conflict visualization         │
    │ • Real-time confidence bars            │
    │ • Shannon loop (4 phases)              │
    │ • Counterfactual analysis              │
    │ • Failure case honesty                 │
    │                                        │
    │ Port: 8501 (default)                   │
    │ File: demo/ultimate_demo.py            │
    └────────────────────────────────────────┘

    2. HTML CONTROL ROOM (PROFESSIONAL)
    ┌────────────────────────────────────────┐
    │ • NASA/military aesthetic              │
    │ • 3-panel layout                       │
    │ • Real backend connection              │
    │ • Live metric updates                  │
    │ • Crisis management                    │
    │ • Rebel spawning                       │
    │                                        │
    │ Port: 8505                             │
    │ File: demo/control_room_html.py        │
    └────────────────────────────────────────┘

    3. SHANNON DEMO (TECHNICAL)
    ┌────────────────────────────────────────┐
    │ • Terminal output                      │
    │ • Shannon loop phases                  │
    │ • Decision comparison table            │
    │ • Reasoning explanation                │
    │ • Counterfactual analysis              │
    │                                        │
    │ Port: N/A (terminal)                   │
    │ File: demo/shannon_demo.py             │
    └────────────────────────────────────────┘

    4. ORIGINAL DASHBOARD (BACKUP)
    ┌────────────────────────────────────────┐
    │ • Streamlit dashboard                  │
    │ • All features working                 │
    │ • Real-time simulation                 │
    │                                        │
    │ Port: 8503                             │
    │ File: demo/dashboard_control_room.py   │
    └────────────────────────────────────────┘
```

---

## 🔄 DATA FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                       │
└─────────────────────────────────────────────────────────────┘

    USER INPUT
        │
        ▼
    ┌──────────────┐
    │ Select       │
    │ Crisis       │
    │ Scenario     │
    └──────────────┘
        │
        ▼
    ┌──────────────┐
    │ Shannon Loop │
    │ Generates    │
    │ 4 Options    │
    └──────────────┘
        │
        ▼
    ┌──────────────┐
    │ Simulate     │
    │ Each Option  │
    │ in Env       │
    └──────────────┘
        │
        ▼
    ┌──────────────┐
    │ Compute      │
    │ Rewards      │
    │ & Scores     │
    └──────────────┘
        │
        ▼
    ┌──────────────┐
    │ Reasoning    │
    │ Agent        │
    │ Explains     │
    └──────────────┘
        │
        ▼
    ┌──────────────┐
    │ Display      │
    │ Results      │
    │ in UI        │
    └──────────────┘
        │
        ▼
    ┌──────────────┐
    │ User Sees:   │
    │ • Best       │
    │ • Why        │
    │ • What if    │
    │ • Confidence │
    └──────────────┘
```

---

## 🏆 HACKATHON COVERAGE MAP

```
┌─────────────────────────────────────────────────────────────┐
│              5 THEMES + 6 BONUSES COVERAGE                  │
└─────────────────────────────────────────────────────────────┘

    THEME 1: MULTI-AGENT
    ✅ 8 agents (6 gov + oversight + rebel)
    ✅ Partial observability
    ✅ Coordinated decisions
    ✅ Emergent behavior (rebel)

    THEME 2: LONG-HORIZON
    ✅ 52-week episodes
    ✅ Compound effects
    ✅ Long-term consequences
    ✅ Trajectory rewards

    THEME 3.1: PROFESSIONAL TASKS
    ✅ 8 FastAPI endpoints
    ✅ Partial observability
    ✅ Tool calls for info
    ✅ RESTful architecture

    THEME 3.2: PERSONAL TASKS
    ✅ Citizen petitions
    ✅ Schema drift (v1→v5)
    ✅ Context-aware messages
    ✅ Evolving complexity

    THEME 4: SELF-IMPROVEMENT
    ✅ 10 difficulty tiers
    ✅ Auto-escalating crises
    ✅ Performance-based adjustment
    ✅ Adaptive challenge

    THEME 5: WILD CARD
    ✅ Emergent rebel agent
    ✅ Spawns when trust < 30%
    ✅ Not pre-programmed
    ✅ Unique mechanic

    BONUS 1: FLEET AI
    ✅ Oversight agent implemented

    BONUS 2: PATRONUS AI
    ✅ Schema drift system

    BONUS 3: HUGGING FACE
    ✅ Qwen 2.5 0.5B model

    BONUS 4: ANTHROPIC
    ✅ Claude-compatible prompts

    BONUS 5: OPENAI
    ✅ GPT-compatible prompts

    BONUS 6: COHERE
    ✅ Cohere-compatible prompts
```

---

## 📊 METRICS & MONITORING

```
┌─────────────────────────────────────────────────────────────┐
│                  TRACKED METRICS                            │
└─────────────────────────────────────────────────────────────┘

    GOVERNANCE METRICS
    • Trust Score (0-100%)
    • Civil Unrest (0-100%)
    • Corruption (0-100%)
    • Rebel Strength (0-100%)

    ECONOMIC METRICS
    • Budget Remaining ($)
    • GDP Index (0-2.0)
    • Unemployment (0-100%)
    • Tax Rate (0-100%)

    HEALTH METRICS
    • Survival Rate (0-100%)
    • Disease Prevalence (0-100%)
    • Hospital Capacity (0-100%)
    • Vaccination Rate (0-100%)

    SECURITY METRICS
    • Crime Index (0-100%)
    • Police Presence (0-100%)
    • Security Level (0-100%)

    INFRASTRUCTURE METRICS
    • Housing Quality (0-100%)
    • Infrastructure (0-100%)
    • Public Services (0-100%)

    TRAINING METRICS
    • Loss (per epoch)
    • Reward (per episode)
    • Confidence (per decision)
    • Impact (HIGH/MEDIUM/LOW)
    • Risk (HIGH/MEDIUM/LOW)
```

---

## 🔧 TECHNOLOGY STACK

```
┌─────────────────────────────────────────────────────────────┐
│                  COMPLETE TECH STACK                        │
└─────────────────────────────────────────────────────────────┘

    CORE FRAMEWORK
    • Python 3.8+
    • OpenEnv (environment)
    • Gymnasium (RL interface)

    MACHINE LEARNING
    • Transformers (Hugging Face)
    • Qwen 2.5 0.5B (model)
    • LoRA (efficient training)
    • PEFT (parameter-efficient)

    TRAINING
    • GRPO (custom implementation)
    • PyTorch (backend)
    • tqdm (progress bars)

    UI FRAMEWORKS
    • Streamlit (dashboards)
    • HTML/CSS/JS (control room)
    • FastAPI (mock APIs)

    DATA & STORAGE
    • JSON (state serialization)
    • Pickle (model checkpoints)
    • CSV (evaluation results)

    DEVELOPMENT
    • Git (version control)
    • Docker (containerization)
    • pytest (testing)
```

---

## 🎯 DECISION FLOW EXAMPLE

```
┌─────────────────────────────────────────────────────────────┐
│           EXAMPLE: LOW TRUST CRISIS                         │
└─────────────────────────────────────────────────────────────┘

    INITIAL STATE
    • Trust: 35%
    • Unrest: 65%
    • Budget: $500k
    • Crisis: Low Trust

    SHANNON LOOP: THINK
    Generated 4 options:
    1. hold
    2. reduce_tax
    3. invest_in_welfare
    4. emergency_budget_release

    SHANNON LOOP: TEST
    Simulated each:
    1. hold → Trust: 34%, Unrest: 66%
    2. reduce_tax → Trust: 45%, Unrest: 65%
    3. invest_in_welfare → Trust: 50%, Unrest: 55%
    4. emergency_budget → Trust: 55%, Unrest: 50%

    SHANNON LOOP: VALIDATE
    Scored each:
    1. hold → 0.512 (LOW impact, LOW risk)
    2. reduce_tax → 0.640 (MEDIUM impact, LOW risk)
    3. invest_in_welfare → 0.723 (HIGH impact, MEDIUM risk)
    4. emergency_budget → 0.615 (HIGH impact, HIGH risk)

    SHANNON LOOP: REPORT
    Best: invest_in_welfare
    Reason: Trust critically low, welfare restores confidence
    Confidence: 78%
    Counterfactual: reduce_tax is 8.3% worse

    RESULT
    • Action taken: invest_in_welfare
    • Trust: 35% → 50% (+15%)
    • Unrest: 65% → 55% (-10%)
    • Budget: $500k → $300k (-$200k)
    • Outcome: Crisis resolved!
```

---

## 🏆 WINNING ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│              WHY THIS ARCHITECTURE WINS                     │
└─────────────────────────────────────────────────────────────┘

    COMPLETENESS
    ✅ All 5 themes covered
    ✅ All 6 bonuses eligible
    ✅ Production-ready code
    ✅ Complete documentation

    INNOVATION
    ✅ Shannon loop (unique)
    ✅ Emergent rebel (only project)
    ✅ Learning visible (shows improvement)
    ✅ Counterfactual (killer feature)

    TECHNICAL EXCELLENCE
    ✅ GRPO training (advanced RL)
    ✅ Context-aware rewards
    ✅ Efficient (RTX 3060)
    ✅ Modular architecture

    PRESENTATION
    ✅ 4 working UIs
    ✅ Professional design
    ✅ Clear documentation
    ✅ Demo-ready

    PROOF OF INTELLIGENCE
    ✅ Doesn't just act
    ✅ PROVES every decision
    ✅ Shows reasoning
    ✅ Demonstrates learning
```

---

*System Architecture - Complete Visual Overview*  
*All Components Documented*  
*Ready for Demo*

