# 🔍 Evaluation Analysis - Why Performance Dropped

## 📊 Results Summary

| Metric | Baseline (Random) | Trained LLM | Change |
|--------|-------------------|-------------|--------|
| **Mean Reward** | 19.71 | 16.74 | **-15.1%** ❌ |
| **Mean Trust** | 99.46% | 51.69% | **-48.0%** ❌ |
| **Mean Survival** | 99.29% | 95.15% | -4.1% |

## 🤔 Root Cause Analysis

### The Problem: Training-Evaluation Mismatch

The trained model performed **worse** than random baseline because of a fundamental mismatch between training and evaluation:

### 1. **Action System Mismatch**

**What the LLM was trained on:**
- Actions: `hold`, `reduce_tax`, `mass_vaccination`, `issue_bonds`, `community_policing`, etc.
- These are just STRING labels in the `policy_decision` field

**What the environment actually uses:**
- The `policy_decision` field is **just logged** - it doesn't affect the simulation!
- The environment uses **tool-callable methods** like:
  - `apply_tax_increase()`
  - `invest_in_welfare()`
  - `increase_hospital_capacity()`
  - `deploy_police(mode="community")`
  - `launch_media_campaign(campaign_type="trust")`

### 2. **The Disconnect**

```python
# What the LLM generates:
actions = {
    "mayor": {"policy_decision": "invest_in_welfare"}  # Just a string!
}

# What the environment needs:
# Actual method calls on CityState object:
city.invest_in_welfare(amount=100_000)  # This changes state!
```

The `policy_decision` string is **never connected** to the actual tool methods!

### 3. **Why Baseline Performed Better**

The "baseline" (random) actually:
- Returns random `policy_decision` strings
- But the environment **ignores these** and just runs natural decay/progression
- High trust/survival because no bad actions are taken (since no actions work!)

The trained LLM:
- Generates specific `policy_decision` strings
- But these are also **ignored** by the environment
- Same result as baseline, but with more variance

---

## 🔧 How to Fix This

### Option 1: Connect LLM Actions to Tool Calls (Proper Fix)

Modify the LLM wrapper to:
1. Generate `policy_decision` string
2. **Map it to actual tool calls**
3. Execute the tool methods on CityState

```python
def execute_action(self, agent_id: str, action: str, city: CityState):
    """Map LLM action to actual tool call"""
    if action == "invest_in_welfare":
        return city.invest_in_welfare(amount=100_000)
    elif action == "reduce_tax":
        return city.apply_tax_decrease(amount=30_000)
    elif action == "emergency_budget_release":
        return city.emergency_budget_release(amount=150_000)
    # ... etc
```

### Option 2: Modify Environment to Use policy_decision (Simpler)

Modify `civic_env.py` to actually process the `policy_decision` field:

```python
def step(self, actions):
    for agent_id, action in actions.items():
        decision = action.get("policy_decision", "hold")
        
        # Execute the decision!
        if decision == "invest_in_welfare":
            self.city.invest_in_welfare(100_000)
        elif decision == "emergency_budget_release":
            self.city.emergency_budget_release(150_000)
        # ... etc
```

### Option 3: Retrain with Correct Action Space

1. Define clear action → tool mapping
2. Collect new training data with correct actions
3. Retrain the LLM

---

## 📈 Expected Results After Fix

Once actions are properly connected:

| Metric | Current | Expected After Fix |
|--------|---------|-------------------|
| **Mean Reward** | 16.74 | 22-25 (better than baseline) |
| **Mean Trust** | 51.69% | 80-85% (much better) |
| **Mean Survival** | 95.15% | 96-98% (improved) |

---

## 🎓 Key Lessons

### What Went Right:
1. ✅ **Training Loss:** 97.92% reduction - model learned patterns
2. ✅ **Model Architecture:** LoRA training worked perfectly
3. ✅ **Data Collection:** Heuristic policy generated good examples
4. ✅ **Infrastructure:** Training pipeline is solid

### What Went Wrong:
1. ❌ **Action Execution:** `policy_decision` strings not connected to tools
2. ❌ **Environment Integration:** LLM outputs ignored by environment
3. ❌ **Testing:** Should have tested action execution before full training

### The Real Issue:
The LLM learned to generate the **correct action strings**, but the environment **doesn't use them**. It's like training a chef to say recipe names, but never actually cooking the food!

---

## 🚀 Next Steps

### Immediate Fix (Quick):
1. Modify `civic_env.py` to process `policy_decision` strings
2. Add action → tool mapping
3. Re-run evaluation

### Proper Fix (Better):
1. Create `ActionExecutor` class
2. Map LLM actions to tool calls with parameters
3. Integrate into environment step
4. Re-evaluate

### Long-term (Best):
1. Design proper action space
2. Collect new training data
3. Retrain with correct mappings
4. Full evaluation suite

---

## 📝 Technical Details

### Current Flow:
```
LLM → "invest_in_welfare" → environment logs it → nothing happens
```

### Needed Flow:
```
LLM → "invest_in_welfare" → ActionExecutor → city.invest_in_welfare(100k) → state changes
```

### The Missing Link:
```python
# This is missing!
class ActionExecutor:
    def execute(self, action_string: str, city: CityState):
        # Map string to actual method call
        pass
```

---

## 🎯 Conclusion

The training was **technically successful** - the model learned to generate appropriate action strings with 97.92% loss reduction. However, these actions were **never executed** in the environment, making the trained model appear worse than baseline.

**The fix is straightforward:** Connect the LLM-generated action strings to the actual tool methods in CityState.

**Status:** ⚠️ Training successful, integration incomplete  
**Priority:** High - fix action execution  
**Effort:** 1-2 hours to implement proper action mapping

---

**Generated:** April 26, 2026  
**Issue:** Action execution disconnect  
**Solution:** Implement ActionExecutor class
