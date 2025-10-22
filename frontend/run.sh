#!/bin/bash

# University Assistant - Start Script
echo "🎓 Starting University Assistant..."

# Kill existing processes
pkill -f "working_proxy" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sleep 2

# Start backend on 8081
echo "🔧 Starting backend on port 8081..."
nohup python3 working_proxy.py > backend.log 2>&1 &
BACKEND_PID=$!

# Start frontend on 8080  
echo "🌐 Starting frontend on port 8080..."
PORT=8080 nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "✅ Services started successfully!"
echo "📱 Frontend: https://cf2f0da36fbf4288832c5b6073ac798d.vfs.cloud9.us-east-1.amazonaws.com:8080"
echo "🔧 Backend:  https://cf2f0da36fbf4288832c5b6073ac798d.vfs.cloud9.us-east-1.amazonaws.com:8081"
echo ""
echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
echo "Logs: backend.log, frontend.log"
