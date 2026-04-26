"""
Agent-Specific Reward System
Each agent has UNIQUE objectives and learns DIFFERENT policies
"""

class AgentSpecificRewards:
    """
    Each agent optimizes for different metrics.
    This ensures agents learn truly different policies.
    """
    
    @staticmethod
    def get_reward(agent_id: str, city_state, action_taken: str = None) -> float:
        """
        Calculate agent-specific reward.
        Each agent has different priorities.
        """
        
        if agent_id == "mayor":
            # Mayor: Balance all aspects of governance
            # Responsible for overall city performance
            reward = (
                0.25 * city_state.trust_score +
                0.25 * city_state.survival_rate +
                0.25 * min(city_state.gdp_index / 1.5, 1.0) +
                0.25 * (1 - city_state.crime_index)
            )
            
            # Bonus for taking action during crisis
            if action_taken and action_taken != "hold":
                if hasattr(city_state, 'active_crises') and len(city_state.active_crises) > 0:
                    reward += 0.1
            
            # Penalty for rebel activity
            if city_state.rebel_active:
                reward -= 0.15
            
            return max(0.0, min(1.0, reward))
        
        elif agent_id == "health_minister":
            # Health Minister: Prioritize survival and healthcare
            # Focus on disease control and hospital capacity
            reward = (
                0.60 * city_state.survival_rate +
                0.20 * city_state.hospital_capacity +
                0.10 * (1 - city_state.disease_prevalence) +
                0.10 * city_state.trust_score
            )
            
            # Bonus for health actions during disease outbreak
            if action_taken in ["mass_vaccination", "increase_hospital_staff"]:
                if city_state.disease_prevalence > 0.05:
                    reward += 0.15
            
            # Penalty for inaction during health crisis
            if action_taken == "hold" and city_state.disease_prevalence > 0.10:
                reward -= 0.20
            
            return max(0.0, min(1.0, reward))
        
        elif agent_id == "finance_officer":
            # Finance Officer: Prioritize economy and fiscal health
            # Focus on GDP, budget management, employment
            reward = (
                0.50 * min(city_state.gdp_index / 1.5, 1.0) +
                0.30 * min(city_state.budget_remaining / 1_000_000, 1.0) +
                0.10 * (1 - city_state.unemployment) +
                0.10 * city_state.trust_score
            )
            
            # Bonus for economic stimulus during downturn
            if action_taken in ["stimulus_package", "issue_bonds"]:
                if city_state.gdp_index < 0.9:
                    reward += 0.15
            
            # Penalty for overspending
            if city_state.budget_remaining < 200_000:
                reward -= 0.10
            
            return max(0.0, min(1.0, reward))
        
        elif agent_id == "police_chief":
            # Police Chief: Prioritize security and public order
            # Focus on crime reduction and civil stability
            reward = (
                0.50 * (1 - city_state.crime_index) +
                0.30 * (1 - city_state.civil_unrest) +
                0.20 * city_state.trust_score
            )
            
            # Bonus for community policing when trust is low
            if action_taken == "community_policing":
                if city_state.trust_score < 0.60:
                    reward += 0.15
            
            # Penalty for inaction during high crime
            if action_taken == "hold" and city_state.crime_index > 0.30:
                reward -= 0.15
            
            # Extra penalty if rebel is active (security failure)
            if city_state.rebel_active:
                reward -= 0.20
            
            return max(0.0, min(1.0, reward))
        
        elif agent_id == "infrastructure_head":
            # Infrastructure Head: Prioritize city systems
            # Focus on power grid, infrastructure health
            reward = (
                0.60 * city_state.power_grid_health +
                0.20 * city_state.hospital_capacity +
                0.10 * min(city_state.gdp_index / 1.5, 1.0) +
                0.10 * city_state.survival_rate
            )
            
            # Bonus for emergency repairs when needed
            if action_taken == "emergency_repairs":
                if city_state.power_grid_health < 0.70:
                    reward += 0.20
            
            # Penalty for infrastructure failure
            if city_state.power_grid_health < 0.50:
                reward -= 0.15
            
            return max(0.0, min(1.0, reward))
        
        elif agent_id == "media_spokesperson":
            # Media Spokesperson: Prioritize trust and communication
            # Focus on public opinion and information control
            reward = (
                0.60 * city_state.trust_score +
                0.20 * city_state.public_satisfaction +
                0.10 * (1 - city_state.misinformation_level) +
                0.10 * city_state.survival_rate
            )
            
            # Bonus for communication during low trust
            if action_taken in ["press_conference", "social_media_campaign"]:
                if city_state.trust_score < 0.60:
                    reward += 0.15
            
            # Penalty for inaction when trust is critical
            if action_taken == "hold" and city_state.trust_score < 0.40:
                reward -= 0.20
            
            # Extra bonus for preventing rebel spawn
            if city_state.trust_score > 0.30 and city_state.consecutive_low_trust_weeks > 0:
                reward += 0.10
            
            return max(0.0, min(1.0, reward))
        
        else:
            # Fallback: use balanced reward
            return (
                0.4 * city_state.survival_rate +
                0.3 * city_state.trust_score +
                0.2 * min(city_state.gdp_index / 1.5, 1.0) +
                0.1 * (1 - city_state.crime_index)
            )
    
    @staticmethod
    def get_all_rewards(city_state, actions: dict = None) -> dict:
        """Get rewards for all agents"""
        rewards = {}
        for agent_id in ["mayor", "health_minister", "finance_officer", 
                        "police_chief", "infrastructure_head", "media_spokesperson"]:
            action = actions.get(agent_id, {}).get("policy_decision", "hold") if actions else "hold"
            rewards[agent_id] = AgentSpecificRewards.get_reward(agent_id, city_state, action)
        return rewards
    
    @staticmethod
    def get_agent_objective(agent_id: str) -> str:
        """Get human-readable objective for each agent"""
        objectives = {
            "mayor": "Balance all aspects of governance (trust, survival, economy, security)",
            "health_minister": "Maximize survival rate and healthcare capacity",
            "finance_officer": "Optimize economic performance and fiscal health",
            "police_chief": "Minimize crime and maintain public order",
            "infrastructure_head": "Maintain city infrastructure and power systems",
            "media_spokesperson": "Maximize public trust and control misinformation"
        }
        return objectives.get(agent_id, "Optimize city performance")
