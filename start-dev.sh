#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Interviewer - Development Server ===${NC}"
echo -e "${YELLOW}Starting both backend and frontend servers...${NC}"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}tmux is not installed. Please install it first:${NC}"
    echo -e "${YELLOW}sudo apt-get install tmux${NC}"
    exit 1
fi

# Create a new tmux session
SESSION_NAME="ai-interviewer"
tmux new-session -d -s $SESSION_NAME

# Split the window horizontally
tmux split-window -h -t $SESSION_NAME

# Start the backend in the left pane
tmux send-keys -t $SESSION_NAME:0.0 "cd $HOME/Documents/GitHub/AI_Interviewer/ai_interviewer && echo -e '${GREEN}Starting backend server...${NC}' && python -m src.ai_interviewer.main" C-m

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start the frontend in the right pane
tmux send-keys -t $SESSION_NAME:0.1 "cd $HOME/Documents/GitHub/AI_Interviewer/lucid-interview-agent-main && echo -e '${GREEN}Starting frontend server...${NC}' && npm run dev" C-m

# Attach to the tmux session
echo -e "${GREEN}Both servers are running!${NC}"
echo -e "${YELLOW}- Backend: http://localhost:8000${NC}"
echo -e "${YELLOW}- Frontend: http://localhost:5173${NC}"
echo -e "${BLUE}Press Ctrl+B then D to detach from tmux session while keeping servers running${NC}"
tmux attach-session -t $SESSION_NAME
