#!/usr/bin/env python3
"""
Complete Cowrie Log Aggregator + GitHub Pusher
Converts ALL Cowrie logs to structured JSON and pushes to GitHub
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import shutil

class CowrieLogAggregator:
    def __init__(self):
        self.log_dir = Path("var/log/cowrie")
        self.output_file = Path("detections/all_logs.json")
        self.summary_file = Path("detections/summary.json")
        self.processed_file = Path("detections/last_processed.txt")
        
    def get_last_processed_time(self) -> float:
        """Get timestamp of last processed log"""
        if self.processed_file.exists():
            try:
                return float(self.processed_file.read_text().strip())
            except:
                pass
        return 0
    
    def save_last_processed_time(self, timestamp: float):
        """Save current processing timestamp"""
        self.processed_file.write_text(str(timestamp))
    
    def collect_all_logs(self) -> List[Dict[str, Any]]:
        """Collect ALL Cowrie JSON logs since last run"""
        all_logs = []
        last_processed = self.get_last_processed_time()
        
        print(f"🔍 Scanning logs since: {datetime.fromtimestamp(last_processed)}")
        
        # Process cowrie.json (main log)
        log_file = self.log_dir / "cowrie.json"
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            log_entry = json.loads(line.strip())
                            # Add processing metadata
                            log_entry['processed_at'] = datetime.now().isoformat()
                            log_entry['line_number'] = line_num
                            
                            # Filter new logs only
                            log_time = datetime.fromisoformat(log_entry.get('timestamp', '1970-01-01T00:00:00'))
                            if log_time.timestamp() > last_processed:
                                all_logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"❌ Error reading {log_file}: {e}")
        
        print(f"✅ Found {len(all_logs)} new log entries")
        return all_logs
    
    def generate_summary(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {
            'total_logs': len(logs),
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'login_attempts': 0,
                'successful_logins': 0,
                'commands_executed': 0,
                'bruteforce_ips': {},
                'top_commands': {},
                'unique_ips': set()
            }
        }
        
        for log in logs:
            eventid = log.get('eventid', 'unknown')
            src_ip = log.get('src_ip', 'unknown')
            
            summary['stats']['unique_ips'].add(src_ip)
            
            if eventid == 'cowrie.login.failed':
                summary['stats']['login_attempts'] += 1
                summary['stats']['bruteforce_ips'][src_ip] = summary['stats']['bruteforce_ips'].get(src_ip, 0) + 1
                
            elif eventid == 'cowrie.login.success':
                summary['stats']['successful_logins'] += 1
                
            elif eventid == 'cowrie.command.input':
                summary['stats']['commands_executed'] += 1
                cmd = log.get('input', 'unknown')[:50]  # Truncate long commands
                summary['stats']['top_commands'][cmd] = summary['stats']['top_commands'].get(cmd, 0) + 1
        
        summary['stats']['unique_ips'] = len(summary['stats']['unique_ips'])
        summary['stats']['bruteforce_threshold'] = {ip: count for ip, count in summary['stats']['bruteforce_ips'].items() if count >= 5}
        
        return summary
    
    def save_logs(self, logs: List[Dict[str, Any]]):
        """Save all logs to JSON file (append mode)"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing logs
        existing_logs = []
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r') as f:
                    existing_logs = json.load(f).get('logs', [])
            except:
                existing_logs = []
        
        # Combine and save
        all_logs_data = {
            'logs': existing_logs + logs,
            'last_updated': datetime.now().isoformat(),
            'total_entries': len(existing_logs + logs)
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(all_logs_data, f, indent=2)
        print(f"💾 Saved {len(logs)} new logs (total: {len(all_logs_data['logs'])})")
    
    def save_summary(self, summary: Dict[str, Any]):
        """Save summary statistics"""
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"📊 Summary saved")
    
    def git_push(self):
        """Git commit and push all changes"""
        try:
            # Git add all detection files
            subprocess.run(['git', 'add', 'detections/'], check=True, capture_output=True)
            
            # Check if there are changes
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.stdout.strip():
                subprocess.run([
                    'git', 'commit', '-m', 
                    f'Auto: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {len(result.stdout.strip().splitlines())} files updated'
                ], check=True, capture_output=True)
                
                subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True)
                print("✅ Pushed to GitHub")
            else:
                print("ℹ️  No changes to commit")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
    
    def run(self):
        """Main processing pipeline"""
        print("🚀 Starting Cowrie Log Aggregation...")
        
        # Collect logs
        logs = self.collect_all_logs()
        if not logs:
            print("ℹ️  No new logs found")
            return
        
        # Generate summary
        summary = self.generate_summary(logs)
        
        # Save files
        self.save_logs(logs)
        self.save_summary(summary)
        
        # Update processed timestamp
        self.save_last_processed_time(datetime.now().timestamp())
        
        # Git push
        self.git_push()
        
        print("🎉 Processing complete!")

if __name__ == "__main__":
    aggregator = CowrieLogAggregator()
    aggregator.run()
