#!/usr/bin/env python3
"""
ONE-LINE Log Submission → Auto GitHub Push
Enter logs → Auto-save → Auto-push
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

class AutoLogSubmitter:
    def __init__(self):
        self.logs_path = Path("var/log/cowrie/cowrie.json")
        self.alerts_path = Path("detections/submitted_logs.json")
        self.logs_path.parent.mkdir(parents=True, exist_ok=True)
        self.alerts_path.parent.mkdir(parents=True, exist_ok=True)
    
    def submit_log(self, log_data: str):
        """Submit single log entry"""
        try:
            # Parse input as JSON or create basic structure
            if log_data.startswith('{'):
                log_entry = json.loads(log_data)
            else:
                # Create basic failed login if not JSON
                parts = log_data.split()
                log_entry = {
                    "eventid": "cowrie.login.failed",
                    "src_ip": parts[0] if parts else "unknown",
                    "username": parts[1] if len(parts) > 1 else "root",
                    "password": ' '.join(parts[2:]) if len(parts) > 2 else "password",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Add metadata
            log_entry["submitted_at"] = datetime.now().isoformat()
            log_entry["source"] = "manual_submission"
            
            # Append to main log
            with open(self.logs_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            # Track submissions
            submissions = []
            if self.alerts_path.exists():
                with open(self.alerts_path, 'r') as f:
                    submissions = json.load(f).get('submissions', [])
            
            submissions.append({
                'log': log_entry,
                'submitted_at': log_entry['submitted_at']
            })
            
            with open(self.alerts_path, 'w') as f:
                json.dump({'submissions': submissions[-50:]}, f, indent=2)
            
            print(f"✅ SUBMITTED: {log_entry['src_ip']} -> {log_entry.get('username', 'N/A')}")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def auto_git_push(self):
        """Auto push to GitHub"""
        try:
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 
                          f'Auto-submit: {datetime.now().strftime("%Y-%m-%d %H:%M:%S") }'], 
                          check=True, capture_output=True)
            subprocess.run(['git', 'push'], check=True, capture_output=True)
            print("🚀 PUSHED TO GITHUB!")
        except:
            print("⚠️ Git push skipped")

def main():
    submitter = AutoLogSubmitter()
    
    if len(sys.argv) > 1:
        # Command line usage
        log_data = ' '.join(sys.argv[1:])
        if submitter.submit_log(log_data):
            submitter.auto_git_push()
    else:
        # Interactive mode
        print("🔥 COWRIE LOG SUBMITTER (Ctrl+C to exit)")
        print("📝 Format: IP USERNAME PASSWORD")
        print("📝 Or full JSON: {\"eventid\":\"cowrie.login.failed\",\"src_ip\":\"1.2.3.4\"}")
        print("-" * 60)
        
        while True:
            try:
                log_input = input("\n📨 Enter log: ").strip()
                if log_input.lower() in ['quit', 'exit', 'q']:
                    break
                if log_input:
                    if submitter.submit_log(log_input):
                        submitter.auto_git_push()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

if __name__ == "__main__":
    main()
