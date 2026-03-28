#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

class CowrieDetector:
    def __init__(self, log_path: str = "var/log/cowrie/cowrie.json", 
                 output_path: str = "detections/alerts.json"):
        # Ensure these are initialized correctly
        self.log_path = Path(log_path)
        self.output_path = Path(output_path)
        self.alerts = []
        
    def load_logs(self) -> List[Dict[str, Any]]:
        logs = []
        if not self.log_path.exists():
            return logs
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        logs.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
            return logs
        except Exception as e:
            print(f"Error: {e}")
            return []

    def analyze(self) -> List[Dict[str, Any]]:
        print("🔍 Analyzing Cowrie logs...")
        logs = self.load_logs()
        
        # Simple detection logic
        bruteforce = [log for log in logs if log.get('eventid') == 'cowrie.login.failed']
        logins = [log for log in logs if log.get('eventid') == 'cowrie.login.success']
        
        self.alerts = bruteforce + logins
        print(f"✅ Generated {len(self.alerts)} alerts")
        return self.alerts

    def save_alerts(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(self.alerts, f, indent=2)
        print(f"💾 Alerts saved to {self.output_path}")

def main():
    detector = CowrieDetector()
    detector.analyze()
    detector.save_alerts()

if __name__ == "__main__":
    main()
