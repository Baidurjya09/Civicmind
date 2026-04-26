
import gradio as gr
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from environment.agent_specific_rewards import AgentSpecificRewards
import random

# Initialize environment
env = None
current_obs = None
episode_history = []

def reset_environment(max_weeks, difficulty, enable_rebel):
    """Reset the environment with new settings"""
    global env, current_obs, episode_history
    
    config = CivicMindConfig(
        max_weeks=int(max_weeks),
        difficulty=int(difficulty),
        enable_rebel=enable_rebel,
        enable_schema_drift=True
    )
    
    env = CivicMindEnv(config)
    current_obs = env.reset()
    episode_history = []
    
    status = f"""
🏙️ **CivicMind Environment Reset**

**Configuration:**
- Episode Length: {max_weeks} weeks
- Difficulty: {difficulty}/10
- Rebel Mechanic: {"Enabled" if enable_rebel else "Disabled"}

**Initial State:**
- Trust: {env.city.trust_score:.1%}
- Survival: {env.city.survival_rate:.1%}
- GDP: {env.city.gdp_index:.2f}
- Budget: ${env.city.budget_remaining:,.0f}

**Ready to start!** Choose actions for each agent below.
"""
    
    return status, get_current_state()

def get_current_state():
    """Get current city state as formatted string"""
    if env is None:
        return "Environment not initialized. Click 'Reset Environment' to start."
    
    rebel_status = ""
    if env.rebel_active:
        rebel_status = f"\n⚠️ **REBEL ACTIVE** (Strength: {env.city.rebel_strength:.1%})"
    
    crises = env.crisis_engine.get_active_crises()
    crisis_list = ", ".join([c.name for c in crises]) if crises else "None"
    
    state = f"""
📊 **Week {env.current_week}/{env.config.max_weeks}**

**City Metrics:**
- 🤝 Trust: {env.city.trust_score:.1%}
- ❤️ Survival: {env.city.survival_rate:.1%}
- 💰 GDP: {env.city.gdp_index:.2f}
- 💵 Budget: ${env.city.budget_remaining:,.0f}
- 🚨 Crime: {env.city.crime_index:.1%}
- 🏥 Hospital Capacity: {env.city.hospital_capacity:.1%}
- ⚡ Power Grid: {env.city.power_grid_health:.1%}

**Active Crises:** {crisis_list}
{rebel_status}

**Agent-Specific Objectives:**
- 👔 Mayor: Balance all governance aspects
- 🏥 Health Minister: Maximize survival & healthcare
- 💼 Finance Officer: Optimize economy & budget
- 👮 Police Chief: Minimize crime & maintain order
- 🏗️ Infrastructure Head: Maintain city systems
- 📢 Media Spokesperson: Maximize trust & communication
"""
    
    return state

def take_step(mayor_action, health_action, finance_action, police_action, infra_action, media_action):
    """Execute one step with agent actions"""
    global env, current_obs, episode_history
    
    if env is None:
        return "Environment not initialized!", "", ""
    
    if env.done:
        return "Episode finished! Reset to continue.", "", ""
    
    # Build actions dict
    actions = {
        "mayor": {"policy_decision": mayor_action, "reasoning": "User selected"},
        "health_minister": {"policy_decision": health_action, "reasoning": "User selected"},
        "finance_officer": {"policy_decision": finance_action, "reasoning": "User selected"},
        "police_chief": {"policy_decision": police_action, "reasoning": "User selected"},
        "infrastructure_head": {"policy_decision": infra_action, "reasoning": "User selected"},
        "media_spokesperson": {"policy_decision": media_action, "reasoning": "User selected"},
    }
    
    # Execute step
    current_obs, reward, done, info = env.step(actions)
    
    # Get agent-specific rewards
    agent_rewards = AgentSpecificRewards.get_all_rewards(env.city, actions)
    
    # Build result message
    result = f"""
✅ **Step {env.current_week} Complete**

**Actions Taken:**
- 👔 Mayor: {mayor_action}
- 🏥 Health: {health_action}
- 💼 Finance: {finance_action}
- 👮 Police: {police_action}
- 🏗️ Infrastructure: {infra_action}
- 📢 Media: {media_action}

**Agent-Specific Rewards:**
- 👔 Mayor: {agent_rewards['mayor']:.3f}
- 🏥 Health: {agent_rewards['health_minister']:.3f}
- 💼 Finance: {agent_rewards['finance_officer']:.3f}
- 👮 Police: {agent_rewards['police_chief']:.3f}
- 🏗️ Infrastructure: {agent_rewards['infrastructure_head']:.3f}
- 📢 Media: {agent_rewards['media_spokesperson']:.3f}

**Overall Reward:** {reward:.3f}
"""
    
    if info.get('new_crises'):
        result += f"\n🚨 **New Crises:** {', '.join(info['new_crises'])}"
    
    if env.rebel_active and env.rebel_spawn_week == env.current_week:
        result += f"\n\n⚠️ **REBEL AGENT SPAWNED!** Trust has been too low for too long."
    
    if done:
        result += f"\n\n🏁 **Episode Finished!**"
        if env.city.survival_rate < 0.5:
            result += " City collapsed!"
        elif env.city.rebel_strength > 0.9:
            result += " Rebel takeover!"
        else:
            result += " Episode complete!"
    
    episode_history.append({
        'week': env.current_week,
        'reward': reward,
        'trust': env.city.trust_score,
        'survival': env.city.survival_rate,
        'rebel_active': env.rebel_active
    })
    
    return result, get_current_state(), get_episode_chart()

