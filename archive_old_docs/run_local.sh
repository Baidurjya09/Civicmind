#!/bin/bash
# CivicMind — Local Development Runner
# Usage: ./run_local.sh [train|eval|api|dashboard|all]

set -e

MODE=${1:-all}

echo "🏛 CivicMind — Local Runner"
echo "Mode: $MODE"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

case $MODE in
    train)
        echo "📊 Generating training dataset..."
        python training/data_generator.py --n_samples 500
        
        echo ""
        echo "🚀 Starting GRPO training..."
        python training/train_grpo.py --mode train --epochs 2 --max_weeks 12
        ;;
    
    eval)
        echo "📈 Running evaluation..."
        python evaluate.py --mode compare --n_episodes 3 --difficulty 3
        ;;
    
    api)
        echo "🌐 Starting API server on port 8080..."
        uvicorn apis.mock_apis:app --host 0.0.0.0 --port 8080 --reload
        ;;
    
    dashboard)
        echo "📊 Starting Streamlit dashboard on port 8501..."
        streamlit run demo/dashboard.py
        ;;
    
    all)
        echo "🚀 Starting full stack..."
        
        # Start API in background
        echo "  [1/3] Starting API server..."
        uvicorn apis.mock_apis:app --host 0.0.0.0 --port 8080 &
        API_PID=$!
        
        # Wait for API to be ready
        sleep 3
        
        # Run quick evaluation
        echo "  [2/3] Running quick evaluation..."
        python evaluate.py --mode compare --n_episodes 1 --difficulty 3
        
        # Start dashboard
        echo "  [3/3] Starting dashboard..."
        streamlit run demo/dashboard.py &
        DASH_PID=$!
        
        echo ""
        echo "✅ All services running:"
        echo "   API:       http://localhost:8080"
        echo "   Dashboard: http://localhost:8501"
        echo ""
        echo "Press Ctrl+C to stop all services"
        
        # Wait for Ctrl+C
        trap "kill $API_PID $DASH_PID 2>/dev/null; exit" INT
        wait
        ;;
    
    *)
        echo "❌ Unknown mode: $MODE"
        echo "Usage: ./run_local.sh [train|eval|api|dashboard|all]"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
