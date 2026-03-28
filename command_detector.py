#!/usr/bin/env python3
"""
Malicious Command Detection
"""
import json
import re

MALICIOUS_PATTERNS = [
    r'wget.*http',
    r'curl.*http',
    r'nc.*[\d.]+.*\d+',
    r'rm\s+-rf',
    r'/etc/passwd',
    r'whoami',
    r'id\s+',
    r'uname\s+-a',
    r'cat\s+/etc/shadow'
]

class CommandDetector:
    def __init__(self, log_file="/var/log/cowrie/cowrie-honeypot.json"):
        self.log_file = log_file
        
    def detect_malicious_commands(self):
        detections = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    event = json.loads(line.strip())
                    if event.get('eventid') == 'cowrie.command.input':
                        command = event.get('input', '').lower()
                        src_ip = event.get('src_ip', 'unknown')
                        
                        for pattern in MALICIOUS_PATTERNS:
                            if re.search(pattern, command):
                                detection = {
                                    'timestamp': event['timestamp'],
                                    'type': 'malicious_command',
                                    'src_ip': src_ip,
                                    'command': event['input'],
                                    'pattern': pattern,
                                    'severity': 'medium'
                                }
                                detections.append(detection)
                                print(f"⚠️  MALICIOUS COMMAND: {src_ip} -> {command}")
                                break
        except Exception as e:
            print(f"Error detecting commands: {e}")
        
        return detections
