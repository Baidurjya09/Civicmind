# Teaching AI Agents to Run a City (And Dealing With Rebels)

So I built this thing for the Meta × Hugging Face hackathon where AI agents try to govern a city. Spoiler: it gets messy.

## The Basic Idea

You've got 6 AI agents running different parts of city government - mayor, health minister, finance officer, police chief, infrastructure head, and media spokesperson. They each make decisions every week for a year, trying to keep people alive, happy, and not broke.

The catch? If they screw up badly enough (trust drops below 30% for too long), a rebel agent spawns and tries to overthrow them. Yeah, I made the AI fight itself.

## Why This Was Harder Than Expected

**Problem 1: Everyone learned to do nothing**

First training run, 4 out of 6 agents learned the same strategy: "hold" (aka do nothing). Turns out when your reward function penalizes spending money, agents figure out pretty quick that the safest move is... not moving.

Had to completely redesign the reward system to actually encourage taking action. Now agents get rewarded for *improving* things, not just maintaining the status quo.

**Problem 2: The task was too easy**

Initial training had agents just outputting single words like "hold" or "issue_bonds". Model learned this in like 100 steps. Loss dropped from 2.88 to 0.06 instantly. Looked impressive (97.92% reduction!) but was basically just teaching it to pick from a menu.

Fixed it by making agents explain their reasoning:
```
Action: emergency_budget_release

Reasoning: Critical situation requires immediate financial intervention 
to stabilize city operations and restore public confidence.

Expected Impact: Budget -$200K, Trust +5%, immediate crisis response
```

Way harder task, more realistic loss curve, actually looks like learning.

## What Actually Worked

**Q-Learning baseline:** Trained a simple tabular Q-learning agent first. Got +18.4% reward improvement and +107% trust improvement over random policy. Took 3 seconds to train. Sometimes simple is better.

**LLM fine-tuning:** Used Qwen2.5-0.5B with LoRA. After fixing the data issues, got each agent learning different strategies:
- Mayor: Proactive crisis management
- Health: Disease response during outbreaks  
- Finance: Economic stimulus when needed
- Police: Community policing when trust is low
- Infrastructure: Emergency repairs during crises
- Media: Public communication strategies

**The rebel mechanic:** This was just for fun but ended up being the most interesting part. When trust tanks, a rebel agent appears and grows stronger the longer you ignore it. Only way to beat it is to actually fix the underlying problems (restore trust above 55%). Forces agents to care about long-term consequences.

## Technical Stuff

- Environment: Custom OpenEnv with 52-week episodes
- Training: Q-learning (3 sec), SFT (55 min), GRPO (2 hours)
- Model: Qwen2.5-0.5B + LoRA (8.7 MB)
- Hardware: RTX 3060 (12GB VRAM)

All code is on GitHub if you want to try breaking your own city.

## Things I'd Do Differently

1. **Start with the reward function:** Spent way too long debugging why agents weren't learning, when the real issue was the reward function incentivizing the wrong behavior.

2. **Make the task harder from the start:** Single-word outputs were a mistake. Should've required reasoning from day one.

3. **Test agent diversity early:** Didn't realize 4 agents were doing the same thing until way too late.

## Results

- Q-Learning: +18.4% reward, +107% trust vs baseline
- LLM: Each agent learned unique policies with reasoning
- Rebel spawned in ~40% of episodes (agents aren't great at their jobs)
- Training time: ~2 hours total on consumer GPU

## Try It

The environment is up on GitHub. Fair warning: your agents will probably let the city collapse a few times before they figure it out. Mine did.

Also the rebel agent is surprisingly hard to beat. Turns out restoring public trust after you've lost it is difficult. Who knew.

---

**Links:**
- Code: [GitHub](https://github.com/Baidurjya09/Civicmind)
- Demo: [HuggingFace Space](https://huggingface.co/spaces/Baidurjya09/civicmind)
- Training: [Colab Notebook](https://colab.research.google.com/github/Baidurjya09/Civicmind/blob/main/CivicMind_Training.ipynb)

Built for Meta × Hugging Face OpenEnv Hackathon 2026.
