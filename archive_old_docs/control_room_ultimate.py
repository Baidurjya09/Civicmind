"""
CivicMind — ULTIMATE AI GOVERNANCE CONTROL ROOM
Professional HTML/CSS frontend connected to REAL CivicMind backend
Frontend is pure visualization - all logic runs in backend
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS

st.set_page_config(page_title="CivicMind Control Room", layout="wide", initial_sidebar_state="collapsed")

# ============================================================================
# BACKEND STATE MANAGEMENT
# ============================================================================

# Initialize session state
if 'env' not in st.session_state:
    st.session_state.env = None
    st.session_state.obs = None
    st.session_state.week = 0
    st.session_state.history = []
    st.session_state.agent_decisions = []
    st.session_state.system_log = []
    st.session_state.running = False
    st.session_state.difficulty = 8
    st.session_state.max_weeks = 20
    st.session_state.policy = "Surveillance State"
    st.session_state.force_rebel = True
    st.session_state.stress_mode = False

# HTML/CSS/JS for the control room
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

:root {
    --bg: #080c10;
    --bg2: #0d1318;
    --bg3: #111820;
    --border: #1e2d3d;
    --green: #00ff87;
    --yellow: #ffd43b;
    --red: #ff3b3b;
    --orange: #ff6b1a;
    --blue: #4dabf7;
    --text: #c8d8e8;
    --text-dim: #5a7a94;
    --mono: 'Share Tech Mono', monospace;
    --sans: 'Rajdhani', sans-serif;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--mono);
    font-size: 12px;
    padding: 0;
    margin: 0;
}

.header {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.logo {
    font-family: var(--sans);
    font-size: 20px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 2px;
}

.logo span {
    color: var(--green);
}

.status-pill {
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 3px;
    letter-spacing: 1px;
    font-weight: 600;
}

.stable { background: rgba(0,255,135,.15); color: var(--green); border: 1px solid var(--green); }
.strained { background: rgba(255,212,59,.15); color: var(--yellow); border: 1px solid var(--yellow); }
.critical { background: rgba(255,59,59,.2); color: var(--red); border: 1px solid var(--red); animation: pulse 1.5s infinite; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.main-grid {
    display: grid;
    grid-template-columns: 240px 1fr 300px;
    height: calc(100vh - 120px);
    gap: 0;
}

.panel {
    background: var(--bg2);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 16px;
}

.panel:last-child {
    border-right: none;
}

.panel-title {
    font-family: var(--sans);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

.metric-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 12px;
}

.metric-label {
    font-size: 9px;
    color: var(--text-dim);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.metric-value {
    font-family: var(--sans);
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
}

.health-score {
    text-align: center;
    padding: 20px;
    margin-bottom: 20px;
    background: var(--bg3);
    border-radius: 6px;
}

.health-value {
    font-family: var(--sans);
    font-size: 56px;
    font-weight: 700;
    letter-spacing: -2px;
}

.rebel-alert {
    background: linear-gradient(135deg, #ff0000, #ff6600);
    color: #fff;
    padding: 20px;
    border-radius: 6px;
    text-align: center;
    font-weight: 700;
    font-size: 16px;
    margin: 16px 0;
    animation: blink 1s infinite, glow 2s infinite;
    border: 3px solid #ffff00;
    box-shadow: 0 0 30px rgba(255,0,0,0.6);
}

@keyframes blink {
    0%, 50%, 100% { opacity: 1; }
    25%, 75% { opacity: 0.7; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(255,0,0,0.6); }
    50% { box-shadow: 0 0 40px rgba(255,0,0,0.9); }
}

.agent-card {
    background: var(--bg3);
    border-left: 4px solid var(--green);
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 3px;
}

.agent-card.conflict {
    border-left-color: var(--red);
    background: rgba(255,59,59,0.05);
}

.agent-name {
    color: var(--green);
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 6px;
}

.agent-action {
    color: var(--text);
    font-size: 12px;
    margin-bottom: 4px;
}

.agent-reason {
    color: var(--text-dim);
    font-size: 11px;
    font-style: italic;
}

.log-entry {
    background: var(--bg3);
    border-left: 3px solid var(--blue);
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 11px;
    border-radius: 2px;
}

.log-crisis { border-left-color: var(--red); }
.log-rebel { border-left-color: var(--orange); background: rgba(255,107,26,0.05); }

.c-green { color: var(--green); }
.c-yellow { color: var(--yellow); }
.c-red { color: var(--red); }
.c-blue { color: var(--blue); }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
</head>
<body>
<div class="header">
    <div class="logo">🏛 <span>CIVIC</span>MIND — AI GOVERNANCE CONTROL ROOM</div>
    <div style="display: flex; gap: 16px; align-items: center;">
        <span id="status-pill" class="status-pill stable">● STABLE</span>
        <span style="color: var(--blue); font-size: 14px; font-weight: 700; letter-spacing: 1px;" id="week-display">WEEK 00 / 20</span>
    </div>
</div>

<div class="main-grid">
    <!-- LEFT PANEL -->
    <div class="panel">
        <div class="panel-title">🎛 CONTROL SYSTEM</div>
        <div id="control-info" style="font-size: 11px; line-height: 1.8; color: var(--text-dim);">
            <div>Difficulty: <span style="color: var(--blue);" id="diff-display">8</span></div>
            <div>Policy: <span style="color: var(--blue);" id="policy-display">Surveillance State</span></div>
            <div>Force Rebel: <span style="color: var(--green);" id="rebel-display">✓ ENABLED</span></div>
            <div>Stress Mode: <span style="color: var(--text-dim);" id="stress-display">DISABLED</span></div>
        </div>
    </div>

    <!-- CENTER PANEL -->
    <div class="panel">
        <div class="panel-title">🌆 CITY CORE</div>
        
        <div class="health-score">
            <div style="font-size: 10px; color: var(--text-dim); letter-spacing: 2px; margin-bottom: 8px;">SYSTEM HEALTH</div>
            <div class="health-value" id="health-value">82%</div>
            <div style="font-size: 12px; margin-top: 8px; color: var(--text-dim);" id="health-trend">● STABLE</div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
            <div class="metric-card">
                <div class="metric-label">Trust Score</div>
                <div class="metric-value c-blue" id="m-trust">75%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Unrest</div>
                <div class="metric-value c-yellow" id="m-unrest">20%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">GDP Index</div>
                <div class="metric-value c-green" id="m-gdp">1.00</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Survival</div>
                <div class="metric-value c-green" id="m-survival">100%</div>
            </div>
        </div>

        <div id="crisis-banner" style="display: none; background: rgba(255,59,59,0.1); border: 1px solid var(--red); padding: 12px; border-radius: 4px; margin-bottom: 16px;">
            <div style="font-size: 11px; color: var(--red); font-weight: 700; margin-bottom: 6px;">⚡ ACTIVE CRISES</div>
            <div id="crisis-list" style="font-size: 11px; color: var(--text);"></div>
        </div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="panel">
        <div class="panel-title">🧠 INTELLIGENCE VIEW</div>
        
        <div style="font-size: 10px; color: var(--text-dim); letter-spacing: 1.5px; margin-bottom: 12px;">AGENT DECISIONS</div>
        <div id="agents-panel"></div>

        <div style="font-size: 10px; color: var(--text-dim); letter-spacing: 1.5px; margin: 20px 0 12px;">REBEL STATUS</div>
        <div id="rebel-panel"></div>

        <div style="font-size: 10px; color: var(--text-dim); letter-spacing: 1.5px; margin: 20px 0 12px;">SYSTEM ALERTS</div>
        <div id="alerts-panel"></div>
    </div>
</div>

<div style="background: var(--bg2); border-top: 1px solid var(--border); padding: 12px 20px; height: 100px; overflow-y: auto;">
    <div style="font-size: 10px; color: var(--text-dim); letter-spacing: 2px; margin-bottom: 8px;">📜 LIVE SYSTEM FEED</div>
    <div id="timeline-feed"></div>
</div>

<script>
function updateUI(data) {
    // Week display
    document.getElementById('week-display').textContent = `WEEK ${String(data.week).padStart(2,'0')} / ${data.max_weeks}`;
    
    // Control info
    document.getElementById('diff-display').textContent = data.difficulty;
    document.getElementById('policy-display').textContent = data.policy;
    document.getElementById('rebel-display').textContent = data.force_rebel ? '✓ ENABLED' : '✗ DISABLED';
    document.getElementById('stress-display').textContent = data.stress_mode ? 'ACTIVE' : 'DISABLED';
    
    // Health score
    const health = Math.round(data.health * 100);
    const healthEl = document.getElementById('health-value');
    healthEl.textContent = health + '%';
    healthEl.className = 'health-value ' + (health > 70 ? 'c-green' : health > 40 ? 'c-yellow' : 'c-red');
    
    // Status pill
    const pill = document.getElementById('status-pill');
    if (health > 70) {
        pill.textContent = '● STABLE';
        pill.className = 'status-pill stable';
    } else if (health > 40) {
        pill.textContent = '● STRAINED';
        pill.className = 'status-pill strained';
    } else {
        pill.textContent = '● CRITICAL';
        pill.className = 'status-pill critical';
    }
    
    // Metrics
    document.getElementById('m-trust').textContent = Math.round(data.trust * 100) + '%';
    document.getElementById('m-unrest').textContent = Math.round(data.unrest * 100) + '%';
    document.getElementById('m-gdp').textContent = data.gdp.toFixed(2);
    document.getElementById('m-survival').textContent = Math.round(data.survival * 100) + '%';
    
    // Crises
    const crisisBanner = document.getElementById('crisis-banner');
    if (data.crises && data.crises.length > 0) {
        crisisBanner.style.display = 'block';
        document.getElementById('crisis-list').innerHTML = data.crises.map(c => 
            `<div>⚡ ${c.name} (${Math.round(c.severity * 100)}%)</div>`
        ).join('');
    } else {
        crisisBanner.style.display = 'none';
    }
    
    // Agent decisions
    const agentsPanel = document.getElementById('agents-panel');
    if (data.agents && data.agents.length > 0) {
        agentsPanel.innerHTML = data.agents.map(a => `
            <div class="agent-card ${a.conflict ? 'conflict' : ''}">
                <div class="agent-name">${a.conflict ? '⚔️ ' : ''}${a.name}</div>
                <div class="agent-action">→ ${a.action}</div>
                <div class="agent-reason">${a.reason}</div>
            </div>
        `).join('');
    } else {
        agentsPanel.innerHTML = '<div style="color: var(--text-dim); font-size: 11px;">Waiting for agent decisions...</div>';
    }
    
    // Rebel status
    const rebelPanel = document.getElementById('rebel-panel');
    if (data.rebel_active) {
        rebelPanel.innerHTML = `
            <div class="rebel-alert">
                🚨 REBEL ACTIVE 🚨<br/><br/>
                Strength: ${Math.round(data.rebel_strength * 100)}%<br/><br/>
                ⚠️ GOVERNMENT UNDER THREAT ⚠️
            </div>
        `;
    } else if (data.trust < 0.35) {
        rebelPanel.innerHTML = `
            <div style="background: rgba(255,212,59,0.1); border: 1px solid var(--yellow); padding: 12px; border-radius: 4px; font-size: 11px;">
                ⚠️ HIGH RISK<br/>
                Trust: ${Math.round(data.trust * 100)}%<br/>
                Rebel spawn imminent!
            </div>
        `;
    } else {
        rebelPanel.innerHTML = `
            <div style="background: rgba(0,255,135,0.05); border: 1px solid var(--green); padding: 12px; border-radius: 4px; font-size: 11px; color: var(--green);">
                ✓ STABLE<br/>
                Trust: ${Math.round(data.trust * 100)}%
            </div>
        `;
    }
    
    // Alerts
    const alertsPanel = document.getElementById('alerts-panel');
    const alerts = [];
    if (data.trust < 0.35) alerts.push('<div style="color: var(--red); font-size: 11px; margin-bottom: 6px;">🔴 Trust critically low</div>');
    if (data.unrest > 0.6) alerts.push('<div style="color: var(--red); font-size: 11px; margin-bottom: 6px;">🔴 Unrest dangerously high</div>');
    if (data.rebel_active) alerts.push('<div style="color: var(--orange); font-size: 11px; margin-bottom: 6px;">🔥 Rebel active - immediate response needed</div>');
    
    if (alerts.length > 0) {
        alertsPanel.innerHTML = alerts.join('');
    } else {
        alertsPanel.innerHTML = '<div style="color: var(--green); font-size: 11px;">✓ All systems nominal</div>';
    }
    
    // Timeline
    if (data.timeline && data.timeline.length > 0) {
        const feed = document.getElementById('timeline-feed');
        feed.innerHTML = data.timeline.slice(-8).reverse().map(entry => {
            const cls = entry.type === 'crisis' ? 'log-crisis' : entry.type === 'rebel' ? 'log-rebel' : 'log-entry';
            return `<div class="${cls}">Week ${entry.week} | ${entry.event}</div>`;
        }).join('');
    }
}

// Listen for updates from Streamlit
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'streamlit:render') {
        const data = event.data.args;
        if (data) {
            updateUI(data);
        }
    }
});
</script>
</body>
</html>
"""

