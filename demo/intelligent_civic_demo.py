"""
Intelligent Civic System Demo
8-Agent Multi-Agent System with LLM Coordination
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from environment import CivicMindEnv, CivicMindConfig
from training.llm_agent_wrapper import LLMAgentWrapper


class IntelligentCivicDemo:
    """
    Demonstrates 8-agent system with LLM coordination.
    Shows agents "speaking" and making decisions together.
    """
    
    def __init__(self):
        # Create environment
        config = CivicMindConfig(
            max_weeks=20,
            difficulty=3,
            enable_rebel=True
        )
        self.env = CivicMindEnv(config)
        self.wrapper = LLMAgentWrapper()
        
        # Agent roles
        self.agent_roles = {
            "mayor": "💼 Mayor",
            "health_minister": "🏥 Health Minister",
            "finance_officer": "💰 Finance Officer",
            "police_chief": "🚓 Police Chief",
            "infrastructure_head": "🏗️ Infrastructure Head",
            "media_spokesperson": "📢 Media Spokesperson"
        }
    
    def format_state(self, obs):
        """Format state for display"""
        return f"""
🌆 CITY STATE (Week {obs['week']}/{obs['max_weeks']}):
  📊 Trust: {obs['trust_score']:.0%}
  ❤️  Survival: {obs['survival_rate']:.0%}
  💵 GDP: {obs['gdp_index']:.2f}
  💰 Budget: ${obs['budget_remaining']:,.0f}
  ⚠️  Crises: {', '.join(obs['active_crises']) if obs['active_crises'] else 'None'}
  🔴 Rebel: {'ACTIVE' if obs['rebel_active'] else 'Inactive'}
"""
    
    def agent_speaks(self, agent_id, observation, action):
        """Generate agent speech"""
        role = self.agent_roles[agent_id]
        trust = observation['trust_score']
        budget = observation['budget_remaining']
        crises = observation['active_crises']
        
        # Generate contextual speech
        if agent_id == "mayor":
            if trust < 0.4:
                speech = f"Public trust is critically low at {trust:.0%}. We must act decisively."
            elif budget < 500000:
                speech = f"Budget is running low (${budget:,.0f}). We need fiscal prudence."
            elif crises:
                speech = f"We face {len(crises)} active crises. Coordination is essential."
            else:
                speech = "City is stable. Let's maintain our course."
        
        elif agent_id == "health_minister":
            survival = observation['survival_rate']
            if survival < 0.85:
                speech = f"Survival rate at {survival:.0%} is concerning. Healthcare intervention needed."
            elif 'pandemic' in crises:
                speech = "Pandemic detected. Immediate health response required."
            else:
                speech = "Public health metrics are acceptable."
        
        elif agent_id == "finance_officer":
            gdp = observation['gdp_index']
            if gdp < 0.9:
                speech = f"GDP at {gdp:.2f} indicates recession. Economic stimulus recommended."
            elif budget > 2000000:
                speech = f"Strong budget position (${budget:,.0f}). Room for investment."
            else:
                speech = "Maintaining fiscal balance."
        
        elif agent_id == "police_chief":
            if observation.get('rebel_active'):
                speech = "Rebel movement detected. Security measures required."
            elif trust < 0.5:
                speech = "Low trust may lead to unrest. Community engagement needed."
            else:
                speech = "Security situation stable."
        
        elif agent_id == "infrastructure_head":
            if 'infrastructure_failure' in crises:
                speech = "Infrastructure failure detected. Emergency repairs needed."
            elif budget > 1500000:
                speech = "Budget allows for infrastructure improvements."
            else:
                speech = "Maintaining existing infrastructure."
        
        elif agent_id == "media_spokesperson":
            if trust < 0.5:
                speech = f"Trust at {trust:.0%}. Public communication campaign needed."
            elif crises:
                speech = "Multiple crises require transparent communication."
            else:
                speech = "Public sentiment is positive."
        
        else:
            speech = "Monitoring situation."
        
        # Add action
        action_desc = self.get_action_description(action)
        
        return f"{role}: \"{speech}\"\n  → Action: {action_desc}"
    
    def get_action_description(self, action):
        """Get human-readable action description"""
        descriptions = {
            "hold": "Monitor and wait",
            "emergency_budget_release": "Release emergency funds",
            "invest_in_welfare": "Invest in public welfare",
            "reduce_tax": "Reduce tax burden",
            "increase_taxes": "Increase tax revenue",
            "mass_vaccination": "Launch vaccination campaign",
            "increase_hospital_staff": "Hire hospital staff",
            "issue_bonds": "Issue government bonds",
            "stimulus_package": "Deploy stimulus package",
            "community_policing": "Deploy community policing",
            "emergency_repairs": "Conduct emergency repairs",
            "press_conference": "Hold press conference",
            "social_media_campaign": "Launch social media campaign"
        }
        return descriptions.get(action, action)
    
    def run_demo(self, num_weeks=5):
        """Run interactive demo"""
        print("\n" + "=" * 80)
        print("  🌆 INTELLIGENT CIVIC SYSTEM DEMO")
        print("  Multi-Agent Governance with LLM Coordination")
        print("=" * 80)
        print()
        
        obs = self.env.reset()
        
        for week in range(num_weeks):
            print("\n" + "─" * 80)
            print(self.format_state(obs["mayor"]))
            print("─" * 80)
            print()
            
            # Collect agent proposals
            print("🗣️  AGENT DELIBERATION:")
            print()
            
            actions = {}
            for agent_id in self.env.AGENT_IDS:
                agent_obs = obs[agent_id]
                
                # Generate action (random for demo, would be LLM in production)
                action = self.wrapper.generate_action(agent_id, agent_obs)
                actions[agent_id] = {"policy_decision": action}
                
                # Agent speaks
                speech = self.agent_speaks(agent_id, agent_obs, action)
                print(speech)
                print()
            
            # Execute step
            print("⚙️  EXECUTING DECISIONS...")
            obs, reward, done, info = self.env.step(actions)
            
            print(f"📊 Week Result: Reward = {reward:.4f}")
            
            if done:
                print("\n🏁 SIMULATION ENDED")
                if info.get('city_collapsed'):
                    print("❌ City collapsed!")
                elif info.get('rebel_active'):
                    print("⚠️  Rebel takeover!")
                else:
                    print("✅ Simulation complete!")
                break
            
            print()
            input("Press Enter to continue to next week...")
        
        print("\n" + "=" * 80)
        print("  ✅ DEMO COMPLETE")
        print("=" * 80)
        print()
        
        # Final stats
        final_obs = obs["mayor"]
        print("📊 FINAL CITY STATE:")
        print(f"  Trust: {final_obs['trust_score']:.0%}")
        print(f"  Survival: {final_obs['survival_rate']:.0%}")
        print(f"  GDP: {final_obs['gdp_index']:.2f}")
        print(f"  Budget: ${final_obs['budget_remaining']:,.0f}")
        print()


def main():
    demo = IntelligentCivicDemo()
    demo.run_demo(num_weeks=5)


if __name__ == "__main__":
    main()