def get_episode_chart():
    """Generate episode history chart"""
    if not episode_history:
        return None
    
    import matplotlib.pyplot as plt
    import io
    import base64
    
    weeks = [h['week'] for h in episode_history]
    trust = [h['trust'] for h in episode_history]
    survival = [h['survival'] for h in episode_history]
    rewards = [h['reward'] for h in episode_history]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot 1: Trust and Survival
    ax1.plot(weeks, trust, 'b-', label='Trust', linewidth=2)
    ax1.plot(weeks, survival, 'g-', label='Survival', linewidth=2)
    ax1.axhline(y=0.3, color='r', linestyle='--', label='Rebel Spawn Threshold')
    ax1.set_xlabel('Week')
    ax1.set_ylabel('Score')
    ax1.set_title('City Metrics Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Highlight rebel periods
    for i, h in enumerate(episode_history):
        if h['rebel_active']:
            ax1.axvspan(weeks[i]-0.5, weeks[i]+0.5, alpha=0.2, color='red')
    
    # Plot 2: Rewards
    ax2.plot(weeks, rewards, 'purple', linewidth=2)
    ax2.set_xlabel('Week')
    ax2.set_ylabel('Reward')
    ax2.set_title('Reward Over Time')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convert to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

def run_random_episode():
    """Run a full episode with random actions"""
    global env, current_obs, episode_history
    
    if env is None:
        return "Environment not initialized!", "", ""
    
    # Reset
    current_obs = env.reset()
    episode_history = []
    
    actions_list = {
        "mayor": ["hold", "emergency_budget_release", "invest_in_welfare", "reduce_tax"],
        "health_minister": ["hold", "mass_vaccination", "increase_hospital_staff"],
        "finance_officer": ["hold", "issue_bonds", "stimulus_package"],
        "police_chief": ["hold", "community_policing"],
        "infrastructure_head": ["hold", "emergency_repairs"],
        "media_spokesperson": ["hold", "press_conference", "social_media_campaign"],
    }
    
    steps = 0
    while not env.done and steps < env.config.max_weeks:
        actions = {
            agent_id: {
                "policy_decision": random.choice(actions_list[agent_id]),
                "reasoning": "Random"
            }
            for agent_id in env.AGENT_IDS
        }
        
        current_obs, reward, done, info = env.step(actions)
        
        episode_history.append({
            'week': env.current_week,
            'reward': reward,
            'trust': env.city.trust_score,
            'survival': env.city.survival_rate,
            'rebel_active': env.rebel_active
        })
        
        steps += 1
    
    result = f"""
🎲 **Random Episode Complete!**

**Final Results:**
- Episodes: {steps} weeks
- Final Trust: {env.city.trust_score:.1%}
- Final Survival: {env.city.survival_rate:.1%}
- Final GDP: {env.city.gdp_index:.2f}
- Rebel Spawned: {"Yes" if env.rebel_active else "No"}
- Average Reward: {sum(h['reward'] for h in episode_history) / len(episode_history):.3f}
"""
    
    return result, get_current_state(), get_episode_chart()

# Create Gradio interface
with gr.Blocks(title="CivicMind - Multi-Agent Governance", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏙️ CivicMind: Multi-Agent Governance Simulation
    
    **Meta × Hugging Face OpenEnv Hackathon 2025**
    
    A reinforcement learning environment where 6 AI agents govern a city through crises.
    
    ## 🎮 How to Use:
    1. **Configure** the environment (episode length, difficulty, rebel mechanic)
    2. **Reset** to start a new episode
    3. **Choose actions** for each agent
    4. **Step** through the simulation week by week
    5. **Watch** for the rebel agent to spawn when trust drops too low!
    
    ## 🤖 The Agents:
    - **👔 Mayor**: Balances all aspects of governance
    - **🏥 Health Minister**: Focuses on survival and healthcare
    - **💼 Finance Officer**: Optimizes economy and budget
    - **👮 Police Chief**: Maintains security and order
    - **🏗️ Infrastructure Head**: Manages city systems
    - **📢 Media Spokesperson**: Builds trust and communication
    
    ## ⚡ Unique Feature: Emergent Rebel Agent
    When trust drops below 30% for 2+ weeks, a rebel agent spawns and tries to overthrow the government!
    Only way to defeat it: restore trust above 55%.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Configuration")
            max_weeks = gr.Slider(10, 52, value=20, step=1, label="Episode Length (weeks)")
            difficulty = gr.Slider(1, 10, value=3, step=1, label="Difficulty")
            enable_rebel = gr.Checkbox(value=True, label="Enable Rebel Mechanic")
            reset_btn = gr.Button("🔄 Reset Environment", variant="primary")
            random_btn = gr.Button("🎲 Run Random Episode", variant="secondary")
        
        with gr.Column(scale=2):
            status_output = gr.Markdown("Click 'Reset Environment' to start!")
    
    gr.Markdown("### 🎮 Agent Actions")
    
    with gr.Row():
        mayor_action = gr.Dropdown(
            ["hold", "emergency_budget_release", "invest_in_welfare", "reduce_tax"],
            value="hold",
            label="👔 Mayor"
        )
        health_action = gr.Dropdown(
            ["hold", "mass_vaccination", "increase_hospital_staff"],
            value="hold",
            label="🏥 Health Minister"
        )
        finance_action = gr.Dropdown(
            ["hold", "issue_bonds", "stimulus_package"],
            value="hold",
            label="💼 Finance Officer"
        )
    
    with gr.Row():
        police_action = gr.Dropdown(
            ["hold", "community_policing"],
            value="hold",
            label="👮 Police Chief"
        )
        infra_action = gr.Dropdown(
            ["hold", "emergency_repairs"],
            value="hold",
            label="🏗️ Infrastructure"
        )
        media_action = gr.Dropdown(
            ["hold", "press_conference", "social_media_campaign"],
            value="hold",
            label="📢 Media"
        )
    
    step_btn = gr.Button("▶️ Execute Step", variant="primary", size="lg")
    
    with gr.Row():
        with gr.Column():
            step_result = gr.Markdown("Results will appear here...")
        with gr.Column():
            current_state = gr.Markdown("Current state will appear here...")
    
    episode_chart = gr.Plot(label="Episode Progress")
    
    gr.Markdown("""
    ---
    ## 📊 About This Project
    
    **CivicMind** is a multi-agent reinforcement learning environment covering all 5 OpenEnv hackathon themes:
    
    1. **Multi-Agent**: 6 government agents + emergent rebel agent
    2. **Long-Horizon**: 52-week episodes with compound effects
    3. **Professional Tasks**: Real-world governance decisions
    4. **Personal Tasks**: Citizen petitions with schema drift
    5. **Self-Improvement**: Auto-escalating difficulty
    
    **Training Results:**
    - Q-Learning: +18.4% reward improvement, +107% trust improvement
    - LLM Fine-Tuning: Each agent learns unique policies
    
    **Code**: [GitHub](https://github.com/YOUR_USERNAME/civicmind)
    """)
    
    # Event handlers
    reset_btn.click(
        reset_environment,
        inputs=[max_weeks, difficulty, enable_rebel],
        outputs=[status_output, current_state]
    )
    
    step_btn.click(
        take_step,
        inputs=[mayor_action, health_action, finance_action, police_action, infra_action, media_action],
        outputs=[step_result, current_state, episode_chart]
    )
    
    random_btn.click(
        run_random_episode,
        outputs=[step_result, current_state, episode_chart]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
