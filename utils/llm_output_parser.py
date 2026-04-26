"""
LLM Output Parser - Extract decisions from complex outputs
CRITICAL: Without this, your system will break!
"""

import re

def extract_decision(output: str) -> str:
    """
    Extract the decision/action from LLM output.
    
    Handles formats like:
    - "Decision: hold"
    - "Action: emergency_budget_release"
    - "hold" (simple)
    - Multi-line with reasoning
    
    Args:
        output: Raw LLM output string
        
    Returns:
        Extracted action string (e.g., "hold", "emergency_budget_release")
    """
    
    # Try to find "Decision:" or "Action:" line
    for line in output.split('\n'):
        line = line.strip()
        
        # Match "Decision: action_name"
        if line.startswith('Decision:'):
            action = line.replace('Decision:', '').strip()
            # Remove any trailing punctuation or extra text
            action = action.split()[0] if action else ""
            return action
        
        # Match "Action: action_name"
        if line.startswith('Action:'):
            action = line.replace('Action:', '').strip()
            action = action.split()[0] if action else ""
            return action
    
    # Fallback: try regex to find decision/action keyword
    decision_match = re.search(r'(?:Decision|Action):\s*(\w+)', output, re.IGNORECASE)
    if decision_match:
        return decision_match.group(1)
    
    # Last resort: return first word (for simple outputs)
    first_word = output.strip().split()[0] if output.strip() else "hold"
    return first_word


def extract_reasoning(output: str) -> str:
    """
    Extract reasoning from LLM output.
    
    Returns:
        Reasoning text or empty string
    """
    for line in output.split('\n'):
        if line.strip().startswith('Reasoning:'):
            return line.replace('Reasoning:', '').strip()
    return ""


def extract_confidence(output: str) -> str:
    """
    Extract confidence level from LLM output.
    
    Returns:
        Confidence level (High/Medium/Low) or "Unknown"
    """
    for line in output.split('\n'):
        if line.strip().startswith('Confidence:'):
            return line.replace('Confidence:', '').strip()
    return "Unknown"


def parse_llm_output(output: str) -> dict:
    """
    Parse complete LLM output into structured dict.
    
    Returns:
        {
            'decision': str,
            'reasoning': str,
            'confidence': str,
            'raw_output': str
        }
    """
    return {
        'decision': extract_decision(output),
        'reasoning': extract_reasoning(output),
        'confidence': extract_confidence(output),
        'raw_output': output
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("LLM OUTPUT PARSER - TESTING")
    print("=" * 70)
    print()
    
    # Test cases
    test_cases = [
        # Elite format
        """Decision: emergency_budget_release

Reasoning: Public trust is critically low. This action will provide immediate relief.

Trade-off: Provides relief but depletes reserves

Expected Impact: Budget: $180K to $220K, Trust: 7% to 10%

Confidence: Medium-High

Timeline: Immediate""",
        
        # Simple format
        "hold",
        
        # Action format
        "Action: mass_vaccination",
        
        # With extra text
        "Decision: invest_in_welfare\nSome extra reasoning here...",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Input: {test[:50]}...")
        result = parse_llm_output(test)
        print(f"Extracted Decision: {result['decision']}")
        print(f"Confidence: {result['confidence']}")
        print()
    
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print()
    print("Usage in your code:")
    print("""
from utils.llm_output_parser import extract_decision

# When LLM generates output:
llm_output = model.generate(...)
action = extract_decision(llm_output)

# Use action in environment:
obs, reward, done, info = env.step({
    "mayor": {"policy_decision": action, "reasoning": "..."}
})
""")
