# 🏛 HTML CONTROL ROOM - WORKING NOW!

## ✅ WHAT'S FIXED

Your HTML control room is now **fully connected to the real CivicMind backend**!

## 🚀 HOW TO USE IT

### Start the Control Room:
```bash
streamlit run demo/control_room_html.py --server.port 8505
```

**URL**: http://localhost:8505

## 🎯 WHAT YOU GET

### 1. Professional NASA-Style UI
- Dark military aesthetic with Share Tech Mono + Rajdhani fonts
- 3-panel layout (Control | City Core | Intelligence)
- Live system feed at bottom
- Scanline overlay effect

### 2. Real Backend Connection
- All metrics update from real CivicMindEnv
- Agent decisions show actual policy choices
- Rebel spawns when backend triggers it
- Crisis alerts display real crisis engine data

### 3. Working Controls
All buttons below the HTML work:
- **🚀 RUN SIMULATION** - Initializes backend
- **▶️ NEXT WEEK** - Steps simulation forward
- **💥 INJECT CRISIS** - Triggers chaos
- **🔥 SPAWN REBEL** - Forces rebel spawn

### 4. Live Updates
Every time you click a button:
- HTML UI updates instantly
- Metrics reflect real city state
- Agent panel shows latest decisions
- Timeline shows system events
- Rebel panel activates when rebel spawns

## 📊 WHAT THE UI SHOWS

### Left Panel - CONTROL SYSTEM
- Difficulty slider (visual only)
- Policy mode selector (visual only)
- Instructions to use Streamlit buttons

### Center Panel - CITY CORE
- **System Health Score** (big number, color-coded)
- **Status Pill** (Stable/Strained/Critical)
- **4 Key Metrics**:
  - Trust Score
  - Unrest Level
  - GDP Index
  - Survival Rate
- **Active Crises** (when present)

### Right Panel - INTELLIGENCE VIEW
- **Agent Decisions** (last 6 actions)
- **Rebel Status** (activates when rebel spawns)
  - Shows strength percentage
  - Pulsing red border
  - "GOVERNMENT UNDER THREAT" warning

### Bottom - LIVE SYSTEM FEED
- Last 10 system events
- Week-by-week timeline
- Crisis notifications
- Rebel spawn alerts

## 🔥 HOW IT WORKS

### Backend → Frontend Flow:
1. You click "NEXT WEEK" in Streamlit
2. Backend runs `env.step(actions)`
3. Python calculates new city state
4. State data converted to JSON
5. JSON injected into HTML
6. JavaScript `updateUI()` function updates display

### Key Code:
```python
state_data = {
    "week": st.session_state.week,
    "health": health_score,
    "trust": city.trust_score,
    "unrest": city.civil_unrest,
    "rebel_active": env.rebel_active,
    # ... more metrics
}

# Inject into HTML
html_with_state = html_content.replace(
    "console.log(...)",
    f"updateUI({json.dumps(state_data)});"
)
```

## 🎮 DEMO WORKFLOW

1. **Start**: Click "RUN SIMULATION"
   - Backend initializes
   - HTML shows initial state (82% health, stable)

2. **Step Forward**: Click "NEXT WEEK" multiple times
   - Watch metrics change
   - See agent decisions update
   - Trust drops, unrest rises

3. **Spawn Rebel**: Click "🔥 SPAWN REBEL"
   - Right panel lights up red
   - "REBEL ACTIVE" warning appears
   - Strength percentage shows

4. **Inject Crisis**: Click "💥 INJECT CRISIS"
   - Trust drops 20%
   - Unrest spikes 30%
   - Crisis banner appears in center

5. **Watch Chaos**: Keep clicking "NEXT WEEK"
   - System health declines
   - Status changes: Stable → Strained → Critical
   - Rebel strength grows
   - Timeline fills with events

## 🏆 WHY THIS WINS

### Before (What User Had):
- Static HTML simulation
- Fake JavaScript logic
- No real backend connection
- Just a pretty demo

### Now (What You Have):
- ✅ Professional military UI
- ✅ Real CivicMind backend
- ✅ Live multi-agent decisions
- ✅ Actual rebel spawning
- ✅ Real crisis engine
- ✅ True system dynamics

### Judge Impact:
When judges see this:
1. **Visual**: "Wow, this looks professional"
2. **Click buttons**: "Everything works!"
3. **See rebel spawn**: "This is emergent behavior!"
4. **Watch metrics**: "This is a real system!"

## 📁 FILES

- `demo/control_room.html` - The HTML UI (static)
- `demo/control_room_html.py` - Streamlit integration (connects backend)
- `environment/civic_env.py` - Backend environment
- `agents/agent_definitions.py` - Agent logic

## 🔧 CUSTOMIZATION

### Change Colors:
Edit `control_room.html` CSS variables:
```css
:root {
    --green: #00ff87;
    --red: #ff3b3b;
    --orange: #ff6b1a;
    /* ... */
}
```

### Add More Metrics:
1. Add to `state_data` dict in `control_room_html.py`
2. Update `updateUI()` function in HTML
3. Add HTML elements to display

### Change Update Logic:
Edit the `updateUI(state)` function in `control_room.html`

## ⚠️ IMPORTANT NOTES

1. **Buttons are in Streamlit, not HTML**
   - HTML is pure visualization
   - All actions happen in Streamlit below
   - This is correct architecture!

2. **State Updates on Rerun**
   - Every button click triggers `st.rerun()`
   - New state injected into HTML
   - JavaScript updates display

3. **No API Server Needed**
   - Everything runs in one Streamlit process
   - Backend and frontend in same app
   - Simpler than REST API approach

## 🎯 NEXT STEPS

You now have:
- ✅ Working HTML control room
- ✅ Real backend connection
- ✅ Professional UI
- ✅ All features working

**You're ready to demo!**

Just run:
```bash
streamlit run demo/control_room_html.py --server.port 8505
```

And show judges the full system in action.

## 🏆 WINNING COMBINATION

You have **3 working UIs** now:

1. **`demo/dashboard_live.py`** (port 8501)
   - Original working dashboard
   - Good for development

2. **`demo/dashboard_control_room.py`** (port 8503)
   - Streamlit-native control room
   - Professional styling
   - Backup option

3. **`demo/control_room_html.py`** (port 8505) ⭐
   - HTML control room with real backend
   - Military/NASA aesthetic
   - **Use this for the demo!**

All three work. Use #3 for maximum judge impact!
