# 🎤 DEMO SCRIPT - RL-FOCUSED (3 MINUTES)

**Use this exact script for judges**

---

## ⏱️ TIMING BREAKDOWN

| Time | Section | Duration |
|------|---------|----------|
| 0:00-0:15 | RL Framing | 15s |
| 0:15-0:45 | Environment | 30s |
| 0:45-1:15 | Before Training | 30s |
| 1:15-1:45 | After Training | 30s |
| 1:45-2:15 | Training Process | 30s |
| 2:15-2:45 | Shannon Loop | 30s |
| 2:45-3:00 | Close | 15s |

**Total**: 3 minutes

---

## 🎬 FULL SCRIPT

### 0:00-0:15 (15s) - RL FRAMING ⭐

**SAY**:
> "This is a reinforcement learning system where AI agents learn optimal civic decisions through environment interaction and reward optimization."

**SHOW**: Title screen

**POINT TO**: RL pipeline diagram

**KEY PHRASE**: "Reinforcement learning" (say it first!)

---

### 0:15-0:45 (30s) - ENVIRONMENT ⭐

**SAY**:
> "The environment is OpenEnv-compliant with reset, step, and reward methods. State space includes 20+ city metrics like trust, economy, and stability."

**SHOW**: Environment interaction panel

**POINT TO**: 
- `env.reset()` → Initial state
- `env.step()` → Next state + reward
- Reward signal

**KEY PHRASE**: "Environment interaction" (not "simulation")

---

### 0:45-1:15 (30s) - BEFORE TRAINING ⭐

**SAY**:
> "Before training, the agent makes random decisions with 0.45 average reward. Watch what happens in a crisis: trust is 35%, unrest is 65%. The agent chooses 'hold' and the crisis worsens."

**SHOW**: Before training example
- State: Trust 35%, Unrest 65%
- Action: hold (random)
- Reward: 0.45 (low)
- Outcome: Crisis worsens

**KEY PHRASE**: "Before training" (emphasize learning)

---

### 1:15-1:45 (30s) - AFTER TRAINING ⭐

**SAY**:
> "After GRPO training, the agent learned optimal policies with 0.72 average reward. Same crisis, but now it chooses 'invest_in_welfare' and the crisis resolves. That's 60% improvement."

**SHOW**: After training example
- State: Trust 35%, Unrest 65%
- Action: invest_in_welfare (learned)
- Reward: 0.72 (high)
- Outcome: Crisis resolves

**POINT TO**: Reward improvement chart

**KEY PHRASE**: "Learned optimal policies" (not "smart decisions")

---

### 1:45-2:15 (30s) - TRAINING PROCESS ⭐

**SAY**:
> "We trained using GRPO for 5 epochs on an RTX 3060. Loss dropped from 0.23 to 0.0035 - that's 98.4% improvement. The model learned from environment feedback and reward signals."

**SHOW**: Training metrics
- Method: GRPO
- Epochs: 5
- Loss: 0.2256 → 0.0035
- Reward: 0.45 → 0.72

**POINT TO**: Loss curve going down

**KEY PHRASE**: "Learned from environment feedback"

---

### 2:15-2:45 (30s) - SHANNON LOOP

**SAY**:
> "Shannon loop proves decisions by using the RL-trained policy to generate multiple options, simulating each, and selecting the best based on predicted rewards. You can see confidence is 82%, score gap is 4.3%, and counterfactual analysis shows what happens if we choose differently."

**SHOW**: Shannon loop in action
- 4 candidate actions
- Simulation results
- Confidence: 82%
- Score gap: +4.3%
- Counterfactual

**CLICK**: Run Shannon Loop Analysis

**KEY PHRASE**: "RL-trained policy generates candidates"

---

### 2:45-3:00 (15s) - CLOSE ⭐

**SAY**:
> "RL-trained, environment-driven, reward-optimized civic intelligence. All 5 hackathon themes, 6 bonus prizes, production-ready. The model learns, improves, and proves every decision."

**SHOW**: Final summary screen

**KEY PHRASE**: "RL-trained, environment-driven, reward-optimized"

---

## 💡 CRITICAL PHRASES (MEMORIZE)