# Render the HTML
components.html(html_code, height=800, scrolling=False)

# Control buttons at the bottom
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🚀 RUN SIMULATION" if not st.session_state.running else "⏸ PAUSE", use_container_width=True):
        if not st.session_state.running:
            # Initialize environment
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
            st.session_state.system_log = [{"week": 0, "event": "System initialized", "type": "system"}]
            st.session_state.running = True
        else:
            st.session_state.running = False

with col2:
    if st.button("▶️ NEXT WEEK", disabled=not st.session_state.env, use_container_width=True):
        if st.session_state.env and st.session_state.week < st.session_state.max_weeks:
            # Simulate one week
            env = st.session_state.env
            
            # Generate actions
            actions = {}
            decisions = []
            for agent_id in env.AGENT_IDS:
                decision = np.random.choice(ALL_AGENTS[agent_id].valid_decisions)
                actions[agent_id] = {
                    "reasoning": f"{st.session_state.policy} strategy",
                    "tool_calls": [],
                    "policy_decision": decision
                }
                decisions.append({
                    "name": agent_id.replace("_", " ").title(),
                    "action": decision.replace("_", " ").title(),
                    "reason": f"Week {st.session_state.week + 1}",
                    "conflict": decision == "deploy_riot_control" and env.city.trust_score < 0.5
                })
            
            # Step environment
            obs, reward, done, info = env.step(actions)
            st.session_state.obs = obs
            st.session_state.week += 1
            st.session_state.agent_decisions = decisions
            
            # Force rebel if enabled
            if st.session_state.force_rebel and st.session_state.week > 5 and not env.rebel_active:
                env.city.trust_score = max(0.25, env.city.trust_score - 0.05)
                env.city.civil_unrest = min(1.0, env.city.civil_unrest + 0.05)
            
            # Log
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": f"Week {st.session_state.week} completed",
                "type": "system"
            })
            
            if env.rebel_active and not any(log.get('type') == 'rebel' for log in st.session_state.system_log[-3:]):
                st.session_state.system_log.append({
                    "week": st.session_state.week,
                    "event": f"REBEL SPAWNED | Strength: {env.city.rebel_strength:.0%}",
                    "type": "rebel"
                })

