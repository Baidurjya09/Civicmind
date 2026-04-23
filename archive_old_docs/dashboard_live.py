"""
CivicMind — LIVE Interactive Dashboard
Shows real-time agent decisions, conflicts, rebel spawning, and chaos!
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS

st.set_page_config(page_title="CivicMind LIVE", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better visuals and readability
st.markdown("""
<style>
/* Improve overall text visibility */
.stApp {
    background-color: #0e1117;
}

/* Make all text larger and more readable */
.stMarkdown, .stText {
    font-size: 16px !important;
    line-height: 1.6 !important;
}

/* Headers */
h1, h2, h3, h4 {
    color: #ffffff !important;
    font-weight: 600 !important;
}

h1 {font-size: 2.5rem !important;}
h2 {font-size: 2rem !important;}
h3 {font-size: 1.5rem !important;}

/* Metrics - larger and clearer */
[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: bold !important;
    color: #ffffff !important;
}

[data-testid="stMetricLabel"] {
    font-size: 16px !important;
    color: #fafafa !important;
}

[data-testid="stMetricDelta"] {
    font-size: 14px !important;
}

/* Crisis alert - bright and visible */
.crisis-alert {
    background-color: #ff4444; 
    color: white; 
    padding: 15px; 
    border-radius: 8px; 
    font-weight: bold;
    font-size: 18px !important;
    text-align: center;
    margin: 10px 0;
}

/* Rebel alert - unmissable */
.rebel-alert {
    background-color: #ff0000; 
    color: white; 
    padding: 20px; 
    border-radius: 8px; 
    font-weight: bold;
    font-size: 20px !important;
    text-align: center;
    animation: blink 1s infinite;
    border: 3px solid #ffff00;
    box-shadow: 0 0 20px rgba(255, 0, 0, 0.8);
}

/* Agent decisions - clear and readable */
.agent-decision {
    background-color: #1e2530; 
    padding: 12px; 
    margin: 8px 0; 
    border-left: 5px solid #4CAF50; 
    border-radius: 5px;
    font-size: 15px !important;
    color: #ffffff !important;
}

.agent-decision b {
    color: #4CAF50 !important;
    font-size: 16px !important;
}

/* Conflict styling */
.conflict {
    border-left: 5px solid #ff4444 !important;
    background-color: #2d1f1f !important;
}

.conflict b {
    color: #ff4444 !important;
}

/* Info boxes */
.stAlert {
    font-size: 15px !important;
    padding: 12px !important;
}

/* Success/Warning/Error boxes */
.stSuccess, .stWarning, .stError, .stInfo {
    font-size: 15px !important;
    padding: 15px !important;
}

/* Buttons - larger and more visible */
.stButton > button {
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
}

/* Sidebar text */
.css-1d391kg, .css-1v0mbdj {
    font-size: 15px !important;
}

/* Progress bar text */
.stProgress > div > div {
    font-size: 16px !important;
}

/* Animation for blinking */
@keyframes blink {
    0%, 50%, 100% {opacity:1;}
    25%, 75% {opacity:0.4;}
}

