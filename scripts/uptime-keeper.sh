#!/bin/bash
# UHAKIX Uptime Keeper - Keeps Render free tier awake
# Run this on any server (VPS, Raspberry Pi, or another free service like Railway)

API_URL="https://uhakix-api.onrender.com/api/v1/citizen/ask"

while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d '{"question":"ping"}')
    
    if [ "$response" = "200" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ UHAKIX alive"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Got HTTP $response"
    fi
    
    # Ping every 9 minutes (Render sleeps after 15 min of inactivity)
    sleep 540
done