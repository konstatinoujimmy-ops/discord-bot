"""
Flask web server for keep-alive functionality
This creates an endpoint that external services can ping to keep the bot alive
"""

from flask import Flask, jsonify, render_template_string
import threading
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple HTML template for the status page
STATUS_TEMPLATE = """
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Bot Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status {
            color: #28a745;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .info {
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
        }
        .instructions {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .endpoint {
            background-color: #e9ecef;
            padding: 10px;
            font-family: monospace;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Discord Bot Keep-Alive Status</h1>
        <div class="status">✅ Bot is running!</div>
        
        <div class="info">
            <strong>Last Ping:</strong> {{ timestamp }}
        </div>
        
        <div class="info">
            <strong>Ping Endpoint:</strong>
            <div class="endpoint">{{ ping_url }}/ping</div>
        </div>
        
        <div class="instructions">
            <h3>📋 Οδηγίες για 24/7 λειτουργία:</h3>
            <ol>
                <li>Κάντε account στο <a href="https://uptimerobot.com" target="_blank">UptimeRobot</a> (δωρεάν)</li>
                <li>Προσθέστε νέο monitor με τις εξής ρυθμίσεις:</li>
                <ul>
                    <li><strong>Monitor Type:</strong> HTTP(s)</li>
                    <li><strong>URL:</strong> <code>{{ ping_url }}/ping</code></li>
                    <li><strong>Monitoring Interval:</strong> 5 minutes</li>
                </ul>
                <li>Εναλλακτικά, μπορείτε να χρησιμοποιήσετε το <a href="https://cron-job.org" target="_blank">cron-job.org</a></li>
            </ol>
            
            <p><strong>Σημείωση:</strong> Αυτή η μέθοδος εκμεταλλεύεται το γεγονός ότι το Replit κρατάει τα projects ενεργά όταν λαμβάνουν HTTP requests.</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main status page"""
    # Χρησιμοποιούμε το σωστό Replit dev domain
    dev_domain = os.getenv('REPLIT_DEV_DOMAIN', '')
    if dev_domain:
        ping_url = f"https://{dev_domain}"
    else:
        # Fallback στο παλιό format
        ping_url = os.getenv('REPL_SLUG', 'workspace') + '.' + os.getenv('REPL_OWNER', 'konstantinoudem') + '.repl.co'
        if not ping_url.startswith('http'):
            ping_url = f"https://{ping_url}"
    
    return render_template_string(STATUS_TEMPLATE, 
                                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                                ping_url=ping_url)

@app.route('/ping')
def ping():
    """Ping endpoint for keep-alive services"""
    logger.info("Received ping request")
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat(),
        'message': 'Discord bot is running!'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'running'
    })

def run():
    """Run the Flask server"""
    try:
        # Bind to 0.0.0.0:5000 as required
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Error starting Flask server: {e}")

def keep_alive():
    """Start the keep-alive server in a separate thread"""
    try:
        server_thread = threading.Thread(target=run, daemon=True)
        server_thread.start()
        logger.info("Keep-alive server started successfully on port 5000")
        return server_thread
    except Exception as e:
        logger.error(f"Failed to start keep-alive server: {e}")
        return None