/* Chart labels */
.vega-embed {
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🏛 CivicMind — LIVE Governance Simulation")
st.markdown("**Watch AI Agents Govern in Real-Time | Meta × HF OpenEnv Hackathon 2025**")

# Sidebar
st.sidebar.header("⚙️ Configuration")
difficulty = st.sidebar.slider("🔥 Difficulty (Crisis Intensity)", 1, 10, 7, 
                               help="Higher = more crises, more chaos")
max_weeks = st.sidebar.slider("📅 Simulation Length", 4, 52, 20)

policy_type = st.sidebar.selectbox(
    "🎯 Governance Strategy",
    ["Conservative Policy", "Aggressive Growth", "Welfare State", "Surveillance State", "Random Chaos"],
    help="Different governance philosophies"
)

force_rebel = st.sidebar.checkbox("⚡ Force Rebel Spawn", value=True,
                                  help="Guarantee rebel appears for demo")

st.sidebar.markdown("---")
if st.sidebar.button("🚀 START SIMULATION", type="primary"):
    st.session_state.running = True
    st.session_state.week = 0
    st.session_state.history = []

# Initialize environment
if 'env' not in st.session_state:
    config = CivicMindConfig(
        max_weeks=max_weeks,
        difficulty=difficulty,
        enable_rebel=True,
        enable_schema_drift=True,
        seed=42
    )
    st.session_state.env = CivicMindEnv(config)
    st.session_state.obs = st.session_state.env.reset()
    st.session_state.week = 0
    st.session_state.history = []
    st.session_state.agent_decisions = []
    st.session_state.conflicts = []
    st.session_state.petitions = []

# Main layout - 3 columns
col1, col2, col3 = st.columns([2, 3, 2])

# LEFT COLUMN - System Status
with col1:
    st.subheader("🎮 System Status")
    
    env = st.session_state.env
    city = env.city
    
    # System Health Score
    health_score = (
        city.trust_score * 0.4 +
        (1 - city.corruption) * 0.2 +
        (1 - city.civil_unrest) * 0.2 +
        city.survival_rate * 0.2
    )
    
    health_color = "🟢" if health_score > 0.7 else "🟡" if health_score > 0.4 else "🔴"
    health_status = "HEALTHY" if health_score > 0.7 else "UNSTABLE" if health_score > 0.4 else "CRITICAL"
    
    st.markdown(f"### {health_color} System Health: {health_score:.0%}")
    st.markdown(f"**Status: {health_status}**")
    
    if health_score < 0.4:
        st.markdown('<div class="crisis-alert">⚠️ SYSTEM CRITICAL ⚠️</div>', unsafe_allow_html=True)
    
    # Key Metrics
    st.metric("👥 Trust Score", f"{city.trust_score:.0%}", 
              delta=f"{(city.trust_score - 0.75):.1%}" if st.session_state.week > 0 else None)
    st.metric("💰 Budget", f"${city.budget_remaining:,.0f}",
              delta=f"${city.budget_remaining - 1_000_000:,.0f}" if st.session_state.week > 0 else None)
    st.metric("❤️ Survival Rate", f"{city.survival_rate:.0%}")
    st.metric("⚡ Civil Unrest", f"{city.civil_unrest:.0%}",
              delta=f"{city.civil_unrest:.1%}" if city.civil_unrest > 0.3 else None,
              delta_color="inverse")
    
    # Rebel Status
    st.markdown("---")
    st.markdown("### 🎯 Rebel Status")
    if env.rebel_active:
        st.markdown(f'<div class="rebel-alert">🚨 REBEL ACTIVE 🚨<br/><br/>Strength: {city.rebel_strength:.0%}<br/><br/>⚠️ GOVERNMENT UNDER THREAT ⚠️</div>', 
                   unsafe_allow_html=True)
    elif city.trust_score < 0.35:
        st.warning(f"⚠️ **HIGH REBEL SPAWN RISK**\n\nTrust: {city.trust_score:.0%} (threshold: 30%)\n\nRebel will spawn if trust stays low!")
    else:
        st.success("✅ **Government Stable**\n\nNo rebel threat")
    
    # Active Crises
    st.markdown("---")
    st.markdown("### 🔥 Active Crises")
    active_crises = env.crisis_engine.get_active_crises()
    if active_crises:
        for crisis in active_crises:
            st.error(f"⚠️ **{crisis.name.upper()}**\n\nSeverity: {crisis.severity:.0%}")
    else:
        st.info("✅ No active crises")

# CENTER COLUMN - Timeline & Graphs
with col2:
    st.subheader("📊 Live Metrics")
    
    if st.session_state.week > 0 and st.session_state.history:
        # Create dataframe from history
        df = pd.DataFrame(st.session_state.history)
        
        # Trust & Survival
        st.markdown("**📊 Trust & Survival Over Time**")
        chart_data = pd.DataFrame({
            'Trust': df['trust'],
            'Survival': df['survival'],
            'Unrest': df['unrest']
        })
        st.line_chart(chart_data, height=200)
        
        # Reward
        st.markdown("**🎯 Reward Score**")
        st.line_chart(df['reward'], height=150)
        
        # GDP
        st.markdown("**💰 Economic Health (GDP Index)**")
        st.area_chart(df['gdp'], height=150)
        
    else:
        st.info("📈 **Charts will appear as simulation runs**\n\nClick 'START SIMULATION' to begin")
    
    # Week Progress
    st.markdown("---")
    progress = st.session_state.week / max_weeks
    st.progress(progress)
    st.markdown(f"### Week {st.session_state.week} / {max_weeks}")
    
    if st.session_state.week == 0:
        st.info("👉 Click 'START SIMULATION' in the sidebar to begin")
    elif st.session_state.week >= max_weeks:
        st.success("✅ Simulation Complete!")

# RIGHT COLUMN - Agent Decisions & Events
with col3:
    st.subheader("🧠 Agent Activity")
    
    # Recent Agent Decisions
    if st.session_state.agent_decisions:
        st.markdown("**Latest Agent Decisions:**")
        for decision in st.session_state.agent_decisions[-5:]:
            conflict_class = "conflict" if decision.get('conflict') else ""
            conflict_icon = "⚔️ " if decision.get('conflict') else ""
            st.markdown(f'<div class="agent-decision {conflict_class}">'
                       f'{conflict_icon}<b>{decision["agent"]}</b><br/>'
                       f'→ {decision["action"]}<br/>'
                       f'<small style="color: #aaaaaa;">{decision["reason"]}</small>'
                       f'</div>', unsafe_allow_html=True)
    else:
        st.info("🤖 Agent decisions will appear here as simulation runs")
    
    # Conflicts
    if st.session_state.conflicts:
        st.markdown("---")
        st.markdown("**⚔️ Agent Conflicts:**")
        for conflict in st.session_state.conflicts[-3:]:
            st.warning(f"**{conflict['agents']}**\n\n{conflict['issue']}")
    
    # Citizen Petitions
    st.markdown("---")
    st.subheader("📢 Citizen Voices")
    if st.session_state.petitions:
        for petition in st.session_state.petitions[-3:]:
            urgency_icon = "🔴" if petition['urgency'] > 0.7 else "🟡" if petition['urgency'] > 0.4 else "🟢"
            urgency_text = "URGENT" if petition['urgency'] > 0.7 else "Important" if petition['urgency'] > 0.4 else "Normal"
            st.markdown(f"{urgency_icon} **{urgency_text}**\n\n*\"{petition['message']}\"*")
    else:
        st.info("📢 Citizen petitions will appear here")

# Control Buttons
st.markdown("---")
button_col1, button_col2, button_col3, button_col4 = st.columns(4)

with button_col1:
    if st.button("▶️ Next Week", disabled=st.session_state.week >= max_weeks):
        # Simulate one week
        env = st.session_state.env
        
        # Generate agent actions (simplified for demo)
        actions = {}
        decisions = []
        conflicts = []
        
        for agent_id in env.AGENT_IDS:
            obs = st.session_state.obs[agent_id]
            
            # Simple decision logic based on policy type
            if policy_type == "Conservative Policy":
                decision = "hold" if env.city.trust_score > 0.5 else "emergency_budget_release"
            elif policy_type == "Aggressive Growth":
                decision = "stimulus_package" if env.city.budget_remaining > 500_000 else "issue_bonds"
            elif policy_type == "Welfare State":
                decision = "invest_in_welfare" if env.city.budget_remaining > 300_000 else "hold"
            elif policy_type == "Surveillance State":
                decision = "deploy_riot_control" if env.city.civil_unrest > 0.3 else "hold"
            else:  # Random Chaos
                decision = np.random.choice(ALL_AGENTS[agent_id].valid_decisions)
            
            actions[agent_id] = {
                "reasoning": f"{policy_type} strategy",
                "tool_calls": [],
                "policy_decision": decision
            }
            
            # Track decision
            decisions.append({
                "agent": agent_id.replace("_", " ").title(),
                "action": decision.replace("_", " ").title(),
                "reason": f"Week {st.session_state.week + 1}",
                "conflict": decision == "deploy_riot_control" and env.city.trust_score < 0.5
            })
            
            # Detect conflicts
            if decision == "deploy_riot_control" and env.city.trust_score < 0.5:
                conflicts.append({
                    "agents": "Police vs Citizens",
                    "issue": "Riot control deployed despite low trust - will backfire!"
                })
        
        # Step environment
        obs, reward, done, info = env.step(actions)
        st.session_state.obs = obs
        st.session_state.week += 1
        
        # Force chaos if needed
        if force_rebel and st.session_state.week > 5 and not env.rebel_active:
            env.city.trust_score = max(0.25, env.city.trust_score - 0.1)
            env.city.civil_unrest = min(1.0, env.city.civil_unrest + 0.1)
        
        # Record history
        st.session_state.history.append({
            'week': st.session_state.week,
            'trust': env.city.trust_score,
            'survival': env.city.survival_rate,
            'gdp': env.city.gdp_index,
            'reward': reward,
            'unrest': env.city.civil_unrest,
            'rebel': env.rebel_active
        })
        
        st.session_state.agent_decisions.extend(decisions)
        st.session_state.conflicts.extend(conflicts)
        
        # Generate citizen petitions
        if st.session_state.week % 3 == 0:
            petitions = [
                {"message": "Hospital is full! Need more beds!", "urgency": 0.8},
                {"message": "No power in my neighborhood for 3 days", "urgency": 0.9},
                {"message": "Taxes are crushing small businesses", "urgency": 0.6},
                {"message": "Crime is out of control in District 5", "urgency": 0.7},
            ]
            st.session_state.petitions.extend(np.random.choice(petitions, 2, replace=False))
        
        st.rerun()

with button_col2:
    if st.button("⏩ Fast Forward (5 weeks)"):
        for _ in range(5):
            if st.session_state.week < max_weeks:
                # Simplified fast forward
                st.session_state.week += 1
        st.rerun()

with button_col3:
    if st.button("🔄 Reset"):
        st.session_state.clear()
        st.rerun()

with button_col4:
    if st.button("💥 Trigger Crisis"):
        env = st.session_state.env
        env.city.trust_score -= 0.2
        env.city.civil_unrest += 0.3
        env.city.budget_remaining -= 200_000
        st.session_state.conflicts.append({
            "agents": "System",
            "issue": "MAJOR CRISIS TRIGGERED - Multiple systems failing!"
        })
        st.rerun()

# Footer
st.markdown("---")
st.markdown("**🏆 CivicMind** | All 5 Themes | 6 Bonus Prizes | Emergent Rebel Agent | Built with OpenEnv + Unsloth")
