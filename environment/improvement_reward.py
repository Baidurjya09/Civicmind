"""
Improvement-Based Reward Function
Rewards progress and intelligent action-taking
"""

def calculate_improvement_reward(env) -> float:
    """
    Reward function focused on IMPROVEMENT and PROGRESS.
    
    Key insight: Good governance improves metrics over time,
    not just maintains high values.
    """
    
    reward = 0.0
    
    # 1. IMPROVEMENT REWARDS (50% of total) - Most important!
    if len(env.episode_history) >= 2:
        prev_state = env.episode_history[-2]['city_state']
        curr_state = env.city.metrics_dict()
        
        # Trust improvement (most important for governance)
        trust_delta = curr_state['trust_score'] - prev_state['trust_score']
        if trust_delta > 0:
            reward += trust_delta * 2.0  # Strong reward for trust gains
        elif trust_delta < -0.05:
            reward += trust_delta * 0.5  # Small penalty for trust loss
        
        # Survival improvement
        survival_delta = curr_state['survival_rate'] - prev_state['survival_rate']
        if survival_delta > 0:
            reward += survival_delta * 1.0
        
        # GDP improvement
        gdp_delta = curr_state['gdp_index'] - prev_state['gdp_index']
        if gdp_delta > 0:
            reward += gdp_delta * 0.5
    
    # 2. BASELINE STATE QUALITY (30% of total)
    reward += env.city.survival_rate * 0.15
    reward += env.city.trust_score * 0.10
    reward += (env.city.gdp_index / 1.5) * 0.05
    
    # 3. ACTIVE GOVERNANCE BONUS (20% of total)
    if hasattr(env, 'episode_history') and len(env.episode_history) > 0:
        last_actions = env.episode_history[-1].get('actions', {})
        
        # Count meaningful actions
        meaningful_actions = sum(
            1 for action in last_actions.values()
            if action.get('policy_decision') in [
                'invest_in_welfare', 'emergency_budget_release',
                'mass_vaccination', 'increase_hospital_staff',
                'community_policing', 'emergency_repairs',
                'press_conference', 'social_media_campaign'
            ]
        )
        
        # Reward taking meaningful actions
        if meaningful_actions > 0:
            reward += 0.10 * min(1.0, meaningful_actions / 2)
        
        # Bonus for action during crisis
        active_crises = env.crisis_engine.get_active_crises()
        if len(active_crises) > 0 and meaningful_actions > 0:
            reward += 0.10
    
    # 4. PENALTIES
    # Crisis penalty
    crisis_severity = env.crisis_engine.get_total_severity()
    reward -= crisis_severity * 0.10
    
    # Rebel penalty
    if env.rebel_active:
        reward -= env.city.rebel_strength * 0.15
    
    # Collapse penalty
    if env.city.survival_rate < 0.70:
        reward -= 0.20
    if env.city.trust_score < 0.30:
        reward -= 0.15
    
    return max(0.0, min(1.0, reward))
