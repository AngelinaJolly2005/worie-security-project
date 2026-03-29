#!/usr/bin/env python3
"""
REAL-TIME Cowrie Attack Detection + GitHub Push
Monitors logs continuously and pushes attacks immediately
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
import subprocess
import threading
from typing import Dict, List, Any

class RealTimeAttackDetector:
    def __init__(self):
        self.log_path = Path("var/log/cowrie/cowrie.json")
        self.alerts_path = Path("detections/realtime_alerts.json")
        self.summary_path = Path("detections/realtime_summary.json")
        
        # Attack tracking (sliding window of 5 minutes)
        self.bruteforce_tracker = defaultdict(lambda: deque(maxlen=50))
        self.session_tracker = defaultdict(list)
        
        # Attack thresholds
        self.BRUTEFORCE_THRESHOLD = 5  # attempts in 5 min
        self.RAPID_FIRE_THRESHOLD = 10  # attempts in 1 min
        
        self.running = True
        self.last_position = 0
        
    def tail_file(self):
        """Tail the log file like `tail -f`"""
        if not self.log_path.exists():
            return
            
        with open(self.log_path, 'r') as f:
            f.seek(0, 2)  # Go to end
            while self.running:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line.strip()
    
    def parse_log(self, line: str) -> Dict[str, Any]:
        """Parse single JSON log line"""
        try:
            return json.loads(line)
        except:
            return {}
    
    def detect_attacks(self, log_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect attacks in real-time"""
        alerts = []
        eventid = log_entry.get('eventid')
        src_ip = log_entry.get('src_ip')
        timestamp = datetime.fromisoformat(log_entry.get('timestamp', '1970-01-01T00:00:00'))
        now = datetime.now()
        
        if not src_ip or eventid != 'cowrie.login.failed':
            return alerts
        
        # Track attempts with timestamp
        self.bruteforce_tracker[src_ip].append(now.timestamp())
        
        # Brute force detection (5+ attempts in 5 min)
        recent_attempts = [t for t in self.bruteforce_tracker[src_ip] 
                          if now.timestamp() - t < 300]  # 5 minutes
        if len(recent_attempts) >= self.BRUTEFORCE_THRESHOLD:
            alerts.append({
                'type': 'BRUTEFORCE_ATTACK',
                'severity': 'CRITICAL',
                'src_ip': src_ip,
                'attempts': len(recent_attempts),
                'time_window': 300,
                'timestamp': log_entry['timestamp'],
                'detected_at': datetime.now().isoformat()
            })
        
        # Rapid fire detection (10+ attempts in 1 min)
        rapid_attempts = [t for t in self.bruteforce_tracker[src_ip] 
                         if now.timestamp() - t < 60]  # 1 minute
        if len(rapid_attempts) >= self.RAPID_FIRE_THRESHOLD:
            alerts.append({
                'type': 'RAPID_FIRE_ATTACK',
                'severity': 'CRITICAL',
                'src_ip': src_ip,
                'attempts': len(rapid_attempts),
                'time_window': 60,
                'timestamp': log_entry['timestamp'],
                'detected_at': datetime.now().isoformat()
            })
        
        return alerts
    
    def save_alerts(self, new_alerts: List[Dict[str, Any]]):
        """Save alerts immediately"""
        if not new_alerts:
            return
            
        self.alerts_path.parent.mkdir(exist_ok=True)
        
        # Load existing
        existing = []
        if self.alerts_path.exists():
            try:
                with open(self.alerts_path, 'r') as f:
                    data = json.load(f)
                    existing = data.get('alerts', [])
            except:
                pass
        
        # Add new alerts
        all_alerts = existing + new_alerts
        data = {
            'alerts': all_alerts[-100:],  # Keep last 100
            'total_alerts': len(all_alerts),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.alerts_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"🚨 ALERTS GENERATED: {len(new_alerts)} | Total: {data['total_alerts']}")
    
    def git_push_async(self):
        """Push to GitHub in background"""
        try:
            subprocess.run(['git', 'add', 'detections/'], check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 
                          f'Real-time alerts: {datetime.now().strftime("%H:%M:%S")}'], 
                          check=True, capture_output=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True)
            print("✅ LIVE PUSH TO GITHUB")
        except:
            pass  # Silent fail for real-time
    
    def run_detector(self):
        """Main real-time detection loop"""
        print("🔥 REAL-TIME ATTACK DETECTOR STARTED")
        print("📡 Monitoring var/log/cowrie/cowrie.json...")
        
        for line in self.tail_file():
            log_entry = self.parse_log(line)
            if not log_entry:
                continue
            
            # Detect attacks
            alerts = self.detect_attacks(log_entry)
            
            if alerts:
                self.save_alerts(alerts)
                # Push immediately in background
                threading.Thread(target=self.git_push_async, daemon=True).start()
            
            # Print live activity
            eventid = log_entry.get('eventid', 'UNKNOWN')
            ip = log_entry.get('src_ip', 'unknown')
            if eventid in ['cowrie.login.failed', 'cowrie.login.success']:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {eventid} <- {ip}")

if __name__ == "__main__":
    detector = RealTimeAttackDetector()
    try:
        detector.run_detector()
    except KeyboardInterrupt:
        print("\n🛑 Detector stopped")
