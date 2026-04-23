"""
CivicMind — Streamlit Dashboard
Live visualization for demos and presentations.
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from evaluate import random_policy, heuristic_policy, run_episode

st.set_page_config(page_title="CivicMind Dashboard", layout="wide")

st.title("🏛 CivicMind — AI Governance Simulation")
st.markdown("**Meta × Hugging Face OpenEnv Hackathon 2025**")

# Sidebar controls
st.sidebar.header("Configuration")
difficulty = st.sidebar.slider("Difficulty", 1, 10, 3)
max_weeks = st.sidebar.slider("Max Weeks", 4, 52, 12)
policy_type = st.sidebar.selectbox("Policy", ["Random", "Heuristic"])

if st.sidebar.button("Run Simulation"):
    st.session_state.running = True

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("City Metrics")
    
    if "running" in st.session_state and st.session_state.running:
        with st.spinner("Running simulation..."):
            policy_fn = random_policy if policy_type == "Random" else heuristic_policy
            result = run_episode(
                policy_fn,
                policy_name=policy_type,
                difficulty=difficulty,
                max_weeks=max_weeks,
                seed=42,
                verbose=False,
            )
            
            st.success(f"Simulation complete!")
            st.metric("Mean Reward", f"{result.mean_reward:.4f}")
            st.metric("Final Trust", f"{result.trust_scores[-1]:.0%}")
            st.metric("Final Survival", f"{result.survival_rates[-1]:.0%}")
            st.metric("Rebel Spawned", "Yes" if result.rebel_spawned else "No")
            
            # Plot rewards
            st.line_chart(result.rewards)
            
            st.session_state.running = False
    else:
        st.info("Click 'Run Simulation' to start")

with col2:
    st.subheader("System Info")
    st.markdown("""
    **All 5 Themes:**
    - ✅ T1: Multi-Agent (6 gov + oversight + rebel)
    - ✅ T2: Long-Horizon (52-week simulation)
    - ✅ T3.1: Professional (8 API endpoints)
    - ✅ T3.2: Personal (citizen petitions)
    - ✅ T4: Self-Improve (10-tier difficulty)
    - ✅ T5: Wild Card (emergent rebel agent)
    
    **6 Bonus Prizes:**
    - Fleet AI, Halluminate, Scale AI, Snorkel AI, Patronus AI, Mercor
    """)

st.markdown("---")
st.markdown("**Built with:** OpenEnv | Unsloth | HF TRL | PyTorch")
