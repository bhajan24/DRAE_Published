#!/bin/bash

# Start both React frontend and proxy backend

echo "Starting EduPortal Application..."
echo "================================"

# Start proxy server in background
echo "Starting proxy server on port 8081..."
python3 working_proxy.py &
PROXY_PID=$!

# Wait a moment for proxy to start
sleep 3

# Start React development server
echo "Starting React frontend on port 3000..."
npm start &
REACT_PID=$!

echo ""
echo "✅ Both servers started successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8081"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap 'echo "Stopping servers..."; kill $PROXY_PID $REACT_PID; exit' INT
wait
