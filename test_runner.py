# test_runner.py
"""
Automated test runner with logging.
Run: python test_runner.py
"""

import os
import sys
import django
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_tests():
    """Run all tests and log results."""
    print("🚀 Starting automated test suite...")
    
    # Create logs directory
    Path("test_logs").mkdir(exist_ok=True)
    
    # Get timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = Path(f"test_logs/test_report_{timestamp}.txt")
    json_log_file = Path(f"test_logs/test_report_{timestamp}.json")
    
    # Run tests
    cmd = [
        sys.executable, "manage.py", "test",
        "core.tests",
        "--verbosity=2",
        "--keepdb",
        "--noinput"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # ---- Write Text Report ----
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("GOODDEEDS – AUTOMATED TEST REPORT\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test Suite: core.tests\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("STDOUT:\n")
        f.write("-" * 40 + "\n")
        f.write(result.stdout)
        f.write("\n\nSTDERR:\n")
        f.write("-" * 40 + "\n")
        f.write(result.stderr)
        f.write("\n\n" + "=" * 80 + "\n")
        f.write(f"EXIT CODE: {result.returncode}\n")
        f.write(f"STATUS: {'✅ PASSED' if result.returncode == 0 else '❌ FAILED'}\n")
        f.write("=" * 80 + "\n")
    
    # ---- Write JSON Report ----
    test_summary = {
        "timestamp": timestamp,
        "date": datetime.now().isoformat(),
        "exit_code": result.returncode,
        "status": "PASSED" if result.returncode == 0 else "FAILED",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": " ".join(cmd)
    }
    
    with open(json_log_file, 'w', encoding='utf-8') as f:
        json.dump(test_summary, f, indent=2)
    
    print(f"\n✅ Test report saved to: {log_file}")
    print(f"📊 JSON report saved to: {json_log_file}")
    
    if result.returncode == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED. Check the log file for details.")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())