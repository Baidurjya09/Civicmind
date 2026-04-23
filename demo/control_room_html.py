"""
CivicMind — Professional HTML Control Room
Standalone HTML UI served by Streamlit, connected to real backend
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
import numpy as np
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS

st.set_page_config(page_title="CivicMind Control Room", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state
if 'env' not in st.session_state:
    st.session_state.env = None
    st.session_state.obs = None
    st.session_state.week = 0
    st.session_state.history = []
    st.session_state.agent_decisions = []
    st.session_state.system_log = []
    st.session_state.running = False
    st.session_state.max_weeks = 20
    st.session_state.difficulty = 8
    st.session_state.policy_mode = "Conservative"
    st.session_state.force_rebel = True

# Read HTML file
html_file = Path(__file__).parent / "control_room.html"

if not html_file.exists():
    st.error("control_room.html not found!")
    st.stop()

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Prepare state data for HTML
if st.session_state.env:
    city = st.session_state.env.city
    
    # Calculate health score
    health_score = (
        city.trust_score * 0.4 +
        (1 - city.corruption) * 0.2 +
        (1 - city.civil_unrest) * 0.2 +
        city.survival_rate * 0.2
    )
    
    # Health trend
    if len(st.session_state.history) > 1:
        prev_health = st.session_state.history[-1].get('health', health_score)
        health_trend = "↑ Rising" if health_score > prev_health else "↓ Declining"
    else:
        health_trend = "▶ STABLE"
    
    # Get active crises
    active_crises = [c.name.upper() for c in st.session_state.env.crisis_engine.get_active_crises()]
    
    # Format agent decisions
    agents_display = []
    if st.session_state.agent_decisions:
        for decision in st.session_state.agent_decisions[-6:]:
            agents_display.append({
                "name": decision["agent"],
                "action": decision["action"]
            })
    
    state_data = {
        "week": st.session_state.week,
        "max_weeks": st.session_state.max_weeks,
        "health": health_score,
        "health_trend": health_trend,
        "trust": city.trust_score,
        "unrest": city.civil_unrest,
        "gdp": city.gdp_index,
        "survival": city.survival_rate,
        "crises": active_crises,
        "agents": agents_display,
        "rebel_active": st.session_state.env.rebel_active,
        "rebel_strength": city.rebel_strength,
        "log": st.session_state.system_log
    }
    
    # Inject state into HTML
    state_json = json.dumps(state_data)
    html_with_state = html_content.replace(
        "console.log('CivicMind Control Room loaded - waiting for backend data');",
        f"console.log('CivicMind Control Room loaded - waiting for backend data');\nupdateUI({state_json});"
    )
else:
    # Initial state
    state_data = {
        "week": 0,
        "max_weeks": 20,
        "health": 0.82,
        "health_trend": "▶ STABLE",
        "trust": 0.75,
        "unrest": 0.20,
        "gdp": 1.00,
        "survival": 1.00,
        "crises": [],
        "agents": [{"name": "Mayor", "action": "Monitoring situation"}],
        "rebel_active": False,
        "rebel_strength": 0,
        "log": [{"week": 0, "event": "System initialized"}]
    }
    state_json = json.dumps(state_data)
    html_with_state = html_content.replace(
        "console.log('CivicMind Control Room loaded - waiting for backend data');",
        f"console.log('CivicMind Control Room loaded - waiting for backend data');\nupdateUI({state_json});"
    )

# Display HTML
components.html(html_with_state, height=700, scrolling=False)

# Control buttons below HTML
st.markdown("---")
st.markdown("### 🎛 CONTROL PANEL")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🚀 RUN SIMULATION", type="primary", use_container_width=True):
        config = CivicMindConfig(
            max_weeks=st.session_state.max_weeks,
            difficulty=st.session_state.difficulty,
            enable_rebel=True,
            enable_schema_drift=True,
            seed=42
        )
        st.session_state.env = CivicMindEnv(config)
        st.session_state.obs = st.session_state.env.reset()
        st.session_state.week = 0
        st.session_state.history = []
        st.session_state.agent_decisions = []
        st.session_state.system_log = [{"week": 0, "event": "🚀 SYSTEM INITIALIZED"}]
        st.session_state.running = True
        st.rerun()

with col2:
    if st.button("▶️ NEXT WEEK", disabled=st.session_state.env is None, use_container_width=True):
        if st.session_state.env:
            env = st.session_state.env
            
            # Generate agent actions
            actions = {}
            decisions = []
            
            for agent_id in env.AGENT_IDS:
                # Simple policy logic
                if st.session_state.policy_mode == "Conservative":
                    decision = "hold" if env.city.trust_score > 0.5 else "emergency_budget_release"
                elif st.session_state.policy_mode == "Welfare State":
                    decision = "invest_in_welfare"
                elif st.session_state.policy_mode == "Surveillance State":
                    decision = "deploy_riot_control" if env.city.civil_unrest > 0.3 else "hold"
                else:
                    decision = np.random.choice(ALL_AGENTS[agent_id].valid_decisions)
                
                actions[agent_id] = {
                    "reasoning": f"{st.session_state.policy_mode} strategy",
                    "tool_calls": [],
                    "policy_decision": decision
                }
                
                decisions.append({
                    "agent": agent_id.replace("_", " ").title(),
                    "action": decision.replace("_", " ").title(),
                })
            
            # Step environment
            obs, reward, done, info = env.step(actions)
            st.session_state.obs = obs
            st.session_state.week += 1
            
            # Force rebel if enabled
            if st.session_state.force_rebel and st.session_state.week > 5 and not env.rebel_active:
                env.city.trust_score = max(0.25, env.city.trust_score - 0.05)
                env.city.civil_unrest = min(1.0, env.city.civil_unrest + 0.05)
            
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
            
            # System log
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": f"Week completed | Trust: {env.city.trust_score:.0%} | Unrest: {env.city.civil_unrest:.0%}"
            })
            
            # Check for rebel spawn
            if env.rebel_active and st.session_state.week > 0:
                if not any(log.get('event', '').startswith('🔥') for log in st.session_state.system_log[-3:]):
                    st.session_state.system_log.append({
                        "week": st.session_state.week,
                        "event": f"🔥 REBEL AGENT SPAWNED | Strength: {env.city.rebel_strength:.0%}"
                    })
            
            st.rerun()

with col3:
    if st.button("💥 INJECT CRISIS", disabled=st.session_state.env is None, use_container_width=True):
        if st.session_state.env:
            st.session_state.env.city.trust_score -= 0.2
            st.session_state.env.city.civil_unrest += 0.3
            st.session_state.env.city.budget_remaining -= 200_000
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": "💥 MAJOR CRISIS INJECTED"
            })
            st.rerun()

with col4:
    if st.button("🔥 SPAWN REBEL", disabled=st.session_state.env is None, use_container_width=True):
        if st.session_state.env:
            st.session_state.env.rebel_active = True
            st.session_state.env.city.rebel_strength = 0.35
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": "🔥 REBEL AGENT SPAWNED"
            })
            st.rerun()

# Settings
st.markdown("---")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    st.session_state.difficulty = st.slider("🔥 Difficulty", 1, 10, st.session_state.difficulty)

with col_s2:
    st.session_state.max_weeks = st.slider("📅 Weeks", 4, 52, st.session_state.max_weeks)

with col_s3:
    st.session_state.policy_mode = st.selectbox(
        "🎯 Policy Mode",
        ["Conservative", "Welfare State", "Surveillance State", "Random Chaos"],
        index=["Conservative", "Welfare State", "Surveillance State", "Random Chaos"].index(st.session_state.policy_mode)
    )

with col_s4:
    st.session_state.force_rebel = st.checkbox("⚡ Force Rebel", value=st.session_state.force_rebel)

# Footer
st.markdown("---")
st.markdown("**🏆 CivicMind Control Room** | Connected to Real Backend | Meta × HF OpenEnv Hackathon 2025")

if st.session_state.env:
    st.success(f"✅ Backend Active | Week {st.session_state.week}/{st.session_state.max_weeks} | Health: {state_data['health']:.0%}")
else:
    st.info("👆 Click RUN SIMULATION to start the backend")
