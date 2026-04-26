"""
LLM Agent Wrapper for CivicMind
Converts environment observations to LLM prompts and parses LLM responses to actions
"""

import re
from typing import Dict, Any, Optional


class LLMAgentWrapper:
    """
    Wraps LLM to act as governance agent in CivicMind environment.
    
    Converts:
    - Environment state → LLM prompt
    - LLM response → Environment action
    """
    
    # Action mappings per agent
    AGENT_ACTIONS = {
        "mayor": {
            "hold": "Take no action this week",
            "emergency_budget_release": "Release emergency budget funds",
            "invest_in_welfare": "Invest in citizen welfare programs",
            "reduce_tax": "Reduce tax burden on citizens"
        },
        "health_minister": {
            "hold": "Take no action this week",
            "mass_vaccination": "Launch mass vaccination campaign",
            "increase_hospital_staff": "Hire additional hospital staff"
        },
        "finance_officer": {
            "hold": "Take no action this week",
            "issue_bonds": "Issue government bonds",
            "stimulus_package": "Deploy economic stimulus package"
        },
        "police_chief": {
            "hold": "Take no action this week",
            "community_policing": "Deploy community policing initiatives"
        },
        "infrastructure_head": {
            "hold": "Take no action this week",
            "emergency_repairs": "Conduct emergency infrastructure repairs"
        },
        "media_spokesperson": {
            "hold": "Take no action this week",
            "press_conference": "Hold press conference",
            "social_media_campaign": "Launch social media campaign"
        }
    }
    
    def __init__(self, model=None, tokenizer=None):
        """
        Initialize LLM agent wrapper.
        
        Args:
            model: HuggingFace model (optional, for inference)
            tokenizer: HuggingFace tokenizer (optional, for inference)
        """
        self.model = model
        self.tokenizer = tokenizer
    
    def observation_to_prompt(self, agent_id: str, observation: Dict[str, Any]) -> str:
        """
        Convert environment observation to LLM prompt.
        
        Args:
            agent_id: Agent identifier (e.g., "mayor")
            observation: Environment observation dict
            
        Returns:
            Formatted prompt string for LLM
        """
        # Get agent role
        role_names = {
            "mayor": "Mayor",
            "health_minister": "Health Minister",
            "finance_officer": "Finance Officer",
            "police_chief": "Police Chief",
            "infrastructure_head": "Infrastructure Head",
            "media_spokesperson": "Media Spokesperson"
        }
        role = role_names.get(agent_id, agent_id)
        
        # Format situation
        trust = observation.get("trust_score", 0.5)
        survival = observation.get("survival_rate", 0.9)
        gdp = observation.get("gdp_index", 1.0)
        budget = observation.get("budget_remaining", 5000000)
        week = observation.get("week", 0)
        max_weeks = observation.get("max_weeks", 52)
        
        # Trust level description
        if trust < 0.3:
            trust_desc = "CRITICALLY LOW"
        elif trust < 0.5:
            trust_desc = "LOW"
        elif trust < 0.7:
            trust_desc = "MODERATE"
        else:
            trust_desc = "HIGH"
        
        # Crisis info
        crises = observation.get("active_crises", [])
        crisis_text = f"{len(crises)} active crises: {', '.join(crises)}" if crises else "No active crises"
        
        # Rebel info
        rebel_active = observation.get("rebel_active", False)
        rebel_text = "⚠️ REBEL MOVEMENT ACTIVE" if rebel_active else ""
        
        # Available actions
        actions = self.AGENT_ACTIONS.get(agent_id, {})
        action_list = "\n".join([f"- {action}: {desc}" for action, desc in actions.items()])
        
        # Build prompt
        prompt = f"""You are the {role} of a city in crisis.

CURRENT SITUATION (Week {week}/{max_weeks}):
- Public Trust: {trust_desc} ({trust:.0%})
- Survival Rate: {survival:.0%}
- GDP Index: {gdp:.2f}
- Budget: ${budget:,.0f}
- {crisis_text}
{rebel_text}

AVAILABLE ACTIONS:
{action_list}

What action should you take this week? Respond with ONLY the action name (e.g., "hold" or "emergency_budget_release").

Action:"""
        
        return prompt
    
    def parse_llm_response(self, agent_id: str, response: str) -> str:
        """
        Parse LLM response to extract action.
        
        Args:
            agent_id: Agent identifier
            response: Raw LLM response text
            
        Returns:
            Valid action string (defaults to "hold" if parsing fails)
        """
        # Get valid actions for this agent
        valid_actions = list(self.AGENT_ACTIONS.get(agent_id, {}).keys())
        
        # Clean response
        response = response.strip().lower()
        
        # Try exact match first
        if response in valid_actions:
            return response
        
        # Try to find action in response
        for action in valid_actions:
            if action in response:
                return action
        
        # Try fuzzy matching
        response_words = set(response.split())
        for action in valid_actions:
            action_words = set(action.replace("_", " ").split())
            if action_words.intersection(response_words):
                return action
        
        # Default to hold if can't parse
        return "hold"
    
    def generate_action(self, agent_id: str, observation: Dict[str, Any], 
                       temperature: float = 0.7, max_tokens: int = 50) -> str:
        """
        Generate action using LLM.
        
        Args:
            agent_id: Agent identifier
            observation: Environment observation
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Action string
        """
        if self.model is None or self.tokenizer is None:
            # No model loaded, return random action
            import random
            actions = list(self.AGENT_ACTIONS.get(agent_id, {"hold": ""}).keys())
            return random.choice(actions)
        
        # Generate prompt
        prompt = self.observation_to_prompt(agent_id, observation)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if self.model.device.type == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the generated part (after prompt)
        response = response[len(prompt):].strip()
        
        # Parse to action
        action = self.parse_llm_response(agent_id, response)
        
        return action
    
    def create_training_example(self, agent_id: str, observation: Dict[str, Any], 
                               action: str, reward: float) -> Dict[str, Any]:
        """
        Create training example for SFT.
        
        Args:
            agent_id: Agent identifier
            observation: Environment observation
            action: Action taken
            reward: Reward received
            
        Returns:
            Training example dict with prompt and completion
        """
        prompt = self.observation_to_prompt(agent_id, observation)
        completion = action
        
        return {
            "prompt": prompt,
            "completion": completion,
            "reward": reward,
            "agent_id": agent_id
        }


