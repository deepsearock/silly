set -e

# Ensure OPENAI_API_KEY is set
if [[ -z "$OPENAI_API_KEY" ]]; then
  echo "Error: OPENAI_API_KEY is not set."
  exit 1
fi

# Start FastAPI backend in the background
echo "Starting FastAPI backend on http://0.0.0.0:8000..."
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Give backend a moment to start
sleep 2

# Start Streamlit frontend on port 8501
echo "Starting Streamlit frontend on http://localhost:8501..."
streamlit run frontend/app.py --server.port 8501

# When Streamlit exits, shut down backend
echo "Shutting down backend (PID $BACKEND_PID)..."
kill $BACKEND_PID