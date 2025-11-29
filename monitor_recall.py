import subprocess
import time
import re

print("🔄 LIVE MONITORING - Recall DMs Progress\n")
print("=" * 60)

last_line_count = 0
while True:
    try:
        # Get latest logs
        result = subprocess.run(
            ['tail', '-500', '/tmp/logs/Discord_Bot_20251129_102243_136.log'],
            capture_output=True,
            text=True
        )
        
        logs = result.stdout
        
        # Find all PROGRESS lines
        progress_lines = re.findall(r'⏸️.*PROGRESS.*', logs)
        completion_lines = re.findall(r'📋.*Report.*', logs)
        
        # Extract latest progress
        if progress_lines:
            latest = progress_lines[-1]
            print(f"\n{latest}")
        
        # Check if finished
        if "finished" in logs.lower() or "✅" in logs and "Report" in logs:
            print("\n✅ FINISHED!")
            break
        
        time.sleep(5)  # Check every 5 seconds
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