with col3:
    if st.button("💥 INJECT CRISIS", disabled=not st.session_state.env, use_container_width=True):
        if st.session_state.env:
            st.session_state.env.city.trust_score -= 0.2
            st.session_state.env.city.civil_unrest += 0.3
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": "MAJOR CRISIS INJECTED",
                "type": "crisis"
            })

with col4:
    if st.button("🔥 SPAWN REBEL", disabled=not st.session_state.env, use_container_width=True):
        if st.session_state.env:
            st.session_state.env.rebel_active = True
            st.session_state.env.city.rebel_strength = 0.35
            st.session_state.system_log.append({
                "week": st.session_state.week,
                "event": "REBEL MANUALLY SPAWNED",
                "type": "rebel"
            })

with col5:
    if st.button("🔄 RESET", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Prepare data for HTML update
if st.session_state.env:
    city = st.session_state.env.city
    health_score = (
        city.trust_score * 0.4 +
        (1 - city.corruption) * 0.2 +
        (1 - city.civil_unrest) * 0.2 +
        city.survival_rate * 0.2
    )
    
    active_crises = st.session_state.env.crisis_engine.get_active_crises()
    
    data = {
        "week": st.session_state.week,
        "max_weeks": st.session_state.max_weeks,
        "difficulty": st.session_state.difficulty,
        "policy": st.session_state.policy,
        "force_rebel": st.session_state.force_rebel,
        "stress_mode": st.session_state.stress_mode,
        "health": health_score,
        "trust": city.trust_score,
        "unrest": city.civil_unrest,
        "gdp": city.gdp_index,
        "survival": city.survival_rate,
        "rebel_active": st.session_state.env.rebel_active,
        "rebel_strength": city.rebel_strength,
        "crises": [{"name": c.name, "severity": c.severity} for c in active_crises],
        "agents": st.session_state.agent_decisions,
        "timeline": st.session_state.system_log
    }
    
    # Send data to HTML
    st.markdown(f"""
    <script>
    window.parent.postMessage({{
        type: 'streamlit:render',
        args: {json.dumps(data)}
    }}, '*');
    </script>
    """, unsafe_allow_html=True)
