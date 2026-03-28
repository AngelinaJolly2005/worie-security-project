#!/bin/bash
# Enhanced Cowrie Log → JSON → GitHub Automation

LOG_AGGREGATOR="log_aggregator.py"
INTERVAL=30  # Check every 30 seconds
MAX_RUNTIME=3600  # Run for 1 hour then restart

echo "🚀 Starting Cowrie Log Aggregator (Ctrl+C to stop)"
echo "📁 Logs: var/log/cowrie/cowrie.json"
echo "📤 Output: detections/all_logs.json + summary.json"
echo "⏱️  Interval: ${INTERVAL}s"

START_TIME=$(date +%s)
RUNTIME=0

while [ $RUNTIME -lt $MAX_RUNTIME ]; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "\n[${TIMESTAMP}] 🔄 Processing logs..."
    
    if python3 "$LOG_AGGREGATOR"; then
        echo "✅ Processing successful"
    else
        echo "❌ Processing failed"
    fi
    
    RUNTIME=$(( $(date +%s) - START_TIME ))
    REMAINING=$(( MAX_RUNTIME - RUNTIME ))
    
    echo "💤 Sleeping ${INTERVAL}s (remaining: ${REMAINING}s)..."
    sleep $INTERVAL
done

echo "⏰ Max runtime reached. Restarting..."