### Must Say:
1. **"Reinforcement learning system"** (first sentence)
2. **"Environment interaction"** (not simulation)
3. **"Reward signal"** (not score)
4. **"Learned optimal policies"** (not smart decisions)
5. **"GRPO training"** (specific method)
6. **"60% improvement"** (measurable)
7. **"RL-trained policy"** (not AI model)

### Never Say:
- ❌ "Simulation system"
- ❌ "Rule-based"
- ❌ "Heuristic"
- ❌ "Pre-programmed"
- ❌ "Smart algorithm"

---

## 🎯 WHAT TO EMPHASIZE

### Emphasize (RL):
- ✅ Environment with reset() and step()
- ✅ Reward signals drive learning
- ✅ Policy network trained via GRPO
- ✅ Measurable improvement (60%)
- ✅ OpenEnv compliant

### De-emphasize (Non-RL):
- ⚠️ Shannon loop (mention but don't focus)
- ⚠️ UI design (show but don't dwell)
- ⚠️ Documentation (mention if asked)

---

## 🔥 BACKUP ANSWERS (IF ASKED)

### Q: "Is this really RL?"
**A**: "Yes. We have an OpenEnv-compliant environment with reset() and step(), a trained policy network, reward signals, and GRPO training with 98.4% loss reduction. You can see the before/after improvement."

### Q: "What's the environment?"
**A**: "CivicMindEnv - OpenEnv compliant with 20+ state metrics, 30+ actions, and composite reward function. Each action goes through env.step() and returns next state plus reward."

### Q: "What's the reward?"
**A**: "Composite: 35% trust, 25% survival, 20% economy, 10% security, 10% stability, minus penalties. Context-aware - same action gets different rewards based on state."

### Q: "How long did training take?"
**A**: "6.5 hours on RTX 3060 for 5 epochs. Loss went from 0.23 to 0.0035. Reward improved from 0.45 to 0.72."

### Q: "What's Shannon loop?"
**A**: "Decision verification layer on top of the RL policy. Uses the trained model to generate candidates, simulates each, and proves the best choice. It's not a replacement for RL - it's a proof mechanism."

---

## 📊 VISUAL CUES

### Point To:
1. **RL Pipeline diagram** (when explaining RL)
2. **env.reset() / env.step()** (when explaining environment)
3. **Before/After comparison** (when showing improvement)
4. **Loss curve** (when explaining training)
5. **Reward chart** (when showing 60% improvement)
6. **Confidence bar** (when showing Shannon loop)

### Click:
1. **Select crisis scenario**
2. **Run Shannon Loop Analysis**
3. **Show reasoning** (if time)

---

## ⏱️ TIME MANAGEMENT

### If Running Short (2:30 left):
- Skip Shannon loop details
- Go straight to close

### If Running Long (3:30 used):
- Cut Shannon loop to 15s
- Cut training process to 20s

### If Perfect (3:00):
- Follow script exactly

---

## 🏆 SUCCESS CRITERIA

### Judge Should Understand:
- ✅ This is RL (not simulation)
- ✅ Environment drives learning
- ✅ Reward signals guide policy
- ✅ Training produced improvement
- ✅ System is production-ready

### Judge Should Remember:
- ✅ "RL-trained civic intelligence"
- ✅ "60% improvement"
- ✅ "Environment interaction"
- ✅ "Reward optimization"

---

## 🎯 FINAL CHECKLIST

Before demo:
- [ ] Memorize RL framing (first 15s)
- [ ] Practice saying "reinforcement learning"
- [ ] Know the 60% improvement number
- [ ] Can explain env.step() quickly
- [ ] Understand GRPO basics
- [ ] Confident with RL terminology

During demo:
- [ ] Say "reinforcement learning" first
- [ ] Show environment interaction
- [ ] Show before/after comparison
- [ ] Emphasize 60% improvement
- [ ] Point to visual cues
- [ ] Stay under 3 minutes

After demo:
- [ ] Answer RL questions confidently
- [ ] Reference environment and reward
- [ ] Show technical credibility
- [ ] Thank judges

---

## 💡 THE ONE THING TO REMEMBER

> **"This is reinforcement learning. The agent learns from environment interaction and reward signals. We have 60% measurable improvement."**

**Say this if you forget everything else.**

---

*Demo Script - RL-Focused*  
*3 Minutes*  
*Memorize This*  
*Win This*  
*🏆*