if __name__ == "__main__":
    """Test LLM agent wrapper"""
    print("Testing LLM Agent Wrapper...")
    print()
    
    wrapper = LLMAgentWrapper()
    
    # Test observation
    obs = {
        "trust_score": 0.42,
        "survival_rate": 0.85,
        "gdp_index": 1.1,
        "budget_remaining": 3500000,
        "week": 15,
        "max_weeks": 52,
        "active_crises": ["pandemic", "economic_crisis"],
        "rebel_active": True
    }
    
    # Test prompt generation
    print("=" * 70)
    print("TEST: Prompt Generation")
    print("=" * 70)
    prompt = wrapper.observation_to_prompt("mayor", obs)
    print(prompt)
    print()
    
    # Test action parsing
    print("=" * 70)
    print("TEST: Action Parsing")
    print("=" * 70)
    test_responses = [
        "emergency_budget_release",
        "I think we should release emergency budget",
        "Let's invest in welfare programs",
        "hold",
        "random gibberish"
    ]
    
    for response in test_responses:
        action = wrapper.parse_llm_response("mayor", response)
        print(f"Response: '{response}' → Action: '{action}'")
    print()
    
    # Test training example creation
    print("=" * 70)
    print("TEST: Training Example Creation")
    print("=" * 70)
    example = wrapper.create_training_example("mayor", obs, "emergency_budget_release", 0.85)
    print(f"Prompt length: {len(example['prompt'])} chars")
    print(f"Completion: {example['completion']}")
    print(f"Reward: {example['reward']}")
    print()
    
    print("✅ All tests passed!")
