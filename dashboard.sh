#!/bin/bash
clear
echo "🔥 COWRIE REAL-TIME DASHBOARD"
echo "================================"
echo "📊 GitHub: $(git remote get-url origin | sed 's|https://[^@]*@||')"
echo "🕐 Last update: $(date)"
echo ""

# Recent alerts
echo "🚨 RECENT ATTACKS:"
jq -r '.alerts[] | "\$.detected_at[11:19]) \$.type) \$.severity) \$.src_ip) (\$.attempts))"' detections/realtime_alerts.json 2>/dev/null | tail -5 || echo "No alerts"

echo ""
echo "📈 SUMMARY:"
jq '.total_alerts // 0' detections/realtime_alerts.json 2>/dev/null || echo 0

echo ""
echo "🔍 LIVE LOGS:"
tail -5 var/log/cowrie/cowrie.json | jq -r 'select(.eventid? | test("login")) | .src_ip + " " + (.eventid // "unknown")'

echo ""
echo "👉 GitHub: $(git remote get-url origin | sed 's|https://[^@]*@||')"
