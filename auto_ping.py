"""
Αυτόματο ping σύστημα για 24/7 uptime
Κάνει ping το server κάθε 4 λεπτά για να το κρατά ζωντανό
"""

import requests
import time
import threading
import logging
import os

logger = logging.getLogger(__name__)

class AutoPing:
    def __init__(self):
        self.running = False
        self.thread = None
        self.ping_interval = 20  # 20 δευτερόλεπτα για maximum uptime
        
    def get_ping_url(self):
        """Παίρνει το σωστό URL για ping"""
        dev_domain = os.getenv('REPLIT_DEV_DOMAIN', '')
        if dev_domain:
            return f"https://{dev_domain}/ping"
        else:
            # Fallback
            return f"https://{os.getenv('REPL_SLUG', 'workspace')}.{os.getenv('REPL_OWNER', 'konstantinoudem')}.repl.co/ping"
    
    def ping_self(self):
        """Κάνει ping το server για να το κρατά ζωντανό"""
        try:
            url = self.get_ping_url()
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Auto-ping successful - bot staying alive!")
                return True
            else:
                logger.warning(f"⚠️ Auto-ping returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Auto-ping failed: {e}")
            return False
    
    def ping_loop(self):
        """Κύριος βρόχος ping"""
        logger.info(f"🚀 Auto-ping started - pinging every {self.ping_interval//60} minutes")
        
        # Κάνε αμέσως το πρώτο ping
        if self.running:
            self.ping_self()
        
        while self.running:
            # Περίμενε, μετά κάνε ping
            time.sleep(self.ping_interval)
            
            if self.running:  # Έλεγχος ξανά μετά το sleep
                self.ping_self()
    
    def start(self):
        """Ξεκινά το auto-ping σύστημα"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.ping_loop, daemon=True)
            self.thread.start()
            logger.info("🔄 Auto-ping system started!")
    
    def stop(self):
        """Σταματά το auto-ping σύστημα"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ Auto-ping system stopped!")

# Δημιουργία global instance
auto_ping = AutoPing()

def start_auto_ping():
    """Ξεκινά το αυτόματο ping σύστημα"""
    auto_ping.start()

def stop_auto_ping():
    """Σταματά το αυτόματο ping σύστημα"""
    auto_ping.stop()