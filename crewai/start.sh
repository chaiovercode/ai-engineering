#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting backend..."
(cd "$SCRIPT_DIR/backend" && python main.py) &
BACKEND_PID=$!

echo "Starting frontend..."
(cd "$SCRIPT_DIR/frontend" && PORT=3008 npm run dev) &
FRONTEND_PID=$!

echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend: http://127.0.0.1:8008"
echo "Frontend: http://localhost:3008"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Kill both processes on Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" EXIT

wait
