"""
Action Executor - Connects LLM policy decisions to actual environment tools
"""

from typing import Dict, Any
from .city_state import CityState


class ActionExecutor:
    """
    Maps LLM-generated policy_decision strings to actual CityState tool calls.
    This is the missing link between LLM outputs and environment state changes.
    """
    
    # Action mappings: policy_decision string → (method_name, default_params)
    ACTION_MAP = {
        # Mayor actions
        "hold": None,  # No action
        "emergency_budget_release": ("emergency_budget_release", {"amount": 150_000}),
        "invest_in_welfare": ("invest_in_welfare", {"amount": 100_000}),
        "reduce_tax": ("apply_tax_decrease", {"amount": 30_000}),
        "increase_taxes": ("apply_tax_increase", {"amount": 50_000}),
        
        # Health Minister actions
        "mass_vaccination": ("increase_hospital_capacity", {"amount": 80_000}),
        "increase_hospital_staff": ("increase_hospital_capacity", {"amount": 60_000}),
        
        # Finance Officer actions
        "issue_bonds": ("apply_tax_increase", {"amount": 100_000}),  # Simulates bond revenue
        "stimulus_package": ("invest_in_welfare", {"amount": 150_000}),
        
        # Police Chief actions
        "community_policing": ("deploy_police", {"mode": "community"}),
        "riot_control": ("deploy_police", {"mode": "riot_control"}),
        
        # Infrastructure Head actions
        "emergency_repairs": ("repair_infrastructure", {"amount": 70_000}),
        
        # Media Spokesperson actions
        "press_conference": ("launch_media_campaign", {"campaign_type": "trust"}),
        "social_media_campaign": ("launch_media_campaign", {"campaign_type": "trust"}),
    }
    
    def __init__(self):
        """Initialize action executor"""
        self.execution_log = []
    
    def execute(self, agent_id: str, policy_decision: str, city: CityState) -> Dict[str, Any]:
        """
        Execute a policy decision on the city state.
        
        Args:
            agent_id: Agent making the decision
            policy_decision: Action string from LLM
            city: CityState to modify
            
        Returns:
            Result dict with success status and effects
        """
        # Get action mapping
        action_info = self.ACTION_MAP.get(policy_decision)
        
        if action_info is None:
            # "hold" or unknown action - no effect
            result = {
                "agent": agent_id,
                "action": policy_decision,
                "success": True,
                "effect": "none",
                "reason": "hold_action"
            }
        else:
            method_name, params = action_info
            
            # Get the method from CityState
            method = getattr(city, method_name, None)
            
            if method is None:
                result = {
                    "agent": agent_id,
                    "action": policy_decision,
                    "success": False,
                    "effect": "none",
                    "reason": f"method_not_found: {method_name}"
                }
            else:
                # Execute the method
                try:
                    method_result = method(**params)
                    result = {
                        "agent": agent_id,
                        "action": policy_decision,
                        "success": method_result.get("success", True),
                        "effect": method_result,
                        "method": method_name,
                        "params": params
                    }
                except Exception as e:
                    result = {
                        "agent": agent_id,
                        "action": policy_decision,
                        "success": False,
                        "effect": "none",
                        "reason": f"execution_error: {str(e)}"
                    }
        
        # Log execution
        self.execution_log.append(result)
        
        return result
    
    def execute_all(self, actions: Dict[str, Dict], city: CityState) -> Dict[str, Any]:
        """
        Execute all agent actions for one step.
        
        Args:
            actions: {agent_id: {"policy_decision": action_string}}
            city: CityState to modify
            
        Returns:
            Summary of all executions
        """
        results = {}
        
        for agent_id, action_dict in actions.items():
            policy_decision = action_dict.get("policy_decision", "hold")
            result = self.execute(agent_id, policy_decision, city)
            results[agent_id] = result
        
        return results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all executions this episode"""
        total = len(self.execution_log)
        successful = sum(1 for r in self.execution_log if r["success"])
        
        return {
            "total_actions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0.0
        }
    
    def reset(self):
        """Reset execution log"""
        self.execution_log = []


if __name__ == "__main__":
    """Test action executor"""
    print("Testing Action Executor...")
    print()
    
    # Create city and executor
    city = CityState()
    executor = ActionExecutor()
    
    print("Initial State:")
    print(f"  Trust: {city.trust_score:.2%}")
    print(f"  Budget: ${city.budget_remaining:,.0f}")
    print()
    
    # Test actions
    test_actions = {
        "mayor": {"policy_decision": "invest_in_welfare"},
        "health_minister": {"policy_decision": "mass_vaccination"},
        "finance_officer": {"policy_decision": "hold"},
    }
    
    print("Executing actions...")
    results = executor.execute_all(test_actions, city)
    
    for agent_id, result in results.items():
        print(f"\n{agent_id}:")
        print(f"  Action: {result['action']}")
        print(f"  Success: {result['success']}")
        if result['effect'] != 'none':
            print(f"  Effect: {result['effect']}")
    
    print("\nFinal State:")
    print(f"  Trust: {city.trust_score:.2%}")
    print(f"  Budget: ${city.budget_remaining:,.0f}")
    print()
    
    print("Summary:")
    summary = executor.get_execution_summary()
    print(f"  Total actions: {summary['total_actions']}")
    print(f"  Success rate: {summary['success_rate']:.0%}")
    print()
    
    print("✅ Action Executor working!")
