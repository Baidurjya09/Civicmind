"""
CivicMind — AI GOVERNANCE CONTROL ROOM
The winning UI design - makes judges feel they're watching a real system under pressure
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS

st.set_page_config(page_title="CivicMind Control Room", layout="wide", initial_sidebar_state="collapsed")

# CONTROL ROOM STYLING
st.markdown("""
<style>
/* Dark control room theme */
.stApp {
    background-color: #0a0e1a;
    color: #e0e0e0;
}

/* Headers */
h1, h2, h3 {
    color: #ffffff !important;
    font-family: 'Courier New', monospace !important;
    letter-spacing: 1px;
}

/* Metrics - larger and clearer */
[data-testid="stMetricValue"] {
    font-size: 32px !important;
    font-weight: bold !important;
    font-family: 'Courier New', monospace !important;
}

[data-testid="stMetricLabel"] {
    font-size: 14px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Status indicators */
.status-stable {
    background: linear-gradient(90deg, #00ff00 0%, #00cc00 100%);
    color: #000;
    padding: 15px;
    border-radius: 5px;
    font-weight: bold;
    font-size: 20px;
    text-align: center;
    margin: 10px 0;
}

.status-strained {
    background: linear-gradient(90deg, #ffaa00 0%, #ff8800 100%);
    color: #000;
    padding: 15px;
    border-radius: 5px;
    font-weight: bold;
    font-size: 20px;
    text-align: center;
    margin: 10px 0;
}

.status-critical {
    background: linear-gradient(90deg, #ff0000 0%, #cc0000 100%);
    color: #fff;
    padding: 15px;
    border-radius: 5px;
    font-weight: bold;
    font-size: 20px;
    text-align: center;
    margin: 10px 0;
    animation: pulse 1.5s infinite;
}

/* Rebel alert - unmissable */
.rebel-active {
    background: linear-gradient(45deg, #ff0000, #ff6600, #ff0000);
    background-size: 200% 200%;
    animation: gradient 2s ease infinite, pulse 1s infinite;
    color: #fff;
    padding: 25px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 24px;
    text-align: center;
    border: 4px solid #ffff00;
    box-shadow: 0 0 30px rgba(255, 0, 0, 0.8);
    margin: 15px 0;
}

/* Agent decision cards */
.agent-card {
    background-color: #1a1f2e;
    border-left: 4px solid #00ff00;
    padding: 12px;
    margin: 8px 0;
    border-radius: 5px;
    font-family: 'Courier New', monospace;
}

.agent-card-conflict {
    border-left: 4px solid #ff0000;
    background-color: #2e1a1a;
}

.agent-name {
    color: #00ff00;
    font-weight: bold;
    font-size: 16px;
}

.agent-action {
    color: #ffffff;
    font-size: 14px;
    margin: 5px 0;
}

.agent-reason {
    color: #888888;
    font-size: 12px;
    font-style: italic;
}

/* System log */
.log-entry {
    background-color: #0f1419;
    border-left: 3px solid #00aaff;
    padding: 10px;
    margin: 5px 0;
    font-family: 'Courier New', monospace;
    font-size: 13px;
}

.log-crisis {
    border-left: 3px solid #ff0000;
}

.log-rebel {
    border-left: 3px solid #ff6600;
    background-color: #1a0f0f;
}

/* Petition cards */
.petition-urgent {
    background-color: #2e1a1a;
    border-left: 4px solid #ff0000;
    padding: 10px;
    margin: 5px 0;
    border-radius: 3px;
}

.petition-important {
    background-color: #2e2a1a;
    border-left: 4px solid #ffaa00;
    padding: 10px;
    margin: 5px 0;
    border-radius: 3px;
}

.petition-normal {
    background-color: #1a2e1a;
    border-left: 4px solid #00ff00;
    padding: 10px;
    margin: 5px 0;
    border-radius: 3px;
}

/* Buttons */
.stButton > button {
    font-family: 'Courier New', monospace !important;
    font-weight: bold !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-radius: 5px !important;
    padding: 12px 24px !important;
}

/* Animations */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* System health bar */
.health-bar {
    background-color: #1a1f2e;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin: 15px 0;
}

.health-score {
    font-size: 48px;
    font-weight: bold;
    font-family: 'Courier New', monospace;
}

.health-green { color: #00ff00; }
.health-yellow { color: #ffaa00; }
.health-red { color: #ff0000; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'env' not in st.session_state:
    st.session_state.env = None
    st.session_state.obs = None
    st.session_state.week = 0
    st.session_state.history = []
    st.session_state.agent_decisions = []
    st.session_state.conflicts = []
    st.session_state.petitions = []
    st.session_state.system_log = []
    st.session_state.running = False

# HEADER
st.markdown("# 🏛 CIVICMIND — AI GOVERNANCE CONTROL ROOM")
st.markdown("**Meta × Hugging Face OpenEnv Hackathon 2025 | Live Multi-Agent System**")
st.markdown("---")

# MAIN LAYOUT - 3 COLUMNS
col_control, col_city, col_intel = st.columns([1, 2, 1])

# ============================================================================
# LEFT PANEL - CONTROL SYSTEM
# ============================================================================
with col_control:
    st.markdown("### 🎛 CONTROL PANEL")
    
    # Configuration
    difficulty = st.slider("🔥 Difficulty", 1, 10, 8, help="Crisis intensity")
    max_weeks = st.slider("📅 Weeks", 4, 52, 20)
    
    policy_mode = st.selectbox(
        "🎯 Policy Mode",
        ["RL Policy", "Conservative", "Welfare State", "Surveillance State", "Random Chaos"]
    )
    
    force_rebel = st.checkbox("⚡ Force Rebel Spawn", value=True, 
                              help="Guarantee rebel appears")
    
    stress_test = st.checkbox("⚠️ Stress Test Mode", value=False,
                             help="Auto-inject chaos every 3 weeks")
    
    st.markdown("---")
    
    # Control buttons
    if st.button("🚀 RUN SIMULATION", type="primary", use_container_width=True):
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
        st.session_state.system_log = [{"week": 0, "event": "🚀 SYSTEM INITIALIZED", "type": "system"}]
        st.session_state.running = True
        st.rerun()
    
    if st.button("💥 INJECT CRISIS", use_container_width=True, disabled=st.session_state.env is None):
        if st.session_state.env:
            st.session_state.env.city.trust_score -= 0.2
            st.session_state.env.city.civil_unrest += 0.3
            st.session_state.env.city.budget_remaining -= 200_000
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": "💥 MAJOR CRISIS INJECTED - Multiple systems failing",
                "type": "crisis"
            })
            st.rerun()
    
    if st.button("🔥 SPAWN REBEL NOW", use_container_width=True, disabled=st.session_state.env is None):
        if st.session_state.env:
            st.session_state.env.rebel_active = True
            st.session_state.env.city.rebel_strength = 0.35
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": "🔥 REBEL AGENT SPAWNED - Government under threat",
                "type": "rebel"
            })
            st.rerun()
    
    st.markdown("---")
    
    # System info
    if st.session_state.env:
        st.markdown("**📊 SYSTEM STATUS**")
        st.markdown(f"Week: **{st.session_state.week}/{max_weeks}**")
        st.markdown(f"Agents: **6 Active**")
        st.markdown(f"Mode: **{policy_mode}**")

# ============================================================================
# CENTER PANEL - CITY CORE
# ============================================================================
with col_city:
    st.markdown("### 🌆 CITY CORE")
    
    if st.session_state.env:
        city = st.session_state.env.city
        
        # System status bar
        health_score = (
            city.trust_score * 0.4 +
            (1 - city.corruption) * 0.2 +
            (1 - city.civil_unrest) * 0.2 +
            city.survival_rate * 0.2
        )
        
        if health_score > 0.7:
            st.markdown('<div class="status-stable">🟢 SYSTEM STABLE</div>', unsafe_allow_html=True)
        elif health_score > 0.4:
            st.markdown('<div class="status-strained">🟡 SYSTEM STRAINED</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-critical">🔴 SYSTEM CRITICAL</div>', unsafe_allow_html=True)
        
        # Main metrics - 2 rows of 3
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric("💰 GDP", f"${city.gdp_index * 1_000_000:,.0f}", 
                     delta=f"{(city.gdp_index - 1.0) * 100:.1f}%")
        with metric_col2:
            st.metric("👥 Trust", f"{city.trust_score:.0%}",
                     delta=f"{(city.trust_score - 0.75) * 100:.0f}%",
                     delta_color="normal")
        with metric_col3:
            st.metric("⚡ Unrest", f"{city.civil_unrest:.0%}",
                     delta=f"{city.civil_unrest * 100:.0f}%",
                     delta_color="inverse")
        
        metric_col4, metric_col5, metric_col6 = st.columns(3)
        
        with metric_col4:
            st.metric("🕵️ Corruption", f"{city.corruption:.0%}")
        with metric_col5:
            st.metric("❤️ Survival", f"{city.survival_rate:.0%}")
        with metric_col6:
            st.metric("💵 Budget", f"${city.budget_remaining:,.0f}")
        
        # System health score - BIG
        health_color = "health-green" if health_score > 0.7 else "health-yellow" if health_score > 0.4 else "health-red"
        health_trend = "↑ Rising" if len(st.session_state.history) > 1 and health_score > st.session_state.history[-1].get('health', 0) else "↓ Declining" if len(st.session_state.history) > 1 else "—"
        
        st.markdown(f'''
        <div class="health-bar">
            <div style="font-size: 16px; color: #888;">🧬 SYSTEM HEALTH</div>
            <div class="health-score {health_color}">{health_score:.0%}</div>
            <div style="font-size: 18px; margin-top: 10px;">{health_trend}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Graphs
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            
            # Trust vs Unrest
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=df['week'], y=df['trust'], name='Trust', 
                                     line=dict(color='#00ff00', width=3)))
            fig1.add_trace(go.Scatter(x=df['week'], y=df['unrest'], name='Unrest',
                                     line=dict(color='#ff0000', width=3)))
            fig1.update_layout(
                title="Trust vs Unrest",
                template="plotly_dark",
                height=200,
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # GDP Trend
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df['week'], y=df['gdp'], 
                                     fill='tozeroy', line=dict(color='#00aaff', width=2)))
            fig2.update_layout(
                title="Economic Health (GDP Index)",
                template="plotly_dark",
                height=150,
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Active crises
        st.markdown("**🚨 ACTIVE CRISES**")
        active_crises = st.session_state.env.crisis_engine.get_active_crises()
        if active_crises:
            for crisis in active_crises:
                st.error(f"⚡ **{crisis.name.upper()}** | Severity: {crisis.severity:.0%}")
        else:
            st.success("✅ No active crises")
    
    else:
        st.info("👈 Click **RUN SIMULATION** to start")

# ============================================================================
# RIGHT PANEL - INTELLIGENCE VIEW
# ============================================================================
with col_intel:
    st.markdown("### 🧠 INTELLIGENCE PANEL")
    
    if st.session_state.env:
        # Rebel status - TOP PRIORITY
        st.markdown("**🔥 REBEL STATUS**")
        if st.session_state.env.rebel_active:
            rebel_strength = st.session_state.env.city.rebel_strength
            st.markdown(f'''
            <div class="rebel-active">
                🚨 REBEL ACTIVE 🚨<br/><br/>
                Strength: {rebel_strength:.0%}<br/>
                Influence: {"CRITICAL" if rebel_strength > 0.7 else "RISING"}<br/><br/>
                ⚠️ GOVERNMENT UNDER THREAT ⚠️
            </div>
            ''', unsafe_allow_html=True)
        else:
            trust = st.session_state.env.city.trust_score
            if trust < 0.35:
                st.warning(f"⚠️ **HIGH RISK**\n\nTrust: {trust:.0%}\nRebel spawn imminent!")
            else:
                st.success(f"✅ **STABLE**\n\nTrust: {trust:.0%}")
        
        st.markdown("---")
        
        # Agent decisions
        st.markdown("**🤖 AGENT DECISIONS**")
        if st.session_state.agent_decisions:
            for decision in st.session_state.agent_decisions[-5:]:
                card_class = "agent-card-conflict" if decision.get('conflict') else "agent-card"
                conflict_icon = "⚔️ " if decision.get('conflict') else ""
                st.markdown(f'''
                <div class="{card_class}">
                    <div class="agent-name">{conflict_icon}{decision["agent"]}</div>
                    <div class="agent-action">→ {decision["action"]}</div>
                    <div class="agent-reason">{decision["reason"]}</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("Waiting for agent decisions...")
        
        st.markdown("---")
        
        # Citizen voices
        st.markdown("**📢 CITIZEN VOICES**")
        if st.session_state.petitions:
            for petition in st.session_state.petitions[-3:]:
                urgency = petition['urgency']
                if urgency > 0.7:
                    st.markdown(f'''
                    <div class="petition-urgent">
                        🔴 <b>URGENT</b><br/>
                        "{petition['message']}"
                    </div>
                    ''', unsafe_allow_html=True)
                elif urgency > 0.4:
                    st.markdown(f'''
                    <div class="petition-important">
                        🟡 <b>Important</b><br/>
                        "{petition['message']}"
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="petition-normal">
                        🟢 <b>Normal</b><br/>
                        "{petition['message']}"
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.info("No petitions yet")
        
        st.markdown("---")
        
        # System alerts
        st.markdown("**⚠️ SYSTEM ALERTS**")
        alerts = []
        if st.session_state.env.city.trust_score < 0.4:
            alerts.append("🔴 Trust critically low")
        if st.session_state.env.city.civil_unrest > 0.6:
            alerts.append("🔴 Unrest dangerously high")
        if st.session_state.env.city.budget_remaining < 200_000:
            alerts.append("🟡 Budget deficit critical")
        if st.session_state.env.city.corruption > 0.5:
            alerts.append("🟡 Corruption spreading")
        
        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("✅ All systems nominal")
    
    else:
        st.info("Awaiting system initialization")

# ============================================================================
# BOTTOM PANEL - LIVE SYSTEM FEED
# ============================================================================
st.markdown("---")
st.markdown("### 📜 LIVE SYSTEM FEED")

if st.session_state.system_log:
    # Show last 10 entries
    for entry in st.session_state.system_log[-10:][::-1]:
        log_class = "log-crisis" if entry['type'] == 'crisis' else "log-rebel" if entry['type'] == 'rebel' else "log-entry"
        st.markdown(f'''
        <div class="{log_class}">
            <b>Week {entry['week']}</b> | {entry['event']}
        </div>
        ''', unsafe_allow_html=True)
else:
    st.info("System log will appear here")

# ============================================================================
# CONTROL BUTTONS (Bottom)
# ============================================================================
st.markdown("---")
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

with btn_col1:
    if st.button("▶️ NEXT WEEK", disabled=st.session_state.env is None or st.session_state.week >= max_weeks):
        if st.session_state.env:
            # Simulate one week
            env = st.session_state.env
            
            # Generate agent actions
            actions = {}
            decisions = []
            
            for agent_id in env.AGENT_IDS:
                # Simple policy logic
                if policy_mode == "Conservative":
                    decision = "hold" if env.city.trust_score > 0.5 else "emergency_budget_release"
                elif policy_mode == "Welfare State":
                    decision = "invest_in_welfare"
                elif policy_mode == "Surveillance State":
                    decision = "deploy_riot_control" if env.city.civil_unrest > 0.3 else "hold"
                else:
                    decision = np.random.choice(ALL_AGENTS[agent_id].valid_decisions)
                
                actions[agent_id] = {
                    "reasoning": f"{policy_mode} strategy",
                    "tool_calls": [],
                    "policy_decision": decision
                }
                
                decisions.append({
                    "agent": agent_id.replace("_", " ").title(),
                    "action": decision.replace("_", " ").title(),
                    "reason": f"Week {st.session_state.week + 1}: {policy_mode}",
                    "conflict": decision == "deploy_riot_control" and env.city.trust_score < 0.5
                })
            
            # Step environment
            obs, reward, done, info = env.step(actions)
            st.session_state.obs = obs
            st.session_state.week += 1
            
            # Force rebel if enabled
            if force_rebel and st.session_state.week > 5 and not env.rebel_active:
                env.city.trust_score = max(0.25, env.city.trust_score - 0.05)
                env.city.civil_unrest = min(1.0, env.city.civil_unrest + 0.05)
            
            # Stress test mode
            if stress_test and st.session_state.week % 3 == 0:
                env.city.trust_score -= 0.1
                env.city.civil_unrest += 0.15
                st.session_state.system_log.append({
                    "week": st.session_state.week,
                    "event": "⚠️ STRESS TEST: Auto-chaos injected",
                    "type": "crisis"
                })
            
            # Record history
            health_score = (
                env.city.trust_score * 0.4 +
                (1 - env.city.corruption) * 0.2 +
                (1 - env.city.civil_unrest) * 0.2 +
                env.city.survival_rate * 0.2
            )
            
            st.session_state.history.append({
                'week': st.session_state.week,
                'trust': env.city.trust_score,
                'survival': env.city.survival_rate,
                'gdp': env.city.gdp_index,
                'reward': reward,
                'unrest': env.city.civil_unrest,
                'rebel': env.rebel_active,
                'health': health_score
            })
            
            st.session_state.agent_decisions.extend(decisions)
            
            # Generate petitions
            if st.session_state.week % 3 == 0:
                petitions = [
                    {"message": "Hospital is full! Need more beds!", "urgency": 0.9},
                    {"message": "No power for 3 days in District 5", "urgency": 0.85},
                    {"message": "Taxes are crushing small businesses", "urgency": 0.6},
                    {"message": "Crime is out of control", "urgency": 0.75},
                    {"message": "We need better schools", "urgency": 0.4},
                ]
                selected = np.random.choice(len(petitions), 2, replace=False)
                st.session_state.petitions.extend([petitions[i] for i in selected])
            
            # System log
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": f"Week {st.session_state.week} completed | Trust: {env.city.trust_score:.0%} | Unrest: {env.city.civil_unrest:.0%}",
                "type": "system"
            })
            
            # Check for rebel spawn
            if env.rebel_active and st.session_state.week > 0:
                if not any(log['type'] == 'rebel' for log in st.session_state.system_log[-3:]):
                    st.session_state.system_log.append({
                        "week": st.session_state.week,
                        "event": f"🔥 REBEL AGENT SPAWNED | Strength: {env.city.rebel_strength:.0%}",
                        "type": "rebel"
                    })
            
            st.rerun()

with btn_col2:
    if st.button("⏩ FAST FORWARD", disabled=st.session_state.env is None):
        # Advance 5 weeks
        for _ in range(min(5, max_weeks - st.session_state.week)):
            if st.session_state.week < max_weeks:
                st.session_state.week += 1
        st.rerun()

with btn_col3:
    if st.button("🔄 RESET SYSTEM"):
        st.session_state.clear()
        st.rerun()

with btn_col4:
    st.markdown(f"**Week {st.session_state.week}/{max_weeks}**")

# Footer
st.markdown("---")
st.markdown("**🏆 CivicMind Control Room** | All 5 Themes | 6 Bonus Prizes | Emergent AI Governance | Meta × HF OpenEnv Hackathon 2025")
