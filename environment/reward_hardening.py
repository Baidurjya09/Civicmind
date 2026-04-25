"""
REWARD HARDENING - THE WINNING MOVE
Add penalties and bonuses to make RL training more effective
"""

def calculate_hardened_reward(env) -> float:
    """
    Improved reward function with:
    1. Penalty for inaction
    2. Penalty for instability
    3. Bonus for fast resolution
    """
    
    # Base components (same as before)
    survival_component = env.city.survival_rate * 0.4
    trust_component = env.city.trust_score * 0.3
    gdp_component = (env.city.gdp_index / 1.5) * 0.2
    security_component = (1 - env.city.crime_index) * 0.1
    
    # Existing penalties
    rebel_penalty = env.city.rebel_strength * 0.2 if env.rebel_active else 0
    crisis_penalty = env.crisis_engine.get_total_severity() * 0.05
    
    # NEW: Penalty for inaction (check if all agents did "hold")
    inaction_penalty = 0.0
    if hasattr(env, 'episode_history') and len(env.episode_history) > 0:
        last_actions = env.episode_history[-1].get('actions', {})
        all_hold = all(
            action.get('policy_decision', 'hold') == 'hold' 
            for action in last_actions.values()
        )
        if all_hold and env.crisis_engine.get_total_severity() > 0.3:
            inaction_penalty = 0.10  # Penalize doing nothing during crisis
    
    # NEW: Penalty for instability (rapid metric changes)
    instability_penalty = 0.0
    if len(env.episode_history) >= 2:
        prev_state = env.episode_history[-2]['city_state']
        curr_state = env.city.metrics_dict()
        
        # Check for large swings
        trust_change = abs(curr_state['trust_score'] - prev_state['trust_score'])
        survival_change = abs(curr_state['survival_rate'] - prev_state['survival_rate'])
        
        if trust_change > 0.15 or survival_change > 0.10:
            instability_penalty = 0.08  # Penalize erratic behavior
    
    # NEW: Bonus for fast crisis resolution
    resolution_bonus = 0.0
    active_crises = len(env.crisis_engine.get_active_crises())
    if active_crises == 0 and env.current_week < env.config.max_weeks * 0.7:
        resolution_bonus = 0.12  # Reward early crisis resolution
    
    # NEW: Bonus for maintaining high trust
    sustained_trust_bonus = 0.0
    if env.city.trust_score > 0.70 and env.current_week > 5:
        sustained_trust_bonus = 0.05
    
    # NEW: Penalty for low budget (running out of resources)
    budget_penalty = 0.0
    if env.city.budget_remaining < 5000:
        budget_penalty = 0.06
    
    # Calculate final reward
    reward = (
        survival_component +
        trust_component +
        gdp_component +
        security_component +
        resolution_bonus +
        sustained_trust_bonus -
        rebel_penalty -
        crisis_penalty -
        inaction_penalty -
        instability_penalty -
        budget_penalty
    )
    
    return max(0.0, min(1.0, reward))


def get_reward_breakdown(env) -> dict:
    """Get detailed breakdown of reward components for debugging"""
    survival_component = env.city.survival_rate * 0.4
    trust_component = env.city.trust_score * 0.3
    gdp_component = (env.city.gdp_index / 1.5) * 0.2
    security_component = (1 - env.city.crime_index) * 0.1
    
    rebel_penalty = env.city.rebel_strength * 0.2 if env.rebel_active else 0
    crisis_penalty = env.crisis_engine.get_total_severity() * 0.05
    
    return {
        "survival": survival_component,
        "trust": trust_component,
        "gdp": gdp_component,
        "security": security_component,
        "rebel_penalty": -rebel_penalty,
        "crisis_penalty": -crisis_penalty,
        "total": calculate_hardened_reward(env)
    }
