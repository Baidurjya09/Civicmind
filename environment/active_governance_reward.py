"""
Active Governance Reward Function
Properly values intelligent decision-making over inaction
"""

def calculate_active_governance_reward(env) -> float:
    """
    Reward function that values active, intelligent governance.
    
    Key principles:
    1. Reward improvement, not just high values
    2. Reward appropriate actions during crises
    3. Penalize inaction when action is needed
    4. Value long-term stability over short-term metrics
    """
    
    # Base state quality (40% of reward)
    survival_component = env.city.survival_rate * 0.15
    trust_component = env.city.trust_score * 0.15
    gdp_component = (env.city.gdp_index / 1.5) * 0.10
    
    # Improvement bonus (30% of reward) - NEW!
    improvement_bonus = 0.0
    if len(env.episode_history) >= 2:
        prev_state = env.episode_history[-2]['city_state']
        curr_state = env.city.metrics_dict()
        
        # Reward improvements
        trust_improvement = curr_state['trust_score'] - prev_state['trust_score']
        survival_improvement = curr_state['survival_rate'] - prev_state['survival_rate']
        gdp_improvement = curr_state['gdp_index'] - prev_state['gdp_index']
        
        if trust_improvement > 0:
            improvement_bonus += trust_improvement * 0.5  # Strong reward for trust gains
        if survival_improvement > 0:
            improvement_bonus += survival_improvement * 0.3
        if gdp_improvement > 0:
            improvement_bonus += gdp_improvement * 0.2
        
        # Cap improvement bonus
        improvement_bonus = min(0.30, improvement_bonus)
    
    # Action appropriateness (20% of reward) - NEW!
    action_bonus = 0.0
    if hasattr(env, 'episode_history') and len(env.episode_history) > 0:
        last_actions = env.episode_history[-1].get('actions', {})
        active_crises = env.crisis_engine.get_active_crises()
        
        # Count non-hold actions
        active_actions = sum(
            1 for action in last_actions.values()
            if action.get('policy_decision', 'hold') != 'hold'
        )
        
        # Reward taking action during crises - INCREASED
        if len(active_crises) > 0 and active_actions > 0:
            action_bonus = 0.20 * min(1.0, active_actions / 2)  # Up to 0.20 for 2+ actions
        
        # Reward appropriate welfare spending when trust is low - INCREASED
        if env.city.trust_score < 0.6:
            welfare_actions = sum(
                1 for action in last_actions.values()
                if action.get('policy_decision') in ['invest_in_welfare', 'emergency_budget_release']
            )
            if welfare_actions > 0:
                action_bonus += 0.10  # Doubled from 0.05
        
        # Reward health actions during health crises - INCREASED
        if any('pandemic' in c.name.lower() for c in active_crises):
            health_actions = sum(
                1 for action in last_actions.values()
                if action.get('policy_decision') in ['mass_vaccination', 'increase_hospital_staff']
            )
            if health_actions > 0:
                action_bonus += 0.10  # Doubled from 0.05
        
        # NEW: Reward any proactive action even without crisis
        if active_actions > 0 and len(active_crises) == 0:
            action_bonus += 0.05  # Small bonus for proactive governance
    
    # Crisis management (10% of reward)
    crisis_severity = env.crisis_engine.get_total_severity()
    crisis_component = (1.0 - crisis_severity) * 0.10
    
    # Penalties
    rebel_penalty = env.city.rebel_strength * 0.15 if env.rebel_active else 0
    
    # Inaction penalty - STRONGER
    inaction_penalty = 0.0
    if hasattr(env, 'episode_history') and len(env.episode_history) > 0:
        last_actions = env.episode_history[-1].get('actions', {})
        all_hold = all(
            action.get('policy_decision', 'hold') == 'hold' 
            for action in last_actions.values()
        )
        
        # Strong penalty for inaction during crisis
        if all_hold:
            if crisis_severity > 0.5:
                inaction_penalty = 0.30  # MAJOR penalty during severe crisis
            elif crisis_severity > 0.3:
                inaction_penalty = 0.20  # Strong penalty during crisis
            elif env.city.trust_score < 0.5:
                inaction_penalty = 0.15  # Penalty when trust is low
            else:
                inaction_penalty = 0.05  # Small penalty even in good times
    
    # Budget management penalty
    budget_penalty = 0.0
    if env.city.budget_remaining < 100_000:
        budget_penalty = 0.10  # Penalty for running out of money
    elif env.city.budget_remaining > 5_000_000:
        budget_penalty = 0.05  # Small penalty for hoarding (not using resources)
    
    # Calculate final reward
    reward = (
        survival_component +
        trust_component +
        gdp_component +
        improvement_bonus +
        action_bonus +
        crisis_component -
        rebel_penalty -
        inaction_penalty -
        budget_penalty
    )
    
    return max(0.0, min(1.0, reward))


def get_active_governance_breakdown(env) -> dict:
    """Get detailed breakdown for debugging"""
    
    survival_component = env.city.survival_rate * 0.15
    trust_component = env.city.trust_score * 0.15
    gdp_component = (env.city.gdp_index / 1.5) * 0.10
    
    improvement_bonus = 0.0
    if len(env.episode_history) >= 2:
        prev_state = env.episode_history[-2]['city_state']
        curr_state = env.city.metrics_dict()
        trust_improvement = curr_state['trust_score'] - prev_state['trust_score']
        survival_improvement = curr_state['survival_rate'] - prev_state['survival_rate']
        gdp_improvement = curr_state['gdp_index'] - prev_state['gdp_index']
        
        if trust_improvement > 0:
            improvement_bonus += trust_improvement * 0.5
        if survival_improvement > 0:
            improvement_bonus += survival_improvement * 0.3
        if gdp_improvement > 0:
            improvement_bonus += gdp_improvement * 0.2
        improvement_bonus = min(0.30, improvement_bonus)
    
    return {
        "survival": survival_component,
        "trust": trust_component,
        "gdp": gdp_component,
        "improvement": improvement_bonus,
        "total": calculate_active_governance_reward(env)
    }
