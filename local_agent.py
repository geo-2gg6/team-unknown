#!/usr/bin/env python3
"""
Local Privacy Scanner Agent
Collects network activity from this device and sends to cloud backend.
Run this on the device you want to monitor.
"""

import time
import json
import requests
import threading
from collections import deque
from typing import Dict, List, Any

try:
    import psutil
    from psutil import AccessDenied, NoSuchProcess
except ImportError:
    print("Error: psutil not installed. Run: pip install psutil")
    exit(1)

# Configuration
CLOUD_BACKEND = "https://your-app.onrender.com"  # Replace with your Render URL
SEND_INTERVAL = 5  # seconds
MAX_EVENTS = 100

class LocalAgent:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip('/')
        self.events = deque(maxlen=MAX_EVENTS)
        self.running = False
        self.thread = None
        
    def collect_connections(self) -> List[Dict[str, Any]]:
        """Collect TCP connections from this device"""
        events = []
        if not psutil:
            return events
            
        try:
            connections = psutil.net_connections(kind="tcp")
        except (AccessDenied, Exception):
            return events
            
        now = time.time()
        seen = set()
        
        for conn in connections:
            try:
                status = getattr(conn, "status", "").upper()
                raddr = getattr(conn, "raddr", None)
                
                # Only outgoing established connections
                if not raddr or status not in {"ESTABLISHED", "CONNECTED"}:
                    continue
                    
                pid = getattr(conn, "pid", None)
                key = (pid, getattr(conn, "laddr"), raddr, status)
                if key in seen:
                    continue
                seen.add(key)
                
                # Get process name
                process_name = None
                if pid:
                    try:
                        process_name = psutil.Process(pid).name()
                    except (NoSuchProcess, AccessDenied, ProcessLookupError):
                        pass
                
                # Format addresses
                laddr = f"{conn.laddr[0]}:{conn.laddr[1]}" if conn.laddr else None
                raddr_str = f"{raddr[0]}:{raddr[1]}" if raddr else None
                
                events.append({
                    "pid": pid,
                    "process_name": process_name,
                    "laddr": laddr,
                    "raddr": raddr_str,
                    "status": status,
                    "timestamp": now,
                    "device_id": self.get_device_id()
                })
                
            except Exception:
                continue
                
        return events
    
    def get_device_id(self) -> str:
        """Generate a unique device identifier"""
        try:
            import platform
            import hashlib
            # Use hostname + MAC address for device ID
            hostname = platform.node()
            mac = None
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:  # MAC address
                        mac = addr.address
                        break
                if mac:
                    break
            device_str = f"{hostname}-{mac or 'unknown'}"
            return hashlib.md5(device_str.encode()).hexdigest()[:12]
        except Exception:
            return "unknown-device"
    
    def classify_event(self, event: Dict[str, Any]) -> str:
        """Classify event as Safe/Risk/Caution based on destination"""
        raddr = event.get("raddr", "")
        status = event.get("status", "").upper()
        
        if not raddr or ":" not in str(raddr):
            return "Caution"
            
        try:
            host = str(raddr).split(":")[0]
            port = int(str(raddr).split(":")[1])
        except (ValueError, IndexError):
            return "Caution"
        
        # Trusted domains
        trusted_patterns = [
            "google.com", "gstatic.com", "googleapis.com", "microsoft.com",
            "windowsupdate.com", "live.com", "github.com", "amazonaws.com",
            "cloudflare.com", "office365.com", "office.com"
        ]
        
        # Risky patterns
        risky_patterns = [
            "doubleclick.net", "adservice.google.com", "adsystem.com",
            "tracking", "tracker", "pixel", "coinhive", "cryptominer"
        ]
        
        host_lower = host.lower()
        
        # Check trusted patterns
        if any(pattern in host_lower for pattern in trusted_patterns):
            return "Safe" if status in {"ESTABLISHED", "CONNECTED"} else "Caution"
            
        # Check risky patterns
        if any(pattern in host_lower for pattern in risky_patterns):
            return "Risk"
            
        # Port-based classification
        risky_ports = {21, 23, 25, 135, 139, 445, 3389}
        web_ports = {80, 443}
        
        if status not in {"ESTABLISHED", "CONNECTED"}:
            return "Caution"
        if port in risky_ports:
            return "Risk"
        if port in web_ports:
            return "Safe"
            
        return "Caution"
    
    def send_events(self) -> bool:
        """Send collected events to cloud backend"""
        if not self.events:
            return True
            
        try:
            events_to_send = list(self.events)
            self.events.clear()
            
            payload = {
                "events": events_to_send,
                "device_id": self.get_device_id(),
                "timestamp": time.time()
            }
            
            response = requests.post(
                f"{self.backend_url}/api/device-events",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ Sent {len(events_to_send)} events to cloud")
                return True
            else:
                print(f"✗ Failed to send events: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error sending events: {e}")
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print(f"🔍 Starting privacy monitor for device {self.get_device_id()}")
        print(f"📡 Sending data to: {self.backend_url}")
        
        while self.running:
            try:
                # Collect new events
                new_events = self.collect_connections()
                
                # Classify and add to queue
                for event in new_events:
                    event["verdict"] = self.classify_event(event)
                    self.events.append(event)
                
                # Send events to cloud
                if self.events:
                    self.send_events()
                    
            except Exception as e:
                print(f"⚠️  Error in monitor loop: {e}")
            
            time.sleep(SEND_INTERVAL)
    
    def start(self):
        """Start the monitoring agent"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        print("🚀 Local agent started!")
    
    def stop(self):
        """Stop the monitoring agent"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Local agent stopped!")

def main():
    print("🔒 Privacy Scanner - Local Agent")
    print("=" * 40)
    
    # Get backend URL from user
    backend_url = input(f"Enter your Render app URL (default: {CLOUD_BACKEND}): ").strip()
    if not backend_url:
        backend_url = CLOUD_BACKEND
    
    if not backend_url.startswith(('http://', 'https://')):
        backend_url = 'https://' + backend_url
    
    agent = LocalAgent(backend_url)
    
    try:
        agent.start()
        print("\nPress Ctrl+C to stop monitoring...")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        agent.stop()
        print("Goodbye! 👋")

if __name__ == "__main__":
    main()
